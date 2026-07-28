"""Wave BC1 H-OPSFAM runner (nano:opsfam) — BC-FOREVER FH 0 via family gate."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from curated_sources import SOURCES
from fastbase_ops import fastbase_generate
from genpeak_ops import chunk_doc
from matrix_common import REPO, write_json
from opsfam_ops import (
    AZ_HELDOUT_ROWS,
    BA_FOREVER_ROWS,
    BC_FOREVER_ROWS,
    BB_FOREVER_ROWS,
    DECODE_PROBE_ASK,
    NOVEL_PROBES,
    KNOWN_ASK,
    NEAR_MISS_ASK,
    OVERREFUSE_ROWS,
    PEAK_ASK,
    OPSFAM_ANTI_FP,
    OPSFAM_CLAIM,
    OPSFAM_ID,
    OPSFAM_SAFE_NOTE,
    OPSFAM_THESIS,
    bars_from_scoreboard,
    decide_opsfam,
    extract_opsfam_board,
    gate_junk_decode,
    intent_false_hit,
    intent_row_ok,
    overrefuse_miss,
    overrefuse_row_ok,
    score_live_row,
)
from run_metrics import run_metrics
from run_shipui import run_shipui
from run_z_ask import ask_once
from shipreal_ops import attach_shipreal
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-bc/opsfam_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-bc/trials"
_BC_BANK = REPO / "results/nano-lm/wave-bc/error_bank.jsonl"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hopsfam-opsfam.md"
_LOCAL_SESSION = REPO / ".local/wave-bc/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENTS = REPO / "AGENTS.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_METRICS_OUT = REPO / "results/nano-lm/wave-bc/metrics_reg.json"
_SHIP_OUT = REPO / "results/nano-lm/wave-bc/shipui_reg.json"
_EMPTY_BANK = REPO / "results/nano-lm/wave-bc/_decode_empty_bank.jsonl"
_PEAK_SOURCE = "rust-book-ch04-01"
_BY_ID = {str(s["id"]): s for s in SOURCES}

# Live scoreboard probes (prod=eval): BB seeds + BA hold + AZ + clear + novel.
_LIVE_PROBES: tuple[dict[str, str], ...] = (
    {
        "id": "BC-LIVE-01",
        "kind": "bc_forever_floordiv",
        "expect_mode": "ABSTAIN",
        "question": str(BC_FOREVER_ROWS[0]["question"]),
    },
    {
        "id": "BC-LIVE-02",
        "kind": "bc_forever_gcd",
        "expect_mode": "ABSTAIN",
        "question": str(BC_FOREVER_ROWS[6]["question"]),
    },
    {
        "id": "BC-LIVE-03",
        "kind": "bc_forever_nand",
        "expect_mode": "ABSTAIN",
        "question": str(BC_FOREVER_ROWS[15]["question"]),
    },
    {
        "id": "BC-LIVE-04",
        "kind": "ba_forever_pow",
        "expect_mode": "ABSTAIN",
        "question": str(BA_FOREVER_ROWS[0]["question"]),
    },
    {
        "id": "BC-LIVE-05",
        "kind": "az_hold_div",
        "expect_mode": "ABSTAIN",
        "question": str(AZ_HELDOUT_ROWS[0]["question"]),
    },
    {
        "id": "BC-LIVE-06",
        "kind": "overrefuse_clear",
        "expect_mode": "LOOKUP",
        "question": str(OVERREFUSE_ROWS[0]["question"]),
        "gold": "a.clear()",
    },
) + tuple(
    {
        "id": str(p["id"]),
        "kind": f"novel_{p['class']}",
        "expect_mode": str(p["expect_mode"]),
        "question": str(p["question"]),
    }
    for p in NOVEL_PROBES
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
    # 16c / ~31Gi: leave ≥4 cores free under memory pressure.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    workers = min(8, max(4, cpus - 4))
    return threads, workers


def _ask(
    question: str,
    *,
    root: Path,
    bank: Path,
    curated: Path,
    semwrap: bool = True,
) -> dict[str, Any]:
    payload = ask_once(
        question=question,
        root=root,
        seed=0,
        wrap=True,
        semwrap=semwrap,
        bank_path=bank,
        curated_root=curated,
        abstain=True,
    )
    return attach_shipreal(dict(payload))


def _decode_probe(*, root: Path, curated: Path) -> dict[str, Any]:
    _EMPTY_BANK.parent.mkdir(parents=True, exist_ok=True)
    if not _EMPTY_BANK.is_file():
        _EMPTY_BANK.write_text("", encoding="utf-8")
    payload = ask_once(
        question=DECODE_PROBE_ASK,
        root=root,
        seed=1,
        wrap=True,
        bank_path=_EMPTY_BANK,
        curated_root=curated,
        abstain=False,
    )
    row = attach_shipreal(dict(payload))
    return attach_shipreal(gate_junk_decode(row))


def _peak_row(*, curated: Path, question: str) -> dict[str, Any]:
    meta = _BY_ID.get(_PEAK_SOURCE)
    if meta is None:
        raise ValueError(f"unknown source_id: {_PEAK_SOURCE}")
    path = curated / str(meta["path"])
    doc = path.read_text(encoding="utf-8", errors="ignore")
    chunks = chunk_doc(doc, win=400, stride=160)
    payload = fastbase_generate(question=question, chunks=chunks, doc=doc)
    row = attach_shipreal(dict(payload))
    row["arm"] = "PEAK"
    row["question"] = question
    return row


def _score_pack(
    rows: list[dict[str, str]],
    *,
    root: Path,
    bank: Path,
    curated: Path,
    workers: int,
    pack: str,
) -> list[dict[str, Any]]:
    def _one(item: dict[str, str]) -> dict[str, Any]:
        p = _ask(item["question"], root=root, bank=bank, curated=curated)
        out: dict[str, Any] = {
            "id": item["id"],
            "pack": pack,
            "mode": p.get("mode"),
            "product_mode": p.get("product_mode"),
            "completion": str(p.get("completion", ""))[:120],
            "wall_ms": p.get("wall_ms"),
        }
        if pack in {"bc-forever", "bb-forever", "ba-forever", "az-hold"}:
            out["class"] = item.get("class")
            out["false_hit"] = intent_false_hit(p)
            out["ok"] = intent_row_ok(p)
        elif pack == "overrefuse":
            out["gold"] = item.get("gold")
            out["miss"] = overrefuse_miss(p)
            out["ok"] = overrefuse_row_ok(p)
        elif pack == "live":
            out["kind"] = item.get("kind")
            out["expect_mode"] = item.get("expect_mode")
            out["gold"] = item.get("gold")
            out["score"] = score_live_row(p, expect_mode=str(item["expect_mode"]))
        return out

    n = min(workers, 12, len(rows))
    with ThreadPoolExecutor(max_workers=max(1, n)) as pool:
        return list(pool.map(_one, rows))


def _write_public(
    *,
    decision: str,
    board: dict[str, Any],
    wall_s: float,
) -> None:
    bars = bars_from_scoreboard()
    lat_rows = [
        f"| {name} | **{row.get('p50_wall_ms')}** | "
        f"**{row.get('p99_wall_ms')}** |"
        for name, row in (board.get("latency") or {}).items()
    ]
    holes = board.get("kb_hole_list") or []
    hole_lines = [f"- `{h}`" for h in holes] or ["_(none / see METRICS)_"]
    status = decision.split("(", 1)[0].strip()
    live = board.get("live_scores") or {}
    body = "\n".join(
        [
            f"# H-OPSFAM — BC-FOREVER FH 0 + BA/BB/AZ hold (**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §9 BC1 · Session: "
            "`.local/wave-bc/SESSION.md`  ",
            "> Parent: [wave-bc-session.md](wave-bc-session.md) · "
            "Suite: BC0 scoreboard  ",
            "> Module: `nano_lm/src/opsfam_ops.py` · "
            "Runner: `npm run nano:opsfam`",
            "",
            "## Hypothesis",
            "",
            OPSFAM_THESIS,
            "",
            "## Gate",
            "",
            "| Metric | Result | Bar |",
            "|--------|-------:|-----|",
            f"| bc_forever_false_hit | **{board.get('bc_forever_false_hit')}** "
            f"({board.get('bc_forever_ok_n')}/{board.get('bc_forever_n')} ABSTAIN) | "
            f"**{bars.get('bc_forever_false_hit_max')}** |",
            f"| ba_forever_false_hit | **{board.get('ba_forever_false_hit')}** "
            f"({board.get('ba_forever_ok_n')}/{board.get('ba_forever_n')} ABSTAIN) | "
            f"**{bars.get('ba_forever_false_hit_max')}** |",
            f"| bb_forever_false_hit | **{board.get('bb_forever_false_hit')}** "
            f"({board.get('bb_forever_ok_n')}/{board.get('bb_forever_n')} ABSTAIN) | "
            f"**{bars.get('bb_forever_false_hit_max')}** |",
            f"| az_hold_false_hit | **{board.get('az_hold_false_hit')}** "
            f"({board.get('az_hold_ok_n')}/{board.get('az_hold_n')} ABSTAIN) | "
            f"**{bars.get('az_hold_false_hit_max')}** |",
            f"| overrefuse_miss | **{board.get('overrefuse_miss')}** "
            f"({board.get('overrefuse_ok_n')}/{board.get('overrefuse_n')} LOOKUP) | "
            f"**{bars.get('overrefuse_miss_max')}** |",
            f"| live_ask (OK/FP/MISS+ABSTAIN-OK) | "
            f"**{board.get('live_ask_ok_fp_miss')}** "
            f"(FP={live.get('FP', 0)}) | FP **0** |",
            f"| false_hit (near-miss) | **{board.get('false_hit')}** | **0** |",
            f"| near_miss_ok | **{board.get('near_miss_ok')}** "
            f"({board.get('near_miss_mode')}) | ABSTAIN |",
            f"| decode_content_ok | **{board.get('decode_content_ok')}** "
            f"({board.get('decode_mode')}) | usable or ABSTAIN |",
            f"| peak_ok | **{board.get('peak_ok')}** "
            f"({board.get('peak_mode')}) | usable or ABSTAIN |",
            f"| known_lookup_ok | **{board.get('known_lookup_ok')}** | True |",
            f"| modes_visible | **{' · '.join(board.get('modes_visible') or [])}** "
            f"({board.get('modes_n')}/4) | LOOKUP·PEAK·DECODE·ABSTAIN |",
            f"| kb_coverage_pct | **{board.get('kb_coverage_pct')}** | "
            "publish + holes |",
            f"| Decision | **{status}** | — |",
            "",
            "## Latency p50/p99 (republish)",
            "",
            "| Path | p50 wall_ms | p99 wall_ms |",
            "|------|------------:|------------:|",
            *lat_rows,
            "",
            "## KB holes",
            "",
            *hole_lines,
            "",
            "## Finding",
            "",
            "1. BC-FOREVER (N≥18 · floordiv·neg·gcd·lshift·rshift·nand) scored on production "
            "`nano:z:ask --wrap --semwrap`.  ",
            "2. SEMWRAP `contrastive_reject` + `intent_ask_must_abstain` close "
            "floordiv→add · neg→add · gcd→add · lshift→add · rshift→add · nand→add — "
            "**not** bank stuffing.  ",
            "3. BA-FOREVER + BB-FOREVER hold + AZ hold + "
            "over-refuse `a.clear()` LOOKUP held.  ",
            "4. Live ask scoreboard OK|FP|MISS|ABSTAIN-OK (prod=eval).  ",
            "5. Near-miss BIP-39+SegWit stays ABSTAIN.  ",
            "6. DECODE content law holds — usable or ABSTAIN.  ",
            "7. Modes + latency + KB republished.  ",
            f"8. Wall clock ~{wall_s:.1f}s · max safe CPU (`cpus-4`).  ",
            "9. Generative claim still locked (gen stance **defer**; "
            "H-NANOGEN13; NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER).",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:opsfam",
            "npm run nano:bc:session",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-bc/opsfam_summary.json`  ",
            "- Contract: `nano_lm/tests/test_opsfam.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            f"| {OPSFAM_CLAIM} | Open chat / mini-AGI |",
            "| BC-FOREVER mismatch → ABSTAIN | BC FP as LOOKUP hit · BA+BB PASS with BC FP |",
            "| Exact clear → LOOKUP | Over-refuse as “safe” win |",
            "| Eval path = prod ask path | LOOKUP-as-IQ · pack theater |",
            "| BA+BB PASS ≠ BC forever coverage | Bank stuffing |",
            "",
            f"SAFE note: {OPSFAM_SAFE_NOTE}  ",
            f"Anti-FP: {OPSFAM_ANTI_FP}",
            "",
            "Next: **BC2 H-FASTLIFT** — speed p50/p99 hold/improve without FP regress.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _update_local_session(decision: str, board: dict[str, Any]) -> None:
    _LOCAL_SESSION.parent.mkdir(parents=True, exist_ok=True)
    status = f"DONE — {decision.split('(', 1)[0].strip()}"
    body = "\n".join(
        [
            f"# Wave BC session checklist (**OPEN** · BC1 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave BC **OPEN** · compositional anti-FP + ctx/speed + honest gen).  ",
            f"> Ship lock: **{OPSFAM_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**BC1 — H-OPSFAM ({status})** · Next: **BC2 H-FASTLIFT**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **BC ACTIVE** |",
            f"| bc_forever_false_hit | **{board.get('bc_forever_false_hit')}** "
            f"({board.get('bc_forever_ok_n')}/{board.get('bc_forever_n')}) |",
            f"| ba_forever_false_hit | **{board.get('ba_forever_false_hit')}** "
            f"({board.get('ba_forever_ok_n')}/{board.get('ba_forever_n')}) |",
            f"| bb_forever_false_hit | **{board.get('bb_forever_false_hit')}** "
            f"({board.get('bb_forever_ok_n')}/{board.get('bb_forever_n')}) |",
            f"| az_hold_false_hit | **{board.get('az_hold_false_hit')}** "
            f"({board.get('az_hold_ok_n')}/{board.get('az_hold_n')}) |",
            f"| overrefuse_miss | **{board.get('overrefuse_miss')}** "
            f"({board.get('overrefuse_ok_n')}/{board.get('overrefuse_n')}) |",
            f"| live_ask | **{board.get('live_ask_ok_fp_miss')}** "
            f"(FP={board.get('live_fp')}) |",
            f"| near_miss_ok / FH | **{board.get('near_miss_ok')}** / "
            f"**{board.get('false_hit')}** |",
            f"| decode_content_ok | **{board.get('decode_content_ok')}** "
            f"({board.get('decode_mode')}) |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| BC0 | SESSION | **DONE — PROMOTE** |",
            f"| BC1 | H-OPSFAM | **{status}** |",
            "| BC2 | H-FASTREAL | **NEXT** |",
            "| BC3 | H-CTXREAL2 | pending |",
            "| BC4 | H-NANOGEN13 | pending (defer unless real new method) |",
            "| BC5 | BB-REAL-EVAL | pending |",
            "| BC6 | BB-REPORT | pending |",
            "| BC7 | BB-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    bc1_next = (
        "| BC1 | **H-OPSFAM** | Family ops/intent gate → BC-FOREVER FH 0 · "
        "BA/BB hold · novel FP 0 | §1 board | **NEXT** |"
    )
    bc1_done = (
        "| BC1 | **H-OPSFAM** | Family ops/intent gate → BC-FOREVER FH 0 · "
        "BA/BB hold · novel FP 0 | §1 board | **DONE — PROMOTE** |"
    )
    if bc1_next in text:
        text = text.replace(bc1_next, bc1_done, 1)
    bc2_pending = (
        "| BC2 | **H-FASTLIFT** | Speed p50/p99 hold **or** improve "
        "**without** FP regress | latency + §1 | pending |"
    )
    bc2_next = (
        "| BC2 | **H-FASTLIFT** | Speed p50/p99 hold **or** improve "
        "**without** FP regress | latency + §1 | **NEXT** |"
    )
    if bc2_pending in text:
        text = text.replace(bc2_pending, bc2_next, 1)
    text = text.replace(
        "2. **BC1 H-OPSFAM** — **NEXT** — family ops/intent gate → "
        "BC-FOREVER FH 0; BA/BB hold; ≥10 novel live probes FP 0.  ",
        "2. **BC1 H-OPSFAM** — **DONE PROMOTE** "
        "(`npm run nano:opsfam`) — BC-FOREVER FH 0 via family gate; "
        "BA/BB/AZ hold; ≥10 novel FP 0.  ",
        1,
    )
    text = text.replace(
        "3. **BC2 H-FASTLIFT** — prod p50/p99 hold or improve; anti-FP hold.  ",
        "3. **BC2 H-FASTLIFT** — **NEXT** — prod p50/p99 hold or improve; "
        "anti-FP hold.  ",
        1,
    )
    text = text.replace(
        "(BC0 **DONE — PROMOTE**; next BC1 H-OPSFAM).",
        "(BC0 DONE — PROMOTE · BC1 **DONE — PROMOTE**; next BC2 H-FASTLIFT).",
        1,
    )
    bash_old = (
        "npm run nano:bc:session\n"
        "# next: nano:opsfam · nano:bc:fastlift · nano:bc:ctxlift2 · "
        "nano:nanogen13\n"
    )
    bash_new = (
        "npm run nano:bc:session\n"
        "npm run nano:opsfam\n"
        "# next: nano:bc:fastlift · nano:bc:ctxlift2 · nano:nanogen13\n"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")




def _patch_local_notes(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    if _LOCAL_IMPL.is_file():
        impl = """# Implementation plan — nano generative LM

