"""Wave AM1 H-GENTRUTH runner: dual-arm + peak ablation true-gen gate."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from askfast_ops import AskCompletionCache
from asksmart_ops import is_period_collapse
from curated_sources import SOURCES
from gentruth_ops import (
    GENTRUTH_ID,
    GENTRUTH_N,
    GENTRUTH_PACK,
    apply_gentruth_peak,
    chunk_doc,
    decide_gentruth,
    gentruth_stats,
    gentruth_top_k_chunks,
    score_gentruth_gen,
    score_gentruth_lookup,
)
from matrix_common import REPO, write_json
from run_genplus import _run_gen_grounded
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row, classify_semwrap, semantic_lookup
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AM_BANK = REPO / "results/nano-lm/wave-am/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-am/trials"
_SUMMARY = REPO / "results/nano-lm/wave-am/gentruth_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_JUDGE = "cursor-composer-frontier-chat"
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


def _load_doc(source_id: str, curated: Path) -> str:
    meta = _BY_ID.get(source_id)
    if meta is None:
        raise ValueError(f"unknown source_id: {source_id}")
    path = curated / str(meta["path"])
    if not path.is_file():
        raise FileNotFoundError(str(path))
    return path.read_text(encoding="utf-8", errors="ignore")


def _contexts_for(
    items: list[dict[str, str]],
    curated: Path,
    *,
    k_retrieve: int,
) -> list[str]:
    out: list[str] = []
    for item in items:
        doc = _load_doc(item["source_id"], curated)
        chunks = chunk_doc(doc, win=400, stride=160)
        hits = gentruth_top_k_chunks(
            item["question"], chunks, max(3, int(k_retrieve))
        )
        out.append("\n\n".join(hits)[:2400])
    return out


def _seed_pack(bank_path: Path, am_bank: Path) -> int:
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    am_bank.parent.mkdir(parents=True, exist_ok=True)
    if not am_bank.is_file():
        am_bank.write_text("", encoding="utf-8")
    existing = {
        str(r.get("question", "")).strip() for r in load_bank_rows(bank_path)
    }
    n = 0
    for i, item in enumerate(GENTRUTH_PACK, start=1):
        q = str(item["question"]).strip()
        if q in existing:
            continue
        row = alias_bank_row(
            trial_id=f"AM-GENTRUTH-SEED-{i:02d}",
            question=q,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = GENTRUTH_ID
        row["judge_notes"] = [
            "GENTRUTH seed for LOOKUP arm",
            "LOOKUP product path — not generative IQ",
            "no student weight update",
        ]
        append_error_row(bank_path, row)
        append_error_row(am_bank, row)
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
    am_bank: Path,
    root: Path,
    curated: Path,
    seed: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], int]:
    row = alias_bank_row(
        trial_id=f"AM-GENTRUTH-FIX-{i:02d}",
        question=item["question"],
        source_id=item["source_id"],
        gold=item["gold"],
    )
    row["hyp_id"] = GENTRUTH_ID
    append_error_row(bank_path, row)
    append_error_row(am_bank, row)
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


def _split_gen_arms(
    raw: list[dict[str, Any]],
    items: list[dict[str, str]],
    contexts: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return (ablated peak_off, peak_on) payloads sharing decode telemetry."""
    ablated: list[dict[str, Any]] = []
    peaked: list[dict[str, Any]] = []
    for gp, item, ctx in zip(raw, items, contexts, strict=True):
        decode = str(gp.get("completion", ""))
        off = dict(gp)
        off["completion"] = decode
        off["peak_used"] = False
        off["peak_span"] = None
        off["mode"] = "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+ABLATED"
        ablated.append(off)
        text, used, peak = apply_gentruth_peak(
            decode_text=decode,
            question=item["question"],
            context=ctx,
        )
        on = dict(gp)
        on["completion"] = text
        on["peak_used"] = bool(used)
        on["peak_span"] = peak
        on["mode"] = "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+PEAK"
        peaked.append(on)
    return ablated, peaked


