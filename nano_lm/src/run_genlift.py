"""Wave AH1 H-GENLIFT runner: dual-arm LOOKUP + ASKSMART-polish GENERATE."""

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
from asksmart_ops import anti_period_pick, is_period_collapse, strip_stop
from data_tiny import load_tokenizer
from decode_beamkv import decode_beams_shared_kv
from decode_early import decode_early
from eval_student import load_student_ckpt
from genlift_ops import (
    GENLIFT_ID,
    GENLIFT_N,
    GENLIFT_PACK,
    decide_genlift,
    genlift_stats,
    score_genlift_gen,
    score_genlift_lookup,
)
from load_model import load_causal_lm, resolve_device
from matrix_common import REPO, matrix_cfg, write_json
from pfb2_ops import K2_BEAMS
from pfb_ops import PFB_TEMP
from pfb_score import attach_code_teacher, collect_beam_banks, commit_pfb_rows
from qt_quant import quantize_student_int8
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row, classify_semwrap, semantic_lookup
from tchr_ops import STORY_TEACHER_ID, code_teacher_meta
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AH_BANK = REPO / "results/nano-lm/wave-ah/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-ah/trials"
_SUMMARY = REPO / "results/nano-lm/wave-ah/genlift_summary.json"
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


def _seed_pack(bank_path: Path, ah_bank: Path) -> int:
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    ah_bank.parent.mkdir(parents=True, exist_ok=True)
    if not ah_bank.is_file():
        ah_bank.write_text("", encoding="utf-8")
    existing = {
        str(r.get("question", "")).strip() for r in load_bank_rows(bank_path)
    }
    n = 0
    for i, item in enumerate(GENLIFT_PACK, start=1):
        q = str(item["question"]).strip()
        if q in existing:
            continue
        row = alias_bank_row(
            trial_id=f"AH-GENLIFT-SEED-{i:02d}",
            question=q,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = GENLIFT_ID
        row["judge_notes"] = [
            "GENLIFT seed for LOOKUP arm",
            "LOOKUP product path — not generative IQ",
            "no student weight update",
        ]
        append_error_row(bank_path, row)
        append_error_row(ah_bank, row)
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
        item["question"], bank, curated_root=curated
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
    ah_bank: Path,
    root: Path,
    curated: Path,
    seed: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], int]:
    row = alias_bank_row(
        trial_id=f"AH-GENLIFT-FIX-{i:02d}",
        question=item["question"],
        source_id=item["source_id"],
        gold=item["gold"],
    )
    row["hyp_id"] = GENLIFT_ID
    append_error_row(bank_path, row)
    append_error_row(ah_bank, row)
    bank = load_bank_rows(bank_path)
    re_payloads = ask_many(
        questions=[item["question"]],
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
    # ASKSMART knobs: disable early-exit; keep gene temp for beams.
    return {
        **gene,
        "n": 1,
        "conf_threshold": 1.0,
        "patience": 99,
        "min_new": max(8, int(gene.get("min_new", 8))),
    }


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
        prompt = f"Question: {q}\nShort factual answer:"
        parent = decode_early(
            qt,
            tok,
            prompt,
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
        text = strip_stop(parent.text)
        p_story = float(code_teacher_mean_logprob(story, prompt, text))
        rows.append(
            {
                "family": "H-GENLIFT-parent",
                "prompt": prompt,
                "question": q,
                "continuation": text,
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


def _anti_period_commit(
    banks: list[dict[str, Any]],
    committed: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for bank, row in zip(banks, committed, strict=True):
        conts = [strip_stop(c) for c in list(bank.get("conts", []))]
        picked, idx, used = anti_period_pick(conts)
        crow = dict(row)
        if used and picked and not is_period_collapse(picked):
            crow["continuation"] = picked
            crow["anti_period"] = True
            crow["anti_period_idx"] = idx
        else:
            crow["continuation"] = strip_stop(str(row.get("continuation", "")))
            crow["anti_period"] = False
        out.append(crow)
    return out


def _run_gen_asksmart(
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
        raise RuntimeError("H-GENLIFT gen arm requires CUDA")
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
            beam_seed=int(seed) + 5500,
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
            family="H-GENLIFT",
        )
        committed = _anti_period_commit(banks, committed)
    finally:
        _free_cuda(code)

    if len(committed) != len(questions):
        raise RuntimeError(
            f"expected {len(questions)} commits, got {len(committed)}"
        )
    out: list[dict[str, Any]] = []
    for row in committed:
        text = strip_stop(str(row.get("continuation", "")))
        out.append(
            {
                "completion": text,
                "wall_ms": float(row.get("wall_ms") or 0.0),
                "n_new": int(row.get("n_new") or 0),
                "mode": "QPFB2+BEAMKV+ANTI_PERIOD",
                "seed": row.get("seed", seed),
                "switched": row.get("switched"),
                "pick": row.get("pick"),
                "anti_period": row.get("anti_period"),
            }
        )
    return out


def run_genlift(
    *,
    bank_path: Path,
    ah_bank: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN AH0 asks
    WHEN LOOKUP (ASKFAST) + GENERATE (ASKSMART polish) dual-arm ×10
    THEN PROMOTE if lookup≥7 ∧ gen≥5 else HOLD; false-hit→KILL.
    """
    if len(GENLIFT_PACK) != GENLIFT_N:
        raise ValueError("GENLIFT pack must be 10")

    trials_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    seeded = _seed_pack(bank_path, ah_bank)
    bank = load_bank_rows(bank_path)
    questions = [p["question"] for p in GENLIFT_PACK]

    lookup_payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated_root,
        ask_cache=AskCompletionCache(),
    )
    gen_payloads = _run_gen_asksmart(champ=root, questions=questions, seed=seed)

    lookup_trials: list[dict[str, Any]] = []
    gen_trials: list[dict[str, Any]] = []
    fix_count = 0
    n_period = 0
    for i, (item, lp, gp) in enumerate(
        zip(GENLIFT_PACK, lookup_payloads, gen_payloads, strict=True),
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
                ah_bank=ah_bank,
                root=root,
                curated=curated_root,
                seed=seed,
            )
            fix_count += 1
            kind, sem_meta, text = _classify_lookup(
                dict(item), lp, bank, curated_root
            )
        score_l, err_l, notes_l = score_genlift_lookup(
            mode=str(lp.get("mode", "")),
            completion=text,
            expected_gold=item["gold"],
            lookup_kind=kind,
            payload=lp,
        )
        lt = {
            "trial_id": f"AH-GENLIFT-LOOKUP-HITL-{i:02d}",
            "stage": "AH1",
            "hyp_id": GENLIFT_ID,
            "arm": "LOOKUP",
            "app_id": item["app_id"],
            "question": item["question"],
            "source_id": item["source_id"],
            "completion": lp.get("completion"),
            "wall_ms": lp.get("wall_ms"),
            "n_new": lp.get("n_new"),
            "mode": lp.get("mode"),
            "lookup_kind": kind,
            "semwrap": sem_meta,
            "score": score_l,
            "error": err_l,
            "fix_pass": fix_pass,
            "judge_model_name": _JUDGE,
            "judge_notes": notes_l,
            "gold": item["gold"],
            "weight_update": False,
        }
        score_g, err_g, notes_g = score_genlift_gen(
            completion=str(gp.get("completion", "")),
            expected_gold=item["gold"],
            payload=gp,
        )
        if is_period_collapse(str(gp.get("completion", ""))):
            n_period += 1
        gt = {
            "trial_id": f"AH-GENLIFT-GEN-HITL-{i:02d}",
            "stage": "AH1",
            "hyp_id": GENLIFT_ID,
            "arm": "GENERATE",
            "app_id": item["app_id"],
            "question": item["question"],
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
            "anti_period": gp.get("anti_period"),
            "switched": gp.get("switched"),
        }
        if err_g:
            append_error_row(
                ah_bank,
                {
                    "trial_id": gt["trial_id"],
                    "question": item["question"],
                    "source_id": item["source_id"],
                    "model_raw": str(gp.get("completion") or ""),
                    "score": float(score_g),
                    "error": True,
                    "recipe_id": "champion-qpfb2-v0",
                    "hyp_id": GENLIFT_ID,
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
    stats = genlift_stats(
        lookup_scores=[float(t["score"]) for t in lookup_trials],
        lookup_errors=[bool(t["error"]) for t in lookup_trials],
        gen_scores=[float(t["score"]) for t in gen_trials],
        gen_errors=[bool(t["error"]) for t in gen_trials],
        n_true_hit=n_true,
        n_false_hit=n_false,
        n_period=n_period,
        n_fix=fix_count,
    )
    decision = decide_genlift(stats)
    summary: dict[str, Any] = {
        "hyp_id": GENLIFT_ID,
        "stage": "AH1",
        "decision": decision,
        "compose": [
            "ASKFAST/SEMWRAP LOOKUP",
            "QPFB2+BEAMKV+ANTI_PERIOD GENERATE",
            "framed Short factual answer prompt",
        ],
        "forbidden": [
            "QI",
            "STREAM",
            "GENCACHE",
            "LOOKUP-as-gen-IQ",
            "open chat",
        ],
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
                "completion": str(t.get("completion") or "")[:160],
            }
            for t in gen_trials
        ],
        "finding": (
            f"{GENLIFT_ID}: L_lookup={stats['lookup_mean']:.1f} "
            f"L_gen={stats['gen_mean']:.1f} false_hit={n_false} "
            f"period={n_period} beats_smartreal={stats['beats_smartreal_gen']} "
            f"pass_gen={stats['pass_gen']} fix={fix_count} → {decision}"
        ),
        "public_note": "docs/results/nano-lm/formal-hgenlift-genlift.md",
        "ship_claim": "AF packaged stack until AH6 gen bar",
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--ah-bank", type=Path, default=_AH_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    try:
        summary = run_genlift(
            bank_path=Path(args.bank),
            ah_bank=Path(args.ah_bank),
            root=Path(args.root),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            curated_root=Path(args.curated),
            seed=int(args.seed),
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2

    ok = str(summary.get("decision", "")).startswith(("PROMOTE", "HOLD"))
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": GENLIFT_ID,
                "decision": summary.get("decision"),
                "lookup_mean": summary["stats"]["lookup_mean"],
                "gen_mean": summary["stats"]["gen_mean"],
                "cpu_threads": threads,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
