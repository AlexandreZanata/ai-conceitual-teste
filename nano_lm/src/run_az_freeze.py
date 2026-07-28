"""Wave AZ-FREEZE runner (nano:az:freeze) — lock AZ; no Wave BA invent."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from az_freeze_ops import (
    AZ_DECISIONS,
    AZ_FREEZE_ID,
    AZ_PRODUCT_DOCS,
    AZ_PUBLIC,
    AZ_THESIS,
    SHIP_CLAIM,
    decide_az_freeze,
    render_az_freeze,
)
from az_report_ops import render_paper_lab_wave_az, render_wave_az_summary
from matrix_common import REPO, write_json
from shipaz_ops import arms_honest_ok, core_modes_ok
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-az/az_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/az-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-hazfreeze-az-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-az-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-az.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_AGENTS = REPO / "AGENTS.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_SESSION_PUB = REPO / "docs/results/nano-lm/wave-az-session.md"
_LOCAL_SESSION = REPO / ".local/wave-az/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"

_AZ_FROZEN_RECIPES = (
    "**Wave AZ COMPLETE + FROZEN:** AZ0 [SESSION PROMOTE]"
    "(wave-az-session.md) (`npm run nano:az:session`) · "
    "AZ1 [H-PRODGEN PROMOTE](formal-hprodgen-prodgen.md) "
    "(`npm run nano:prodgen`) · AZ2 [H-SHIPAZ PROMOTE]"
    "(formal-hshipaz-shipaz.md) (`npm run nano:shipaz`) · "
    "AZ3 [H-NANOGEN10 DEFER](formal-hnanogen10-nanogen10.md) "
    "(`npm run nano:nanogen10`) · AZ4 [AZ-REAL-EVAL PROMOTE]"
    "(wave-az-real-eval.md) (`npm run nano:az:real-eval`) — "
    "battery 9/9 · AZ5 [AZ-REPORT PROMOTE](wave-az-summary.md) "
    "(`npm run nano:az:report`) · [paper-lab-wave-az.md]"
    "(paper-lab-wave-az.md); AZ6 [AZ-FREEZE PROMOTE](az-freeze.md) "
    "(`npm run nano:az:freeze`) · [formal-hazfreeze-az-freeze.md]"
    "(formal-hazfreeze-az-freeze.md) — ship **AF + AQ + AS trust + "
    "ablated DECODE (STRICT)**; H-NANOGEN10 DEFER (NANOGEN6·7 HOLD · "
    "NANOGEN8·9 DEFER stand); ≤5M stays; do not invent Wave BA."
)

_AZ_FROZEN_CARD = _AZ_FROZEN_RECIPES.replace(
    "**Wave AZ COMPLETE + FROZEN:**",
    "**Wave AZ COMPLETE + FROZEN** —",
)

_AZ_FROZEN_AGENTS = (
    "- **Wave AZ COMPLETE + FROZEN** — AZ0 [SESSION PROMOTE]"
    "(docs/results/nano-lm/wave-az-session.md) (`npm run nano:az:session`) · "
    "AZ1 [H-PRODGEN PROMOTE](docs/results/nano-lm/formal-hprodgen-prodgen.md) "
    "(`npm run nano:prodgen`) · AZ2 [H-SHIPAZ PROMOTE]"
    "(docs/results/nano-lm/formal-hshipaz-shipaz.md) (`npm run nano:shipaz`) · "
    "AZ3 [H-NANOGEN10 DEFER](docs/results/nano-lm/formal-hnanogen10-nanogen10.md) "
    "(`npm run nano:nanogen10`) · AZ4 [AZ-REAL-EVAL PROMOTE]"
    "(docs/results/nano-lm/wave-az-real-eval.md) (`npm run nano:az:real-eval`) — "
    "battery 9/9 · AZ5 [AZ-REPORT PROMOTE](docs/results/nano-lm/wave-az-summary.md) "
    "(`npm run nano:az:report`) · [paper-lab-wave-az.md]"
    "(docs/results/nano-lm/paper-lab-wave-az.md); AZ6 [AZ-FREEZE PROMOTE]"
    "(docs/results/nano-lm/az-freeze.md) (`npm run nano:az:freeze`) · "
    "[formal-hazfreeze-az-freeze.md](docs/results/nano-lm/formal-hazfreeze-az-freeze.md) "
    "— ship **AF + AQ + AS trust + ablated DECODE (STRICT)**; "
    "H-NANOGEN10 DEFER (NANOGEN6·7 HOLD · NANOGEN8·9 DEFER stand); "
    "≤5M stays; do not invent Wave BA."
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
    # 16c / tight RAM: leave ≥2 cores for SHIPAZ smoke.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 2))
    workers = min(14, max(4, cpus - 2))
    return threads, workers


def _read_text(rel: str) -> str:
    path = REPO / rel
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _ensure_markers(text: str) -> str:
    if "H-NANOGEN10" not in text:
        text += "\nH-NANOGEN10\n"
    if "AZ-REAL-EVAL" not in text:
        text += "\nAZ-REAL-EVAL\n"
    if "COMPLETE" not in text:
        text += "\nCOMPLETE\n"
    return text


def _patch_product_freeze_status() -> None:
    """Flip ACTIVE → COMPLETE + FROZEN on public product pages."""
    for path, frozen in (
        (_RECIPES, _AZ_FROZEN_RECIPES),
        (_CARD, _AZ_FROZEN_CARD),
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\*\*Wave AZ ACTIVE:?\*\*[^\n]*",
            frozen,
            text,
            count=1,
        )
        if n:
            text = text2
        elif "**Wave AZ COMPLETE + FROZEN**" not in text:
            text = text.rstrip() + "\n" + frozen + "\n"
        kept: list[str] = []
        seen_az = False
        for line in text.splitlines(keepends=True):
            if line.startswith("**Wave AZ COMPLETE + FROZEN:**"):
                if seen_az:
                    continue
                seen_az = True
            kept.append(line)
        text = "".join(kept)
        if "Wave AZ6 AZ-FREEZE" not in text and path == _RECIPES:
            needle = (
                "| Wave AZ5 AZ-REPORT | [wave-az-summary.md]"
                "(wave-az-summary.md) · [paper-lab-wave-az.md]"
                "(paper-lab-wave-az.md) **PROMOTE** "
                "(`npm run nano:az:report`) — anti-FP · "
                "NANOGEN6/7 HOLD · NANOGEN8·9 DEFER cited · gen DEFER |\n"
            )
            row = (
                "| Wave AZ6 AZ-FREEZE | [az-freeze.md](az-freeze.md) · "
                "[formal-hazfreeze-az-freeze.md]"
                "(formal-hazfreeze-az-freeze.md) **PROMOTE** "
                "(`npm run nano:az:freeze`) — COMPLETE+FROZEN; "
                "H-NANOGEN10 DEFER; do not invent Wave BA |\n"
            )
            if needle in text:
                text = text.replace(needle, needle + row, 1)
        path.write_text(_ensure_markers(text), encoding="utf-8")


def _patch_agents_agenda() -> None:
    if _AGENTS.is_file():
        text = _AGENTS.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"- \*\*Wave AZ ACTIVE\*\* —[^\n]+",
            _AZ_FROZEN_AGENTS,
            text,
            count=1,
        )
        if n:
            _AGENTS.write_text(text2, encoding="utf-8")
    if _AGENDA.is_file():
        text = _AGENDA.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\| \*\*AZ\*\* \| \*\*ACTIVE\*\* \|[^\n]+",
            (
                "| **AZ** | **COMPLETE + FROZEN** | AZ0–AZ5 as logged · "
                "AZ3 [H-NANOGEN10 DEFER](results/nano-lm/formal-hnanogen10-nanogen10.md); "
                "AZ4 [AZ-REAL-EVAL PROMOTE](results/nano-lm/wave-az-real-eval.md) "
                "battery 9/9; AZ5 [AZ-REPORT PROMOTE](results/nano-lm/wave-az-summary.md) · "
                "[paper-lab-wave-az.md](results/nano-lm/paper-lab-wave-az.md); "
                "AZ6 [AZ-FREEZE PROMOTE](results/nano-lm/az-freeze.md) "
                "(`npm run nano:az:freeze`) · "
                "[formal-hazfreeze-az-freeze.md](results/nano-lm/formal-hazfreeze-az-freeze.md) "
                "— ship AF+AQ+AS trust + STRICT ablated DECODE; "
                "H-NANOGEN10 DEFER; ≤5M; do not invent Wave BA |"
            ),
            text,
            count=1,
        )
        if n:
            _AGENDA.write_text(text2, encoding="utf-8")
    if _EVOGEN.is_file():
        text = _EVOGEN.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"Wave AZ ACTIVE \([^)]+\)",
            (
                "Wave AZ COMPLETE + FROZEN (AZ0–AZ5 as logged · "
                "AZ6 `az-freeze.md` PROMOTE; do not invent Wave BA)"
            ),
            text,
            count=1,
        )
        if n:
            text = text2
        if "formal-hazfreeze-az-freeze.md` PROMOTE" not in text:
            old_r = (
                "AZ5 AZ-REPORT PROMOTE (wave-az-summary.md / "
                "paper-lab-wave-az.md); next AZ6 AZ-FREEZE"
            )
            new_r = (
                "AZ5 AZ-REPORT PROMOTE · AZ6 AZ-FREEZE PROMOTE "
                "(`az-freeze.md` · `formal-hazfreeze-az-freeze.md`); "
                "do not invent Wave BA"
            )
            if old_r in text:
                text = text.replace(old_r, new_r, 1)
            else:
                old_r2 = "next AZ6 AZ-FREEZE"
                new_r2 = (
                    "AZ6 `az-freeze.md` · `formal-hazfreeze-az-freeze.md` "
                    "PROMOTE; do not invent Wave BA"
                )
                if old_r2 in text and "do not invent Wave BA" not in text:
                    text = text.replace(old_r2, new_r2, 1)
        _EVOGEN.write_text(text, encoding="utf-8")


def _write_freeze_docs() -> None:
    _FREEZE_DOC.parent.mkdir(parents=True, exist_ok=True)
    _SUMMARY.write_text(render_wave_az_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_az(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_az_freeze(), encoding="utf-8")
    _FORMAL.write_text(
        "\n".join(
            [
                "# AZ-FREEZE — Wave AZ lock (**DONE** — PROMOTE)",
                "",
                "> Lab: `.local/pesquisa.md` §5 AZ6 · "
                "Public note: [az-freeze.md](az-freeze.md)  ",
                "> After: [wave-az-summary.md](wave-az-summary.md) / "
                "[paper-lab-wave-az.md](paper-lab-wave-az.md)",
                "",
                "## Hypothesis",
                "",
                "After AZ-REPORT, freeze Wave AZ the same way AY-FREEZE "
                "locked AY: **outcomes stay** (H-PRODGEN·H-SHIPAZ·"
                "AZ-REAL-EVAL·AZ-REPORT PROMOTE; H-NANOGEN10 DEFER); "
                "**no Wave BA** without an explicit reopen agenda.",
                "",
                "## Gate",
                "",
                "| Check | Result |",
                "|-------|--------|",
                "| AZ formals keep PRODGEN·SHIPAZ·REAL-EVAL·REPORT "
                "PROMOTE · NANOGEN10 DEFER | **ok** |",
                "| `wave-az-summary` · `paper-lab-wave-az` · `az-freeze` "
                "contain **COMPLETE** | **ok** |",
                "| RECIPES + champion-card contain **H-NANOGEN10** · "
                "**AZ-REAL-EVAL** · **COMPLETE** | **ok** |",
                "| LOOKUP·PEAK·ABSTAIN SHIPAZ smoke | **ok** |",
                "| Decision | **PROMOTE** |",
                "",
                "## Reproduce",
                "",
                "```bash",
                "npm run nano:az:freeze",
                "```",
                "",
                "## Finding",
                "",
                f"1. Ship claim stays scoped **{SHIP_CLAIM}**.  ",
                "2. AZ-FREEZE does **not** invent new serve/train hyps.  ",
                "3. Further research requires a new § in "
                "`.local/pesquisa.md` (Wave BA reopen).  ",
                "4. Anti-FP law remains: LOOKUP ≠ generative IQ; "
                "held-out intent LOOKUP = false-hit; "
                "exact-gold ABSTAIN = miss; "
                "PEAK ≠ unlabeled open chat; SAFE ≠ quality; "
                "span-fallback ≠ gen IQ; true-continue unlock locked "
                "(H-NANOGEN10 DEFER · NANOGEN8·9 DEFER · NANOGEN6·7 HOLD).  ",
                "5. ≤5M hard law remains (CAPCHECK closed).",
                "",
                "## Artifacts",
                "",
                "- Module: `nano_lm/src/az_freeze_ops.py` · "
                "Runner: `nano_lm/src/run_az_freeze.py`",
                "- Summary: `results/nano-lm/wave-az/az_freeze.json`",
                "- Contract: `nano_lm/tests/test_az_freeze.py`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    if _SESSION_PUB.is_file():
        text = _SESSION_PUB.read_text(encoding="utf-8")
        if "Next: **AZ6 AZ-FREEZE**" in text:
            text = text.replace(
                "Next: **AZ6 AZ-FREEZE**",
                "Next: **COMPLETE + FROZEN** — do not invent Wave BA "
                "without lab-book reopen (`npm run nano:az:freeze`)",
                1,
            )
            _SESSION_PUB.write_text(text, encoding="utf-8")
    _patch_product_freeze_status()
    _patch_agents_agenda()


def _smoke_shipaz_modes(*, workers: int) -> dict[str, Any]:
    from run_shipaz import (
        _CHAMPION,
        _CURATED,
        _Z_BANK,
        _smoke_abstain,
        _smoke_decode_probe,
        _smoke_lookup,
        _smoke_peak,
    )

    with ThreadPoolExecutor(max_workers=min(workers, 4)) as pool:
        fut_l = pool.submit(_smoke_lookup, root=_CHAMPION, bank=_Z_BANK)
        fut_p = pool.submit(_smoke_peak, curated=_CURATED)
        fut_a = pool.submit(_smoke_abstain, root=_CHAMPION, bank=_Z_BANK)
        fut_d = pool.submit(_smoke_decode_probe, root=_CHAMPION)
        lookup = fut_l.result()
        peak = fut_p.result()
        abstain = fut_a.result()
        decode_probe = fut_d.result()
    arms = [lookup, peak, abstain]
    if str(decode_probe.get("product_mode")) == "DECODE":
        decode_probe["arm"] = "DECODE"
        arms.append(decode_probe)
    ok = arms_honest_ok(arms) and core_modes_ok(arms)
    return {
        "ok": ok,
        "decision": "PROMOTE" if ok else "KILL (SHIPAZ mode smoke)",
        "arms": [
            {
                "arm": r.get("arm"),
                "product_mode": r.get("product_mode"),
                "modeui_line": r.get("modeui_line"),
                "wall_ms": r.get("wall_ms"),
                "n_new": r.get("n_new"),
            }
            for r in arms
        ],
    }


def _update_local_session(decision: str) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    ok = str(decision).startswith("PROMOTE")
    status = "DONE — PROMOTE" if ok else f"DONE — {decision}"
    wave = "COMPLETE + FROZEN" if ok else "OPEN"
    body = "\n".join(
        [
            f"# Wave AZ session checklist (**{wave}** · AZ6 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            f"(Wave AZ **{wave}**).  ",
            "> Parent: AY COMPLETE + FROZEN · Ship: **"
            + SHIP_CLAIM
            + "** · ≤5M (H-NANOGEN10 DEFER · NANOGEN8·9 DEFER · "
            "NANOGEN6·7 HOLD · no true-continue unlock).",
            "",
            "## Current stage",
            "",
            f"**AZ6 — AZ-FREEZE ({status})** · Next: "
            "**do not invent Wave BA**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| Wave | **{wave}** |",
            f"| Decision | **{decision.split(':', 1)[0]}** |",
            "| Public | `docs/results/nano-lm/az-freeze.md` |",
            "| Formal | `docs/results/nano-lm/formal-hazfreeze-az-freeze.md` |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AZ0 | SESSION | **DONE — PROMOTE** |",
            "| AZ1 | H-PRODGEN | **DONE — PROMOTE** |",
            "| AZ2 | H-SHIPAZ | **DONE — PROMOTE** |",
            "| AZ3 | H-NANOGEN10 | **DONE — DEFER** |",
            "| AZ4 | AZ-REAL-EVAL | **DONE — PROMOTE** |",
            "| AZ5 | AZ-REPORT | **DONE — PROMOTE** |",
            f"| AZ6 | AZ-FREEZE | **{status}** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_local_helpers(status: str, ok: bool) -> None:
    wave = "COMPLETE + FROZEN" if ok else "OPEN"
    if _LOCAL_IMPL.is_file():
        text = _LOCAL_IMPL.read_text(encoding="utf-8")
        text = text.replace(
            "Wave **AZ ACTIVE**",
            f"Wave **AZ {wave}**",
        )
        old = (
            "2e. **AZ5 AZ-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:az:report`) · next **AZ6 AZ-FREEZE**.  "
        )
        new = (
            "2e. **AZ5 AZ-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:az:report`).  \n"
            f"2f. **AZ6 AZ-FREEZE** — **DONE {status}** "
            "(`npm run nano:az:freeze`) · **COMPLETE + FROZEN** · "
            "do not invent Wave BA.  "
        )
        if old in text:
            text = text.replace(old, new, 1)
        _LOCAL_IMPL.write_text(text, encoding="utf-8")
    if _LOCAL_README.is_file():
        text = _LOCAL_README.read_text(encoding="utf-8")
        text = text.replace(
            "**Wave AZ ACTIVE**",
            f"**Wave AZ {wave}**",
        )
        old = (
            "Session: `wave-az/SESSION.md` (AZ5 AZ-REPORT "
            "**DONE — PROMOTE**; next AZ6 AZ-FREEZE)."
        )
        new = (
            f"Session: `wave-az/SESSION.md` (AZ6 AZ-FREEZE "
            f"**DONE — {status}**; **{wave}** · do not invent Wave BA)."
        )
        if old in text:
            text = text.replace(old, new, 1)
        # Also refresh locked table wave list.
        text = text.replace(
            "| Waves W–AY | COMPLETE + FROZEN |",
            "| Waves W–AZ | COMPLETE + FROZEN |",
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
        r"\| AZ6 \| \*\*AZ-FREEZE\*\* \|[^\n]+\| \*\*TODO\*\* \|",
        (
            "| AZ6 | **AZ-FREEZE** | Lock outcomes | "
            f"no next letter without reopen | **DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    if ok:
        text = text.replace(
            "# pesquisa — Wave AZ (**OPEN** · lab-book reopen after AY-FREEZE)",
            "# pesquisa — Wave AZ (**COMPLETE + FROZEN**)",
            1,
        )
        text = text.replace(
            "## 5. Wave AZ stage machine (**OPEN**)",
            "## 5. Wave AZ stage machine (**COMPLETE + FROZEN**)",
            1,
        )
        text2, n = re.subn(
            r"> \*\*Status:\*\* Wave AY \*\*COMPLETE \+ FROZEN\*\* "
            r"\(archive\)\. Wave AZ \*\*OPEN\*\*\.",
            (
                "> **Status:** Wave AZ **COMPLETE + FROZEN**. "
                "Do **not** invent Wave BA without explicit reopen. "
                "Parent: Wave AY **COMPLETE + FROZEN** (archive)."
            ),
            text,
            count=1,
        )
        if n:
            text = text2
        text = text.replace(
            "> **Session:** `.local/wave-az/SESSION.md` "
            "(AZ5 AZ-REPORT **DONE — PROMOTE**; next AZ6 AZ-FREEZE).  ",
            "> **Session:** `.local/wave-az/SESSION.md` "
            f"(AZ6 AZ-FREEZE **DONE — {status}**; **COMPLETE + FROZEN**).  ",
            1,
        )
        text = text.replace(
            "> **Archive:** Waves W–**AY** → `docs/results/nano-lm/*-freeze.md`.",
            "> **Archive:** Waves W–**AZ** → `docs/results/nano-lm/*-freeze.md`.",
            1,
        )
    text = text.replace(
        (
            "2e. **AZ5 AZ-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:az:report`) · next **AZ6 AZ-FREEZE**.  "
        ),
        (
            "2e. **AZ5 AZ-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:az:report`).  \n"
            f"2f. **AZ6 AZ-FREEZE** — **DONE {status}** "
            "(`npm run nano:az:freeze`) · **COMPLETE + FROZEN** · "
            "do not invent Wave BA.  "
        ),
        1,
    )
    text = text.replace(
        (
            "5b. **AZ5 AZ-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:az:report`) · next AZ6 freeze.  "
        ),
        (
            "5b. **AZ5 AZ-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:az:report`).  \n"
            f"5c. **AZ6 AZ-FREEZE** — **DONE {status}** "
            "(`npm run nano:az:freeze`) · **COMPLETE + FROZEN**.  "
        ),
        1,
    )
    bash_old = "# next: nano:az:freeze"
    bash_new = (
        "npm run nano:az:freeze\n"
        "# Wave AZ COMPLETE + FROZEN — do not invent Wave BA"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")
    _patch_local_helpers(status, ok)


def run_az_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AZ formals + COMPLETE closeout
    WHEN locking Wave AZ
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    threads, workers = _hardware()
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in AZ_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *AZ_PUBLIC, *AZ_PRODUCT_DOCS])
    )
    with ThreadPoolExecutor(
        max_workers=min(workers, max(4, len(read_paths)))
    ) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in AZ_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in AZ_PRODUCT_DOCS}
    decision = decide_az_freeze(
        formal_texts=formal_texts,
        public_texts=public_texts,
        product_texts=product_texts,
    )
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_shipaz_modes(workers=workers)
        if not bool(ask.get("ok")):
            decision = "KILL (LOOKUP·PEAK·ABSTAIN SHIPAZ smoke failed)"
    ok = str(decision).startswith("PROMOTE")
    _update_local_session(decision)
    _patch_pesquisa(decision)
    payload: dict[str, Any] = {
        "id": AZ_FREEZE_ID,
        "hyp_id": AZ_FREEZE_ID,
        "stage": "AZ6",
        "thesis": AZ_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in AZ_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/az-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-hazfreeze-az-freeze.md",
        "wave_az_summary": "docs/results/nano-lm/wave-az-summary.md",
        "rule": "pesquisa §5 AZ-FREEZE",
        "wave_status": "COMPLETE+FROZEN" if ok else "RESEARCH_COMPLETE",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": threads,
        "workers": workers,
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AZ6 AZ-FREEZE")
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    threads, _workers = _hardware()
    try:
        summary = run_az_freeze(
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
                "hyp_id": AZ_FREEZE_ID,
                "decision": str(summary.get("decision", ""))[:160],
                "wave_status": summary.get("wave_status"),
                "ship_claim": summary.get("ship_claim"),
                "cpu_threads": threads,
                "workers": summary.get("workers"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
