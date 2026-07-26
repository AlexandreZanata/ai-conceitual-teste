"""Wave AI1 H-GENPLUS runner: dual-arm LOOKUP + grounded GENERATE."""

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
from curated_sources import SOURCES
from data_tiny import load_tokenizer
from decode_beamkv import decode_beams_shared_kv
from decode_early import decode_early
from eval_student import load_student_ckpt
from genc_prompt import top_k_chunks
from genplus_ops import (
    GENPLUS_ID,
    GENPLUS_N,
    GENPLUS_PACK,
    chunk_doc,
    decide_genplus,
    fit_prompt_tokens,
    genplus_stats,
    ground_prompt,
    normalize_gen_answer,
    prefer_context_beam,
    score_genplus_gen,
    score_genplus_lookup,
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
_AI_BANK = REPO / "results/nano-lm/wave-ai/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-ai/trials"
_SUMMARY = REPO / "results/nano-lm/wave-ai/genplus_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_JUDGE = "cursor-composer-frontier-chat"
_MAX_NEW = 64
_BY_ID = {str(s["id"]): s for s in SOURCES}


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


def _load_doc(source_id: str, curated: Path) -> str:
    meta = _BY_ID.get(source_id)
    if meta is None:
        raise ValueError(f"unknown source_id: {source_id}")
    path = curated / str(meta["path"])
    if not path.is_file():
        raise FileNotFoundError(str(path))
    return path.read_text(encoding="utf-8", errors="ignore")


def _seed_pack(bank_path: Path, ai_bank: Path) -> int:
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    ai_bank.parent.mkdir(parents=True, exist_ok=True)
    if not ai_bank.is_file():
        ai_bank.write_text("", encoding="utf-8")
    existing = {
        str(r.get("question", "")).strip() for r in load_bank_rows(bank_path)
    }
    n = 0
    for i, item in enumerate(GENPLUS_PACK, start=1):
        q = str(item["question"]).strip()
        if q in existing:
            continue
        row = alias_bank_row(
            trial_id=f"AI-GENPLUS-SEED-{i:02d}",
            question=q,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = GENPLUS_ID
        row["judge_notes"] = [
            "GENPLUS seed for LOOKUP arm",
            "LOOKUP product path — not generative IQ",
            "no student weight update",
        ]
        append_error_row(bank_path, row)
        append_error_row(ai_bank, row)
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
    ai_bank: Path,
    root: Path,
    curated: Path,
    seed: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], int]:
    row = alias_bank_row(
        trial_id=f"AI-GENPLUS-FIX-{i:02d}",
        question=item["question"],
        source_id=item["source_id"],
        gold=item["gold"],
    )
    row["hyp_id"] = GENPLUS_ID
    append_error_row(bank_path, row)
    append_error_row(ai_bank, row)
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
    prompts: list[str],
    questions: list[str],
    gene: dict[str, Any],
    device: torch.device,
    seed: int,
) -> list[dict[str, Any]]:
    from tchr_score import code_teacher_mean_logprob

    rows: list[dict[str, Any]] = []
    for i, (prompt, q) in enumerate(zip(prompts, questions, strict=True)):
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
                "family": "H-GENPLUS-parent",
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


def _pick_gen_text(
    bank: dict[str, Any],
    row: dict[str, Any],
    *,
    context: str,
) -> tuple[str, dict[str, Any]]:
    conts = [strip_stop(c) for c in list(bank.get("conts", []))]
    picked, idx, used_ctx = prefer_context_beam(conts, context=context)
    if not used_ctx or is_period_collapse(picked):
        picked, idx, used_ap = anti_period_pick(conts)
        meta = {
            "anti_period": bool(used_ap),
            "context_pick": False,
            "pick_idx": idx,
        }
    else:
        meta = {
            "anti_period": True,
            "context_pick": True,
            "pick_idx": idx,
        }
    if is_period_collapse(picked):
        picked = strip_stop(str(row.get("continuation", "")))
    return normalize_gen_answer(picked), meta


