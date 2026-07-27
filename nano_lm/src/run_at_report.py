"""Wave AT REPORT runner: public closeout + four-mode anti-FP smoke."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from at_report_ops import (
    AT_EVIDENCE,
    AT_ID,
    AT_SCOREBOARD,
    AT_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_at_report,
    realeval_section_ok,
    render_paper_lab_wave_at,
    render_wave_at_summary,
    report_markers_ok,
    scoreboard_ok,
)
from matrix_common import REPO, write_json
from shipui_ops import decide_shipui
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-at/at_report_summary.json"
_SUMMARY = REPO / "docs/results/nano-lm/wave-at-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-at.md"
_FREEZE_STUB = REPO / "docs/results/nano-lm/at-freeze.md"
_FORMAL_FREEZE_STUB = REPO / "docs/results/nano-lm/formal-hatfreeze-at-freeze.md"
_LOCAL_SESSION = REPO / ".local/wave-at/SESSION.md"


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
    return {p: (REPO / p).is_file() for p in AT_EVIDENCE}


def _load_json(rel: str) -> dict[str, Any] | None:
    path = REPO / rel
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_facts() -> dict[str, Any]:
    keys = {
        "session": "results/nano-lm/wave-at/at0_session.json",
        "prodreg": "results/nano-lm/wave-at/prodreg_summary.json",
        "shipapp": "results/nano-lm/wave-at/shipapp_summary.json",
        "nanogen4": "results/nano-lm/wave-at/nanogen4_summary.json",
        "real_eval": "results/nano-lm/wave-at/real_eval_summary.json",
    }
    out: dict[str, Any] = {}
    for name, rel in keys.items():
        data = _load_json(rel) or {}
        out[name] = data.get("decision")
    return out


def _smoke_four_modes() -> dict[str, Any]:
    """LOOKUP · PEAK · DECODE · ABSTAIN smoke — no formal rewrite."""
    from run_shipapp import (
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
                f"# {title} — placeholder (pending AT6)",
                "",
                "> Written by AT5 report so paper-lab links resolve. "
                "AT6 replaces this with the formal freeze.",
                "",
                f"Ship claim: **{SHIP_CLAIM}**",
                "",
                "Do not invent Wave AU without lab-book reopen.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _ensure_freeze_stubs() -> None:
    _write_stub(_FREEZE_STUB, "AT-FREEZE")
    _write_stub(_FORMAL_FREEZE_STUB, "formal-hatfreeze-at-freeze")


def _write_public() -> None:
    _SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    _ensure_freeze_stubs()
    _SUMMARY.write_text(render_wave_at_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_at(), encoding="utf-8")


def _update_local_session(decision: str) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    status = "DONE — PROMOTE" if decision == "PROMOTE" else f"DONE — {decision}"
    body = "\n".join(
        [
            f"# Wave AT session checklist (**OPEN** · AT5 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AT **OPEN**).  ",
            "> Parent: AS COMPLETE + FROZEN · Ship: **"
            + SHIP_CLAIM
            + "** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AT5 — AT-REPORT ({status})** · Next: **AT6 AT-FREEZE**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AT OPEN** (RESEARCH_COMPLETE pending FREEZE) |",
            f"| Decision | **{decision}** |",
            "| Public | `docs/results/nano-lm/wave-at-summary.md` |",
            "| Paper-lab | `docs/results/nano-lm/paper-lab-wave-at.md` |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AT0 | SESSION | **DONE — PROMOTE** |",
            "| AT1 | H-PRODREG | **DONE — PROMOTE** |",
            "| AT2 | H-SHIPAPP | **DONE — PROMOTE** |",
            "| AT3 | H-NANOGEN4 | **DONE — PROMOTE** |",
            "| AT4 | AT-REAL-EVAL | **DONE — PROMOTE** |",
            f"| AT5 | AT-REPORT | **{status}** |",
            "| AT6 | AT-FREEZE | **NEXT** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def run_at_report(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AT0–AT4 evidence
    WHEN writing public summary + paper-lab and checking anti-FP/four-mode
    THEN PROMOTE iff evidence ∧ markers ∧ scoreboard ∧ antifp ∧ realeval ∧ smoke.
    """
    _write_public()
    evidence = _evidence_map()
    decision = decide_at_report(evidence)
    report_text = _SUMMARY.read_text(encoding="utf-8")
    markers = report_markers_ok(report_text)
    board = scoreboard_ok(report_text)
    antifp = antifp_section_ok(report_text)
    realeval = realeval_section_ok(report_text)
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_four_modes()
        if not bool(ask.get("ok")):
            decision = (
                "KILL (LOOKUP·PEAK·DECODE·ABSTAIN four-mode smoke failed)"
            )
    if decision.startswith("PROMOTE") and not markers:
        decision = "KILL (wave-at-summary missing thesis markers)"
    if decision.startswith("PROMOTE") and not board:
        decision = "KILL (wave-at-summary missing scoreboard)"
    if decision.startswith("PROMOTE") and not antifp:
        decision = "KILL (wave-at-summary missing anti-FP evidence)"
    if decision.startswith("PROMOTE") and not realeval:
        decision = "KILL (wave-at-summary missing real-eval section)"
    ok = (
        str(decision).startswith("PROMOTE")
        and markers
        and board
        and antifp
        and realeval
    )
    if ask is not None:
        ok = ok and bool(ask.get("ok"))
    final = "PROMOTE" if ok else decision
    _update_local_session(final)
    payload: dict[str, Any] = {
        "id": AT_ID,
        "hyp_id": AT_ID,
        "stage": "AT5",
        "thesis": AT_THESIS,
        "decision": final,
        "markers_ok": markers,
        "scoreboard_ok": board,
        "antifp_ok": antifp,
        "realeval_ok": realeval,
        "scoreboard": list(AT_SCOREBOARD),
        "evidence": evidence,
        "stage_facts": _stage_facts(),
        "ask_smoke": ask,
        "public_report": "docs/results/nano-lm/wave-at-summary.md",
        "paper_lab": "docs/results/nano-lm/paper-lab-wave-at.md",
        "wave_status": "RESEARCH_COMPLETE" if ok else "OPEN",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "finding": (
            f"{AT_ID}: decision={final}; "
            f"markers={markers}; scoreboard={board}; "
            f"antifp={antifp}; realeval={realeval}."
        ),
        "next": "AT6 AT-FREEZE",
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
        summary = run_at_report(
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
                "hyp_id": AT_ID,
                "decision": summary.get("decision"),
                "wave_status": summary.get("wave_status"),
                "markers_ok": summary.get("markers_ok"),
                "scoreboard_ok": summary.get("scoreboard_ok"),
                "antifp_ok": summary.get("antifp_ok"),
                "realeval_ok": summary.get("realeval_ok"),
                "ship_claim": summary.get("ship_claim"),
                "cpu_threads": threads,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
