"""Wave BC-FREEZE runner (nano:bc:freeze) — lock BC; no Wave BD invent."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from bc_freeze_ops import (
    BC_DECISIONS,
    BC_FREEZE_ID,
    BC_PRODUCT_DOCS,
    BC_PUBLIC,
    BC_THESIS,
    SHIP_CLAIM,
    decide_bc_freeze,
    render_bc_freeze,
)
from bc_report_ops import render_paper_lab_wave_bc, render_wave_bc_summary
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-bc/bc_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/bc-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-habcfreeze-bc-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-bc-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-bc.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_AGENTS = REPO / "AGENTS.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_SESSION_PUB = REPO / "docs/results/nano-lm/wave-bc-session.md"
_LOCAL_SESSION = REPO / ".local/wave-bc/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"

_BC_FROZEN_RECIPES = (
    "**Wave BC COMPLETE + FROZEN:** BC0 [SESSION PROMOTE]"
    "(wave-bc-session.md) (`npm run nano:bc:session`) · "
    "BC1 [H-OPSFAM PROMOTE](formal-hopsfam-opsfam.md) "
    "(`npm run nano:opsfam`) · BC2 [H-FASTLIFT PROMOTE]"
    "(formal-hfastlift-bc2.md) (`npm run nano:bc:fastlift`) · "
    "BC3 [H-CTXLIFT2 PROMOTE](formal-hctxlift2-ctxlift2.md) "
    "(`npm run nano:bc:ctxlift2`) · BC4 [H-NANOGEN13 DEFER]"
    "(formal-hnanogen13-nanogen13.md) (`npm run nano:nanogen13`) · "
    "BC5 [BC-REAL-EVAL PROMOTE](wave-bc-real-eval.md) "
    "(`npm run nano:bc:real-eval`) — battery 13/13 · "
    "BC6 [BC-REPORT PROMOTE](wave-bc-summary.md) "
    "(`npm run nano:bc:report`) · [paper-lab-wave-bc.md]"
    "(paper-lab-wave-bc.md); BC7 [BC-FREEZE PROMOTE](bc-freeze.md) "
    "(`npm run nano:bc:freeze`) · [formal-habcfreeze-bc-freeze.md]"
    "(formal-habcfreeze-bc-freeze.md) — ship **AF + AQ + AS trust + "
    "ablated DECODE (STRICT)**; H-NANOGEN13 DEFER (NANOGEN6·7 HOLD · "
    "NANOGEN8·9·10·11·12 DEFER stand); ≤5M stays; do not invent Wave BD."
)

_BC_FROZEN_CARD = _BC_FROZEN_RECIPES.replace(
    "**Wave BC COMPLETE + FROZEN:**",
    "**Wave BC COMPLETE + FROZEN** —",
)

_BC_FROZEN_AGENTS = (
    "- **Wave BC COMPLETE + FROZEN** — BC0 [SESSION PROMOTE]"
    "(docs/results/nano-lm/wave-bc-session.md) (`npm run nano:bc:session`) · "
    "BC1 [H-OPSFAM PROMOTE]"
    "(docs/results/nano-lm/formal-hopsfam-opsfam.md) "
    "(`npm run nano:opsfam`) · BC2 [H-FASTLIFT PROMOTE]"
    "(docs/results/nano-lm/formal-hfastlift-bc2.md) "
    "(`npm run nano:bc:fastlift`) · BC3 [H-CTXLIFT2 PROMOTE]"
    "(docs/results/nano-lm/formal-hctxlift2-ctxlift2.md) "
    "(`npm run nano:bc:ctxlift2`) · BC4 [H-NANOGEN13 DEFER]"
    "(docs/results/nano-lm/formal-hnanogen13-nanogen13.md) "
    "(`npm run nano:nanogen13`) · BC5 [BC-REAL-EVAL PROMOTE]"
    "(docs/results/nano-lm/wave-bc-real-eval.md) "
    "(`npm run nano:bc:real-eval`) — battery 13/13 · "
    "BC6 [BC-REPORT PROMOTE](docs/results/nano-lm/wave-bc-summary.md) "
    "(`npm run nano:bc:report`) · [paper-lab-wave-bc.md]"
    "(docs/results/nano-lm/paper-lab-wave-bc.md); "
    "BC7 [BC-FREEZE PROMOTE](docs/results/nano-lm/bc-freeze.md) "
    "(`npm run nano:bc:freeze`) · "
    "[formal-habcfreeze-bc-freeze.md]"
    "(docs/results/nano-lm/formal-habcfreeze-bc-freeze.md) "
    "— ship **AF + AQ + AS trust + ablated DECODE (STRICT)**; "
    "H-NANOGEN13 DEFER (NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER stand); "
    "≤5M stays; do not invent Wave BD."
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
    if "H-NANOGEN13" not in text:
        text += "\nH-NANOGEN13\n"
    if "BC-REAL-EVAL" not in text:
        text += "\nBC-REAL-EVAL\n"
    if "COMPLETE" not in text:
        text += "\nCOMPLETE\n"
    return text


def _dedupe_bc_frozen_lines(text: str) -> str:
    kept: list[str] = []
    seen = False
    for line in text.splitlines(keepends=True):
        if line.startswith("**Wave BC COMPLETE + FROZEN:**"):
            if seen:
                continue
            seen = True
        kept.append(line)
    return "".join(kept)


def _patch_product_freeze_status() -> None:
    """Flip ACTIVE → COMPLETE + FROZEN on public product pages."""
    for path, frozen in (
        (_RECIPES, _BC_FROZEN_RECIPES),
        (_CARD, _BC_FROZEN_CARD),
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\*\*Wave BC ACTIVE:?\*\*[^\n]*",
            frozen,
            text,
            count=1,
        )
        if n:
            text = text2
        elif "**Wave BC COMPLETE + FROZEN**" not in text:
            text = text.rstrip() + "\n" + frozen + "\n"
        text = _dedupe_bc_frozen_lines(text)
        if "Wave BC7 BC-FREEZE" not in text and path == _RECIPES:
            needle = (
                "| Wave BC6 BC-REPORT | [wave-bc-summary.md]"
                "(wave-bc-summary.md) · [paper-lab-wave-bc.md]"
                "(paper-lab-wave-bc.md) **PROMOTE** "
                "(`npm run nano:bc:report`) — anti-FP · BC4 DEFER · "
                "NANOGEN6/7 HOLD · NANOGEN8·9·10·11·12 DEFER cited |\n"
            )
            row = (
                "| Wave BC7 BC-FREEZE | [bc-freeze.md](bc-freeze.md) · "
                "[formal-habcfreeze-bc-freeze.md]"
                "(formal-habcfreeze-bc-freeze.md) **PROMOTE** "
                "(`npm run nano:bc:freeze`) — COMPLETE+FROZEN; "
                "H-NANOGEN13 DEFER; do not invent Wave BD |\n"
            )
            if needle in text:
                text = text.replace(needle, needle + row, 1)
            elif "| Wave BC6 BC-REPORT |" in text:
                text2, n2 = re.subn(
                    r"(\| Wave BC6 BC-REPORT \|[^\n]+\|\n)",
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
            r"- \*\*Wave BC ACTIVE\*\* —[^\n]+",
            _BC_FROZEN_AGENTS,
            text,
            count=1,
        )
        if n:
            _AGENTS.write_text(text2, encoding="utf-8")
    if _AGENDA.is_file():
        text = _AGENDA.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\| \*\*BC\*\* \| \*\*ACTIVE\*\* \|[^\n]+",
            (
                "| **BC** | **COMPLETE + FROZEN** | BC0–BC6 as logged · "
                "BC4 [H-NANOGEN13 DEFER]"
                "(results/nano-lm/formal-hnanogen13-nanogen13.md); "
                "BC5 [BC-REAL-EVAL PROMOTE]"
                "(results/nano-lm/wave-bc-real-eval.md) battery 13/13; "
                "BC6 [BC-REPORT PROMOTE]"
                "(results/nano-lm/wave-bc-summary.md) · "
                "[paper-lab-wave-bc.md](results/nano-lm/paper-lab-wave-bc.md); "
                "BC7 [BC-FREEZE PROMOTE](results/nano-lm/bc-freeze.md) "
                "(`npm run nano:bc:freeze`) · "
                "[formal-habcfreeze-bc-freeze.md]"
                "(results/nano-lm/formal-habcfreeze-bc-freeze.md) "
                "— ship AF+AQ+AS trust + STRICT ablated DECODE; "
                "H-NANOGEN13 DEFER; ≤5M; do not invent Wave BD |"
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
        r"Wave BC ACTIVE \([^)]+\)",
        (
            "Wave BC COMPLETE + FROZEN (BC0–BC6 as logged · "
            "BC7 `bc-freeze.md` PROMOTE; do not invent Wave BD)"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    old_r = (
        "BC5 BC-REAL-EVAL PROMOTE · BC6 BC-REPORT PROMOTE; "
        "next BC7 BC-FREEZE"
    )
    new_r = (
        "BC5 BC-REAL-EVAL PROMOTE · BC6 BC-REPORT PROMOTE · "
        "BC7 BC-FREEZE PROMOTE "
        "(`bc-freeze.md` · `formal-habcfreeze-bc-freeze.md`); "
        "do not invent Wave BD"
    )
    if old_r in text:
        text = text.replace(old_r, new_r, 1)
    elif "next BC7 BC-FREEZE" in text:
        text = text.replace(
            "next BC7 BC-FREEZE",
            (
                "BC7 `bc-freeze.md` · `formal-habcfreeze-bc-freeze.md` "
                "PROMOTE; do not invent Wave BD"
            ),
            1,
        )
    _EVOGEN.write_text(text, encoding="utf-8")


def _render_formal() -> str:
    return "\n".join(
        [
            "# BC-FREEZE — Wave BC lock (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §9 BC7 · "
            "Public note: [bc-freeze.md](bc-freeze.md)  ",
            "> After: [wave-bc-summary.md](wave-bc-summary.md) / "
            "[paper-lab-wave-bc.md](paper-lab-wave-bc.md)",
            "",
            "## Hypothesis",
            "",
            "After BC-REPORT, freeze Wave BC the same way BB-FREEZE "
            "locked BB: **outcomes stay** (H-OPSFAM·H-FASTLIFT·"
            "H-CTXLIFT2·BC-REAL-EVAL·BC-REPORT PROMOTE; "
            "H-NANOGEN13 DEFER); **no Wave BD** without an explicit "
            "reopen agenda.",
            "",
            "## Gate",
            "",
            "| Check | Result |",
            "|-------|--------|",
            "| BC formals keep OPSFAM·FASTLIFT·CTXLIFT2·REAL-EVAL·"
            "REPORT PROMOTE · NANOGEN13 DEFER | **ok** |",
            "| `wave-bc-summary` · `paper-lab-wave-bc` · `bc-freeze` "
            "contain **COMPLETE** | **ok** |",
            "| RECIPES + champion-card contain **H-NANOGEN13** · "
            "**BC-REAL-EVAL** · **COMPLETE** | **ok** |",
            "| LOOKUP·BC-FOREVER·OOD·over-refuse BC smoke | **ok** |",
            "| Decision | **PROMOTE** |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:bc:freeze",
            "```",
            "",
            "## Finding",
            "",
            f"1. Ship claim stays scoped **{SHIP_CLAIM}**.  ",
            "2. BC-FREEZE does **not** invent new serve/train hyps.  ",
            "3. Further research requires a new § in "
            "`.local/pesquisa.md` (Wave BD reopen).  ",
            "4. Anti-FP law remains: LOOKUP ≠ generative IQ; "
            "BC-FOREVER intent LOOKUP = false-hit; "
            "exact-gold ABSTAIN = miss; "
            "PEAK ≠ unlabeled open chat; SAFE ≠ quality; "
            "span-fallback ≠ gen IQ; true-continue unlock locked "
            "(H-NANOGEN13 DEFER · NANOGEN8·9·10·11·12 DEFER · "
            "NANOGEN6·7 HOLD).  ",
            "5. ≤5M hard law remains (CAPCHECK closed).",
            "",
            "## Artifacts",
            "",
            "- Module: `nano_lm/src/bc_freeze_ops.py` · "
            "Runner: `nano_lm/src/run_bc_freeze.py`",
            "- Summary: `results/nano-lm/wave-bc/bc_freeze.json`",
            "- Contract: `nano_lm/tests/test_bc_freeze.py`",
            "",
        ]
    )


def _write_freeze_docs() -> None:
    _FREEZE_DOC.parent.mkdir(parents=True, exist_ok=True)
    _SUMMARY.write_text(render_wave_bc_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_bc(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_bc_freeze(), encoding="utf-8")
    _FORMAL.write_text(_render_formal(), encoding="utf-8")
    if _SESSION_PUB.is_file():
        text = _SESSION_PUB.read_text(encoding="utf-8")
        if "Next: **BC7 BC-FREEZE**" in text:
            text = text.replace(
                "Next: **BC7 BC-FREEZE**",
                "Next: **COMPLETE + FROZEN** — do not invent Wave BD "
                "without lab-book reopen (`npm run nano:bc:freeze`)",
                1,
            )
            _SESSION_PUB.write_text(text, encoding="utf-8")
        elif "next BC7 BC-FREEZE" in text:
            text = text.replace(
                "next BC7 BC-FREEZE",
                "COMPLETE + FROZEN — do not invent Wave BD",
                1,
            )
            _SESSION_PUB.write_text(text, encoding="utf-8")
        elif "Next: **BC6 BC-REPORT**" in text:
            text = text.replace(
                "Next: **BC6 BC-REPORT**",
                "Next: **COMPLETE + FROZEN** — do not invent Wave BD "
                "without lab-book reopen (`npm run nano:bc:freeze`)",
                1,
            )
            _SESSION_PUB.write_text(text, encoding="utf-8")
    _patch_product_freeze_status()
    _patch_agents_agenda()


def _smoke_bc_modes(*, workers: int) -> dict[str, Any]:
    from run_bc_report import _smoke_bc_modes as _smoke

    return _smoke(workers=workers)


def _update_local_session(decision: str) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    ok = str(decision).startswith("PROMOTE")
    status = "DONE — PROMOTE" if ok else f"DONE — {decision}"
    wave = "COMPLETE + FROZEN" if ok else "OPEN"
    body = "\n".join(
        [
            f"# Wave BC session checklist (**{wave}** · BC7 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            f"(Wave BC **{wave}**).  ",
            "> Parent: BB COMPLETE + FROZEN · Ship: **"
            + SHIP_CLAIM
            + "** · ≤5M (H-NANOGEN13 DEFER · NANOGEN8·9·10·11·12 DEFER · "
            "NANOGEN6·7 HOLD · no true-continue unlock).",
            "",
            "## Current stage",
            "",
            f"**BC7 — BC-FREEZE ({status})** · Next: "
            "**do not invent Wave BD**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| Wave | **{wave}** |",
            f"| Decision | **{decision.split(':', 1)[0]}** |",
            "| Public | `docs/results/nano-lm/bc-freeze.md` |",
            "| Formal | "
            "`docs/results/nano-lm/formal-habcfreeze-bc-freeze.md` |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| BC0 | SESSION | **DONE — PROMOTE** |",
            "| BC1 | H-OPSFAM | **DONE — PROMOTE** |",
            "| BC2 | H-FASTLIFT | **DONE — PROMOTE** |",
            "| BC3 | H-CTXLIFT2 | **DONE — PROMOTE** |",
            "| BC4 | H-NANOGEN13 | **DONE — DEFER** |",
            "| BC5 | BC-REAL-EVAL | **DONE — PROMOTE** |",
            "| BC6 | BC-REPORT | **DONE — PROMOTE** |",
            f"| BC7 | BC-FREEZE | **{status}** |",
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

**Wave BC {wave}** · BC7 BC-FREEZE **DONE — {status}**.
Do **not** invent Wave BD without lab-book reopen.

```bash
npm run nano:bc:freeze
npm run nano:test && npm run verify
```
""",
        encoding="utf-8",
    )
    _LOCAL_README.write_text(
        f"""# Local research notebook

Full lab book: **`pesquisa.md`**.

**Wave BC {wave}** — BC7 **BC-FREEZE {status}**.

Do **not** invent Wave BD without explicit reopen.
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
        r"\| BC7 \| \*\*BC-FREEZE\*\* \|[^\n]+\| \*\*NEXT\*\* \|",
        (
            "| BC7 | **BC-FREEZE** | Lock outcomes | "
            f"no next letter without reopen | **DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"(\| BC7 \| \*\*BC-FREEZE\*\* \|[^\n]+\| )pending \|",
        (
            "| BC7 | **BC-FREEZE** | Lock outcomes | "
            f"no next letter without reopen | **DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    if ok:
        text = text.replace(
            "# pesquisa — Wave BC (**ACTIVE** · reopened 2026-07-28)",
            "# pesquisa — Wave BC (**COMPLETE + FROZEN**)",
            1,
        )
        text = text.replace(
            "## 9. Wave BC stage machine (**ACTIVE**)",
            "## 9. Wave BC stage machine (**COMPLETE + FROZEN**)",
            1,
        )
        text2, n = re.subn(
            r"> \*\*Status:\*\* Wave BC \*\*ACTIVE\*\*[^\n]*\.",
            (
                "> **Status:** Wave BC **COMPLETE + FROZEN**. "
                "Do **not** invent Wave BD without explicit reopen. "
                "Parent: Wave BB **COMPLETE + FROZEN** (archive)."
            ),
            text,
            count=1,
        )
        if n:
            text = text2
        text = text.replace(
            "> **Session:** `.local/wave-bc/SESSION.md` "
            "(BC6 BC-REPORT **DONE — PROMOTE**; next BC7 BC-FREEZE).  ",
            "> **Session:** `.local/wave-bc/SESSION.md` "
            f"(BC7 BC-FREEZE **DONE — {status}**; "
            "**COMPLETE + FROZEN**).  ",
            1,
        )
        text = text.replace(
            "> **Archive:** Waves W–**BB** → `docs/results/nano-lm/*-freeze.md`.",
            "> **Archive:** Waves W–**BC** → `docs/results/nano-lm/*-freeze.md`.",
            1,
        )
    text = text.replace(
        (
            "7. **BC6 BC-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:bc:report`) · next BC7 freeze.  \n"
            "8. **BC7 BC-FREEZE** — **NEXT** — lock outcomes.  "
        ),
        (
            "7. **BC6 BC-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:bc:report`).  \n"
            f"8. **BC7 BC-FREEZE** — **DONE {status}** "
            "(`npm run nano:bc:freeze`) · **COMPLETE + FROZEN** · "
            "do not invent Wave BD.  "
        ),
        1,
    )
    bash_old = "# next: nano:bc:freeze"
    bash_new = (
        "npm run nano:bc:freeze\n"
        "# Wave BC COMPLETE + FROZEN — do not invent Wave BD"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")
    _patch_local_helpers(status, ok)


def run_bc_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN BC formals + COMPLETE closeout
    WHEN locking Wave BC
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    threads, workers = _hardware()
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in BC_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *BC_PUBLIC, *BC_PRODUCT_DOCS])
    )
    with ThreadPoolExecutor(
        max_workers=min(workers, max(4, len(read_paths)))
    ) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in BC_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in BC_PRODUCT_DOCS}
    decision = decide_bc_freeze(
        formal_texts=formal_texts,
        public_texts=public_texts,
        product_texts=product_texts,
    )
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_bc_modes(workers=workers)
        if not bool(ask.get("ok")):
            decision = "KILL (BC forever/modes smoke failed)"
    ok = str(decision).startswith("PROMOTE")
    _update_local_session(decision)
    _patch_pesquisa(decision)
    payload: dict[str, Any] = {
        "id": BC_FREEZE_ID,
        "hyp_id": BC_FREEZE_ID,
        "stage": "BC7",
        "thesis": BC_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in BC_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/bc-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-habcfreeze-bc-freeze.md",
        "wave_bc_summary": "docs/results/nano-lm/wave-bc-summary.md",
        "rule": "pesquisa §9 BC-FREEZE",
        "wave_status": "COMPLETE+FROZEN" if ok else "RESEARCH_COMPLETE",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": threads,
        "workers": workers,
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave BC7 BC-FREEZE")
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    threads, _workers = _hardware()
    try:
        summary = run_bc_freeze(
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
                "hyp_id": BC_FREEZE_ID,
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
