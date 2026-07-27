"""Wave AQ5 H-MODEUI runner (nano:modeui) — three modes visible on ship/demo."""

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
from modeui_ops import (
    MODEUI_ID,
    MODEUI_THESIS,
    REQUIRED_MODES,
    attach_modeui,
    decide_modeui,
    demo_card_markdown,
)
from run_z_ask import ask_once
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-aq/modeui_summary.json"
_DEMO = REPO / "docs/results/nano-lm/modeui-demo.md"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hmodeui-modeui.md"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_BY_ID = {str(s["id"]): s for s in SOURCES}
_KNOWN = (
    "Write a short Python function named add that returns "
    "the sum of two integers a and b."
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
    row = attach_modeui(dict(payload))
    row["arm"] = "LOOKUP"
    return row


def _smoke_decode(*, root: Path, bank: Path) -> dict[str, Any]:
    payload = ask_once(
        question="Explain Merkle trees briefly",
        root=root,
        seed=0,
        wrap=False,
        bank_path=bank,
        curated_root=_CURATED,
    )
    row = attach_modeui(dict(payload))
    row["arm"] = "DECODE"
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
    # Warm then one measured sample (max HW already pinned).
    for _ in range(4):
        fastbase_generate(
            question=str(item["question"]), chunks=chunks, doc=doc
        )
    payload = fastbase_generate(
        question=str(item["question"]), chunks=chunks, doc=doc
    )
    row = attach_modeui(dict(payload))
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
            f"# H-MODEUI — mode-visible ship/demo (**DONE** — {decision})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AQ5 · Session: "
            "`.local/wave-aq/SESSION.md`  ",
            "> Parent: [formal-hkbcov-kbcov.md](formal-hkbcov-kbcov.md) · "
            "Charter: [wave-aq-session.md](wave-aq-session.md)  ",
            "> Module: `nano_lm/src/modeui_ops.py` · "
            "Runner: `npm run nano:modeui`",
            "",
            "## Hypothesis",
            "",
            "Every ship/demo answer shows exactly one of "
            "`mode=LOOKUP|PEAK|DECODE` — never unlabeled.",
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
            "2. LOOKUP · PEAK · DECODE smokes each render a visible mode.  ",
            "3. Demo card published at `modeui-demo.md`.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:modeui",
            "npm run nano:z:ask -- --wrap --question \"Write a short Python "
            "function named add that returns the sum of two integers a and b.\"",
            "npm run nano:z:ask -- --question \"Explain Merkle trees briefly\"",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-aq/modeui_summary.json`  ",
            "- Demo: [modeui-demo.md](modeui-demo.md)  ",
            "- Contract: `nano_lm/tests/test_modeui.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Labeled LOOKUP/PEAK/DECODE UI | Unlabeled answers |",
            "| Mode banner on every ask | LOOKUP sold as DECODE IQ |",
            "| Three-arm smoke | Peak-as-open-chat |",
            "",
            "Next: **AQ6 H-NANOGEN** — **DONE HOLD** → "
            "[formal-hnanogen-nanogen.md](formal-hnanogen-nanogen.md).",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")
    _DEMO.write_text(demo_card_markdown(rows), encoding="utf-8")


def run_modeui(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
) -> dict[str, Any]:
    """
    GIVEN champion + bank + curated
    WHEN smoking LOOKUP · PEAK · DECODE
    THEN PROMOTE iff all three modes visible on ship/demo.
    """
    lookup = _smoke_lookup(root=root, bank=bank)
    peak = _smoke_peak(curated=curated)
    decode = _smoke_decode(root=root, bank=bank)
    rows = [lookup, peak, decode]
    decision = decide_modeui(rows=rows)
    public = "PROMOTE" if decision == "PROMOTE" else "KILL"
    _write_public(decision=public, rows=rows)
    summary: dict[str, Any] = {
        "hyp_id": MODEUI_ID,
        "stage": "AQ5",
        "thesis": MODEUI_THESIS,
        "decision": decision,
        "arms": [
            {
                "arm": r["arm"],
                "product_mode": r["product_mode"],
                "modeui_line": r["modeui_line"],
                "raw_mode": r.get("mode"),
                "wall_ms": r.get("wall_ms"),
                "n_new": r.get("n_new"),
            }
            for r in rows
        ],
        "demo": "docs/results/nano-lm/modeui-demo.md",
        "forbidden": [
            "unlabeled answer",
            "LOOKUP-as-DECODE-IQ",
            "peak-as-open-chat",
            "Wave AR invent",
        ],
        "public_note": "docs/results/nano-lm/formal-hmodeui-modeui.md",
        "next": "AQ6 H-NANOGEN",
    }
    write_json(Path(out), summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AQ5 H-MODEUI")
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    args = ap.parse_args()
    threads = _hardware()
    try:
        summary = run_modeui(
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
                "hyp_id": MODEUI_ID,
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
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
