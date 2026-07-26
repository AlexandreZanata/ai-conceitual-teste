"""Freeze DEPL-Y deploy routes + evidence gate (nano:z:depl-y)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from depl_y_ops import (
    DEPL_Y_EVIDENCE,
    DEPL_Y_FORBIDDEN,
    DEPL_Y_ID,
    choose_depl_y,
    decide_depl_y,
    reject_forbidden,
    route_table,
)
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-z/depl_y_freeze.json"


def _evidence_map() -> dict[str, bool]:
    return {p: (REPO / p).is_file() for p in DEPL_Y_EVIDENCE}


def _smoke_wrap_ask() -> dict[str, object]:
    """Manual product check: known-ask wrap on CUDA (or lookup-only)."""
    from run_z_ask import ask_once

    q = (
        "Write a short Python function named add that returns "
        "the sum of two integers a and b."
    )
    payload = ask_once(question=q, wrap=True, seed=0)
    mode = str(payload.get("mode", ""))
    text = str(payload.get("completion", "")).strip()
    ok = mode == "WRAP_LOOKUP" and "def add" in text
    return {
        "ok": ok,
        "mode": mode,
        "wall_ms": payload.get("wall_ms"),
        "n_new": payload.get("n_new"),
        "completion_prefix": text[:80],
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
    ap.add_argument(
        "--skip-ask",
        action="store_true",
        help="Skip CUDA/wrap product smoke",
    )
    args = ap.parse_args()
    threads = tune_cpu_threads(max(4, int(os.cpu_count() or 4) - 2))
    evidence = _evidence_map()
    decision = decide_depl_y(evidence)
    routes = {
        g: choose_depl_y(g)
        for g in (
            "speed_128",
            "code_128",
            "code_btc",
            "long_ctx",
            "hitl_known",
            "story_ce",
            "train",
            "quality_in_dist",
        )
    }
    # L-gate sanity (contract must reject mismatches).
    l_checks = {
        "code_128@256": choose_depl_y("code_128", L=256),
        "long_ctx@128": choose_depl_y("long_ctx", L=128),
        "speed_128@512": choose_depl_y("speed_128", L=512),
    }
    if not all(str(v).startswith("REJECT") for v in l_checks.values()):
        print(json.dumps({"ok": False, "error": "L-gate failed", "l_checks": l_checks}))
        return 2
    bans_ok = all(reject_forbidden(b) for b in DEPL_Y_FORBIDDEN)
    ask: dict[str, object] | None = None
    if not args.skip_ask:
        try:
            ask = _smoke_wrap_ask()
        except (OSError, RuntimeError, ValueError) as exc:
            print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
            return 2
        if not bool(ask.get("ok")):
            print(json.dumps({"ok": False, "error": "wrap ask smoke failed", "ask": ask}))
            return 2
    payload = {
        "id": DEPL_Y_ID,
        "decision": decision,
        "cpu_threads": threads,
        "routes": routes,
        "route_table": route_table(),
        "forbidden": sorted(DEPL_Y_FORBIDDEN),
        "evidence": evidence,
        "l_checks": l_checks,
        "bans_ok": bans_ok,
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/wave-z-depl-y.md",
    }
    write_json(Path(args.out), payload)
    ok = decision.startswith("PROMOTE") and bans_ok
    print(
        json.dumps(
            {
                "ok": ok,
                "decision": decision.split(":")[0] if ":" in decision else decision[:32],
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
