"""Wave AA4 H-DEPL-DOC: sync one-pagers to DEPL-Y (nano:depl-doc)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from depl_doc_ops import (
    DEPL_DOC_ID,
    ONE_PAGERS,
    decide_depl_doc,
    page_sync_report,
)
from depl_y_ops import DEPL_Y_FORBIDDEN, DEPL_Y_ROUTES, choose_depl_y, reject_forbidden
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-aa/depl_doc_summary.json"


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


def _read(path: str) -> str:
    return (REPO / path).read_text(encoding="utf-8")


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
        "completion_prefix": text[:80],
        "wall_ms": payload.get("wall_ms"),
    }


def run_depl_doc(*, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN DEPL-Y routes + public one-pagers
    WHEN scanning markers + optional wrap smoke
    THEN PROMOTE iff docs sync and smoke ok.
    """
    reports = [page_sync_report(p, _read(p)) for p in ONE_PAGERS]
    decision = decide_depl_doc(reports)
    routes = {g: choose_depl_y(g) for g in DEPL_Y_ROUTES}
    bans_ok = all(reject_forbidden(b) for b in DEPL_Y_FORBIDDEN)
    if "H-WRAPBANK" not in routes.get("hitl_known", ""):
        decision = "KILL (DEPL_Y hitl_known missing H-WRAPBANK)"
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_wrap()
        if not bool(ask.get("ok")):
            decision = "KILL (wrap product smoke failed)"
    if decision == "PROMOTE" and not bans_ok:
        decision = "KILL (forbidden list broken)"
    summary: dict[str, Any] = {
        "hyp_id": DEPL_DOC_ID,
        "stage": "AA4",
        "decision": decision,
        "pages": reports,
        "routes": routes,
        "forbidden": sorted(DEPL_Y_FORBIDDEN),
        "bans_ok": bans_ok,
        "ask_smoke": ask,
        "note": "Doc sync only — no new hypotheses; DEPL-Y + Wave AA outcomes aligned.",
    }
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    threads = tune_cpu_threads(max(4, int(os.cpu_count() or 4) - 2))
    try:
        summary = run_depl_doc(skip_ask=bool(args.skip_ask))
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    summary["cpu_threads"] = threads
    write_json(Path(args.out), summary)
    ok = str(summary["decision"]) == "PROMOTE"
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": DEPL_DOC_ID,
                "decision": summary["decision"],
                "cpu_threads": threads,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
