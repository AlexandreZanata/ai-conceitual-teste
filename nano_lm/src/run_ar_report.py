"""Wave AR REPORT runner: public closeout + four-mode anti-FP smoke."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from ar_report_ops import (
    AR_EVIDENCE,
    AR_ID,
    AR_SCOREBOARD,
    AR_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_ar_report,
    render_paper_lab_wave_ar,
    render_wave_ar_summary,
    report_markers_ok,
    scoreboard_ok,
)
from matrix_common import REPO, write_json
from shipdemo_ops import decide_shipdemo
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-ar/ar_report_summary.json"
_SUMMARY = REPO / "docs/results/nano-lm/wave-ar-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-ar.md"
_FREEZE_STUB = REPO / "docs/results/nano-lm/ar-freeze.md"
_LOCAL_SESSION = REPO / ".local/wave-ar/SESSION.md"


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
    return {p: (REPO / p).is_file() for p in AR_EVIDENCE}


def _load_json(rel: str) -> dict[str, Any] | None:
    path = REPO / rel
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_facts() -> dict[str, Any]:
    keys = {
        "abstain": "results/nano-lm/wave-ar/abstain_summary.json",
        "shipdemo": "results/nano-lm/wave-ar/shipdemo_summary.json",
        "paraext": "results/nano-lm/wave-ar/paraext_summary.json",
        "advreg": "results/nano-lm/wave-ar/advreg_summary.json",
        "nanogen2": "results/nano-lm/wave-ar/nanogen2_summary.json",
        "dual_hitl": "results/nano-lm/wave-ar/ar_dual_hitl_summary.json",
    }
    out: dict[str, Any] = {}
    for name, rel in keys.items():
        data = _load_json(rel) or {}
        out[name] = data.get("decision")
    return out


def _smoke_four_modes() -> dict[str, Any]:
    """LOOKUP · PEAK · DECODE · ABSTAIN smoke — no formal/SESSION rewrite."""
    from run_shipdemo import (
        _CHAMPION,
        _CURATED,
        _Z_BANK,
        _smoke_abstain,
        _smoke_decode,
        _smoke_lookup,
        _smoke_peak,
    )

    lookup = _smoke_lookup(root=_CHAMPION, bank=_Z_BANK)
    peak = _smoke_peak(curated=_CURATED)
    decode = _smoke_decode(root=_CHAMPION, bank=_Z_BANK)
    abstain = _smoke_abstain(root=_CHAMPION, bank=_Z_BANK)
    rows = [lookup, peak, decode, abstain]
    decision = decide_shipdemo(rows=rows)
    ok = decision == "PROMOTE"
    return {
        "ok": ok,
        "decision": decision,
        "arms": [
            {
                "arm": r.get("arm"),
                "product_mode": r.get("product_mode"),
                "modeui_line": r.get("modeui_line"),
                "wall_ms": r.get("wall_ms"),
                "n_new": r.get("n_new"),
            }
            for r in rows
        ],
    }


def _ensure_freeze_stub() -> None:
    """AR7 links ar-freeze.md; AR8 replaces with the formal freeze."""
    if _FREEZE_STUB.is_file():
        return
    _FREEZE_STUB.parent.mkdir(parents=True, exist_ok=True)
    _FREEZE_STUB.write_text(
        "\n".join(
            [
                "# AR-FREEZE — placeholder (pending AR8)",
                "",
                "> Written by AR7 report so paper-lab links resolve. "
                "AR8 replaces this with the formal freeze.",
                "",
                f"Ship claim: **{SHIP_CLAIM}**",
                "",
                "Do not invent Wave AS without lab-book reopen.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_public() -> None:
    _SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    _ensure_freeze_stub()
    _SUMMARY.write_text(render_wave_ar_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_ar(), encoding="utf-8")


def _update_local_session(decision: str) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    status = "DONE — PROMOTE" if decision == "PROMOTE" else f"DONE — {decision}"
    body = "\n".join(
        [
            f"# Wave AR session checklist (**OPEN** · AR7 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AR **OPEN**).  ",
            "> Parent: AQ COMPLETE + FROZEN · Ship: **AF packaged stack + "
            "AQ product layer — not open chat LM** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AR7 — AR-REPORT ({status})** · Next: **AR8 AR-FREEZE**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AR OPEN** (RESEARCH_COMPLETE pending FREEZE) |",
            f"| Decision | **{decision}** |",
            "| Public | `docs/results/nano-lm/wave-ar-summary.md` |",
            "| Paper-lab | `docs/results/nano-lm/paper-lab-wave-ar.md` |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AR0 | SESSION | **DONE — PROMOTE** |",
            "| AR1 | H-ABSTAIN | **DONE — PROMOTE** |",
            "| AR2 | H-SHIPDEMO | **DONE — PROMOTE** |",
            "| AR3 | H-PARAEXT | **DONE — HOLD** |",
            "| AR4 | H-ADVREG | **DONE — KILL** |",
            "| AR5 | H-NANOGEN2 | **DONE — HOLD** |",
            "| AR6 | AR-DUAL-HITL | **DONE — HOLD** |",
            f"| AR7 | AR-REPORT | **{status}** |",
            "| AR8 | AR-FREEZE | **NEXT** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def run_ar_report(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AR0–AR6 evidence
    WHEN writing public summary + paper-lab and checking anti-FP/four-mode
    THEN PROMOTE iff evidence ∧ markers ∧ scoreboard ∧ antifp ∧ smoke.
    """
    _write_public()
    evidence = _evidence_map()
    decision = decide_ar_report(evidence)
    report_text = _SUMMARY.read_text(encoding="utf-8")
    markers = report_markers_ok(report_text)
    board = scoreboard_ok(report_text)
    antifp = antifp_section_ok(report_text)
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_four_modes()
        if not bool(ask.get("ok")):
            decision = (
                "KILL (LOOKUP·PEAK·DECODE·ABSTAIN four-mode smoke failed)"
            )
    if decision.startswith("PROMOTE") and not markers:
        decision = "KILL (wave-ar-summary missing thesis markers)"
    if decision.startswith("PROMOTE") and not board:
        decision = "KILL (wave-ar-summary missing product scoreboard)"
    if decision.startswith("PROMOTE") and not antifp:
        decision = "KILL (wave-ar-summary missing anti-FP evidence)"
    ok = (
        str(decision).startswith("PROMOTE")
        and markers
        and board
        and antifp
    )
    if ask is not None:
        ok = ok and bool(ask.get("ok"))
    final = "PROMOTE" if ok else decision
    _update_local_session(final)
    payload: dict[str, Any] = {
        "id": AR_ID,
        "hyp_id": AR_ID,
        "stage": "AR7",
        "thesis": AR_THESIS,
        "decision": final,
        "markers_ok": markers,
        "scoreboard_ok": board,
        "antifp_ok": antifp,
        "scoreboard": list(AR_SCOREBOARD),
        "evidence": evidence,
        "stage_facts": _stage_facts(),
        "ask_smoke": ask,
        "public_report": "docs/results/nano-lm/wave-ar-summary.md",
        "paper_lab": "docs/results/nano-lm/paper-lab-wave-ar.md",
        "wave_status": "RESEARCH_COMPLETE" if ok else "OPEN",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "finding": (
            f"{AR_ID}: decision={final}; "
            f"markers={markers}; scoreboard={board}; antifp={antifp}."
        ),
        "next": "AR8 AR-FREEZE",
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
    threads = tune_cpu_threads(max(4, cpus - 2))
    try:
        summary = run_ar_report(
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
                "hyp_id": AR_ID,
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
