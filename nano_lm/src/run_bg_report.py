"""Wave BG REPORT runner: public closeout + BG-FOREVER/modes live smoke."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from bg_real_eval_ops import battery_row_ok
from bg_report_ops import (
    BG_EVIDENCE,
    BG_ID,
    BG_SCOREBOARD,
    BG_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_bg_report,
    realeval_section_ok,
    render_paper_lab_wave_bg,
    render_wave_bg_summary,
    report_markers_ok,
    scoreboard_ok,
)
from bg_session_ops import BG0_ASK_BATTERY
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-bg/bg_report_summary.json"
_SUMMARY = REPO / "docs/results/nano-lm/wave-bg-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-bg.md"
_FREEZE_STUB = REPO / "docs/results/nano-lm/bg-freeze.md"
_FORMAL_FREEZE_STUB = REPO / "docs/results/nano-lm/formal-habgfreeze-bg-freeze.md"
_LOCAL_SESSION = REPO / ".local/wave-bg/SESSION.md"
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

# Compact live smoke: LOOKUP · OOD · BG-FOREVER unary · over-refuse · util.
_SMOKE_IDS = frozenset(
    {"BG-ASK-01", "BG-ASK-02", "BG-ASK-07", "BG-ASK-08", "BG-ASK-17"}
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
    # 16c / ~31Gi: leave ≥6 cores free under mem pressure; cap workers.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 6))
    workers = min(6, max(3, cpus - 6))
    return threads, workers


def _evidence_map() -> dict[str, bool]:
    return {p: (REPO / p).is_file() for p in BG_EVIDENCE}


def _load_json(rel: str) -> dict[str, Any] | None:
    path = REPO / rel
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_facts() -> dict[str, Any]:
    keys = {
        "session": "results/nano-lm/wave-bg/bg0_session.json",
        "unaryint": "results/nano-lm/wave-bg/unaryint_summary.json",
        "shippub": "results/nano-lm/wave-bg/shippub_summary.json",
        "fastbg": "results/nano-lm/wave-bg/fastbg_summary.json",
        "ctxbg": "results/nano-lm/wave-bg/ctxbg_summary.json",
        "nanogen17": "results/nano-lm/wave-bg/nanogen17_summary.json",
        "real_eval": "results/nano-lm/wave-bg/bg_real_eval_summary.json",
    }
    out: dict[str, Any] = {}
    for name, rel in keys.items():
        data = _load_json(rel) or {}
        out[name] = data.get("decision")
    return out


def _smoke_bg_modes(*, workers: int) -> dict[str, Any]:
    """LOOKUP · OOD · BG-FOREVER FP · over-refuse · util via BG ask path."""
    from run_bg_real_eval import _ask_row

    items = [dict(p) for p in BG0_ASK_BATTERY if p["id"] in _SMOKE_IDS]

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
        "decision": "PROMOTE" if ok else "KILL (BG forever/modes smoke)",
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
                f"# {title} — placeholder (pending BG8)",
                "",
                "> Written by BG7 report so paper-lab links resolve. "
                "BG8 replaces this with the formal freeze.",
                "",
                f"Ship claim: **{SHIP_CLAIM}**",
                "",
                "Do not invent Wave BH without lab-book reopen.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _ensure_freeze_stubs() -> None:
    _write_stub(_FREEZE_STUB, "BG-FREEZE")
    _write_stub(_FORMAL_FREEZE_STUB, "formal-habgfreeze-bg-freeze")


def _write_public() -> None:
    _SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    _ensure_freeze_stubs()
    _SUMMARY.write_text(render_wave_bg_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_bg(), encoding="utf-8")


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
            f"# Wave BG session checklist (**OPEN** · BG7 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md`.  ",
            "> Ship lock: **"
            + SHIP_CLAIM
            + "** · ≤5M (no TAC / true-continue unlock).",
            "",
            "## Current stage",
            "",
            f"**BG7 — BG-REPORT ({status})** · Next: **BG8 BG-FREEZE**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **BG OPEN** (RESEARCH_COMPLETE pending FREEZE) |",
            f"| Decision | **{decision}** |",
            "| Public | `docs/results/nano-lm/wave-bg-summary.md` |",
            "| Paper-lab | `docs/results/nano-lm/paper-lab-wave-bg.md` |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| BG0 | SESSION | **DONE — PROMOTE** |",
            "| BG1 | H-UNARYINT | **DONE — PROMOTE** |",
            "| BG2 | H-SHIPPUB | **DONE — PROMOTE** |",
            "| BG3 | H-FASTBG | **DONE — PROMOTE** |",
            "| BG4 | H-CTXBG | **DONE — PROMOTE** |",
            "| BG5 | H-NANOGEN17 / SKIP | **DONE — SKIP** |",
            "| BG6 | BG-REAL-EVAL | **DONE — PROMOTE** |",
            f"| BG7 | BG-REPORT | **{status}** |",
            "| BG8 | BG-FREEZE | **NEXT** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_local_helpers(status: str) -> None:
    _LOCAL_IMPL.write_text(
        f"""# Implementation plan — nano generative LM

