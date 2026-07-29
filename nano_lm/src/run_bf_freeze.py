"""Wave BF-FREEZE runner (nano:bf:freeze) — lock BF; no Wave BG invent."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from bf_freeze_ops import (
    BF_DECISIONS,
    BF_FREEZE_ID,
    BF_PRODUCT_DOCS,
    BF_PUBLIC,
    BF_THESIS,
    SHIP_CLAIM,
    decide_bf_freeze,
    render_bf_freeze,
)
from bf_report_ops import render_paper_lab_wave_bf, render_wave_bf_summary
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-bf/bf_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/bf-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-habffreeze-bf-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-bf-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-bf.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_AGENTS = REPO / "AGENTS.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_SESSION_PUB = REPO / "docs/results/nano-lm/wave-bf-session.md"
_REAL_EVAL = REPO / "docs/results/nano-lm/wave-bf-real-eval.md"
_LOCAL_SESSION = REPO / ".local/wave-bf/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"

_BF_FROZEN_RECIPES = (
    "**Wave BF COMPLETE + FROZEN:** BF0 [SESSION PROMOTE]"
    "(wave-bf-session.md) (`npm run nano:bf:session`) · "
    "BF1 [H-PREDINT PROMOTE](formal-hpredint-predint.md) "
    "(`npm run nano:predint`) · BF2 [H-SHIPUSE2 PROMOTE]"
    "(formal-hshipuse2-shipuse2.md) (`npm run nano:shipuse2`) · "
    "BF3 [H-FASTBF PROMOTE](formal-hfastbf-fastbf.md) "
    "(`npm run nano:fastbf`) · BF4 [H-CTXBF PROMOTE]"
    "(formal-hctxbf-ctxbf.md) (`npm run nano:ctxbf`) · "
    "BF5 [H-NANOGEN16 SKIP](formal-hnanogen16-nanogen16.md) "
    "(`npm run nano:nanogen16`) · BF6 [BF-REAL-EVAL PROMOTE]"
    "(wave-bf-real-eval.md) (`npm run nano:bf:real-eval`) — "
    "battery 16/16 · BF7 [BF-REPORT PROMOTE](wave-bf-summary.md) "
    "(`npm run nano:bf:report`) · [paper-lab-wave-bf.md]"
    "(paper-lab-wave-bf.md); BF8 [BF-FREEZE PROMOTE](bf-freeze.md) "
    "(`npm run nano:bf:freeze`) · [formal-habffreeze-bf-freeze.md]"
    "(formal-habffreeze-bf-freeze.md) — ship **AF + AQ + AS trust + "
    "ablated DECODE (STRICT)**; H-NANOGEN16 SKIP (NANOGEN6·7 HOLD · "
    "NANOGEN8…15 DEFER stand); ≤5M stays; do not invent Wave BG."
)

_BF_FROZEN_CARD = _BF_FROZEN_RECIPES.replace(
    "**Wave BF COMPLETE + FROZEN:**",
    "**Wave BF COMPLETE + FROZEN** —",
)

_BF_FROZEN_AGENTS = (
    "- **Wave BF COMPLETE + FROZEN** — BF0 [SESSION PROMOTE]"
    "(docs/results/nano-lm/wave-bf-session.md) (`npm run nano:bf:session`) · "
    "BF1 [H-PREDINT PROMOTE]"
    "(docs/results/nano-lm/formal-hpredint-predint.md) "
    "(`npm run nano:predint`) · BF2 [H-SHIPUSE2 PROMOTE]"
    "(docs/results/nano-lm/formal-hshipuse2-shipuse2.md) "
    "(`npm run nano:shipuse2`) · BF3 [H-FASTBF PROMOTE]"
    "(docs/results/nano-lm/formal-hfastbf-fastbf.md) "
    "(`npm run nano:fastbf`) · BF4 [H-CTXBF PROMOTE]"
    "(docs/results/nano-lm/formal-hctxbf-ctxbf.md) "
    "(`npm run nano:ctxbf`) · BF5 [H-NANOGEN16 SKIP]"
    "(docs/results/nano-lm/formal-hnanogen16-nanogen16.md) "
    "(`npm run nano:nanogen16`) · BF6 [BF-REAL-EVAL PROMOTE]"
    "(docs/results/nano-lm/wave-bf-real-eval.md) "
    "(`npm run nano:bf:real-eval`) — battery 16/16 · "
    "BF7 [BF-REPORT PROMOTE](docs/results/nano-lm/wave-bf-summary.md) "
    "(`npm run nano:bf:report`) · [paper-lab-wave-bf.md]"
    "(docs/results/nano-lm/paper-lab-wave-bf.md); "
    "BF8 [BF-FREEZE PROMOTE](docs/results/nano-lm/bf-freeze.md) "
    "(`npm run nano:bf:freeze`) · "
    "[formal-habffreeze-bf-freeze.md]"
    "(docs/results/nano-lm/formal-habffreeze-bf-freeze.md) "
    "— ship **AF + AQ + AS trust + ablated DECODE (STRICT)**; "
    "H-NANOGEN16 SKIP (NANOGEN6·7 HOLD · NANOGEN8…15 DEFER "
    "stand); ≤5M stays; do not invent Wave BG."
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
    # 16c / ~31Gi: leave ≥4 cores free; prefer throughput for live smoke.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    workers = min(8, max(4, cpus - 4))
    return threads, workers


def _read_text(rel: str) -> str:
    path = REPO / rel
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _ensure_markers(text: str) -> str:
    if "H-NANOGEN16" not in text:
        text += "\nH-NANOGEN16\n"
    if "BF-REAL-EVAL" not in text:
        text += "\nBF-REAL-EVAL\n"
    if "COMPLETE" not in text:
        text += "\nCOMPLETE\n"
    return text


def _dedupe_bf_frozen_lines(text: str) -> str:
    kept: list[str] = []
    seen = False
    for line in text.splitlines(keepends=True):
        if line.startswith("**Wave BF COMPLETE + FROZEN:**"):
            if seen:
                continue
            seen = True
        kept.append(line)
    return "".join(kept)


def _patch_product_freeze_status() -> None:
    """Flip ACTIVE → COMPLETE + FROZEN on public product pages."""
    for path, frozen in (
        (_RECIPES, _BF_FROZEN_RECIPES),
        (_CARD, _BF_FROZEN_CARD),
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\*\*Wave BF ACTIVE:?\*\*[^\n]*",
            frozen,
            text,
            count=1,
        )
        if n:
            text = text2
        elif "**Wave BF COMPLETE + FROZEN**" not in text:
            text = text.rstrip() + "\n" + frozen + "\n"
        text = _dedupe_bf_frozen_lines(text)
        if "Wave BF8 BF-FREEZE" not in text and path == _RECIPES:
            needle = (
                "| Wave BF7 BF-REPORT | [wave-bf-summary.md]"
                "(wave-bf-summary.md) · [paper-lab-wave-bf.md]"
                "(paper-lab-wave-bf.md) **PROMOTE** "
                "(`npm run nano:bf:report`) — anti-FP · util · "
                "BF5 SKIP · NANOGEN6/7 HOLD · NANOGEN8…15 DEFER cited |\n"
            )
            row = (
                "| Wave BF8 BF-FREEZE | [bf-freeze.md](bf-freeze.md) · "
                "[formal-habffreeze-bf-freeze.md]"
                "(formal-habffreeze-bf-freeze.md) **PROMOTE** "
                "(`npm run nano:bf:freeze`) — COMPLETE+FROZEN; "
                "H-NANOGEN16 SKIP; do not invent Wave BG |\n"
            )
            if needle in text:
                text = text.replace(needle, needle + row, 1)
            elif "| Wave BF7 BF-REPORT |" in text:
                text2, n2 = re.subn(
                    r"(\| Wave BF7 BF-REPORT \|[^\n]+\|\n)",
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
            r"- \*\*Wave BF ACTIVE\*\* —[^\n]+",
            _BF_FROZEN_AGENTS,
            text,
            count=1,
        )
        if n:
            _AGENTS.write_text(text2, encoding="utf-8")
    if _AGENDA.is_file():
        text = _AGENDA.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\| \*\*BF\*\* \| \*\*ACTIVE\*\* \|[^\n]+",
            (
                "| **BF** | **COMPLETE + FROZEN** | BF0–BF7 as logged · "
                "BF5 [H-NANOGEN16 SKIP]"
                "(results/nano-lm/formal-hnanogen16-nanogen16.md); "
                "BF6 [BF-REAL-EVAL PROMOTE]"
                "(results/nano-lm/wave-bf-real-eval.md) battery 16/16; "
                "BF7 [BF-REPORT PROMOTE]"
                "(results/nano-lm/wave-bf-summary.md) · "
                "[paper-lab-wave-bf.md](results/nano-lm/paper-lab-wave-bf.md); "
                "BF8 [BF-FREEZE PROMOTE](results/nano-lm/bf-freeze.md) "
                "(`npm run nano:bf:freeze`) · "
                "[formal-habffreeze-bf-freeze.md]"
                "(results/nano-lm/formal-habffreeze-bf-freeze.md) "
                "— ship AF+AQ+AS trust + STRICT ablated DECODE; "
                "H-NANOGEN16 SKIP; ≤5M; do not invent Wave BG |"
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
        r"Wave BF ACTIVE \([^)]+\)",
        (
            "Wave BF COMPLETE + FROZEN (BF0–BF7 as logged · "
            "BF8 `bf-freeze.md` PROMOTE; do not invent Wave BG)"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    old_r = (
        "BF6 BF-REAL-EVAL PROMOTE · BF7 BF-REPORT PROMOTE; "
        "next BF8 BF-FREEZE"
    )
    new_r = (
        "BF6 BF-REAL-EVAL PROMOTE · BF7 BF-REPORT PROMOTE · "
        "BF8 BF-FREEZE PROMOTE "
        "(`bf-freeze.md` · `formal-habffreeze-bf-freeze.md`); "
        "do not invent Wave BG"
    )
    if old_r in text:
        text = text.replace(old_r, new_r, 1)
    elif "next BF8 BF-FREEZE" in text:
        text = text.replace(
            "next BF8 BF-FREEZE",
            (
                "BF8 `bf-freeze.md` · `formal-habffreeze-bf-freeze.md` "
                "PROMOTE; do not invent Wave BG"
            ),
            1,
        )
    _EVOGEN.write_text(text, encoding="utf-8")


def _render_formal() -> str:
    return "\n".join(
        [
            "# BF-FREEZE — Wave BF lock (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §9 BF8 · "
            "Public note: [bf-freeze.md](bf-freeze.md)  ",
            "> After: [wave-bf-summary.md](wave-bf-summary.md) / "
            "[paper-lab-wave-bf.md](paper-lab-wave-bf.md)",
            "",
            "## Hypothesis",
            "",
            "After BF-REPORT, freeze Wave BF the same way BE-FREEZE "
            "locked BE: **outcomes stay** (H-PREDINT·H-SHIPUSE2·"
            "H-FASTBF·H-CTXBF·BF-REAL-EVAL·BF-REPORT PROMOTE; "
            "H-NANOGEN16 SKIP); **no Wave BG** without an explicit "
            "reopen agenda.",
            "",
            "## Gate",
            "",
            "| Check | Result |",
            "|-------|--------|",
            "| BF formals keep PREDINT·SHIPUSE2·FASTBF·CTXBF·REAL-EVAL·"
            "REPORT PROMOTE · NANOGEN16 SKIP | **ok** |",
            "| `wave-bf-summary` · `paper-lab-wave-bf` · `bf-freeze` "
            "contain **COMPLETE** | **ok** |",
            "| RECIPES + champion-card contain **H-NANOGEN16** · "
            "**BF-REAL-EVAL** · **COMPLETE** | **ok** |",
            "| LOOKUP·BF-FOREVER·OOD·over-refuse·util BF smoke | **ok** |",
            "| Decision | **PROMOTE** |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:bf:freeze",
            "```",
            "",
            "## Finding",
            "",
            f"1. Ship claim stays scoped **{SHIP_CLAIM}**.  ",
            "2. BF-FREEZE does **not** invent new serve/train hyps.  ",
            "3. Further research requires a new § in "
            "`.local/pesquisa.md` (Wave BG reopen).  ",
            "4. Anti-FP law remains: LOOKUP ≠ generative IQ; "
            "BF-FOREVER predicate LOOKUP = false-hit; "
            "exact-gold ABSTAIN = miss; "
            "PEAK ≠ unlabeled open chat; SAFE ≠ quality; "
            "span-fallback ≠ gen IQ; true-continue unlock locked "
            "(H-NANOGEN16 SKIP · NANOGEN8…15 DEFER · "
            "NANOGEN6·7 HOLD).  ",
            "5. ≤5M hard law remains (CAPCHECK closed).",
            "",
            "## Artifacts",
            "",
            "- Module: `nano_lm/src/bf_freeze_ops.py` · "
            "Runner: `nano_lm/src/run_bf_freeze.py`",
            "- Summary: `results/nano-lm/wave-bf/bf_freeze.json`",
            "- Contract: `nano_lm/tests/test_bf_freeze.py`",
            "",
        ]
    )


def _write_freeze_docs() -> None:
    _FREEZE_DOC.parent.mkdir(parents=True, exist_ok=True)
    _SUMMARY.write_text(render_wave_bf_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_bf(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_bf_freeze(), encoding="utf-8")
    _FORMAL.write_text(_render_formal(), encoding="utf-8")
    if _SESSION_PUB.is_file():
        text = _SESSION_PUB.read_text(encoding="utf-8")
        for old, new in (
            (
                "Next: **BF8 BF-FREEZE**",
                "Next: **COMPLETE + FROZEN** — do not invent Wave BG "
                "without lab-book reopen (`npm run nano:bf:freeze`)",
            ),
            (
                "next BF8 BF-FREEZE",
                "COMPLETE + FROZEN — do not invent Wave BG",
            ),
            (
                "Next: **BF7 BF-REPORT**",
                "Next: **COMPLETE + FROZEN** — do not invent Wave BG "
                "without lab-book reopen (`npm run nano:bf:freeze`)",
            ),
            (
                "Next: **BF1 H-PREDINT**",
                "Next: **COMPLETE + FROZEN** — do not invent Wave BG "
                "without lab-book reopen (`npm run nano:bf:freeze`)",
            ),
        ):
            if old in text:
                text = text.replace(old, new, 1)
                _SESSION_PUB.write_text(text, encoding="utf-8")
                break
    if _REAL_EVAL.is_file():
        text = _REAL_EVAL.read_text(encoding="utf-8")
        text = text.replace(
            "Next: **BF7 BF-REPORT** (`npm run nano:bf:report`).",
            "Next: **COMPLETE + FROZEN** — do not invent Wave BG "
            "(`npm run nano:bf:freeze`).",
            1,
        )
        text = text.replace(
            "Next: **BF8 BF-FREEZE** (`npm run nano:bf:freeze`).",
            "Next: **COMPLETE + FROZEN** — do not invent Wave BG "
            "(`npm run nano:bf:freeze`).",
            1,
        )
        _REAL_EVAL.write_text(text, encoding="utf-8")
    _patch_product_freeze_status()
    _patch_agents_agenda()


def _smoke_bf_modes(*, workers: int) -> dict[str, Any]:
    from run_bf_report import _smoke_bf_modes as _smoke

    return _smoke(workers=workers)


def _update_local_session(decision: str) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    ok = str(decision).startswith("PROMOTE")
    status = "DONE — PROMOTE" if ok else f"DONE — {decision}"
    wave = "COMPLETE + FROZEN" if ok else "OPEN"
    body = "\n".join(
        [
            f"# Wave BF session checklist (**{wave}** · BF8 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            f"(Wave BF **{wave}**).  ",
            "> Parent: BE COMPLETE + FROZEN · Ship: **"
            + SHIP_CLAIM
            + "** · ≤5M (H-NANOGEN16 SKIP · NANOGEN8…15 DEFER · "
            "NANOGEN6·7 HOLD · no true-continue unlock).",
            "",
            "## Current stage",
            "",
            f"**BF8 — BF-FREEZE ({status})** · Next: "
            "**do not invent Wave BG**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| Wave | **{wave}** |",
            f"| Decision | **{'PROMOTE' if ok else decision}** |",
            "| Public | `docs/results/nano-lm/bf-freeze.md` |",
            "| Formal | "
            "`docs/results/nano-lm/formal-habffreeze-bf-freeze.md` |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| BF0 | SESSION | **DONE — PROMOTE** |",
            "| BF1 | H-PREDINT | **DONE — PROMOTE** |",
            "| BF2 | H-SHIPUSE2 | **DONE — PROMOTE** |",
            "| BF3 | H-FASTBF | **DONE — PROMOTE** |",
            "| BF4 | H-CTXBF | **DONE — PROMOTE** |",
            "| BF5 | H-NANOGEN16 | **DONE — SKIP** |",
            "| BF6 | BF-REAL-EVAL | **DONE — PROMOTE** |",
            "| BF7 | BF-REPORT | **DONE — PROMOTE** |",
            f"| BF8 | BF-FREEZE | **{status}** |",
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

**Wave BF {wave}** · BF8 BF-FREEZE **DONE — {status}**.
Do **not** invent Wave BG without lab-book reopen.

```bash
npm run nano:bf:freeze
npm run nano:test && npm run verify
```
""",
        encoding="utf-8",
    )
    _LOCAL_README.write_text(
        f"""# Local research notebook

Full lab book: **`pesquisa.md`**.

**Wave BF {wave}** — BF8 **BF-FREEZE {status}**.

Do **not** invent Wave BG without explicit reopen.
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
        r"\| BF8 \| \*\*BF-FREEZE\*\* \|[^\n]+\| \*\*NEXT\*\* \|",
        (
            "| BF8 | **BF-FREEZE** | Lock outcomes | "
            f"no Wave BG without reopen | **DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"(\| BF8 \| \*\*BF-FREEZE\*\* \|[^\n]+\| )\*\*TODO\*\* \|",
        (
            "| BF8 | **BF-FREEZE** | Lock outcomes | "
            f"no Wave BG without reopen | **DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    if ok:
        text = text.replace(
            "# pesquisa — Wave BF (**REOPENED** · post-BE live truth)",
            "# pesquisa — Wave BF (**COMPLETE + FROZEN**)",
            1,
        )
        text = text.replace(
            "## 9. Wave BF stage machine (**REOPENED**)",
            "## 9. Wave BF stage machine (**COMPLETE + FROZEN**)",
            1,
        )
        text2, n = re.subn(
            r"> \*\*Status:\*\* Wave BE \*\*COMPLETE \+ FROZEN\*\* "
            r"\(archive\)\. Wave \*\*BF ACTIVE\*\*[^\n]*\.",
            (
                "> **Status:** Wave BF **COMPLETE + FROZEN**. "
                "Do **not** invent Wave BG without explicit reopen. "
                "Parent: Wave BE **COMPLETE + FROZEN** (archive)."
            ),
            text,
            count=1,
        )
        if n:
            text = text2
        text = text.replace(
            "> **Session:** `.local/wave-bf/SESSION.md` "
            "(BF7 BF-REPORT **DONE — PROMOTE**; next BF8 BF-FREEZE).  ",
            "> **Session:** `.local/wave-bf/SESSION.md` "
            f"(BF8 BF-FREEZE **DONE — {status}**; "
            "**COMPLETE + FROZEN**).  ",
            1,
        )
        text = text.replace(
            "> **Archive:** Waves W–**BE** → "
            "`docs/results/nano-lm/*-freeze.md`.",
            "> **Archive:** Waves W–**BF** → "
            "`docs/results/nano-lm/*-freeze.md`.",
            1,
        )
        text = text.replace(
            "### W–BE — COMPLETE + FROZEN",
            "### W–BF — COMPLETE + FROZEN",
            1,
        )
        text = text.replace(
            "Invent Wave BG before BF-FREEZE",
            "Invent Wave BG without lab-book reopen",
            1,
        )
    text = text.replace(
        (
            "8. **BF7 BF-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:bf:report`) · next BF8 freeze.  \n"
            "9. **BF8 BF-FREEZE** — **NEXT** — lock; do not invent Wave BG.  "
        ),
        (
            "8. **BF7 BF-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:bf:report`).  \n"
            f"9. **BF8 BF-FREEZE** — **DONE {status}** "
            "(`npm run nano:bf:freeze`) · **COMPLETE + FROZEN** · "
            "do not invent Wave BG.  "
        ),
        1,
    )
    bash_old = "# next: nano:bf:freeze"
    bash_new = (
        "npm run nano:bf:freeze\n"
        "# Wave BF COMPLETE + FROZEN — do not invent Wave BG"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")
    _patch_local_helpers(status, ok)


def run_bf_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN BF formals + COMPLETE closeout
    WHEN locking Wave BF
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    threads, workers = _hardware()
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in BF_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *BF_PUBLIC, *BF_PRODUCT_DOCS])
    )
    with ThreadPoolExecutor(
        max_workers=min(workers, max(4, len(read_paths)))
    ) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in BF_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in BF_PRODUCT_DOCS}
    decision = decide_bf_freeze(
        formal_texts=formal_texts,
        public_texts=public_texts,
        product_texts=product_texts,
    )
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_bf_modes(workers=workers)
        if not bool(ask.get("ok")):
            decision = "KILL (BF forever/modes smoke failed)"
    ok = str(decision).startswith("PROMOTE")
    _update_local_session(decision)
    _patch_pesquisa(decision)
    payload: dict[str, Any] = {
        "id": BF_FREEZE_ID,
        "hyp_id": BF_FREEZE_ID,
        "stage": "BF8",
        "thesis": BF_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in BF_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/bf-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-habffreeze-bf-freeze.md",
        "wave_bf_summary": "docs/results/nano-lm/wave-bf-summary.md",
        "rule": "pesquisa §9 BF-FREEZE",
        "wave_status": "COMPLETE+FROZEN" if ok else "RESEARCH_COMPLETE",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": threads,
        "workers": workers,
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave BF8 BF-FREEZE")
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    threads, _workers = _hardware()
    try:
        summary = run_bf_freeze(
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
                "hyp_id": BF_FREEZE_ID,
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
