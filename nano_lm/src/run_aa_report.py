"""Wave AA REPORT runner: evidence + thesis markers (nano:aa:report)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from aa_report_ops import (
    AA_EVIDENCE,
    AA_ID,
    AA_THESIS,
    decide_aa_report,
    report_markers_ok,
)
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-aa/aa_report_summary.json"
_REPORT = REPO / "docs/results/nano-lm/wave-aa-summary.md"


def _evidence_map() -> dict[str, bool]:
    return {p: (REPO / p).is_file() for p in AA_EVIDENCE}


def _load_json(rel: str) -> dict[str, Any] | None:
    path = REPO / rel
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_facts() -> dict[str, Any]:
    return {
        "wrapbank": (_load_json("results/nano-lm/wave-aa/wrapbank_summary.json") or {}).get(
            "decision"
        ),
        "para": (_load_json("results/nano-lm/wave-aa/para_summary.json") or {}).get(
            "decision"
        ),
        "servealign": (
            _load_json("results/nano-lm/wave-aa/servealign_summary.json") or {}
        ).get("decision"),
        "zpref": (_load_json("results/nano-lm/wave-aa/zpref_summary.json") or {}).get(
            "decision"
        ),
        "depl_doc": (
            _load_json("results/nano-lm/wave-aa/depl_doc_summary.json") or {}
        ).get("decision"),
    }


def _smoke_wrap() -> dict[str, Any]:
    from run_z_ask import ask_once

    q = (
        "Write a short Python function named add that returns "
        "the sum of two integers a and b."
    )
    payload = ask_once(question=q, wrap=True, seed=0)
    text = str(payload.get("completion", "")).strip()
    mode = str(payload.get("mode", ""))
    return {
        "ok": mode == "WRAP_LOOKUP" and "def add" in text,
        "mode": mode,
        "wall_ms": payload.get("wall_ms"),
    }


def main() -> int:
    for key in (
        "http_proxy",
        "https_proxy",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "all_proxy",
    ):
        os.environ.pop(key, None)
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    threads = tune_cpu_threads(max(4, int(os.cpu_count() or 4) - 2))
    evidence = _evidence_map()
    decision = decide_aa_report(evidence)
    report_text = _REPORT.read_text(encoding="utf-8") if _REPORT.is_file() else ""
    markers = report_markers_ok(report_text)
    ask: dict[str, Any] | None = None
    if not args.skip_ask:
        try:
            ask = _smoke_wrap()
        except (OSError, RuntimeError, ValueError) as exc:
            print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
            return 2
        if not bool(ask.get("ok")):
            print(json.dumps({"ok": False, "error": "wrap smoke failed", "ask": ask}))
            return 2
    if decision.startswith("PROMOTE") and not markers:
        decision = "KILL (wave-aa-summary missing thesis markers)"
    payload = {
        "id": AA_ID,
        "thesis": AA_THESIS,
        "decision": decision,
        "markers_ok": markers,
        "cpu_threads": threads,
        "evidence": evidence,
        "stage_facts": _stage_facts(),
        "ask_smoke": ask,
        "public_report": "docs/results/nano-lm/wave-aa-summary.md",
        "paper_lab": "docs/results/nano-lm/paper-lab-wave-aa.md",
        "wave_status": "COMPLETE",
    }
    write_json(Path(args.out), payload)
    ok = str(decision).startswith("PROMOTE") and markers
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": AA_ID,
                "decision": "PROMOTE" if ok else decision[:80],
                "cpu_threads": threads,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
