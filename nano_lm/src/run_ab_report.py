"""Wave AB REPORT runner: write public closeout + evidence gate (nano:ab:report)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from ab_report_ops import (
    AB_EVIDENCE,
    AB_HITL_SCOREBOARD,
    AB_ID,
    AB_THESIS,
    decide_ab_report,
    render_paper_lab_wave_ab,
    render_wave_ab_summary,
    report_markers_ok,
    scoreboard_ok,
)
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-ab/ab_report_summary.json"
_SUMMARY = REPO / "docs/results/nano-lm/wave-ab-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-ab.md"


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


def _evidence_map() -> dict[str, bool]:
    return {p: (REPO / p).is_file() for p in AB_EVIDENCE}


def _load_json(rel: str) -> dict[str, Any] | None:
    path = REPO / rel
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_facts() -> dict[str, Any]:
    keys = {
        "semwrap": "results/nano-lm/wave-ab/semwrap_summary.json",
        "askfast": "results/nano-lm/wave-ab/askfast_summary.json",
        "longapp": "results/nano-lm/wave-ab/longapp_summary.json",
        "asksmart": "results/nano-lm/wave-ab/asksmart_summary.json",
        "realapp": "results/nano-lm/wave-ab/realapp_summary.json",
        "ab_hitl": "results/nano-lm/wave-ab/ab_hitl_summary.json",
    }
    out: dict[str, Any] = {}
    for name, rel in keys.items():
        data = _load_json(rel) or {}
        out[name] = data.get("decision")
    return out


def _smoke_askfast() -> dict[str, Any]:
    from askfast_ops import AskCompletionCache
    from run_z_ask import ask_once

    q = (
        "Which Bitcoin signature scheme does BIP-340 lock in, "
        "and over which curve?"
    )
    cache = AskCompletionCache()
    payload = ask_once(
        question=q,
        askfast=True,
        seed=0,
        bank_path=REPO / "results/nano-lm/wave-z/error_bank.jsonl",
        curated_root=REPO / "nano_lm/data/curated",
        ask_cache=cache,
    )
    mode = str(payload.get("mode", ""))
    text = str(payload.get("completion", "")).strip()
    ok = mode in {"SEMWRAP_LOOKUP", "WRAP_LOOKUP", "ASKFAST_CACHE"} and bool(text)
    return {
        "ok": ok,
        "mode": mode,
        "wall_ms": payload.get("wall_ms"),
        "n_chars": len(text),
    }


def _write_public() -> None:
    _SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    _SUMMARY.write_text(render_wave_ab_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_ab(), encoding="utf-8")


def run_ab_report(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AB0–AB6 evidence
    WHEN writing public summary + paper-lab and checking markers/FIX log
    THEN PROMOTE iff evidence ∧ markers ∧ scoreboard ∧ smoke.
    """
    _write_public()
    evidence = _evidence_map()
    decision = decide_ab_report(evidence)
    report_text = _SUMMARY.read_text(encoding="utf-8")
    markers = report_markers_ok(report_text)
    board = scoreboard_ok(report_text)
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_askfast()
        if not bool(ask.get("ok")):
            decision = "KILL (askfast smoke failed)"
    if decision.startswith("PROMOTE") and not markers:
        decision = "KILL (wave-ab-summary missing thesis markers)"
    if decision.startswith("PROMOTE") and not board:
        decision = "KILL (wave-ab-summary missing per-model FIX scoreboard)"
    ok = str(decision).startswith("PROMOTE") and markers and board
    if ask is not None:
        ok = ok and bool(ask.get("ok"))
    payload: dict[str, Any] = {
        "id": AB_ID,
        "hyp_id": AB_ID,
        "stage": "AB7",
        "thesis": AB_THESIS,
        "decision": "PROMOTE" if ok else decision,
        "markers_ok": markers,
        "scoreboard_ok": board,
        "scoreboard": list(AB_HITL_SCOREBOARD),
        "evidence": evidence,
        "stage_facts": _stage_facts(),
        "ask_smoke": ask,
        "public_report": "docs/results/nano-lm/wave-ab-summary.md",
        "paper_lab": "docs/results/nano-lm/paper-lab-wave-ab.md",
        "wave_status": "COMPLETE" if ok else "OPEN",
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "finding": (
            f"{AB_ID}: decision={'PROMOTE' if ok else decision}; "
            f"markers={markers}; scoreboard={board}."
        ),
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    try:
        summary = run_ab_report(out=Path(args.out), skip_ask=bool(args.skip_ask))
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    ok = str(summary.get("decision")) == "PROMOTE"
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": AB_ID,
                "decision": summary.get("decision"),
                "wave_status": summary.get("wave_status"),
                "markers_ok": summary.get("markers_ok"),
                "scoreboard_ok": summary.get("scoreboard_ok"),
                "cpu_threads": threads,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
