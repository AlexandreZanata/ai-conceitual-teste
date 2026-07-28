"""Wave BB REPORT runner: public closeout + BB-FOREVER/modes live smoke."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from bb_real_eval_ops import battery_row_ok
from bb_report_ops import (
    BB_EVIDENCE,
    BB_ID,
    BB_SCOREBOARD,
    BB_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_bb_report,
    realeval_section_ok,
    render_paper_lab_wave_bb,
    render_wave_bb_summary,
    report_markers_ok,
    scoreboard_ok,
)
from bb_session_ops import BB0_ASK_BATTERY
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-bb/bb_report_summary.json"
_SUMMARY = REPO / "docs/results/nano-lm/wave-bb-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-bb.md"
_FREEZE_STUB = REPO / "docs/results/nano-lm/bb-freeze.md"
_FORMAL_FREEZE_STUB = REPO / "docs/results/nano-lm/formal-habbfreeze-bb-freeze.md"
_LOCAL_SESSION = REPO / ".local/wave-bb/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENTS = REPO / "AGENTS.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"

# Compact live smoke: LOOKUP · OOD · BB-FOREVER · over-refuse (max HW, low RAM).
_SMOKE_IDS = frozenset(
    {"BB-ASK-01", "BB-ASK-02", "BB-ASK-07", "BB-ASK-08"}
)


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


def _hardware() -> tuple[int, int]:
    """Max safe CPU: leave ~6 cores free (16c → threads≈10, workers≤6)."""
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 6))
    workers = min(6, max(4, cpus - 6))
    return threads, workers


def _evidence_map() -> dict[str, bool]:
    return {p: (REPO / p).is_file() for p in BB_EVIDENCE}


def _load_json(rel: str) -> dict[str, Any] | None:
    path = REPO / rel
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_facts() -> dict[str, Any]:
    keys = {
        "session": "results/nano-lm/wave-bb/bb0_session.json",
        "intentgen": "results/nano-lm/wave-bb/intentgen_summary.json",
        "fasthold": "results/nano-lm/wave-bb/bb_fasthold_summary.json",
        "ctxhold": "results/nano-lm/wave-bb/bb_ctxhold_summary.json",
        "nanogen12": "results/nano-lm/wave-bb/nanogen12_summary.json",
        "real_eval": "results/nano-lm/wave-bb/bb_real_eval_summary.json",
    }
    out: dict[str, Any] = {}
    for name, rel in keys.items():
        data = _load_json(rel) or {}
        out[name] = data.get("decision")
    return out


def _smoke_bb_modes(*, workers: int) -> dict[str, Any]:
    """LOOKUP · OOD · BB-FOREVER FP · over-refuse via BB ask path."""
    from run_bb_real_eval import _ask_row

    items = [dict(p) for p in BB0_ASK_BATTERY if p["id"] in _SMOKE_IDS]

    def _one(item: dict[str, str]) -> dict[str, Any]:
        return _ask_row(
            item=item, root=_CHAMPION, bank=_Z_BANK, curated=_CURATED
        )

    with ThreadPoolExecutor(max_workers=min(workers, len(items) or 1)) as pool:
        rows = list(pool.map(_one, items))
    by_id = {str(r["id"]): r for r in rows}
    ordered = [by_id[i["id"]] for i in items]
    ok = all(battery_row_ok(r) for r in ordered)
    return {
        "ok": ok,
        "decision": "PROMOTE" if ok else "KILL (BB forever/modes smoke)",
        "n_pass": sum(1 for r in ordered if battery_row_ok(r)),
        "n_total": len(ordered),
        "arms": [
            {
                "id": r.get("id"),
                "kind": r.get("kind"),
                "product_mode": r.get("product_mode"),
                "expect_mode": r.get("expect_mode"),
                "wall_ms": r.get("wall_ms"),
                "n_new": r.get("n_new"),
                "content_ok": r.get("content_ok"),
                "row_ok": battery_row_ok(r),
            }
            for r in ordered
        ],
    }


def _write_stub(path: Path, title: str) -> None:
    if path.is_file():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                f"# {title} — placeholder (pending BB7)",
                "",
                "> Written by BB6 report so paper-lab links resolve. "
                "BB7 replaces this with the formal freeze.",
                "",
                f"Ship claim: **{SHIP_CLAIM}**",
                "",
                "Do not invent Wave BC without lab-book reopen.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _ensure_freeze_stubs() -> None:
    _write_stub(_FREEZE_STUB, "BB-FREEZE")
    _write_stub(_FORMAL_FREEZE_STUB, "formal-habbfreeze-bb-freeze")


def _write_public() -> None:
    _SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    _ensure_freeze_stubs()
    _SUMMARY.write_text(render_wave_bb_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_bb(), encoding="utf-8")


def _status_word(decision: str) -> str:
    return (
        "PROMOTE"
        if decision == "PROMOTE" or decision.startswith("PROMOTE")
        else decision.split("(", 1)[0].strip()
    )


def _update_local_session(decision: str) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    status = (
        "DONE — PROMOTE"
        if decision == "PROMOTE"
        else f"DONE — {decision}"
    )
    body = "\n".join(
        [
            f"# Wave BB session checklist (**OPEN** · BB6 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md`.  ",
            "> Ship lock: **"
            + SHIP_CLAIM
            + "** · ≤5M (no TAC / true-continue unlock).",
            "",
            "## Current stage",
            "",
            f"**BB6 — BB-REPORT ({status})** · Next: **BB7 BB-FREEZE**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **BB OPEN** (RESEARCH_COMPLETE pending FREEZE) |",
            f"| Decision | **{decision}** |",
            "| Public | `docs/results/nano-lm/wave-bb-summary.md` |",
            "| Paper-lab | `docs/results/nano-lm/paper-lab-wave-bb.md` |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| BB0 | SESSION | **DONE — PROMOTE** |",
            "| BB1 | H-INTENTGEN | **DONE — PROMOTE** |",
            "| BB2 | H-FASTHOLD | **DONE — PROMOTE** |",
            "| BB3 | H-CTXHOLD | **DONE — PROMOTE** |",
            "| BB4 | H-NANOGEN12 | **DONE — DEFER** |",
            "| BB5 | BB-REAL-EVAL | **DONE — PROMOTE** |",
            f"| BB6 | BB-REPORT | **{status}** |",
            "| BB7 | BB-FREEZE | **NEXT** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_local_helpers(status: str) -> None:
    _LOCAL_IMPL.write_text(
        f"""# Implementation plan — nano generative LM

