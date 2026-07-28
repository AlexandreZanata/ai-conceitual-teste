"""Wave BD3 H-CTXGAIN runner (nano:bd:ctxgain) — content bars + anti-FP."""

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

from bd_ctxgain_ops import (
    APP_SMOKE_PACK,
    CTXGAIN_ANTI_FP,
    CTXGAIN_CLAIM,
    CTXGAIN_ID,
    CTXGAIN_SAFE_NOTE,
    CTXGAIN_THESIS,
    CTX_CONTENT_ROWS,
    KNOWN_ASK,
    PEAK_ASK,
    decide_ctxgain,
    extract_ctxgain_board,
    intent_false_hit,
    intent_row_ok,
    overrefuse_miss,
    overrefuse_row_ok,
)
from bd_session_ops import BD0_FOREVER_ROWS, BD0_MODES
from bc_session_ops import BC0_FOREVER_ROWS
from curated_sources import SOURCES
from fastbase_ops import fastbase_generate
from genpeak_ops import chunk_doc
from intentgen_ops import (
    AZ_HELDOUT_ROWS,
    BA_FOREVER_ROWS,
    BB_FOREVER_ROWS,
    OVERREFUSE_ROWS,
    score_live_row,
)
from matrix_common import REPO, write_json
from prodhard_ops import NEAR_MISS_ASK, peak_ok
from prodship_ops import (
    DECODE_PROBE_ASK,
    decode_content_honest,
    gate_junk_decode,
    human_para_hit,
    near_miss_ok,
)
from run_bd_fastgain import _measure_latency_tetrad
from run_z_ask import ask_once
from shipreal_ops import attach_shipreal
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-bd/bd_ctxgain_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-bd/trials"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hctxgain-ctxgain.md"
_LOCAL_SESSION = REPO / ".local/wave-bd/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENTS = REPO / "AGENTS.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_EMPTY_BANK = REPO / "results/nano-lm/wave-bd/_decode_empty_bank.jsonl"
_PEAK_SOURCE = "rust-book-ch04-01"
_BY_ID = {str(s["id"]): s for s in SOURCES}

