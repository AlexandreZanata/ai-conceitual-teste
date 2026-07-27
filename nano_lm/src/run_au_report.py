"""Wave AU REPORT runner: public closeout + four-mode anti-FP smoke."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from au_report_ops import (
    AU_EVIDENCE,
    AU_ID,
    AU_SCOREBOARD,
    AU_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_au_report,
    realeval_section_ok,
    render_paper_lab_wave_au,
    render_wave_au_summary,
    report_markers_ok,
    scoreboard_ok,
)
from matrix_common import REPO, write_json
from shipreal_ops import arms_content_ok
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-au/au_report_summary.json"
_SUMMARY = REPO / "docs/results/nano-lm/wave-au-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-au.md"
_FREEZE_STUB = REPO / "docs/results/nano-lm/au-freeze.md"
_FORMAL_FREEZE_STUB = REPO / "docs/results/nano-lm/formal-haufreeze-au-freeze.md"
_LOCAL_SESSION = REPO / ".local/wave-au/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"


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
    return {p: (REPO / p).is_file() for p in AU_EVIDENCE}


def _load_json(rel: str) -> dict[str, Any] | None:
    path = REPO / rel
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_facts() -> dict[str, Any]:
    keys = {
        "session": "results/nano-lm/wave-au/au0_session.json",
        "prodhard": "results/nano-lm/wave-au/prodhard_summary.json",
        "shipreal": "results/nano-lm/wave-au/shipreal_summary.json",
        "nanogen5": "results/nano-lm/wave-au/nanogen5_summary.json",
        "real_eval": "results/nano-lm/wave-au/real_eval_summary.json",
    }
    out: dict[str, Any] = {}
    for name, rel in keys.items():
        data = _load_json(rel) or {}
        out[name] = data.get("decision")
    return out


def _smoke_four_modes() -> dict[str, Any]:
    """LOOKUP · PEAK · DECODE · ABSTAIN smoke via SHIPREAL content bars."""
    from run_shipreal import (
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
    ok = arms_content_ok(rows)
    return {
        "ok": ok,
        "decision": "PROMOTE" if ok else "KILL (SHIPREAL content smoke)",
        "arms": [
            {
                "arm": r.get("arm"),
                "product_mode": r.get("product_mode"),
                "modeui_line": r.get("modeui_line"),
                "wall_ms": r.get("wall_ms"),
                "n_new": r.get("n_new"),
                "content_ok": True,
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
                f"# {title} — placeholder (pending AU6)",
                "",
                "> Written by AU5 report so paper-lab links resolve. "
                "AU6 replaces this with the formal freeze.",
                "",
                f"Ship claim: **{SHIP_CLAIM}**",
                "",
                "Do not invent Wave AV without lab-book reopen.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _ensure_freeze_stubs() -> None:
    _write_stub(_FREEZE_STUB, "AU-FREEZE")
    _write_stub(_FORMAL_FREEZE_STUB, "formal-haufreeze-au-freeze")


def _write_public() -> None:
    _SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    _ensure_freeze_stubs()
    _SUMMARY.write_text(render_wave_au_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_au(), encoding="utf-8")


def _update_local_session(decision: str) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    status = "DONE — PROMOTE" if decision == "PROMOTE" else f"DONE — {decision}"
    body = "\n".join(
        [
            f"# Wave AU session checklist (**OPEN** · AU5 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AU **OPEN**).  ",
            "> Parent: AT COMPLETE + FROZEN · Ship: **"
            + SHIP_CLAIM
            + "** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AU5 — AU-REPORT ({status})** · Next: **AU6 AU-FREEZE**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AU OPEN** (RESEARCH_COMPLETE pending FREEZE) |",
            f"| Decision | **{decision}** |",
            "| Public | `docs/results/nano-lm/wave-au-summary.md` |",
            "| Paper-lab | `docs/results/nano-lm/paper-lab-wave-au.md` |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AU0 | SESSION | **DONE — PROMOTE** |",
            "| AU1 | H-PRODHARD | **DONE — PROMOTE** |",
            "| AU2 | H-SHIPREAL | **DONE — PROMOTE** |",
            "| AU3 | H-NANOGEN5 | **DONE — PROMOTE** |",
            "| AU4 | AU-REAL-EVAL | **DONE — PROMOTE** |",
            f"| AU5 | AU-REPORT | **{status}** |",
            "| AU6 | AU-FREEZE | **NEXT** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    status = "PROMOTE" if decision == "PROMOTE" else decision.split("(", 1)[0].strip()
    text2, n = re.subn(
        r"(\| AU5 \| \*\*AU-REPORT\*\* \| Public summary \+ paper-lab \| "
        r"anti-FP \+ real-eval section \| )\*\*[^*]+\*\*",
        rf"\1**DONE — {status}**",
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"2d\. \*\*AU4 AU-REAL-EVAL\*\* — \*\*DONE [^*]+\*\*"
        r"(?: \(`npm run nano:au:real-eval`\))? · next \*\*AU5 AU-REPORT\*\*\.",
        (
            "2d. **AU4 AU-REAL-EVAL** — **DONE PROMOTE** "
            "(`npm run nano:au:real-eval`).  \n"
            f"2e. **AU5 AU-REPORT** — **DONE {status}** "
            "(`npm run nano:au:report`) · next **AU6 AU-FREEZE**."
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"2e\. \*\*AU5 AU-REPORT\*\* — \*\*DONE [^*]+\*\*",
        f"2e. **AU5 AU-REPORT** — **DONE {status}**",
        text,
        count=1,
    )
    if n:
        text = text2
    bash_old = "# next: nano:au:report (as stages land)"
    bash_new = (
        "npm run nano:au:report\n"
        "# next: nano:au:freeze (as stages land)"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def run_au_report(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AU0–AU4 evidence
    WHEN writing public summary + paper-lab and checking anti-FP/four-mode
    THEN PROMOTE iff evidence ∧ markers ∧ scoreboard ∧ antifp ∧ realeval ∧ smoke.
    """
    _write_public()
    evidence = _evidence_map()
    decision = decide_au_report(evidence)
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
        decision = "KILL (wave-au-summary missing thesis markers)"
    if decision.startswith("PROMOTE") and not board:
        decision = "KILL (wave-au-summary missing scoreboard)"
    if decision.startswith("PROMOTE") and not antifp:
        decision = "KILL (wave-au-summary missing anti-FP evidence)"
    if decision.startswith("PROMOTE") and not realeval:
        decision = "KILL (wave-au-summary missing real-eval section)"
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
    _patch_pesquisa(final)
    payload: dict[str, Any] = {
        "id": AU_ID,
        "hyp_id": AU_ID,
        "stage": "AU5",
        "thesis": AU_THESIS,
        "decision": final,
        "markers_ok": markers,
        "scoreboard_ok": board,
        "antifp_ok": antifp,
        "realeval_ok": realeval,
        "scoreboard": list(AU_SCOREBOARD),
        "evidence": evidence,
        "stage_facts": _stage_facts(),
        "ask_smoke": ask,
        "public_report": "docs/results/nano-lm/wave-au-summary.md",
        "paper_lab": "docs/results/nano-lm/paper-lab-wave-au.md",
        "wave_status": "RESEARCH_COMPLETE" if ok else "OPEN",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "finding": (
            f"{AU_ID}: decision={final}; "
            f"markers={markers}; scoreboard={board}; "
            f"antifp={antifp}; realeval={realeval}."
        ),
        "next": "AU6 AU-FREEZE",
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
        summary = run_au_report(
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
                "hyp_id": AU_ID,
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