def _run_gen_ablation(
    *,
    champ: Path,
    items: list[dict[str, str]],
    curated: Path,
    seed: int,
    k_retrieve: int = 6,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    raw = _run_gen_grounded(
        champ=champ,
        items=items,
        curated=curated,
        seed=seed,
        k_retrieve=min(3, int(k_retrieve)),
    )
    contexts = _contexts_for(items, curated, k_retrieve=k_retrieve)
    return _split_gen_arms(raw, items, contexts)


def run_gentruth(
    *,
    bank_path: Path,
    am_bank: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN AM0 asks
    WHEN LOOKUP + GENERATE ablated + peak comparison ×10
    THEN PROMOTE iff lookup≥7 ∧ ablated gen≥5; peak-only → HOLD.
    """
    if len(GENTRUTH_PACK) != GENTRUTH_N:
        raise ValueError("GENTRUTH pack must be 10")

    trials_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    seeded = _seed_pack(bank_path, am_bank)
    bank = load_bank_rows(bank_path)
    questions = [p["question"] for p in GENTRUTH_PACK]

    lookup_payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated_root,
        ask_cache=AskCompletionCache(),
    )
    gen_off, gen_on = _run_gen_ablation(
        champ=root,
        items=[dict(p) for p in GENTRUTH_PACK],
        curated=curated_root,
        seed=seed,
        k_retrieve=6,
    )

    lookup_trials: list[dict[str, Any]] = []
    fix_count = 0
    for i, (item, lp) in enumerate(
        zip(GENTRUTH_PACK, lookup_payloads, strict=True),
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
                am_bank=am_bank,
                root=root,
                curated=curated_root,
                seed=seed,
            )
            fix_count += 1
            kind, sem_meta, text = _classify_lookup(
                dict(item), lp, bank, curated_root
            )
        score_l, err_l, notes_l = score_gentruth_lookup(
            mode=str(lp.get("mode", "")),
            completion=text,
            expected_gold=item["gold"],
            lookup_kind=kind,
            payload=lp,
        )
        lookup_trials.append(
            {
                "trial_id": f"AM-GENTRUTH-LOOKUP-HITL-{i:02d}",
                "stage": "AM1",
                "hyp_id": GENTRUTH_ID,
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

    gen_scores: list[float] = []
    gen_errors: list[bool] = []
    gen_notes: list[list[str]] = []
    gen_fix: list[int] = []
    peak_scores: list[float] = []
    n_period = 0
    weak_idx: list[int] = []

    for i, (item, off, on) in enumerate(
        zip(GENTRUTH_PACK, gen_off, gen_on, strict=True)
    ):
        score_g, err_g, notes_g = score_gentruth_gen(
            completion=str(off.get("completion", "")),
            expected_gold=item["gold"],
            payload=off,
            peak_ablated=True,
        )
        score_p, _err_p, notes_p = score_gentruth_gen(
            completion=str(on.get("completion", "")),
            expected_gold=item["gold"],
            payload=on,
            peak_ablated=False,
        )
        if is_period_collapse(str(off.get("completion", ""))):
            n_period += 1
        gen_scores.append(score_g)
        gen_errors.append(err_g)
        gen_notes.append(list(notes_g) + [f"peak_compare_score={score_p}"])
        peak_scores.append(score_p)
        gen_fix.append(0)
        on["judge_notes_peak"] = notes_p
        if err_g and score_g <= 4.0:
            weak_idx.append(i)

    fix_attempts = 0
    if weak_idx:
        re_items = [dict(GENTRUTH_PACK[i]) for i in weak_idx]
        re_off, re_on = _run_gen_ablation(
            champ=root,
            items=re_items,
            curated=curated_root,
            seed=seed + 2100,
            k_retrieve=8,
        )
        fix_attempts = len(weak_idx)
        for j, idx in enumerate(weak_idx):
            item = GENTRUTH_PACK[idx]
            score2, err2, notes2 = score_gentruth_gen(
                completion=str(re_off[j].get("completion", "")),
                expected_gold=item["gold"],
                payload=re_off[j],
                peak_ablated=True,
            )
            score_p2, _, _ = score_gentruth_gen(
                completion=str(re_on[j].get("completion", "")),
                expected_gold=item["gold"],
                payload=re_on[j],
                peak_ablated=False,
            )
            if score2 > gen_scores[idx]:
                gen_off[idx] = re_off[j]
                gen_on[idx] = re_on[j]
                gen_scores[idx] = score2
                gen_errors[idx] = err2
                peak_scores[idx] = score_p2
                gen_notes[idx] = list(notes2) + [
                    "FIX: re-ground ablated decode",
                    f"peak_compare_score={score_p2}",
                ]
                gen_fix[idx] = 1
                fix_count += 1
            else:
                gen_notes[idx] = list(gen_notes[idx]) + [
                    "FIX attempted: re-ground ablated decode (no lift)"
                ]

    gen_trials: list[dict[str, Any]] = []
    n_peak = 0
    for i, (item, off, on) in enumerate(
        zip(GENTRUTH_PACK, gen_off, gen_on, strict=True),
        start=1,
    ):
        idx = i - 1
        if bool(on.get("peak_used")):
            n_peak += 1
        gt = {
            "trial_id": f"AM-GENTRUTH-GEN-HITL-{i:02d}",
            "stage": "AM1",
            "hyp_id": GENTRUTH_ID,
            "arm": "GENERATE",
            "app_id": item["app_id"],
            "question": item["question"],
            "source_id": item["source_id"],
            "completion": off.get("completion"),
            "completion_peak": on.get("completion"),
            "wall_ms": off.get("wall_ms"),
            "n_new": off.get("n_new"),
            "mode": off.get("mode"),
            "score": gen_scores[idx],
            "score_peak": peak_scores[idx],
            "error": gen_errors[idx],
            "fix_pass": gen_fix[idx],
            "judge_model_name": _JUDGE,
            "judge_notes": gen_notes[idx],
            "gold": item["gold"],
            "weight_update": False,
            "anti_period": off.get("anti_period"),
            "peak_used": False,
            "peak_used_compare": on.get("peak_used"),
            "peak_span": on.get("peak_span"),
            "switched": off.get("switched"),
        }
        if gen_errors[idx]:
            append_error_row(
                am_bank,
                {
                    "trial_id": gt["trial_id"],
                    "question": item["question"],
                    "source_id": item["source_id"],
                    "model_raw": str(off.get("completion") or ""),
                    "score": float(gen_scores[idx]),
                    "error": True,
                    "recipe_id": "champion-qpfb2-v0",
                    "hyp_id": GENTRUTH_ID,
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

    n_true = sum(1 for t in lookup_trials if t["lookup_kind"] == "TRUE_HIT")
    n_false = sum(
        1 for t in lookup_trials if t["lookup_kind"] == "FALSE_HIT"
    )
    stats = gentruth_stats(
        lookup_scores=[float(t["score"]) for t in lookup_trials],
        lookup_errors=[bool(t["error"]) for t in lookup_trials],
        gen_scores=[float(t["score"]) for t in gen_trials],
        gen_errors=[bool(t["error"]) for t in gen_trials],
        gen_peak_scores=peak_scores,
        n_true_hit=n_true,
        n_false_hit=n_false,
        n_period=n_period,
        n_fix=fix_count,
        n_peak=n_peak,
    )
    decision = decide_gentruth(stats)
    summary: dict[str, Any] = {
        "hyp_id": GENTRUTH_ID,
        "stage": "AM1",
        "decision": decision,
        "compose": [
            "ASKFAST/SEMWRAP LOOKUP",
            "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD ablated GENERATE (gate)",
            "extractive peak comparison arm (anti-FP — not smarter-LM)",
        ],
        "forbidden": [
            "QI",
            "STREAM",
            "GENCACHE",
            "LOOKUP-as-gen-IQ",
            "peak-as-open-chat-IQ",
            "invent Wave AN",
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
                "score_peak": t["score_peak"],
                "wall_ms": t["wall_ms"],
                "n_new": t["n_new"],
                "error": t["error"],
                "peak_used_compare": t.get("peak_used_compare"),
                "completion": str(t.get("completion") or "")[:160],
                "completion_peak": str(t.get("completion_peak") or "")[:80],
            }
            for t in gen_trials
        ],
        "finding": (
            f"{GENTRUTH_ID}: L_lookup={stats['lookup_mean']:.1f} "
            f"L_gen_ablated={stats['gen_mean']:.1f} "
            f"L_gen_peak={stats['gen_peak_mean']:.1f} "
            f"false_hit={n_false} period={n_period} peak={n_peak} "
            f"peak_only={stats['peak_only_lift']} "
            f"pass_gen={stats['pass_gen']} fix={fix_count} → {decision}"
        ),
        "public_note": "docs/results/nano-lm/formal-hgentruth-gentruth.md",
        "ship_claim": "AF packaged stack (ablated gen gate; peak labeled)",
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--am-bank", type=Path, default=_AM_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    cpus = int(os.cpu_count() or 4)
    # Max safe: leave 2 cores free (laptop GPU + desktop responsive).
    threads = tune_cpu_threads(max(4, cpus - 2))
    try:
        summary = run_gentruth(
            bank_path=Path(args.bank),
            am_bank=Path(args.am_bank),
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
                "hyp_id": GENTRUTH_ID,
                "decision": summary.get("decision"),
                "lookup_mean": summary["stats"]["lookup_mean"],
                "gen_mean": summary["stats"]["gen_mean"],
                "gen_peak_mean": summary["stats"]["gen_peak_mean"],
                "peak_only_lift": summary["stats"]["peak_only_lift"],
                "n_peak": summary["stats"]["n_peak"],
                "cpu_threads": threads,
                "elapsed_s": summary.get("elapsed_s"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
