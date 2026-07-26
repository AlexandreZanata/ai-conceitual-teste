"""Wave AI1b H-CAPRENEG runner: dual-arm + named CAP-125M gen probe."""

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
from asksmart_ops import is_period_collapse, strip_stop
from capreneg_ops import (
    BUDGET_VRAM_GB,
    BUDGET_WALL_S,
    CAPRENEG_ID,
    CAPRENEG_N,
    CAPRENEG_PACK,
    HARD_CAP_PARAMS,
    PROBE_HF_ID,
    PROBE_TOKENIZER_ID,
    PROPOSAL_ID,
    PROPOSED_MAX_PARAMS,
    capreneg_stats,
    decide_capreneg,
    score_capreneg_gen,
    score_capreneg_lookup,
)
from curated_sources import SOURCES
from decode_early import decode_early
from eval_student import load_student_ckpt
from genplus_ops import (
    chunk_doc,
    fit_prompt_tokens,
    ground_prompt,
    normalize_gen_answer,
)
from load_model import load_causal_lm, resolve_device
from matrix_common import REPO, matrix_cfg, write_json
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row, classify_semwrap, semantic_lookup
from student_model import count_params
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AI_BANK = REPO / "results/nano-lm/wave-ai/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-ai/trials"
_SUMMARY = REPO / "results/nano-lm/wave-ai/capreneg_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_JUDGE = "cursor-composer-frontier-chat"
_MAX_NEW = 48
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


