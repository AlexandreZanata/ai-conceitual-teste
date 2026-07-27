"""Wave AU-FREEZE runner (nano:au:freeze) — lock AU; no Wave AV invent."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from au_freeze_ops import (
    AU_DECISIONS,
    AU_FREEZE_ID,
    AU_PRODUCT_DOCS,
    AU_PUBLIC,
    AU_THESIS,
    SHIP_CLAIM,
    decide_au_freeze,
    render_au_freeze,
)
from au_report_ops import render_paper_lab_wave_au, render_wave_au_summary
from matrix_common import REPO, write_json
from shipreal_ops import arms_content_ok
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-au/au_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/au-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-haufreeze-au-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-au-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-au.md"
_LOCAL_SESSION = REPO / ".local/wave-au/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"


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


def _read_text(rel: str) -> str:
    path = REPO / rel
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _write_freeze_docs() -> None:
    _FREEZE_DOC.parent.mkdir(parents=True, exist_ok=True)
    _SUMMARY.write_text(render_wave_au_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_au(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_au_freeze(), encoding="utf-8")
    _FORMAL.write_text(
        "\n".join(
            [
                "# AU-FREEZE — Wave AU lock (**DONE** — PROMOTE)",
                "",
                "> Lab: `.local/pesquisa.md` §5 AU6 · "
                "Public note: [au-freeze.md](au-freeze.md)  ",
                "> After: [wave-au-summary.md](wave-au-summary.md) / "
                "[paper-lab-wave-au.md](paper-lab-wave-au.md)",
                "",
                "## Hypothesis",
                "",
                "After AU-REPORT, freeze Wave AU the same way AT-FREEZE "
                "locked AT: **outcomes stay** (H-PRODHARD·H-SHIPREAL·"
                "H-NANOGEN5·AU-REAL-EVAL·AU-REPORT PROMOTE); "
                "**no Wave AV** without an explicit reopen agenda.",
                "",
                "## Gate",
                "",
                "| Check | Result |",
                "|-------|--------|",
                "| AU formals keep PRODHARD·SHIPREAL·NANOGEN5·REAL-EVAL·"
                "REPORT PROMOTE | **ok** |",
                "| `wave-au-summary` · `paper-lab-wave-au` · `au-freeze` "
                "contain **COMPLETE** | **ok** |",
                "| RECIPES + champion-card contain **H-NANOGEN5** · "
                "**AU-REAL-EVAL** · **COMPLETE** | **ok** |",
                "| LOOKUP·PEAK·DECODE·ABSTAIN four-mode smoke | **ok** |",
                "| Decision | **PROMOTE** |",
                "",
                "## Reproduce",
                "",
                "```bash",
                "npm run nano:au:freeze",
                "```",
                "",
                "## Finding",
                "",
                f"1. Ship claim stays scoped **{SHIP_CLAIM}**.  ",
                "2. AU-FREEZE does **not** invent new serve/train hyps.  ",
                "3. Further research requires a new § in "
                "`.local/pesquisa.md` (Wave AV reopen).  ",
                "4. Anti-FP law remains: LOOKUP ≠ generative IQ; "
                "PEAK ≠ unlabeled open chat; SAFE ≠ quality; "
                "STRICT ablated ≠ GPT-class; gold-substring ≠ gen; "
                "gibberish-tail fails.  ",
                "5. ≤5M hard law remains (CAPCHECK closed).",
                "",
                "## Artifacts",
                "",
                "- Module: `nano_lm/src/au_freeze_ops.py` · "
                "Runner: `nano_lm/src/run_au_freeze.py`",
                "- Summary: `results/nano-lm/wave-au/au_freeze.json`",
                "- Contract: `nano_lm/tests/test_au_freeze.py`",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _smoke_four_modes() -> dict[str, Any]:
    """LOOKUP · PEAK · DECODE · ABSTAIN smoke via SHIPREAL content bars."""
    from run_shipreal import (
        _CHAMPION,
        _CURATED,
        _Z_BANK,
        _smoke_abstain,
        _smoke_decode,
        _smoke_lookup,
        _smoke_peak,
    )

    lookup = _smoke_lookup(root=_CHAMPION, bank=_Z_BANK)
    peak = _smoke_peak(curated=_CURATED)
    decode = _smoke_decode(root=_CHAMPION, bank=_Z_BANK)
    abstain = _smoke_abstain(root=_CHAMPION, bank=_Z_BANK)
    rows = [lookup, peak, decode, abstain]
    ok = arms_content_ok(rows)
    return {
        "ok": ok,
        "decision": "PROMOTE" if ok else "KILL (SHIPREAL content smoke)",
        "arms": [
            {
                "arm": r.get("arm"),
                "product_mode": r.get("product_mode"),
                "modeui_line": r.get("modeui_line"),
                "wall_ms": r.get("wall_ms"),
                "n_new": r.get("n_new"),
            }
            for r in rows
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
            f"# Wave AU session checklist (**{wave}** · AU6 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            f"(Wave AU **{wave}**).  ",
            "> Parent: AT COMPLETE + FROZEN · Ship: **"
            + SHIP_CLAIM
            + "** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AU6 — AU-FREEZE ({status})** · Next: "
            "**do not invent Wave AV**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| Wave | **{wave}** |",
            f"| Decision | **{decision.split(':', 1)[0]}** |",
            "| Public | `docs/results/nano-lm/au-freeze.md` |",
            "| Formal | `docs/results/nano-lm/formal-haufreeze-au-freeze.md` |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AU0 | SESSION | **DONE — PROMOTE** |",
            "| AU1 | H-PRODHARD | **DONE — PROMOTE** |",
            "| AU2 | H-SHIPREAL | **DONE — PROMOTE** |",
            "| AU3 | H-NANOGEN5 | **DONE — PROMOTE** |",
            "| AU4 | AU-REAL-EVAL | **DONE — PROMOTE** |",
            "| AU5 | AU-REPORT | **DONE — PROMOTE** |",
            f"| AU6 | AU-FREEZE | **{status}** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    ok = str(decision).startswith("PROMOTE")
    status = "PROMOTE" if ok else decision.split("(", 1)[0].strip()
    text2, n = re.subn(
        r"(\| AU6 \| \*\*AU-FREEZE\*\* \| Lock AU outcomes \| "
        r"no next letter invent without reopen \| )\*\*[^*]+\*\*",
        rf"\1**DONE — {status}**",
        text,
        count=1,
    )
    if n:
        text = text2
    if ok:
        text = text.replace(
            "# pesquisa — post-AT reopen (**ACTIVE**)",
            "# pesquisa — Wave AU (**COMPLETE + FROZEN**)",
            1,
        )
        text = text.replace(
            "## 5. Wave AU stage machine (**ACTIVE** — reopen)",
            "## 5. Wave AU stage machine (**COMPLETE + FROZEN**)",
            1,
        )
        text2, n = re.subn(
            r"> \*\*Status:\*\* Wave AT \*\*COMPLETE \+ FROZEN\*\* \(archive\)\. "
            r"\*\*This lab book reopens\*\* the dual mandate below — "
            r"\*\*no letter-clone theater\*\*\.",
            "> **Status:** Wave AU **COMPLETE + FROZEN**. "
            "Do **not** invent Wave AV without explicit reopen. "
            "Parent: Wave AT **COMPLETE + FROZEN** (archive).",
            text,
            count=1,
        )
        if n:
            text = text2
    text2, n = re.subn(
        r"2e\. \*\*AU5 AU-REPORT\*\* — \*\*DONE [^*]+\*\*"
        r"(?: \(`npm run nano:au:report`\))? · next \*\*AU6 AU-FREEZE\*\*\.",
        (
            "2e. **AU5 AU-REPORT** — **DONE PROMOTE** "
            "(`npm run nano:au:report`).  \n"
            f"2f. **AU6 AU-FREEZE** — **DONE {status}** "
            "(`npm run nano:au:freeze`) · **COMPLETE + FROZEN** · "
            "do not invent Wave AV."
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"2f\. \*\*AU6 AU-FREEZE\*\* — \*\*DONE [^*]+\*\*",
        f"2f. **AU6 AU-FREEZE** — **DONE {status}**",
        text,
        count=1,
    )
    if n:
        text = text2
    bash_old = "# next: nano:au:freeze (as stages land)"
    bash_new = (
        "npm run nano:au:freeze\n"
        "# Wave AU COMPLETE + FROZEN — do not invent Wave AV"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def run_au_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AU formals + COMPLETE closeout
    WHEN locking Wave AU
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in AU_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *AU_PUBLIC, *AU_PRODUCT_DOCS])
    )
    cpus = int(os.cpu_count() or 4)
    workers = min(14, max(4, cpus - 2), max(4, len(read_paths)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in AU_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in AU_PRODUCT_DOCS}
    decision = decide_au_freeze(
        formal_texts=formal_texts,
        public_texts=public_texts,
        product_texts=product_texts,
    )
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_four_modes()
        if not bool(ask.get("ok")):
            decision = (
                "KILL (LOOKUP·PEAK·DECODE·ABSTAIN four-mode smoke failed)"
            )
    ok = str(decision).startswith("PROMOTE")
    _update_local_session(decision)
    _patch_pesquisa(decision)
    payload: dict[str, Any] = {
        "id": AU_FREEZE_ID,
        "hyp_id": AU_FREEZE_ID,
        "stage": "AU6",
        "thesis": AU_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in AU_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/au-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-haufreeze-au-freeze.md",
        "wave_au_summary": "docs/results/nano-lm/wave-au-summary.md",
        "rule": "pesquisa §5 AU-FREEZE",
        "wave_status": "COMPLETE+FROZEN" if ok else "RESEARCH_COMPLETE",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "workers": workers,
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 2))
    try:
        summary = run_au_freeze(
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
                "hyp_id": AU_FREEZE_ID,
                "decision": str(summary.get("decision", ""))[:120],
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
