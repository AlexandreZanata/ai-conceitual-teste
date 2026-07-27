"""Wave AR2 H-SHIPDEMO runner (nano:shipdemo) — four modes visible."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from abstain_ops import apply_abstain
from ap_session_ops import AP0_PACK
from curated_sources import SOURCES
from fastbase_ops import fastbase_generate
from genpeak_ops import chunk_doc
from matrix_common import REPO, write_json
from run_z_ask import ask_once
from shipdemo_ops import (
    REQUIRED_MODES,
    SHIPDEMO_ID,
    SHIPDEMO_THESIS,
    attach_shipdemo,
    decide_shipdemo,
    demo_card_markdown,
)
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-ar/shipdemo_summary.json"
_DEMO = REPO / "docs/results/nano-lm/shipdemo-demo.md"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hshipdemo-shipdemo.md"
_LOCAL_SESSION = REPO / ".local/wave-ar/SESSION.md"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_BY_ID = {str(s["id"]): s for s in SOURCES}
_KNOWN = (
    "Write a short Python function named add that returns "
    "the sum of two integers a and b."
)
_OOD = "Which nation hosted the 2016 Summer Olympics?"


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
    )
    row = attach_shipdemo(dict(payload))
    row["arm"] = "LOOKUP"
    return row


def _smoke_decode(*, root: Path, bank: Path) -> dict[str, Any]:
    # Raw DECODE path (labeled) — refuse-junk is the ABSTAIN arm.
    payload = ask_once(
        question="Explain Merkle trees briefly",
        root=root,
        seed=0,
        wrap=False,
        bank_path=bank,
        curated_root=_CURATED,
        abstain=False,
    )
    row = attach_shipdemo(dict(payload))
    row["arm"] = "DECODE"
    return row


def _smoke_abstain(*, root: Path, bank: Path) -> dict[str, Any]:
    # Default ask path already applies refuse-junk (H-ASKABSTAIN).
    payload = ask_once(
        question=_OOD,
        root=root,
        seed=0,
        wrap=False,
        bank_path=bank,
        curated_root=_CURATED,
    )
    gated = apply_abstain(dict(payload))
    row = attach_shipdemo(gated)
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
    row = attach_shipdemo(dict(payload))
    row["arm"] = "PEAK"
    row["question"] = item["question"]
    return row


def _write_public(*, decision: str, rows: list[dict[str, Any]]) -> None:
    table = [
        f"| {r['arm']} | **{r['product_mode']}** | `{r['modeui_line']}` |"
        for r in rows
    ]
    body = "\n".join(
        [
            f"# H-SHIPDEMO — four-mode ship/demo (**DONE** — {decision})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AR2 · Session: "
            "`.local/wave-ar/SESSION.md`  ",
            "> Parent: [formal-habstain-abstain.md](formal-habstain-abstain.md) · "
            "Charter: [wave-ar-session.md](wave-ar-session.md)  ",
            "> Module: `nano_lm/src/shipdemo_ops.py` · "
            "Runner: `npm run nano:shipdemo`",
            "",
            "## Hypothesis",
            "",
            "Every ship/demo answer shows exactly one of "
            "`mode=LOOKUP|PEAK|DECODE|ABSTAIN` — never unlabeled.",
            "",
            "## Gate",
            "",
            "| Arm | product_mode | modeui_line |",
            "|-----|--------------|-------------|",
            *table,
            "",
            f"| Modes required | **{' · '.join(REQUIRED_MODES)}** | — |",
            f"| Decision | **{decision}** | — |",
            "",
            "## Finding",
            "",
            "1. ASK payloads attach `product_mode` + `modeui_line`.  ",
            "2. LOOKUP · PEAK · DECODE · ABSTAIN each render a visible mode.  ",
            "3. ABSTAIN arm uses H-ABSTAIN refuse-junk on OOD DECODE.  ",
            "4. Demo card published at `shipdemo-demo.md`.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:shipdemo",
            "npm run nano:z:ask -- --wrap --question \"Write a short Python "
            "function named add that returns the sum of two integers a and b.\"",
            "npm run nano:abstain",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-ar/shipdemo_summary.json`  ",
            "- Demo: [shipdemo-demo.md](shipdemo-demo.md)  ",
            "- Contract: `nano_lm/tests/test_shipdemo.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Labeled LOOKUP/PEAK/DECODE/ABSTAIN UI | Unlabeled answers |",
            "| Mode banner on every ask | LOOKUP sold as DECODE IQ |",
            "| Four-arm smoke | Peak-as-open-chat · mini-AGI claim |",
            "",
            "Next: **AR3 H-PARAEXT** — fresh external paraphrase hit-rate.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")
    _DEMO.write_text(demo_card_markdown(rows), encoding="utf-8")


def _update_local_session(decision: str, rows: list[dict[str, Any]]) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    status = "DONE — PROMOTE" if decision == "PROMOTE" else f"DONE — {decision}"
    modes = " · ".join(f"{r['arm']}={r['product_mode']}" for r in rows)
    body = "\n".join(
        [
            f"# Wave AR session checklist (**OPEN** · AR2 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AR **OPEN**).  ",
            "> Parent: AQ COMPLETE + FROZEN · Ship: **AF packaged stack + "
            "AQ product layer — not open chat LM** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AR2 — H-SHIPDEMO ({status})** · Next: **AR3 H-PARAEXT**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AR OPEN** |",
            f"| Modes smoke | {modes} |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AR0 | SESSION | **DONE — PROMOTE** |",
            "| AR1 | H-ABSTAIN | **DONE — PROMOTE** |",
            f"| AR2 | H-SHIPDEMO | **{status}** |",
            "| AR3 | H-PARAEXT | **NEXT** |",
            "| AR4 | H-ADVREG | pending |",
            "| AR5 | H-NANOGEN2 | pending |",
            "| AR6 | AR-DUAL-HITL | pending |",
            "| AR7 | AR-REPORT | pending |",
            "| AR8 | AR-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def run_shipdemo(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
) -> dict[str, Any]:
    """
    GIVEN champion + bank + curated
    WHEN smoking LOOKUP · PEAK · DECODE · ABSTAIN
    THEN PROMOTE iff all four modes visible on ship/demo.
    """
    lookup = _smoke_lookup(root=root, bank=bank)
    peak = _smoke_peak(curated=curated)
    decode = _smoke_decode(root=root, bank=bank)
    abstain = _smoke_abstain(root=root, bank=bank)
    rows = [lookup, peak, decode, abstain]
    decision = decide_shipdemo(rows=rows)
    public = "PROMOTE" if decision == "PROMOTE" else "KILL"
    _write_public(decision=public, rows=rows)
    _update_local_session(decision, rows)
    summary: dict[str, Any] = {
        "hyp_id": SHIPDEMO_ID,
        "stage": "AR2",
        "thesis": SHIPDEMO_THESIS,
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
        "demo": "docs/results/nano-lm/shipdemo-demo.md",
        "forbidden": [
            "unlabeled answer",
            "LOOKUP-as-DECODE-IQ",
            "peak-as-open-chat",
            "Wave AS invent",
        ],
        "public_note": "docs/results/nano-lm/formal-hshipdemo-shipdemo.md",
        "next": "AR3 H-PARAEXT",
    }
    write_json(Path(out), summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AR2 H-SHIPDEMO")
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    args = ap.parse_args()
    threads = _hardware()
    try:
        summary = run_shipdemo(
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
                "hyp_id": SHIPDEMO_ID,
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
