"""Wave AQ4 H-KBCOV runner (nano:kbcov) — coverage % + explicit holes."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from aq_session_ops import AQ0_PARA_PACK
from curated_sources import SOURCES, source_ids
from kbcov_ops import (
    KBCOV_ID,
    KBCOV_THESIS,
    PRODUCT_HOLES,
    build_kbcov_snapshot,
    curated_blob_stats,
    decide_kbcov,
    parent_gold_hits,
)
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads
from z_wrap import load_bank_rows

_SUMMARY = REPO / "results/nano-lm/wave-aq/kbcov_summary.json"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hkbcov-kbcov.md"
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


def _hardware() -> tuple[int, int]:
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 2))
    workers = min(14, max(4, cpus - 2))
    return threads, workers


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


def _write_public(
    *,
    decision: str,
    snap: dict[str, Any],
    blobs: dict[str, Any],
    parents: dict[str, Any],
) -> None:
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
            f"# H-KBCOV — KB coverage + holes (**DONE** — {decision})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AQ4 · Session: "
            "`.local/wave-aq/SESSION.md`  ",
            "> Parent: [formal-hlatp-latp.md](formal-hlatp-latp.md) · "
            "AQ0: [wave-aq-session.md](wave-aq-session.md)  ",
            "> Module: `nano_lm/src/kbcov_ops.py` · "
            "Runner: `npm run nano:kbcov`",
            "",
            "## Hypothesis",
            "",
            "Publish honest **curated∩bank coverage %** plus an **explicit "
            "hole list**. Registry 100% ≠ complete product KB.",
            "",
            "## Gate",
            "",
            "| Metric | Value |",
            "|--------|------:|",
            f"| curated covered | **{snap.get('covered_n')}** / "
            f"**{snap.get('curated_n')}** |",
            f"| coverage_pct | **{snap.get('coverage_pct')}** |",
            f"| curated blobs present | **{blobs.get('present_n')}** / "
            f"**{blobs.get('n')}** ({blobs.get('present_pct')}%) |",
            f"| PARA parent LOOKUP golds | **{parents.get('hit_n')}** / "
            f"**{parents.get('n')}** ({parents.get('hit_pct')}%) |",
            f"| complete_claim_forbidden | "
            f"**{snap.get('complete_claim_forbidden')}** |",
            f"| Decision | **{decision}** |",
            "",
            "## Missing curated ids in bank",
            "",
            miss_row,
            "",
            "## PARA parent gold misses",
            "",
            parent_row,
            "",
            "## Explicit holes (product + registry)",
            "",
            *holes,
            "",
            "## Finding",
            "",
            "1. Coverage % published under max safe CPU threads (`cpus-2`).  ",
            "2. Product holes always listed — no fake 100% completeness.  ",
            f"3. Frozen product holes n={len(PRODUCT_HOLES)} "
            "(open-world · languages · BIPs/RFCs · math · tools · anti-FP).",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:kbcov",
            "npm run nano:z:ask -- --wrap --question \"Write a short Python "
            "function named add that returns the sum of two integers a and b.\"",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-aq/kbcov_summary.json`  ",
            "- Contract: `nano_lm/tests/test_kbcov.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Publish coverage % + holes | Fake complete product KB |",
            "| Registry 100% with product holes | Selling curated∩bank as "
            "open-world |",
            "| List PARA gold misses | Expanding bank until HITL theater |",
            "",
            "Next: **AQ5 H-MODEUI** — **DONE PROMOTE** → "
            "[formal-hmodeui-modeui.md](formal-hmodeui-modeui.md).",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def run_kbcov(
    *,
    bank: Path,
    curated: Path,
    out: Path,
    workers: int,
) -> dict[str, Any]:
    """
    GIVEN bank + curated registry
    WHEN computing H-KBCOV
    THEN write summary + formal with coverage % and holes.
    """
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

    def _one(sid: str) -> dict[str, Any]:
        return _blob_check(sid, curated_root=curated_root)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        checks = list(pool.map(_one, sorted(curated_set)))
    blobs = curated_blob_stats(checks)
    parents = parent_gold_hits(AQ0_PARA_PACK, bank_rows)
    decision = decide_kbcov(snap=snap, blobs=blobs, parents=parents)
    public_decision = "PROMOTE" if decision == "PROMOTE" else "HOLD"
    if decision.startswith("KILL"):
        public_decision = "KILL"
    _write_public(
        decision=public_decision,
        snap=snap,
        blobs=blobs,
        parents=parents,
    )
    summary: dict[str, Any] = {
        "hyp_id": KBCOV_ID,
        "stage": "AQ4",
        "thesis": KBCOV_THESIS,
        "decision": decision if decision == "PROMOTE" else decision,
        "kb": snap,
        "curated_blobs": blobs,
        "para_parent_golds": parents,
        "bank_rows_n": len(bank_rows),
        "forbidden": [
            "fake complete product KB",
            "registry 100% sold as open-world",
            "empty holes list",
            "Wave AR invent",
        ],
        "public_note": "docs/results/nano-lm/formal-hkbcov-kbcov.md",
        "next": "AQ5 H-MODEUI",
    }
    write_json(Path(out), summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AQ4 H-KBCOV")
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        summary = run_kbcov(
            bank=Path(args.bank),
            curated=Path(args.curated),
            out=Path(args.out),
            workers=workers,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    decision = str(summary["decision"])
    ok = decision == "PROMOTE"
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": KBCOV_ID,
                "decision": decision,
                "coverage_pct": summary["kb"]["coverage_pct"],
                "holes_n": len(summary["kb"]["holes"]),
                "parent_gold_pct": summary["para_parent_golds"]["hit_pct"],
                "cpu_threads": threads,
                "workers": workers,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
