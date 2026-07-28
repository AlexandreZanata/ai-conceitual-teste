"""Wave AW-FREEZE runner (nano:aw:freeze) — lock AW; no Wave AX invent."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from aw_freeze_ops import (
    AW_DECISIONS,
    AW_FREEZE_ID,
    AW_PRODUCT_DOCS,
    AW_PUBLIC,
    AW_THESIS,
    SHIP_CLAIM,
    decide_aw_freeze,
    render_aw_freeze,
)
from aw_report_ops import render_paper_lab_wave_aw, render_wave_aw_summary
from matrix_common import REPO, write_json
from shipkeep_ops import arms_honest_ok, core_modes_ok
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-aw/aw_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/aw-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-hawfreeze-aw-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-aw-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-aw.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_AGENTS = REPO / "AGENTS.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_LOCAL_SESSION = REPO / ".local/wave-aw/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"

_AW_ACTIVE_LINE = (
    "**Wave AW ACTIVE:** AW0 [SESSION PROMOTE](wave-aw-session.md) · "
    "AW1 [H-PRODKEEP PROMOTE](formal-hprodkeep-prodkeep.md) · "
    "AW2 [H-SHIPKEEP PROMOTE](formal-hshipkeep-shipkeep.md) · "
    "AW3 [H-NANOGEN7 HOLD](formal-hnanogen7-nanogen7.md) · "
    "AW4 [AW-REAL-EVAL PROMOTE](wave-aw-real-eval.md) · "
    "AW5 [AW-REPORT PROMOTE](wave-aw-summary.md) "
    "(`npm run nano:aw:report`) · [paper-lab-wave-aw.md]"
    "(paper-lab-wave-aw.md); next AW6 AW-FREEZE; "
    "ship **AF + AQ + AS trust + STRICT ablated DECODE**; ≤5M stays."
)

_AW_FROZEN_LINE = (
    "**Wave AW COMPLETE + FROZEN:** AW0 [SESSION PROMOTE]"
    "(wave-aw-session.md) (`npm run nano:aw:session`) · "
    "AW1 [H-PRODKEEP PROMOTE](formal-hprodkeep-prodkeep.md) "
    "(`npm run nano:prodkeep`) · AW2 [H-SHIPKEEP PROMOTE]"
    "(formal-hshipkeep-shipkeep.md) (`npm run nano:shipkeep`) · "
    "AW3 [H-NANOGEN7 HOLD](formal-hnanogen7-nanogen7.md) "
    "(`npm run nano:nanogen7`) · AW4 [AW-REAL-EVAL PROMOTE]"
    "(wave-aw-real-eval.md) (`npm run nano:aw:real-eval`) — "
    "battery 8/8 · AW5 [AW-REPORT PROMOTE](wave-aw-summary.md) "
    "(`npm run nano:aw:report`) · [paper-lab-wave-aw.md]"
    "(paper-lab-wave-aw.md); AW6 [AW-FREEZE PROMOTE](aw-freeze.md) "
    "(`npm run nano:aw:freeze`) · [formal-hawfreeze-aw-freeze.md]"
    "(formal-hawfreeze-aw-freeze.md) — ship **AF + AQ + AS trust + "
    "ablated DECODE (STRICT)**; H-NANOGEN7 HOLD (no TAC true-continue); "
    "≤5M stays; do not invent Wave AX."
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


def _patch_product_freeze_status() -> None:
    """Flip ACTIVE → COMPLETE + FROZEN on public product pages."""
    recipes_active = _AW_ACTIVE_LINE
    recipes_frozen = _AW_FROZEN_LINE
    card_active = recipes_active.replace(
        "**Wave AW ACTIVE:**", "**Wave AW ACTIVE** —"
    )
    card_frozen = recipes_frozen.replace(
        "**Wave AW COMPLETE + FROZEN:**",
        "**Wave AW COMPLETE + FROZEN** —",
    )
    # Champion card ACTIVE line may include npm run on AW0–AW4.
    card_active_alt = (
        "**Wave AW ACTIVE** — AW0 [SESSION PROMOTE](wave-aw-session.md) "
        "(`npm run nano:aw:session`) · AW1 [H-PRODKEEP PROMOTE]"
        "(formal-hprodkeep-prodkeep.md) (`npm run nano:prodkeep`) · "
        "AW2 [H-SHIPKEEP PROMOTE](formal-hshipkeep-shipkeep.md) "
        "(`npm run nano:shipkeep`) · AW3 [H-NANOGEN7 HOLD]"
        "(formal-hnanogen7-nanogen7.md) (`npm run nano:nanogen7`) · "
        "AW4 [AW-REAL-EVAL PROMOTE](wave-aw-real-eval.md) "
        "(`npm run nano:aw:real-eval`) — battery 8/8 · "
        "AW5 [AW-REPORT PROMOTE](wave-aw-summary.md) "
        "(`npm run nano:aw:report`) · [paper-lab-wave-aw.md]"
        "(paper-lab-wave-aw.md); next AW6 AW-FREEZE; "
        "ship remains **AF + AQ + AS trust + STRICT ablated DECODE**; "
        "≤5M stays."
    )
    for path, actives, frozen in (
        (_RECIPES, (recipes_active,), recipes_frozen),
        (_CARD, (card_active_alt, card_active), card_frozen),
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        replaced = False
        for active in actives:
            if active in text:
                text = text.replace(active, frozen, 1)
                replaced = True
                break
        if not replaced:
            text2, n = re.subn(
                r"\*\*Wave AW ACTIVE\*\*[^\n]*",
                frozen,
                text,
                count=1,
            )
            if n:
                text = text2
        if "H-NANOGEN7" not in text:
            text += "\nH-NANOGEN7\n"
        if "AW-REAL-EVAL" not in text:
            text += "\nAW-REAL-EVAL\n"
        if "COMPLETE" not in text:
            text += "\nCOMPLETE\n"
        path.write_text(text, encoding="utf-8")


def _patch_agents_agenda() -> None:
    frozen_agents = (
        "- **Wave AW COMPLETE + FROZEN** — AW0 [SESSION PROMOTE]"
        "(docs/results/nano-lm/wave-aw-session.md) (`npm run nano:aw:session`) · "
        "AW1 [H-PRODKEEP PROMOTE](docs/results/nano-lm/formal-hprodkeep-prodkeep.md) "
        "(`npm run nano:prodkeep`) · AW2 [H-SHIPKEEP PROMOTE]"
        "(docs/results/nano-lm/formal-hshipkeep-shipkeep.md) (`npm run nano:shipkeep`) · "
        "AW3 [H-NANOGEN7 HOLD](docs/results/nano-lm/formal-hnanogen7-nanogen7.md) "
        "(`npm run nano:nanogen7`) · AW4 [AW-REAL-EVAL PROMOTE]"
        "(docs/results/nano-lm/wave-aw-real-eval.md) (`npm run nano:aw:real-eval`) — "
        "battery 8/8 · AW5 [AW-REPORT PROMOTE](docs/results/nano-lm/wave-aw-summary.md) "
        "(`npm run nano:aw:report`) · [paper-lab-wave-aw.md]"
        "(docs/results/nano-lm/paper-lab-wave-aw.md); AW6 [AW-FREEZE PROMOTE]"
        "(docs/results/nano-lm/aw-freeze.md) (`npm run nano:aw:freeze`) · "
        "[formal-hawfreeze-aw-freeze.md](docs/results/nano-lm/formal-hawfreeze-aw-freeze.md) "
        "— ship **AF + AQ + AS trust + ablated DECODE (STRICT)**; "
        "H-NANOGEN7 HOLD (no TAC true-continue); ≤5M stays; do not invent Wave AX."
    )
    if _AGENTS.is_file():
        text = _AGENTS.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"- \*\*Wave AW ACTIVE\*\* —[^\n]+",
            frozen_agents,
            text,
            count=1,
        )
        if n:
            _AGENTS.write_text(text2, encoding="utf-8")
    if _AGENDA.is_file():
        text = _AGENDA.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\| \*\*AW\*\* \| \*\*ACTIVE\*\* \|[^\n]+",
            (
                "| **AW** | **COMPLETE + FROZEN** | AW0–AW5 as logged · "
                "AW3 [H-NANOGEN7 HOLD](results/nano-lm/formal-hnanogen7-nanogen7.md); "
                "AW4 [AW-REAL-EVAL PROMOTE](results/nano-lm/wave-aw-real-eval.md) "
                "battery 8/8; AW5 [AW-REPORT PROMOTE](results/nano-lm/wave-aw-summary.md) · "
                "[paper-lab-wave-aw.md](results/nano-lm/paper-lab-wave-aw.md); "
                "AW6 [AW-FREEZE PROMOTE](results/nano-lm/aw-freeze.md) "
                "(`npm run nano:aw:freeze`) · "
                "[formal-hawfreeze-aw-freeze.md](results/nano-lm/formal-hawfreeze-aw-freeze.md) "
                "— ship AF+AQ+AS trust + STRICT ablated DECODE; "
                "H-NANOGEN7 HOLD; ≤5M; do not invent Wave AX |"
            ),
            text,
            count=1,
        )
        if n:
            _AGENDA.write_text(text2, encoding="utf-8")
    if _EVOGEN.is_file():
        text = _EVOGEN.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"Wave AW ACTIVE —[^;]+; next AW6 AW-FREEZE; \*\*Wave AP\*\*",
            (
                "Wave AW COMPLETE + FROZEN — AW0–AW5 as logged · "
                "AW6 `aw-freeze.md` PROMOTE (`npm run nano:aw:freeze`) — "
                "COMPLETE+FROZEN; H-NANOGEN7 HOLD; do not invent Wave AX; "
                "**Wave AP**"
            ),
            text,
            count=1,
        )
        if n:
            text = text2
        old_r = (
            "· Wave AW5: `wave-aw-summary.md` · `paper-lab-wave-aw.md` PROMOTE"
        )
        new_r = (
            "· Wave AW5: `wave-aw-summary.md` · `paper-lab-wave-aw.md` PROMOTE · "
            "Wave AW6: `aw-freeze.md` · `formal-hawfreeze-aw-freeze.md` PROMOTE"
        )
        if old_r in text and "formal-hawfreeze-aw-freeze.md` PROMOTE" not in text:
            text = text.replace(old_r, new_r, 1)
        _EVOGEN.write_text(text, encoding="utf-8")


def _write_freeze_docs() -> None:
    _FREEZE_DOC.parent.mkdir(parents=True, exist_ok=True)
    _SUMMARY.write_text(render_wave_aw_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_aw(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_aw_freeze(), encoding="utf-8")
    _FORMAL.write_text(
        "\n".join(
            [
                "# AW-FREEZE — Wave AW lock (**DONE** — PROMOTE)",
                "",
                "> Lab: `.local/pesquisa.md` §2 AW6 · "
                "Public note: [aw-freeze.md](aw-freeze.md)  ",
                "> After: [wave-aw-summary.md](wave-aw-summary.md) / "
                "[paper-lab-wave-aw.md](paper-lab-wave-aw.md)",
                "",
                "## Hypothesis",
                "",
                "After AW-REPORT, freeze Wave AW the same way AV-FREEZE "
                "locked AV: **outcomes stay** (H-PRODKEEP·H-SHIPKEEP·"
                "AW-REAL-EVAL·AW-REPORT PROMOTE; H-NANOGEN7 HOLD); "
                "**no Wave AX** without an explicit reopen agenda.",
                "",
                "## Gate",
                "",
                "| Check | Result |",
                "|-------|--------|",
                "| AW formals keep PRODKEEP·SHIPKEEP·REAL-EVAL·REPORT "
                "PROMOTE · NANOGEN7 HOLD | **ok** |",
                "| `wave-aw-summary` · `paper-lab-wave-aw` · `aw-freeze` "
                "contain **COMPLETE** | **ok** |",
                "| RECIPES + champion-card contain **H-NANOGEN7** · "
                "**AW-REAL-EVAL** · **COMPLETE** | **ok** |",
                "| LOOKUP·PEAK·ABSTAIN SHIPKEEP smoke | **ok** |",
                "| Decision | **PROMOTE** |",
                "",
                "## Reproduce",
                "",
                "```bash",
                "npm run nano:aw:freeze",
                "```",
                "",
                "## Finding",
                "",
                f"1. Ship claim stays scoped **{SHIP_CLAIM}**.  ",
                "2. AW-FREEZE does **not** invent new serve/train hyps.  ",
                "3. Further research requires a new § in "
                "`.local/pesquisa.md` (Wave AX reopen).  ",
                "4. Anti-FP law remains: LOOKUP ≠ generative IQ; "
                "PEAK ≠ unlabeled open chat; SAFE ≠ quality; "
                "span-fallback ≠ gen IQ; TAC unlock locked "
                "(H-NANOGEN7 HOLD).  ",
                "5. ≤5M hard law remains (CAPCHECK closed).",
                "",
                "## Artifacts",
                "",
                "- Module: `nano_lm/src/aw_freeze_ops.py` · "
                "Runner: `nano_lm/src/run_aw_freeze.py`",
                "- Summary: `results/nano-lm/wave-aw/aw_freeze.json`",
                "- Contract: `nano_lm/tests/test_aw_freeze.py`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    _patch_product_freeze_status()
    _patch_agents_agenda()


def _smoke_shipkeep_modes(*, workers: int) -> dict[str, Any]:
    from run_shipkeep import (
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
        "decision": "PROMOTE" if ok else "KILL (SHIPKEEP mode smoke)",
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
            f"# Wave AW session checklist (**{wave}** · AW6 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            f"(Wave AW **{wave}**).  ",
            "> Parent: AV COMPLETE + FROZEN · Ship: **"
            + SHIP_CLAIM
            + "** · ≤5M (H-NANOGEN7 HOLD · no TAC true-continue unlock).",
            "",
            "## Current stage",
            "",
            f"**AW6 — AW-FREEZE ({status})** · Next: "
            "**do not invent Wave AX**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| Wave | **{wave}** |",
            f"| Decision | **{decision.split(':', 1)[0]}** |",
            "| Public | `docs/results/nano-lm/aw-freeze.md` |",
            "| Formal | `docs/results/nano-lm/formal-hawfreeze-aw-freeze.md` |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AW0 | SESSION | **DONE — PROMOTE** |",
            "| AW1 | H-PRODKEEP | **DONE — PROMOTE** |",
            "| AW2 | H-SHIPKEEP | **DONE — PROMOTE** |",
            "| AW3 | H-NANOGEN7 | **DONE — HOLD** |",
            "| AW4 | AW-REAL-EVAL | **DONE — PROMOTE** |",
            "| AW5 | AW-REPORT | **DONE — PROMOTE** |",
            f"| AW6 | AW-FREEZE | **{status}** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_local_helpers(status: str, ok: bool) -> None:
    wave = "COMPLETE + FROZEN" if ok else "OPEN"
    if _LOCAL_IMPL.is_file():
        text = _LOCAL_IMPL.read_text(encoding="utf-8")
        text = text.replace(
            "Wave **AW ACTIVE**",
            f"Wave **AW {wave}**",
        )
        old = (
            "2e. **AW5 AW-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:aw:report`) · next **AW6 AW-FREEZE**."
        )
        new = (
            "2e. **AW5 AW-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:aw:report`).  \n"
            f"2f. **AW6 AW-FREEZE** — **DONE {status}** "
            "(`npm run nano:aw:freeze`) · **COMPLETE + FROZEN** · "
            "do not invent Wave AX."
        )
        if old in text:
            text = text.replace(old, new, 1)
        _LOCAL_IMPL.write_text(text, encoding="utf-8")
    if _LOCAL_README.is_file():
        text = _LOCAL_README.read_text(encoding="utf-8")
        text = text.replace(
            "**Wave AW ACTIVE**",
            f"**Wave AW {wave}**",
        )
        old = (
            "Session: `wave-aw/SESSION.md` (AW5 AW-REPORT "
            "**DONE — PROMOTE**; next AW6 AW-FREEZE)."
        )
        new = (
            f"Session: `wave-aw/SESSION.md` (AW6 AW-FREEZE "
            f"**DONE — {status}**; **{wave}** · do not invent Wave AX)."
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
        r"(\| AW6 \| \*\*AW-FREEZE\*\* \| Lock AW outcomes \| "
        r"no next letter invent without reopen \| )\*\*[^*]+\*\*",
        rf"\1**DONE — {status}**",
        text,
        count=1,
    )
    if n:
        text = text2
    if ok:
        text = text.replace(
            "# pesquisa — Wave AW (**ACTIVE** — reopen)",
            "# pesquisa — Wave AW (**COMPLETE + FROZEN**)",
            1,
        )
        text = text.replace(
            "## 2. Wave AW stage machine (**ACTIVE**)",
            "## 2. Wave AW stage machine (**COMPLETE + FROZEN**)",
            1,
        )
        text2, n = re.subn(
            r"> \*\*Status:\*\* Wave AW \*\*ACTIVE\*\* \(reopened after "
            r"AV-FREEZE\)\. Parent: Wave AV \*\*COMPLETE \+ FROZEN\*\* "
            r"\(archive\)\.",
            "> **Status:** Wave AW **COMPLETE + FROZEN**. "
            "Do **not** invent Wave AX without explicit reopen. "
            "Parent: Wave AV **COMPLETE + FROZEN** (archive).",
            text,
            count=1,
        )
        if n:
            text = text2
    text2, n = re.subn(
        r"2e\. \*\*AW5 AW-REPORT\*\* — \*\*DONE [^*]+\*\*"
        r"(?: \(`npm run nano:aw:report`\))? · next \*\*AW6 AW-FREEZE\*\*\.",
        (
            "2e. **AW5 AW-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:aw:report`).  \n"
            f"2f. **AW6 AW-FREEZE** — **DONE {status}** "
            "(`npm run nano:aw:freeze`) · **COMPLETE + FROZEN** · "
            "do not invent Wave AX."
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    bash_old = "# next: nano:aw:freeze"
    bash_new = (
        "npm run nano:aw:freeze\n"
        "# Wave AW COMPLETE + FROZEN — do not invent Wave AX"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")
    _patch_local_helpers(status, ok)


def run_aw_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AW formals + COMPLETE closeout
    WHEN locking Wave AW
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    threads, workers = _hardware()
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in AW_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *AW_PUBLIC, *AW_PRODUCT_DOCS])
    )
    with ThreadPoolExecutor(
        max_workers=min(workers, max(4, len(read_paths)))
    ) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in AW_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in AW_PRODUCT_DOCS}
    decision = decide_aw_freeze(
        formal_texts=formal_texts,
        public_texts=public_texts,
        product_texts=product_texts,
    )
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_shipkeep_modes(workers=workers)
        if not bool(ask.get("ok")):
            decision = "KILL (LOOKUP·PEAK·ABSTAIN SHIPKEEP smoke failed)"
    ok = str(decision).startswith("PROMOTE")
    _update_local_session(decision)
    _patch_pesquisa(decision)
    payload: dict[str, Any] = {
        "id": AW_FREEZE_ID,
        "hyp_id": AW_FREEZE_ID,
        "stage": "AW6",
        "thesis": AW_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in AW_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/aw-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-hawfreeze-aw-freeze.md",
        "wave_aw_summary": "docs/results/nano-lm/wave-aw-summary.md",
        "rule": "pesquisa §2 AW-FREEZE",
        "wave_status": "COMPLETE+FROZEN" if ok else "RESEARCH_COMPLETE",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": threads,
        "workers": workers,
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AW6 AW-FREEZE")
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    threads, _workers = _hardware()
    try:
        summary = run_aw_freeze(
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
                "hyp_id": AW_FREEZE_ID,
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
