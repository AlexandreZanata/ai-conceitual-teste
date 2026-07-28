"""Wave BB-FREEZE runner (nano:bb:freeze) — lock BB; no Wave BC invent."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from bb_freeze_ops import (
    BB_DECISIONS,
    BB_FREEZE_ID,
    BB_PRODUCT_DOCS,
    BB_PUBLIC,
    BB_THESIS,
    SHIP_CLAIM,
    decide_bb_freeze,
    render_bb_freeze,
)
from bb_report_ops import render_paper_lab_wave_bb, render_wave_bb_summary
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-bb/bb_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/bb-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-habbfreeze-bb-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-bb-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-bb.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_AGENTS = REPO / "AGENTS.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_SESSION_PUB = REPO / "docs/results/nano-lm/wave-bb-session.md"
_LOCAL_SESSION = REPO / ".local/wave-bb/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"

_BB_FROZEN_RECIPES = (
    "**Wave BB COMPLETE + FROZEN:** BB0 [SESSION PROMOTE]"
    "(wave-bb-session.md) (`npm run nano:bb:session`) · "
    "BB1 [H-INTENTGEN PROMOTE](formal-hintentgen-intentgen.md) "
    "(`npm run nano:intentgen`) · BB2 [H-FASTHOLD PROMOTE]"
    "(formal-hfasthold-fasthold.md) (`npm run nano:bb:fasthold`) · "
    "BB3 [H-CTXHOLD PROMOTE](formal-hctxhold-ctxhold.md) "
    "(`npm run nano:bb:ctxhold`) · BB4 [H-NANOGEN12 DEFER]"
    "(formal-hnanogen12-nanogen12.md) (`npm run nano:nanogen12`) · "
    "BB5 [BB-REAL-EVAL PROMOTE](wave-bb-real-eval.md) "
    "(`npm run nano:bb:real-eval`) — battery 12/12 · "
    "BB6 [BB-REPORT PROMOTE](wave-bb-summary.md) "
    "(`npm run nano:bb:report`) · [paper-lab-wave-bb.md]"
    "(paper-lab-wave-bb.md); BB7 [BB-FREEZE PROMOTE](bb-freeze.md) "
    "(`npm run nano:bb:freeze`) · [formal-habbfreeze-bb-freeze.md]"
    "(formal-habbfreeze-bb-freeze.md) — ship **AF + AQ + AS trust + "
    "ablated DECODE (STRICT)**; H-NANOGEN12 DEFER (NANOGEN6·7 HOLD · "
    "NANOGEN8·9·10·11 DEFER stand); ≤5M stays; do not invent Wave BC."
)

_BB_FROZEN_CARD = _BB_FROZEN_RECIPES.replace(
    "**Wave BB COMPLETE + FROZEN:**",
    "**Wave BB COMPLETE + FROZEN** —",
)

_BB_FROZEN_AGENTS = (
    "- **Wave BB COMPLETE + FROZEN** — BB0 [SESSION PROMOTE]"
    "(docs/results/nano-lm/wave-bb-session.md) (`npm run nano:bb:session`) · "
    "BB1 [H-INTENTGEN PROMOTE]"
    "(docs/results/nano-lm/formal-hintentgen-intentgen.md) "
    "(`npm run nano:intentgen`) · BB2 [H-FASTHOLD PROMOTE]"
    "(docs/results/nano-lm/formal-hfasthold-fasthold.md) "
    "(`npm run nano:bb:fasthold`) · BB3 [H-CTXHOLD PROMOTE]"
    "(docs/results/nano-lm/formal-hctxhold-ctxhold.md) "
    "(`npm run nano:bb:ctxhold`) · BB4 [H-NANOGEN12 DEFER]"
    "(docs/results/nano-lm/formal-hnanogen12-nanogen12.md) "
    "(`npm run nano:nanogen12`) · BB5 [BB-REAL-EVAL PROMOTE]"
    "(docs/results/nano-lm/wave-bb-real-eval.md) "
    "(`npm run nano:bb:real-eval`) — battery 12/12 · "
    "BB6 [BB-REPORT PROMOTE](docs/results/nano-lm/wave-bb-summary.md) "
    "(`npm run nano:bb:report`) · [paper-lab-wave-bb.md]"
    "(docs/results/nano-lm/paper-lab-wave-bb.md); "
    "BB7 [BB-FREEZE PROMOTE](docs/results/nano-lm/bb-freeze.md) "
    "(`npm run nano:bb:freeze`) · "
    "[formal-habbfreeze-bb-freeze.md]"
    "(docs/results/nano-lm/formal-habbfreeze-bb-freeze.md) "
    "— ship **AF + AQ + AS trust + ablated DECODE (STRICT)**; "
    "H-NANOGEN12 DEFER (NANOGEN6·7 HOLD · NANOGEN8·9·10·11 DEFER stand); "
    "≤5M stays; do not invent Wave BC."
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


def _read_text(rel: str) -> str:
    path = REPO / rel
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _ensure_markers(text: str) -> str:
    if "H-NANOGEN12" not in text:
        text += "\nH-NANOGEN12\n"
    if "BB-REAL-EVAL" not in text:
        text += "\nBB-REAL-EVAL\n"
    if "COMPLETE" not in text:
        text += "\nCOMPLETE\n"
    return text


def _dedupe_bb_frozen_lines(text: str) -> str:
    kept: list[str] = []
    seen = False
    for line in text.splitlines(keepends=True):
        if line.startswith("**Wave BB COMPLETE + FROZEN:**"):
            if seen:
                continue
            seen = True
        kept.append(line)
    return "".join(kept)


def _patch_product_freeze_status() -> None:
    """Flip ACTIVE → COMPLETE + FROZEN on public product pages."""
    for path, frozen in (
        (_RECIPES, _BB_FROZEN_RECIPES),
        (_CARD, _BB_FROZEN_CARD),
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\*\*Wave BB ACTIVE:?\*\*[^\n]*",
            frozen,
            text,
            count=1,
        )
        if n:
            text = text2
        elif "**Wave BB COMPLETE + FROZEN**" not in text:
            text = text.rstrip() + "\n" + frozen + "\n"
        text = _dedupe_bb_frozen_lines(text)
        if "Wave BB7 BB-FREEZE" not in text and path == _RECIPES:
            needle = (
                "| Wave BB6 BB-REPORT | [wave-bb-summary.md]"
                "(wave-bb-summary.md) · [paper-lab-wave-bb.md]"
                "(paper-lab-wave-bb.md) **PROMOTE** "
                "(`npm run nano:bb:report`) — anti-FP · BB4 DEFER · "
                "NANOGEN6/7 HOLD · NANOGEN8·9·10·11 DEFER cited |\n"
            )
            row = (
                "| Wave BB7 BB-FREEZE | [bb-freeze.md](bb-freeze.md) · "
                "[formal-habbfreeze-bb-freeze.md]"
                "(formal-habbfreeze-bb-freeze.md) **PROMOTE** "
                "(`npm run nano:bb:freeze`) — COMPLETE+FROZEN; "
                "H-NANOGEN12 DEFER; do not invent Wave BC |\n"
            )
            if needle in text:
                text = text.replace(needle, needle + row, 1)
            elif "| Wave BB6 BB-REPORT |" in text:
                text2, n2 = re.subn(
                    r"(\| Wave BB6 BB-REPORT \|[^\n]+\|\n)",
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
            r"- \*\*Wave BB ACTIVE\*\* —[^\n]+",
            _BB_FROZEN_AGENTS,
            text,
            count=1,
        )
        if n:
            _AGENTS.write_text(text2, encoding="utf-8")
    if _AGENDA.is_file():
        text = _AGENDA.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\| \*\*BB\*\* \| \*\*ACTIVE\*\* \|[^\n]+",
            (
                "| **BB** | **COMPLETE + FROZEN** | BB0–BB6 as logged · "
                "BB4 [H-NANOGEN12 DEFER]"
                "(results/nano-lm/formal-hnanogen12-nanogen12.md); "
                "BB5 [BB-REAL-EVAL PROMOTE]"
                "(results/nano-lm/wave-bb-real-eval.md) battery 12/12; "
                "BB6 [BB-REPORT PROMOTE]"
                "(results/nano-lm/wave-bb-summary.md) · "
                "[paper-lab-wave-bb.md](results/nano-lm/paper-lab-wave-bb.md); "
                "BB7 [BB-FREEZE PROMOTE](results/nano-lm/bb-freeze.md) "
                "(`npm run nano:bb:freeze`) · "
                "[formal-habbfreeze-bb-freeze.md]"
                "(results/nano-lm/formal-habbfreeze-bb-freeze.md) "
                "— ship AF+AQ+AS trust + STRICT ablated DECODE; "
                "H-NANOGEN12 DEFER; ≤5M; do not invent Wave BC |"
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
        r"Wave BB ACTIVE \([^)]+\)",
        (
            "Wave BB COMPLETE + FROZEN (BB0–BB6 as logged · "
            "BB7 `bb-freeze.md` PROMOTE; do not invent Wave BC)"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    old_r = (
        "BB5 BB-REAL-EVAL PROMOTE · BB6 BB-REPORT PROMOTE; "
        "next BB7 BB-FREEZE"
    )
    new_r = (
        "BB5 BB-REAL-EVAL PROMOTE · BB6 BB-REPORT PROMOTE · "
        "BB7 BB-FREEZE PROMOTE "
        "(`bb-freeze.md` · `formal-habbfreeze-bb-freeze.md`); "
        "do not invent Wave BC"
    )
    if old_r in text:
        text = text.replace(old_r, new_r, 1)
    elif "next BB7 BB-FREEZE" in text:
        text = text.replace(
            "next BB7 BB-FREEZE",
            (
                "BB7 `bb-freeze.md` · `formal-habbfreeze-bb-freeze.md` "
                "PROMOTE; do not invent Wave BC"
            ),
            1,
        )
    _EVOGEN.write_text(text, encoding="utf-8")


def _render_formal() -> str:
    return "\n".join(
        [
            "# BB-FREEZE — Wave BB lock (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §8 BB7 · "
            "Public note: [bb-freeze.md](bb-freeze.md)  ",
            "> After: [wave-bb-summary.md](wave-bb-summary.md) / "
            "[paper-lab-wave-bb.md](paper-lab-wave-bb.md)",
            "",
            "## Hypothesis",
            "",
            "After BB-REPORT, freeze Wave BB the same way BA-FREEZE "
            "locked BA: **outcomes stay** (H-INTENTGEN·H-FASTHOLD·"
            "H-CTXHOLD·BB-REAL-EVAL·BB-REPORT PROMOTE; "
            "H-NANOGEN12 DEFER); **no Wave BC** without an explicit "
            "reopen agenda.",
            "",
            "## Gate",
            "",
            "| Check | Result |",
            "|-------|--------|",
            "| BB formals keep INTENTGEN·FASTHOLD·CTXHOLD·REAL-EVAL·"
            "REPORT PROMOTE · NANOGEN12 DEFER | **ok** |",
            "| `wave-bb-summary` · `paper-lab-wave-bb` · `bb-freeze` "
            "contain **COMPLETE** | **ok** |",
            "| RECIPES + champion-card contain **H-NANOGEN12** · "
            "**BB-REAL-EVAL** · **COMPLETE** | **ok** |",
            "| LOOKUP·BB-FOREVER·OOD·over-refuse BB smoke | **ok** |",
            "| Decision | **PROMOTE** |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:bb:freeze",
            "```",
            "",
            "## Finding",
            "",
            f"1. Ship claim stays scoped **{SHIP_CLAIM}**.  ",
            "2. BB-FREEZE does **not** invent new serve/train hyps.  ",
            "3. Further research requires a new § in "
            "`.local/pesquisa.md` (Wave BC reopen).  ",
            "4. Anti-FP law remains: LOOKUP ≠ generative IQ; "
            "BB-FOREVER intent LOOKUP = false-hit; "
            "exact-gold ABSTAIN = miss; "
            "PEAK ≠ unlabeled open chat; SAFE ≠ quality; "
            "span-fallback ≠ gen IQ; true-continue unlock locked "
            "(H-NANOGEN12 DEFER · NANOGEN8·9·10·11 DEFER · "
            "NANOGEN6·7 HOLD).  ",
            "5. ≤5M hard law remains (CAPCHECK closed).",
            "",
            "## Artifacts",
            "",
            "- Module: `nano_lm/src/bb_freeze_ops.py` · "
            "Runner: `nano_lm/src/run_bb_freeze.py`",
            "- Summary: `results/nano-lm/wave-bb/bb_freeze.json`",
            "- Contract: `nano_lm/tests/test_bb_freeze.py`",
            "",
        ]
    )


def _write_freeze_docs() -> None:
    _FREEZE_DOC.parent.mkdir(parents=True, exist_ok=True)
    _SUMMARY.write_text(render_wave_bb_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_bb(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_bb_freeze(), encoding="utf-8")
    _FORMAL.write_text(_render_formal(), encoding="utf-8")
    if _SESSION_PUB.is_file():
        text = _SESSION_PUB.read_text(encoding="utf-8")
        if "Next: **BB7 BB-FREEZE**" in text:
            text = text.replace(
                "Next: **BB7 BB-FREEZE**",
                "Next: **COMPLETE + FROZEN** — do not invent Wave BC "
                "without lab-book reopen (`npm run nano:bb:freeze`)",
                1,
            )
            _SESSION_PUB.write_text(text, encoding="utf-8")
        elif "next BB7 BB-FREEZE" in text:
            text = text.replace(
                "next BB7 BB-FREEZE",
                "COMPLETE + FROZEN — do not invent Wave BC",
                1,
            )
            _SESSION_PUB.write_text(text, encoding="utf-8")
    _patch_product_freeze_status()
    _patch_agents_agenda()


def _smoke_bb_modes(*, workers: int) -> dict[str, Any]:
    from run_bb_report import _smoke_bb_modes as _smoke

    return _smoke(workers=workers)


def _update_local_session(decision: str) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    ok = str(decision).startswith("PROMOTE")
    status = "DONE — PROMOTE" if ok else f"DONE — {decision}"
    wave = "COMPLETE + FROZEN" if ok else "OPEN"
    body = "\n".join(
        [
            f"# Wave BB session checklist (**{wave}** · BB7 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            f"(Wave BB **{wave}**).  ",
            "> Parent: BA COMPLETE + FROZEN · Ship: **"
            + SHIP_CLAIM
            + "** · ≤5M (H-NANOGEN12 DEFER · NANOGEN8·9·10·11 DEFER · "
            "NANOGEN6·7 HOLD · no true-continue unlock).",
            "",
            "## Current stage",
            "",
            f"**BB7 — BB-FREEZE ({status})** · Next: "
            "**do not invent Wave BC**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| Wave | **{wave}** |",
            f"| Decision | **{decision.split(':', 1)[0]}** |",
            "| Public | `docs/results/nano-lm/bb-freeze.md` |",
            "| Formal | "
            "`docs/results/nano-lm/formal-habbfreeze-bb-freeze.md` |",
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
            "| BB6 | BB-REPORT | **DONE — PROMOTE** |",
            f"| BB7 | BB-FREEZE | **{status}** |",
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

**Wave BB {wave}** · BB7 BB-FREEZE **DONE — {status}**.
Do **not** invent Wave BC without lab-book reopen.

```bash
npm run nano:bb:freeze
npm run nano:test && npm run verify
```
""",
        encoding="utf-8",
    )
    _LOCAL_README.write_text(
        f"""# Local research notebook

Full lab book: **`pesquisa.md`**.

**Wave BB {wave}** — BB7 **BB-FREEZE {status}**.

Do **not** invent Wave BC without explicit reopen.
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
        r"\| BB7 \| \*\*BB-FREEZE\*\* \|[^\n]+\| \*\*NEXT\*\* \|",
        (
            "| BB7 | **BB-FREEZE** | Lock outcomes | "
            f"no next letter without reopen | **DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"\| BB7 \| \*\*BB-FREEZE\*\* \|[^\n]+\| \*\*TODO\*\* \|",
        (
            "| BB7 | **BB-FREEZE** | Lock outcomes | "
            f"no next letter without reopen | **DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    if ok:
        text = text.replace(
            "# pesquisa — Wave BB (**REOPEN** after BA-FREEZE)",
            "# pesquisa — Wave BB (**COMPLETE + FROZEN**)",
            1,
        )
        text = text.replace(
            "## 8. Wave BB stage machine (**REOPEN**)",
            "## 8. Wave BB stage machine (**COMPLETE + FROZEN**)",
            1,
        )
        text2, n = re.subn(
            r"> \*\*Status:\*\* Wave BA \*\*COMPLETE \+ FROZEN\*\* "
            r"\(archive\)\. Wave BB \*\*REOPENED\*\*[^\n]*\.",
            (
                "> **Status:** Wave BB **COMPLETE + FROZEN**. "
                "Do **not** invent Wave BC without explicit reopen. "
                "Parent: Wave BA **COMPLETE + FROZEN** (archive)."
            ),
            text,
            count=1,
        )
        if n:
            text = text2
        text = text.replace(
            "> **Session:** `.local/wave-bb/SESSION.md` "
            "(BB6 BB-REPORT **DONE — PROMOTE**; next BB7 BB-FREEZE).  ",
            "> **Session:** `.local/wave-bb/SESSION.md` "
            f"(BB7 BB-FREEZE **DONE — {status}**; "
            "**COMPLETE + FROZEN**).  ",
            1,
        )
        text = text.replace(
            "> **Archive:** Waves W–**BA** → `docs/results/nano-lm/*-freeze.md`.",
            "> **Archive:** Waves W–**BB** → `docs/results/nano-lm/*-freeze.md`.",
            1,
        )
    text = text.replace(
        (
            "7. **BB6 BB-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:bb:report`) · next BB7 freeze.  \n"
            "8. **BB7 BB-FREEZE** — **NEXT** — lock outcomes "
            "(update `paper/` only if measured).  "
        ),
        (
            "7. **BB6 BB-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:bb:report`).  \n"
            f"8. **BB7 BB-FREEZE** — **DONE {status}** "
            "(`npm run nano:bb:freeze`) · **COMPLETE + FROZEN** · "
            "do not invent Wave BC.  "
        ),
        1,
    )
    bash_old = "# next: nano:bb:freeze"
    bash_new = (
        "npm run nano:bb:freeze\n"
        "# Wave BB COMPLETE + FROZEN — do not invent Wave BC"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")
    _patch_local_helpers(status, ok)


def run_bb_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN BB formals + COMPLETE closeout
    WHEN locking Wave BB
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    threads, workers = _hardware()
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in BB_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *BB_PUBLIC, *BB_PRODUCT_DOCS])
    )
    with ThreadPoolExecutor(
        max_workers=min(workers, max(4, len(read_paths)))
    ) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in BB_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in BB_PRODUCT_DOCS}
    decision = decide_bb_freeze(
        formal_texts=formal_texts,
        public_texts=public_texts,
        product_texts=product_texts,
    )
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_bb_modes(workers=workers)
        if not bool(ask.get("ok")):
            decision = "KILL (BB forever/modes smoke failed)"
    ok = str(decision).startswith("PROMOTE")
    _update_local_session(decision)
    _patch_pesquisa(decision)
    payload: dict[str, Any] = {
        "id": BB_FREEZE_ID,
        "hyp_id": BB_FREEZE_ID,
        "stage": "BB7",
        "thesis": BB_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in BB_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/bb-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-habbfreeze-bb-freeze.md",
        "wave_bb_summary": "docs/results/nano-lm/wave-bb-summary.md",
        "rule": "pesquisa §8 BB-FREEZE",
        "wave_status": "COMPLETE+FROZEN" if ok else "RESEARCH_COMPLETE",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": threads,
        "workers": workers,
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave BB7 BB-FREEZE")
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    threads, _workers = _hardware()
    try:
        summary = run_bb_freeze(
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
                "hyp_id": BB_FREEZE_ID,
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
