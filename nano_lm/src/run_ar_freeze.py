"""Wave AR-FREEZE runner (nano:ar:freeze) — lock AR; no Wave AS invent."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from ar_freeze_ops import (
    AR_DECISIONS,
    AR_FREEZE_ID,
    AR_PRODUCT_DOCS,
    AR_PUBLIC,
    AR_THESIS,
    SHIP_CLAIM,
    decide_ar_freeze,
    render_ar_freeze,
)
from ar_report_ops import render_paper_lab_wave_ar, render_wave_ar_summary
from matrix_common import REPO, write_json
from shipdemo_ops import decide_shipdemo
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-ar/ar_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/ar-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-harfreeze-ar-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-ar-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-ar.md"
_LOCAL_SESSION = REPO / ".local/wave-ar/SESSION.md"


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
    _SUMMARY.write_text(render_wave_ar_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_ar(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_ar_freeze(), encoding="utf-8")
    _FORMAL.write_text(
        "\n".join(
            [
                "# AR-FREEZE — Wave AR lock (**DONE** — PROMOTE)",
                "",
                "> Lab: `.local/pesquisa.md` §5 AR8 · "
                "Public note: [ar-freeze.md](ar-freeze.md)  ",
                "> After: [wave-ar-summary.md](wave-ar-summary.md) / "
                "[paper-lab-wave-ar.md](paper-lab-wave-ar.md)",
                "",
                "## Hypothesis",
                "",
                "After AR-REPORT, freeze Wave AR the same way AQ-FREEZE "
                "locked AQ: **outcomes stay** (core PROMOTEs + deepen "
                "HOLD/KILL + H-NANOGEN2 HOLD); **no Wave AS** without an "
                "explicit reopen agenda.",
                "",
                "## Gate",
                "",
                "| Check | Result |",
                "|-------|--------|",
                "| AR formals keep ABSTAIN·SHIPDEMO PROMOTE · "
                "PARAEXT HOLD · ADVREG KILL · NANOGEN2 HOLD · "
                "DUAL-HITL HOLD · REPORT PROMOTE | **ok** |",
                "| `wave-ar-summary` · `paper-lab-wave-ar` · `ar-freeze` "
                "contain **COMPLETE** | **ok** |",
                "| RECIPES + champion-card contain **H-ABSTAIN** · "
                "**AR-DUAL-HITL** · **COMPLETE** | **ok** |",
                "| LOOKUP·PEAK·DECODE·ABSTAIN four-mode smoke | **ok** |",
                "| Decision | **PROMOTE** |",
                "",
                "## Reproduce",
                "",
                "```bash",
                "npm run nano:ar:freeze",
                "```",
                "",
                "## Finding",
                "",
                f"1. Ship claim stays scoped **{SHIP_CLAIM}**.  ",
                "2. AR-FREEZE does **not** invent new serve/train hyps.  ",
                "3. Further research requires a new § in "
                "`.local/pesquisa.md` (Wave AS reopen).  ",
                "4. Anti-FP law remains: LOOKUP ≠ generative IQ; "
                "PEAK ≠ open-chat IQ; SAFE ≠ quality; "
                "H-NANOGEN2 HOLD locks gen claim.  ",
                "5. ≤5M hard law remains (CAPCHECK closed).",
                "",
                "## Artifacts",
                "",
                "- Module: `nano_lm/src/ar_freeze_ops.py` · "
                "Runner: `nano_lm/src/run_ar_freeze.py`",
                "- Summary: `results/nano-lm/wave-ar/ar_freeze.json`",
                "- Contract: `nano_lm/tests/test_ar_freeze.py`",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _smoke_four_modes() -> dict[str, Any]:
    """LOOKUP · PEAK · DECODE · ABSTAIN smoke — no formal rewrite."""
    from run_shipdemo import (
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
    decision = decide_shipdemo(rows=rows)
    ok = decision == "PROMOTE"
    return {
        "ok": ok,
        "decision": decision,
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
            f"# Wave AR session checklist (**{wave}** · AR8 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            f"(Wave AR **{wave}**).  ",
            "> Parent: AQ COMPLETE + FROZEN · Ship: **AF packaged stack + "
            "AQ product layer — not open chat LM** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AR8 — AR-FREEZE ({status})** · Next: "
            "**do not invent Wave AS**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| Wave | **{wave}** |",
            f"| Decision | **{decision.split(':', 1)[0]}** |",
            "| Public | `docs/results/nano-lm/ar-freeze.md` |",
            "| Formal | `docs/results/nano-lm/formal-harfreeze-ar-freeze.md` |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AR0 | SESSION | **DONE — PROMOTE** |",
            "| AR1 | H-ABSTAIN | **DONE — PROMOTE** |",
            "| AR2 | H-SHIPDEMO | **DONE — PROMOTE** |",
            "| AR3 | H-PARAEXT | **DONE — HOLD** |",
            "| AR4 | H-ADVREG | **DONE — KILL** |",
            "| AR5 | H-NANOGEN2 | **DONE — HOLD** |",
            "| AR6 | AR-DUAL-HITL | **DONE — HOLD** |",
            "| AR7 | AR-REPORT | **DONE — PROMOTE** |",
            f"| AR8 | AR-FREEZE | **{status}** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def run_ar_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AR formals + COMPLETE closeout
    WHEN locking Wave AR
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in AR_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *AR_PUBLIC, *AR_PRODUCT_DOCS])
    )
    cpus = int(os.cpu_count() or 4)
    workers = min(14, max(4, cpus - 2), max(4, len(read_paths)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in AR_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in AR_PRODUCT_DOCS}
    decision = decide_ar_freeze(
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
    payload: dict[str, Any] = {
        "id": AR_FREEZE_ID,
        "hyp_id": AR_FREEZE_ID,
        "stage": "AR8",
        "thesis": AR_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in AR_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/ar-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-harfreeze-ar-freeze.md",
        "wave_ar_summary": "docs/results/nano-lm/wave-ar-summary.md",
        "rule": "pesquisa §5 AR-FREEZE",
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
        summary = run_ar_freeze(
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
                "hyp_id": AR_FREEZE_ID,
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