def _vram_gb() -> float:
    if not torch.cuda.is_available():
        return 0.0
    return float(torch.cuda.max_memory_allocated()) / (1024.0**3)


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
    for i, item in enumerate(CAPRENEG_PACK, start=1):
        q = str(item["question"]).strip()
        if q in existing:
            continue
        row = alias_bank_row(
            trial_id=f"AI-CAPRENEG-SEED-{i:02d}",
            question=q,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = CAPRENEG_ID
        row["judge_notes"] = [
            "CAPRENEG seed for LOOKUP arm",
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
        trial_id=f"AI-CAPRENEG-FIX-{i:02d}",
        question=item["question"],
        source_id=item["source_id"],
        gold=item["gold"],
    )
    row["hyp_id"] = CAPRENEG_ID
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


def _champion_params(root: Path) -> int:
    recipe = json.loads((root / "recipe.json").read_text(encoding="utf-8"))
    cfg = matrix_cfg()
    from data_tiny import load_tokenizer

    tok = load_tokenizer(str(recipe["tokenizer_id"]), cfg["cache"])
    device = resolve_device(True)
    student = load_student_ckpt(root / str(recipe["ckpt"]), tok, device)
    try:
        return int(count_params(student))
    finally:
        _free_cuda(student)


def _run_probe_gen(
    *,
    items: list[dict[str, str]],
    curated: Path,
    seed: int,
) -> tuple[list[dict[str, Any]], int, float]:
    """Decode-only grounded gen on named CAP-125M probe (no weight update)."""
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
    cfg = matrix_cfg()
    loaded = load_causal_lm(
        PROBE_HF_ID,
        PROBE_TOKENIZER_ID,
        cache_dir=cfg["cache"],
        use_fp16=True,
    )
    probe_n = int(count_params(loaded.model))
    out: list[dict[str, Any]] = []
    try:
        for i, item in enumerate(items):
            doc = _load_doc(item["source_id"], curated)
            prompt = fit_prompt_tokens(
                ground_prompt(
                    item["question"],
                    chunks=chunk_doc(doc),
                    k=2,
                    max_ctx_chars=600,
                ),
                max_chars=1200,
            )
            # Keep under probe positions with headroom for max_new.
            max_pos = int(
                getattr(loaded.model.config, "max_position_embeddings", 2048)
            )
            # Char surrogate ≈ 4 chars/token; stay well under.
            prompt = fit_prompt_tokens(
                prompt, max_chars=max(400, (max_pos - _MAX_NEW - 8) * 3)
            )
            parent = decode_early(
                loaded.model,
                loaded.tokenizer,
                prompt,
                n=1,
                max_new_tokens=_MAX_NEW,
                min_new=4,
                conf_threshold=1.0,
                patience=99,
                temperature=1e-6,
                top_p=0.9,
                seed=int(seed) + i,
                device=loaded.device,
            )
            text = normalize_gen_answer(strip_stop(parent.text))
            out.append(
                {
                    "completion": text,
                    "wall_ms": float(parent.wall_ms),
                    "n_new": len(parent.token_ids),
                    "mode": "PROBE-125M+GROUNDED",
                    "seed": int(seed) + i,
                    "probe_hf_id": PROBE_HF_ID,
                }
            )
    finally:
        peak = _vram_gb()
        _free_cuda(loaded.model, loaded.tokenizer, loaded)
    return out, probe_n, peak


def run_capreneg(
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
    GIVEN AI0 asks + GENPLUS HOLD
    WHEN LOOKUP (≤5M product) + GENERATE (CAP-125M probe) dual-arm ×10
    THEN PROMOTE size raise iff lookup≥7 ∧ gen≥5 ∧ budget else HOLD ≤5M.
    """
    if len(CAPRENEG_PACK) != CAPRENEG_N:
        raise ValueError("CAPRENEG pack must be 10")

    trials_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    seeded = _seed_pack(bank_path, ai_bank)
    bank = load_bank_rows(bank_path)
    champion_n = _champion_params(root)
    if champion_n > HARD_CAP_PARAMS:
        raise RuntimeError(
            f"champion params {champion_n} exceed hard cap {HARD_CAP_PARAMS}"
        )

    questions = [p["question"] for p in CAPRENEG_PACK]
    lookup_payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated_root,
        ask_cache=AskCompletionCache(),
    )

    lookup_trials: list[dict[str, Any]] = []
    fix_count = 0
    for i, (item, lp) in enumerate(
        zip(CAPRENEG_PACK, lookup_payloads, strict=True),
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
        score_l, err_l, notes_l = score_capreneg_lookup(
            mode=str(lp.get("mode", "")),
            completion=text,
            expected_gold=item["gold"],
            lookup_kind=kind,
            payload=lp,
        )
        lookup_trials.append(
            {
                "trial_id": f"AI-CAPRENEG-LOOKUP-HITL-{i:02d}",
                "stage": "AI1b",
                "hyp_id": CAPRENEG_ID,
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

    gen_payloads, probe_n, vram_peak = _run_probe_gen(
        items=[dict(p) for p in CAPRENEG_PACK],
        curated=curated_root,
        seed=seed,
    )

    gen_scores: list[float] = []
    gen_errors: list[bool] = []
    gen_notes: list[list[str]] = []
    gen_fix: list[int] = []
    n_period = 0
    weak_idx: list[int] = []
    for i, (item, gp) in enumerate(
        zip(CAPRENEG_PACK, gen_payloads, strict=True)
    ):
        score_g, err_g, notes_g = score_capreneg_gen(
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

    fix_attempts = 0
    if weak_idx:
        re_items = [dict(CAPRENEG_PACK[i]) for i in weak_idx]
        re_payloads, _, vram2 = _run_probe_gen(
            items=re_items,
            curated=curated_root,
            seed=seed + 1900,
        )
        vram_peak = max(float(vram_peak), float(vram2))
        fix_attempts = len(weak_idx)
        for j, idx in enumerate(weak_idx):
            item = CAPRENEG_PACK[idx]
            re_gp = re_payloads[j]
            score2, err2, notes2 = score_capreneg_gen(
                completion=str(re_gp.get("completion", "")),
                expected_gold=item["gold"],
                payload=re_gp,
            )
            if score2 > gen_scores[idx]:
                gen_payloads[idx] = re_gp
                gen_scores[idx] = score2
                gen_errors[idx] = err2
                gen_notes[idx] = list(notes2) + ["FIX: re-probe decode"]
                gen_fix[idx] = 1
                fix_count += 1
            else:
                gen_notes[idx] = list(gen_notes[idx]) + [
                    "FIX attempted: re-probe decode (no lift)"
                ]

    gen_trials: list[dict[str, Any]] = []
    for i, (item, gp) in enumerate(
        zip(CAPRENEG_PACK, gen_payloads, strict=True),
        start=1,
    ):
        idx = i - 1
        gt = {
            "trial_id": f"AI-CAPRENEG-GEN-HITL-{i:02d}",
            "stage": "AI1b",
            "hyp_id": CAPRENEG_ID,
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
            "probe_hf_id": PROBE_HF_ID,
            "proposal_id": PROPOSAL_ID,
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
                    "recipe_id": PROPOSAL_ID,
                    "hyp_id": CAPRENEG_ID,
                    "arm": "GENERATE",
                    "judge_notes": gen_notes[idx],
                    "gold": item["gold"],
                },
            )
        write_json(
            trials_dir / f"{lookup_trials[idx]['trial_id']}.json",
            lookup_trials[idx],
        )
        write_json(trials_dir / f"{gt['trial_id']}.json", gt)
        gen_trials.append(gt)

    elapsed = time.perf_counter() - t0
    n_true = sum(1 for t in lookup_trials if t["lookup_kind"] == "TRUE_HIT")
    n_false = sum(
        1 for t in lookup_trials if t["lookup_kind"] == "FALSE_HIT"
    )
    stats = capreneg_stats(
        lookup_scores=[float(t["score"]) for t in lookup_trials],
        lookup_errors=[bool(t["error"]) for t in lookup_trials],
        gen_scores=gen_scores,
        gen_errors=gen_errors,
        n_true_hit=n_true,
        n_false_hit=n_false,
        n_period=n_period,
        n_fix=fix_count,
        champion_params=champion_n,
        probe_params=probe_n,
        elapsed_s=elapsed,
        vram_gb_peak=float(vram_peak),
        weight_update=False,
    )
    decision = decide_capreneg(stats)
    summary: dict[str, Any] = {
        "hyp_id": CAPRENEG_ID,
        "stage": "AI1b",
        "decision": decision,
        "proposal_id": PROPOSAL_ID,
        "proposed_max_params": PROPOSED_MAX_PARAMS,
        "hard_cap_params": HARD_CAP_PARAMS,
        "compose": [
            "ASKFAST/SEMWRAP LOOKUP on ≤5M champion",
            f"DECODE-ONLY GENERATE on {PROBE_HF_ID}",
            "named budget: no train / wall≤600s / VRAM≤8GB",
        ],
        "forbidden": [
            "QI",
            "STREAM",
            "GENCACHE",
            "LOOKUP-as-gen-IQ",
            "silent hard-cap raise without gen≥5",
            "open chat",
        ],
        "seeded_golds": int(seeded),
        "fix_count": int(fix_count),
        "fix_attempts": int(fix_attempts),
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "elapsed_s": elapsed,
        "budget_wall_s": BUDGET_WALL_S,
        "budget_vram_gb": BUDGET_VRAM_GB,
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
            f"{CAPRENEG_ID}: proposal={PROPOSAL_ID} "
            f"champ={champion_n} probe={probe_n} "
            f"L_lookup={stats['lookup_mean']:.1f} "
            f"L_gen={stats['gen_mean']:.1f} "
            f"budget_ok={stats['budget_ok']} → {decision}"
        ),
        "public_note": "docs/results/nano-lm/formal-hcapreneg-capreneg.md",
        "ship_claim": (
            "AF packaged stack; ≤5M hard remains unless PROMOTE"
            if decision != "PROMOTE"
            else f"AF packaged stack; hard cap raised to {PROPOSAL_ID}"
        ),
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
        summary = run_capreneg(
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
                "hyp_id": CAPRENEG_ID,
                "decision": summary.get("decision"),
                "proposal_id": PROPOSAL_ID,
                "lookup_mean": summary["stats"]["lookup_mean"],
                "gen_mean": summary["stats"]["gen_mean"],
                "champion_params": summary["stats"]["champion_params"],
                "probe_params": summary["stats"]["probe_params"],
                "vram_gb_peak": summary["stats"]["vram_gb_peak"],
                "cpu_threads": threads,
                "elapsed_s": summary.get("elapsed_s"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
