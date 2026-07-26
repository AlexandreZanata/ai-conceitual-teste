"""Wave AG6 AG-HITL-10 runner: final dual-arm verify (nano:ag:hitl)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from ag_hitl_ops import (
    AG6_ID,
    AG6_N,
    DECLARED_STACK,
    SHIP_CLAIM_AF,
    STACK_CLAIM,
    ag6_stats,
    claim_is_honest,
    decide_ag6,
    score_ag6_gen,
    score_ag6_lookup,
)
from ag_session_ops import AG0_PACK, overlaps_prior_questions
from antifp_ops import extract_telemetry
from askfast_ops import AskCompletionCache
from matrix_common import REPO, write_json
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row, classify_semwrap, semantic_lookup
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AG_BANK = REPO / "results/nano-lm/wave-ag/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-ag/trials"
_SUMMARY = REPO / "results/nano-lm/wave-ag/ag_hitl_summary.json"
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


def _seed_pack(bank_path: Path, ag_bank: Path) -> int:
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    ag_bank.parent.mkdir(parents=True, exist_ok=True)
    if not ag_bank.is_file():
        ag_bank.write_text("", encoding="utf-8")
    existing = {
        str(r.get("question", "")).strip() for r in load_bank_rows(bank_path)
    }
    n = 0
    for i, item in enumerate(AG0_PACK, start=1):
        q = str(item["question"]).strip()
        if q in existing:
            continue
        row = alias_bank_row(
            trial_id=f"AG-HITL-SEED-{i:02d}",
            question=q,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = AG6_ID
        row["judge_notes"] = [
            "AG6 final HITL seed",
            "LOOKUP product path — not generative IQ",
            "no student weight update",
        ]
        append_error_row(bank_path, row)
        append_error_row(ag_bank, row)
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


def run_ag_hitl(
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
    GIVEN frozen AG0 held-out asks
    WHEN final LOOKUP + GENERATE ASK→EVAL→FIX×10
    THEN lookup≥7; gen≥5 → PROMOTE else documented HOLD.
    """
    if len(AG0_PACK) != AG6_N:
        raise ValueError("AG0 pack must be 10")
    trials_dir.mkdir(parents=True, exist_ok=True)
    held_out_ok = len(overlaps_prior_questions()) == 0
    claim_ok = claim_is_honest(STACK_CLAIM)
    seeded = _seed_pack(bank_path, ag_bank)
    bank = load_bank_rows(bank_path)
    questions = [p["question"] for p in AG0_PACK]

    lookup_payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated_root,
        ask_cache=AskCompletionCache(),
    )
    # GENERATE: wrap=False open decode (wall_ms>0); not LOOKUP cache.
    gen_payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        wrap=False,
        askfast=False,
    )
    if len(lookup_payloads) != AG6_N or len(gen_payloads) != AG6_N:
        raise RuntimeError("expected 10 dual-arm payloads")

    lookup_trials: list[dict[str, Any]] = []
    gen_trials: list[dict[str, Any]] = []
    fix_count = 0
    n_gen_wall_ok = 0

    for i, (item, lp, gp) in enumerate(
        zip(AG0_PACK, lookup_payloads, gen_payloads, strict=True),
        start=1,
    ):
        kind, sem_meta = _classify(dict(item), lp, bank, curated_root)
        fix_pass = 0
        if kind != "TRUE_HIT":
            row = alias_bank_row(
                trial_id=f"AG-FINAL-FIX-{i:02d}",
                question=item["question"],
                source_id=item["source_id"],
                gold=item["gold"],
            )
            row["hyp_id"] = AG6_ID
            append_error_row(bank_path, row)
            append_error_row(ag_bank, row)
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

        l_score, l_err, l_notes = score_ag6_lookup(
            mode=str(lp.get("mode", "")),
            completion=str(lp.get("completion", "")),
            expected_gold=str(item["gold"]),
            lookup_kind=kind,
            payload=lp,
        )
        l_tel = extract_telemetry(lp)
        lt = {
            "trial_id": f"AG-FINAL-LOOKUP-HITL-{i:02d}",
            "stage": "AG6",
            "hyp_id": AG6_ID,
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
        g_score, g_err, g_notes = score_ag6_gen(
            completion=str(gp.get("completion", "")),
            expected_gold=str(item["gold"]),
            payload=gp,
        )
        gt = {
            "trial_id": f"AG-FINAL-GEN-HITL-{i:02d}",
            "stage": "AG6",
            "hyp_id": AG6_ID,
            "arm": "GENERATE",
            "app_id": item["app_id"],
            "question": item["question"],
            "source_id": item["source_id"],
            "completion": gp.get("completion"),
            "mode": g_tel["mode"],
            "wall_ms": g_tel["wall_ms"],
            "n_new": g_tel["n_new"],
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
    n_known = sum(1 for p in AG0_PACK if p["app_id"] == "known-ask")
    n_howto = sum(1 for p in AG0_PACK if p["app_id"] == "howto")
    n_long = sum(1 for p in AG0_PACK if p["app_id"] == "long-doc")
    stats = ag6_stats(
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
        n_known=n_known,
        n_howto=n_howto,
        n_long=n_long,
    )
    decision = decide_ag6(stats)
    ship = (
        STACK_CLAIM
        if decision == "PROMOTE" and bool(stats["pass_gen"])
        else SHIP_CLAIM_AF
    )
    summary: dict[str, Any] = {
        "hyp_id": AG6_ID,
        "stage": "AG6",
        "decision": decision,
        "compose": list(DECLARED_STACK),
        "forbidden": [
            "STREAM",
            "KVCACHE-Q",
            "GENCACHE",
            "LOOKUP-only smarter LM",
            "open chat claim",
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
            }
            for t in gen_trials
        ],
        "finding": (
            f"{AG6_ID}: L={stats['lookup_mean']:.1f} "
            f"G={stats['gen_mean']:.1f} "
            f"wall_ok={n_gen_wall_ok}/10 "
            f"false_hit={n_false} fix={fix_count} "
            f"decision={decision}."
        ),
        "public_note": "docs/results/nano-lm/wave-ag-hitl.md",
        "claim": ship,
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
        summary = run_ag_hitl(
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
    st = summary["stats"]
    print(
        json.dumps(
            {
                "ok": True,
                "hyp_id": AG6_ID,
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
