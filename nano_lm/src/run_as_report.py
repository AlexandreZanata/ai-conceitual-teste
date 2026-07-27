"""Wave AS REPORT runner: public closeout + four-mode anti-FP smoke."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from as_report_ops import (
    AS_EVIDENCE,
    AS_ID,
    AS_SCOREBOARD,
    AS_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_as_report,
    render_paper_lab_wave_as,
    render_wave_as_summary,
    report_markers_ok,
    scoreboard_ok,
)
from matrix_common import REPO, write_json
from shipui_ops import decide_shipui
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-as/as_report_summary.json"
_SUMMARY = REPO / "docs/results/nano-lm/wave-as-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-as.md"
_FREEZE_STUB = REPO / "docs/results/nano-lm/as-freeze.md"
_FORMAL_FREEZE_STUB = REPO / "docs/results/nano-lm/formal-hasfreeze-as-freeze.md"
_LOCAL_SESSION = REPO / ".local/wave-as/SESSION.md"


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
    return {p: (REPO / p).is_file() for p in AS_EVIDENCE}


def _load_json(rel: str) -> dict[str, Any] | None:
    path = REPO / rel
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_facts() -> dict[str, Any]:
    keys = {
        "askabstain": "results/nano-lm/wave-as/askabstain_summary.json",
        "semfix": "results/nano-lm/wave-as/semfix_summary.json",
        "advsafe": "results/nano-lm/wave-as/advsafe_summary.json",
        "paraext2": "results/nano-lm/wave-as/paraext2_summary.json",
        "metrics": "results/nano-lm/wave-as/metrics_summary.json",
        "shipui": "results/nano-lm/wave-as/shipui_summary.json",
        "nanogen3": "results/nano-lm/wave-as/nanogen3_summary.json",
        "dual_hitl": "results/nano-lm/wave-as/as_dual_hitl_summary.json",
    }
    out: dict[str, Any] = {}
    for name, rel in keys.items():
        data = _load_json(rel) or {}
        out[name] = data.get("decision")
    return out


def _smoke_four_modes() -> dict[str, Any]:
    """LOOKUP · PEAK · DECODE · ABSTAIN smoke — no formal rewrite."""
    from run_shipui import (
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
    decision = decide_shipui(rows=rows)
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


def _write_stub(path: Path, title: str) -> None:
    if path.is_file():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                f"# {title} — placeholder (pending AS10)",
                "",
                "> Written by AS9 report so paper-lab links resolve. "
                "AS10 replaces this with the formal freeze.",
                "",
                f"Ship claim: **{SHIP_CLAIM}**",
                "",
                "Do not invent Wave AT without lab-book reopen.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _ensure_freeze_stubs() -> None:
    _write_stub(_FREEZE_STUB, "AS-FREEZE")
    _write_stub(_FORMAL_FREEZE_STUB, "formal-hasfreeze-as-freeze")


def _write_public() -> None:
    _SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    _ensure_freeze_stubs()
    _SUMMARY.write_text(render_wave_as_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_as(), encoding="utf-8")


def _update_local_session(decision: str) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    status = "DONE — PROMOTE" if decision == "PROMOTE" else f"DONE — {decision}"
    body = "\n".join(
        [
            f"# Wave AS session checklist (**OPEN** · AS9 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AS **OPEN**).  ",
            "> Parent: AR COMPLETE + FROZEN · Ship: **AF packaged stack + "
            "AQ product layer — not open chat LM** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AS9 — AS-REPORT ({status})** · Next: **AS10 AS-FREEZE**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AS OPEN** (RESEARCH_COMPLETE pending FREEZE) |",
            f"| Decision | **{decision}** |",
            "| Public | `docs/results/nano-lm/wave-as-summary.md` |",
            "| Paper-lab | `docs/results/nano-lm/paper-lab-wave-as.md` |",
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
            "| AS5 | H-METRICS | **DONE — PROMOTE** |",
            "| AS6 | H-SHIPUI | **DONE — PROMOTE** |",
            "| AS7 | H-NANOGEN3 | **DONE — HOLD** |",
            "| AS8 | AS-DUAL-HITL | **DONE — PROMOTE** |",
            f"| AS9 | AS-REPORT | **{status}** |",
            "| AS10 | AS-FREEZE | **NEXT** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def run_as_report(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AS0–AS8 evidence
    WHEN writing public summary + paper-lab and checking anti-FP/four-mode
    THEN PROMOTE iff evidence ∧ markers ∧ scoreboard ∧ antifp ∧ smoke.
    """
    _write_public()
    evidence = _evidence_map()
    decision = decide_as_report(evidence)
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
        decision = "KILL (wave-as-summary missing thesis markers)"
    if decision.startswith("PROMOTE") and not board:
        decision = "KILL (wave-as-summary missing product scoreboard)"
    if decision.startswith("PROMOTE") and not antifp:
        decision = "KILL (wave-as-summary missing anti-FP evidence)"
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
        "id": AS_ID,
        "hyp_id": AS_ID,
        "stage": "AS9",
        "thesis": AS_THESIS,
        "decision": final,
        "markers_ok": markers,
        "scoreboard_ok": board,
        "antifp_ok": antifp,
        "scoreboard": list(AS_SCOREBOARD),
        "evidence": evidence,
        "stage_facts": _stage_facts(),
        "ask_smoke": ask,
        "public_report": "docs/results/nano-lm/wave-as-summary.md",
        "paper_lab": "docs/results/nano-lm/paper-lab-wave-as.md",
        "wave_status": "RESEARCH_COMPLETE" if ok else "OPEN",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "finding": (
            f"{AS_ID}: decision={final}; "
            f"markers={markers}; scoreboard={board}; antifp={antifp}."
        ),
        "next": "AS10 AS-FREEZE",
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
        summary = run_as_report(
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
                "hyp_id": AS_ID,
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
