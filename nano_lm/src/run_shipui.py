"""Wave AS6 H-SHIPUI runner — 4/4 modes on ship/demo + default ask."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from ap_session_ops import AP0_PACK
from curated_sources import SOURCES
from fastbase_ops import fastbase_generate
from genpeak_ops import chunk_doc
from matrix_common import REPO, write_json
from run_z_ask import ask_once
from shipui_ops import (
    REQUIRED_MODES,
    SHIPUI_ID,
    SHIPUI_THESIS,
    attach_shipui,
    decide_shipui,
    demo_card_markdown,
)
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-as/shipui_summary.json"
_DEMO = REPO / "docs/results/nano-lm/shipui-demo.md"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hshipui-shipui.md"
_LOCAL_SESSION = REPO / ".local/wave-as/SESSION.md"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_BY_ID = {str(s["id"]): s for s in SOURCES}
_KNOWN = (
    "Write a short Python function named add that returns "
    "the sum of two integers a and b."
)
_OOD = "Which nation hosted the 2016 Summer Olympics?"
_DECODE_Q = "Explain Merkle trees briefly"


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


def _hardware() -> int:
    cpus = int(os.cpu_count() or 4)
    return tune_cpu_threads(max(4, cpus - 2))


def _smoke_lookup(*, root: Path, bank: Path) -> dict[str, Any]:
    payload = ask_once(
        question=_KNOWN,
        root=root,
        seed=0,
        wrap=True,
        bank_path=bank,
        curated_root=_CURATED,
        abstain=True,
    )
    row = attach_shipui(dict(payload))
    row["arm"] = "LOOKUP"
    return row


def _smoke_decode(*, root: Path, bank: Path) -> dict[str, Any]:
    payload = ask_once(
        question=_DECODE_Q,
        root=root,
        seed=0,
        wrap=False,
        bank_path=bank,
        curated_root=_CURATED,
        abstain=False,
    )
    row = attach_shipui(dict(payload))
    row["arm"] = "DECODE"
    return row


def _smoke_abstain(*, root: Path, bank: Path) -> dict[str, Any]:
    # Default ask path (H-ASKABSTAIN) — no runner-only abstain patch.
    payload = ask_once(
        question=_OOD,
        root=root,
        seed=0,
        semwrap=True,
        bank_path=bank,
        curated_root=_CURATED,
        abstain=True,
    )
    row = attach_shipui(dict(payload))
    row["arm"] = "ABSTAIN"
    row["question"] = _OOD
    return row


def _smoke_peak(*, curated: Path) -> dict[str, Any]:
    item = dict(AP0_PACK[0])
    sid = str(item["source_id"])
    meta = _BY_ID.get(sid)
    if meta is None:
        raise ValueError(f"unknown source_id: {sid}")
    path = curated / str(meta["path"])
    doc = path.read_text(encoding="utf-8", errors="ignore")
    chunks = chunk_doc(doc, win=400, stride=160)
    for _ in range(4):
        fastbase_generate(
            question=str(item["question"]), chunks=chunks, doc=doc
        )
    payload = fastbase_generate(
        question=str(item["question"]), chunks=chunks, doc=doc
    )
    row = attach_shipui(dict(payload))
    row["arm"] = "PEAK"
    row["question"] = item["question"]
    return row


def _default_ask_samples(*, root: Path, bank: Path) -> list[dict[str, Any]]:
    """Raw default-ask payloads (LOOKUP + ABSTAIN) before re-attach."""
    known = ask_once(
        question=_KNOWN,
        root=root,
        seed=0,
        wrap=True,
        bank_path=bank,
        curated_root=_CURATED,
        abstain=True,
    )
    ood = ask_once(
        question=_OOD,
        root=root,
        seed=0,
        semwrap=True,
        bank_path=bank,
        curated_root=_CURATED,
        abstain=True,
    )
    return [dict(known), dict(ood)]


def _write_public(*, decision: str, rows: list[dict[str, Any]]) -> None:
    table = [
        f"| {r['arm']} | **{r['product_mode']}** | `{r['modeui_line']}` |"
        for r in rows
    ]
    body = "\n".join(
        [
            f"# H-SHIPUI — mode-visible ask + ship/demo (**DONE** — {decision})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AS6 · Session: "
            "`.local/wave-as/SESSION.md`  ",
            "> Parent: [formal-hmetrics-metrics.md](formal-hmetrics-metrics.md) · "
            "Prior: [formal-hshipdemo-shipdemo.md](formal-hshipdemo-shipdemo.md)  ",
            "> Module: `nano_lm/src/shipui_ops.py` · "
            "Runner: `npm run nano:shipui`",
            "",
            "## Hypothesis",
            "",
            "After ASKABSTAIN on the **default** ask path, every ship/demo "
            "and ask answer shows exactly one of "
            "`mode=LOOKUP|PEAK|DECODE|ABSTAIN` — never unlabeled.",
            "",
            "## Gate",
            "",
            "| Arm | product_mode | modeui_line |",
            "|-----|--------------|-------------|",
            *table,
            "",
            f"| Modes required | **{' · '.join(REQUIRED_MODES)}** | — |",
            f"| Decision | **{decision}** | 4/4 visible · no unlabeled |",
            "",
            "## Finding",
            "",
            "1. Default `nano:z:ask` already emits `product_mode` + "
            "`modeui_line` (ASKABSTAIN + MODEUI).  ",
            "2. LOOKUP · PEAK · DECODE · ABSTAIN each render a visible mode.  ",
            "3. ABSTAIN arm uses default-path refuse-junk on OOD (not "
            "runner-only).  ",
            "4. Demo card published at `shipui-demo.md`.  ",
            "5. AR H-SHIPDEMO stays locked; AS6 re-validates after ask-path "
            "changes.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:shipui",
            "npm run nano:z:ask -- --wrap --question \"Write a short Python "
            "function named add that returns the sum of two integers a and b.\"",
            f'npm run nano:z:ask -- --semwrap --question "{_OOD}"',
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-as/shipui_summary.json`  ",
            "- Demo: [shipui-demo.md](shipui-demo.md)  ",
            "- Contract: `nano_lm/tests/test_shipui.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Labeled LOOKUP/PEAK/DECODE/ABSTAIN UI | Unlabeled answers |",
            "| Mode banner on default ask | Runner-only abstain theater |",
            "| Four-arm smoke 4/4 | Peak-as-open-chat · mini-AGI claim |",
            "",
            "Next: **AS7 H-NANOGEN3** — ablated DECODE ≥ **5.0**.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")
    card = demo_card_markdown(rows).replace(
        "# SHIPDEMO — mode always visible (incl. ABSTAIN)",
        "# SHIPUI — mode always visible (ask + ship/demo)",
    )
    _DEMO.write_text(card, encoding="utf-8")


def _update_local_session(decision: str, rows: list[dict[str, Any]]) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    status = f"DONE — {decision}"
    modes = " · ".join(f"{r['arm']}={r['product_mode']}" for r in rows)
    body = "\n".join(
        [
            f"# Wave AS session checklist (**OPEN** · AS6 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AS **OPEN**).  ",
            "> Parent: AR COMPLETE + FROZEN · Ship: **AF packaged stack + "
            "AQ product layer — not open chat LM** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AS6 — H-SHIPUI ({status})** · Next: **AS7 H-NANOGEN3**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AS OPEN** |",
            f"| Modes smoke | {modes} |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AS0 | SESSION | **DONE — PROMOTE** |",
            "| AS1 | H-ASKABSTAIN | **DONE — PROMOTE** |",
            "| AS2 | H-SEMFIX | **DONE — PROMOTE** |",
            "| AS3 | H-ADVSAFE | **DONE — PROMOTE** |",
            "| AS4 | H-PARAEXT2 | **DONE — PROMOTE** |",
            "| AS5 | H-METRICS | **DONE — PROMOTE** |",
            f"| AS6 | H-SHIPUI | **{status}** |",
            "| AS7 | H-NANOGEN3 | **NEXT** |",
            "| AS8 | AS-DUAL-HITL | pending |",
            "| AS9 | AS-REPORT | pending |",
            "| AS10 | AS-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def run_shipui(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    write_docs: bool = True,
) -> dict[str, Any]:
    """
    GIVEN champion + bank after ASKABSTAIN
    WHEN smoking LOOKUP · PEAK · DECODE · ABSTAIN + default asks
    THEN PROMOTE iff 4/4 modes visible and default asks labeled.
    """
    lookup = _smoke_lookup(root=root, bank=bank)
    peak = _smoke_peak(curated=curated)
    decode = _smoke_decode(root=root, bank=bank)
    abstain = _smoke_abstain(root=root, bank=bank)
    rows = [lookup, peak, decode, abstain]
    defaults = _default_ask_samples(root=root, bank=bank)
    decision = decide_shipui(rows=rows, default_asks=defaults)
    public = "PROMOTE" if decision == "PROMOTE" else "KILL"
    if write_docs:
        _write_public(decision=public, rows=rows)
        _update_local_session(decision, rows)
    summary: dict[str, Any] = {
        "hyp_id": SHIPUI_ID,
        "stage": "AS6",
        "thesis": SHIPUI_THESIS,
        "decision": decision,
        "arms": [
            {
                "arm": r["arm"],
                "product_mode": r["product_mode"],
                "modeui_line": r["modeui_line"],
                "raw_mode": r.get("mode"),
                "wall_ms": r.get("wall_ms"),
                "n_new": r.get("n_new"),
                "completion_preview": str(r.get("completion", ""))[:80],
            }
            for r in rows
        ],
        "default_asks_labeled": [
            {
                "product_mode": d.get("product_mode"),
                "modeui_line": d.get("modeui_line"),
            }
            for d in defaults
        ],
        "demo": "docs/results/nano-lm/shipui-demo.md",
        "compose": ["MODEUI", "SHIPDEMO", "ASKABSTAIN", "default nano:z:ask"],
        "forbidden": [
            "unlabeled answer",
            "runner-only abstain theater",
            "LOOKUP-as-DECODE-IQ",
            "peak-as-open-chat",
            "Wave AT invent",
        ],
        "public_note": "docs/results/nano-lm/formal-hshipui-shipui.md",
        "next": "AS7 H-NANOGEN3",
        "anti_fp": "4/4 mode labels only; generative bar remains AS7",
    }
    write_json(Path(out), summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AS6 H-SHIPUI")
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    args = ap.parse_args()
    threads = _hardware()
    try:
        summary = run_shipui(
            root=Path(args.root),
            bank=Path(args.bank),
            curated=Path(args.curated),
            out=Path(args.out),
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    decision = str(summary["decision"])
    ok = decision == "PROMOTE"
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": SHIPUI_ID,
                "decision": decision,
                "arms": [
                    {
                        "arm": a["arm"],
                        "product_mode": a["product_mode"],
                        "modeui_line": a["modeui_line"],
                    }
                    for a in summary["arms"]
                ],
                "cpu_threads": threads,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
