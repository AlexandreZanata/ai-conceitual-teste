"""Wave AX-FREEZE runner (nano:ax:freeze) — lock AX; no Wave AY invent."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from ax_freeze_ops import (
    AX_DECISIONS,
    AX_FREEZE_ID,
    AX_PRODUCT_DOCS,
    AX_PUBLIC,
    AX_THESIS,
    SHIP_CLAIM,
    decide_ax_freeze,
    render_ax_freeze,
)
from ax_report_ops import render_paper_lab_wave_ax, render_wave_ax_summary
from matrix_common import REPO, write_json
from shipux_ops import arms_honest_ok, core_modes_ok
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-ax/ax_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/ax-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-haxfreeze-ax-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-ax-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-ax.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_AGENTS = REPO / "AGENTS.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_SESSION_PUB = REPO / "docs/results/nano-lm/wave-ax-session.md"
_LOCAL_SESSION = REPO / ".local/wave-ax/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"

_AX_FROZEN_RECIPES = (
    "**Wave AX COMPLETE + FROZEN:** AX0 [SESSION PROMOTE]"
    "(wave-ax-session.md) (`npm run nano:ax:session`) · "
    "AX1 [H-PRODNAT PROMOTE](formal-hprodnat-prodnat.md) "
    "(`npm run nano:prodnat`) · AX2 [H-SHIPUX PROMOTE]"
    "(formal-hshipux-shipux.md) (`npm run nano:shipux`) · "
    "AX3 [H-NANOGEN8 DEFER](formal-hnanogen8-nanogen8.md) "
    "(`npm run nano:nanogen8`) · AX4 [AX-REAL-EVAL PROMOTE]"
    "(wave-ax-real-eval.md) (`npm run nano:ax:real-eval`) — "
    "battery 8/8 · AX5 [AX-REPORT PROMOTE](wave-ax-summary.md) "
    "(`npm run nano:ax:report`) · [paper-lab-wave-ax.md]"
    "(paper-lab-wave-ax.md); AX6 [AX-FREEZE PROMOTE](ax-freeze.md) "
    "(`npm run nano:ax:freeze`) · [formal-haxfreeze-ax-freeze.md]"
    "(formal-haxfreeze-ax-freeze.md) — ship **AF + AQ + AS trust + "
    "ablated DECODE (STRICT)**; H-NANOGEN8 DEFER (NANOGEN6·7 HOLD stand); "
    "≤5M stays; do not invent Wave AY."
)

_AX_FROZEN_CARD = _AX_FROZEN_RECIPES.replace(
    "**Wave AX COMPLETE + FROZEN:**",
    "**Wave AX COMPLETE + FROZEN** —",
)

_AX_FROZEN_AGENTS = (
    "- **Wave AX COMPLETE + FROZEN** — AX0 [SESSION PROMOTE]"
    "(docs/results/nano-lm/wave-ax-session.md) (`npm run nano:ax:session`) · "
    "AX1 [H-PRODNAT PROMOTE](docs/results/nano-lm/formal-hprodnat-prodnat.md) "
    "(`npm run nano:prodnat`) · AX2 [H-SHIPUX PROMOTE]"
    "(docs/results/nano-lm/formal-hshipux-shipux.md) (`npm run nano:shipux`) · "
    "AX3 [H-NANOGEN8 DEFER](docs/results/nano-lm/formal-hnanogen8-nanogen8.md) "
    "(`npm run nano:nanogen8`) · AX4 [AX-REAL-EVAL PROMOTE]"
    "(docs/results/nano-lm/wave-ax-real-eval.md) (`npm run nano:ax:real-eval`) — "
    "battery 8/8 · AX5 [AX-REPORT PROMOTE](docs/results/nano-lm/wave-ax-summary.md) "
    "(`npm run nano:ax:report`) · [paper-lab-wave-ax.md]"
    "(docs/results/nano-lm/paper-lab-wave-ax.md); AX6 [AX-FREEZE PROMOTE]"
    "(docs/results/nano-lm/ax-freeze.md) (`npm run nano:ax:freeze`) · "
    "[formal-haxfreeze-ax-freeze.md](docs/results/nano-lm/formal-haxfreeze-ax-freeze.md) "
    "— ship **AF + AQ + AS trust + ablated DECODE (STRICT)**; "
    "H-NANOGEN8 DEFER (NANOGEN6·7 HOLD stand); ≤5M stays; do not invent Wave AY."
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
    if "H-NANOGEN8" not in text:
        text += "\nH-NANOGEN8\n"
    if "AX-REAL-EVAL" not in text:
        text += "\nAX-REAL-EVAL\n"
    if "COMPLETE" not in text:
        text += "\nCOMPLETE\n"
    return text


def _patch_product_freeze_status() -> None:
    """Flip ACTIVE → COMPLETE + FROZEN on public product pages."""
    for path, frozen in (
        (_RECIPES, _AX_FROZEN_RECIPES),
        (_CARD, _AX_FROZEN_CARD),
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\*\*Wave AX ACTIVE\*\*[^\n]*",
            frozen,
            text,
            count=1,
        )
        if n:
            text = text2
        elif "**Wave AX COMPLETE + FROZEN**" not in text:
            # Append near other wave closeouts (never prepend file header).
            text = text.rstrip() + "\n" + frozen + "\n"
        # Idempotent: collapse accidental duplicate COMPLETE lines.
        text = re.sub(
            r"(\*\*Wave AX COMPLETE \+ FROZEN\*\*:[^\n]*\n)"
            r"(?:\*\*Wave AX COMPLETE \+ FROZEN\*\*:[^\n]*\n)+",
            r"\1",
            text,
        )
        if "Wave AX6 AX-FREEZE" not in text and path == _RECIPES:
            needle = (
                "| Wave AX5 AX-REPORT | [wave-ax-summary.md]"
                "(wave-ax-summary.md) · [paper-lab-wave-ax.md]"
                "(paper-lab-wave-ax.md) **PROMOTE** "
                "(`npm run nano:ax:report`) — anti-FP · "
                "NANOGEN6/7 HOLD cited · gen DEFER |\n"
            )
            row = (
                "| Wave AX6 AX-FREEZE | [ax-freeze.md](ax-freeze.md) · "
                "[formal-haxfreeze-ax-freeze.md]"
                "(formal-haxfreeze-ax-freeze.md) **PROMOTE** "
                "(`npm run nano:ax:freeze`) — COMPLETE+FROZEN; "
                "H-NANOGEN8 DEFER; do not invent Wave AY |\n"
            )
            if needle in text:
                text = text.replace(needle, needle + row, 1)
        path.write_text(_ensure_markers(text), encoding="utf-8")


def _patch_agents_agenda() -> None:
    if _AGENTS.is_file():
        text = _AGENTS.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"- \*\*Wave AX ACTIVE\*\* —[^\n]+",
            _AX_FROZEN_AGENTS,
            text,
            count=1,
        )
        if n:
            _AGENTS.write_text(text2, encoding="utf-8")
    if _AGENDA.is_file():
        text = _AGENDA.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\| \*\*AX\*\* \| \*\*ACTIVE\*\* \|[^\n]+",
            (
                "| **AX** | **COMPLETE + FROZEN** | AX0–AX5 as logged · "
                "AX3 [H-NANOGEN8 DEFER](results/nano-lm/formal-hnanogen8-nanogen8.md); "
                "AX4 [AX-REAL-EVAL PROMOTE](results/nano-lm/wave-ax-real-eval.md) "
                "battery 8/8; AX5 [AX-REPORT PROMOTE](results/nano-lm/wave-ax-summary.md) · "
                "[paper-lab-wave-ax.md](results/nano-lm/paper-lab-wave-ax.md); "
                "AX6 [AX-FREEZE PROMOTE](results/nano-lm/ax-freeze.md) "
                "(`npm run nano:ax:freeze`) · "
                "[formal-haxfreeze-ax-freeze.md](results/nano-lm/formal-haxfreeze-ax-freeze.md) "
                "— ship AF+AQ+AS trust + STRICT ablated DECODE; "
                "H-NANOGEN8 DEFER; ≤5M; do not invent Wave AY |"
            ),
            text,
            count=1,
        )
        if n:
            _AGENDA.write_text(text2, encoding="utf-8")
    if _EVOGEN.is_file():
        text = _EVOGEN.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"Wave AX ACTIVE \([^)]+\)",
            (
                "Wave AX COMPLETE + FROZEN (AX0–AX5 as logged · "
                "AX6 `ax-freeze.md` PROMOTE; do not invent Wave AY)"
            ),
            text,
            count=1,
        )
        if n:
            text = text2
        if "formal-haxfreeze-ax-freeze.md` PROMOTE" not in text:
            old_r = (
                "Wave AX5: `wave-ax-summary.md` · `paper-lab-wave-ax.md` PROMOTE · "
            )
            new_r = (
                "Wave AX5: `wave-ax-summary.md` · `paper-lab-wave-ax.md` PROMOTE · "
                "Wave AX6: `ax-freeze.md` · `formal-haxfreeze-ax-freeze.md` PROMOTE · "
            )
            if old_r in text:
                text = text.replace(old_r, new_r, 1)
        _EVOGEN.write_text(text, encoding="utf-8")


def _write_freeze_docs() -> None:
    _FREEZE_DOC.parent.mkdir(parents=True, exist_ok=True)
    _SUMMARY.write_text(render_wave_ax_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_ax(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_ax_freeze(), encoding="utf-8")
    _FORMAL.write_text(
        "\n".join(
            [
                "# AX-FREEZE — Wave AX lock (**DONE** — PROMOTE)",
                "",
                "> Lab: `.local/pesquisa.md` §5 AX6 · "
                "Public note: [ax-freeze.md](ax-freeze.md)  ",
                "> After: [wave-ax-summary.md](wave-ax-summary.md) / "
                "[paper-lab-wave-ax.md](paper-lab-wave-ax.md)",
                "",
                "## Hypothesis",
                "",
                "After AX-REPORT, freeze Wave AX the same way AW-FREEZE "
                "locked AW: **outcomes stay** (H-PRODNAT·H-SHIPUX·"
                "AX-REAL-EVAL·AX-REPORT PROMOTE; H-NANOGEN8 DEFER); "
                "**no Wave AY** without an explicit reopen agenda.",
                "",
                "## Gate",
                "",
                "| Check | Result |",
                "|-------|--------|",
                "| AX formals keep PRODNAT·SHIPUX·REAL-EVAL·REPORT "
                "PROMOTE · NANOGEN8 DEFER | **ok** |",
                "| `wave-ax-summary` · `paper-lab-wave-ax` · `ax-freeze` "
                "contain **COMPLETE** | **ok** |",
                "| RECIPES + champion-card contain **H-NANOGEN8** · "
                "**AX-REAL-EVAL** · **COMPLETE** | **ok** |",
                "| LOOKUP·PEAK·ABSTAIN SHIPUX smoke | **ok** |",
                "| Decision | **PROMOTE** |",
                "",
                "## Reproduce",
                "",
                "```bash",
                "npm run nano:ax:freeze",
                "```",
                "",
                "## Finding",
                "",
                f"1. Ship claim stays scoped **{SHIP_CLAIM}**.  ",
                "2. AX-FREEZE does **not** invent new serve/train hyps.  ",
                "3. Further research requires a new § in "
                "`.local/pesquisa.md` (Wave AY reopen).  ",
                "4. Anti-FP law remains: LOOKUP ≠ generative IQ; "
                "PEAK ≠ unlabeled open chat; SAFE ≠ quality; "
                "span-fallback ≠ gen IQ; true-continue unlock locked "
                "(H-NANOGEN8 DEFER · NANOGEN6·7 HOLD).  ",
                "5. ≤5M hard law remains (CAPCHECK closed).",
                "",
                "## Artifacts",
                "",
                "- Module: `nano_lm/src/ax_freeze_ops.py` · "
                "Runner: `nano_lm/src/run_ax_freeze.py`",
                "- Summary: `results/nano-lm/wave-ax/ax_freeze.json`",
                "- Contract: `nano_lm/tests/test_ax_freeze.py`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    if _SESSION_PUB.is_file():
        text = _SESSION_PUB.read_text(encoding="utf-8")
        if "Next: **AX6 AX-FREEZE**" in text:
            text = text.replace(
                "Next: **AX6 AX-FREEZE** — lock AX outcomes; "
                "no Wave AY invent without lab-book reopen.",
                "Next: **COMPLETE + FROZEN** — do not invent Wave AY "
                "without lab-book reopen (`npm run nano:ax:freeze`).",
                1,
            )
            _SESSION_PUB.write_text(text, encoding="utf-8")
    _patch_product_freeze_status()
    _patch_agents_agenda()


def _smoke_shipux_modes(*, workers: int) -> dict[str, Any]:
    from run_shipux import (
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
        "decision": "PROMOTE" if ok else "KILL (SHIPUX mode smoke)",
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
            f"# Wave AX session checklist (**{wave}** · AX6 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            f"(Wave AX **{wave}**).  ",
            "> Parent: AW COMPLETE + FROZEN · Ship: **"
            + SHIP_CLAIM
            + "** · ≤5M (H-NANOGEN8 DEFER · NANOGEN6·7 HOLD · "
            "no true-continue unlock).",
            "",
            "## Current stage",
            "",
            f"**AX6 — AX-FREEZE ({status})** · Next: "
            "**do not invent Wave AY**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| Wave | **{wave}** |",
            f"| Decision | **{decision.split(':', 1)[0]}** |",
            "| Public | `docs/results/nano-lm/ax-freeze.md` |",
            "| Formal | `docs/results/nano-lm/formal-haxfreeze-ax-freeze.md` |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AX0 | SESSION | **DONE — PROMOTE** |",
            "| AX1 | H-PRODNAT | **DONE — PROMOTE** |",
            "| AX2 | H-SHIPUX | **DONE — PROMOTE** |",
            "| AX3 | H-NANOGEN8 | **DONE — DEFER** |",
            "| AX4 | AX-REAL-EVAL | **DONE — PROMOTE** |",
            "| AX5 | AX-REPORT | **DONE — PROMOTE** |",
            f"| AX6 | AX-FREEZE | **{status}** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_local_helpers(status: str, ok: bool) -> None:
    wave = "COMPLETE + FROZEN" if ok else "OPEN"
    if _LOCAL_IMPL.is_file():
        text = _LOCAL_IMPL.read_text(encoding="utf-8")
        text = text.replace(
            "Wave **AX ACTIVE**",
            f"Wave **AX {wave}**",
        )
        old = (
            "2e. **AX5 AX-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:ax:report`) · next **AX6 AX-FREEZE**.  "
        )
        new = (
            "2e. **AX5 AX-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:ax:report`).  \n"
            f"2f. **AX6 AX-FREEZE** — **DONE {status}** "
            "(`npm run nano:ax:freeze`) · **COMPLETE + FROZEN** · "
            "do not invent Wave AY.  "
        )
        if old in text:
            text = text.replace(old, new, 1)
        _LOCAL_IMPL.write_text(text, encoding="utf-8")
    if _LOCAL_README.is_file():
        text = _LOCAL_README.read_text(encoding="utf-8")
        text = text.replace(
            "**Wave AX ACTIVE**",
            f"**Wave AX {wave}**",
        )
        old = (
            "Session: `wave-ax/SESSION.md` (AX5 AX-REPORT "
            "**DONE — PROMOTE**; next AX6 AX-FREEZE)."
        )
        new = (
            f"Session: `wave-ax/SESSION.md` (AX6 AX-FREEZE "
            f"**DONE — {status}**; **{wave}** · do not invent Wave AY)."
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
        r"\| AX6 \| \*\*AX-FREEZE\*\* \|[^\n]+\| \*\*TODO\*\* \|",
        (
            "| AX6 | **AX-FREEZE** | Lock AX outcomes | "
            f"no next letter invent without reopen | **DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    if ok:
        text = text.replace(
            "# pesquisa — post-AW reopen (**ACTIVE**)",
            "# pesquisa — Wave AX (**COMPLETE + FROZEN**)",
            1,
        )
        text = text.replace(
            "## 5. Wave AX stage machine (**ACTIVE** — reopen)",
            "## 5. Wave AX stage machine (**COMPLETE + FROZEN**)",
            1,
        )
        text2, n = re.subn(
            r"> \*\*Status:\*\* Wave AW \*\*COMPLETE \+ FROZEN\*\* "
            r"\(archive\)\. \*\*This lab book reopens\*\* the dual "
            r"mandate below — \*\*no letter-clone theater\*\*\.",
            (
                "> **Status:** Wave AX **COMPLETE + FROZEN**. "
                "Do **not** invent Wave AY without explicit reopen. "
                "Parent: Wave AW **COMPLETE + FROZEN** (archive)."
            ),
            text,
            count=1,
        )
        if n:
            text = text2
        text = text.replace(
            "> **Session:** `.local/wave-ax/SESSION.md` "
            "(AX5 AX-REPORT **DONE — PROMOTE**; next AX6 AX-FREEZE).  ",
            "> **Session:** `.local/wave-ax/SESSION.md` "
            f"(AX6 AX-FREEZE **DONE — {status}**; **COMPLETE + FROZEN**).  ",
            1,
        )
    text = text.replace(
        (
            "2e. **AX5 AX-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:ax:report`) · next **AX6 AX-FREEZE**.  "
        ),
        (
            "2e. **AX5 AX-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:ax:report`).  \n"
            f"2f. **AX6 AX-FREEZE** — **DONE {status}** "
            "(`npm run nano:ax:freeze`) · **COMPLETE + FROZEN** · "
            "do not invent Wave AY.  "
        ),
        1,
    )
    bash_old = "# next: nano:ax:freeze"
    bash_new = (
        "npm run nano:ax:freeze\n"
        "# Wave AX COMPLETE + FROZEN — do not invent Wave AY"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")
    _patch_local_helpers(status, ok)


def run_ax_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AX formals + COMPLETE closeout
    WHEN locking Wave AX
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    threads, workers = _hardware()
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in AX_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *AX_PUBLIC, *AX_PRODUCT_DOCS])
    )
    with ThreadPoolExecutor(
        max_workers=min(workers, max(4, len(read_paths)))
    ) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in AX_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in AX_PRODUCT_DOCS}
    decision = decide_ax_freeze(
        formal_texts=formal_texts,
        public_texts=public_texts,
        product_texts=product_texts,
    )
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_shipux_modes(workers=workers)
        if not bool(ask.get("ok")):
            decision = "KILL (LOOKUP·PEAK·ABSTAIN SHIPUX smoke failed)"
    ok = str(decision).startswith("PROMOTE")
    _update_local_session(decision)
    _patch_pesquisa(decision)
    payload: dict[str, Any] = {
        "id": AX_FREEZE_ID,
        "hyp_id": AX_FREEZE_ID,
        "stage": "AX6",
        "thesis": AX_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in AX_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/ax-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-haxfreeze-ax-freeze.md",
        "wave_ax_summary": "docs/results/nano-lm/wave-ax-summary.md",
        "rule": "pesquisa §5 AX-FREEZE",
        "wave_status": "COMPLETE+FROZEN" if ok else "RESEARCH_COMPLETE",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": threads,
        "workers": workers,
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AX6 AX-FREEZE")
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    threads, _workers = _hardware()
    try:
        summary = run_ax_freeze(
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
                "hyp_id": AX_FREEZE_ID,
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
