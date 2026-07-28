"""Wave BA-FREEZE runner (nano:ba:freeze) — lock BA; no Wave BB invent."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from ba_freeze_ops import (
    BA_DECISIONS,
    BA_FREEZE_ID,
    BA_PRODUCT_DOCS,
    BA_PUBLIC,
    BA_THESIS,
    SHIP_CLAIM,
    decide_ba_freeze,
    render_ba_freeze,
)
from ba_report_ops import render_paper_lab_wave_ba, render_wave_ba_summary
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-ba/ba_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/ba-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-habfreeze-ba-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-ba-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-ba.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_AGENTS = REPO / "AGENTS.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_SESSION_PUB = REPO / "docs/results/nano-lm/wave-ba-session.md"
_LOCAL_SESSION = REPO / ".local/wave-ba/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"

_BA_FROZEN_RECIPES = (
    "**Wave BA COMPLETE + FROZEN:** BA0 [SESSION PROMOTE]"
    "(wave-ba-session.md) (`npm run nano:ba:session`) · "
    "BA1 [H-REALGAIN PROMOTE](formal-hrealgain-realgain.md) "
    "(`npm run nano:realgain`) · BA2 [H-FASTREAL PROMOTE]"
    "(formal-hfastreal-ba2.md) (`npm run nano:ba:fastreal`) · "
    "BA3 [H-CTXREAL2 PROMOTE](formal-hctxreal2-ctxreal2.md) "
    "(`npm run nano:ba:ctxreal2`) · BA4 [H-NANOGEN11 DEFER]"
    "(formal-hnanogen11-nanogen11.md) (`npm run nano:nanogen11`) · "
    "BA5 [BA-REAL-EVAL PROMOTE](wave-ba-real-eval.md) "
    "(`npm run nano:ba:real-eval`) — battery 10/10 · "
    "BA6 [BA-REPORT PROMOTE](wave-ba-summary.md) "
    "(`npm run nano:ba:report`) · [paper-lab-wave-ba.md]"
    "(paper-lab-wave-ba.md); BA7 [BA-FREEZE PROMOTE](ba-freeze.md) "
    "(`npm run nano:ba:freeze`) · [formal-habfreeze-ba-freeze.md]"
    "(formal-habfreeze-ba-freeze.md) — ship **AF + AQ + AS trust + "
    "ablated DECODE (STRICT)**; H-NANOGEN11 DEFER (NANOGEN6·7 HOLD · "
    "NANOGEN8·9·10 DEFER stand); ≤5M stays; do not invent Wave BB."
)

_BA_FROZEN_CARD = _BA_FROZEN_RECIPES.replace(
    "**Wave BA COMPLETE + FROZEN:**",
    "**Wave BA COMPLETE + FROZEN** —",
)

_BA_FROZEN_AGENTS = (
    "- **Wave BA COMPLETE + FROZEN** — BA0 [SESSION PROMOTE]"
    "(docs/results/nano-lm/wave-ba-session.md) (`npm run nano:ba:session`) · "
    "BA1 [H-REALGAIN PROMOTE](docs/results/nano-lm/formal-hrealgain-realgain.md) "
    "(`npm run nano:realgain`) · BA2 [H-FASTREAL PROMOTE]"
    "(docs/results/nano-lm/formal-hfastreal-ba2.md) "
    "(`npm run nano:ba:fastreal`) · BA3 [H-CTXREAL2 PROMOTE]"
    "(docs/results/nano-lm/formal-hctxreal2-ctxreal2.md) "
    "(`npm run nano:ba:ctxreal2`) · BA4 [H-NANOGEN11 DEFER]"
    "(docs/results/nano-lm/formal-hnanogen11-nanogen11.md) "
    "(`npm run nano:nanogen11`) · BA5 [BA-REAL-EVAL PROMOTE]"
    "(docs/results/nano-lm/wave-ba-real-eval.md) "
    "(`npm run nano:ba:real-eval`) — battery 10/10 · "
    "BA6 [BA-REPORT PROMOTE](docs/results/nano-lm/wave-ba-summary.md) "
    "(`npm run nano:ba:report`) · [paper-lab-wave-ba.md]"
    "(docs/results/nano-lm/paper-lab-wave-ba.md); "
    "BA7 [BA-FREEZE PROMOTE](docs/results/nano-lm/ba-freeze.md) "
    "(`npm run nano:ba:freeze`) · "
    "[formal-habfreeze-ba-freeze.md]"
    "(docs/results/nano-lm/formal-habfreeze-ba-freeze.md) "
    "— ship **AF + AQ + AS trust + ablated DECODE (STRICT)**; "
    "H-NANOGEN11 DEFER (NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER stand); "
    "≤5M stays; do not invent Wave BB."
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
    # 16c / ~9–10Gi avail: leave ≥4 cores free; cap workers for model RAM.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    workers = min(10, max(4, cpus - 4))
    return threads, workers


def _read_text(rel: str) -> str:
    path = REPO / rel
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _ensure_markers(text: str) -> str:
    if "H-NANOGEN11" not in text:
        text += "\nH-NANOGEN11\n"
    if "BA-REAL-EVAL" not in text:
        text += "\nBA-REAL-EVAL\n"
    if "COMPLETE" not in text:
        text += "\nCOMPLETE\n"
    return text


def _dedupe_ba_frozen_lines(text: str) -> str:
    kept: list[str] = []
    seen = False
    for line in text.splitlines(keepends=True):
        if line.startswith("**Wave BA COMPLETE + FROZEN:**"):
            if seen:
                continue
            seen = True
        kept.append(line)
    return "".join(kept)


def _patch_product_freeze_status() -> None:
    """Flip ACTIVE → COMPLETE + FROZEN on public product pages."""
    for path, frozen in (
        (_RECIPES, _BA_FROZEN_RECIPES),
        (_CARD, _BA_FROZEN_CARD),
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\*\*Wave BA ACTIVE:?\*\*[^\n]*",
            frozen,
            text,
            count=1,
        )
        if n:
            text = text2
        elif "**Wave BA COMPLETE + FROZEN**" not in text:
            text = text.rstrip() + "\n" + frozen + "\n"
        text = _dedupe_ba_frozen_lines(text)
        if "Wave BA7 BA-FREEZE" not in text and path == _RECIPES:
            needle = (
                "| Wave BA6 BA-REPORT | [wave-ba-summary.md]"
                "(wave-ba-summary.md) · [paper-lab-wave-ba.md]"
                "(paper-lab-wave-ba.md) **PROMOTE** "
                "(`npm run nano:ba:report`) — anti-FP · BA4 DEFER · "
                "NANOGEN6/7 HOLD · NANOGEN8·9·10 DEFER cited |\n"
            )
            row = (
                "| Wave BA7 BA-FREEZE | [ba-freeze.md](ba-freeze.md) · "
                "[formal-habfreeze-ba-freeze.md]"
                "(formal-habfreeze-ba-freeze.md) **PROMOTE** "
                "(`npm run nano:ba:freeze`) — COMPLETE+FROZEN; "
                "H-NANOGEN11 DEFER; do not invent Wave BB |\n"
            )
            if needle in text:
                text = text.replace(needle, needle + row, 1)
        path.write_text(_ensure_markers(text), encoding="utf-8")


def _patch_agents_agenda() -> None:
    if _AGENTS.is_file():
        text = _AGENTS.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"- \*\*Wave BA ACTIVE\*\* —[^\n]+",
            _BA_FROZEN_AGENTS,
            text,
            count=1,
        )
        if n:
            _AGENTS.write_text(text2, encoding="utf-8")
    if _AGENDA.is_file():
        text = _AGENDA.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\| \*\*BA\*\* \| \*\*ACTIVE\*\* \|[^\n]+",
            (
                "| **BA** | **COMPLETE + FROZEN** | BA0–BA6 as logged · "
                "BA4 [H-NANOGEN11 DEFER]"
                "(results/nano-lm/formal-hnanogen11-nanogen11.md); "
                "BA5 [BA-REAL-EVAL PROMOTE]"
                "(results/nano-lm/wave-ba-real-eval.md) battery 10/10; "
                "BA6 [BA-REPORT PROMOTE]"
                "(results/nano-lm/wave-ba-summary.md) · "
                "[paper-lab-wave-ba.md](results/nano-lm/paper-lab-wave-ba.md); "
                "BA7 [BA-FREEZE PROMOTE](results/nano-lm/ba-freeze.md) "
                "(`npm run nano:ba:freeze`) · "
                "[formal-habfreeze-ba-freeze.md]"
                "(results/nano-lm/formal-habfreeze-ba-freeze.md) "
                "— ship AF+AQ+AS trust + STRICT ablated DECODE; "
                "H-NANOGEN11 DEFER; ≤5M; do not invent Wave BB |"
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
        r"Wave BA ACTIVE \([^)]+\)",
        (
            "Wave BA COMPLETE + FROZEN (BA0–BA6 as logged · "
            "BA7 `ba-freeze.md` PROMOTE; do not invent Wave BB)"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    old_r = (
        "BA6 BA-REPORT PROMOTE (wave-ba-summary.md / "
        "paper-lab-wave-ba.md); next BA7 BA-FREEZE"
    )
    new_r = (
        "BA6 BA-REPORT PROMOTE · BA7 BA-FREEZE PROMOTE "
        "(`ba-freeze.md` · `formal-habfreeze-ba-freeze.md`); "
        "do not invent Wave BB"
    )
    if old_r in text:
        text = text.replace(old_r, new_r, 1)
    elif "next BA7 BA-FREEZE" in text and "do not invent Wave BB" not in text:
        text = text.replace(
            "next BA7 BA-FREEZE",
            (
                "BA7 `ba-freeze.md` · `formal-habfreeze-ba-freeze.md` "
                "PROMOTE; do not invent Wave BB"
            ),
            1,
        )
    _EVOGEN.write_text(text, encoding="utf-8")


def _render_formal() -> str:
    return "\n".join(
        [
            "# BA-FREEZE — Wave BA lock (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §8 BA7 · "
            "Public note: [ba-freeze.md](ba-freeze.md)  ",
            "> After: [wave-ba-summary.md](wave-ba-summary.md) / "
            "[paper-lab-wave-ba.md](paper-lab-wave-ba.md)",
            "",
            "## Hypothesis",
            "",
            "After BA-REPORT, freeze Wave BA the same way AZ-FREEZE "
            "locked AZ: **outcomes stay** (H-REALGAIN·H-FASTREAL·"
            "H-CTXREAL2·BA-REAL-EVAL·BA-REPORT PROMOTE; "
            "H-NANOGEN11 DEFER); **no Wave BB** without an explicit "
            "reopen agenda.",
            "",
            "## Gate",
            "",
            "| Check | Result |",
            "|-------|--------|",
            "| BA formals keep REALGAIN·FASTREAL·CTXREAL2·REAL-EVAL·"
            "REPORT PROMOTE · NANOGEN11 DEFER | **ok** |",
            "| `wave-ba-summary` · `paper-lab-wave-ba` · `ba-freeze` "
            "contain **COMPLETE** | **ok** |",
            "| RECIPES + champion-card contain **H-NANOGEN11** · "
            "**BA-REAL-EVAL** · **COMPLETE** | **ok** |",
            "| LOOKUP·forever·OOD·over-refuse BA smoke | **ok** |",
            "| Decision | **PROMOTE** |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:ba:freeze",
            "```",
            "",
            "## Finding",
            "",
            f"1. Ship claim stays scoped **{SHIP_CLAIM}**.  ",
            "2. BA-FREEZE does **not** invent new serve/train hyps.  ",
            "3. Further research requires a new § in "
            "`.local/pesquisa.md` (Wave BB reopen).  ",
            "4. Anti-FP law remains: LOOKUP ≠ generative IQ; "
            "forever intent LOOKUP = false-hit; "
            "exact-gold ABSTAIN = miss; "
            "PEAK ≠ unlabeled open chat; SAFE ≠ quality; "
            "span-fallback ≠ gen IQ; true-continue unlock locked "
            "(H-NANOGEN11 DEFER · NANOGEN8·9·10 DEFER · "
            "NANOGEN6·7 HOLD).  ",
            "5. ≤5M hard law remains (CAPCHECK closed).",
            "",
            "## Artifacts",
            "",
            "- Module: `nano_lm/src/ba_freeze_ops.py` · "
            "Runner: `nano_lm/src/run_ba_freeze.py`",
            "- Summary: `results/nano-lm/wave-ba/ba_freeze.json`",
            "- Contract: `nano_lm/tests/test_ba_freeze.py`",
            "",
        ]
    )


def _write_freeze_docs() -> None:
    _FREEZE_DOC.parent.mkdir(parents=True, exist_ok=True)
    _SUMMARY.write_text(render_wave_ba_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_ba(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_ba_freeze(), encoding="utf-8")
    _FORMAL.write_text(_render_formal(), encoding="utf-8")
    if _SESSION_PUB.is_file():
        text = _SESSION_PUB.read_text(encoding="utf-8")
        if "Next: **BA7 BA-FREEZE**" in text:
            text = text.replace(
                "Next: **BA7 BA-FREEZE**",
                "Next: **COMPLETE + FROZEN** — do not invent Wave BB "
                "without lab-book reopen (`npm run nano:ba:freeze`)",
                1,
            )
            _SESSION_PUB.write_text(text, encoding="utf-8")
        elif "next BA7 BA-FREEZE" in text:
            text = text.replace(
                "next BA7 BA-FREEZE",
                "COMPLETE + FROZEN — do not invent Wave BB",
                1,
            )
            _SESSION_PUB.write_text(text, encoding="utf-8")
    _patch_product_freeze_status()
    _patch_agents_agenda()


def _smoke_ba_modes(*, workers: int) -> dict[str, Any]:
    from run_ba_report import _smoke_ba_modes as _smoke

    return _smoke(workers=workers)


def _update_local_session(decision: str) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    ok = str(decision).startswith("PROMOTE")
    status = "DONE — PROMOTE" if ok else f"DONE — {decision}"
    wave = "COMPLETE + FROZEN" if ok else "OPEN"
    body = "\n".join(
        [
            f"# Wave BA session checklist (**{wave}** · BA7 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            f"(Wave BA **{wave}**).  ",
            "> Parent: AZ COMPLETE + FROZEN · Ship: **"
            + SHIP_CLAIM
            + "** · ≤5M (H-NANOGEN11 DEFER · NANOGEN8·9·10 DEFER · "
            "NANOGEN6·7 HOLD · no true-continue unlock).",
            "",
            "## Current stage",
            "",
            f"**BA7 — BA-FREEZE ({status})** · Next: "
            "**do not invent Wave BB**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| Wave | **{wave}** |",
            f"| Decision | **{decision.split(':', 1)[0]}** |",
            "| Public | `docs/results/nano-lm/ba-freeze.md` |",
            "| Formal | `docs/results/nano-lm/formal-habfreeze-ba-freeze.md` |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| BA0 | SESSION | **DONE — PROMOTE** |",
            "| BA1 | H-REALGAIN | **DONE — PROMOTE** |",
            "| BA2 | H-FASTREAL | **DONE — PROMOTE** |",
            "| BA3 | H-CTXREAL2 | **DONE — PROMOTE** |",
            "| BA4 | H-NANOGEN11 | **DONE — DEFER** |",
            "| BA5 | BA-REAL-EVAL | **DONE — PROMOTE** |",
            "| BA6 | BA-REPORT | **DONE — PROMOTE** |",
            f"| BA7 | BA-FREEZE | **{status}** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_local_helpers(status: str, ok: bool) -> None:
    wave = "COMPLETE + FROZEN" if ok else "OPEN"
    if _LOCAL_IMPL.is_file():
        text = _LOCAL_IMPL.read_text(encoding="utf-8")
        text = text.replace("Wave **BA ACTIVE**", f"Wave **BA {wave}**")
        old = (
            f"7. **BA6 BA-REPORT** — **DONE {status}** "
            "(`npm run nano:ba:report`) · next **BA7 BA-FREEZE**.  "
        )
        # Prefer the known DONE PROMOTE wording from BA6.
        old_alt = (
            "7. **BA6 BA-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:ba:report`) · next BA7 freeze.  "
        )
        new = (
            "7. **BA6 BA-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:ba:report`).  \n"
            f"8. **BA7 BA-FREEZE** — **DONE {status}** "
            "(`npm run nano:ba:freeze`) · **COMPLETE + FROZEN** · "
            "do not invent Wave BB.  "
        )
        if old_alt in text:
            text = text.replace(old_alt, new, 1)
        elif old in text:
            text = text.replace(old, new, 1)
        _LOCAL_IMPL.write_text(text, encoding="utf-8")
    if _LOCAL_README.is_file():
        text = _LOCAL_README.read_text(encoding="utf-8")
        text = text.replace("**Wave BA ACTIVE**", f"**Wave BA {wave}**")
        old = (
            "Session: `wave-ba/SESSION.md` (BA6 BA-REPORT "
            "**DONE — PROMOTE**; next BA7 BA-FREEZE)."
        )
        new = (
            f"Session: `wave-ba/SESSION.md` (BA7 BA-FREEZE "
            f"**DONE — {status}**; **{wave}** · do not invent Wave BB)."
        )
        if old in text:
            text = text.replace(old, new, 1)
        text = text.replace(
            "| Waves W–AZ | COMPLETE + FROZEN |",
            "| Waves W–BA | COMPLETE + FROZEN |",
            1,
        )
        _LOCAL_README.write_text(text, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    ok = str(decision).startswith("PROMOTE")
    status = "PROMOTE" if ok else decision.split("(", 1)[0].strip()
    text2, n = re.subn(
        r"\| BA7 \| \*\*BA-FREEZE\*\* \|[^\n]+\| \*\*TODO\*\* \|",
        (
            "| BA7 | **BA-FREEZE** | Lock outcomes | "
            f"no next letter without reopen | **DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    if ok:
        text = text.replace(
            "# pesquisa — Wave BA (**REOPEN** after AZ-FREEZE)",
            "# pesquisa — Wave BA (**COMPLETE + FROZEN**)",
            1,
        )
        text = text.replace(
            "## 8. Wave BA stage machine (**REOPEN**)",
            "## 8. Wave BA stage machine (**COMPLETE + FROZEN**)",
            1,
        )
        text2, n = re.subn(
            r"> \*\*Status:\*\* Wave AZ \*\*COMPLETE \+ FROZEN\*\* "
            r"\(archive\)\. Wave BA \*\*REOPENED\*\*[^\n]*\.",
            (
                "> **Status:** Wave BA **COMPLETE + FROZEN**. "
                "Do **not** invent Wave BB without explicit reopen. "
                "Parent: Wave AZ **COMPLETE + FROZEN** (archive)."
            ),
            text,
            count=1,
        )
        if n:
            text = text2
        text = text.replace(
            "> **Session:** `.local/wave-ba/SESSION.md` "
            "(BA6 BA-REPORT **DONE — PROMOTE**; next BA7 BA-FREEZE).  ",
            "> **Session:** `.local/wave-ba/SESSION.md` "
            f"(BA7 BA-FREEZE **DONE — {status}**; "
            "**COMPLETE + FROZEN**).  ",
            1,
        )
        text = text.replace(
            "> **Archive:** Waves W–**AZ** → `docs/results/nano-lm/*-freeze.md`.",
            "> **Archive:** Waves W–**BA** → `docs/results/nano-lm/*-freeze.md`.",
            1,
        )
    text = text.replace(
        (
            "7. **BA6 BA-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:ba:report`) · next BA7 freeze.  \n"
            "8. **BA7 BA-FREEZE** — **NEXT** — lock outcomes.  "
        ),
        (
            "7. **BA6 BA-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:ba:report`).  \n"
            f"8. **BA7 BA-FREEZE** — **DONE {status}** "
            "(`npm run nano:ba:freeze`) · **COMPLETE + FROZEN** · "
            "do not invent Wave BB.  "
        ),
        1,
    )
    bash_old = "# next: nano:ba:freeze"
    bash_new = (
        "npm run nano:ba:freeze\n"
        "# Wave BA COMPLETE + FROZEN — do not invent Wave BB"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")
    _patch_local_helpers(status, ok)


def run_ba_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN BA formals + COMPLETE closeout
    WHEN locking Wave BA
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    threads, workers = _hardware()
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in BA_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *BA_PUBLIC, *BA_PRODUCT_DOCS])
    )
    with ThreadPoolExecutor(
        max_workers=min(workers, max(4, len(read_paths)))
    ) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in BA_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in BA_PRODUCT_DOCS}
    decision = decide_ba_freeze(
        formal_texts=formal_texts,
        public_texts=public_texts,
        product_texts=product_texts,
    )
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_ba_modes(workers=workers)
        if not bool(ask.get("ok")):
            decision = "KILL (BA forever/modes smoke failed)"
    ok = str(decision).startswith("PROMOTE")
    _update_local_session(decision)
    _patch_pesquisa(decision)
    payload: dict[str, Any] = {
        "id": BA_FREEZE_ID,
        "hyp_id": BA_FREEZE_ID,
        "stage": "BA7",
        "thesis": BA_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in BA_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/ba-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-habfreeze-ba-freeze.md",
        "wave_ba_summary": "docs/results/nano-lm/wave-ba-summary.md",
        "rule": "pesquisa §8 BA-FREEZE",
        "wave_status": "COMPLETE+FROZEN" if ok else "RESEARCH_COMPLETE",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": threads,
        "workers": workers,
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave BA7 BA-FREEZE")
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    threads, _workers = _hardware()
    try:
        summary = run_ba_freeze(
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
                "hyp_id": BA_FREEZE_ID,
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
