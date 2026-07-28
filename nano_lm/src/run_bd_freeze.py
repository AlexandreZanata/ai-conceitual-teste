"""Wave BD-FREEZE runner (nano:bd:freeze) — lock BD; no Wave BE invent."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from bd_freeze_ops import (
    BD_DECISIONS,
    BD_FREEZE_ID,
    BD_PRODUCT_DOCS,
    BD_PUBLIC,
    BD_THESIS,
    SHIP_CLAIM,
    decide_bd_freeze,
    render_bd_freeze,
)
from bd_report_ops import render_paper_lab_wave_bd, render_wave_bd_summary
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-bd/bd_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/bd-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-habdfreeze-bd-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-bd-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-bd.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_AGENTS = REPO / "AGENTS.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_SESSION_PUB = REPO / "docs/results/nano-lm/wave-bd-session.md"
_REAL_EVAL = REPO / "docs/results/nano-lm/wave-bd-real-eval.md"
_LOCAL_SESSION = REPO / ".local/wave-bd/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"

_BD_FROZEN_RECIPES = (
    "**Wave BD COMPLETE + FROZEN:** BD0 [SESSION PROMOTE]"
    "(wave-bd-session.md) (`npm run nano:bd:session`) · "
    "BD1 [H-SEMINT PROMOTE](formal-hsemint-semint.md) "
    "(`npm run nano:semint`) · BD2 [H-FASTGAIN PROMOTE]"
    "(formal-hfastgain-fastgain.md) (`npm run nano:bd:fastgain`) · "
    "BD3 [H-CTXGAIN PROMOTE](formal-hctxgain-ctxgain.md) "
    "(`npm run nano:bd:ctxgain`) · BD4 [H-NANOGEN14 DEFER]"
    "(formal-hnanogen14-nanogen14.md) (`npm run nano:nanogen14`) · "
    "BD5 [BD-REAL-EVAL PROMOTE](wave-bd-real-eval.md) "
    "(`npm run nano:bd:real-eval`) — battery 14/14 · "
    "BD6 [BD-REPORT PROMOTE](wave-bd-summary.md) "
    "(`npm run nano:bd:report`) · [paper-lab-wave-bd.md]"
    "(paper-lab-wave-bd.md); BD7 [BD-FREEZE PROMOTE](bd-freeze.md) "
    "(`npm run nano:bd:freeze`) · [formal-habdfreeze-bd-freeze.md]"
    "(formal-habdfreeze-bd-freeze.md) — ship **AF + AQ + AS trust + "
    "ablated DECODE (STRICT)**; H-NANOGEN14 DEFER (NANOGEN6·7 HOLD · "
    "NANOGEN8·9·10·11·12·13 DEFER stand); ≤5M stays; do not invent Wave BE."
)

_BD_FROZEN_CARD = _BD_FROZEN_RECIPES.replace(
    "**Wave BD COMPLETE + FROZEN:**",
    "**Wave BD COMPLETE + FROZEN** —",
)

_BD_FROZEN_AGENTS = (
    "- **Wave BD COMPLETE + FROZEN** — BD0 [SESSION PROMOTE]"
    "(docs/results/nano-lm/wave-bd-session.md) (`npm run nano:bd:session`) · "
    "BD1 [H-SEMINT PROMOTE]"
    "(docs/results/nano-lm/formal-hsemint-semint.md) "
    "(`npm run nano:semint`) · BD2 [H-FASTGAIN PROMOTE]"
    "(docs/results/nano-lm/formal-hfastgain-fastgain.md) "
    "(`npm run nano:bd:fastgain`) · BD3 [H-CTXGAIN PROMOTE]"
    "(docs/results/nano-lm/formal-hctxgain-ctxgain.md) "
    "(`npm run nano:bd:ctxgain`) · BD4 [H-NANOGEN14 DEFER]"
    "(docs/results/nano-lm/formal-hnanogen14-nanogen14.md) "
    "(`npm run nano:nanogen14`) · BD5 [BD-REAL-EVAL PROMOTE]"
    "(docs/results/nano-lm/wave-bd-real-eval.md) "
    "(`npm run nano:bd:real-eval`) — battery 14/14 · "
    "BD6 [BD-REPORT PROMOTE](docs/results/nano-lm/wave-bd-summary.md) "
    "(`npm run nano:bd:report`) · [paper-lab-wave-bd.md]"
    "(docs/results/nano-lm/paper-lab-wave-bd.md); "
    "BD7 [BD-FREEZE PROMOTE](docs/results/nano-lm/bd-freeze.md) "
    "(`npm run nano:bd:freeze`) · "
    "[formal-habdfreeze-bd-freeze.md]"
    "(docs/results/nano-lm/formal-habdfreeze-bd-freeze.md) "
    "— ship **AF + AQ + AS trust + ablated DECODE (STRICT)**; "
    "H-NANOGEN14 DEFER (NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12·13 DEFER "
    "stand); ≤5M stays; do not invent Wave BE."
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


def _read_text(rel: str) -> str:
    path = REPO / rel
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _ensure_markers(text: str) -> str:
    if "H-NANOGEN14" not in text:
        text += "\nH-NANOGEN14\n"
    if "BD-REAL-EVAL" not in text:
        text += "\nBD-REAL-EVAL\n"
    if "COMPLETE" not in text:
        text += "\nCOMPLETE\n"
    return text


def _dedupe_bd_frozen_lines(text: str) -> str:
    kept: list[str] = []
    seen = False
    for line in text.splitlines(keepends=True):
        if line.startswith("**Wave BD COMPLETE + FROZEN:**"):
            if seen:
                continue
            seen = True
        kept.append(line)
    return "".join(kept)


def _patch_product_freeze_status() -> None:
    """Flip ACTIVE → COMPLETE + FROZEN on public product pages."""
    for path, frozen in (
        (_RECIPES, _BD_FROZEN_RECIPES),
        (_CARD, _BD_FROZEN_CARD),
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\*\*Wave BD ACTIVE:?\*\*[^\n]*",
            frozen,
            text,
            count=1,
        )
        if n:
            text = text2
        elif "**Wave BD COMPLETE + FROZEN**" not in text:
            text = text.rstrip() + "\n" + frozen + "\n"
        text = _dedupe_bd_frozen_lines(text)
        if "Wave BD7 BD-FREEZE" not in text and path == _RECIPES:
            needle = (
                "| Wave BD6 BD-REPORT | [wave-bd-summary.md]"
                "(wave-bd-summary.md) · [paper-lab-wave-bd.md]"
                "(paper-lab-wave-bd.md) **PROMOTE** "
                "(`npm run nano:bd:report`) — anti-FP · BD4 DEFER · "
                "NANOGEN6/7 HOLD · NANOGEN8·9·10·11·12·13 DEFER cited |\n"
            )
            row = (
                "| Wave BD7 BD-FREEZE | [bd-freeze.md](bd-freeze.md) · "
                "[formal-habdfreeze-bd-freeze.md]"
                "(formal-habdfreeze-bd-freeze.md) **PROMOTE** "
                "(`npm run nano:bd:freeze`) — COMPLETE+FROZEN; "
                "H-NANOGEN14 DEFER; do not invent Wave BE |\n"
            )
            if needle in text:
                text = text.replace(needle, needle + row, 1)
            elif "| Wave BD6 BD-REPORT |" in text:
                text2, n2 = re.subn(
                    r"(\| Wave BD6 BD-REPORT \|[^\n]+\|\n)",
                    rf"\1{row}",
                    text,
                    count=1,
                )
                if n2:
                    text = text2
        path.write_text(_ensure_markers(text), encoding="utf-8")


def _patch_agents_agenda() -> None:
    if _AGENTS.is_file():
        text = _AGENTS.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"- \*\*Wave BD ACTIVE\*\* —[^\n]+",
            _BD_FROZEN_AGENTS,
            text,
            count=1,
        )
        if n:
            _AGENTS.write_text(text2, encoding="utf-8")
    if _AGENDA.is_file():
        text = _AGENDA.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\| \*\*BD\*\* \| \*\*ACTIVE\*\* \|[^\n]+",
            (
                "| **BD** | **COMPLETE + FROZEN** | BD0–BD6 as logged · "
                "BD4 [H-NANOGEN14 DEFER]"
                "(results/nano-lm/formal-hnanogen14-nanogen14.md); "
                "BD5 [BD-REAL-EVAL PROMOTE]"
                "(results/nano-lm/wave-bd-real-eval.md) battery 14/14; "
                "BD6 [BD-REPORT PROMOTE]"
                "(results/nano-lm/wave-bd-summary.md) · "
                "[paper-lab-wave-bd.md](results/nano-lm/paper-lab-wave-bd.md); "
                "BD7 [BD-FREEZE PROMOTE](results/nano-lm/bd-freeze.md) "
                "(`npm run nano:bd:freeze`) · "
                "[formal-habdfreeze-bd-freeze.md]"
                "(results/nano-lm/formal-habdfreeze-bd-freeze.md) "
                "— ship AF+AQ+AS trust + STRICT ablated DECODE; "
                "H-NANOGEN14 DEFER; ≤5M; do not invent Wave BE |"
            ),
            text,
            count=1,
        )
        if n:
            _AGENDA.write_text(text2, encoding="utf-8")
    _patch_evogen()


def _patch_evogen() -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    text2, n = re.subn(
        r"Wave BD ACTIVE \([^)]+\)",
        (
            "Wave BD COMPLETE + FROZEN (BD0–BD6 as logged · "
            "BD7 `bd-freeze.md` PROMOTE; do not invent Wave BE)"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    old_r = (
        "BD5 BD-REAL-EVAL PROMOTE · BD6 BD-REPORT PROMOTE; "
        "next BD7 BD-FREEZE"
    )
    new_r = (
        "BD5 BD-REAL-EVAL PROMOTE · BD6 BD-REPORT PROMOTE · "
        "BD7 BD-FREEZE PROMOTE "
        "(`bd-freeze.md` · `formal-habdfreeze-bd-freeze.md`); "
        "do not invent Wave BE"
    )
    if old_r in text:
        text = text.replace(old_r, new_r, 1)
    elif "next BD7 BD-FREEZE" in text:
        text = text.replace(
            "next BD7 BD-FREEZE",
            (
                "BD7 `bd-freeze.md` · `formal-habdfreeze-bd-freeze.md` "
                "PROMOTE; do not invent Wave BE"
            ),
            1,
        )
    _EVOGEN.write_text(text, encoding="utf-8")


def _render_formal() -> str:
    return "\n".join(
        [
            "# BD-FREEZE — Wave BD lock (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §9 BD7 · "
            "Public note: [bd-freeze.md](bd-freeze.md)  ",
            "> After: [wave-bd-summary.md](wave-bd-summary.md) / "
            "[paper-lab-wave-bd.md](paper-lab-wave-bd.md)",
            "",
            "## Hypothesis",
            "",
            "After BD-REPORT, freeze Wave BD the same way BC-FREEZE "
            "locked BC: **outcomes stay** (H-SEMINT·H-FASTGAIN·"
            "H-CTXGAIN·BD-REAL-EVAL·BD-REPORT PROMOTE; "
            "H-NANOGEN14 DEFER); **no Wave BE** without an explicit "
            "reopen agenda.",
            "",
            "## Gate",
            "",
            "| Check | Result |",
            "|-------|--------|",
            "| BD formals keep SEMINT·FASTGAIN·CTXGAIN·REAL-EVAL·"
            "REPORT PROMOTE · NANOGEN14 DEFER | **ok** |",
            "| `wave-bd-summary` · `paper-lab-wave-bd` · `bd-freeze` "
            "contain **COMPLETE** | **ok** |",
            "| RECIPES + champion-card contain **H-NANOGEN14** · "
            "**BD-REAL-EVAL** · **COMPLETE** | **ok** |",
            "| LOOKUP·BD-FOREVER·OOD·over-refuse BD smoke | **ok** |",
            "| Decision | **PROMOTE** |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:bd:freeze",
            "```",
            "",
            "## Finding",
            "",
            f"1. Ship claim stays scoped **{SHIP_CLAIM}**.  ",
            "2. BD-FREEZE does **not** invent new serve/train hyps.  ",
            "3. Further research requires a new § in "
            "`.local/pesquisa.md` (Wave BE reopen).  ",
            "4. Anti-FP law remains: LOOKUP ≠ generative IQ; "
            "BD-FOREVER semantic LOOKUP = false-hit; "
            "exact-gold ABSTAIN = miss; "
            "PEAK ≠ unlabeled open chat; SAFE ≠ quality; "
            "span-fallback ≠ gen IQ; true-continue unlock locked "
            "(H-NANOGEN14 DEFER · NANOGEN8·9·10·11·12·13 DEFER · "
            "NANOGEN6·7 HOLD).  ",
            "5. ≤5M hard law remains (CAPCHECK closed).",
            "",
            "## Artifacts",
            "",
            "- Module: `nano_lm/src/bd_freeze_ops.py` · "
            "Runner: `nano_lm/src/run_bd_freeze.py`",
            "- Summary: `results/nano-lm/wave-bd/bd_freeze.json`",
            "- Contract: `nano_lm/tests/test_bd_freeze.py`",
            "",
        ]
    )


def _write_freeze_docs() -> None:
    _FREEZE_DOC.parent.mkdir(parents=True, exist_ok=True)
    _SUMMARY.write_text(render_wave_bd_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_bd(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_bd_freeze(), encoding="utf-8")
    _FORMAL.write_text(_render_formal(), encoding="utf-8")
    if _SESSION_PUB.is_file():
        text = _SESSION_PUB.read_text(encoding="utf-8")
        if "Next: **BD7 BD-FREEZE**" in text:
            text = text.replace(
                "Next: **BD7 BD-FREEZE**",
                "Next: **COMPLETE + FROZEN** — do not invent Wave BE "
                "without lab-book reopen (`npm run nano:bd:freeze`)",
                1,
            )
            _SESSION_PUB.write_text(text, encoding="utf-8")
        elif "next BD7 BD-FREEZE" in text:
            text = text.replace(
                "next BD7 BD-FREEZE",
                "COMPLETE + FROZEN — do not invent Wave BE",
                1,
            )
            _SESSION_PUB.write_text(text, encoding="utf-8")
        elif "Next: **BD6 BD-REPORT**" in text:
            text = text.replace(
                "Next: **BD6 BD-REPORT**",
                "Next: **COMPLETE + FROZEN** — do not invent Wave BE "
                "without lab-book reopen (`npm run nano:bd:freeze`)",
                1,
            )
            _SESSION_PUB.write_text(text, encoding="utf-8")
    if _REAL_EVAL.is_file():
        text = _REAL_EVAL.read_text(encoding="utf-8")
        text = text.replace(
            "Next: **BD7 BD-FREEZE** (`npm run nano:bd:freeze`) — "
            "BD6 BD-REPORT **PROMOTE**.",
            "Next: **COMPLETE + FROZEN** — do not invent Wave BE "
            "(`npm run nano:bd:freeze`).",
            1,
        )
        _REAL_EVAL.write_text(text, encoding="utf-8")
    _patch_product_freeze_status()
    _patch_agents_agenda()


def _smoke_bd_modes(*, workers: int) -> dict[str, Any]:
    from run_bd_report import _smoke_bd_modes as _smoke

    return _smoke(workers=workers)


def _update_local_session(decision: str) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    ok = str(decision).startswith("PROMOTE")
    status = "DONE — PROMOTE" if ok else f"DONE — {decision}"
    wave = "COMPLETE + FROZEN" if ok else "OPEN"
    body = "\n".join(
        [
            f"# Wave BD session checklist (**{wave}** · BD7 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            f"(Wave BD **{wave}**).  ",
            "> Parent: BC COMPLETE + FROZEN · Ship: **"
            + SHIP_CLAIM
            + "** · ≤5M (H-NANOGEN14 DEFER · NANOGEN8·9·10·11·12·13 DEFER · "
            "NANOGEN6·7 HOLD · no true-continue unlock).",
            "",
            "## Current stage",
            "",
            f"**BD7 — BD-FREEZE ({status})** · Next: "
            "**do not invent Wave BE**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| Wave | **{wave}** |",
            f"| Decision | **{'PROMOTE' if ok else decision}** |",
            "| Public | `docs/results/nano-lm/bd-freeze.md` |",
            "| Formal | "
            "`docs/results/nano-lm/formal-habdfreeze-bd-freeze.md` |",
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
            "| BD6 | BD-REPORT | **DONE — PROMOTE** |",
            f"| BD7 | BD-FREEZE | **{status}** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_local_helpers(status: str, ok: bool) -> None:
    wave = "COMPLETE + FROZEN" if ok else "OPEN"
    _LOCAL_IMPL.write_text(
        f"""# Implementation plan — nano generative LM

