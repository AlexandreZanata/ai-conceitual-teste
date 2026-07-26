"""Wave Z6 REPORT runner: evidence + thesis markers (nano:z:z6)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads
from z6_ops import (
    Z6_EVIDENCE,
    Z6_ID,
    Z6_THESIS,
    decide_z6,
    report_markers_ok,
)

_OUT = REPO / "results/nano-lm/wave-z/z6_summary.json"
_REPORT = REPO / "docs/results/nano-lm/wave-z-hitl.md"


def _evidence_map() -> dict[str, bool]:
    return {p: (REPO / p).is_file() for p in Z6_EVIDENCE}


def _load_json(rel: str) -> dict[str, object] | None:
    path = REPO / rel
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_facts() -> dict[str, object]:
    z1 = _load_json("results/nano-lm/wave-z/z1_summary.json") or {}
    z2 = _load_json("results/nano-lm/wave-z/z2_summary.json") or {}
    z3 = _load_json("results/nano-lm/wave-z/z3_zerr_summary.json") or {}
    z4 = _load_json("results/nano-lm/wave-z/z4_summary.json") or {}
    depl = _load_json("results/nano-lm/wave-z/depl_y_freeze.json") or {}
    return {
        "z1_mean": z1.get("mean"),
        "z2_mean": z2.get("mean"),
        "z3_decision": z3.get("decision"),
        "z4_decision": z4.get("decision"),
        "z4_claim": z4.get("claim_branch"),
        "depl_decision": str(depl.get("decision", ""))[:48],
    }


def _smoke_wrap() -> dict[str, object]:
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
    decision = decide_z6(evidence)
    report_text = _REPORT.read_text(encoding="utf-8") if _REPORT.is_file() else ""
    markers = report_markers_ok(report_text)
    ask: dict[str, object] | None = None
    if not args.skip_ask:
        try:
            ask = _smoke_wrap()
        except (OSError, RuntimeError, ValueError) as exc:
            print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
            return 2
        if not bool(ask.get("ok")):
            print(json.dumps({"ok": False, "error": "wrap smoke failed", "ask": ask}))
            return 2
    payload = {
        "id": Z6_ID,
        "thesis": Z6_THESIS,
        "decision": decision,
        "markers_ok": markers,
        "cpu_threads": threads,
        "evidence": evidence,
        "stage_facts": _stage_facts(),
        "ask_smoke": ask,
        "public_report": "docs/results/nano-lm/wave-z-hitl.md",
        "paper_lab": "docs/results/nano-lm/paper-lab-wave-z.md",
        "wave_status": "COMPLETE",
    }
    write_json(Path(args.out), payload)
    ok = decision.startswith("PROMOTE") and markers
    print(
        json.dumps(
            {
                "ok": ok,
                "decision": "PROMOTE" if ok else decision[:64],
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
