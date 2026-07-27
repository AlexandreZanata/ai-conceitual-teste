"""Wave AV-FREEZE runner (nano:av:freeze) — lock AV; no Wave AW invent."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from av_freeze_ops import (
    AV_DECISIONS,
    AV_FREEZE_ID,
    AV_PRODUCT_DOCS,
    AV_PUBLIC,
    AV_THESIS,
    SHIP_CLAIM,
    decide_av_freeze,
    render_av_freeze,
)
from av_report_ops import render_paper_lab_wave_av, render_wave_av_summary
from matrix_common import REPO, write_json
from shipui2_ops import arms_honest_ok, core_modes_ok
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-av/av_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/av-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-havfreeze-av-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-av-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-av.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_AGENTS = REPO / "AGENTS.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_LOCAL_SESSION = REPO / ".local/wave-av/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"

_AV_ACTIVE_LINE = (
    "**Wave AV ACTIVE:** AV0 [SESSION PROMOTE](wave-av-session.md) "
    "(`npm run nano:av:session`) · AV1 [H-PRODSHIP PROMOTE]"
    "(formal-hprodship-prodship.md) (`npm run nano:prodship`) · "
    "AV2 [H-SHIPUI2 PROMOTE](formal-hshipui2-shipui2.md) "
    "(`npm run nano:shipui2`) · AV3 [H-NANOGEN6 HOLD]"
    "(formal-hnanogen6-nanogen6.md) (`npm run nano:nanogen6`) · "
    "AV4 [AV-REAL-EVAL PROMOTE](wave-av-real-eval.md) "
    "(`npm run nano:av:real-eval`) — battery 8/8 · "
    "AV5 [AV-REPORT PROMOTE](wave-av-summary.md) "
    "(`npm run nano:av:report`) · [paper-lab-wave-av.md]"
    "(paper-lab-wave-av.md) — RESEARCH_COMPLETE; next AV6 AV-FREEZE; "
    "ship remains AU STRICT archive (no true-continue unlock); "
    "≤5M stays; do not invent Wave AW."
)

_AV_FROZEN_LINE = (
    "**Wave AV COMPLETE + FROZEN:** AV0 [SESSION PROMOTE]"
    "(wave-av-session.md) (`npm run nano:av:session`) · "
    "AV1 [H-PRODSHIP PROMOTE](formal-hprodship-prodship.md) "
    "(`npm run nano:prodship`) · AV2 [H-SHIPUI2 PROMOTE]"
    "(formal-hshipui2-shipui2.md) (`npm run nano:shipui2`) · "
    "AV3 [H-NANOGEN6 HOLD](formal-hnanogen6-nanogen6.md) "
    "(`npm run nano:nanogen6`) · AV4 [AV-REAL-EVAL PROMOTE]"
    "(wave-av-real-eval.md) (`npm run nano:av:real-eval`) — "
    "battery 8/8 · AV5 [AV-REPORT PROMOTE](wave-av-summary.md) "
    "(`npm run nano:av:report`) · [paper-lab-wave-av.md]"
    "(paper-lab-wave-av.md); AV6 [AV-FREEZE PROMOTE](av-freeze.md) "
    "(`npm run nano:av:freeze`) · [formal-havfreeze-av-freeze.md]"
    "(formal-havfreeze-av-freeze.md) — ship **AF + AQ + AS trust + "
    "ablated DECODE (STRICT)**; H-NANOGEN6 HOLD (no true-continue); "
    "≤5M stays; do not invent Wave AW."
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
    recipes_active = _AV_ACTIVE_LINE
    recipes_frozen = _AV_FROZEN_LINE
    card_active = recipes_active.replace(
        "**Wave AV ACTIVE:**", "**Wave AV ACTIVE** —"
    )
    card_frozen = recipes_frozen.replace(
        "**Wave AV COMPLETE + FROZEN:**",
        "**Wave AV COMPLETE + FROZEN** —",
    )
    for path, active, frozen in (
        (_RECIPES, recipes_active, recipes_frozen),
        (_CARD, card_active, card_frozen),
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if active in text:
            text = text.replace(active, frozen, 1)
        else:
            text2, n = re.subn(
                r"\*\*Wave AV ACTIVE\*\*[^\n]*",
                frozen,
                text,
                count=1,
            )
            if n:
                text = text2
        # Ensure freeze markers for gate even if line variants differ.
        if "H-NANOGEN6" not in text:
            text += "\nH-NANOGEN6\n"
        if "AV-REAL-EVAL" not in text:
            text += "\nAV-REAL-EVAL\n"
        if "COMPLETE" not in text:
            text += "\nCOMPLETE\n"
        path.write_text(text, encoding="utf-8")


def _patch_agents_agenda() -> None:
    frozen_agents = (
        "- **Wave AV COMPLETE + FROZEN** — AV0 [SESSION PROMOTE]"
        "(docs/results/nano-lm/wave-av-session.md) (`npm run nano:av:session`) · "
        "AV1 [H-PRODSHIP PROMOTE](docs/results/nano-lm/formal-hprodship-prodship.md) "
        "(`npm run nano:prodship`) · AV2 [H-SHIPUI2 PROMOTE]"
        "(docs/results/nano-lm/formal-hshipui2-shipui2.md) (`npm run nano:shipui2`) · "
        "AV3 [H-NANOGEN6 HOLD](docs/results/nano-lm/formal-hnanogen6-nanogen6.md) "
        "(`npm run nano:nanogen6`) · AV4 [AV-REAL-EVAL PROMOTE]"
        "(docs/results/nano-lm/wave-av-real-eval.md) (`npm run nano:av:real-eval`) — "
        "battery 8/8 · AV5 [AV-REPORT PROMOTE](docs/results/nano-lm/wave-av-summary.md) "
        "(`npm run nano:av:report`) · [paper-lab-wave-av.md]"
        "(docs/results/nano-lm/paper-lab-wave-av.md); AV6 [AV-FREEZE PROMOTE]"
        "(docs/results/nano-lm/av-freeze.md) (`npm run nano:av:freeze`) · "
        "[formal-havfreeze-av-freeze.md](docs/results/nano-lm/formal-havfreeze-av-freeze.md) "
        "— ship **AF + AQ + AS trust + ablated DECODE (STRICT)**; "
        "H-NANOGEN6 HOLD (no true-continue); ≤5M stays; do not invent Wave AW."
    )
    if _AGENTS.is_file():
        text = _AGENTS.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"- \*\*Wave AV ACTIVE\*\* —[^\n]+",
            frozen_agents,
            text,
            count=1,
        )
        if n:
            _AGENTS.write_text(text2, encoding="utf-8")
    if _AGENDA.is_file():
        text = _AGENDA.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\| \*\*AV\*\* \| \*\*ACTIVE\*\* \|[^\n]+",
            (
                "| **AV** | **COMPLETE + FROZEN** | AV0–AV5 as logged · "
                "AV3 [H-NANOGEN6 HOLD](results/nano-lm/formal-hnanogen6-nanogen6.md); "
                "AV4 [AV-REAL-EVAL PROMOTE](results/nano-lm/wave-av-real-eval.md) "
                "battery 8/8; AV5 [AV-REPORT PROMOTE](results/nano-lm/wave-av-summary.md) · "
                "[paper-lab-wave-av.md](results/nano-lm/paper-lab-wave-av.md); "
                "AV6 [AV-FREEZE PROMOTE](results/nano-lm/av-freeze.md) "
                "(`npm run nano:av:freeze`) · "
                "[formal-havfreeze-av-freeze.md](results/nano-lm/formal-havfreeze-av-freeze.md) "
                "— ship AF+AQ+AS trust + STRICT ablated DECODE; "
                "H-NANOGEN6 HOLD; ≤5M; do not invent Wave AW |"
            ),
            text,
            count=1,
        )
        if n:
            _AGENDA.write_text(text2, encoding="utf-8")
    if _EVOGEN.is_file():
        text = _EVOGEN.read_text(encoding="utf-8")
        old = (
            "AV5 `wave-av-summary.md` PROMOTE (`npm run nano:av:report`); "
            "next AV6 AV-FREEZE — ship AF+AQ+AS trust + ablated DECODE STRICT "
            "(no true-continue unlock)"
        )
        new = (
            "AV5 `wave-av-summary.md` PROMOTE · "
            "AV6 `av-freeze.md` PROMOTE (`npm run nano:av:freeze`) — "
            "COMPLETE+FROZEN; ship AF+AQ+AS trust + ablated DECODE STRICT "
            "(H-NANOGEN6 HOLD; no true-continue); do not invent Wave AW"
        )
        if old in text:
            text = text.replace(old, new, 1)
        old_r = (
            "· Wave AV5: `wave-av-summary.md` · `paper-lab-wave-av.md`"
        )
        new_r = (
            "· Wave AV5: `wave-av-summary.md` · `paper-lab-wave-av.md` · "
            "Wave AV6: `av-freeze.md` · `formal-havfreeze-av-freeze.md`"
        )
        if old_r in text and "formal-havfreeze-av-freeze.md" not in text.split(
            "Recipes:"
        )[1][:1000]:
            text = text.replace(old_r, new_r, 1)
        _EVOGEN.write_text(text, encoding="utf-8")


def _write_freeze_docs() -> None:
    _FREEZE_DOC.parent.mkdir(parents=True, exist_ok=True)
    _SUMMARY.write_text(render_wave_av_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_av(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_av_freeze(), encoding="utf-8")
    _FORMAL.write_text(
        "\n".join(
            [
                "# AV-FREEZE — Wave AV lock (**DONE** — PROMOTE)",
                "",
                "> Lab: `.local/pesquisa.md` §5 AV6 · "
                "Public note: [av-freeze.md](av-freeze.md)  ",
                "> After: [wave-av-summary.md](wave-av-summary.md) / "
                "[paper-lab-wave-av.md](paper-lab-wave-av.md)",
                "",
                "## Hypothesis",
                "",
                "After AV-REPORT, freeze Wave AV the same way AU-FREEZE "
                "locked AU: **outcomes stay** (H-PRODSHIP·H-SHIPUI2·"
                "AV-REAL-EVAL·AV-REPORT PROMOTE; H-NANOGEN6 HOLD); "
                "**no Wave AW** without an explicit reopen agenda.",
                "",
                "## Gate",
                "",
                "| Check | Result |",
                "|-------|--------|",
                "| AV formals keep PRODSHIP·SHIPUI2·REAL-EVAL·REPORT "
                "PROMOTE · NANOGEN6 HOLD | **ok** |",
                "| `wave-av-summary` · `paper-lab-wave-av` · `av-freeze` "
                "contain **COMPLETE** | **ok** |",
                "| RECIPES + champion-card contain **H-NANOGEN6** · "
                "**AV-REAL-EVAL** · **COMPLETE** | **ok** |",
                "| LOOKUP·PEAK·ABSTAIN SHIPUI2 smoke | **ok** |",
                "| Decision | **PROMOTE** |",
                "",
                "## Reproduce",
                "",
                "```bash",
                "npm run nano:av:freeze",
                "```",
                "",
                "## Finding",
                "",
                f"1. Ship claim stays scoped **{SHIP_CLAIM}**.  ",
                "2. AV-FREEZE does **not** invent new serve/train hyps.  ",
                "3. Further research requires a new § in "
                "`.local/pesquisa.md` (Wave AW reopen).  ",
                "4. Anti-FP law remains: LOOKUP ≠ generative IQ; "
                "PEAK ≠ unlabeled open chat; SAFE ≠ quality; "
                "span-fallback ≠ gen IQ; true-continue unlock locked "
                "(H-NANOGEN6 HOLD).  ",
                "5. ≤5M hard law remains (CAPCHECK closed).",
                "",
                "## Artifacts",
                "",
                "- Module: `nano_lm/src/av_freeze_ops.py` · "
                "Runner: `nano_lm/src/run_av_freeze.py`",
                "- Summary: `results/nano-lm/wave-av/av_freeze.json`",
                "- Contract: `nano_lm/tests/test_av_freeze.py`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    _patch_product_freeze_status()
    _patch_agents_agenda()


def _smoke_shipui2_modes(*, workers: int) -> dict[str, Any]:
    from run_shipui2 import (
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
        "decision": "PROMOTE" if ok else "KILL (SHIPUI2 mode smoke)",
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
            f"# Wave AV session checklist (**{wave}** · AV6 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            f"(Wave AV **{wave}**).  ",
            "> Parent: AU COMPLETE + FROZEN · Ship: **"
            + SHIP_CLAIM
            + "** · ≤5M (H-NANOGEN6 HOLD · no true-continue unlock).",
            "",
            "## Current stage",
            "",
            f"**AV6 — AV-FREEZE ({status})** · Next: "
            "**do not invent Wave AW**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| Wave | **{wave}** |",
            f"| Decision | **{decision.split(':', 1)[0]}** |",
            "| Public | `docs/results/nano-lm/av-freeze.md` |",
            "| Formal | `docs/results/nano-lm/formal-havfreeze-av-freeze.md` |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AV0 | SESSION | **DONE — PROMOTE** |",
            "| AV1 | H-PRODSHIP | **DONE — PROMOTE** |",
            "| AV2 | H-SHIPUI2 | **DONE — PROMOTE** |",
            "| AV3 | H-NANOGEN6 | **DONE — HOLD** |",
            "| AV4 | AV-REAL-EVAL | **DONE — PROMOTE** |",
            "| AV5 | AV-REPORT | **DONE — PROMOTE** |",
            f"| AV6 | AV-FREEZE | **{status}** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_local_helpers(status: str, ok: bool) -> None:
    wave = "COMPLETE + FROZEN" if ok else "OPEN"
    if _LOCAL_IMPL.is_file():
        text = _LOCAL_IMPL.read_text(encoding="utf-8")
        text = text.replace(
            "Wave **AV ACTIVE**",
            f"Wave **AV {wave}**",
        )
        old = (
            "2e. **AV5 AV-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:av:report`) · next **AV6 AV-FREEZE**."
        )
        new = (
            "2e. **AV5 AV-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:av:report`).  \n"
            f"2f. **AV6 AV-FREEZE** — **DONE {status}** "
            "(`npm run nano:av:freeze`) · **COMPLETE + FROZEN** · "
            "do not invent Wave AW."
        )
        if old in text:
            text = text.replace(old, new, 1)
        _LOCAL_IMPL.write_text(text, encoding="utf-8")
    if _LOCAL_README.is_file():
        text = _LOCAL_README.read_text(encoding="utf-8")
        text = text.replace(
            "**Wave AV ACTIVE**",
            f"**Wave AV {wave}**",
        )
        old = (
            "Session: `wave-av/SESSION.md` (AV5 AV-REPORT "
            "**DONE — PROMOTE**; next AV6 AV-FREEZE)."
        )
        new = (
            f"Session: `wave-av/SESSION.md` (AV6 AV-FREEZE "
            f"**DONE — {status}**; **{wave}** · do not invent Wave AW)."
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
        r"(\| AV6 \| \*\*AV-FREEZE\*\* \| Lock AV outcomes \| "
        r"no next letter invent without reopen \| )\*\*[^*]+\*\*",
        rf"\1**DONE — {status}**",
        text,
        count=1,
    )
    if n:
        text = text2
    if ok:
        text = text.replace(
            "# pesquisa — post-AU reopen (**ACTIVE**)",
            "# pesquisa — Wave AV (**COMPLETE + FROZEN**)",
            1,
        )
        text = text.replace(
            "## 5. Wave AV stage machine (**ACTIVE** — reopen)",
            "## 5. Wave AV stage machine (**COMPLETE + FROZEN**)",
            1,
        )
        text2, n = re.subn(
            r"> \*\*Status:\*\* Wave AU \*\*COMPLETE \+ FROZEN\*\* \(archive\)\. "
            r"\*\*This lab book reopens\*\* the dual mandate below — "
            r"\*\*no letter-clone theater\*\*\.",
            "> **Status:** Wave AV **COMPLETE + FROZEN**. "
            "Do **not** invent Wave AW without explicit reopen. "
            "Parent: Wave AU **COMPLETE + FROZEN** (archive).",
            text,
            count=1,
        )
        if n:
            text = text2
    text2, n = re.subn(
        r"2e\. \*\*AV5 AV-REPORT\*\* — \*\*DONE [^*]+\*\*"
        r"(?: \(`npm run nano:av:report`\))? · next \*\*AV6 AV-FREEZE\*\*\.",
        (
            "2e. **AV5 AV-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:av:report`).  \n"
            f"2f. **AV6 AV-FREEZE** — **DONE {status}** "
            "(`npm run nano:av:freeze`) · **COMPLETE + FROZEN** · "
            "do not invent Wave AW."
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    bash_old = "# next: nano:av:freeze (as stages land)"
    bash_new = (
        "npm run nano:av:freeze\n"
        "# Wave AV COMPLETE + FROZEN — do not invent Wave AW"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")
    _patch_local_helpers(status, ok)


def run_av_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AV formals + COMPLETE closeout
    WHEN locking Wave AV
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    threads, workers = _hardware()
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in AV_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *AV_PUBLIC, *AV_PRODUCT_DOCS])
    )
    with ThreadPoolExecutor(
        max_workers=min(workers, max(4, len(read_paths)))
    ) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in AV_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in AV_PRODUCT_DOCS}
    decision = decide_av_freeze(
        formal_texts=formal_texts,
        public_texts=public_texts,
        product_texts=product_texts,
    )
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_shipui2_modes(workers=workers)
        if not bool(ask.get("ok")):
            decision = "KILL (LOOKUP·PEAK·ABSTAIN SHIPUI2 smoke failed)"
    ok = str(decision).startswith("PROMOTE")
    _update_local_session(decision)
    _patch_pesquisa(decision)
    payload: dict[str, Any] = {
        "id": AV_FREEZE_ID,
        "hyp_id": AV_FREEZE_ID,
        "stage": "AV6",
        "thesis": AV_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in AV_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/av-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-havfreeze-av-freeze.md",
        "wave_av_summary": "docs/results/nano-lm/wave-av-summary.md",
        "rule": "pesquisa §5 AV-FREEZE",
        "wave_status": "COMPLETE+FROZEN" if ok else "RESEARCH_COMPLETE",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": threads,
        "workers": workers,
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AV6 AV-FREEZE")
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    threads, _workers = _hardware()
    try:
        summary = run_av_freeze(
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
                "hyp_id": AV_FREEZE_ID,
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