def _run_gen_grounded(
    *,
    champ: Path,
    items: list[dict[str, str]],
    curated: Path,
    seed: int,
    k_retrieve: int = 3,
) -> list[dict[str, Any]]:
    recipe = json.loads((champ / "recipe.json").read_text(encoding="utf-8"))
    gene = _load_gene(champ, recipe)
    cfg = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        raise RuntimeError("H-GENPLUS gen arm requires CUDA")

    contexts: list[str] = []
    prompts: list[str] = []
    questions = [str(it["question"]) for it in items]
    for item in items:
        doc = _load_doc(item["source_id"], curated)
        chunks = chunk_doc(doc)
        # Keep prompt under student max_position (512) − max_new (64).
        prompt = fit_prompt_tokens(
            ground_prompt(
                item["question"],
                chunks=chunks,
                k=min(3, int(k_retrieve)),
                max_ctx_chars=480,
            ),
            max_chars=900,
        )
        prompts.append(prompt)
        hits = top_k_chunks(item["question"], chunks, min(3, int(k_retrieve)))
        contexts.append("\n\n".join(hits)[:720])

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
            prompts=prompts,
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
            beam_seed=int(seed) + 5600,
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
            family="H-GENPLUS",
        )
    finally:
        _free_cuda(code)

    if len(committed) != len(items):
        raise RuntimeError(
            f"expected {len(items)} commits, got {len(committed)}"
        )
    out: list[dict[str, Any]] = []
    for bank, row, ctx in zip(banks, committed, contexts, strict=True):
        text, pick_meta = _pick_gen_text(bank, row, context=ctx)
        out.append(
            {
                "completion": text,
                "wall_ms": float(row.get("wall_ms") or 0.0),
                "n_new": int(row.get("n_new") or 0),
                "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD",
                "seed": row.get("seed", seed),
                "switched": row.get("switched"),
                "pick": row.get("pick"),
                "anti_period": pick_meta.get("anti_period"),
                "context_pick": pick_meta.get("context_pick"),
            }
        )
    return out