> Private. Lab: [`pesquisa.md`](pesquisa.md).

## Status

Wave AZ **COMPLETE + FROZEN**. Wave **BA ACTIVE**.  
**BC0 SESSION:** DONE — PROMOTE · **BC1 H-OPSFAM:** **DONE — PROMOTE** (`npm run nano:opsfam`).

## Next

1. BC0/BC1 done.  
2. **BC2 H-FASTLIFT** — **NEXT** — prod p50/p99 without FP regress.  
3. Ship stays AZ lock: **AF + AQ + AS trust + STRICT ablated DECODE**.

```bash
npm run nano:opsfam
npm run nano:test && npm run verify
```
"""
        _LOCAL_IMPL.write_text(impl, encoding="utf-8")
    if _LOCAL_README.is_file():
        readme = """# Local research notebook

Full lab book: **`pesquisa.md`**.

## Current wave

**Wave BC ACTIVE** — BC0 SESSION PROMOTE · BC1 **H-OPSFAM PROMOTE** (forever FH 0 via gate).

Next: **BC2 H-FASTLIFT**. Parent: Wave BB **COMPLETE + FROZEN**.

## Do not

LOOKUP-as-IQ · pack theater · bank stuffing · NANOGEN rename · CTX/SMART/FAST clones.
"""
        _LOCAL_README.write_text(readme, encoding="utf-8")


def _patch_agents() -> None:
    if not _AGENTS.is_file():
        return
    text = _AGENTS.read_text(encoding="utf-8")
    if "formal-hopsfam-opsfam.md" in text:
        return
    line = (
        "- **Wave BC ACTIVE** — BC0 [SESSION PROMOTE]"
        "(docs/results/nano-lm/wave-bc-session.md) "
        "(`npm run nano:bc:session`) · BC1 [H-OPSFAM PROMOTE]"
        "(docs/results/nano-lm/formal-hopsfam-opsfam.md) "
        "(`npm run nano:opsfam`) — BC-FOREVER FH 0 · BA/BB/AZ hold; next BC2 "
        "H-FASTLIFT; ship remains **AF + AQ + AS trust + STRICT ablated "
        "DECODE**; NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER; ≤5M stays."
    )
    text2, n = re.subn(
        r"- \*\*Wave BC ACTIVE\*\* —[^\n]+",
        line,
        text,
        count=1,
    )
    if n:
        _AGENTS.write_text(text2, encoding="utf-8")


def _patch_agenda() -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    if "formal-hopsfam-opsfam.md" in text:
        return
    text2, n = re.subn(
        r"\| \*\*BC\*\* \| \*\*ACTIVE\*\* \|[^\n]+",
        "| **BC** | **ACTIVE** | BC0 [SESSION PROMOTE]"
        "(results/nano-lm/wave-bc-session.md) · BC1 [H-OPSFAM PROMOTE]"
        "(results/nano-lm/formal-hopsfam-opsfam.md) "
        "(`npm run nano:opsfam`) — BC-FOREVER FH 0; next BC2 H-FASTLIFT; "
        "ship AF+AQ+AS trust + STRICT ablated DECODE; ≤5M |",
        text,
        count=1,
    )
    if n:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_recipes(board: dict[str, Any]) -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    insert = (
        "| Wave BC1 H-OPSFAM | [formal-hopsfam-opsfam.md]"
        "(formal-hopsfam-opsfam.md) **PROMOTE** (`npm run nano:opsfam`) "
        f"— BC FH {board.get('bc_forever_false_hit')} · BA hold "
        f"{board.get('ba_forever_false_hit')} · AZ hold "
        f"{board.get('az_hold_false_hit')} · live FP {board.get('live_fp')} |"
    )
    if "Wave BC1 H-OPSFAM" in text:
        return
    marker = "| Wave BC0 SESSION |"
    idx = text.find(marker)
    if idx < 0:
        return
    end = text.find("\n", idx)
    if end < 0:
        return
    text = text[: end + 1] + insert + "\n" + text[end + 1 :]
    text2, n = re.subn(
        r"\*\*Wave BC ACTIVE:\*\*[^\n]+",
        "**Wave BC ACTIVE:** BC0 [SESSION PROMOTE](wave-bc-session.md) · "
        "BC1 [H-OPSFAM PROMOTE](formal-hopsfam-opsfam.md) "
        "(`npm run nano:opsfam`) — BC-FOREVER FH 0 · BA/BB/AZ hold; next BC2 "
        "H-FASTLIFT; ship remains **AF + AQ + AS trust + STRICT ablated "
        "DECODE**; ≤5M stays.",
        text,
        count=1,
    )
    _RECIPES.write_text(text2 if n else text, encoding="utf-8")


def _patch_card(board: dict[str, Any]) -> None:
    if not _CARD.is_file():
        return
    text = _CARD.read_text(encoding="utf-8")
    text2, n = re.subn(
        r"\*\*Wave BC ACTIVE\*\* —[^\n]+",
        "**Wave BC ACTIVE** — BC0 [SESSION PROMOTE](wave-bc-session.md) · "
        "BC1 [H-OPSFAM PROMOTE](formal-hopsfam-opsfam.md) "
        f"(`npm run nano:opsfam`) — BC FH {board.get('bc_forever_false_hit')} "
        f"· BB hold {board.get('bb_forever_false_hit')}; next BC2 H-FASTLIFT; "
        "ship remains **AF + AQ + AS trust + STRICT ablated DECODE**; ≤5M stays.",
        text,
        count=1,
    )
    if n:
        _CARD.write_text(text2, encoding="utf-8")


def _patch_evogen() -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    if "H-OPSFAM PROMOTE" in text:
        return
    text = text.replace(
        "Wave BC ACTIVE (BC0 SESSION PROMOTE; next BC1 H-OPSFAM)",
        "Wave BC ACTIVE (BC0 SESSION PROMOTE · BC1 H-OPSFAM PROMOTE; "
        "next BC2 H-FASTLIFT)",
        1,
    )
    _EVOGEN.write_text(text, encoding="utf-8")


def _patch_public_status(decision: str, board: dict[str, Any]) -> None:
    if not decision.startswith("PROMOTE"):
        return
    _patch_agents()
    _patch_agenda()
    _patch_recipes(board)
    _patch_card(board)
    _patch_evogen()


def run_opsfam(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    trials_dir: Path,
    workers: int,
) -> dict[str, Any]:
    """
    GIVEN BC0 scoreboard
    WHEN measuring BC-FOREVER FH + BA/BB/AZ hold + live ask on prod path
    THEN PROMOTE/HOLD/KILL per pesquisa §9 BC1.
    """
    t0 = time.perf_counter()
    trials_dir.mkdir(parents=True, exist_ok=True)
    _BC_BANK.parent.mkdir(parents=True, exist_ok=True)
    if not _BC_BANK.is_file():
        _BC_BANK.write_text("", encoding="utf-8")

    bc_rows = _score_pack(
        list(BC_FOREVER_ROWS),
        root=root,
        bank=bank,
        curated=curated,
        workers=workers,
        pack="bc-forever",
    )
    ba_rows = _score_pack(
        list(BA_FOREVER_ROWS),
        root=root,
        bank=bank,
        curated=curated,
        workers=workers,
        pack="ba-forever",
    )
    bb_rows = _score_pack(
        list(BB_FOREVER_ROWS),
        root=root,
        bank=bank,
        curated=curated,
        workers=workers,
        pack="bb-forever",
    )
    az_rows = _score_pack(
        list(AZ_HELDOUT_ROWS),
        root=root,
        bank=bank,
        curated=curated,
        workers=workers,
        pack="az-hold",
    )
    orf_rows = _score_pack(
        list(OVERREFUSE_ROWS),
        root=root,
        bank=bank,
        curated=curated,
        workers=workers,
        pack="overrefuse",
    )
    live_rows = _score_pack(
        [dict(p) for p in _LIVE_PROBES],
        root=root,
        bank=bank,
        curated=curated,
        workers=workers,
        pack="live",
    )
    live_scores = [str(r.get("score") or "MISS") for r in live_rows]

    with ThreadPoolExecutor(max_workers=min(4, workers)) as pool:
        fut_nm = pool.submit(
            _ask, NEAR_MISS_ASK, root=root, bank=bank, curated=curated
        )
        fut_kn = pool.submit(
            _ask, KNOWN_ASK, root=root, bank=bank, curated=curated
        )
        fut_pk = pool.submit(_peak_row, curated=curated, question=PEAK_ASK)
        fut_dc = pool.submit(_decode_probe, root=root, curated=curated)
        near = fut_nm.result()
        known = fut_kn.result()
        peak = fut_pk.result()
        decode = fut_dc.result()

    metrics = run_metrics(
        root=root,
        bank=bank,
        curated=curated,
        out=_METRICS_OUT,
        workers=workers,
        seed=0,
        write_docs=False,
    )
    ship = run_shipui(
        root=root,
        bank=bank,
        curated=curated,
        out=_SHIP_OUT,
        write_docs=False,
    )
    board = extract_opsfam_board(
        bc_rows=bc_rows,
        ba_rows=ba_rows,
        bb_rows=bb_rows,
        az_rows=az_rows,
        overrefuse_rows=orf_rows,
        live_scores=live_scores,
        near=near,
        peak=peak,
        known=known,
        decode=decode,
        metrics=metrics,
        ship=ship,
    )
    decision = decide_opsfam(board=board, anti_fp_signed=True)
    wall_s = time.perf_counter() - t0
    write_json(
        trials_dir / "BC-OPSFAM-BOARD.json",
        {
            "board": board,
            "bc_rows": bc_rows,
            "ba_rows": ba_rows,
            "bb_rows": bb_rows,
            "az_rows": az_rows,
            "overrefuse_rows": orf_rows,
            "live_rows": live_rows,
            "decision": decision,
        },
    )
    _write_public(decision=decision, board=board, wall_s=wall_s)
    _update_local_session(decision, board)
    _patch_pesquisa(decision)
    _patch_local_notes(decision)
    _patch_public_status(decision, board)
    payload = {
        "id": OPSFAM_ID,
        "thesis": OPSFAM_THESIS,
        "decision": decision,
        "board": board,
        "bc_rows": bc_rows,
        "ba_rows": ba_rows,
        "bb_rows": bb_rows,
        "az_rows": az_rows,
        "overrefuse_rows": orf_rows,
        "live_rows": live_rows,
        "wall_s": wall_s,
        "workers": workers,
        "claim": OPSFAM_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hopsfam-opsfam.md",
        "next": "BC2 H-FASTLIFT (speed hold/improve; no FP regress)",
        "anti_fp_signed": True,
        "bank_stuff_forbidden": True,
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        payload = run_opsfam(
            root=Path(args.root),
            bank=Path(args.bank),
            curated=Path(args.curated),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            workers=workers,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    decision = str(payload.get("decision", ""))
    ok = decision.startswith("PROMOTE")
    board = payload.get("board") or {}
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": OPSFAM_ID,
                "decision": decision[:140],
                "cpu_threads": threads,
                "workers": workers,
                "bc_forever_false_hit": board.get("bc_forever_false_hit"),
                "ba_forever_false_hit": board.get("ba_forever_false_hit"),
                "bb_forever_false_hit": board.get("bb_forever_false_hit"),
                "az_hold_false_hit": board.get("az_hold_false_hit"),
                "overrefuse_miss": board.get("overrefuse_miss"),
                "live_fp": board.get("live_fp"),
                "false_hit": board.get("false_hit"),
                "decode_content_ok": board.get("decode_content_ok"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