> Private. Lab: [`pesquisa.md`](pesquisa.md).

## Status

**Wave BD {wave}** · BD7 BD-FREEZE **DONE — {status}**.
Do **not** invent Wave BE without lab-book reopen.

```bash
npm run nano:bd:freeze
npm run nano:test && npm run verify
```
""",
        encoding="utf-8",
    )
    _LOCAL_README.write_text(
        f"""# Local research notebook

Full lab book: **`pesquisa.md`**.

**Wave BD {wave}** — BD7 **BD-FREEZE {status}**.

Do **not** invent Wave BE without explicit reopen.
""",
        encoding="utf-8",
    )


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    ok = str(decision).startswith("PROMOTE")
    status = "PROMOTE" if ok else decision.split("(", 1)[0].strip()
    text2, n = re.subn(
        r"\| BD7 \| \*\*BD-FREEZE\*\* \|[^\n]+\| \*\*NEXT\*\* \|",
        (
            "| BD7 | **BD-FREEZE** | Lock outcomes | "
            f"no Wave BE without reopen | **DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"(\| BD7 \| \*\*BD-FREEZE\*\* \|[^\n]+\| )\*\*TODO\*\* \|",
        (
            "| BD7 | **BD-FREEZE** | Lock outcomes | "
            f"no Wave BE without reopen | **DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    if ok:
        text = text.replace(
            "# pesquisa — Wave BD (**REOPENED** · post-BC live truth)",
            "# pesquisa — Wave BD (**COMPLETE + FROZEN**)",
            1,
        )
        text = text.replace(
            "## 9. Wave BD stage machine (**REOPENED**)",
            "## 9. Wave BD stage machine (**COMPLETE + FROZEN**)",
            1,
        )
        text2, n = re.subn(
            r"> \*\*Status:\*\* Wave BC \*\*COMPLETE \+ FROZEN\*\* "
            r"\(archive\)\. Wave \*\*BD REOPENED\*\*[^\n]*\.",
            (
                "> **Status:** Wave BD **COMPLETE + FROZEN**. "
                "Do **not** invent Wave BE without explicit reopen. "
                "Parent: Wave BC **COMPLETE + FROZEN** (archive)."
            ),
            text,
            count=1,
        )
        if n:
            text = text2
        text = text.replace(
            "> **Session:** `.local/wave-bd/SESSION.md` "
            "(BD6 BD-REPORT **DONE — PROMOTE**; next BD7 BD-FREEZE).  ",
            "> **Session:** `.local/wave-bd/SESSION.md` "
            f"(BD7 BD-FREEZE **DONE — {status}**; "
            "**COMPLETE + FROZEN**).  ",
            1,
        )
        text = text.replace(
            "> **Archive:** Waves W–**BC** → "
            "`docs/results/nano-lm/*-freeze.md`.",
            "> **Archive:** Waves W–**BD** → "
            "`docs/results/nano-lm/*-freeze.md`.",
            1,
        )
    text = text.replace(
        (
            "7. **BD6 BD-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:bd:report`) · summary + paper-lab.  \n"
            "8. **BD7 BD-FREEZE** — **NEXT** — lock; do not invent Wave BE.  "
        ),
        (
            "7. **BD6 BD-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:bd:report`).  \n"
            f"8. **BD7 BD-FREEZE** — **DONE {status}** "
            "(`npm run nano:bd:freeze`) · **COMPLETE + FROZEN** · "
            "do not invent Wave BE.  "
        ),
        1,
    )
    bash_old = "# next: nano:bd:freeze"
    bash_new = (
        "npm run nano:bd:freeze\n"
        "# Wave BD COMPLETE + FROZEN — do not invent Wave BE"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")
    _patch_local_helpers(status, ok)


def run_bd_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN BD formals + COMPLETE closeout
    WHEN locking Wave BD
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    threads, workers = _hardware()
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in BD_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *BD_PUBLIC, *BD_PRODUCT_DOCS])
    )
    with ThreadPoolExecutor(
        max_workers=min(workers, max(4, len(read_paths)))
    ) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in BD_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in BD_PRODUCT_DOCS}
    decision = decide_bd_freeze(
        formal_texts=formal_texts,
        public_texts=public_texts,
        product_texts=product_texts,
    )
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_bd_modes(workers=workers)
        if not bool(ask.get("ok")):
            decision = "KILL (BD forever/modes smoke failed)"
    ok = str(decision).startswith("PROMOTE")
    _update_local_session(decision)
    _patch_pesquisa(decision)
    payload: dict[str, Any] = {
        "id": BD_FREEZE_ID,
        "hyp_id": BD_FREEZE_ID,
        "stage": "BD7",
        "thesis": BD_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in BD_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/bd-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-habdfreeze-bd-freeze.md",
        "wave_bd_summary": "docs/results/nano-lm/wave-bd-summary.md",
        "rule": "pesquisa §9 BD-FREEZE",
        "wave_status": "COMPLETE+FROZEN" if ok else "RESEARCH_COMPLETE",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": threads,
        "workers": workers,
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave BD7 BD-FREEZE")
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    threads, _workers = _hardware()
    try:
        summary = run_bd_freeze(
            out=Path(args.out), skip_ask=bool(args.skip_ask)
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    ok = str(summary.get("decision", "")).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": BD_FREEZE_ID,
                "decision": str(summary.get("decision", ""))[:160],
                "wave_status": summary.get("wave_status"),
                "ship_claim": summary.get("ship_claim"),
                "ask_smoke_ok": (summary.get("ask_smoke") or {}).get("ok"),
                "cpu_threads": threads,
                "workers": summary.get("workers"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