> Private. Lab: [`pesquisa.md`](pesquisa.md).

## Status

**BB0–BB3 PROMOTE · BB4 DEFER · BB5–BB6 DONE — {status}**. Next: **BB7 BB-FREEZE**.

```bash
npm run nano:bb:report
npm run nano:test && npm run verify
```
""",
        encoding="utf-8",
    )
    _LOCAL_README.write_text(
        f"""# Local research notebook

Full lab book: **`pesquisa.md`**.

**Wave BB ACTIVE** — BB6 **BB-REPORT {status}** (gen locked).

Next: **BB7 BB-FREEZE**.
""",
        encoding="utf-8",
    )


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    status = _status_word(decision)
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    text2, n = re.subn(
        r"\| BB6 \| \*\*BB-REPORT\*\* \|[^\n]+\| \*\*NEXT\*\* \|",
        (
            "| BB6 | **BB-REPORT** | Summary + paper-lab "
            "(+ update archive paper if lift measured) | "
            "anti-FP · HOLD/DEFER cited | "
            f"**DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"(\| BB7 \| \*\*BB-FREEZE\*\* \|[^\n]+\| )\*\*TODO\*\* \|",
        r"\1**NEXT** |",
        text,
        count=1,
    )
    if n:
        text = text2
    text = text.replace(
        (
            "7. **BB6 BB-REPORT** — **NEXT** — summary + paper-lab.  \n"
            "8. **BB7 BB-FREEZE** — lock outcomes "
            "(update `paper/` only if measured).  "
        ),
        (
            f"7. **BB6 BB-REPORT** — **DONE {status}** "
            "(`npm run nano:bb:report`) · next BB7 freeze.  \n"
            "8. **BB7 BB-FREEZE** — **NEXT** — lock outcomes "
            "(update `paper/` only if measured).  "
        ),
        1,
    )
    text = text.replace(
        "> **Session:** `.local/wave-bb/SESSION.md` "
        "(BB5 BB-REAL-EVAL **DONE — PROMOTE**; next BB6 BB-REPORT).  ",
        "> **Session:** `.local/wave-bb/SESSION.md` "
        f"(BB6 BB-REPORT **DONE — {status}**; next BB7 BB-FREEZE).  ",
        1,
    )
    if "# next: nano:bb:report" in text:
        text = text.replace(
            "# next: nano:bb:report\n# npm run nano:bb:report\n",
            "npm run nano:bb:report\n# next: nano:bb:freeze\n",
            1,
        )
        if "# next: nano:bb:report" in text:
            text = text.replace(
                "# next: nano:bb:report\n",
                "npm run nano:bb:report\n# next: nano:bb:freeze\n",
                1,
            )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")
    _patch_local_helpers(status)


def _bb_active_line(status: str) -> str:
    return (
        "BB0 [SESSION PROMOTE](wave-bb-session.md) · "
        "BB1 [H-INTENTGEN PROMOTE](formal-hintentgen-intentgen.md) · "
        "BB2 [H-FASTHOLD PROMOTE](formal-hfasthold-fasthold.md) · "
        "BB3 [H-CTXHOLD PROMOTE](formal-hctxhold-ctxhold.md) · "
        "BB4 [H-NANOGEN12 DEFER](formal-hnanogen12-nanogen12.md) · "
        "BB5 [BB-REAL-EVAL PROMOTE](wave-bb-real-eval.md) · "
        f"BB6 [BB-REPORT {status}](wave-bb-summary.md) "
        "(`npm run nano:bb:report`) · [paper-lab-wave-bb.md]"
        "(paper-lab-wave-bb.md); next BB7 BB-FREEZE; ship remains "
        "**AF + AQ + AS trust + STRICT ablated DECODE**; ≤5M stays"
    )


def _patch_recipes(status: str) -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    line = f"**Wave BB ACTIVE:** {_bb_active_line(status)}."
    text2, n = re.subn(
        r"\*\*Wave BB ACTIVE:\*\*[^\n]*",
        line,
        text,
        count=1,
    )
    if n:
        text = text2
    if "Wave BB6 BB-REPORT" not in text:
        needle = (
            "| Wave BB5 BB-REAL-EVAL | [wave-bb-real-eval.md]"
            "(wave-bb-real-eval.md) **PROMOTE** "
            "(`npm run nano:bb:real-eval`) — battery 12/12 · "
            "gen locked (BB4 DEFER) |\n"
        )
        row = (
            "| Wave BB6 BB-REPORT | [wave-bb-summary.md]"
            "(wave-bb-summary.md) · [paper-lab-wave-bb.md]"
            "(paper-lab-wave-bb.md) **PROMOTE** "
            "(`npm run nano:bb:report`) — anti-FP · BB4 DEFER · "
            "NANOGEN6/7 HOLD · NANOGEN8·9·10·11 DEFER cited |\n"
        )
        if needle in text:
            text = text.replace(needle, needle + row, 1)
        elif "| Wave BB5 BB-REAL-EVAL |" in text:
            text2, n2 = re.subn(
                r"(\| Wave BB5 BB-REAL-EVAL \|[^\n]+\|\n)",
                rf"\1{row}",
                text,
                count=1,
            )
            if n2:
                text = text2
    _RECIPES.write_text(text, encoding="utf-8")


def _patch_card(status: str) -> None:
    if not _CARD.is_file():
        return
    text = _CARD.read_text(encoding="utf-8")
    line = f"**Wave BB ACTIVE** — {_bb_active_line(status)}."
    text2, n = re.subn(
        r"\*\*Wave BB ACTIVE\*\* —[^\n]*",
        line,
        text,
        count=1,
    )
    if n:
        _CARD.write_text(text2, encoding="utf-8")


def _patch_agents(status: str) -> None:
    if not _AGENTS.is_file():
        return
    text = _AGENTS.read_text(encoding="utf-8")
    agents = (
        "- **Wave BB ACTIVE** — BB0 [SESSION PROMOTE]"
        "(docs/results/nano-lm/wave-bb-session.md) · BB1 [H-INTENTGEN PROMOTE]"
        "(docs/results/nano-lm/formal-hintentgen-intentgen.md) · BB2 "
        "[H-FASTHOLD PROMOTE](docs/results/nano-lm/formal-hfasthold-fasthold.md) · "
        "BB3 [H-CTXHOLD PROMOTE]"
        "(docs/results/nano-lm/formal-hctxhold-ctxhold.md) · BB4 "
        "[H-NANOGEN12 DEFER](docs/results/nano-lm/formal-hnanogen12-nanogen12.md) "
        "· BB5 [BB-REAL-EVAL PROMOTE]"
        "(docs/results/nano-lm/wave-bb-real-eval.md) · "
        f"BB6 [BB-REPORT {status}]"
        "(docs/results/nano-lm/wave-bb-summary.md) "
        "(`npm run nano:bb:report`) · "
        "[paper-lab-wave-bb.md](docs/results/nano-lm/paper-lab-wave-bb.md); "
        "next BB7 BB-FREEZE; ship remains "
        "**AF + AQ + AS trust + STRICT ablated DECODE**; ≤5M stays."
    )
    text2, n = re.subn(
        r"- \*\*Wave BB ACTIVE\*\* —[^\n]+", agents, text, count=1
    )
    if n:
        _AGENTS.write_text(text2, encoding="utf-8")


def _patch_agenda(status: str) -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    row = (
        f"| **BB** | **ACTIVE** | BB0–BB3 PROMOTE · BB4 DEFER · BB5 "
        f"BB-REAL-EVAL PROMOTE · BB6 BB-REPORT {status} "
        f"(`npm run nano:bb:report`); next BB7 BB-FREEZE; ≤5M |"
    )
    text2, n = re.subn(
        r"\| \*\*BB\*\* \| \*\*ACTIVE\*\* \|[^\n]+", row, text, count=1
    )
    if n:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen(status: str) -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    text = text.replace(
        (
            "Wave BB ACTIVE (BB0–BB3 PROMOTE · BB4 DEFER · "
            "BB5 BB-REAL-EVAL PROMOTE; next BB6 BB-REPORT)"
        ),
        (
            f"Wave BB ACTIVE (BB0–BB3 PROMOTE · BB4 DEFER · "
            f"BB5 BB-REAL-EVAL PROMOTE · BB6 BB-REPORT {status}; "
            f"next BB7 BB-FREEZE)"
        ),
        1,
    )
    _EVOGEN.write_text(text, encoding="utf-8")


def _patch_public_status(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    status = "PROMOTE"
    _patch_recipes(status)
    _patch_card(status)
    _patch_agents(status)
    _patch_agenda(status)
    _patch_evogen(status)


def _gates(
    decision: str,
    *,
    markers: bool,
    board: bool,
    antifp: bool,
    realeval: bool,
    ask: dict[str, Any] | None,
) -> str:
    if ask is not None and not bool(ask.get("ok")):
        return "KILL (BB forever/modes smoke failed)"
    if decision.startswith("PROMOTE") and not markers:
        return "KILL (wave-bb-summary missing thesis markers)"
    if decision.startswith("PROMOTE") and not board:
        return "KILL (wave-bb-summary missing scoreboard)"
    if decision.startswith("PROMOTE") and not antifp:
        return "KILL (wave-bb-summary missing anti-FP evidence)"
    if decision.startswith("PROMOTE") and not realeval:
        return "KILL (wave-bb-summary missing real-eval section)"
    return decision


def run_bb_report(
    *, out: Path, skip_ask: bool = False, workers: int = 6
) -> dict[str, Any]:
    """
    GIVEN BB0–BB5 evidence
    WHEN writing public summary + paper-lab and checking anti-FP/mode smoke
    THEN PROMOTE iff evidence ∧ markers ∧ scoreboard ∧ antifp ∧ realeval ∧ smoke.
    """
    _write_public()
    evidence = _evidence_map()
    decision = decide_bb_report(evidence)
    report_text = _SUMMARY.read_text(encoding="utf-8")
    markers = report_markers_ok(report_text)
    board = scoreboard_ok(report_text)
    antifp = antifp_section_ok(report_text)
    realeval = realeval_section_ok(report_text)
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_bb_modes(workers=workers)
    decision = _gates(
        decision,
        markers=markers,
        board=board,
        antifp=antifp,
        realeval=realeval,
        ask=ask,
    )
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
    _patch_public_status(final)
    payload: dict[str, Any] = {
        "id": BB_ID,
        "hyp_id": BB_ID,
        "stage": "BB6",
        "thesis": BB_THESIS,
        "decision": final,
        "markers_ok": markers,
        "scoreboard_ok": board,
        "antifp_ok": antifp,
        "realeval_ok": realeval,
        "scoreboard": list(BB_SCOREBOARD),
        "evidence": evidence,
        "stage_facts": _stage_facts(),
        "ask_smoke": ask,
        "public_report": "docs/results/nano-lm/wave-bb-summary.md",
        "paper_lab": "docs/results/nano-lm/paper-lab-wave-bb.md",
        "wave_status": "RESEARCH_COMPLETE" if ok else "OPEN",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "workers": int(workers),
        "finding": (
            f"{BB_ID}: decision={final}; "
            f"markers={markers}; scoreboard={board}; "
            f"antifp={antifp}; realeval={realeval}."
        ),
        "next": "BB7 BB-FREEZE",
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave BB6 BB-REPORT")
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        summary = run_bb_report(
            out=Path(args.out),
            skip_ask=bool(args.skip_ask),
            workers=workers,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    ok = str(summary.get("decision")) == "PROMOTE"
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": BB_ID,
                "decision": summary.get("decision"),
                "markers_ok": summary.get("markers_ok"),
                "scoreboard_ok": summary.get("scoreboard_ok"),
                "antifp_ok": summary.get("antifp_ok"),
                "realeval_ok": summary.get("realeval_ok"),
                "ask_smoke_ok": (summary.get("ask_smoke") or {}).get("ok"),
                "cpu_threads": threads,
                "workers": workers,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
