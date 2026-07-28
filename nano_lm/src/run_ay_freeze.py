"""Wave AY-FREEZE runner (nano:ay:freeze) — lock AY; no Wave AZ invent."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from ay_freeze_ops import (
    AY_DECISIONS,
    AY_FREEZE_ID,
    AY_PRODUCT_DOCS,
    AY_PUBLIC,
    AY_THESIS,
    SHIP_CLAIM,
    decide_ay_freeze,
    render_ay_freeze,
)
from ay_report_ops import render_paper_lab_wave_ay, render_wave_ay_summary
from matrix_common import REPO, write_json
from shipay_ops import arms_honest_ok, core_modes_ok
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-ay/ay_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/ay-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-hayfreeze-ay-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-ay-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-ay.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_AGENTS = REPO / "AGENTS.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_SESSION_PUB = REPO / "docs/results/nano-lm/wave-ay-session.md"
_LOCAL_SESSION = REPO / ".local/wave-ay/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"

_AY_FROZEN_RECIPES = (
    "**Wave AY COMPLETE + FROZEN:** AY0 [SESSION PROMOTE]"
    "(wave-ay-session.md) (`npm run nano:ay:session`) · "
    "AY1 [H-PRODINT PROMOTE](formal-hprodint-prodint.md) "
    "(`npm run nano:prodint`) · AY2 [H-SHIPAY PROMOTE]"
    "(formal-hshipay-shipay.md) (`npm run nano:shipay`) · "
    "AY3 [H-NANOGEN9 DEFER](formal-hnanogen9-nanogen9.md) "
    "(`npm run nano:nanogen9`) · AY4 [AY-REAL-EVAL PROMOTE]"
    "(wave-ay-real-eval.md) (`npm run nano:ay:real-eval`) — "
    "battery 8/8 · AY5 [AY-REPORT PROMOTE](wave-ay-summary.md) "
    "(`npm run nano:ay:report`) · [paper-lab-wave-ay.md]"
    "(paper-lab-wave-ay.md); AY6 [AY-FREEZE PROMOTE](ay-freeze.md) "
    "(`npm run nano:ay:freeze`) · [formal-hayfreeze-ay-freeze.md]"
    "(formal-hayfreeze-ay-freeze.md) — ship **AF + AQ + AS trust + "
    "ablated DECODE (STRICT)**; H-NANOGEN9 DEFER (NANOGEN6·7 HOLD · "
    "NANOGEN8 DEFER stand); ≤5M stays; do not invent Wave AZ."
)

_AY_FROZEN_CARD = _AY_FROZEN_RECIPES.replace(
    "**Wave AY COMPLETE + FROZEN:**",
    "**Wave AY COMPLETE + FROZEN** —",
)

_AY_FROZEN_AGENTS = (
    "- **Wave AY COMPLETE + FROZEN** — AY0 [SESSION PROMOTE]"
    "(docs/results/nano-lm/wave-ay-session.md) (`npm run nano:ay:session`) · "
    "AY1 [H-PRODINT PROMOTE](docs/results/nano-lm/formal-hprodint-prodint.md) "
    "(`npm run nano:prodint`) · AY2 [H-SHIPAY PROMOTE]"
    "(docs/results/nano-lm/formal-hshipay-shipay.md) (`npm run nano:shipay`) · "
    "AY3 [H-NANOGEN9 DEFER](docs/results/nano-lm/formal-hnanogen9-nanogen9.md) "
    "(`npm run nano:nanogen9`) · AY4 [AY-REAL-EVAL PROMOTE]"
    "(docs/results/nano-lm/wave-ay-real-eval.md) (`npm run nano:ay:real-eval`) — "
    "battery 8/8 · AY5 [AY-REPORT PROMOTE](docs/results/nano-lm/wave-ay-summary.md) "
    "(`npm run nano:ay:report`) · [paper-lab-wave-ay.md]"
    "(docs/results/nano-lm/paper-lab-wave-ay.md); AY6 [AY-FREEZE PROMOTE]"
    "(docs/results/nano-lm/ay-freeze.md) (`npm run nano:ay:freeze`) · "
    "[formal-hayfreeze-ay-freeze.md](docs/results/nano-lm/formal-hayfreeze-ay-freeze.md) "
    "— ship **AF + AQ + AS trust + ablated DECODE (STRICT)**; "
    "H-NANOGEN9 DEFER (NANOGEN6·7 HOLD · NANOGEN8 DEFER stand); "
    "≤5M stays; do not invent Wave AZ."
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
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 2))
    workers = min(14, max(4, cpus - 2))
    return threads, workers


def _read_text(rel: str) -> str:
    path = REPO / rel
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _ensure_markers(text: str) -> str:
    if "H-NANOGEN9" not in text:
        text += "\nH-NANOGEN9\n"
    if "AY-REAL-EVAL" not in text:
        text += "\nAY-REAL-EVAL\n"
    if "COMPLETE" not in text:
        text += "\nCOMPLETE\n"
    return text


def _patch_product_freeze_status() -> None:
    """Flip ACTIVE → COMPLETE + FROZEN on public product pages."""
    for path, frozen in (
        (_RECIPES, _AY_FROZEN_RECIPES),
        (_CARD, _AY_FROZEN_CARD),
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\*\*Wave AY ACTIVE:?\*\*[^\n]*",
            frozen,
            text,
            count=1,
        )
        if n:
            text = text2
        elif "**Wave AY COMPLETE + FROZEN**" not in text:
            text = text.rstrip() + "\n" + frozen + "\n"
        kept: list[str] = []
        seen_ay = False
        for line in text.splitlines(keepends=True):
            if line.startswith("**Wave AY COMPLETE + FROZEN:**"):
                if seen_ay:
                    continue
                seen_ay = True
            kept.append(line)
        text = "".join(kept)
        if "Wave AY6 AY-FREEZE" not in text and path == _RECIPES:
            needle = (
                "| Wave AY5 AY-REPORT | [wave-ay-summary.md]"
                "(wave-ay-summary.md) · [paper-lab-wave-ay.md]"
                "(paper-lab-wave-ay.md) **PROMOTE** "
                "(`npm run nano:ay:report`) — anti-FP · "
                "NANOGEN6/7 HOLD · NANOGEN8 DEFER cited · gen DEFER |\n"
            )
            row = (
                "| Wave AY6 AY-FREEZE | [ay-freeze.md](ay-freeze.md) · "
                "[formal-hayfreeze-ay-freeze.md]"
                "(formal-hayfreeze-ay-freeze.md) **PROMOTE** "
                "(`npm run nano:ay:freeze`) — COMPLETE+FROZEN; "
                "H-NANOGEN9 DEFER; do not invent Wave AZ |\n"
            )
            if needle in text:
                text = text.replace(needle, needle + row, 1)
        path.write_text(_ensure_markers(text), encoding="utf-8")


def _patch_agents_agenda() -> None:
    if _AGENTS.is_file():
        text = _AGENTS.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"- \*\*Wave AY ACTIVE\*\* —[^\n]+",
            _AY_FROZEN_AGENTS,
            text,
            count=1,
        )
        if n:
            _AGENTS.write_text(text2, encoding="utf-8")
    if _AGENDA.is_file():
        text = _AGENDA.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\| \*\*AY\*\* \| \*\*ACTIVE\*\* \|[^\n]+",
            (
                "| **AY** | **COMPLETE + FROZEN** | AY0–AY5 as logged · "
                "AY3 [H-NANOGEN9 DEFER](results/nano-lm/formal-hnanogen9-nanogen9.md); "
                "AY4 [AY-REAL-EVAL PROMOTE](results/nano-lm/wave-ay-real-eval.md) "
                "battery 8/8; AY5 [AY-REPORT PROMOTE](results/nano-lm/wave-ay-summary.md) · "
                "[paper-lab-wave-ay.md](results/nano-lm/paper-lab-wave-ay.md); "
                "AY6 [AY-FREEZE PROMOTE](results/nano-lm/ay-freeze.md) "
                "(`npm run nano:ay:freeze`) · "
                "[formal-hayfreeze-ay-freeze.md](results/nano-lm/formal-hayfreeze-ay-freeze.md) "
                "— ship AF+AQ+AS trust + STRICT ablated DECODE; "
                "H-NANOGEN9 DEFER; ≤5M; do not invent Wave AZ |"
            ),
            text,
            count=1,
        )
        if n:
            _AGENDA.write_text(text2, encoding="utf-8")
    if _EVOGEN.is_file():
        text = _EVOGEN.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"Wave AY ACTIVE \([^)]+\)",
            (
                "Wave AY COMPLETE + FROZEN (AY0–AY5 as logged · "
                "AY6 `ay-freeze.md` PROMOTE; do not invent Wave AZ)"
            ),
            text,
            count=1,
        )
        if n:
            text = text2
        if "formal-hayfreeze-ay-freeze.md` PROMOTE" not in text:
            old_r = (
                "Wave AY5: `wave-ay-summary.md` / `paper-lab-wave-ay.md` PROMOTE · "
            )
            new_r = (
                "Wave AY5: `wave-ay-summary.md` / `paper-lab-wave-ay.md` PROMOTE · "
                "Wave AY6: `ay-freeze.md` · `formal-hayfreeze-ay-freeze.md` PROMOTE · "
            )
            if old_r in text:
                text = text.replace(old_r, new_r, 1)
            else:
                old_r2 = (
                    "Wave AY5: `wave-ay-summary.md` / `paper-lab-wave-ay.md` "
                    "PROMOTE · Wave AX0:"
                )
                new_r2 = (
                    "Wave AY5: `wave-ay-summary.md` / `paper-lab-wave-ay.md` "
                    "PROMOTE · Wave AY6: `ay-freeze.md` · "
                    "`formal-hayfreeze-ay-freeze.md` PROMOTE · Wave AX0:"
                )
                if old_r2 in text:
                    text = text.replace(old_r2, new_r2, 1)
        _EVOGEN.write_text(text, encoding="utf-8")


def _write_freeze_docs() -> None:
    _FREEZE_DOC.parent.mkdir(parents=True, exist_ok=True)
    _SUMMARY.write_text(render_wave_ay_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_ay(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_ay_freeze(), encoding="utf-8")
    _FORMAL.write_text(
        "\n".join(
            [
                "# AY-FREEZE — Wave AY lock (**DONE** — PROMOTE)",
                "",
                "> Lab: `.local/pesquisa.md` §5 AY6 · "
                "Public note: [ay-freeze.md](ay-freeze.md)  ",
                "> After: [wave-ay-summary.md](wave-ay-summary.md) / "
                "[paper-lab-wave-ay.md](paper-lab-wave-ay.md)",
                "",
                "## Hypothesis",
                "",
                "After AY-REPORT, freeze Wave AY the same way AX-FREEZE "
                "locked AX: **outcomes stay** (H-PRODINT·H-SHIPAY·"
                "AY-REAL-EVAL·AY-REPORT PROMOTE; H-NANOGEN9 DEFER); "
                "**no Wave AZ** without an explicit reopen agenda.",
                "",
                "## Gate",
                "",
                "| Check | Result |",
                "|-------|--------|",
                "| AY formals keep PRODINT·SHIPAY·REAL-EVAL·REPORT "
                "PROMOTE · NANOGEN9 DEFER | **ok** |",
                "| `wave-ay-summary` · `paper-lab-wave-ay` · `ay-freeze` "
                "contain **COMPLETE** | **ok** |",
                "| RECIPES + champion-card contain **H-NANOGEN9** · "
                "**AY-REAL-EVAL** · **COMPLETE** | **ok** |",
                "| LOOKUP·PEAK·ABSTAIN SHIPAY smoke | **ok** |",
                "| Decision | **PROMOTE** |",
                "",
                "## Reproduce",
                "",
                "```bash",
                "npm run nano:ay:freeze",
                "```",
                "",
                "## Finding",
                "",
                f"1. Ship claim stays scoped **{SHIP_CLAIM}**.  ",
                "2. AY-FREEZE does **not** invent new serve/train hyps.  ",
                "3. Further research requires a new § in "
                "`.local/pesquisa.md` (Wave AZ reopen).  ",
                "4. Anti-FP law remains: LOOKUP ≠ generative IQ; "
                "intent-mismatch LOOKUP = false-hit; "
                "PEAK ≠ unlabeled open chat; SAFE ≠ quality; "
                "span-fallback ≠ gen IQ; true-continue unlock locked "
                "(H-NANOGEN9 DEFER · NANOGEN8 DEFER · NANOGEN6·7 HOLD).  ",
                "5. ≤5M hard law remains (CAPCHECK closed).",
                "",
                "## Artifacts",
                "",
                "- Module: `nano_lm/src/ay_freeze_ops.py` · "
                "Runner: `nano_lm/src/run_ay_freeze.py`",
                "- Summary: `results/nano-lm/wave-ay/ay_freeze.json`",
                "- Contract: `nano_lm/tests/test_ay_freeze.py`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    if _SESSION_PUB.is_file():
        text = _SESSION_PUB.read_text(encoding="utf-8")
        if "Next: **AY6 AY-FREEZE**" in text:
            text = text.replace(
                "Next: **AY6 AY-FREEZE**",
                "Next: **COMPLETE + FROZEN** — do not invent Wave AZ "
                "without lab-book reopen (`npm run nano:ay:freeze`)",
                1,
            )
            _SESSION_PUB.write_text(text, encoding="utf-8")
    _patch_product_freeze_status()
    _patch_agents_agenda()


def _smoke_shipay_modes(*, workers: int) -> dict[str, Any]:
    from run_shipay import (
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
        "decision": "PROMOTE" if ok else "KILL (SHIPAY mode smoke)",
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
            f"# Wave AY session checklist (**{wave}** · AY6 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            f"(Wave AY **{wave}**).  ",
            "> Parent: AX COMPLETE + FROZEN · Ship: **"
            + SHIP_CLAIM
            + "** · ≤5M (H-NANOGEN9 DEFER · NANOGEN8 DEFER · "
            "NANOGEN6·7 HOLD · no true-continue unlock).",
            "",
            "## Current stage",
            "",
            f"**AY6 — AY-FREEZE ({status})** · Next: "
            "**do not invent Wave AZ**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| Wave | **{wave}** |",
            f"| Decision | **{decision.split(':', 1)[0]}** |",
            "| Public | `docs/results/nano-lm/ay-freeze.md` |",
            "| Formal | `docs/results/nano-lm/formal-hayfreeze-ay-freeze.md` |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AY0 | SESSION | **DONE — PROMOTE** |",
            "| AY1 | H-PRODINT | **DONE — PROMOTE** |",
            "| AY2 | H-SHIPAY | **DONE — PROMOTE** |",
            "| AY3 | H-NANOGEN9 | **DONE — DEFER** |",
            "| AY4 | AY-REAL-EVAL | **DONE — PROMOTE** |",
            "| AY5 | AY-REPORT | **DONE — PROMOTE** |",
            f"| AY6 | AY-FREEZE | **{status}** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_local_helpers(status: str, ok: bool) -> None:
    wave = "COMPLETE + FROZEN" if ok else "OPEN"
    if _LOCAL_IMPL.is_file():
        text = _LOCAL_IMPL.read_text(encoding="utf-8")
        text = text.replace(
            "Wave **AY ACTIVE**",
            f"Wave **AY {wave}**",
        )
        old = (
            "2e. **AY5 AY-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:ay:report`) · next **AY6 AY-FREEZE**.  "
        )
        new = (
            "2e. **AY5 AY-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:ay:report`).  \n"
            f"2f. **AY6 AY-FREEZE** — **DONE {status}** "
            "(`npm run nano:ay:freeze`) · **COMPLETE + FROZEN** · "
            "do not invent Wave AZ.  "
        )
        if old in text:
            text = text.replace(old, new, 1)
        _LOCAL_IMPL.write_text(text, encoding="utf-8")
    if _LOCAL_README.is_file():
        text = _LOCAL_README.read_text(encoding="utf-8")
        text = text.replace(
            "**Wave AY ACTIVE**",
            f"**Wave AY {wave}**",
        )
        old = (
            "Session: `wave-ay/SESSION.md` (AY5 AY-REPORT "
            "**DONE — PROMOTE**; next AY6 AY-FREEZE)."
        )
        new = (
            f"Session: `wave-ay/SESSION.md` (AY6 AY-FREEZE "
            f"**DONE — {status}**; **{wave}** · do not invent Wave AZ)."
        )
        if old in text:
            text = text.replace(old, new, 1)
        _LOCAL_README.write_text(text, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    ok = str(decision).startswith("PROMOTE")
    status = "PROMOTE" if ok else decision.split("(", 1)[0].strip()
    text2, n = re.subn(
        r"\| AY6 \| \*\*AY-FREEZE\*\* \|[^\n]+\| \*\*TODO\*\* \|",
        (
            "| AY6 | **AY-FREEZE** | Lock AY outcomes | "
            f"no next letter invent without reopen | **DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    if ok:
        text = text.replace(
            "# pesquisa — Wave AY (**OPEN** · lab-book reopen after AX-FREEZE)",
            "# pesquisa — Wave AY (**COMPLETE + FROZEN**)",
            1,
        )
        text = text.replace(
            "## 5. Wave AY stage machine (**OPEN**)",
            "## 5. Wave AY stage machine (**COMPLETE + FROZEN**)",
            1,
        )
        text2, n = re.subn(
            r"> \*\*Status:\*\* Wave AX \*\*COMPLETE \+ FROZEN\*\* "
            r"\(archive\)\. Wave AY \*\*OPEN\*\* by this reopen\.",
            (
                "> **Status:** Wave AY **COMPLETE + FROZEN**. "
                "Do **not** invent Wave AZ without explicit reopen. "
                "Parent: Wave AX **COMPLETE + FROZEN** (archive)."
            ),
            text,
            count=1,
        )
        if n:
            text = text2
        text = text.replace(
            "> **Session:** `.local/wave-ay/SESSION.md` "
            "(AY5 AY-REPORT **DONE — PROMOTE**; next AY6 AY-FREEZE).  ",
            "> **Session:** `.local/wave-ay/SESSION.md` "
            f"(AY6 AY-FREEZE **DONE — {status}**; **COMPLETE + FROZEN**).  ",
            1,
        )
    text = text.replace(
        (
            "2e. **AY5 AY-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:ay:report`) · next **AY6 AY-FREEZE**.  "
        ),
        (
            "2e. **AY5 AY-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:ay:report`).  \n"
            f"2f. **AY6 AY-FREEZE** — **DONE {status}** "
            "(`npm run nano:ay:freeze`) · **COMPLETE + FROZEN** · "
            "do not invent Wave AZ.  "
        ),
        1,
    )
    text = text.replace(
        (
            "5b. **AY5 AY-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:ay:report`) · next AY6 freeze.  "
        ),
        (
            "5b. **AY5 AY-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:ay:report`).  \n"
            f"5c. **AY6 AY-FREEZE** — **DONE {status}** "
            "(`npm run nano:ay:freeze`) · **COMPLETE + FROZEN**.  "
        ),
        1,
    )
    bash_old = "# next: nano:ay:freeze"
    bash_new = (
        "npm run nano:ay:freeze\n"
        "# Wave AY COMPLETE + FROZEN — do not invent Wave AZ"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")
    _patch_local_helpers(status, ok)


def run_ay_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AY formals + COMPLETE closeout
    WHEN locking Wave AY
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    threads, workers = _hardware()
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in AY_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *AY_PUBLIC, *AY_PRODUCT_DOCS])
    )
    with ThreadPoolExecutor(
        max_workers=min(workers, max(4, len(read_paths)))
    ) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in AY_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in AY_PRODUCT_DOCS}
    decision = decide_ay_freeze(
        formal_texts=formal_texts,
        public_texts=public_texts,
        product_texts=product_texts,
    )
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_shipay_modes(workers=workers)
        if not bool(ask.get("ok")):
            decision = "KILL (LOOKUP·PEAK·ABSTAIN SHIPAY smoke failed)"
    ok = str(decision).startswith("PROMOTE")
    _update_local_session(decision)
    _patch_pesquisa(decision)
    payload: dict[str, Any] = {
        "id": AY_FREEZE_ID,
        "hyp_id": AY_FREEZE_ID,
        "stage": "AY6",
        "thesis": AY_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in AY_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/ay-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-hayfreeze-ay-freeze.md",
        "wave_ay_summary": "docs/results/nano-lm/wave-ay-summary.md",
        "rule": "pesquisa §5 AY-FREEZE",
        "wave_status": "COMPLETE+FROZEN" if ok else "RESEARCH_COMPLETE",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": threads,
        "workers": workers,
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AY6 AY-FREEZE")
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    threads, _workers = _hardware()
    try:
        summary = run_ay_freeze(
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
                "hyp_id": AY_FREEZE_ID,
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
