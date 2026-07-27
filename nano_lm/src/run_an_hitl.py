"""Wave AN6 AN-HITL-10 runner: final dual-arm verify (nano:an:hitl)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from an_hitl_ops import (
    AN6_ID,
    AN6_N,
    DECLARED_STACK,
    SHIP_CLAIM_AF,
    STACK_CLAIM,
    an6_stats,
    claim_is_honest,
    decide_an6,
    score_an6_gen,
    score_an6_lookup,
)
from an_session_ops import AN0_PACK, overlaps_prior_questions, pack_app_counts
from antifp_ops import extract_telemetry
from askfast_ops import AskCompletionCache
from matrix_common import REPO, write_json
from run_genedge import _run_gen_ablation
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row, classify_semwrap, semantic_lookup
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AN_BANK = REPO / "results/nano-lm/wave-an/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-an/trials"
_SUMMARY = REPO / "results/nano-lm/wave-an/an_hitl_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_JUDGE = "cursor-composer-frontier-chat"


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


def _seed_pack(bank_path: Path, an_bank: Path) -> int:
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    an_bank.parent.mkdir(parents=True, exist_ok=True)
    if not an_bank.is_file():
        an_bank.write_text("", encoding="utf-8")
    existing = {
        str(r.get("question", "")).strip() for r in load_bank_rows(bank_path)
    }
    n = 0
    for i, item in enumerate(AN0_PACK, start=1):
        q = str(item["question"]).strip()
        if q in existing:
            continue
        row = alias_bank_row(
            trial_id=f"AN-HITL-SEED-{i:02d}",
            question=q,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = AN6_ID
        row["judge_notes"] = [
            "AN6 final HITL seed",
            "LOOKUP product path — not generative IQ",
            "no student weight update",
        ]
        append_error_row(bank_path, row)
        append_error_row(an_bank, row)
        existing.add(q)
        n += 1
    return n


def _classify(
    item: dict[str, str],
    payload: dict[str, Any],
    bank: list[dict[str, Any]],
    curated: Path,
) -> tuple[str, dict[str, Any]]:
    mode = str(payload.get("mode", ""))
    _g, meta = semantic_lookup(
        item["question"], bank, curated_root=curated
    )
    looked = (
        str(payload.get("completion"))
        if mode in {"SEMWRAP_LOOKUP", "WRAP_LOOKUP", "ASKFAST_CACHE"}
        else _g
    )
    kind = classify_semwrap(
        looked,
        expected_gold=item["gold"],
        expected_source_id=item["source_id"],
        hit_source_id=str(meta.get("source_id") or "") or None,
    )
    return kind, meta


def run_an_hitl(
    *,
    bank_path: Path,
    an_bank: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN frozen AN0 held-out asks
    WHEN final LOOKUP + GENEDGE peak GENERATE ASK→EVAL→FIX×10
    THEN lookup≥7; gen≥5 → PROMOTE else documented HOLD.
    """
    if len(AN0_PACK) != AN6_N:
        raise ValueError("AN0 pack must be 10")
    trials_dir.mkdir(parents=True, exist_ok=True)
    held_out_ok = len(overlaps_prior_questions()) == 0
    claim_ok = claim_is_honest(STACK_CLAIM)
    seeded = _seed_pack(bank_path, an_bank)
    bank = load_bank_rows(bank_path)
    questions = [p["question"] for p in AN0_PACK]

    lookup_payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated_root,
        ask_cache=AskCompletionCache(),
    )
    gen_items = [dict(p) for p in AN0_PACK]
    _ablated, gen_payloads = _run_gen_ablation(
        champ=root,
        items=gen_items,
        curated=curated_root,
        seed=seed,
        k_retrieve=6,
    )
    del _ablated
    if len(lookup_payloads) != AN6_N or len(gen_payloads) != AN6_N:
        raise RuntimeError("expected 10 dual-arm payloads")

    lookup_trials: list[dict[str, Any]] = []
    gen_trials: list[dict[str, Any]] = []
    fix_count = 0
    n_gen_wall_ok = 0

    for i, (item, lp, gp) in enumerate(
        zip(AN0_PACK, lookup_payloads, gen_payloads, strict=True),
        start=1,
    ):
        kind, sem_meta = _classify(dict(item), lp, bank, curated_root)
        fix_pass = 0
        if kind != "TRUE_HIT":
            row = alias_bank_row(
                trial_id=f"AN-FINAL-FIX-{i:02d}",
                question=item["question"],
                source_id=item["source_id"],
                gold=item["gold"],
            )
            row["hyp_id"] = AN6_ID
            append_error_row(bank_path, row)
            append_error_row(an_bank, row)
            bank = load_bank_rows(bank_path)
            fix_count += 1
            fix_pass = 1
            lp = ask_many(
                questions=[item["question"]],
                root=root,
                seed=seed,
                askfast=True,
                bank_path=bank_path,
                curated_root=curated_root,
                ask_cache=AskCompletionCache(),
            )[0]
            kind, sem_meta = _classify(dict(item), lp, bank, curated_root)

        l_score, l_err, l_notes = score_an6_lookup(
            mode=str(lp.get("mode", "")),
            completion=str(lp.get("completion", "")),
            expected_gold=str(item["gold"]),
            lookup_kind=kind,
            payload=lp,
        )
        l_tel = extract_telemetry(lp)
        lt = {
            "trial_id": f"AN-FINAL-LOOKUP-HITL-{i:02d}",
            "stage": "AN6",
            "hyp_id": AN6_ID,
            "arm": "LOOKUP",
            "app_id": item["app_id"],
            "question": item["question"],
            "source_id": item["source_id"],
            "completion": lp.get("completion"),
            "mode": l_tel["mode"],
            "wall_ms": l_tel["wall_ms"],
            "n_new": l_tel["n_new"],
            "lookup_kind": kind,
            "semwrap": sem_meta,
            "score": l_score,
            "error": l_err,
            "fix_pass": fix_pass,
            "judge_model_name": _JUDGE,
            "judge_notes": l_notes,
            "gold": str(item["gold"]).strip(),
            "weight_update": False,
        }
        write_json(trials_dir / f"{lt['trial_id']}.json", lt)
        lookup_trials.append(lt)

        g_tel = extract_telemetry(gp)
        if g_tel["wall_ms"] > 0.0 and g_tel["n_new"] > 0:
            n_gen_wall_ok += 1
        g_score, g_err, g_notes = score_an6_gen(
            completion=str(gp.get("completion", "")),
            expected_gold=str(item["gold"]),
            payload=gp,
        )
        gt = {
            "trial_id": f"AN-FINAL-GEN-HITL-{i:02d}",
            "stage": "AN6",
            "hyp_id": AN6_ID,
            "arm": "GENERATE",
            "app_id": item["app_id"],
            "question": item["question"],
            "source_id": item["source_id"],
            "completion": gp.get("completion"),
            "mode": g_tel["mode"],
            "wall_ms": g_tel["wall_ms"],
            "n_new": g_tel["n_new"],
            "peak_used": bool(gp.get("peak_used")),
            "score": g_score,
            "error": g_err,
            "fix_pass": 0,
            "judge_model_name": _JUDGE,
            "judge_notes": g_notes,
            "gold": str(item["gold"]).strip(),
            "weight_update": False,
        }
        write_json(trials_dir / f"{gt['trial_id']}.json", gt)
        gen_trials.append(gt)

    n_true = sum(
        1 for t in lookup_trials if t["lookup_kind"] == "TRUE_HIT"
    )
    n_false = sum(
        1 for t in lookup_trials if t["lookup_kind"] == "FALSE_HIT"
    )
    counts = pack_app_counts()
    stats = an6_stats(
        lookup_scores=[float(t["score"]) for t in lookup_trials],
        lookup_errors=[bool(t["error"]) for t in lookup_trials],
        gen_scores=[float(t["score"]) for t in gen_trials],
        gen_errors=[bool(t["error"]) for t in gen_trials],
        n_true_hit=n_true,
        n_false_hit=n_false,
        n_gen_wall_ok=n_gen_wall_ok,
        n_fix=fix_count,
        claim_ok=claim_ok,
        held_out_ok=held_out_ok,
        n_known=int(counts.get("known-ask", 0)),
        n_howto=int(counts.get("howto", 0)),
        n_long=int(counts.get("long-doc", 0)),
    )
    decision = decide_an6(stats)
    ship = (
        STACK_CLAIM
        if decision == "PROMOTE" and bool(stats["pass_gen"])
        else SHIP_CLAIM_AF
    )
    summary: dict[str, Any] = {
        "hyp_id": AN6_ID,
        "stage": "AN6",
        "decision": decision,
        "compose": list(DECLARED_STACK),
        "forbidden": [
            "STREAM",
            "KVCACHE-Q",
            "GENCACHE",
            "LOOKUP-only smarter LM",
            "open chat claim",
            "peak-as-open-chat-IQ",
            "invent Wave AO",
        ],
        "seeded_golds": int(seeded),
        "fix_count": int(fix_count),
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "stats": stats,
        "ship_claim": ship,
        "lookup_trials": [
            {
                "trial_id": t["trial_id"],
                "app_id": t["app_id"],
                "mode": t["mode"],
                "lookup_kind": t["lookup_kind"],
                "score": t["score"],
                "error": t["error"],
                "wall_ms": t["wall_ms"],
            }
            for t in lookup_trials
        ],
        "gen_trials": [
            {
                "trial_id": t["trial_id"],
                "app_id": t["app_id"],
                "mode": t["mode"],
                "score": t["score"],
                "error": t["error"],
                "wall_ms": t["wall_ms"],
                "n_new": t["n_new"],
                "peak_used": t.get("peak_used"),
                "completion": str(t.get("completion") or "")[:80],
            }
            for t in gen_trials
        ],
        "finding": (
            f"{AN6_ID}: L={stats['lookup_mean']:.1f} "
            f"G={stats['gen_mean']:.1f} "
            f"wall_ok={n_gen_wall_ok}/10 "
            f"false_hit={n_false} fix={fix_count} "
            f"held_out={held_out_ok} → {decision}"
        ),
        "public_note": "docs/results/nano-lm/wave-an-hitl.md",
        "claim": ship,
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--an-bank", type=Path, default=_AN_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    cpus = int(os.cpu_count() or 4)
    # Max safe: leave 2 cores free (CUDA gen + LOOKUP).
    threads = tune_cpu_threads(max(4, cpus - 2))
    try:
        summary = run_an_hitl(
            bank_path=Path(args.bank),
            an_bank=Path(args.an_bank),
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
    st = summary["stats"]
    print(
        json.dumps(
            {
                "ok": True,
                "hyp_id": AN6_ID,
                "decision": decision,
                "lookup_mean": st["lookup_mean"],
                "gen_mean": st["gen_mean"],
                "n_false_hit": st["n_false_hit"],
                "n_gen_wall_ok": st["n_gen_wall_ok"],
                "pass_lookup": st["pass_lookup"],
                "pass_gen": st["pass_gen"],
                "held_out_ok": st["held_out_ok"],
                "ship_claim": summary["ship_claim"],
                "fix_count": summary["fix_count"],
                "cpu_threads": threads,
                "out": str(args.out),
            }
        )
    )
    return 0 if decision in {"PROMOTE", "HOLD"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
