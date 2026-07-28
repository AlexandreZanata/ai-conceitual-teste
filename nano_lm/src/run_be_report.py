"""Wave BE REPORT runner: public closeout + BE-FOREVER/modes live smoke."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from be_real_eval_ops import battery_row_ok
from be_report_ops import (
    BE_EVIDENCE,
    BE_ID,
    BE_SCOREBOARD,
    BE_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_be_report,
    realeval_section_ok,
    render_paper_lab_wave_be,
    render_wave_be_summary,
    report_markers_ok,
    scoreboard_ok,
)
from be_session_ops import BE0_ASK_BATTERY
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-be/be_report_summary.json"
_SUMMARY = REPO / "docs/results/nano-lm/wave-be-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-be.md"
_FREEZE_STUB = REPO / "docs/results/nano-lm/be-freeze.md"
_FORMAL_FREEZE_STUB = REPO / "docs/results/nano-lm/formal-habefreeze-be-freeze.md"
_LOCAL_SESSION = REPO / ".local/wave-be/SESSION.md"
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

# Compact live smoke: LOOKUP · OOD · BE-FOREVER · over-refuse · util.
_SMOKE_IDS = frozenset(
    {"BE-ASK-01", "BE-ASK-02", "BE-ASK-07", "BE-ASK-08", "BE-ASK-15"}
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
    return {p: (REPO / p).is_file() for p in BE_EVIDENCE}


def _load_json(rel: str) -> dict[str, Any] | None:
    path = REPO / rel
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_facts() -> dict[str, Any]:
    keys = {
        "session": "results/nano-lm/wave-be/be0_session.json",
        "compint": "results/nano-lm/wave-be/compint_summary.json",
        "shipuse": "results/nano-lm/wave-be/shipuse_summary.json",
        "fastbe": "results/nano-lm/wave-be/fastbe_summary.json",
        "ctxbe": "results/nano-lm/wave-be/ctxbe_summary.json",
        "nanogen15": "results/nano-lm/wave-be/nanogen15_summary.json",
        "real_eval": "results/nano-lm/wave-be/be_real_eval_summary.json",
    }
    out: dict[str, Any] = {}
    for name, rel in keys.items():
        data = _load_json(rel) or {}
        out[name] = data.get("decision")
    return out


def _smoke_be_modes(*, workers: int) -> dict[str, Any]:
    """LOOKUP · OOD · BE-FOREVER FP · over-refuse · util via BE ask path."""
    from run_be_real_eval import _ask_row

    items = [dict(p) for p in BE0_ASK_BATTERY if p["id"] in _SMOKE_IDS]

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
        "decision": "PROMOTE" if ok else "KILL (BE forever/modes smoke)",
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
                f"# {title} — placeholder (pending BE8)",
                "",
                "> Written by BE7 report so paper-lab links resolve. "
                "BE8 replaces this with the formal freeze.",
                "",
                f"Ship claim: **{SHIP_CLAIM}**",
                "",
                "Do not invent Wave BF without lab-book reopen.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _ensure_freeze_stubs() -> None:
    _write_stub(_FREEZE_STUB, "BE-FREEZE")
    _write_stub(_FORMAL_FREEZE_STUB, "formal-habefreeze-be-freeze")


def _write_public() -> None:
    _SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    _ensure_freeze_stubs()
    _SUMMARY.write_text(render_wave_be_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_be(), encoding="utf-8")


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
            f"# Wave BE session checklist (**OPEN** · BE7 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md`.  ",
            "> Ship lock: **"
            + SHIP_CLAIM
            + "** · ≤5M (no TAC / true-continue unlock).",
            "",
            "## Current stage",
            "",
            f"**BE7 — BE-REPORT ({status})** · Next: **BE8 BE-FREEZE**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **BE OPEN** (RESEARCH_COMPLETE pending FREEZE) |",
            f"| Decision | **{decision}** |",
            "| Public | `docs/results/nano-lm/wave-be-summary.md` |",
            "| Paper-lab | `docs/results/nano-lm/paper-lab-wave-be.md` |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| BE0 | SESSION | **DONE — PROMOTE** |",
            "| BE1 | H-COMPINT | **DONE — PROMOTE** |",
            "| BE2 | H-SHIPUSE | **DONE — PROMOTE** |",
            "| BE3 | H-FASTBE | **DONE — PROMOTE** |",
            "| BE4 | H-CTXBE | **DONE — PROMOTE** |",
            "| BE5 | H-NANOGEN15 | **DONE — DEFER** |",
            "| BE6 | BE-REAL-EVAL | **DONE — PROMOTE** |",
            f"| BE7 | BE-REPORT | **{status}** |",
            "| BE8 | BE-FREEZE | **NEXT** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_local_helpers(status: str) -> None:
    _LOCAL_IMPL.write_text(
        f"""# Implementation plan — nano generative LM

