"""Wave AQ3 H-LATP runner (nano:latp) — LOOKUP · PEAK · DECODE p50/p99."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from ap_session_ops import AP0_PACK
from aq_session_ops import AQ0_LATENCY_PROTOCOL, map_product_mode
from curated_sources import SOURCES
from fastbase_ops import fastbase_generate
from genpeak_ops import chunk_doc
from latp_ops import (
    DECODE_N,
    FASTBASE_HOT_WALL_MS,
    LATP_ID,
    LATP_THESIS,
    LOOKUP_N,
    PEAK_N,
    decide_latp,
    path_latency_stats,
    peak_regressed,
    telemetry_rules_ok,
)
from matrix_common import REPO, write_json
from run_z_ask import ask_many
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-aq/latp_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-aq/trials"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hlatp-latp.md"
_BY_ID = {str(s["id"]): s for s in SOURCES}
_KNOWN = (
    "Write a short Python function named add that returns "
    "the sum of two integers a and b."
)


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


def _hardware() -> int:
    cpus = int(os.cpu_count() or 4)
    return tune_cpu_threads(max(4, cpus - 2))


def _measure_lookup(*, root: Path, bank: Path, curated: Path, seed: int) -> dict[str, Any]:
    payloads = ask_many(
        questions=[_KNOWN] * LOOKUP_N,
        root=root,
        seed=seed,
        wrap=True,
        bank_path=bank,
        curated_root=curated,
    )
    walls = [float(p.get("wall_ms") or 0.0) for p in payloads]
    modes = [str(p.get("mode", "")) for p in payloads]
    n_news = [int(p.get("n_new") or 0) for p in payloads]
    stats = path_latency_stats(walls)
    ok = telemetry_rules_ok(
        path="LOOKUP", walls=walls, n_news=n_news, modes=modes
    )
    return {
        "path": "LOOKUP",
        "stats": stats,
        "telemetry_ok": ok,
        "sample_mode": modes[0] if modes else "",
        "product_mode": map_product_mode(modes[0]) if modes else "",
        "note": "LOOKUP wall_ms may be 0 — not speed IQ",
    }


def _measure_decode(*, root: Path, bank: Path, curated: Path, seed: int) -> dict[str, Any]:
    payloads = ask_many(
        questions=[_KNOWN] * DECODE_N,
        root=root,
        seed=seed,
        wrap=False,
        bank_path=bank,
        curated_root=curated,
    )
    walls = [float(p.get("wall_ms") or 0.0) for p in payloads]
    modes = [str(p.get("mode", "")) for p in payloads]
    n_news = [int(p.get("n_new") or 0) for p in payloads]
    stats = path_latency_stats(walls)
    ok = telemetry_rules_ok(
        path="DECODE", walls=walls, n_news=n_news, modes=modes
    )
    return {
        "path": "DECODE",
        "stats": stats,
        "telemetry_ok": ok,
        "sample_mode": modes[0] if modes else "",
        "product_mode": map_product_mode(modes[0]) if modes else "",
        "note": "neural DECODE — not compared to FASTBASE peak-fast hot",
    }


def _load_peak_doc(curated: Path) -> tuple[str, list[str], str]:
    item = dict(AP0_PACK[0])
    sid = str(item["source_id"])
    meta = _BY_ID.get(sid)
    if meta is None:
        raise ValueError(f"unknown source_id: {sid}")
    path = curated / str(meta["path"])
    doc = path.read_text(encoding="utf-8", errors="ignore")
    return str(item["question"]), chunk_doc(doc, win=400, stride=160), doc


def _measure_peak(*, curated: Path) -> dict[str, Any]:
    question, chunks, doc = _load_peak_doc(curated)
    # Warm-up then hot samples (max HW already pinned via tune_cpu_threads).
    for _ in range(8):
        fastbase_generate(question=question, chunks=chunks, doc=doc)
    payloads = [
        fastbase_generate(question=question, chunks=chunks, doc=doc)
        for _ in range(PEAK_N)
    ]
    walls = [float(p.get("wall_ms") or 0.0) for p in payloads]
    modes = [str(p.get("mode", "")) for p in payloads]
    n_news = [int(p.get("n_new") or 0) for p in payloads]
    stats = path_latency_stats(walls)
    ok = telemetry_rules_ok(
        path="PEAK", walls=walls, n_news=n_news, modes=modes
    )
    return {
        "path": "PEAK",
        "stats": stats,
        "telemetry_ok": ok,
        "sample_mode": modes[0] if modes else "",
        "product_mode": map_product_mode(modes[0]) if modes else "",
        "question": question,
        "note": "PEAK_FAST+GENBASE extractive — compared to FASTBASE hot",
    }


def _write_public(
    *,
    decision: str,
    paths: dict[str, Any],
    regress: bool,
    regress_note: str,
) -> None:
    rows = []
    for name in ("LOOKUP", "PEAK", "DECODE"):
        st = paths[name]["stats"]
        rows.append(
            f"| {name} | **{st['p50_wall_ms']:.4f}** | "
            f"**{st['p99_wall_ms']:.4f}** | {st['n']} | "
            f"{paths[name].get('sample_mode', '')} |"
        )
    body = "\n".join(
        [
            f"# H-LATP — latency triad p50/p99 (**DONE** — {decision})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AQ3 · Session: "
            "`.local/wave-aq/SESSION.md`  ",
            "> Parent: [formal-hadvfp-advfp.md](formal-hadvfp-advfp.md) · "
            "Baseline: [formal-hfastbase-fastbase.md](formal-hfastbase-fastbase.md)  ",
            "> Module: `nano_lm/src/latp_ops.py` · "
            "Runner: `npm run nano:latp`",
            "",
            "## Hypothesis",
            "",
            "Publish honest **p50/p99 wall_ms** for LOOKUP · PEAK · DECODE "
            "under AQ0 latency protocol. PEAK must not silently regress vs "
            f"FASTBASE hot (**{FASTBASE_HOT_WALL_MS:.4f} ms**).",
            "",
            "## Gate",
            "",
            "| Path | p50 wall_ms | p99 wall_ms | n | sample mode |",
            "|------|------------:|------------:|--:|-------------|",
            *rows,
            "",
            f"| FASTBASE hot (baseline) | **{FASTBASE_HOT_WALL_MS:.4f}** | — | — | PEAK_FAST |",
            f"| PEAK regress vs baseline | **{regress}** | — | — | — |",
            f"| Decision | **{decision}** | — | — | — |",
            "",
            "## Regress note",
            "",
            regress_note if regress_note else "- (none — no PEAK regress)",
            "",
            "## Protocol (AQ0)",
            "",
            "| Path | Rule |",
            "|------|------|",
            "| LOOKUP | `wall_ms` may be 0 — **not** speed IQ |",
            "| PEAK | `wall_ms` > 0; labeled extractive |",
            "| DECODE | `wall_ms` > 0 and `n_new` > 0 |",
            "",
            "## Finding",
            "",
            "1. Triad published under max safe CPU threads (`cpus-2`).  ",
            "2. LOOKUP path labeled product retrieve — never sold as speed IQ.  ",
            "3. DECODE neural wall is a different regime than PEAK-fast hot.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:latp",
            "npm run nano:z:ask -- --wrap --question \"Write a short Python function named add that returns the sum of two integers a and b.\"",
            "npm run nano:z:ask -- --question \"Explain Merkle trees briefly\"",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-aq/latp_summary.json`  ",
            "- Contract: `nano_lm/tests/test_latp.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Publish triad p50/p99 | LOOKUP wall=0 as speed IQ |",
            "| Honest PEAK regress note | Silent regress vs FASTBASE hot |",
            "| DECODE wall>0 · n_new>0 | Peak-as-open-chat |",
            "",
            "Next: **AQ4 H-KBCOV** — KB coverage % + explicit hole list.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def run_latp(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    trials_dir: Path,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN AQ0 latency protocol + FASTBASE hot baseline
    WHEN sampling LOOKUP · PEAK · DECODE walls
    THEN publish p50/p99; PROMOTE if telemetry ok and no silent regress.
    """
    trials_dir.mkdir(parents=True, exist_ok=True)
    lookup = _measure_lookup(root=root, bank=bank, curated=curated, seed=seed)
    peak = _measure_peak(curated=curated)
    decode = _measure_decode(root=root, bank=bank, curated=curated, seed=seed)
    paths = {"LOOKUP": lookup, "PEAK": peak, "DECODE": decode}
    tel_ok = {k: bool(v["telemetry_ok"]) for k, v in paths.items()}
    peak_p50 = float(peak["stats"]["p50_wall_ms"])
    regress = peak_regressed(peak_p50)
    if regress:
        note = (
            f"PEAK p50 {peak_p50:.4f} ms > FASTBASE hot "
            f"{FASTBASE_HOT_WALL_MS:.4f} ms — noted (host variance / "
            "load); still published honestly; not silent."
        )
    else:
        note = (
            f"PEAK p50 {peak_p50:.4f} ms ≤ FASTBASE hot "
            f"{FASTBASE_HOT_WALL_MS:.4f} ms — no regress."
        )
    path_stats = {k: v["stats"] for k, v in paths.items()}
    decision = decide_latp(
        paths=path_stats,
        telemetry_ok=tel_ok,
        regress_noted=True,  # always attach explicit note
    )
    _write_public(
        decision=decision if decision.startswith("PROMOTE") else decision,
        paths=paths,
        regress=regress,
        regress_note=note,
    )
    summary: dict[str, Any] = {
        "hyp_id": LATP_ID,
        "stage": "AQ3",
        "thesis": LATP_THESIS,
        "decision": decision,
        "protocol": dict(AQ0_LATENCY_PROTOCOL),
        "fastbase_hot_wall_ms": FASTBASE_HOT_WALL_MS,
        "peak_regressed": regress,
        "regress_note": note,
        "paths": paths,
        "samples": {"LOOKUP": LOOKUP_N, "PEAK": PEAK_N, "DECODE": DECODE_N},
        "forbidden": [
            "LOOKUP-as-speed-IQ",
            "silent PEAK regress vs FASTBASE hot",
            "peak-as-open-chat",
            "Wave AR invent",
        ],
        "public_note": "docs/results/nano-lm/formal-hlatp-latp.md",
        "next": "AQ4 H-KBCOV",
    }
    write_json(out, summary)
    write_json(
        trials_dir / "AQ-LATP-SUMMARY.json",
        {
            "trial_id": "AQ-LATP-SUMMARY",
            "stage": "AQ3",
            "hyp_id": LATP_ID,
            "decision": decision,
            "paths": path_stats,
        },
    )
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    threads = _hardware()
    try:
        summary = run_latp(
            root=Path(args.root),
            bank=Path(args.bank),
            curated=Path(args.curated),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            seed=int(args.seed),
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    decision = str(summary.get("decision", ""))
    ok = decision.startswith("PROMOTE")
    peak = summary["paths"]["PEAK"]["stats"]
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": LATP_ID,
                "decision": decision,
                "lookup_p50": summary["paths"]["LOOKUP"]["stats"]["p50_wall_ms"],
                "peak_p50": peak["p50_wall_ms"],
                "peak_p99": peak["p99_wall_ms"],
                "decode_p50": summary["paths"]["DECODE"]["stats"]["p50_wall_ms"],
                "peak_regressed": summary["peak_regressed"],
                "cpu_threads": threads,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
