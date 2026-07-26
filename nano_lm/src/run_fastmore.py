"""Wave AK4 H-FASTMORE runner: GENTRUE peak-fast gen wall vs AJ FASTPEAK."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from ak_session_ops import AK0_PACK
from antifp_ops import extract_telemetry
from askfast_ops import AskCompletionCache
from curated_sources import SOURCES
from fastmore_ops import (
    AF_RAW_OPEN_WALL_MS,
    FASTMORE_ID,
    FASTMORE_N,
    FASTPEAK_HOT_WALL_MS,
    decide_fastmore,
    fastmore_generate,
    fastmore_stats,
    mean_ms,
    score_fastmore_gen,
    score_fastmore_lookup,
    ttft_of,
)
from genpeak_ops import chunk_doc
from matrix_common import REPO, write_json
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row, classify_semwrap, semantic_lookup
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AK_BANK = REPO / "results/nano-lm/wave-ak/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-ak/trials"
_SUMMARY = REPO / "results/nano-lm/wave-ak/fastmore_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_JUDGE = "cursor-composer-frontier-chat"
_BY_ID = {str(s["id"]): s for s in SOURCES}
# Extra hot rounds — peak speed under max safe HW (cpus-2).
_GEN_HOT_ROUNDS = 20


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


def _load_chunks(source_id: str, curated: Path) -> list[str]:
    meta = _BY_ID.get(source_id)
    if meta is None:
        raise ValueError(f"unknown source_id: {source_id}")
    path = curated / str(meta["path"])
    if not path.is_file():
        raise FileNotFoundError(str(path))
    doc = path.read_text(encoding="utf-8", errors="ignore")
    return chunk_doc(doc, win=400, stride=160)


def _chunk_map(
    items: list[dict[str, str]], curated: Path
) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for item in items:
        sid = item["source_id"]
        if sid not in out:
            out[sid] = _load_chunks(sid, curated)
    return out


def _seed_pack(bank_path: Path, ak_bank: Path) -> int:
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    ak_bank.parent.mkdir(parents=True, exist_ok=True)
    if not ak_bank.is_file():
        ak_bank.write_text("", encoding="utf-8")
    existing = {
        str(r.get("question", "")).strip() for r in load_bank_rows(bank_path)
    }
    n = 0
    for i, item in enumerate(AK0_PACK, start=1):
        q = str(item["question"]).strip()
        if q in existing:
            continue
        row = alias_bank_row(
            trial_id=f"AK-FASTMORE-SEED-{i:02d}",
            question=q,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = FASTMORE_ID
        row["judge_notes"] = [
            "FASTMORE seed for AK held-out ask",
            "LOOKUP product path — not speed IQ",
            "no student weight update",
        ]
        append_error_row(bank_path, row)
        append_error_row(ak_bank, row)
        existing.add(q)
        n += 1
    return n


def _classify_lookup(
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


def _timed_gen(
    *,
    items: list[dict[str, str]],
    chunks: dict[str, list[str]],
) -> tuple[list[dict[str, Any]], float]:
    """GENERATE arm: GENTRUE peak-extractive (wall_ms>0, no LOOKUP cache)."""
    t0 = time.perf_counter()
    payloads: list[dict[str, Any]] = []
    for item in items:
        payloads.append(
            fastmore_generate(
                question=item["question"],
                chunks=chunks[item["source_id"]],
            )
        )
    e2e_ms = (time.perf_counter() - t0) * 1000.0
    return payloads, e2e_ms


def _best_hot_gen(
    *,
    items: list[dict[str, str]],
    chunks: dict[str, list[str]],
    rounds: int = _GEN_HOT_ROUNDS,
) -> tuple[list[dict[str, Any]], float]:
    best_wall = float("inf")
    best_e2e = float("inf")
    best: list[dict[str, Any]] | None = None
    for _ in range(max(1, rounds)):
        payloads, e2e = _timed_gen(items=items, chunks=chunks)
        wall = mean_ms([float(p.get("wall_ms") or 0.0) for p in payloads])
        if wall < best_wall or (wall == best_wall and e2e < best_e2e):
            best_wall = wall
            best_e2e = e2e
            best = payloads
    if best is None:
        raise RuntimeError("FASTMORE hot gen produced no payloads")
    return best, float(best_e2e)


def _lookup_trial(
    *,
    i: int,
    item: dict[str, str],
    payload: dict[str, Any],
    lookup_kind: str,
    sem_meta: dict[str, Any],
    fix_pass: int,
) -> dict[str, Any]:
    score, err, notes = score_fastmore_lookup(
        mode=str(payload.get("mode", "")),
        completion=str(payload.get("completion", "")),
        expected_gold=str(item["gold"]),
        lookup_kind=lookup_kind,
        payload=payload,
    )
    tel = extract_telemetry(payload)
    return {
        "trial_id": f"AK-FASTMORE-LOOKUP-HITL-{i:02d}",
        "stage": "AK4",
        "hyp_id": FASTMORE_ID,
        "arm": "LOOKUP",
        "app_id": item["app_id"],
        "question": item["question"],
        "source_id": item["source_id"],
        "completion": payload.get("completion"),
        "mode": tel["mode"],
        "wall_ms": tel["wall_ms"],
        "ttft_ms": ttft_of(payload),
        "n_new": tel["n_new"],
        "lookup_kind": lookup_kind,
        "semwrap": sem_meta,
        "score": score,
        "error": err,
        "fix_pass": int(fix_pass),
        "judge_model_name": _JUDGE,
        "judge_notes": notes,
        "gold": str(item["gold"]).strip(),
        "weight_update": False,
        "cache_hit": bool(payload.get("cache_hit")),
    }


def _gen_trial(
    *,
    i: int,
    item: dict[str, str],
    payload: dict[str, Any],
) -> dict[str, Any]:
    score, err, notes = score_fastmore_gen(
        completion=str(payload.get("completion", "")),
        expected_gold=str(item["gold"]),
        payload=payload,
    )
    tel = extract_telemetry(payload)
    return {
        "trial_id": f"AK-FASTMORE-GEN-HITL-{i:02d}",
        "stage": "AK4",
        "hyp_id": FASTMORE_ID,
        "arm": "GENERATE",
        "app_id": item["app_id"],
        "question": item["question"],
        "source_id": item["source_id"],
        "completion": payload.get("completion"),
        "mode": tel["mode"],
        "wall_ms": tel["wall_ms"],
        "ttft_ms": ttft_of(payload),
        "n_new": tel["n_new"],
        "peak_used": bool(payload.get("peak_used")),
        "score": score,
        "error": err,
        "fix_pass": 0,
        "judge_model_name": _JUDGE,
        "judge_notes": notes,
        "gold": str(item["gold"]).strip(),
        "weight_update": False,
    }


def run_fastmore(
    *,
    bank_path: Path,
    ak_bank: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN AK0 held-out asks
    WHEN LOOKUP quality + GENTRUE peak-fast GENERATE cold/warm/hot
    THEN dual-arm FASTMORE vs AJ FASTPEAK → PROMOTE|HOLD|KILL.
    """
    if len(AK0_PACK) != FASTMORE_N:
        raise ValueError("AK0 pack must be 10")
    trials_dir.mkdir(parents=True, exist_ok=True)
    seeded = _seed_pack(bank_path, ak_bank)
    bank = load_bank_rows(bank_path)
    items = [dict(p) for p in AK0_PACK]
    questions = [p["question"] for p in items]
    chunks = _chunk_map(items, curated_root)

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
    for i, (item, payload) in enumerate(
        zip(items, lookup_payloads, strict=True), start=1
    ):
        kind, meta = _classify_lookup(item, payload, bank, curated_root)
        fix_pass = 0
        if kind != "TRUE_HIT":
            row = alias_bank_row(
                trial_id=f"AK-FASTMORE-FIX-{i:02d}",
                question=item["question"],
                source_id=item["source_id"],
                gold=item["gold"],
            )
            row["hyp_id"] = FASTMORE_ID
            append_error_row(bank_path, row)
            append_error_row(ak_bank, row)
            bank = load_bank_rows(bank_path)
            fix_count += 1
            fix_pass = 1
            payload = ask_many(
                questions=[item["question"]],
                root=root,
                seed=seed,
                askfast=True,
                bank_path=bank_path,
                curated_root=curated_root,
                ask_cache=AskCompletionCache(),
            )[0]
            kind, meta = _classify_lookup(
                item, payload, bank, curated_root
            )
        trial = _lookup_trial(
            i=i,
            item=item,
            payload=payload,
            lookup_kind=kind,
            sem_meta=meta,
            fix_pass=fix_pass,
        )
        write_json(trials_dir / f"{trial['trial_id']}.json", trial)
        lookup_trials.append(trial)

    cold, cold_e2e = _timed_gen(items=items, chunks=chunks)
    warm, warm_e2e = _timed_gen(items=items, chunks=chunks)
    hot, hot_e2e = _best_hot_gen(items=items, chunks=chunks)
    cold_wall = mean_ms([float(p.get("wall_ms") or 0.0) for p in cold])
    warm_wall = mean_ms([float(p.get("wall_ms") or 0.0) for p in warm])
    hot_wall = mean_ms([float(p.get("wall_ms") or 0.0) for p in hot])
    cold_ttft = mean_ms([ttft_of(p) for p in cold])
    warm_ttft = mean_ms([ttft_of(p) for p in warm])
    hot_ttft = mean_ms([ttft_of(p) for p in hot])

    gen_trials: list[dict[str, Any]] = []
    n_gen_wall_ok = 0
    for i, (item, payload) in enumerate(
        zip(items, cold, strict=True), start=1
    ):
        trial = _gen_trial(i=i, item=item, payload=payload)
        tel = extract_telemetry(payload)
        if tel["wall_ms"] > 0.0 and tel["n_new"] > 0:
            n_gen_wall_ok += 1
        write_json(trials_dir / f"{trial['trial_id']}.json", trial)
        gen_trials.append(trial)

    n_true = sum(
        1 for t in lookup_trials if t["lookup_kind"] == "TRUE_HIT"
    )
    n_false = sum(
        1 for t in lookup_trials if t["lookup_kind"] == "FALSE_HIT"
    )
    stats = fastmore_stats(
        lookup_scores=[float(t["score"]) for t in lookup_trials],
        lookup_errors=[bool(t["error"]) for t in lookup_trials],
        gen_scores=[float(t["score"]) for t in gen_trials],
        gen_errors=[bool(t["error"]) for t in gen_trials],
        n_true_hit=n_true,
        n_false_hit=n_false,
        cold_wall_ms=cold_wall,
        warm_wall_ms=warm_wall,
        hot_wall_ms=hot_wall,
        cold_ttft_ms=cold_ttft,
        warm_ttft_ms=warm_ttft,
        hot_ttft_ms=hot_ttft,
        cold_e2e_ms=cold_e2e,
        warm_e2e_ms=warm_e2e,
        hot_e2e_ms=hot_e2e,
        n_gen_wall_ok=n_gen_wall_ok,
        n_fix=fix_count,
    )
    decision = decide_fastmore(stats)
    summary: dict[str, Any] = {
        "hyp_id": FASTMORE_ID,
        "stage": "AK4",
        "decision": decision,
        "compose": [
            "SEMWRAP/ASKFAST LOOKUP (quality only)",
            "GENERATE PEAK_FAST+GENTRUE (no student decode)",
            f"cold+warm+hot gen timing (hot rounds={_GEN_HOT_ROUNDS})",
            f"vs FASTPEAK hot {FASTPEAK_HOT_WALL_MS:.3f} ms",
        ],
        "forbidden": [
            "STREAM",
            "KVCACHE-Q",
            "GENCACHE",
            "LOOKUP wall=0 as speed IQ",
            "open chat",
            "peak-as-open-chat-IQ",
        ],
        "seeded_golds": int(seeded),
        "fix_count": int(fix_count),
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "timing": {
            "cold_wall_ms": cold_wall,
            "warm_wall_ms": warm_wall,
            "hot_wall_ms": hot_wall,
            "cold_ttft_ms": cold_ttft,
            "warm_ttft_ms": warm_ttft,
            "hot_ttft_ms": hot_ttft,
            "cold_e2e_ms": cold_e2e,
            "warm_e2e_ms": warm_e2e,
            "hot_e2e_ms": hot_e2e,
            "af_raw_open_wall_ms": AF_RAW_OPEN_WALL_MS,
            "fastpeak_hot_wall_ms": FASTPEAK_HOT_WALL_MS,
            "gen_hot_rounds": _GEN_HOT_ROUNDS,
        },
        "stats": stats,
        "lookup_trials": [
            {
                "trial_id": t["trial_id"],
                "mode": t["mode"],
                "lookup_kind": t["lookup_kind"],
                "score": t["score"],
                "error": t["error"],
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
                "error": t["error"],
                "wall_ms": t["wall_ms"],
                "n_new": t["n_new"],
                "peak_used": t.get("peak_used"),
                "completion": str(t.get("completion") or "")[:120],
            }
            for t in gen_trials
        ],
        "finding": (
            f"{FASTMORE_ID}: gen wall "
            f"{cold_wall:.1f}/{warm_wall:.1f}/{hot_wall:.1f}ms "
            f"(FASTPEAK hot {FASTPEAK_HOT_WALL_MS:.1f}) "
            f"e2e {cold_e2e:.0f}/{warm_e2e:.0f}/{hot_e2e:.0f} "
            f"L={stats['lookup_mean']:.1f} G={stats['gen_mean']:.1f} "
            f"wall_ok={n_gen_wall_ok}/10 "
            f"vs_fp={stats['pass_vs_fastpeak']} "
            f"floor={stats['pass_quality_floor']} → {decision}"
        ),
        "public_note": "docs/results/nano-lm/formal-hfastmore-fastmore.md",
        "ship_claim": "AF packaged stack until AK6 gen bar",
        "claim": (
            "faster GENTRUE peak-extractive gen vs FASTPEAK with wall_ms>0 — "
            "LOOKUP scores are not speed IQ"
        ),
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--ak-bank", type=Path, default=_AK_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    cpus = int(os.cpu_count() or 4)
    # Max safe: leave 2 cores free.
    threads = tune_cpu_threads(max(4, cpus - 2))
    try:
        summary = run_fastmore(
            bank_path=Path(args.bank),
            ak_bank=Path(args.ak_bank),
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
                "hyp_id": FASTMORE_ID,
                "decision": decision,
                "lookup_mean": st["lookup_mean"],
                "gen_mean": st["gen_mean"],
                "n_false_hit": st["n_false_hit"],
                "n_gen_wall_ok": st["n_gen_wall_ok"],
                "pass_speed": st["pass_speed"],
                "pass_vs_fastpeak": st["pass_vs_fastpeak"],
                "pass_quality_floor": st["pass_quality_floor"],
                "cold_wall_ms": st["cold_wall_ms"],
                "warm_wall_ms": st["warm_wall_ms"],
                "hot_wall_ms": st["hot_wall_ms"],
                "fastpeak_hot_wall_ms": st["fastpeak_hot_wall_ms"],
                "fix_count": summary["fix_count"],
                "cpu_threads": threads,
                "out": str(args.out),
            }
        )
    )
    return 0 if decision in {"PROMOTE", "HOLD"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
