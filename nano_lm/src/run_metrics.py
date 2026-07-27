"""Wave AS5 H-METRICS runner — latency tetrad(+ABSTAIN) + KB coverage refresh."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from ap_session_ops import AP0_PACK
from as_session_ops import AS0_METRICS_PROTOCOL, AS0_PARAEXT2_PACK
from askabstain_ops import ASKABSTAIN_OOD_PACK
from curated_sources import SOURCES, source_ids
from fastbase_ops import fastbase_generate
from genpeak_ops import chunk_doc
from kbcov_ops import (
    PRODUCT_HOLES,
    build_kbcov_snapshot,
    curated_blob_stats,
    parent_gold_hits,
)
from matrix_common import REPO, write_json
from metrics_ops import (
    ABSTAIN_N,
    DECODE_N,
    FASTBASE_HOT_WALL_MS,
    LOOKUP_N,
    METRICS_ID,
    METRICS_PATHS,
    METRICS_THESIS,
    PEAK_N,
    decide_metrics,
    map_as_product_mode,
    path_latency_stats,
    peak_regressed,
    telemetry_rules_ok,
)
from run_z_ask import ask_many
from tipd_pair import tune_cpu_threads
from z_wrap import load_bank_rows

_SUMMARY = REPO / "results/nano-lm/wave-as/metrics_summary.json"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hmetrics-metrics.md"
_LOCAL_SESSION = REPO / ".local/wave-as/SESSION.md"
_BY_ID = {str(s["id"]): s for s in SOURCES}
_KNOWN = (
    "Write a short Python function named add that returns "
    "the sum of two integers a and b."
)
_OOD = str(ASKABSTAIN_OOD_PACK[0]["ask"])


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


def _hardware() -> tuple[int, int]:
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 2))
    workers = min(14, max(4, cpus - 2))
    return threads, workers


def _pack_measure(
    *,
    path: str,
    payloads: list[dict[str, Any]],
    note: str,
) -> dict[str, Any]:
    walls = [float(p.get("wall_ms") or 0.0) for p in payloads]
    modes = [str(p.get("mode", "")) for p in payloads]
    n_news = [int(p.get("n_new") or 0) for p in payloads]
    pmodes = [
        str(p.get("product_mode") or map_as_product_mode(m))
        for p, m in zip(payloads, modes)
    ]
    stats = path_latency_stats(walls)
    ok = telemetry_rules_ok(
        path=path,
        walls=walls,
        n_news=n_news,
        modes=modes,
        product_modes=pmodes,
    )
    return {
        "path": path,
        "stats": stats,
        "telemetry_ok": ok,
        "sample_mode": modes[0] if modes else "",
        "product_mode": pmodes[0] if pmodes else "",
        "note": note,
    }


def _measure_lookup(
    *, root: Path, bank: Path, curated: Path, seed: int
) -> dict[str, Any]:
    payloads = ask_many(
        questions=[_KNOWN] * LOOKUP_N,
        root=root,
        seed=seed,
        wrap=True,
        bank_path=bank,
        curated_root=curated,
        abstain=True,
    )
    return _pack_measure(
        path="LOOKUP",
        payloads=payloads,
        note="LOOKUP wall_ms may be 0 — not speed IQ",
    )


def _measure_decode(
    *, root: Path, bank: Path, curated: Path, seed: int
) -> dict[str, Any]:
    # abstain=False — measure neural DECODE walls (not NO_ANSWER rewrite)
    payloads = ask_many(
        questions=[_KNOWN] * DECODE_N,
        root=root,
        seed=seed,
        wrap=False,
        bank_path=bank,
        curated_root=curated,
        abstain=False,
    )
    return _pack_measure(
        path="DECODE",
        payloads=payloads,
        note="neural DECODE (abstain off for latency sample)",
    )


def _measure_abstain(
    *, root: Path, bank: Path, curated: Path, seed: int
) -> dict[str, Any]:
    payloads = ask_many(
        questions=[_OOD] * ABSTAIN_N,
        root=root,
        seed=seed,
        semwrap=True,
        bank_path=bank,
        curated_root=curated,
        abstain=True,
    )
    return _pack_measure(
        path="ABSTAIN",
        payloads=payloads,
        note="default ask OOD → ABSTAIN; wall_ms published",
    )


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
    for _ in range(8):
        fastbase_generate(question=question, chunks=chunks, doc=doc)
    payloads = [
        fastbase_generate(question=question, chunks=chunks, doc=doc)
        for _ in range(PEAK_N)
    ]
    return _pack_measure(
        path="PEAK",
        payloads=payloads,
        note="PEAK_FAST+GENBASE extractive — vs FASTBASE hot",
    )


def _blob_check(source_id: str, *, curated_root: Path) -> dict[str, Any]:
    meta = _BY_ID.get(source_id, {})
    rel = str(meta.get("path", ""))
    path = curated_root / rel if rel else Path()
    exists = path.is_file()
    size = int(path.stat().st_size) if exists else 0
    return {
        "source_id": source_id,
        "path": rel,
        "exists": exists,
        "bytes": size,
    }


def _kb_refresh(*, bank: Path, curated: Path, workers: int) -> dict[str, Any]:
    curated_root = Path(curated)
    curated_set = set(source_ids())
    bank_rows = load_bank_rows(Path(bank))
    bank_srcs = {
        str(r.get("source_id", "")).strip()
        for r in bank_rows
        if str(r.get("source_id", "")).strip()
    }
    snap = build_kbcov_snapshot(
        curated_ids=curated_set, bank_source_ids=bank_srcs
    )
    ids = sorted(curated_set)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        checks = list(
            pool.map(
                lambda sid: _blob_check(sid, curated_root=curated_root), ids
            )
        )
    blobs = curated_blob_stats(checks)
    parents = parent_gold_hits(AS0_PARAEXT2_PACK, bank_rows)
    return {"snap": snap, "blobs": blobs, "parents": parents}


def _write_public(
    *,
    decision: str,
    paths: dict[str, Any],
    regress: bool,
    regress_note: str,
    kb: dict[str, Any],
) -> None:
    rows = []
    for name in METRICS_PATHS:
        st = paths[name]["stats"]
        rows.append(
            f"| {name} | **{st['p50_wall_ms']:.4f}** | "
            f"**{st['p99_wall_ms']:.4f}** | {st['n']} | "
            f"{paths[name].get('sample_mode', '')} |"
        )
    snap = kb["snap"]
    blobs = kb["blobs"]
    parents = kb["parents"]
    holes = [f"- {h}" for h in snap.get("holes", [])]
    miss_cur = snap.get("missing_curated_in_bank") or []
    miss_row = (
        ", ".join(f"`{x}`" for x in miss_cur) if miss_cur else "_(none)_"
    )
    parent_miss = parents.get("miss_ids") or []
    parent_row = (
        ", ".join(f"`{x}`" for x in parent_miss) if parent_miss else "_(none)_"
    )
    body = "\n".join(
        [
            f"# H-METRICS — latency tetrad + KB refresh (**DONE** — {decision})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AS5 · Session: "
            "`.local/wave-as/SESSION.md`  ",
            "> Parent: [formal-hparaext2-paraext2.md]"
            "(formal-hparaext2-paraext2.md) · Protocol: AS0 METRICS  ",
            "> Module: `nano_lm/src/metrics_ops.py` · "
            "Runner: `npm run nano:metrics`",
            "",
            "## Hypothesis",
            "",
            "After ASKABSTAIN · SEMFIX · ADVSAFE · PARAEXT2, republish "
            "honest **p50/p99 wall_ms** for LOOKUP · PEAK · DECODE · "
            "**ABSTAIN** plus **KB coverage %** with explicit holes.",
            "",
            "## Latency gate",
            "",
            "| Path | p50 wall_ms | p99 wall_ms | n | sample mode |",
            "|------|------------:|------------:|--:|-------------|",
            *rows,
            "",
            f"| FASTBASE hot (baseline) | **{FASTBASE_HOT_WALL_MS:.4f}** | "
            "— | — | PEAK_FAST |",
            f"| PEAK regress vs baseline | **{regress}** | — | — | — |",
            f"| Decision | **{decision}** | — | — | — |",
            "",
            "## Regress note",
            "",
            regress_note if regress_note else "- (none — no PEAK regress)",
            "",
            "## Protocol (AS0)",
            "",
            "| Path | Rule |",
            "|------|------|",
            "| LOOKUP | `wall_ms` may be 0 — **not** speed IQ |",
            "| PEAK | `wall_ms` > 0; labeled extractive |",
            "| DECODE | `wall_ms` > 0 and `n_new` > 0 (sample abstain off) |",
            "| ABSTAIN | default ask OOD → `NO_ANSWER`; publish `wall_ms` |",
            "",
            "## KB coverage refresh",
            "",
            "| Metric | Value |",
            "|--------|------:|",
            f"| curated covered | **{snap.get('covered_n')}** / "
            f"**{snap.get('curated_n')}** |",
            f"| coverage_pct | **{snap.get('coverage_pct')}** |",
            f"| curated blobs present | **{blobs.get('present_n')}** / "
            f"**{blobs.get('n')}** ({blobs.get('present_pct')}%) |",
            f"| PARAEXT2 parent LOOKUP golds | **{parents.get('hit_n')}** / "
            f"**{parents.get('n')}** ({parents.get('hit_pct')}%) |",
            f"| complete_claim_forbidden | "
            f"**{snap.get('complete_claim_forbidden')}** |",
            "",
            "## Missing curated ids in bank",
            "",
            miss_row,
            "",
            "## PARAEXT2 parent gold misses",
            "",
            parent_row,
            "",
            "## Explicit holes (product + registry)",
            "",
            *holes,
            "",
            "## Finding",
            "",
            "1. Tetrad(+ABSTAIN) published under max safe CPU (`cpus-2`).  ",
            "2. LOOKUP wall=0 not sold as speed IQ.  ",
            "3. ABSTAIN path measured on default ask after AS1.  ",
            "4. KB holes explicit — no fake world-complete claim.  ",
            f"5. Product holes n={len(PRODUCT_HOLES)}.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:metrics",
            "npm run nano:z:ask -- --wrap --question "
            '"Write a short Python function named add that returns '
            'the sum of two integers a and b."',
            f'npm run nano:z:ask -- --semwrap --question "{_OOD}"',
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-as/metrics_summary.json`  ",
            "- Contract: `nano_lm/tests/test_metrics.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Publish tetrad p50/p99 + KB holes | LOOKUP wall=0 as speed IQ |",
            "| Honest PEAK regress note | Silent regress / fake complete KB |",
            "| ABSTAIN wall published | Mini-AGI / open-chat claim |",
            "",
            "Next: **AS6 H-SHIPUI** — mode visible on ship/demo + ask.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _update_local_session(
    decision: str, paths: dict[str, Any], kb: dict[str, Any]
) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    status = f"DONE — {decision}"
    st_l = paths["LOOKUP"]["stats"]
    st_a = paths["ABSTAIN"]["stats"]
    body = "\n".join(
        [
            f"# Wave AS session checklist (**OPEN** · AS5 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AS **OPEN**).  ",
            "> Parent: AR COMPLETE + FROZEN · Ship: **AF packaged stack + "
            "AQ product layer — not open chat LM** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AS5 — H-METRICS ({status})** · Next: **AS6 H-SHIPUI**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AS OPEN** |",
            f"| LOOKUP p50 | **{st_l.get('p50_wall_ms')}** |",
            f"| ABSTAIN p50 | **{st_a.get('p50_wall_ms')}** |",
            f"| coverage_pct | **{kb['snap'].get('coverage_pct')}** |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AS0 | SESSION | **DONE — PROMOTE** |",
            "| AS1 | H-ASKABSTAIN | **DONE — PROMOTE** |",
            "| AS2 | H-SEMFIX | **DONE — PROMOTE** |",
            "| AS3 | H-ADVSAFE | **DONE — PROMOTE** |",
            "| AS4 | H-PARAEXT2 | **DONE — PROMOTE** |",
            f"| AS5 | H-METRICS | **{status}** |",
            "| AS6 | H-SHIPUI | **NEXT** |",
            "| AS7 | H-NANOGEN3 | pending |",
            "| AS8 | AS-DUAL-HITL | pending |",
            "| AS9 | AS-REPORT | pending |",
            "| AS10 | AS-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def run_metrics(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    workers: int,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN AS0 metrics protocol after ask-path changes
    WHEN sampling LOOKUP·PEAK·DECODE·ABSTAIN + KB refresh
    THEN publish numbers · holes → PROMOTE|KILL.
    """
    lookup = _measure_lookup(
        root=root, bank=bank, curated=curated, seed=seed
    )
    peak = _measure_peak(curated=curated)
    decode = _measure_decode(
        root=root, bank=bank, curated=curated, seed=seed
    )
    abstain = _measure_abstain(
        root=root, bank=bank, curated=curated, seed=seed
    )
    paths = {
        "LOOKUP": lookup,
        "PEAK": peak,
        "DECODE": decode,
        "ABSTAIN": abstain,
    }
    tel_ok = {k: bool(v["telemetry_ok"]) for k, v in paths.items()}
    peak_p50 = float(peak["stats"]["p50_wall_ms"])
    regress = peak_regressed(peak_p50)
    if regress:
        note = (
            f"PEAK p50 {peak_p50:.4f} ms > FASTBASE hot "
            f"{FASTBASE_HOT_WALL_MS:.4f} ms — noted honestly; not silent."
        )
    else:
        note = (
            f"PEAK p50 {peak_p50:.4f} ms ≤ FASTBASE hot "
            f"{FASTBASE_HOT_WALL_MS:.4f} ms — no regress."
        )
    kb = _kb_refresh(bank=bank, curated=curated, workers=workers)
    path_stats = {k: v["stats"] for k, v in paths.items()}
    decision = decide_metrics(
        paths=path_stats,
        telemetry_ok=tel_ok,
        regress_noted=True,
        snap=kb["snap"],
    )
    _write_public(
        decision=decision,
        paths=paths,
        regress=regress,
        regress_note=note,
        kb=kb,
    )
    _update_local_session(decision, paths, kb)
    summary: dict[str, Any] = {
        "hyp_id": METRICS_ID,
        "stage": "AS5",
        "thesis": METRICS_THESIS,
        "decision": decision,
        "protocol": dict(AS0_METRICS_PROTOCOL),
        "fastbase_hot_wall_ms": FASTBASE_HOT_WALL_MS,
        "peak_regressed": regress,
        "regress_note": note,
        "paths": paths,
        "kb": kb,
        "samples": {
            "LOOKUP": LOOKUP_N,
            "PEAK": PEAK_N,
            "DECODE": DECODE_N,
            "ABSTAIN": ABSTAIN_N,
        },
        "compose": ["LATP-family", "KBCOV-family", "ASKABSTAIN", "AS0-METRICS"],
        "forbidden": [
            "LOOKUP-wall-as-speed-IQ",
            "silent PEAK regress",
            "fake complete KB",
            "open-chat claim",
            "Wave AT invent",
        ],
        "public_note": "docs/results/nano-lm/formal-hmetrics-metrics.md",
        "next": "AS6 H-SHIPUI",
        "anti_fp": (
            "publish tetrad+holes only; generative bar remains AS7"
        ),
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        summary = run_metrics(
            root=Path(args.root),
            bank=Path(args.bank),
            curated=Path(args.curated),
            out=Path(args.out),
            workers=workers,
            seed=int(args.seed),
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    decision = str(summary.get("decision", ""))
    ok = decision == "PROMOTE"
    paths = summary["paths"]
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": METRICS_ID,
                "decision": decision,
                "lookup_p50": paths["LOOKUP"]["stats"]["p50_wall_ms"],
                "peak_p50": paths["PEAK"]["stats"]["p50_wall_ms"],
                "decode_p50": paths["DECODE"]["stats"]["p50_wall_ms"],
                "abstain_p50": paths["ABSTAIN"]["stats"]["p50_wall_ms"],
                "coverage_pct": summary["kb"]["snap"].get("coverage_pct"),
                "cpu_threads": threads,
                "workers": workers,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
