"""Wave AQ REPORT runner: public closeout + mode-triad anti-FP smoke."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from aq_report_ops import (
    AQ_EVIDENCE,
    AQ_ID,
    AQ_SCOREBOARD,
    AQ_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_aq_report,
    render_paper_lab_wave_aq,
    render_wave_aq_summary,
    report_markers_ok,
    scoreboard_ok,
)
from matrix_common import REPO, write_json
from modeui_ops import decide_modeui
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-aq/aq_report_summary.json"
_SUMMARY = REPO / "docs/results/nano-lm/wave-aq-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-aq.md"
_FREEZE_STUB = REPO / "docs/results/nano-lm/aq-freeze.md"


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
    return {p: (REPO / p).is_file() for p in AQ_EVIDENCE}


def _load_json(rel: str) -> dict[str, Any] | None:
    path = REPO / rel
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_facts() -> dict[str, Any]:
    keys = {
        "parahit": "results/nano-lm/wave-aq/parahit_summary.json",
        "advfp": "results/nano-lm/wave-aq/advfp_summary.json",
        "latp": "results/nano-lm/wave-aq/latp_summary.json",
        "kbcov": "results/nano-lm/wave-aq/kbcov_summary.json",
        "modeui": "results/nano-lm/wave-aq/modeui_summary.json",
        "nanogen": "results/nano-lm/wave-aq/nanogen_summary.json",
        "aq_product_hitl": (
            "results/nano-lm/wave-aq/aq_product_hitl_summary.json"
        ),
    }
    out: dict[str, Any] = {}
    for name, rel in keys.items():
        data = _load_json(rel) or {}
        out[name] = data.get("decision")
    return out


def _smoke_mode_triad() -> dict[str, Any]:
    """LOOKUP · PEAK · DECODE smoke (MODEUI) — no formal rewrite."""
    from run_modeui import (
        _CHAMPION,
        _CURATED,
        _Z_BANK,
        _smoke_decode,
        _smoke_lookup,
        _smoke_peak,
    )

    lookup = _smoke_lookup(root=_CHAMPION, bank=_Z_BANK)
    peak = _smoke_peak(curated=_CURATED)
    decode = _smoke_decode(root=_CHAMPION, bank=_Z_BANK)
    rows = [lookup, peak, decode]
    decision = decide_modeui(rows=rows)
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
    """AQ8 links aq-freeze.md; AQ9 replaces with the formal freeze."""
    if _FREEZE_STUB.is_file():
        return
    _FREEZE_STUB.parent.mkdir(parents=True, exist_ok=True)
    _FREEZE_STUB.write_text(
        "\n".join(
            [
                "# AQ-FREEZE — placeholder (pending AQ9)",
                "",
                "> Written by AQ8 report so paper-lab links resolve. "
                "AQ9 replaces this with the formal freeze.",
                "",
                f"Ship claim: **{SHIP_CLAIM}**",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_public() -> None:
    _SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    _ensure_freeze_stub()
    _SUMMARY.write_text(render_wave_aq_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_aq(), encoding="utf-8")


def run_aq_report(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AQ0–AQ7 evidence
    WHEN writing public summary + paper-lab and checking anti-FP/mode triad
    THEN PROMOTE iff evidence ∧ markers ∧ scoreboard ∧ antifp ∧ smoke.
    """
    _write_public()
    evidence = _evidence_map()
    decision = decide_aq_report(evidence)
    report_text = _SUMMARY.read_text(encoding="utf-8")
    markers = report_markers_ok(report_text)
    board = scoreboard_ok(report_text)
    antifp = antifp_section_ok(report_text)
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_mode_triad()
        if not bool(ask.get("ok")):
            decision = "KILL (LOOKUP·PEAK·DECODE mode triad smoke failed)"
    if decision.startswith("PROMOTE") and not markers:
        decision = "KILL (wave-aq-summary missing thesis markers)"
    if decision.startswith("PROMOTE") and not board:
        decision = "KILL (wave-aq-summary missing product scoreboard)"
    if decision.startswith("PROMOTE") and not antifp:
        decision = "KILL (wave-aq-summary missing anti-FP evidence)"
    ok = (
        str(decision).startswith("PROMOTE")
        and markers
        and board
        and antifp
    )
    if ask is not None:
        ok = ok and bool(ask.get("ok"))
    payload: dict[str, Any] = {
        "id": AQ_ID,
        "hyp_id": AQ_ID,
        "stage": "AQ8",
        "thesis": AQ_THESIS,
        "decision": "PROMOTE" if ok else decision,
        "markers_ok": markers,
        "scoreboard_ok": board,
        "antifp_ok": antifp,
        "scoreboard": list(AQ_SCOREBOARD),
        "evidence": evidence,
        "stage_facts": _stage_facts(),
        "ask_smoke": ask,
        "public_report": "docs/results/nano-lm/wave-aq-summary.md",
        "paper_lab": "docs/results/nano-lm/paper-lab-wave-aq.md",
        "wave_status": "RESEARCH_COMPLETE" if ok else "OPEN",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "finding": (
            f"{AQ_ID}: decision={'PROMOTE' if ok else decision}; "
            f"markers={markers}; scoreboard={board}; antifp={antifp}."
        ),
        "next": "AQ9 AQ-FREEZE",
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
        summary = run_aq_report(
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
                "hyp_id": AQ_ID,
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