> Private. Lab: [`pesquisa.md`](pesquisa.md).

## Status

**BE0–BE4 PROMOTE · BE5 DEFER · BE6–BE7 DONE — {status}**. Next: **BE8 BE-FREEZE**.

```bash
npm run nano:be:report
npm run nano:test && npm run verify
```
""",
        encoding="utf-8",
    )
    _LOCAL_README.write_text(
        f"""# Local research notebook

Full lab book: **`pesquisa.md`**.

**Wave BE ACTIVE** — BE7 **BE-REPORT {status}** (gen locked · util cited).

Next: **BE8 BE-FREEZE**.
""",
        encoding="utf-8",
    )


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    status = _status_word(decision)
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    text2, n = re.subn(
        r"\| BE7 \| \*\*BE-REPORT\*\* \|[^\n]+\| \*\*NEXT\*\* \|",
        (
            "| BE7 | **BE-REPORT** | Summary + paper-lab "
            "(+ arXiv-ready if lift) | "
            "anti-FP · util · HOLD/DEFER cited | "
            f"**DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"(\| BE8 \| \*\*BE-FREEZE\*\* \|[^\n]+\| )\*\*TODO\*\* \|",
        r"\1**NEXT** |",
        text,
        count=1,
    )
    if n:
        text = text2
    else:
        text2, n = re.subn(
            r"(\| BE8 \| \*\*BE-FREEZE\*\* \|[^\n]+\| )pending \|",
            r"\1**NEXT** |",
            text,
            count=1,
        )
        if n:
            text = text2
    text = text.replace(
        (
            "8. **BE7 BE-REPORT** — **NEXT** — summary + paper-lab; "
            "arXiv path if measured lift.  \n"
            "9. **BE8 BE-FREEZE** — lock; do not invent Wave BF.  "
        ),
        (
            f"8. **BE7 BE-REPORT** — **DONE {status}** "
            "(`npm run nano:be:report`) · next BE8 freeze.  \n"
            "9. **BE8 BE-FREEZE** — **NEXT** — lock; do not invent Wave BF.  "
        ),
        1,
    )
    text = text.replace(
        "> **Session:** `.local/wave-be/SESSION.md` "
        "(BE6 BE-REAL-EVAL **DONE — PROMOTE**; next BE7 BE-REPORT).  ",
        "> **Session:** `.local/wave-be/SESSION.md` "
        f"(BE7 BE-REPORT **DONE — {status}**; next BE8 BE-FREEZE).  ",
        1,
    )
    text = text.replace(
        "(BE6 BE-REAL-EVAL **DONE — PROMOTE**; next BE7 BE-REPORT)",
        f"(BE7 BE-REPORT **DONE — {status}**; next BE8 BE-FREEZE)",
        1,
    )
    if "# next: nano:be:report" in text:
        text = text.replace(
            "# next: nano:be:report\n# npm run nano:be:report\n",
            "npm run nano:be:report\n# next: nano:be:freeze\n",
            1,
        )
        if "# next: nano:be:report" in text:
            text = text.replace(
                "# next: nano:be:report\n",
                "npm run nano:be:report\n# next: nano:be:freeze\n",
                1,
            )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")
    _patch_local_helpers(status)


def _be_active_line(status: str) -> str:
    return (
        "BE0 [SESSION PROMOTE](wave-be-session.md) · "
        "BE1 [H-COMPINT PROMOTE](formal-hcompint-compint.md) · "
        "BE2 [H-SHIPUSE PROMOTE](formal-hshipuse-shipuse.md) · "
        "BE3 [H-FASTBE PROMOTE](formal-hfastbe-fastbe.md) · "
        "BE4 [H-CTXBE PROMOTE](formal-hctxbe-ctxbe.md) · "
        "BE5 [H-NANOGEN15 DEFER](formal-hnanogen15-nanogen15.md) · "
        "BE6 [BE-REAL-EVAL PROMOTE](wave-be-real-eval.md) · "
        f"BE7 [BE-REPORT {status}](wave-be-summary.md) "
        "(`npm run nano:be:report`) · [paper-lab-wave-be.md]"
        "(paper-lab-wave-be.md); next BE8 BE-FREEZE; ship remains "
        "**AF + AQ + AS trust + STRICT ablated DECODE**; ≤5M stays"
    )


def _patch_recipes(status: str) -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    line = f"**Wave BE ACTIVE:** {_be_active_line(status)}."
    text2, n = re.subn(
        r"\*\*Wave BE ACTIVE:\*\*[^\n]*",
        line,
        text,
        count=1,
    )
    if n:
        text = text2
    if "Wave BE7 BE-REPORT" not in text:
        row = (
            "| Wave BE7 BE-REPORT | [wave-be-summary.md]"
            "(wave-be-summary.md) · [paper-lab-wave-be.md]"
            "(paper-lab-wave-be.md) **PROMOTE** "
            "(`npm run nano:be:report`) — anti-FP · util · BE5 DEFER · "
            "NANOGEN6/7 HOLD · NANOGEN8…15 DEFER cited |\n"
        )
        if "| Wave BE6 BE-REAL-EVAL |" in text:
            text2, n2 = re.subn(
                r"(\| Wave BE6 BE-REAL-EVAL \|[^\n]+\|\n)",
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
    line = f"**Wave BE ACTIVE** — {_be_active_line(status)}."
    text2, n = re.subn(
        r"\*\*Wave BE ACTIVE\*\* —[^\n]*",
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
        "- **Wave BE ACTIVE** — BE0 [SESSION PROMOTE]"
        "(docs/results/nano-lm/wave-be-session.md) "
        "(`npm run nano:be:session`) · BE1 [H-COMPINT PROMOTE]"
        "(docs/results/nano-lm/formal-hcompint-compint.md) "
        "(`npm run nano:compint`) · BE2 [H-SHIPUSE PROMOTE]"
        "(docs/results/nano-lm/formal-hshipuse-shipuse.md) "
        "(`npm run nano:shipuse`) · BE3 [H-FASTBE PROMOTE]"
        "(docs/results/nano-lm/formal-hfastbe-fastbe.md) "
        "(`npm run nano:fastbe`) · BE4 [H-CTXBE PROMOTE]"
        "(docs/results/nano-lm/formal-hctxbe-ctxbe.md) "
        "(`npm run nano:ctxbe`) · BE5 [H-NANOGEN15 DEFER]"
        "(docs/results/nano-lm/formal-hnanogen15-nanogen15.md) "
        "(`npm run nano:nanogen15`) · BE6 [BE-REAL-EVAL PROMOTE]"
        "(docs/results/nano-lm/wave-be-real-eval.md) "
        "(`npm run nano:be:real-eval`) · "
        f"BE7 [BE-REPORT {status}]"
        "(docs/results/nano-lm/wave-be-summary.md) "
        "(`npm run nano:be:report`) · "
        "[paper-lab-wave-be.md](docs/results/nano-lm/paper-lab-wave-be.md); "
        "next BE8 BE-FREEZE; ship remains "
        "**AF + AQ + AS trust + STRICT ablated DECODE**; NANOGEN6·7 HOLD · "
        "NANOGEN8…15 DEFER; ≤5M stays."
    )
    text2, n = re.subn(
        r"- \*\*Wave BE ACTIVE\*\* —[^\n]+", agents, text, count=1
    )
    if n:
        _AGENTS.write_text(text2, encoding="utf-8")


def _patch_agenda(status: str) -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    row = (
        f"| **BE** | **ACTIVE** | BE0–BE4 PROMOTE · BE5 DEFER · BE6 "
        f"BE-REAL-EVAL PROMOTE · BE7 BE-REPORT {status} "
        f"(`npm run nano:be:report`); next BE8 BE-FREEZE; ≤5M |"
    )
    text2, n = re.subn(
        r"\| \*\*BE\*\* \| \*\*ACTIVE\*\* \|[^\n]+", row, text, count=1
    )
    if n:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen(status: str) -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    text = text.replace(
        (
            "Wave BE ACTIVE (BE0–BE4 PROMOTE · BE5 DEFER · "
            "BE6 BE-REAL-EVAL PROMOTE; next BE7 BE-REPORT)"
        ),
        (
            f"Wave BE ACTIVE (BE0–BE4 PROMOTE · BE5 DEFER · "
            f"BE6 BE-REAL-EVAL PROMOTE · BE7 BE-REPORT {status}; "
            f"next BE8 BE-FREEZE)"
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
        return "KILL (BE forever/modes smoke failed)"
    if decision.startswith("PROMOTE") and not markers:
        return "KILL (wave-be-summary missing thesis markers)"
    if decision.startswith("PROMOTE") and not board:
        return "KILL (wave-be-summary missing scoreboard)"
    if decision.startswith("PROMOTE") and not antifp:
        return "KILL (wave-be-summary missing anti-FP evidence)"
    if decision.startswith("PROMOTE") and not realeval:
        return "KILL (wave-be-summary missing real-eval section)"
    return decision


def run_be_report(
    *, out: Path, skip_ask: bool = False, workers: int = 6
) -> dict[str, Any]:
    """
    GIVEN BE0–BE6 evidence
    WHEN writing public summary + paper-lab and checking anti-FP/mode smoke
    THEN PROMOTE iff evidence ∧ markers ∧ scoreboard ∧ antifp ∧ realeval ∧ smoke.
    """
    _write_public()
    evidence = _evidence_map()
    decision = decide_be_report(evidence)
    report_text = _SUMMARY.read_text(encoding="utf-8")
    markers = report_markers_ok(report_text)
    board = scoreboard_ok(report_text)
    antifp = antifp_section_ok(report_text)
    realeval = realeval_section_ok(report_text)
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_be_modes(workers=workers)
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
        "id": BE_ID,
        "hyp_id": BE_ID,
        "stage": "BE7",
        "thesis": BE_THESIS,
        "decision": final,
        "markers_ok": markers,
        "scoreboard_ok": board,
        "antifp_ok": antifp,
        "realeval_ok": realeval,
        "scoreboard": list(BE_SCOREBOARD),
        "evidence": evidence,
        "stage_facts": _stage_facts(),
        "ask_smoke": ask,
        "public_report": "docs/results/nano-lm/wave-be-summary.md",
        "paper_lab": "docs/results/nano-lm/paper-lab-wave-be.md",
        "wave_status": "RESEARCH_COMPLETE" if ok else "OPEN",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "workers": int(workers),
        "finding": (
            f"{BE_ID}: decision={final}; "
            f"markers={markers}; scoreboard={board}; "
            f"antifp={antifp}; realeval={realeval}."
        ),
        "next": "BE8 BE-FREEZE",
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave BE7 BE-REPORT")
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        summary = run_be_report(
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
                "hyp_id": BE_ID,
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