> Private. Lab: [`pesquisa.md`](pesquisa.md).

## Status

**BG0–BG4 PROMOTE · BG5 SKIP · BG6–BG7 DONE — {status}**. Next: **BG8 BG-FREEZE**.

```bash
npm run nano:bg:report
npm run nano:test && npm run verify
```
""",
        encoding="utf-8",
    )
    _LOCAL_README.write_text(
        f"""# Local research notebook

Full lab book: **`pesquisa.md`**.

**Wave BG ACTIVE** — BG7 **BG-REPORT {status}** (gen locked · util cited).

Next: **BG8 BG-FREEZE**.
""",
        encoding="utf-8",
    )


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    status = _status_word(decision)
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    text2, n = re.subn(
        r"\| BG7 \| \*\*BG-REPORT\*\* \|[^\n]+\| \*\*NEXT\*\* \|",
        (
            "| BG7 | **BG-REPORT** | Summary + paper-lab "
            "(+ arXiv path) | "
            "anti-FP · util · SKIP cited | "
            f"**DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"(\| BG8 \| \*\*BG-FREEZE\*\* \|[^\n]+\| )\*\*TODO\*\* \|",
        r"\1**NEXT** |",
        text,
        count=1,
    )
    if n:
        text = text2
    else:
        text2, n = re.subn(
            r"(\| BG8 \| \*\*BG-FREEZE\*\* \|[^\n]+\| )pending \|",
            r"\1**NEXT** |",
            text,
            count=1,
        )
        if n:
            text = text2
    text = text.replace(
        (
            "8. **BG7 BG-REPORT** — **NEXT** — summary + paper-lab; "
            "arXiv path if measured lift.  \n"
            "9. **BG8 BG-FREEZE** — lock; do not invent Wave BH.  "
        ),
        (
            f"8. **BG7 BG-REPORT** — **DONE {status}** "
            "(`npm run nano:bg:report`) · next BG8 freeze.  \n"
            "9. **BG8 BG-FREEZE** — **NEXT** — lock; do not invent Wave BH.  "
        ),
        1,
    )
    text = text.replace(
        "> **Session:** `.local/wave-bg/SESSION.md` "
        "(BG6 BG-REAL-EVAL **DONE — PROMOTE**; next BG7 BG-REPORT).  ",
        "> **Session:** `.local/wave-bg/SESSION.md` "
        f"(BG7 BG-REPORT **DONE — {status}**; next BG8 BG-FREEZE).  ",
        1,
    )
    text = text.replace(
        "(BG6 BG-REAL-EVAL **DONE — PROMOTE**; next BG7 BG-REPORT)",
        f"(BG7 BG-REPORT **DONE — {status}**; next BG8 BG-FREEZE)",
    )
    text = text.replace(
        "npm run nano:bg:real-eval\n# next: nano:bg:report\n",
        "npm run nano:bg:real-eval\nnpm run nano:bg:report\n"
        "# next: nano:bg:freeze\n",
        1,
    )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")
    _patch_local_helpers(status)


def _bg_active_line(status: str) -> str:
    return (
        "BG0 [SESSION PROMOTE](wave-bg-session.md) · "
        "BG1 [H-UNARYINT PROMOTE](formal-hunaryint-unaryint.md) · "
        "BG2 [H-SHIPPUB PROMOTE](formal-hshippub-shippub.md) · "
        "BG3 [H-FASTBG PROMOTE](formal-hfastbg-fastbg.md) · "
        "BG4 [H-CTXBG PROMOTE](formal-hctxbg-ctxbg.md) · "
        "BG5 [H-NANOGEN17 SKIP](formal-hnanogen17-nanogen17.md) · "
        "BG6 [BG-REAL-EVAL PROMOTE](wave-bg-real-eval.md) · "
        f"BG7 [BG-REPORT {status}](wave-bg-summary.md) "
        "(`npm run nano:bg:report`) · [paper-lab-wave-bg.md]"
        "(paper-lab-wave-bg.md); next BG8 BG-FREEZE; ship remains "
        "**AF + AQ + AS trust + STRICT ablated DECODE**; ≤5M stays"
    )


def _patch_recipes(status: str) -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    line = f"**Wave BG ACTIVE:** {_bg_active_line(status)}."
    text2, n = re.subn(
        r"\*\*Wave BG ACTIVE:\*\*[^\n]*",
        line,
        text,
        count=1,
    )
    if n:
        text = text2
    if "Wave BG7 BG-REPORT" not in text:
        row = (
            "| Wave BG7 BG-REPORT | [wave-bg-summary.md]"
            "(wave-bg-summary.md) · [paper-lab-wave-bg.md]"
            "(paper-lab-wave-bg.md) **PROMOTE** "
            "(`npm run nano:bg:report`) — anti-FP · util · BG5 SKIP · "
            "NANOGEN6/7 HOLD · NANOGEN8…15 DEFER · NANOGEN16 SKIP · "
            "NANOGEN17 SKIP cited |\n"
        )
        if "| Wave BG6 BG-REAL-EVAL |" in text:
            text2, n2 = re.subn(
                r"(\| Wave BG6 BG-REAL-EVAL \|[^\n]+\|\n)",
                rf"\1{row}",
                text,
                count=1,
            )
            if n2:
                text = text2
            else:
                text = text.replace(
                    "| Wave BG6 BG-REAL-EVAL |",
                    row + "| Wave BG6 BG-REAL-EVAL |",
                    1,
                )
    _RECIPES.write_text(text, encoding="utf-8")


def _patch_card(status: str) -> None:
    if not _CARD.is_file():
        return
    text = _CARD.read_text(encoding="utf-8")
    line = f"**Wave BG ACTIVE** — {_bg_active_line(status)}."
    text2, n = re.subn(
        r"\*\*Wave BG ACTIVE\*\* —[^\n]*",
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
        "- **Wave BG ACTIVE** — BG0 [SESSION PROMOTE]"
        "(docs/results/nano-lm/wave-bg-session.md) "
        "(`npm run nano:bg:session`) · BG1 [H-UNARYINT PROMOTE]"
        "(docs/results/nano-lm/formal-hunaryint-unaryint.md) "
        "(`npm run nano:unaryint`) · BG2 [H-SHIPPUB PROMOTE]"
        "(docs/results/nano-lm/formal-hshippub-shippub.md) "
        "(`npm run nano:shippub`) · BG3 [H-FASTBG PROMOTE]"
        "(docs/results/nano-lm/formal-hfastbg-fastbg.md) "
        "(`npm run nano:fastbg`) · BG4 [H-CTXBG PROMOTE]"
        "(docs/results/nano-lm/formal-hctxbg-ctxbg.md) "
        "(`npm run nano:ctxbg`) · BG5 [H-NANOGEN17 SKIP]"
        "(docs/results/nano-lm/formal-hnanogen17-nanogen17.md) "
        "(`npm run nano:nanogen17`) · BG6 [BG-REAL-EVAL PROMOTE]"
        "(docs/results/nano-lm/wave-bg-real-eval.md) "
        "(`npm run nano:bg:real-eval`) · "
        f"BG7 [BG-REPORT {status}]"
        "(docs/results/nano-lm/wave-bg-summary.md) "
        "(`npm run nano:bg:report`) · "
        "[paper-lab-wave-bg.md](docs/results/nano-lm/paper-lab-wave-bg.md); "
        "next BG8 BG-FREEZE; ship remains "
        "**AF + AQ + AS trust + STRICT ablated DECODE**; NANOGEN6·7 HOLD · "
        "NANOGEN8…15 DEFER · NANOGEN16 SKIP · NANOGEN17 SKIP; ≤5M stays."
    )
    text2, n = re.subn(
        r"- \*\*Wave BG ACTIVE\*\* —[^\n]+", agents, text, count=1
    )
    if n:
        _AGENTS.write_text(text2, encoding="utf-8")


def _patch_agenda(status: str) -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    row = (
        f"| **BG** | **ACTIVE** | BG0–BG4 PROMOTE · BG5 SKIP · BG6 "
        f"BG-REAL-EVAL PROMOTE · BG7 BG-REPORT {status} "
        f"(`npm run nano:bg:report`); next BG8 BG-FREEZE; ≤5M |"
    )
    text2, n = re.subn(
        r"\| \*\*BG\*\* \| \*\*ACTIVE\*\* \|[^\n]+", row, text, count=1
    )
    if n:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen(status: str) -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    text = text.replace(
        "BG6 BG-REAL-EVAL PROMOTE; next BG7 BG-REPORT",
        f"BG6 BG-REAL-EVAL PROMOTE · BG7 BG-REPORT {status}; "
        "next BG8 BG-FREEZE",
        1,
    )
    text = text.replace(
        "next BG7 BG-REPORT",
        f"BG7 BG-REPORT {status}; next BG8 BG-FREEZE",
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
        return "KILL (BG forever/modes smoke failed)"
    if decision.startswith("PROMOTE") and not markers:
        return "KILL (wave-bg-summary missing thesis markers)"
    if decision.startswith("PROMOTE") and not board:
        return "KILL (wave-bg-summary missing scoreboard)"
    if decision.startswith("PROMOTE") and not antifp:
        return "KILL (wave-bg-summary missing anti-FP evidence)"
    if decision.startswith("PROMOTE") and not realeval:
        return "KILL (wave-bg-summary missing real-eval section)"
    return decision


def run_bg_report(
    *, out: Path, skip_ask: bool = False, workers: int = 6
) -> dict[str, Any]:
    """
    GIVEN BG0–BG6 evidence
    WHEN writing public summary + paper-lab and checking anti-FP/mode smoke
    THEN PROMOTE iff evidence ∧ markers ∧ scoreboard ∧ antifp ∧ realeval ∧ smoke.
    """
    _write_public()
    evidence = _evidence_map()
    decision = decide_bg_report(evidence)
    report_text = _SUMMARY.read_text(encoding="utf-8")
    markers = report_markers_ok(report_text)
    board = scoreboard_ok(report_text)
    antifp = antifp_section_ok(report_text)
    realeval = realeval_section_ok(report_text)
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_bg_modes(workers=workers)
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
        "id": BG_ID,
        "hyp_id": BG_ID,
        "stage": "BG7",
        "thesis": BG_THESIS,
        "decision": final,
        "markers_ok": markers,
        "scoreboard_ok": board,
        "antifp_ok": antifp,
        "realeval_ok": realeval,
        "scoreboard": list(BG_SCOREBOARD),
        "evidence": evidence,
        "stage_facts": _stage_facts(),
        "ask_smoke": ask,
        "public_report": "docs/results/nano-lm/wave-bg-summary.md",
        "paper_lab": "docs/results/nano-lm/paper-lab-wave-bg.md",
        "wave_status": "RESEARCH_COMPLETE" if ok else "OPEN",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "workers": int(workers),
        "finding": (
            f"{BG_ID}: decision={final}; "
            f"markers={markers}; scoreboard={board}; "
            f"antifp={antifp}; realeval={realeval}."
        ),
        "next": "BG8 BG-FREEZE",
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave BG7 BG-REPORT")
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        summary = run_bg_report(
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
                "hyp_id": BG_ID,
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