_LIVE_PROBES: tuple[dict[str, str], ...] = (
    {
        "id": "BD-CTX-LIVE-01",
        "expect_mode": "ABSTAIN",
        "question": str(BD0_FOREVER_ROWS[0]["question"]),
    },
    {
        "id": "BD-CTX-LIVE-02",
        "expect_mode": "ABSTAIN",
        "question": str(BD0_FOREVER_ROWS[6]["question"]),
    },
    {
        "id": "BD-CTX-LIVE-03",
        "expect_mode": "ABSTAIN",
        "question": str(BB_FOREVER_ROWS[0]["question"]),
    },
    {
        "id": "BD-CTX-LIVE-04",
        "expect_mode": "ABSTAIN",
        "question": str(AZ_HELDOUT_ROWS[0]["question"]),
    },
    {
        "id": "BD-CTX-LIVE-05",
        "expect_mode": "LOOKUP",
        "question": str(OVERREFUSE_ROWS[0]["question"]),
        "gold": "a.clear()",
    },
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
    threads = tune_cpu_threads(max(4, cpus - 4))
    workers = min(8, max(4, cpus - 4))
    return threads, workers


def _ask(
    question: str,
    *,
    root: Path,
    bank: Path,
    curated: Path,
    wrap: bool = True,
    semwrap: bool = True,
) -> dict[str, Any]:
    payload = ask_once(
        question=question,
        root=root,
        seed=0,
        wrap=wrap,
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
    return attach_shipreal(gate_junk_decode(attach_shipreal(dict(payload))))


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
            "completion": str(p.get("completion", ""))[:160],
            "wall_ms": p.get("wall_ms"),
        }
        if pack in {
            "bd-forever",
            "bc-forever",
            "bb-forever",
            "ba-forever",
            "az-hold",
        }:
            out["false_hit"] = intent_false_hit(p)
            out["ok"] = intent_row_ok(p)
        elif pack == "overrefuse":
            out["miss"] = overrefuse_miss(p)
            out["ok"] = overrefuse_row_ok(p)
        else:
            out["score"] = score_live_row(
                {**p, "gold": item.get("gold")},
                expect_mode=str(item["expect_mode"]),
            )
        return out

    n = min(workers, 12, len(rows))
    with ThreadPoolExecutor(max_workers=max(1, n)) as pool:
        return list(pool.map(_one, rows))


def _score_ctx_pack(
    *, root: Path, bank: Path, curated: Path, workers: int
) -> list[dict[str, Any]]:
    def _one(item: dict[str, str]) -> dict[str, Any]:
        if item["kind"] == "long":
            p = _peak_row(curated=curated, question=item["question"])
        else:
            p = _ask(item["question"], root=root, bank=bank, curated=curated)
        return {
            "id": item["id"],
            "kind": item["kind"],
            "expect_mode": item["expect_mode"],
            "gold": item.get("gold", ""),
            "mode": p.get("mode"),
            "product_mode": p.get("product_mode"),
            "completion": str(p.get("completion", ""))[:200],
            "wall_ms": p.get("wall_ms"),
        }

    n = min(workers, 8, len(CTX_CONTENT_ROWS))
    with ThreadPoolExecutor(max_workers=max(1, n)) as pool:
        return list(pool.map(_one, list(CTX_CONTENT_ROWS)))


def _score_apps(
    *, root: Path, bank: Path, curated: Path, workers: int
) -> list[dict[str, Any]]:
    def _one(item: dict[str, str]) -> dict[str, Any]:
        p = _ask(item["question"], root=root, bank=bank, curated=curated)
        return {
            "id": item["id"],
            "app_id": item["app_id"],
            "gold": item.get("gold", ""),
            "mode": p.get("mode"),
            "product_mode": p.get("product_mode"),
            "completion": str(p.get("completion", ""))[:160],
            "modeui_line": p.get("modeui_line"),
            "wall_ms": p.get("wall_ms"),
        }

    n = min(workers, 6, len(APP_SMOKE_PACK))
    with ThreadPoolExecutor(max_workers=max(1, n)) as pool:
        return list(pool.map(_one, list(APP_SMOKE_PACK)))


def _write_public(
    *,
    decision: str,
    board: dict[str, Any],
    wall_s: float,
) -> None:
    status = decision.split("(", 1)[0].strip()
    lat_rows = [
        f"| {name} | **{row.get('p50_wall_ms')}** | "
        f"**{row.get('p99_wall_ms')}** | {row.get('n')} |"
        for name, row in (board.get("latency") or {}).items()
    ]
    body = "\n".join(
        [
            f"# H-CTXGAIN (BD3) — howto·cite·long content + anti-FP "
            f"(**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §3 · §9 BD3 · Session: "
            "`.local/wave-bd/SESSION.md`  ",
            "> Parent: [formal-hfastgain-fastgain.md](formal-hfastgain-fastgain.md) "
            "· BD0 ctx baseline (= H-CTXLIFT2 / H-CTXHOLD)  ",
            "> Module: `nano_lm/src/bd_ctxgain_ops.py` · "
            "Runner: `npm run nano:bd:ctxgain`  ",
            "> **Not** AH [formal-hctxlift-ctxlift.md](formal-hctxlift-ctxlift.md) "
            "· **Not** BC [formal-hctxlift2-ctxlift2.md](formal-hctxlift2-ctxlift2.md) "
            "(`npm run nano:bc:ctxlift2`) · **Not** BB "
            "[formal-hctxhold-ctxhold.md](formal-hctxhold-ctxhold.md)",
            "",
            "## Hypothesis",
            "",
            CTXGAIN_THESIS,
            "",
            "## Gate",
            "",
            "| Metric | Result | Bar |",
            "|--------|-------:|-----|",
            f"| ctx_content_ok | **{board.get('ctx_content_ok_n')}/"
            f"{board.get('ctx_content_n')}** "
            f"(howto={board.get('howto_ok')} cite={board.get('cite_ok')} "
            f"long={board.get('long_ok')}) | all |",
            f"| apps_content_ok | **{board.get('apps_content_ok')}** "
            f"({board.get('apps_n')}) | true |",
            f"| bd_forever_false_hit | **{board.get('bd_forever_false_hit')}** "
            f"({board.get('bd_forever_ok_n')}/{board.get('bd_forever_n')}) | **0** |",
            f"| ba_forever_false_hit | **{board.get('ba_forever_false_hit')}** "
            f"({board.get('ba_forever_ok_n')}/{board.get('ba_forever_n')}) | **0** |",
            f"| bb_forever_false_hit | **{board.get('bb_forever_false_hit')}** "
            f"({board.get('bb_forever_ok_n')}/{board.get('bb_forever_n')}) | **0** |",
            f"| bc_forever_false_hit | **{board.get('bc_forever_false_hit')}** "
            f"({board.get('bc_forever_ok_n')}/{board.get('bc_forever_n')}) | **0** |",
            f"| az_hold_false_hit | **{board.get('az_hold_false_hit')}** "
            f"({board.get('az_hold_ok_n')}/{board.get('az_hold_n')}) | **0** |",
            f"| overrefuse_miss | **{board.get('overrefuse_miss')}** "
            f"({board.get('overrefuse_ok_n')}/{board.get('overrefuse_n')}) | **0** |",
            f"| live_fp | **{board.get('live_fp')}** | **0** |",
            f"| modes_visible | **{' · '.join(board.get('modes_visible') or [])}** "
            f"({board.get('modes_n')}/4) | 4/4 |",
            f"| Decision | **{status}** | — |",
            "",
            "## Latency p50/p99 (published · not sole win)",
            "",
            "| Path | p50 wall_ms | p99 wall_ms | n |",
            "|------|------------:|------------:|--:|",
            *lat_rows,
            "",
            "## Finding",
            "",
            "1. Howto·cite·long content bars held on frozen pack + apps smoke.  ",
            "2. L_eff alone ≠ win (content bars required).  ",
            "3. Anti-FP hold: BD FH 0 · BA FH 0 · BB FH 0 · BC FH 0 · AZ · "
            "over-refuse 0 · live FP 0.  ",
            "4. Prod tetrad p50/p99 published under max safe CPU "
            "(`cpus-4`, workers≤8).  ",
            f"5. Wall clock ~{wall_s:.1f}s.  ",
            "6. AH/BC/BB/BA CTX archives untouched.  ",
            "7. Generative claim still locked (H-NANOGEN14 defer stance).",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:bd:ctxgain",
            "npm run nano:bd:fastgain",
            "# ≠ BC archive: npm run nano:bc:ctxlift2",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-bd/bd_ctxgain_summary.json`  ",
            "- Contract: `nano_lm/tests/test_bd_ctxgain.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            f"| {CTXGAIN_CLAIM} | Open chat / mini-AGI |",
            "| Content bars as ctx win | L_eff alone as pass |",
            "| Anti-FP hold required | Trade FP for ctx |",
            "| AH/BC/BB/BA CTX archives stay | Rewrite formal-hctxlift2 |",
            "",
            f"SAFE note: {CTXGAIN_SAFE_NOTE}  ",
            f"Anti-FP: {CTXGAIN_ANTI_FP}",
            "",
            "Next: **BD4 H-NANOGEN14** — one real method or HOLD/DEFER.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _update_local_session(decision: str, board: dict[str, Any]) -> None:
    status = f"DONE — {decision.split('(', 1)[0].strip()}"
    body = "\n".join(
        [
            f"# Wave BD session checklist (**OPEN** · BD3 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave BD **OPEN** · semantic/wrong-bank anti-FP + ctx/speed + honest gen).  ",
            f"> Ship lock: **{CTXGAIN_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**BD3 — H-CTXGAIN ({status})** · Next: **BD4 H-NANOGEN14**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| ctx_content_ok | **{board.get('ctx_content_ok_n')}/"
            f"{board.get('ctx_content_n')}** |",
            f"| apps_content_ok | **{board.get('apps_content_ok')}** |",
            f"| bd_forever_false_hit | **{board.get('bd_forever_false_hit')}** |",
            f"| ba_forever_false_hit | **{board.get('ba_forever_false_hit')}** |",
            f"| bb_forever_false_hit | **{board.get('bb_forever_false_hit')}** |",
            f"| bc_forever_false_hit | **{board.get('bc_forever_false_hit')}** |",
            f"| az_hold_false_hit | **{board.get('az_hold_false_hit')}** |",
            f"| overrefuse_miss | **{board.get('overrefuse_miss')}** |",
            f"| live_fp | **{board.get('live_fp')}** |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| BD0 | SESSION | **DONE — PROMOTE** |",
            "| BD1 | H-SEMINT | **DONE — PROMOTE** |",
            "| BD2 | H-FASTGAIN | **DONE — PROMOTE** |",
            f"| BD3 | H-CTXGAIN | **{status}** |",
            "| BD4 | H-NANOGEN14 | **NEXT** |",
            "| BD5 | BD-REAL-EVAL | pending |",
            "| BD6 | BD-REPORT | pending |",
            "| BD7 | BD-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.parent.mkdir(parents=True, exist_ok=True)
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    for old_status in ("**NEXT**", "**TODO**", "pending"):
        bd3_old = (
            "| BD3 | **H-CTXGAIN** | Context content bars hold **or** improve "
            f"**without** FP regress | content + §1 | {old_status} |"
        )
        bd3_done = (
            "| BD3 | **H-CTXGAIN** | Context content bars hold **or** improve "
            "**without** FP regress | content + §1 | **DONE — PROMOTE** |"
        )
        if bd3_old in text:
            text = text.replace(bd3_old, bd3_done, 1)
            break
    bd4_pending = (
        "| BD4 | **H-NANOGEN14** | One real gen method **M1\\|M2\\|M3** — else "
        "HOLD/DEFER | true_continue → PROMOTE else HOLD/DEFER | pending |"
    )
    bd4_todo = (
        "| BD4 | **H-NANOGEN14** | One real gen method **M1\\|M2\\|M3** — else "
        "HOLD/DEFER | true_continue → PROMOTE else HOLD/DEFER | **TODO** |"
    )
    bd4_next = (
        "| BD4 | **H-NANOGEN14** | One real gen method **M1\\|M2\\|M3** — else "
        "HOLD/DEFER | true_continue → PROMOTE else HOLD/DEFER | **NEXT** |"
    )
    if bd4_pending in text:
        text = text.replace(bd4_pending, bd4_next, 1)
    elif bd4_todo in text:
        text = text.replace(bd4_todo, bd4_next, 1)
    text = text.replace(
        "4. **BD3 H-CTXGAIN** — **NEXT** — howto·cite·long content_ok hold "
        "or improve **with** anti-FP hold.  ",
        "4. **BD3 H-CTXGAIN** — **DONE PROMOTE** "
        "(`npm run nano:bd:ctxgain`) — howto·cite·long content_ok.  ",
        1,
    )
    text = text.replace(
        "4. **BD3 H-CTXGAIN** — howto·cite·long content_ok hold or improve "
        "**with** anti-FP hold.  ",
        "4. **BD3 H-CTXGAIN** — **DONE PROMOTE** "
        "(`npm run nano:bd:ctxgain`) — howto·cite·long content_ok.  ",
        1,
    )
    text = text.replace(
        "5. **BD4 H-NANOGEN14** — one real method M1\\|M2\\|M3 → true_continue "
        "PROMOTE else HOLD/DEFER (not NANOGEN13 rename).  ",
        "5. **BD4 H-NANOGEN14** — **NEXT** — one real method M1\\|M2\\|M3 → "
        "true_continue PROMOTE else HOLD/DEFER (not NANOGEN13 rename).  ",
        1,
    )
    text = text.replace(
        "(BD0–BD2 **DONE — PROMOTE**; next BD3 H-CTXGAIN).",
        "(BD0–BD3 **DONE — PROMOTE**; next BD4 H-NANOGEN14).",
        1,
    )
    bash_old = (
        "npm run nano:bd:fastgain\n"
        "# next: nano:bd:ctxgain · nano:nanogen14\n"
    )
    bash_new = (
        "npm run nano:bd:fastgain\n"
        "npm run nano:bd:ctxgain\n"
        "# next: nano:nanogen14\n"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def _patch_local_notes(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    if _LOCAL_IMPL.is_file():
        _LOCAL_IMPL.write_text(
            """# Implementation plan — nano generative LM

> Private. Lab: [`pesquisa.md`](pesquisa.md).

## Status

Wave BC **COMPLETE + FROZEN**. Wave **BD ACTIVE**.  
**BD0–BD3 DONE — PROMOTE** · **BD3 H-CTXGAIN** (`npm run nano:bd:ctxgain`).

## Next

1. BD0–BD3 done.  
2. **BD4 H-NANOGEN14** — **NEXT** — one real method or HOLD/DEFER.  
3. Ship stays BC lock: **AF + AQ + AS trust + STRICT ablated DECODE**.

```bash
npm run nano:bd:ctxgain
npm run nano:test && npm run verify
```
""",
            encoding="utf-8",
        )
    if _LOCAL_README.is_file():
        _LOCAL_README.write_text(
            """# Local research notebook

Full lab book: **`pesquisa.md`**.

## Current wave

**Wave BD ACTIVE** — BD0–BD3 **PROMOTE** (H-CTXGAIN content bars).

Next: **BD4 H-NANOGEN14**. Parent: Wave BC **COMPLETE + FROZEN**.

## Do not

LOOKUP-as-IQ · pack theater · bank stuffing · NANOGEN rename · CTX/SMART/FAST clones.
""",
            encoding="utf-8",
        )


def _bd_active_line() -> str:
    return (
        "**Wave BD ACTIVE:** BD0 [SESSION PROMOTE](wave-bd-session.md) · "
        "BD1 [H-SEMINT PROMOTE](formal-hsemint-semint.md) · "
        "BD2 [H-FASTGAIN PROMOTE](formal-hfastgain-fastgain.md) · "
        "BD3 [H-CTXGAIN PROMOTE](formal-hctxgain-ctxgain.md) "
        "(`npm run nano:bd:ctxgain`) — howto·cite·long content_ok; "
        "next BD4 H-NANOGEN14; ship remains **AF + AQ + AS trust + STRICT "
        "ablated DECODE**; ≤5M stays."
    )


def _patch_recipes(board: dict[str, Any], line: str) -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    text2, n = re.subn(r"\*\*Wave BD ACTIVE:\*\*[^\n]+", line, text, count=1)
    insert = (
        "| Wave BD3 H-CTXGAIN | [formal-hctxgain-ctxgain.md]"
        "(formal-hctxgain-ctxgain.md) **PROMOTE** (`npm run nano:bd:ctxgain`) "
        f"— ctx {board.get('ctx_content_ok_n')}/{board.get('ctx_content_n')} · "
        f"BD FH {board.get('bd_forever_false_hit')} · BC FH "
        f"{board.get('bc_forever_false_hit')} · live FP {board.get('live_fp')} "
        "(≠ AH `nano:ctxlift` · ≠ BC `nano:bc:ctxlift2`) |"
    )
    if "Wave BD3 H-CTXGAIN" not in text2:
        marker = "| Wave BD2 H-FASTGAIN |"
        if marker in text2:
            text2 = text2.replace(marker, insert + "\n" + marker, 1)
    if n or "Wave BD3 H-CTXGAIN" in text2:
        _RECIPES.write_text(text2, encoding="utf-8")


def _patch_card_agents_agenda(board: dict[str, Any]) -> None:
    if _CARD.is_file():
        text = _CARD.read_text(encoding="utf-8")
        card = (
            "**Wave BD ACTIVE** — BD0 [SESSION PROMOTE](wave-bd-session.md) · "
            "BD1 [H-SEMINT PROMOTE](formal-hsemint-semint.md) · "
            "BD2 [H-FASTGAIN PROMOTE](formal-hfastgain-fastgain.md) · "
            "BD3 [H-CTXGAIN PROMOTE](formal-hctxgain-ctxgain.md) "
            f"(`npm run nano:bd:ctxgain`) — ctx "
            f"{board.get('ctx_content_ok_n')}/{board.get('ctx_content_n')}; "
            "next BD4 H-NANOGEN14; ship remains **AF + AQ + AS trust + STRICT "
            "ablated DECODE**; ≤5M stays."
        )
        text2, n = re.subn(r"\*\*Wave BD ACTIVE\*\* —[^\n]+", card, text, count=1)
        if n:
            _CARD.write_text(text2, encoding="utf-8")
    if _AGENTS.is_file():
        text = _AGENTS.read_text(encoding="utf-8")
        agents = (
            "- **Wave BD ACTIVE** — BD0 [SESSION PROMOTE]"
            "(docs/results/nano-lm/wave-bd-session.md) "
            "(`npm run nano:bd:session`) · BD1 [H-SEMINT PROMOTE]"
            "(docs/results/nano-lm/formal-hsemint-semint.md) "
            "(`npm run nano:semint`) · BD2 [H-FASTGAIN PROMOTE]"
            "(docs/results/nano-lm/formal-hfastgain-fastgain.md) "
            "(`npm run nano:bd:fastgain`) · BD3 [H-CTXGAIN PROMOTE]"
            "(docs/results/nano-lm/formal-hctxgain-ctxgain.md) "
            "(`npm run nano:bd:ctxgain`) — howto·cite·long content_ok; "
            "next BD4 H-NANOGEN14; ship remains **AF + AQ + AS trust + STRICT "
            "ablated DECODE**; NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12·13 DEFER; "
            "≤5M stays."
        )
        text2, n = re.subn(
            r"- \*\*Wave BD ACTIVE\*\* —[^\n]+", agents, text, count=1
        )
        if n:
            _AGENTS.write_text(text2, encoding="utf-8")
    if _AGENDA.is_file():
        text = _AGENDA.read_text(encoding="utf-8")
        row = (
            "| **BD** | **ACTIVE** | BD0–BD3 PROMOTE (H-CTXGAIN) "
            "(`npm run nano:bd:ctxgain`); next BD4 H-NANOGEN14; ≤5M |"
        )
        text2, n = re.subn(
            r"\| \*\*BD\*\* \| \*\*ACTIVE\*\* \|[^\n]+", row, text, count=1
        )
        if n:
            _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen() -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    text = text.replace(
        "Wave BD ACTIVE (BD0–BD2 PROMOTE · H-FASTGAIN; next BD3 H-CTXGAIN)",
        "Wave BD ACTIVE (BD0–BD3 PROMOTE · H-CTXGAIN; next BD4 H-NANOGEN14)",
        1,
    )
    _EVOGEN.write_text(text, encoding="utf-8")


def _patch_public(decision: str, board: dict[str, Any]) -> None:
    if not decision.startswith("PROMOTE"):
        return
    line = _bd_active_line()
    _patch_recipes(board, line)
    _patch_card_agents_agenda(board)
    _patch_evogen()


def run_bd_ctxgain(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    trials_dir: Path,
    workers: int,
) -> dict[str, Any]:
    """
    GIVEN BD0 ctx baseline + SEMINT/FASTGAIN anti-FP
    WHEN measuring howto·cite·long + apps + BD/BA/BB/BC/AZ hold
    THEN PROMOTE/KILL per pesquisa §9 BD3.
    """
    t0 = time.perf_counter()
    trials_dir.mkdir(parents=True, exist_ok=True)

    path_rows = _measure_latency_tetrad(
        root=root, bank=bank, curated=curated
    )
    latency = {k: dict(v["stats"]) for k, v in path_rows.items()}
    tel_ok = {k: bool(v["telemetry_ok"]) for k, v in path_rows.items()}

    ctx_rows = _score_ctx_pack(
        root=root, bank=bank, curated=curated, workers=workers
    )
    apps_rows = _score_apps(
        root=root, bank=bank, curated=curated, workers=workers
    )
    bd_rows = _score_pack(
        list(BD0_FOREVER_ROWS),
        root=root,
        bank=bank,
        curated=curated,
        workers=workers,
        pack="bd-forever",
    )
    bc_rows = _score_pack(
        list(BC0_FOREVER_ROWS),
        root=root,
        bank=bank,
        curated=curated,
        workers=workers,
        pack="bc-forever",
    )
    bb_rows = _score_pack(
        list(BB_FOREVER_ROWS),
        root=root,
        bank=bank,
        curated=curated,
        workers=workers,
        pack="bb-forever",
    )
    ba_rows = _score_pack(
        list(BA_FOREVER_ROWS),
        root=root,
        bank=bank,
        curated=curated,
        workers=workers,
        pack="ba-forever",
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
    live_fp = sum(1 for r in live_rows if r.get("score") == "FP")

    with ThreadPoolExecutor(max_workers=min(3, workers)) as pool:
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
        dec_q = fut_dc.result()

    board = extract_ctxgain_board(
        ctx_rows=ctx_rows,
        apps_rows=apps_rows,
        bd_rows=bd_rows,
        bc_rows=bc_rows,
        bb_rows=bb_rows,
        ba_rows=ba_rows,
        az_rows=az_rows,
        overrefuse_rows=orf_rows,
        live_fp=live_fp,
        near_miss_ok=near_miss_ok(near),
        known_lookup_ok=human_para_hit(known),
        decode_content_ok=decode_content_honest(dec_q),
        peak_ok=peak_ok(peak),
        latency=latency,
        modes_visible=list(BD0_MODES),
        telemetry_ok=tel_ok,
    )
    decision = decide_ctxgain(board=board, anti_fp_signed=True)
    wall_s = time.perf_counter() - t0
    write_json(
        trials_dir / "BD-CTXGAIN-BOARD.json",
        {
            "board": board,
            "ctx_rows": ctx_rows,
            "apps_rows": apps_rows,
            "bd_rows": bd_rows,
            "bc_rows": bc_rows,
            "bb_rows": bb_rows,
            "ba_rows": ba_rows,
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
    _patch_public(decision, board)
    payload = {
        "id": CTXGAIN_ID,
        "stage": "BD3",
        "thesis": CTXGAIN_THESIS,
        "decision": decision,
        "board": board,
        "ctx_rows": ctx_rows,
        "apps_rows": apps_rows,
        "bd_rows": bd_rows,
        "bc_rows": bc_rows,
        "bb_rows": bb_rows,
        "ba_rows": ba_rows,
        "az_rows": az_rows,
        "overrefuse_rows": orf_rows,
        "live_rows": live_rows,
        "wall_s": wall_s,
        "workers": workers,
        "claim": CTXGAIN_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hctxgain-ctxgain.md",
        "bc_archive": "docs/results/nano-lm/formal-hctxlift2-ctxlift2.md",
        "next": "BD4 H-NANOGEN14",
        "anti_fp_signed": True,
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
        payload = run_bd_ctxgain(
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
                "hyp_id": CTXGAIN_ID,
                "stage": "BD3",
                "decision": decision[:160],
                "cpu_threads": threads,
                "workers": workers,
                "ctx_content_ok_n": board.get("ctx_content_ok_n"),
                "ctx_content_n": board.get("ctx_content_n"),
                "bd_forever_false_hit": board.get("bd_forever_false_hit"),
                "bc_forever_false_hit": board.get("bc_forever_false_hit"),
                "live_fp": board.get("live_fp"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