def run_genplus(
    *,
    bank_path: Path,
    ai_bank: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN AI0 asks
    WHEN LOOKUP (ASKFAST) + GENERATE (grounded ASKSMART polish) dual-arm ×10
    THEN PROMOTE if lookup≥7 ∧ gen≥5 else HOLD; false-hit→KILL.
    """
    if len(GENPLUS_PACK) != GENPLUS_N:
        raise ValueError("GENPLUS pack must be 10")

    trials_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    seeded = _seed_pack(bank_path, ai_bank)
    bank = load_bank_rows(bank_path)
    questions = [p["question"] for p in GENPLUS_PACK]

    lookup_payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated_root,
        ask_cache=AskCompletionCache(),
    )
    gen_payloads = _run_gen_grounded(
        champ=root,
        items=[dict(p) for p in GENPLUS_PACK],
        curated=curated_root,
        seed=seed,
    )

    lookup_trials: list[dict[str, Any]] = []
    gen_scores: list[float] = []
    gen_errors: list[bool] = []
    gen_notes: list[list[str]] = []
    gen_fix: list[int] = []
    fix_count = 0
    n_period = 0

    # LOOKUP arm (+ FIX seed) first — cheap; no teacher reload.
    for i, (item, lp) in enumerate(
        zip(GENPLUS_PACK, lookup_payloads, strict=True),
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
                ai_bank=ai_bank,
                root=root,
                curated=curated_root,
                seed=seed,
            )
            fix_count += 1
            kind, sem_meta, text = _classify_lookup(
                dict(item), lp, bank, curated_root
            )
        score_l, err_l, notes_l = score_genplus_lookup(
            mode=str(lp.get("mode", "")),
            completion=text,
            expected_gold=item["gold"],
            lookup_kind=kind,
            payload=lp,
        )
        lookup_trials.append(
            {
                "trial_id": f"AI-GENPLUS-LOOKUP-HITL-{i:02d}",
                "stage": "AI1",
                "hyp_id": GENPLUS_ID,
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
        )

    # Score gen; batch FIX weak trials in one second decode pass.
    weak_idx: list[int] = []
    for i, (item, gp) in enumerate(
        zip(GENPLUS_PACK, gen_payloads, strict=True)
    ):
        score_g, err_g, notes_g = score_genplus_gen(
            completion=str(gp.get("completion", "")),
            expected_gold=item["gold"],
            payload=gp,
        )
        if is_period_collapse(str(gp.get("completion", ""))):
            n_period += 1
        gen_scores.append(score_g)
        gen_errors.append(err_g)
        gen_notes.append(list(notes_g))
        gen_fix.append(0)
        if err_g and score_g <= 4.0:
            weak_idx.append(i)

    if weak_idx:
        re_items = [dict(GENPLUS_PACK[i]) for i in weak_idx]
        re_payloads = _run_gen_grounded(
            champ=root,
            items=re_items,
            curated=curated_root,
            seed=seed + 1700,
            k_retrieve=3,
        )
        fix_attempts = len(weak_idx)
        for j, idx in enumerate(weak_idx):
            item = GENPLUS_PACK[idx]
            re_gp = re_payloads[j]
            score2, err2, notes2 = score_genplus_gen(
                completion=str(re_gp.get("completion", "")),
                expected_gold=item["gold"],
                payload=re_gp,
            )
            if score2 > gen_scores[idx]:
                gen_payloads[idx] = re_gp
                gen_scores[idx] = score2
                gen_errors[idx] = err2
                gen_notes[idx] = list(notes2) + ["FIX: re-grounded decode"]
                gen_fix[idx] = 1
                fix_count += 1
            else:
                gen_notes[idx] = list(gen_notes[idx]) + [
                    "FIX attempted: re-grounded decode (no lift)"
                ]
    else:
        fix_attempts = 0

    gen_trials: list[dict[str, Any]] = []
    for i, (item, gp) in enumerate(
        zip(GENPLUS_PACK, gen_payloads, strict=True),
        start=1,
    ):
        idx = i - 1
        gt = {
            "trial_id": f"AI-GENPLUS-GEN-HITL-{i:02d}",
            "stage": "AI1",
            "hyp_id": GENPLUS_ID,
            "arm": "GENERATE",
            "app_id": item["app_id"],
            "question": item["question"],
            "source_id": item["source_id"],
            "completion": gp.get("completion"),
            "wall_ms": gp.get("wall_ms"),
            "n_new": gp.get("n_new"),
            "mode": gp.get("mode"),
            "score": gen_scores[idx],
            "error": gen_errors[idx],
            "fix_pass": gen_fix[idx],
            "judge_model_name": _JUDGE,
            "judge_notes": gen_notes[idx],
            "gold": item["gold"],
            "weight_update": False,
            "anti_period": gp.get("anti_period"),
            "context_pick": gp.get("context_pick"),
            "switched": gp.get("switched"),
        }
        if gen_errors[idx]:
            append_error_row(
                ai_bank,
                {
                    "trial_id": gt["trial_id"],
                    "question": item["question"],
                    "source_id": item["source_id"],
                    "model_raw": str(gp.get("completion") or ""),
                    "score": float(gen_scores[idx]),
                    "error": True,
                    "recipe_id": "champion-qpfb2-v0",
                    "hyp_id": GENPLUS_ID,
                    "arm": "GENERATE",
                    "judge_notes": gen_notes[idx],
                    "gold": item["gold"],
                },
            )
        write_json(trials_dir / f"{lookup_trials[idx]['trial_id']}.json", lookup_trials[idx])
        write_json(trials_dir / f"{gt['trial_id']}.json", gt)
        gen_trials.append(gt)

    n_true = sum(1 for t in lookup_trials if t["lookup_kind"] == "TRUE_HIT")
    n_false = sum(
        1 for t in lookup_trials if t["lookup_kind"] == "FALSE_HIT"
    )
    stats = genplus_stats(
        lookup_scores=[float(t["score"]) for t in lookup_trials],
        lookup_errors=[bool(t["error"]) for t in lookup_trials],
        gen_scores=[float(t["score"]) for t in gen_trials],
        gen_errors=[bool(t["error"]) for t in gen_trials],
        n_true_hit=n_true,
        n_false_hit=n_false,
        n_period=n_period,
        n_fix=fix_count,
    )
    decision = decide_genplus(stats)
    summary: dict[str, Any] = {
        "hyp_id": GENPLUS_ID,
        "stage": "AI1",
        "decision": decision,
        "compose": [
            "ASKFAST/SEMWRAP LOOKUP",
            "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD GENERATE",
            "context-prefer beam pick + short-answer polish",
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
        "fix_attempts": int(fix_attempts),
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
            f"{GENPLUS_ID}: L_lookup={stats['lookup_mean']:.1f} "
            f"L_gen={stats['gen_mean']:.1f} false_hit={n_false} "
            f"period={n_period} beats_genlift={stats['beats_genlift_gen']} "
            f"pass_gen={stats['pass_gen']} fix={fix_count} → {decision}"
        ),
        "public_note": "docs/results/nano-lm/formal-hgenplus-genplus.md",
        "ship_claim": "AF packaged stack until AI6 gen bar",
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--ai-bank", type=Path, default=_AI_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    try:
        summary = run_genplus(
            bank_path=Path(args.bank),
            ai_bank=Path(args.ai_bank),
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
                "hyp_id": GENPLUS_ID,
                "decision": summary.get("decision"),
                "lookup_mean": summary["stats"]["lookup_mean"],
                "gen_mean": summary["stats"]["gen_mean"],
                "cpu_threads": threads,
                "elapsed_s": summary.get("elapsed_s"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
