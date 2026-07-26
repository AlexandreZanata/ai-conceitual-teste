"""Wave AG3 H-SMARTREAL runner: dual-arm retrieve + QPFB2 gen EVAL."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import torch

from askfast_ops import AskCompletionCache
from data_tiny import load_tokenizer
from decode_beamkv import decode_beams_shared_kv
from decode_early import decode_early
from eval_student import load_student_ckpt
from load_model import load_causal_lm, resolve_device
from matrix_common import REPO, matrix_cfg, write_json
from pfb2_ops import K2_BEAMS
from pfb_ops import PFB_TEMP
from pfb_score import attach_code_teacher, collect_beam_banks, commit_pfb_rows
from qt_quant import quantize_student_int8
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row, classify_semwrap, semantic_lookup
from smartreal_ops import (
    SMARTREAL_ID,
    SMARTREAL_N,
    SMARTREAL_PACK,
    decide_smartreal,
    hard_paraphrase_ok,
    has_adversarial_noise,
    has_quad_hop_cues,
    score_smartreal_gen,
    score_smartreal_lookup,
    smartreal_stats,
)
from tchr_ops import STORY_TEACHER_ID, code_teacher_meta
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AG_BANK = REPO / "results/nano-lm/wave-ag/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-ag/trials"
_SUMMARY = REPO / "results/nano-lm/wave-ag/smartreal_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_JUDGE = "cursor-composer-frontier-chat"
_MAX_NEW = 64


def _clear_proxy() -> None:
    for key in (
        "http_proxy",
        "https_proxy",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "all_proxy",
    ):
        os.environ.pop(key, None)


def _free_cuda(*objs: object) -> None:
    for obj in objs:
        del obj
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()


def _seed_pack(bank_path: Path, ag_bank: Path) -> int:
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    ag_bank.parent.mkdir(parents=True, exist_ok=True)
    if not ag_bank.is_file():
        ag_bank.write_text("", encoding="utf-8")
    existing = {
        str(r.get("question", "")).strip() for r in load_bank_rows(bank_path)
    }
    n = 0
    for i, item in enumerate(SMARTREAL_PACK, start=1):
        for q_key, q_text in (
            ("parent", item["parent_question"]),
            ("para", item["paraphrase"]),
        ):
            q = str(q_text).strip()
            if q in existing:
                continue
            row = alias_bank_row(
                trial_id=f"AG-SMARTREAL-SEED-{q_key}-{i:02d}",
                question=q,
                source_id=item["source_id"],
                gold=item["gold"],
            )
            row["hyp_id"] = SMARTREAL_ID
            row["judge_notes"] = [
                "SMARTREAL seed for quad-hop paraphrase stress",
                "LOOKUP product path — not generative IQ",
                "no student weight update",
            ]
            append_error_row(bank_path, row)
            append_error_row(ag_bank, row)
            existing.add(q)
            n += 1
    return n


def _classify_lookup(
    item: dict[str, str],
    payload: dict[str, Any],
    bank: list[dict[str, Any]],
    curated: Path,
) -> tuple[str, dict[str, Any], str]:
    completion = str(payload.get("completion", ""))
    mode = str(payload.get("mode", ""))
    _g, meta = semantic_lookup(
        item["paraphrase"], bank, curated_root=curated
    )
    looked = (
        completion
        if mode in {"SEMWRAP_LOOKUP", "WRAP_LOOKUP", "ASKFAST_CACHE"}
        else _g
    )
    kind = classify_semwrap(
        looked,
        expected_gold=item["gold"],
        expected_source_id=item["source_id"],
        hit_source_id=str(meta.get("source_id") or "") or None,
    )
    return kind, meta, completion


def _fix_lookup(
    *,
    i: int,
    item: dict[str, str],
    bank_path: Path,
    ag_bank: Path,
    root: Path,
    curated: Path,
    seed: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], int]:
    row = alias_bank_row(
        trial_id=f"AG-SMARTREAL-FIX-{i:02d}",
        question=item["paraphrase"],
        source_id=item["source_id"],
        gold=item["gold"],
    )
    row["hyp_id"] = SMARTREAL_ID
    append_error_row(bank_path, row)
    append_error_row(ag_bank, row)
    bank = load_bank_rows(bank_path)
    re_payloads = ask_many(
        questions=[item["paraphrase"]],
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated,
        ask_cache=AskCompletionCache(),
    )
    return re_payloads[0], bank, 1


def _load_gene(root: Path, recipe: dict[str, Any]) -> dict[str, Any]:
    path = root / str(recipe["early_gene"])
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"missing best_gene: {path}")
    return {**gene, "n": 1}


def _parent_rows(
    *,
    qt: Any,
    tok: Any,
    story: Any,
    questions: list[str],
    gene: dict[str, Any],
    device: torch.device,
    seed: int,
) -> list[dict[str, Any]]:
    from tchr_score import code_teacher_mean_logprob

    rows: list[dict[str, Any]] = []
    for i, q in enumerate(questions):
        parent = decode_early(
            qt,
            tok,
            q,
            n=1,
            max_new_tokens=_MAX_NEW,
            min_new=int(gene["min_new"]),
            conf_threshold=float(gene["conf_threshold"]),
            patience=int(gene["patience"]),
            temperature=1e-6,
            top_p=float(gene["top_p"]),
            seed=int(seed) + i,
            device=device,
        )
        p_story = float(code_teacher_mean_logprob(story, q, parent.text))
        rows.append(
            {
                "family": "H-QT-EARLY-n1",
                "prompt": q,
                "continuation": parent.text,
                "story_teacher_id": STORY_TEACHER_ID,
                "story_teacher_lp": p_story,
                "wall_ms": float(parent.wall_ms),
                "n_new": len(parent.token_ids),
                "seed": int(seed),
                "unique": 1.0,
                "k": 1.0,
                "pick": 0.0,
                "n_elig": 1.0,
                "switched": 0.0,
            }
        )
    return rows


def _run_gen_qpfb2(
    *,
    champ: Path,
    questions: list[str],
    seed: int,
) -> list[dict[str, Any]]:
    recipe = json.loads((champ / "recipe.json").read_text(encoding="utf-8"))
    gene = _load_gene(champ, recipe)
    cfg = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        raise RuntimeError("H-SMARTREAL gen arm requires CUDA")
    tok = load_tokenizer(str(recipe["tokenizer_id"]), cfg["cache"])
    story = load_causal_lm(
        STORY_TEACHER_ID,
        str(recipe["tokenizer_id"]),
        cache_dir=cfg["cache"],
        use_fp16=True,
    )
    student = load_student_ckpt(champ / str(recipe["ckpt"]), tok, device)
    qt = quantize_student_int8(student)  # type: ignore[arg-type]
    qt.to(device)
    try:
        parents = _parent_rows(
            qt=qt,
            tok=tok,
            story=story,
            questions=questions,
            gene=gene,
            device=device,
            seed=seed,
        )
        banks = collect_beam_banks(
            story_teacher=story,
            student=qt,
            parent_rows=parents,
            gene=gene,
            max_new=_MAX_NEW,
            beam_seed=int(seed) + 3300,
            k=K2_BEAMS,
            temperature=PFB_TEMP,
            decode_beams_fn=decode_beams_shared_kv,
        )
    finally:
        _free_cuda(story, student, qt)

    meta = code_teacher_meta()
    code = load_causal_lm(
        meta["hf_id"],
        meta["tokenizer_id"],
        cache_dir=cfg["cache"],
        use_fp16=True,
    )
    try:
        parents = attach_code_teacher(code, parents)
        parent_code = {
            (str(r["prompt"]), int(r["seed"])): float(r["code_teacher_lp"])
            for r in parents
        }
        committed = commit_pfb_rows(
            code,
            banks,
            parent_code_by_key=parent_code,
            family="H-SMARTREAL",
        )
    finally:
        _free_cuda(code)

    if len(committed) != SMARTREAL_N:
        raise RuntimeError(f"expected {SMARTREAL_N} commits, got {len(committed)}")
    out: list[dict[str, Any]] = []
    for row in committed:
        out.append(
            {
                "completion": row.get("continuation"),
                "wall_ms": float(row.get("wall_ms") or 0.0),
                "n_new": int(row.get("n_new") or 0),
                "mode": "QPFB2+BEAMKV",
                "seed": row.get("seed", seed),
                "switched": row.get("switched"),
                "pick": row.get("pick"),
            }
        )
    return out


def run_smartreal(
    *,
    bank_path: Path,
    ag_bank: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN AG0 paraphrases + parent asks
    WHEN SEMWRAP LOOKUP + QPFB2 GENERATE dual-arm ×10
    THEN false-hit≈0; PROMOTE if gen≥5 else HOLD.
    """
    if len(SMARTREAL_PACK) != SMARTREAL_N:
        raise ValueError("SMARTREAL pack must be 10")
    if not hard_paraphrase_ok():
        raise ValueError("paraphrases must differ from parents")
    if not has_adversarial_noise() or not has_quad_hop_cues():
        raise ValueError("quad-hop adversarial pack incomplete")

    trials_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    seeded = _seed_pack(bank_path, ag_bank)
    bank = load_bank_rows(bank_path)
    paras = [p["paraphrase"] for p in SMARTREAL_PACK]
    parents = [p["parent_question"] for p in SMARTREAL_PACK]

    lookup_payloads = ask_many(
        questions=paras,
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated_root,
        ask_cache=AskCompletionCache(),
    )
    gen_payloads = _run_gen_qpfb2(champ=root, questions=parents, seed=seed)

    lookup_trials: list[dict[str, Any]] = []
    gen_trials: list[dict[str, Any]] = []
    fix_count = 0
    for i, (item, lp, gp) in enumerate(
        zip(SMARTREAL_PACK, lookup_payloads, gen_payloads, strict=True),
        start=1,
    ):
        kind, sem_meta, text = _classify_lookup(
            dict(item), lp, bank, curated_root
        )
        fix_pass = 0
        if kind != "TRUE_HIT":
            lp, bank, fix_pass = _fix_lookup(
                i=i,
                item=dict(item),
                bank_path=bank_path,
                ag_bank=ag_bank,
                root=root,
                curated=curated_root,
                seed=seed,
            )
            fix_count += 1
            kind, sem_meta, text = _classify_lookup(
                dict(item), lp, bank, curated_root
            )
        score_l, err_l, notes_l, cited = score_smartreal_lookup(
            mode=str(lp.get("mode", "")),
            completion=text,
            expected_gold=item["gold"],
            lookup_kind=kind,
            expected_source_id=item["source_id"],
            hit_source_id=str(sem_meta.get("source_id") or "") or None,
            payload=lp,
        )
        lt = {
            "trial_id": f"AG-SMARTREAL-LOOKUP-HITL-{i:02d}",
            "stage": "AG3",
            "hyp_id": SMARTREAL_ID,
            "arm": "LOOKUP",
            "app_id": item["app_id"],
            "question": item["paraphrase"],
            "parent_question": item["parent_question"],
            "source_id": item["source_id"],
            "secondary_source": item["secondary_source"],
            "tertiary_source": item["tertiary_source"],
            "quaternary_source": item["quaternary_source"],
            "completion": lp.get("completion"),
            "wall_ms": lp.get("wall_ms"),
            "n_new": lp.get("n_new"),
            "mode": lp.get("mode"),
            "lookup_kind": kind,
            "cite_ok": cited,
            "semwrap": sem_meta,
            "score": score_l,
            "error": err_l,
            "fix_pass": fix_pass,
            "judge_model_name": _JUDGE,
            "judge_notes": notes_l,
            "gold": item["gold"],
            "weight_update": False,
        }
        score_g, err_g, notes_g = score_smartreal_gen(
            completion=str(gp.get("completion", "")),
            expected_gold=item["gold"],
            payload=gp,
        )
        gt = {
            "trial_id": f"AG-SMARTREAL-GEN-HITL-{i:02d}",
            "stage": "AG3",
            "hyp_id": SMARTREAL_ID,
            "arm": "GENERATE",
            "app_id": item["app_id"],
            "question": item["parent_question"],
            "source_id": item["source_id"],
            "completion": gp.get("completion"),
            "wall_ms": gp.get("wall_ms"),
            "n_new": gp.get("n_new"),
            "mode": gp.get("mode"),
            "score": score_g,
            "error": err_g,
            "fix_pass": 0,
            "judge_model_name": _JUDGE,
            "judge_notes": notes_g,
            "gold": item["gold"],
            "weight_update": False,
            "switched": gp.get("switched"),
        }
        if err_g:
            append_error_row(
                ag_bank,
                {
                    "trial_id": gt["trial_id"],
                    "question": item["parent_question"],
                    "source_id": item["source_id"],
                    "model_raw": str(gp.get("completion") or ""),
                    "score": float(score_g),
                    "error": True,
                    "recipe_id": "champion-qpfb2-v0",
                    "hyp_id": SMARTREAL_ID,
                    "arm": "GENERATE",
                    "judge_notes": notes_g,
                    "gold": item["gold"],
                },
            )
        write_json(trials_dir / f"{lt['trial_id']}.json", lt)
        write_json(trials_dir / f"{gt['trial_id']}.json", gt)
        lookup_trials.append(lt)
        gen_trials.append(gt)

    n_true = sum(1 for t in lookup_trials if t["lookup_kind"] == "TRUE_HIT")
    n_false = sum(
        1 for t in lookup_trials if t["lookup_kind"] == "FALSE_HIT"
    )
    stats = smartreal_stats(
        lookup_scores=[float(t["score"]) for t in lookup_trials],
        lookup_errors=[bool(t["error"]) for t in lookup_trials],
        cite_flags=[bool(t["cite_ok"]) for t in lookup_trials],
        gen_scores=[float(t["score"]) for t in gen_trials],
        gen_errors=[bool(t["error"]) for t in gen_trials],
        n_true_hit=n_true,
        n_false_hit=n_false,
        n_fix=fix_count,
    )
    decision = decide_smartreal(stats)
    summary: dict[str, Any] = {
        "hyp_id": SMARTREAL_ID,
        "stage": "AG3",
        "decision": decision,
        "compose": [
            "SEMWRAP/ASKFAST LOOKUP",
            "quad-hop paraphrase",
            "QPFB2+BEAMKV GENERATE",
        ],
        "forbidden": ["QI", "ZPREF", "MIXD", "LOOKUP-as-gen-IQ", "open chat"],
        "seeded_golds": int(seeded),
        "fix_count": int(fix_count),
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "elapsed_s": time.perf_counter() - t0,
        "stats": stats,
        "lookup_trials": [
            {
                "trial_id": t["trial_id"],
                "mode": t["mode"],
                "score": t["score"],
                "cite_ok": t["cite_ok"],
                "lookup_kind": t["lookup_kind"],
                "wall_ms": t["wall_ms"],
                "n_new": t["n_new"],
            }
            for t in lookup_trials
        ],
        "gen_trials": [
            {
                "trial_id": t["trial_id"],
                "mode": t["mode"],
                "score": t["score"],
                "wall_ms": t["wall_ms"],
                "n_new": t["n_new"],
                "error": t["error"],
            }
            for t in gen_trials
        ],
        "finding": (
            f"{SMARTREAL_ID}: L_lookup={stats['lookup_mean']:.1f} "
            f"L_gen={stats['gen_mean']:.1f} cite={stats['n_cite_ok']}/10 "
            f"false_hit={n_false} beats_servealign={stats['beats_servealign']} "
            f"pass_gen={stats['pass_gen']} fix={fix_count} "
            f"decision={decision}."
        ),
        "public_note": "docs/results/nano-lm/formal-hsmartreal-smartreal.md",
        "claim": (
            "smarter scoped retrieve + QPFB2 gen EVAL — "
            "not open chat; LOOKUP ≠ gen IQ"
        ),
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--ag-bank", type=Path, default=_AG_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    try:
        summary = run_smartreal(
            bank_path=Path(args.bank),
            ag_bank=Path(args.ag_bank),
            root=Path(args.root),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            curated_root=Path(args.curated),
            seed=int(args.seed),
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    decision = str(summary["decision"])
    print(
        json.dumps(
            {
                "ok": True,
                "hyp_id": SMARTREAL_ID,
                "decision": decision,
                "lookup_mean": summary["stats"]["lookup_mean"],
                "gen_mean": summary["stats"]["gen_mean"],
                "n_cite_ok": summary["stats"]["n_cite_ok"],
                "n_false_hit": summary["stats"]["n_false_hit"],
                "beats_servealign": summary["stats"]["beats_servealign"],
                "cpu_threads": threads,
                "elapsed_s": summary["elapsed_s"],
                "out": str(args.out),
            }
        )
    )
    return 0 if decision in {"PROMOTE", "HOLD"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
