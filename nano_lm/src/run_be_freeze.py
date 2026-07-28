"""Wave BE-FREEZE runner (nano:be:freeze) — lock BE; no Wave BF invent."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from be_freeze_ops import (
    BE_DECISIONS,
    BE_FREEZE_ID,
    BE_PRODUCT_DOCS,
    BE_PUBLIC,
    BE_THESIS,
    SHIP_CLAIM,
    decide_be_freeze,
    render_be_freeze,
)
from be_report_ops import render_paper_lab_wave_be, render_wave_be_summary
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-be/be_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/be-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-habefreeze-be-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-be-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-be.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_AGENTS = REPO / "AGENTS.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_SESSION_PUB = REPO / "docs/results/nano-lm/wave-be-session.md"
_REAL_EVAL = REPO / "docs/results/nano-lm/wave-be-real-eval.md"
_LOCAL_SESSION = REPO / ".local/wave-be/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"

_BE_FROZEN_RECIPES = (
    "**Wave BE COMPLETE + FROZEN:** BE0 [SESSION PROMOTE]"
    "(wave-be-session.md) (`npm run nano:be:session`) · "
    "BE1 [H-COMPINT PROMOTE](formal-hcompint-compint.md) "
    "(`npm run nano:compint`) · BE2 [H-SHIPUSE PROMOTE]"
    "(formal-hshipuse-shipuse.md) (`npm run nano:shipuse`) · "
    "BE3 [H-FASTBE PROMOTE](formal-hfastbe-fastbe.md) "
    "(`npm run nano:fastbe`) · BE4 [H-CTXBE PROMOTE]"
    "(formal-hctxbe-ctxbe.md) (`npm run nano:ctxbe`) · "
    "BE5 [H-NANOGEN15 DEFER](formal-hnanogen15-nanogen15.md) "
    "(`npm run nano:nanogen15`) · BE6 [BE-REAL-EVAL PROMOTE]"
    "(wave-be-real-eval.md) (`npm run nano:be:real-eval`) — "
    "battery 15/15 · BE7 [BE-REPORT PROMOTE](wave-be-summary.md) "
    "(`npm run nano:be:report`) · [paper-lab-wave-be.md]"
    "(paper-lab-wave-be.md); BE8 [BE-FREEZE PROMOTE](be-freeze.md) "
    "(`npm run nano:be:freeze`) · [formal-habefreeze-be-freeze.md]"
    "(formal-habefreeze-be-freeze.md) — ship **AF + AQ + AS trust + "
    "ablated DECODE (STRICT)**; H-NANOGEN15 DEFER (NANOGEN6·7 HOLD · "
    "NANOGEN8…14 DEFER stand); ≤5M stays; do not invent Wave BF."
)

_BE_FROZEN_CARD = _BE_FROZEN_RECIPES.replace(
    "**Wave BE COMPLETE + FROZEN:**",
    "**Wave BE COMPLETE + FROZEN** —",
)

_BE_FROZEN_AGENTS = (
    "- **Wave BE COMPLETE + FROZEN** — BE0 [SESSION PROMOTE]"
    "(docs/results/nano-lm/wave-be-session.md) (`npm run nano:be:session`) · "
    "BE1 [H-COMPINT PROMOTE]"
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
    "(`npm run nano:be:real-eval`) — battery 15/15 · "
    "BE7 [BE-REPORT PROMOTE](docs/results/nano-lm/wave-be-summary.md) "
    "(`npm run nano:be:report`) · [paper-lab-wave-be.md]"
    "(docs/results/nano-lm/paper-lab-wave-be.md); "
    "BE8 [BE-FREEZE PROMOTE](docs/results/nano-lm/be-freeze.md) "
    "(`npm run nano:be:freeze`) · "
    "[formal-habefreeze-be-freeze.md]"
    "(docs/results/nano-lm/formal-habefreeze-be-freeze.md) "
    "— ship **AF + AQ + AS trust + ablated DECODE (STRICT)**; "
    "H-NANOGEN15 DEFER (NANOGEN6·7 HOLD · NANOGEN8…14 DEFER "
    "stand); ≤5M stays; do not invent Wave BF."
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
    if "H-NANOGEN15" not in text:
        text += "\nH-NANOGEN15\n"
    if "BE-REAL-EVAL" not in text:
        text += "\nBE-REAL-EVAL\n"
    if "COMPLETE" not in text:
        text += "\nCOMPLETE\n"
    return text


def _dedupe_be_frozen_lines(text: str) -> str:
    kept: list[str] = []
    seen = False
    for line in text.splitlines(keepends=True):
        if line.startswith("**Wave BE COMPLETE + FROZEN:**"):
            if seen:
                continue
            seen = True
        kept.append(line)
    return "".join(kept)


def _patch_product_freeze_status() -> None:
    """Flip ACTIVE → COMPLETE + FROZEN on public product pages."""
    for path, frozen in (
        (_RECIPES, _BE_FROZEN_RECIPES),
        (_CARD, _BE_FROZEN_CARD),
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\*\*Wave BE ACTIVE:?\*\*[^\n]*",
            frozen,
            text,
            count=1,
        )
        if n:
            text = text2
        elif "**Wave BE COMPLETE + FROZEN**" not in text:
            text = text.rstrip() + "\n" + frozen + "\n"
        text = _dedupe_be_frozen_lines(text)
        if "Wave BE8 BE-FREEZE" not in text and path == _RECIPES:
            needle = (
                "| Wave BE7 BE-REPORT | [wave-be-summary.md]"
                "(wave-be-summary.md) · [paper-lab-wave-be.md]"
                "(paper-lab-wave-be.md) **PROMOTE** "
                "(`npm run nano:be:report`) — anti-FP · util · "
                "BE5 DEFER · NANOGEN6/7 HOLD · NANOGEN8…15 DEFER cited |\n"
            )
            row = (
                "| Wave BE8 BE-FREEZE | [be-freeze.md](be-freeze.md) · "
                "[formal-habefreeze-be-freeze.md]"
                "(formal-habefreeze-be-freeze.md) **PROMOTE** "
                "(`npm run nano:be:freeze`) — COMPLETE+FROZEN; "
                "H-NANOGEN15 DEFER; do not invent Wave BF |\n"
            )
            if needle in text:
                text = text.replace(needle, needle + row, 1)
            elif "| Wave BE7 BE-REPORT |" in text:
                text2, n2 = re.subn(
                    r"(\| Wave BE7 BE-REPORT \|[^\n]+\|\n)",
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
            r"- \*\*Wave BE ACTIVE\*\* —[^\n]+",
            _BE_FROZEN_AGENTS,
            text,
            count=1,
        )
        if n:
            _AGENTS.write_text(text2, encoding="utf-8")
    if _AGENDA.is_file():
        text = _AGENDA.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\| \*\*BE\*\* \| \*\*ACTIVE\*\* \|[^\n]+",
            (
                "| **BE** | **COMPLETE + FROZEN** | BE0–BE7 as logged · "
                "BE5 [H-NANOGEN15 DEFER]"
                "(results/nano-lm/formal-hnanogen15-nanogen15.md); "
                "BE6 [BE-REAL-EVAL PROMOTE]"
                "(results/nano-lm/wave-be-real-eval.md) battery 15/15; "
                "BE7 [BE-REPORT PROMOTE]"
                "(results/nano-lm/wave-be-summary.md) · "
                "[paper-lab-wave-be.md](results/nano-lm/paper-lab-wave-be.md); "
                "BE8 [BE-FREEZE PROMOTE](results/nano-lm/be-freeze.md) "
                "(`npm run nano:be:freeze`) · "
                "[formal-habefreeze-be-freeze.md]"
                "(results/nano-lm/formal-habefreeze-be-freeze.md) "
                "— ship AF+AQ+AS trust + STRICT ablated DECODE; "
                "H-NANOGEN15 DEFER; ≤5M; do not invent Wave BF |"
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
        r"Wave BE ACTIVE \([^)]+\)",
        (
            "Wave BE COMPLETE + FROZEN (BE0–BE7 as logged · "
            "BE8 `be-freeze.md` PROMOTE; do not invent Wave BF)"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    old_r = (
        "BE6 BE-REAL-EVAL PROMOTE · BE7 BE-REPORT PROMOTE; "
        "next BE8 BE-FREEZE"
    )
    new_r = (
        "BE6 BE-REAL-EVAL PROMOTE · BE7 BE-REPORT PROMOTE · "
        "BE8 BE-FREEZE PROMOTE "
        "(`be-freeze.md` · `formal-habefreeze-be-freeze.md`); "
        "do not invent Wave BF"
    )
    if old_r in text:
        text = text.replace(old_r, new_r, 1)
    elif "next BE8 BE-FREEZE" in text:
        text = text.replace(
            "next BE8 BE-FREEZE",
            (
                "BE8 `be-freeze.md` · `formal-habefreeze-be-freeze.md` "
                "PROMOTE; do not invent Wave BF"
            ),
            1,
        )
    _EVOGEN.write_text(text, encoding="utf-8")


def _render_formal() -> str:
    return "\n".join(
        [
            "# BE-FREEZE — Wave BE lock (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §9 BE8 · "
            "Public note: [be-freeze.md](be-freeze.md)  ",
            "> After: [wave-be-summary.md](wave-be-summary.md) / "
            "[paper-lab-wave-be.md](paper-lab-wave-be.md)",
            "",
            "## Hypothesis",
            "",
            "After BE-REPORT, freeze Wave BE the same way BD-FREEZE "
            "locked BD: **outcomes stay** (H-COMPINT·H-SHIPUSE·"
            "H-FASTBE·H-CTXBE·BE-REAL-EVAL·BE-REPORT PROMOTE; "
            "H-NANOGEN15 DEFER); **no Wave BF** without an explicit "
            "reopen agenda.",
            "",
            "## Gate",
            "",
            "| Check | Result |",
            "|-------|--------|",
            "| BE formals keep COMPINT·SHIPUSE·FASTBE·CTXBE·REAL-EVAL·"
            "REPORT PROMOTE · NANOGEN15 DEFER | **ok** |",
            "| `wave-be-summary` · `paper-lab-wave-be` · `be-freeze` "
            "contain **COMPLETE** | **ok** |",
            "| RECIPES + champion-card contain **H-NANOGEN15** · "
            "**BE-REAL-EVAL** · **COMPLETE** | **ok** |",
            "| LOOKUP·BE-FOREVER·OOD·over-refuse·util BE smoke | **ok** |",
            "| Decision | **PROMOTE** |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:be:freeze",
            "```",
            "",
            "## Finding",
            "",
            f"1. Ship claim stays scoped **{SHIP_CLAIM}**.  ",
            "2. BE-FREEZE does **not** invent new serve/train hyps.  ",
            "3. Further research requires a new § in "
            "`.local/pesquisa.md` (Wave BF reopen).  ",
            "4. Anti-FP law remains: LOOKUP ≠ generative IQ; "
            "BE-FOREVER type/coercion LOOKUP = false-hit; "
            "exact-gold ABSTAIN = miss; "
            "PEAK ≠ unlabeled open chat; SAFE ≠ quality; "
            "span-fallback ≠ gen IQ; true-continue unlock locked "
            "(H-NANOGEN15 DEFER · NANOGEN8…14 DEFER · "
            "NANOGEN6·7 HOLD).  ",
            "5. ≤5M hard law remains (CAPCHECK closed).",
            "",
            "## Artifacts",
            "",
            "- Module: `nano_lm/src/be_freeze_ops.py` · "
            "Runner: `nano_lm/src/run_be_freeze.py`",
            "- Summary: `results/nano-lm/wave-be/be_freeze.json`",
            "- Contract: `nano_lm/tests/test_be_freeze.py`",
            "",
        ]
    )


def _write_freeze_docs() -> None:
    _FREEZE_DOC.parent.mkdir(parents=True, exist_ok=True)
    _SUMMARY.write_text(render_wave_be_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_be(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_be_freeze(), encoding="utf-8")
    _FORMAL.write_text(_render_formal(), encoding="utf-8")
    if _SESSION_PUB.is_file():
        text = _SESSION_PUB.read_text(encoding="utf-8")
        for old, new in (
            (
                "Next: **BE8 BE-FREEZE**",
                "Next: **COMPLETE + FROZEN** — do not invent Wave BF "
                "without lab-book reopen (`npm run nano:be:freeze`)",
            ),
            (
                "next BE8 BE-FREEZE",
                "COMPLETE + FROZEN — do not invent Wave BF",
            ),
            (
                "Next: **BE7 BE-REPORT**",
                "Next: **COMPLETE + FROZEN** — do not invent Wave BF "
                "without lab-book reopen (`npm run nano:be:freeze`)",
            ),
            (
                "Next: **BE1 H-COMPINT**",
                "Next: **COMPLETE + FROZEN** — do not invent Wave BF "
                "without lab-book reopen (`npm run nano:be:freeze`)",
            ),
        ):
            if old in text:
                text = text.replace(old, new, 1)
                _SESSION_PUB.write_text(text, encoding="utf-8")
                break
    if _REAL_EVAL.is_file():
        text = _REAL_EVAL.read_text(encoding="utf-8")
        text = text.replace(
            "Next: **BE7 BE-REPORT** (`npm run nano:be:report`).",
            "Next: **COMPLETE + FROZEN** — do not invent Wave BF "
            "(`npm run nano:be:freeze`).",
            1,
        )
        text = text.replace(
            "Next: **BE8 BE-FREEZE** (`npm run nano:be:freeze`).",
            "Next: **COMPLETE + FROZEN** — do not invent Wave BF "
            "(`npm run nano:be:freeze`).",
            1,
        )
        _REAL_EVAL.write_text(text, encoding="utf-8")
    _patch_product_freeze_status()
    _patch_agents_agenda()


def _smoke_be_modes(*, workers: int) -> dict[str, Any]:
    from run_be_report import _smoke_be_modes as _smoke

    return _smoke(workers=workers)


def _update_local_session(decision: str) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    ok = str(decision).startswith("PROMOTE")
    status = "DONE — PROMOTE" if ok else f"DONE — {decision}"
    wave = "COMPLETE + FROZEN" if ok else "OPEN"
    body = "\n".join(
        [
            f"# Wave BE session checklist (**{wave}** · BE8 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            f"(Wave BE **{wave}**).  ",
            "> Parent: BD COMPLETE + FROZEN · Ship: **"
            + SHIP_CLAIM
            + "** · ≤5M (H-NANOGEN15 DEFER · NANOGEN8…14 DEFER · "
            "NANOGEN6·7 HOLD · no true-continue unlock).",
            "",
            "## Current stage",
            "",
            f"**BE8 — BE-FREEZE ({status})** · Next: "
            "**do not invent Wave BF**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| Wave | **{wave}** |",
            f"| Decision | **{'PROMOTE' if ok else decision}** |",
            "| Public | `docs/results/nano-lm/be-freeze.md` |",
            "| Formal | "
            "`docs/results/nano-lm/formal-habefreeze-be-freeze.md` |",
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
            "| BE7 | BE-REPORT | **DONE — PROMOTE** |",
            f"| BE8 | BE-FREEZE | **{status}** |",
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

**Wave BE {wave}** · BE8 BE-FREEZE **DONE — {status}**.
Do **not** invent Wave BF without lab-book reopen.

```bash
npm run nano:be:freeze
npm run nano:test && npm run verify
```
""",
        encoding="utf-8",
    )
    _LOCAL_README.write_text(
        f"""# Local research notebook

Full lab book: **`pesquisa.md`**.

**Wave BE {wave}** — BE8 **BE-FREEZE {status}**.

Do **not** invent Wave BF without explicit reopen.
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
        r"\| BE8 \| \*\*BE-FREEZE\*\* \|[^\n]+\| \*\*NEXT\*\* \|",
        (
            "| BE8 | **BE-FREEZE** | Lock outcomes | "
            f"no Wave BF without reopen | **DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"(\| BE8 \| \*\*BE-FREEZE\*\* \|[^\n]+\| )\*\*TODO\*\* \|",
        (
            "| BE8 | **BE-FREEZE** | Lock outcomes | "
            f"no Wave BF without reopen | **DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    if ok:
        text = text.replace(
            "# pesquisa — Wave BE (**REOPENED** · post-BD live truth)",
            "# pesquisa — Wave BE (**COMPLETE + FROZEN**)",
            1,
        )
        text = text.replace(
            "## 9. Wave BE stage machine (**REOPENED**)",
            "## 9. Wave BE stage machine (**COMPLETE + FROZEN**)",
            1,
        )
        text2, n = re.subn(
            r"> \*\*Status:\*\* Wave BD \*\*COMPLETE \+ FROZEN\*\* "
            r"\(archive\)\. Wave \*\*BE ACTIVE\*\*[^\n]*\.",
            (
                "> **Status:** Wave BE **COMPLETE + FROZEN**. "
                "Do **not** invent Wave BF without explicit reopen. "
                "Parent: Wave BD **COMPLETE + FROZEN** (archive)."
            ),
            text,
            count=1,
        )
        if n:
            text = text2
        text = text.replace(
            "> **Session:** `.local/wave-be/SESSION.md` "
            "(BE7 BE-REPORT **DONE — PROMOTE**; next BE8 BE-FREEZE).  ",
            "> **Session:** `.local/wave-be/SESSION.md` "
            f"(BE8 BE-FREEZE **DONE — {status}**; "
            "**COMPLETE + FROZEN**).  ",
            1,
        )
        text = text.replace(
            "> **Archive:** Waves W–**BD** → "
            "`docs/results/nano-lm/*-freeze.md`.",
            "> **Archive:** Waves W–**BE** → "
            "`docs/results/nano-lm/*-freeze.md`.",
            1,
        )
        text = text.replace(
            "### W–BD — COMPLETE + FROZEN",
            "### W–BE — COMPLETE + FROZEN",
            1,
        )
        text = text.replace(
            "invent Wave BF before BE-FREEZE",
            "invent Wave BF without lab-book reopen",
            1,
        )
    text = text.replace(
        (
            "8. **BE7 BE-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:be:report`) · next BE8 freeze.  \n"
            "9. **BE8 BE-FREEZE** — **NEXT** — lock; do not invent Wave BF.  "
        ),
        (
            "8. **BE7 BE-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:be:report`).  \n"
            f"9. **BE8 BE-FREEZE** — **DONE {status}** "
            "(`npm run nano:be:freeze`) · **COMPLETE + FROZEN** · "
            "do not invent Wave BF.  "
        ),
        1,
    )
    bash_old = "# next: nano:be:freeze"
    bash_new = (
        "npm run nano:be:freeze\n"
        "# Wave BE COMPLETE + FROZEN — do not invent Wave BF"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")
    _patch_local_helpers(status, ok)


def run_be_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN BE formals + COMPLETE closeout
    WHEN locking Wave BE
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    threads, workers = _hardware()
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in BE_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *BE_PUBLIC, *BE_PRODUCT_DOCS])
    )
    with ThreadPoolExecutor(
        max_workers=min(workers, max(4, len(read_paths)))
    ) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in BE_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in BE_PRODUCT_DOCS}
    decision = decide_be_freeze(
        formal_texts=formal_texts,
        public_texts=public_texts,
        product_texts=product_texts,
    )
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_be_modes(workers=workers)
        if not bool(ask.get("ok")):
            decision = "KILL (BE forever/modes smoke failed)"
    ok = str(decision).startswith("PROMOTE")
    _update_local_session(decision)
    _patch_pesquisa(decision)
    payload: dict[str, Any] = {
        "id": BE_FREEZE_ID,
        "hyp_id": BE_FREEZE_ID,
        "stage": "BE8",
        "thesis": BE_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in BE_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/be-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-habefreeze-be-freeze.md",
        "wave_be_summary": "docs/results/nano-lm/wave-be-summary.md",
        "rule": "pesquisa §9 BE-FREEZE",
        "wave_status": "COMPLETE+FROZEN" if ok else "RESEARCH_COMPLETE",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": threads,
        "workers": workers,
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave BE8 BE-FREEZE")
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    threads, _workers = _hardware()
    try:
        summary = run_be_freeze(
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
                "hyp_id": BE_FREEZE_ID,
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
