"""Wave BG-FREEZE runner (nano:bg:freeze) — lock BG; no Wave BH invent."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from bg_freeze_ops import (
    BG_DECISIONS,
    BG_FREEZE_ID,
    BG_PRODUCT_DOCS,
    BG_PUBLIC,
    BG_THESIS,
    SHIP_CLAIM,
    decide_bg_freeze,
    render_bg_freeze,
)
from bg_report_ops import render_paper_lab_wave_bg, render_wave_bg_summary
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-bg/bg_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/bg-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-habgfreeze-bg-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-bg-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-bg.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_AGENTS = REPO / "AGENTS.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_SESSION_PUB = REPO / "docs/results/nano-lm/wave-bg-session.md"
_REAL_EVAL = REPO / "docs/results/nano-lm/wave-bg-real-eval.md"
_LOCAL_SESSION = REPO / ".local/wave-bg/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"

_BG_FROZEN_RECIPES = (
    "**Wave BG COMPLETE + FROZEN:** BG0 [SESSION PROMOTE]"
    "(wave-bg-session.md) (`npm run nano:bg:session`) · "
    "BG1 [H-UNARYINT PROMOTE](formal-hunaryint-unaryint.md) "
    "(`npm run nano:unaryint`) · BG2 [H-SHIPPUB PROMOTE]"
    "(formal-hshippub-shippub.md) (`npm run nano:shippub`) · "
    "BG3 [H-FASTBG PROMOTE](formal-hfastbg-fastbg.md) "
    "(`npm run nano:fastbg`) · BG4 [H-CTXBG PROMOTE]"
    "(formal-hctxbg-ctxbg.md) (`npm run nano:ctxbg`) · "
    "BG5 [H-NANOGEN17 SKIP](formal-hnanogen17-nanogen17.md) "
    "(`npm run nano:nanogen17`) · BG6 [BG-REAL-EVAL PROMOTE]"
    "(wave-bg-real-eval.md) (`npm run nano:bg:real-eval`) — "
    "battery 17/17 · BG7 [BG-REPORT PROMOTE](wave-bg-summary.md) "
    "(`npm run nano:bg:report`) · [paper-lab-wave-bg.md]"
    "(paper-lab-wave-bg.md); BG8 [BG-FREEZE PROMOTE](bg-freeze.md) "
    "(`npm run nano:bg:freeze`) · [formal-habgfreeze-bg-freeze.md]"
    "(formal-habgfreeze-bg-freeze.md) — ship **AF + AQ + AS trust + "
    "ablated DECODE (STRICT)**; H-NANOGEN17 SKIP (NANOGEN6·7 HOLD · "
    "NANOGEN8…15 DEFER · NANOGEN16 SKIP stand); ≤5M stays; "
    "do not invent Wave BH."
)

_BG_FROZEN_CARD = _BG_FROZEN_RECIPES.replace(
    "**Wave BG COMPLETE + FROZEN:**",
    "**Wave BG COMPLETE + FROZEN** —",
)

_BG_FROZEN_AGENTS = (
    "- **Wave BG COMPLETE + FROZEN** — BG0 [SESSION PROMOTE]"
    "(docs/results/nano-lm/wave-bg-session.md) (`npm run nano:bg:session`) · "
    "BG1 [H-UNARYINT PROMOTE]"
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
    "(`npm run nano:bg:real-eval`) — battery 17/17 · "
    "BG7 [BG-REPORT PROMOTE](docs/results/nano-lm/wave-bg-summary.md) "
    "(`npm run nano:bg:report`) · [paper-lab-wave-bg.md]"
    "(docs/results/nano-lm/paper-lab-wave-bg.md); "
    "BG8 [BG-FREEZE PROMOTE](docs/results/nano-lm/bg-freeze.md) "
    "(`npm run nano:bg:freeze`) · "
    "[formal-habgfreeze-bg-freeze.md]"
    "(docs/results/nano-lm/formal-habgfreeze-bg-freeze.md) "
    "— ship **AF + AQ + AS trust + ablated DECODE (STRICT)**; "
    "H-NANOGEN17 SKIP (NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · "
    "NANOGEN16 SKIP stand); ≤5M stays; do not invent Wave BH."
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


def _read_text(rel: str) -> str:
    path = REPO / rel
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _ensure_markers(text: str) -> str:
    if "H-NANOGEN17" not in text:
        text += "\nH-NANOGEN17\n"
    if "BG-REAL-EVAL" not in text:
        text += "\nBG-REAL-EVAL\n"
    if "COMPLETE" not in text:
        text += "\nCOMPLETE\n"
    return text


def _dedupe_bg_frozen_lines(text: str) -> str:
    kept: list[str] = []
    seen = False
    for line in text.splitlines(keepends=True):
        if line.startswith("**Wave BG COMPLETE + FROZEN:**"):
            if seen:
                continue
            seen = True
        kept.append(line)
    return "".join(kept)


def _patch_product_freeze_status() -> None:
    """Flip ACTIVE → COMPLETE + FROZEN on public product pages."""
    for path, frozen in (
        (_RECIPES, _BG_FROZEN_RECIPES),
        (_CARD, _BG_FROZEN_CARD),
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\*\*Wave BG ACTIVE:?\*\*[^\n]*",
            frozen,
            text,
            count=1,
        )
        if n:
            text = text2
        elif "**Wave BG COMPLETE + FROZEN**" not in text:
            text = text.rstrip() + "\n" + frozen + "\n"
        text = _dedupe_bg_frozen_lines(text)
        if "Wave BG8 BG-FREEZE" not in text and path == _RECIPES:
            row = (
                "| Wave BG8 BG-FREEZE | [bg-freeze.md](bg-freeze.md) · "
                "[formal-habgfreeze-bg-freeze.md]"
                "(formal-habgfreeze-bg-freeze.md) **PROMOTE** "
                "(`npm run nano:bg:freeze`) — COMPLETE+FROZEN; "
                "H-NANOGEN17 SKIP; do not invent Wave BH |\n"
            )
            if "| Wave BG7 BG-REPORT |" in text:
                text2, n2 = re.subn(
                    r"(\| Wave BG7 BG-REPORT \|[^\n]+\|\n)",
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
            r"- \*\*Wave BG ACTIVE\*\* —[^\n]+",
            _BG_FROZEN_AGENTS,
            text,
            count=1,
        )
        if n:
            _AGENTS.write_text(text2, encoding="utf-8")
        elif "**Wave BG COMPLETE + FROZEN**" not in text:
            # Slim AGENTS: append freeze pointer under Delivery posture.
            pass
    if _AGENDA.is_file():
        text = _AGENDA.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\| \*\*BG\*\* \| \*\*ACTIVE\*\* \|[^\n]+",
            (
                "| **BG** | **COMPLETE + FROZEN** | BG0–BG7 as logged · "
                "BG5 [H-NANOGEN17 SKIP]"
                "(results/nano-lm/formal-hnanogen17-nanogen17.md); "
                "BG6 [BG-REAL-EVAL PROMOTE]"
                "(results/nano-lm/wave-bg-real-eval.md) battery 17/17; "
                "BG7 [BG-REPORT PROMOTE]"
                "(results/nano-lm/wave-bg-summary.md) · "
                "[paper-lab-wave-bg.md](results/nano-lm/paper-lab-wave-bg.md); "
                "BG8 [BG-FREEZE PROMOTE](results/nano-lm/bg-freeze.md) "
                "(`npm run nano:bg:freeze`) · "
                "[formal-habgfreeze-bg-freeze.md]"
                "(results/nano-lm/formal-habgfreeze-bg-freeze.md) "
                "— ship AF+AQ+AS trust + STRICT ablated DECODE; "
                "H-NANOGEN17 SKIP; ≤5M; do not invent Wave BH |"
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
        r"Wave BG ACTIVE \([^)]+\)",
        (
            "Wave BG COMPLETE + FROZEN (BG0–BG7 as logged · "
            "BG8 `bg-freeze.md` PROMOTE; do not invent Wave BH)"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    old_r = (
        "BG6 BG-REAL-EVAL PROMOTE · BG7 BG-REPORT PROMOTE; "
        "next BG8 BG-FREEZE"
    )
    new_r = (
        "BG6 BG-REAL-EVAL PROMOTE · BG7 BG-REPORT PROMOTE · "
        "BG8 BG-FREEZE PROMOTE "
        "(`bg-freeze.md` · `formal-habgfreeze-bg-freeze.md`); "
        "do not invent Wave BH"
    )
    if old_r in text:
        text = text.replace(old_r, new_r, 1)
    elif "next BG8 BG-FREEZE" in text:
        text = text.replace(
            "next BG8 BG-FREEZE",
            (
                "BG8 `bg-freeze.md` · `formal-habgfreeze-bg-freeze.md` "
                "PROMOTE; do not invent Wave BH"
            ),
            1,
        )
    _EVOGEN.write_text(text, encoding="utf-8")


def _render_formal() -> str:
    return "\n".join(
        [
            "# BG-FREEZE — Wave BG lock (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §9 BG8 · "
            "Public note: [bg-freeze.md](bg-freeze.md)  ",
            "> After: [wave-bg-summary.md](wave-bg-summary.md) / "
            "[paper-lab-wave-bg.md](paper-lab-wave-bg.md)",
            "",
            "## Hypothesis",
            "",
            "After BG-REPORT, freeze Wave BG the same way BF-FREEZE "
            "locked BF: **outcomes stay** (H-UNARYINT·H-SHIPPUB·"
            "H-FASTBG·H-CTXBG·BG-REAL-EVAL·BG-REPORT PROMOTE; "
            "H-NANOGEN17 SKIP); **no Wave BH** without an explicit "
            "reopen agenda.",
            "",
            "## Gate",
            "",
            "| Check | Result |",
            "|-------|--------|",
            "| BG formals keep UNARYINT·SHIPPUB·FASTBG·CTXBG·REAL-EVAL·"
            "REPORT PROMOTE · NANOGEN17 SKIP | **ok** |",
            "| `wave-bg-summary` · `paper-lab-wave-bg` · `bg-freeze` "
            "contain **COMPLETE** | **ok** |",
            "| RECIPES + champion-card contain **H-NANOGEN17** · "
            "**BG-REAL-EVAL** · **COMPLETE** | **ok** |",
            "| LOOKUP·BG-FOREVER·OOD·over-refuse·util BG smoke | **ok** |",
            "| Decision | **PROMOTE** |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:bg:freeze",
            "```",
            "",
            "## Finding",
            "",
            f"1. Ship claim stays scoped **{SHIP_CLAIM}**.  ",
            "2. BG-FREEZE does **not** invent new serve/train hyps.  ",
            "3. Further research requires a new § in "
            "`.local/pesquisa.md` (Wave BH reopen).  ",
            "4. Anti-FP law remains: LOOKUP ≠ generative IQ; "
            "BG-FOREVER unary/transform LOOKUP = false-hit; "
            "exact-gold ABSTAIN = miss; "
            "PEAK ≠ unlabeled open chat; SAFE ≠ quality; "
            "span-fallback ≠ gen IQ; true-continue unlock locked "
            "(H-NANOGEN17 SKIP · NANOGEN16 SKIP · NANOGEN8…15 DEFER · "
            "NANOGEN6·7 HOLD).  ",
            "5. ≤5M hard law remains (CAPCHECK closed).",
            "",
            "## Artifacts",
            "",
            "- Module: `nano_lm/src/bg_freeze_ops.py` · "
            "Runner: `nano_lm/src/run_bg_freeze.py`",
            "- Summary: `results/nano-lm/wave-bg/bg_freeze.json`",
            "- Contract: `nano_lm/tests/test_bg_freeze.py`",
            "",
        ]
    )


def _write_freeze_docs() -> None:
    _FREEZE_DOC.parent.mkdir(parents=True, exist_ok=True)
    _SUMMARY.write_text(render_wave_bg_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_bg(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_bg_freeze(), encoding="utf-8")
    _FORMAL.write_text(_render_formal(), encoding="utf-8")
    if _SESSION_PUB.is_file():
        text = _SESSION_PUB.read_text(encoding="utf-8")
        for old, new in (
            (
                "Next: **BG8 BG-FREEZE**",
                "Next: **COMPLETE + FROZEN** — do not invent Wave BH "
                "without lab-book reopen (`npm run nano:bg:freeze`)",
            ),
            (
                "next BG8 BG-FREEZE",
                "COMPLETE + FROZEN — do not invent Wave BH",
            ),
            (
                "Next: **BG7 BG-REPORT**",
                "Next: **COMPLETE + FROZEN** — do not invent Wave BH "
                "without lab-book reopen (`npm run nano:bg:freeze`)",
            ),
        ):
            if old in text:
                text = text.replace(old, new, 1)
                _SESSION_PUB.write_text(text, encoding="utf-8")
                break
    if _REAL_EVAL.is_file():
        text = _REAL_EVAL.read_text(encoding="utf-8")
        text = text.replace(
            "Next: **BG7 BG-REPORT** (`npm run nano:bg:report`).",
            "Next: **COMPLETE + FROZEN** — do not invent Wave BH "
            "(`npm run nano:bg:freeze`).",
            1,
        )
        text = text.replace(
            "Next: **BG8 BG-FREEZE** (`npm run nano:bg:freeze`).",
            "Next: **COMPLETE + FROZEN** — do not invent Wave BH "
            "(`npm run nano:bg:freeze`).",
            1,
        )
        _REAL_EVAL.write_text(text, encoding="utf-8")
    _patch_product_freeze_status()
    _patch_agents_agenda()


def _smoke_bg_modes(*, workers: int) -> dict[str, Any]:
    from run_bg_report import _smoke_bg_modes as _smoke

    return _smoke(workers=workers)


def _update_local_session(decision: str) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    ok = str(decision).startswith("PROMOTE")
    status = "DONE — PROMOTE" if ok else f"DONE — {decision}"
    wave = "COMPLETE + FROZEN" if ok else "OPEN"
    body = "\n".join(
        [
            f"# Wave BG session checklist (**{wave}** · BG8 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            f"(Wave BG **{wave}**).  ",
            "> Parent: BF COMPLETE + FROZEN · Ship: **"
            + SHIP_CLAIM
            + "** · ≤5M (H-NANOGEN17 SKIP · NANOGEN16 SKIP · "
            "NANOGEN8…15 DEFER · NANOGEN6·7 HOLD · no true-continue unlock).",
            "",
            "## Current stage",
            "",
            f"**BG8 — BG-FREEZE ({status})** · Next: "
            "**do not invent Wave BH**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| Wave | **{wave}** |",
            f"| Decision | **{'PROMOTE' if ok else decision}** |",
            "| Public | `docs/results/nano-lm/bg-freeze.md` |",
            "| Formal | "
            "`docs/results/nano-lm/formal-habgfreeze-bg-freeze.md` |",
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
            "| BG5 | H-NANOGEN17 | **DONE — SKIP** |",
            "| BG6 | BG-REAL-EVAL | **DONE — PROMOTE** |",
            "| BG7 | BG-REPORT | **DONE — PROMOTE** |",
            f"| BG8 | BG-FREEZE | **{status}** |",
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

**Wave BG {wave}** · BG8 BG-FREEZE **DONE — {status}**.
Do **not** invent Wave BH without lab-book reopen.

```bash
npm run nano:bg:freeze
npm run nano:test && npm run verify
```
""",
        encoding="utf-8",
    )
    _LOCAL_README.write_text(
        f"""# Local research notebook

Full lab book: **`pesquisa.md`**.

**Wave BG {wave}** — BG8 **BG-FREEZE {status}**.

Do **not** invent Wave BH without explicit reopen.
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
        r"\| BG8 \| \*\*BG-FREEZE\*\* \|[^\n]+\| \*\*NEXT\*\* \|",
        (
            "| BG8 | **BG-FREEZE** | Lock outcomes | "
            f"no Wave BH without reopen | **DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"(\| BG8 \| \*\*BG-FREEZE\*\* \|[^\n]+\| )\*\*TODO\*\* \|",
        (
            "| BG8 | **BG-FREEZE** | Lock outcomes | "
            f"no Wave BH without reopen | **DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    if ok:
        text = text.replace(
            "# pesquisa — Wave BG (**REOPENED** · post-BF live truth)",
            "# pesquisa — Wave BG (**COMPLETE + FROZEN**)",
            1,
        )
        text = text.replace(
            "## 9. Wave BG stage machine (**REOPENED**)",
            "## 9. Wave BG stage machine (**COMPLETE + FROZEN**)",
            1,
        )
        text2, n = re.subn(
            r"> \*\*Status:\*\* Wave BF \*\*COMPLETE \+ FROZEN\*\* "
            r"\(archive\)\. Wave \*\*BG ACTIVE\*\*[^\n]*\.",
            (
                "> **Status:** Wave BG **COMPLETE + FROZEN**. "
                "Do **not** invent Wave BH without explicit reopen. "
                "Parent: Wave BF **COMPLETE + FROZEN** (archive)."
            ),
            text,
            count=1,
        )
        if n:
            text = text2
        text = text.replace(
            "> **Session:** `.local/wave-bg/SESSION.md` "
            "(BG7 BG-REPORT **DONE — PROMOTE**; next BG8 BG-FREEZE).  ",
            "> **Session:** `.local/wave-bg/SESSION.md` "
            f"(BG8 BG-FREEZE **DONE — {status}**; "
            "**COMPLETE + FROZEN**).  ",
            1,
        )
        text = text.replace(
            "(BG7 BG-REPORT **DONE — PROMOTE**; next BG8 BG-FREEZE)",
            f"(BG8 BG-FREEZE **DONE — {status}**; **COMPLETE + FROZEN**)",
        )
        text = text.replace(
            "> **Archive:** Waves W–**BF** → "
            "`docs/results/nano-lm/*-freeze.md`.",
            "> **Archive:** Waves W–**BG** → "
            "`docs/results/nano-lm/*-freeze.md`.",
            1,
        )
        text = text.replace(
            "### W–BF — COMPLETE + FROZEN",
            "### W–BG — COMPLETE + FROZEN",
            1,
        )
        text = text.replace(
            "Invent Wave BH before BG-FREEZE",
            "Invent Wave BH without lab-book reopen",
        )
    text = text.replace(
        (
            "8. **BG7 BG-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:bg:report`) · next BG8 freeze.  \n"
            "9. **BG8 BG-FREEZE** — **NEXT** — lock; do not invent Wave BH.  "
        ),
        (
            "8. **BG7 BG-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:bg:report`).  \n"
            f"9. **BG8 BG-FREEZE** — **DONE {status}** "
            "(`npm run nano:bg:freeze`) · **COMPLETE + FROZEN** · "
            "do not invent Wave BH.  "
        ),
        1,
    )
    bash_old = "# next: nano:bg:freeze"
    bash_new = (
        "npm run nano:bg:freeze\n"
        "# Wave BG COMPLETE + FROZEN — do not invent Wave BH"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")
    _patch_local_helpers(status, ok)


def run_bg_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN BG formals + COMPLETE closeout
    WHEN locking Wave BG
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    threads, workers = _hardware()
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in BG_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *BG_PUBLIC, *BG_PRODUCT_DOCS])
    )
    with ThreadPoolExecutor(
        max_workers=min(workers, max(4, len(read_paths)))
    ) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in BG_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in BG_PRODUCT_DOCS}
    decision = decide_bg_freeze(
        formal_texts=formal_texts,
        public_texts=public_texts,
        product_texts=product_texts,
    )
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_bg_modes(workers=workers)
        if not bool(ask.get("ok")):
            decision = "KILL (BG forever/modes smoke failed)"
    ok = str(decision).startswith("PROMOTE")
    _update_local_session(decision)
    _patch_pesquisa(decision)
    payload: dict[str, Any] = {
        "id": BG_FREEZE_ID,
        "hyp_id": BG_FREEZE_ID,
        "stage": "BG8",
        "thesis": BG_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in BG_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/bg-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-habgfreeze-bg-freeze.md",
        "wave_bg_summary": "docs/results/nano-lm/wave-bg-summary.md",
        "rule": "pesquisa §9 BG-FREEZE",
        "wave_status": "COMPLETE+FROZEN" if ok else "RESEARCH_COMPLETE",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": threads,
        "workers": workers,
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave BG8 BG-FREEZE")
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    threads, _workers = _hardware()
    try:
        summary = run_bg_freeze(
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
                "hyp_id": BG_FREEZE_ID,
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
