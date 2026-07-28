"""Wave BD REPORT runner: public closeout + BD-FOREVER/modes live smoke."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from bd_real_eval_ops import battery_row_ok
from bd_report_ops import (
    BD_EVIDENCE,
    BD_ID,
    BD_SCOREBOARD,
    BD_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_bd_report,
    realeval_section_ok,
    render_paper_lab_wave_bd,
    render_wave_bd_summary,
    report_markers_ok,
    scoreboard_ok,
)
from bd_session_ops import BD0_ASK_BATTERY
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-bd/bd_report_summary.json"
_SUMMARY = REPO / "docs/results/nano-lm/wave-bd-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-bd.md"
_FREEZE_STUB = REPO / "docs/results/nano-lm/bd-freeze.md"
_FORMAL_FREEZE_STUB = REPO / "docs/results/nano-lm/formal-habdfreeze-bd-freeze.md"
_LOCAL_SESSION = REPO / ".local/wave-bd/SESSION.md"
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

# Compact live smoke: LOOKUP · OOD · BD-FOREVER · over-refuse (max HW, low RAM).
_SMOKE_IDS = frozenset(
    {"BD-ASK-01", "BD-ASK-02", "BD-ASK-07", "BD-ASK-08", "BD-ASK-13"}
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
    """Max safe CPU: leave ~4 cores free (16c → threads≈12, workers≤8)."""
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    workers = min(8, max(4, cpus - 4))
    return threads, workers


def _evidence_map() -> dict[str, bool]:
    return {p: (REPO / p).is_file() for p in BD_EVIDENCE}


def _load_json(rel: str) -> dict[str, Any] | None:
    path = REPO / rel
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_facts() -> dict[str, Any]:
    keys = {
        "session": "results/nano-lm/wave-bd/bd0_session.json",
        "semint": "results/nano-lm/wave-bd/semint_summary.json",
        "fastgain": "results/nano-lm/wave-bd/bd_fastgain_summary.json",
        "ctxgain": "results/nano-lm/wave-bd/bd_ctxgain_summary.json",
        "nanogen14": "results/nano-lm/wave-bd/nanogen14_summary.json",
        "real_eval": "results/nano-lm/wave-bd/bd_real_eval_summary.json",
    }
    out: dict[str, Any] = {}
    for name, rel in keys.items():
        data = _load_json(rel) or {}
        out[name] = data.get("decision")
    return out


def _smoke_bd_modes(*, workers: int) -> dict[str, Any]:
    """LOOKUP · OOD · BD-FOREVER FP · over-refuse via BD ask path."""
    from run_bd_real_eval import _ask_row

    items = [dict(p) for p in BD0_ASK_BATTERY if p["id"] in _SMOKE_IDS]

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
        "decision": "PROMOTE" if ok else "KILL (BD forever/modes smoke)",
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
                f"# {title} — placeholder (pending BD7)",
                "",
                "> Written by BD6 report so paper-lab links resolve. "
                "BD7 replaces this with the formal freeze.",
                "",
                f"Ship claim: **{SHIP_CLAIM}**",
                "",
                "Do not invent Wave BE without lab-book reopen.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _ensure_freeze_stubs() -> None:
    _write_stub(_FREEZE_STUB, "BD-FREEZE")
    _write_stub(_FORMAL_FREEZE_STUB, "formal-habdfreeze-bd-freeze")


def _write_public() -> None:
    _SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    _ensure_freeze_stubs()
    _SUMMARY.write_text(render_wave_bd_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_bd(), encoding="utf-8")


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
            f"# Wave BD session checklist (**OPEN** · BD6 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md`.  ",
            "> Ship lock: **"
            + SHIP_CLAIM
            + "** · ≤5M (no TAC / true-continue unlock).",
            "",
            "## Current stage",
            "",
            f"**BD6 — BD-REPORT ({status})** · Next: **BD7 BD-FREEZE**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **BD OPEN** (RESEARCH_COMPLETE pending FREEZE) |",
            f"| Decision | **{decision}** |",
            "| Public | `docs/results/nano-lm/wave-bd-summary.md` |",
            "| Paper-lab | `docs/results/nano-lm/paper-lab-wave-bd.md` |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| BD0 | SESSION | **DONE — PROMOTE** |",
            "| BD1 | H-SEMINT | **DONE — PROMOTE** |",
            "| BD2 | H-FASTGAIN | **DONE — PROMOTE** |",
            "| BD3 | H-CTXGAIN | **DONE — PROMOTE** |",
            "| BD4 | H-NANOGEN14 | **DONE — DEFER** |",
            "| BD5 | BD-REAL-EVAL | **DONE — PROMOTE** |",
            f"| BD6 | BD-REPORT | **{status}** |",
            "| BD7 | BD-FREEZE | **NEXT** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_local_helpers(status: str) -> None:
    _LOCAL_IMPL.write_text(
        f"""# Implementation plan — nano generative LM

> Private. Lab: [`pesquisa.md`](pesquisa.md).

## Status

**BD0–BD3 PROMOTE · BD4 DEFER · BD5–BD6 DONE — {status}**. Next: **BD7 BD-FREEZE**.

