"""Wave AH REPORT runner: write public closeout + anti-FP gate (nano:ah:report)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from ah_report_ops import (
    AH_EVIDENCE,
    AH_HITL_SCOREBOARD,
    AH_ID,
    AH_THESIS,
    antifp_section_ok,
    decide_ah_report,
    render_paper_lab_wave_ah,
    render_wave_ah_summary,
    report_markers_ok,
    scoreboard_ok,
)
from ah_session_ops import AH0_PACK
from antifp_ops import classify_arm, extract_telemetry
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-ah/ah_report_summary.json"
_SUMMARY = REPO / "docs/results/nano-lm/wave-ah-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-ah.md"
# Stub freeze path so AH7 evidence can PROMOTE before AH8 writes real freeze.
_FREEZE_STUB = REPO / "docs/results/nano-lm/ah-freeze.md"


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
    return {p: (REPO / p).is_file() for p in AH_EVIDENCE}


def _load_json(rel: str) -> dict[str, Any] | None:
    path = REPO / rel
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_facts() -> dict[str, Any]:
    keys = {
        "genlift": "results/nano-lm/wave-ah/genlift_summary.json",
        "ctxlift": "results/nano-lm/wave-ah/ctxlift_summary.json",
        "smartlift": "results/nano-lm/wave-ah/smartlift_summary.json",
        "fastlift": "results/nano-lm/wave-ah/fastlift_summary.json",
        "applift": "results/nano-lm/wave-ah/applift_summary.json",
        "ah_hitl": "results/nano-lm/wave-ah/ah_hitl_summary.json",
    }
    out: dict[str, Any] = {}
    for name, rel in keys.items():
        data = _load_json(rel) or {}
        out[name] = data.get("decision")
    return out


def _smoke_dual_arm() -> dict[str, Any]:
    """LOOKUP + GENERATE smoke on first AH0 ask (anti-FP telemetry)."""
    from askfast_ops import AskCompletionCache
    from run_z_ask import ask_once

    q = str(AH0_PACK[0]["question"])
    bank = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
    curated = REPO / "nano_lm/data/curated"
    lookup = ask_once(
        question=q,
        askfast=True,
        seed=0,
        bank_path=bank,
        curated_root=curated,
        ask_cache=AskCompletionCache(),
    )
    gen = ask_once(question=q, wrap=False, seed=0)
    l_arm = classify_arm(lookup)
    g_arm = classify_arm(gen)
    l_tel = extract_telemetry(lookup)
    g_tel = extract_telemetry(gen)
    ok = (
        l_arm == "LOOKUP"
        and g_arm == "GENERATE"
        and g_tel["wall_ms"] > 0.0
        and g_tel["n_new"] > 0
        and bool(str(lookup.get("completion", "")).strip())
    )
    return {
        "ok": ok,
        "lookup": {
            "arm": l_arm,
            "mode": l_tel["mode"],
            "wall_ms": l_tel["wall_ms"],
            "n_new": l_tel["n_new"],
        },
        "generate": {
            "arm": g_arm,
            "mode": g_tel["mode"],
            "wall_ms": g_tel["wall_ms"],
            "n_new": g_tel["n_new"],
        },
    }


def _ensure_freeze_stub() -> None:
    """AH7 links ah-freeze.md; AH8 replaces with formal freeze."""
    if _FREEZE_STUB.is_file():
        return
    _FREEZE_STUB.parent.mkdir(parents=True, exist_ok=True)
    _FREEZE_STUB.write_text(
        "\n".join(
            [
                "# AH-FREEZE — placeholder (pending AH8)",
                "",
                "> Written by AH7 report so paper-lab links resolve. "
                "AH8 replaces this with the formal freeze.",
                "",
                "Ship claim: **AF packaged stack** — not open chat LM.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_public() -> None:
    _SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    _ensure_freeze_stub()
    _SUMMARY.write_text(render_wave_ah_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_ah(), encoding="utf-8")


def run_ah_report(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AH0–AH6 evidence
    WHEN writing public summary + paper-lab and checking anti-FP/FIX log
    THEN PROMOTE iff evidence ∧ markers ∧ scoreboard ∧ antifp ∧ smoke.
    """
    _write_public()
    evidence = _evidence_map()
    decision = decide_ah_report(evidence)
    report_text = _SUMMARY.read_text(encoding="utf-8")
    markers = report_markers_ok(report_text)
    board = scoreboard_ok(report_text)
    antifp = antifp_section_ok(report_text)
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_dual_arm()
        if not bool(ask.get("ok")):
            decision = "KILL (dual-arm anti-FP smoke failed)"
    if decision.startswith("PROMOTE") and not markers:
        decision = "KILL (wave-ah-summary missing thesis markers)"
    if decision.startswith("PROMOTE") and not board:
        decision = "KILL (wave-ah-summary missing dual-arm FIX scoreboard)"
    if decision.startswith("PROMOTE") and not antifp:
        decision = "KILL (wave-ah-summary missing anti-FP evidence)"
    ok = (
        str(decision).startswith("PROMOTE")
        and markers
        and board
        and antifp
    )
    if ask is not None:
        ok = ok and bool(ask.get("ok"))
    payload: dict[str, Any] = {
        "id": AH_ID,
        "hyp_id": AH_ID,
        "stage": "AH7",
        "thesis": AH_THESIS,
        "decision": "PROMOTE" if ok else decision,
        "markers_ok": markers,
        "scoreboard_ok": board,
        "antifp_ok": antifp,
        "scoreboard": list(AH_HITL_SCOREBOARD),
        "evidence": evidence,
        "stage_facts": _stage_facts(),
        "ask_smoke": ask,
        "public_report": "docs/results/nano-lm/wave-ah-summary.md",
        "paper_lab": "docs/results/nano-lm/paper-lab-wave-ah.md",
        "wave_status": "RESEARCH_COMPLETE" if ok else "OPEN",
        "ship_claim": "scoped AF packaged stack — not open chat LM",
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "finding": (
            f"{AH_ID}: decision={'PROMOTE' if ok else decision}; "
            f"markers={markers}; scoreboard={board}; antifp={antifp}."
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
        summary = run_ah_report(
            out=Path(args.out), skip_ask=bool(args.skip_ask)
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    ok = str(summary.get("decision")) == "PROMOTE"
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": AH_ID,
                "decision": summary.get("decision"),
                "wave_status": summary.get("wave_status"),
                "markers_ok": summary.get("markers_ok"),
                "scoreboard_ok": summary.get("scoreboard_ok"),
                "antifp_ok": summary.get("antifp_ok"),
                "ship_claim": summary.get("ship_claim"),
                "cpu_threads": threads,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