```bash
npm run nano:bd:report
npm run nano:test && npm run verify
```
""",
        encoding="utf-8",
    )
    _LOCAL_README.write_text(
        f"""# Local research notebook

Full lab book: **`pesquisa.md`**.

**Wave BD ACTIVE** — BD6 **BD-REPORT {status}** (gen locked).

Next: **BD7 BD-FREEZE**.
""",
        encoding="utf-8",
    )


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    status = _status_word(decision)
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    text2, n = re.subn(
        r"\| BD6 \| \*\*BD-REPORT\*\* \|[^\n]+\| \*\*NEXT\*\* \|",
        (
            "| BD6 | **BD-REPORT** | Summary + paper-lab "
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
        r"(\| BD7 \| \*\*BD-FREEZE\*\* \|[^\n]+\| )\*\*TODO\*\* \|",
        r"\1**NEXT** |",
        text,
        count=1,
    )
    if n:
        text = text2
    else:
        text2, n = re.subn(
            r"(\| BD7 \| \*\*BD-FREEZE\*\* \|[^\n]+\| )pending \|",
            r"\1**NEXT** |",
            text,
            count=1,
        )
        if n:
            text = text2
    text = text.replace(
        (
            "7. **BD6 BD-REPORT** — **NEXT** — summary + paper-lab; "
            "update paper only after measured lift.  \n"
            "8. **BD7 BD-FREEZE** — lock; do not invent Wave BE.  "
        ),
        (
            f"7. **BD6 BD-REPORT** — **DONE {status}** "
            "(`npm run nano:bd:report`) · next BD7 freeze.  \n"
            "8. **BD7 BD-FREEZE** — **NEXT** — lock; do not invent Wave BE.  "
        ),
        1,
    )
    text = text.replace(
        "> **Session:** `.local/wave-bd/SESSION.md` "
        "(BD5 BD-REAL-EVAL **DONE — PROMOTE**; next BD6 BD-REPORT).  ",
        "> **Session:** `.local/wave-bd/SESSION.md` "
        f"(BD6 BD-REPORT **DONE — {status}**; next BD7 BD-FREEZE).  ",
        1,
    )
    if "# next: nano:bd:report" in text:
        text = text.replace(
            "# next: nano:bd:report\n# npm run nano:bd:report\n",
            "npm run nano:bd:report\n# next: nano:bd:freeze\n",
            1,
        )
        if "# next: nano:bd:report" in text:
            text = text.replace(
                "# next: nano:bd:report\n",
                "npm run nano:bd:report\n# next: nano:bd:freeze\n",
                1,
            )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")
    _patch_local_helpers(status)


def _bd_active_line(status: str) -> str:
    return (
        "BD0 [SESSION PROMOTE](wave-bd-session.md) · "
        "BD1 [H-SEMINT PROMOTE](formal-hsemint-semint.md) · "
        "BD2 [H-FASTGAIN PROMOTE](formal-hfastgain-fastgain.md) · "
        "BD3 [H-CTXGAIN PROMOTE](formal-hctxgain-ctxgain.md) · "
        "BD4 [H-NANOGEN14 DEFER](formal-hnanogen14-nanogen14.md) · "
        "BD5 [BD-REAL-EVAL PROMOTE](wave-bd-real-eval.md) · "
        f"BD6 [BD-REPORT {status}](wave-bd-summary.md) "
        "(`npm run nano:bd:report`) · [paper-lab-wave-bd.md]"
        "(paper-lab-wave-bd.md); next BD7 BD-FREEZE; ship remains "
        "**AF + AQ + AS trust + STRICT ablated DECODE**; ≤5M stays"
    )


def _patch_recipes(status: str) -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    line = f"**Wave BD ACTIVE:** {_bd_active_line(status)}."
    text2, n = re.subn(
        r"\*\*Wave BD ACTIVE:\*\*[^\n]*",
        line,
        text,
        count=1,
    )
    if n:
        text = text2
    if "Wave BD6 BD-REPORT" not in text:
        needle = (
            "| Wave BD5 BD-REAL-EVAL | [wave-bd-real-eval.md]"
            "(wave-bd-real-eval.md) **PROMOTE** "
            "(`npm run nano:bd:real-eval`) — battery 14/14 · "
            "gen locked (BD4 DEFER) |\n"
        )
        row = (
            "| Wave BD6 BD-REPORT | [wave-bd-summary.md]"
            "(wave-bd-summary.md) · [paper-lab-wave-bd.md]"
            "(paper-lab-wave-bd.md) **PROMOTE** "
            "(`npm run nano:bd:report`) — anti-FP · BD4 DEFER · "
            "NANOGEN6/7 HOLD · NANOGEN8·9·10·11·12·13 DEFER cited |\n"
        )
        if needle in text:
            text = text.replace(needle, needle + row, 1)
        elif "| Wave BD5 BD-REAL-EVAL |" in text:
            text2, n2 = re.subn(
                r"(\| Wave BD5 BD-REAL-EVAL \|[^\n]+\|\n)",
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
    line = f"**Wave BD ACTIVE** — {_bd_active_line(status)}."
    text2, n = re.subn(
        r"\*\*Wave BD ACTIVE\*\* —[^\n]*",
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
        "- **Wave BD ACTIVE** — BD0 [SESSION PROMOTE]"
        "(docs/results/nano-lm/wave-bd-session.md) · BD1 [H-SEMINT PROMOTE]"
        "(docs/results/nano-lm/formal-hsemint-semint.md) · BD2 "
        "[H-FASTGAIN PROMOTE](docs/results/nano-lm/formal-hfastgain-fastgain.md) · "
        "BD3 [H-CTXGAIN PROMOTE]"
        "(docs/results/nano-lm/formal-hctxgain-ctxgain.md) · BD4 "
        "[H-NANOGEN14 DEFER](docs/results/nano-lm/formal-hnanogen14-nanogen14.md) "
        "· BD5 [BD-REAL-EVAL PROMOTE]"
        "(docs/results/nano-lm/wave-bd-real-eval.md) · "
        f"BD6 [BD-REPORT {status}]"
        "(docs/results/nano-lm/wave-bd-summary.md) "
        "(`npm run nano:bd:report`) · "
        "[paper-lab-wave-bd.md](docs/results/nano-lm/paper-lab-wave-bd.md); "
        "next BD7 BD-FREEZE; ship remains "
        "**AF + AQ + AS trust + STRICT ablated DECODE**; ≤5M stays."
    )
    text2, n = re.subn(
        r"- \*\*Wave BD ACTIVE\*\* —[^\n]+", agents, text, count=1
    )
    if n:
        _AGENTS.write_text(text2, encoding="utf-8")


def _patch_agenda(status: str) -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    row = (
        f"| **BD** | **ACTIVE** | BD0–BD3 PROMOTE · BD4 DEFER · BD5 "
        f"BD-REAL-EVAL PROMOTE · BD6 BD-REPORT {status} "
        f"(`npm run nano:bd:report`); next BD7 BD-FREEZE; ≤5M |"
    )
    text2, n = re.subn(
        r"\| \*\*BD\*\* \| \*\*ACTIVE\*\* \|[^\n]+", row, text, count=1
    )
    if n:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen(status: str) -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    text = text.replace(
        (
            "Wave BD ACTIVE (BD0–BD3 PROMOTE · BD4 DEFER · "
            "BD5 BD-REAL-EVAL PROMOTE; next BD6 BD-REPORT)"
        ),
        (
            f"Wave BD ACTIVE (BD0–BD3 PROMOTE · BD4 DEFER · "
            f"BD5 BD-REAL-EVAL PROMOTE · BD6 BD-REPORT {status}; "
            f"next BD7 BD-FREEZE)"
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
        return "KILL (BD forever/modes smoke failed)"
    if decision.startswith("PROMOTE") and not markers:
        return "KILL (wave-bd-summary missing thesis markers)"
    if decision.startswith("PROMOTE") and not board:
        return "KILL (wave-bd-summary missing scoreboard)"
    if decision.startswith("PROMOTE") and not antifp:
        return "KILL (wave-bd-summary missing anti-FP evidence)"
    if decision.startswith("PROMOTE") and not realeval:
        return "KILL (wave-bd-summary missing real-eval section)"
    return decision


def run_bd_report(
    *, out: Path, skip_ask: bool = False, workers: int = 8
) -> dict[str, Any]:
    """
    GIVEN BD0–BD5 evidence
    WHEN writing public summary + paper-lab and checking anti-FP/mode smoke
    THEN PROMOTE iff evidence ∧ markers ∧ scoreboard ∧ antifp ∧ realeval ∧ smoke.
    """
    _write_public()
    evidence = _evidence_map()
    decision = decide_bd_report(evidence)
    report_text = _SUMMARY.read_text(encoding="utf-8")
    markers = report_markers_ok(report_text)
    board = scoreboard_ok(report_text)
    antifp = antifp_section_ok(report_text)
    realeval = realeval_section_ok(report_text)
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_bd_modes(workers=workers)
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
        "id": BD_ID,
        "hyp_id": BD_ID,
        "stage": "BD6",
        "thesis": BD_THESIS,
        "decision": final,
        "markers_ok": markers,
        "scoreboard_ok": board,
        "antifp_ok": antifp,
        "realeval_ok": realeval,
        "scoreboard": list(BD_SCOREBOARD),
        "evidence": evidence,
        "stage_facts": _stage_facts(),
        "ask_smoke": ask,
        "public_report": "docs/results/nano-lm/wave-bd-summary.md",
        "paper_lab": "docs/results/nano-lm/paper-lab-wave-bd.md",
        "wave_status": "RESEARCH_COMPLETE" if ok else "OPEN",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "workers": int(workers),
        "finding": (
            f"{BD_ID}: decision={final}; "
            f"markers={markers}; scoreboard={board}; "
            f"antifp={antifp}; realeval={realeval}."
        ),
        "next": "BD7 BD-FREEZE",
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave BD6 BD-REPORT")
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        summary = run_bd_report(
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
                "hyp_id": BD_ID,
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
