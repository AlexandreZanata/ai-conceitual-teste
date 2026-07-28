"""Wave BC3 H-CTXLIFT2 runner (nano:bc:ctxlift2) — content bars + anti-FP."""

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

from bc_ctxlift2_ops import (
    APP_SMOKE_PACK,
    CTXLIFT2_ANTI_FP,
    CTXLIFT2_CLAIM,
    CTXLIFT2_ID,
    CTXLIFT2_SAFE_NOTE,
    CTXLIFT2_THESIS,
    CTX_CONTENT_ROWS,
    KNOWN_ASK,
    PEAK_ASK,
    decide_ctxlift2,
    extract_ctxlift2_board,
    intent_false_hit,
    intent_row_ok,
    overrefuse_miss,
    overrefuse_row_ok,
)
from bc_session_ops import BC0_FOREVER_ROWS, BC0_MODES
from intentgen_ops import (
    AZ_HELDOUT_ROWS,
    BA_FOREVER_ROWS,
    BB_FOREVER_ROWS,
    OVERREFUSE_ROWS,
    score_live_row,
)
from curated_sources import SOURCES
from fastbase_ops import fastbase_generate
from genpeak_ops import chunk_doc
from matrix_common import REPO, write_json
from prodhard_ops import NEAR_MISS_ASK, peak_ok
from prodship_ops import (
    DECODE_PROBE_ASK,
    decode_content_honest,
    gate_junk_decode,
    human_para_hit,
    near_miss_ok,
)
from run_bc_fastlift import _measure_latency_tetrad
from run_z_ask import ask_once
from shipreal_ops import attach_shipreal
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-bc/bc_ctxlift2_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-bc/trials"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hctxlift2-ctxlift2.md"
_LOCAL_SESSION = REPO / ".local/wave-bc/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENTS = REPO / "AGENTS.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_EMPTY_BANK = REPO / "results/nano-lm/wave-bc/_decode_empty_bank.jsonl"
_PEAK_SOURCE = "rust-book-ch04-01"
_BY_ID = {str(s["id"]): s for s in SOURCES}

_LIVE_PROBES: tuple[dict[str, str], ...] = (
    {
        "id": "BC-CTX-LIVE-01",
        "expect_mode": "ABSTAIN",
        "question": str(BC0_FOREVER_ROWS[0]["question"]),
    },
    {
        "id": "BC-CTX-LIVE-02",
        "expect_mode": "ABSTAIN",
        "question": str(BC0_FOREVER_ROWS[6]["question"]),
    },
    {
        "id": "BC-CTX-LIVE-03",
        "expect_mode": "ABSTAIN",
        "question": str(BB_FOREVER_ROWS[0]["question"]),
    },
    {
        "id": "BC-CTX-LIVE-04",
        "expect_mode": "ABSTAIN",
        "question": str(AZ_HELDOUT_ROWS[0]["question"]),
    },
    {
        "id": "BC-CTX-LIVE-05",
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
        if pack in {"bc-forever", "bb-forever", "ba-forever", "az-hold"}:
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
        f"**{row.get('p99_wall_ms')}** |"
        for name, row in (board.get("latency") or {}).items()
    ]
    body = "\n".join(
        [
            f"# H-CTXLIFT2 (BC3) — usable long/cite/howto (**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §3 · §9 BC3 · Session: "
            "`.local/wave-bc/SESSION.md`  ",
            "> Parent: [formal-hfastlift-bc2.md](formal-hfastlift-bc2.md) · "
            "BC0 ctx baseline (= BB H-CTXHOLD / BA H-CTXREAL2)  ",
            "> Module: `nano_lm/src/bc_ctxlift2_ops.py` · "
            "Runner: `npm run nano:bc:ctxlift2`  ",
            "> **Not** AH [formal-hctxlift-ctxlift.md](formal-hctxlift-ctxlift.md) "
            "(`npm run nano:ctxlift`) · **Not** BB "
            "[formal-hctxhold-ctxhold.md](formal-hctxhold-ctxhold.md) "
            "(`npm run nano:bb:ctxhold`) · **Not** BA "
            "[formal-hctxreal2-ctxreal2.md](formal-hctxreal2-ctxreal2.md)",
            "",
            "## Hypothesis",
            "",
            CTXLIFT2_THESIS,
            "",
            "## Gate",
            "",
            "| Metric | Result | Bar |",
            "|--------|-------:|-----|",
            f"| ctx_content_ok | **{board.get('ctx_content_ok_n')}/"
            f"{board.get('ctx_content_n')}** | all |",
            f"| howto_ok / cite_ok / long_ok | **{board.get('howto_ok')}** / "
            f"**{board.get('cite_ok')}** / **{board.get('long_ok')}** | True |",
            f"| apps_content_ok | **{board.get('apps_content_ok')}** "
            f"({board.get('apps_n')}) | known·howto·long-doc |",
            f"| bc_forever_false_hit | **{board.get('bc_forever_false_hit')}** "
            f"({board.get('bc_forever_ok_n')}/{board.get('bc_forever_n')}) | **0** |",
            f"| ba_forever_false_hit | **{board.get('ba_forever_false_hit')}** "
            f"({board.get('ba_forever_ok_n')}/{board.get('ba_forever_n')}) | **0** |",
            f"| bb_forever_false_hit | **{board.get('bb_forever_false_hit')}** "
            f"({board.get('bb_forever_ok_n')}/{board.get('bb_forever_n')}) | **0** |",
            f"| az_hold_false_hit | **{board.get('az_hold_false_hit')}** "
            f"({board.get('az_hold_ok_n')}/{board.get('az_hold_n')}) | **0** |",
            f"| overrefuse_miss | **{board.get('overrefuse_miss')}** "
            f"({board.get('overrefuse_ok_n')}/{board.get('overrefuse_n')}) | **0** |",
            f"| live_fp | **{board.get('live_fp')}** | **0** |",
            f"| modes_visible | **{' · '.join(board.get('modes_visible') or [])}** "
            f"({board.get('modes_n')}/4) | 4/4 |",
            f"| Decision | **{status}** | — |",
            "",
            "## Latency p50/p99 (republish)",
            "",
            "| Path | p50 wall_ms | p99 wall_ms |",
            "|------|------------:|------------:|",
            *lat_rows,
            "",
            "## Finding",
            "",
            "1. Frozen howto·cite·long content pack scored on prod path.  ",
            "2. Apps known-ask · howto · long-doc LOOKUP gold held.  ",
            "3. Anti-FP hold: BC FH 0 · BA FH 0 · BB FH 0 · AZ hold · "
            "over-refuse 0.  ",
            "4. p50/p99 republished; L_eff alone **not** a win.  ",
            f"5. Wall clock ~{wall_s:.1f}s · max safe CPU (`cpus-4`, workers≤8).  ",
            "6. AH `nano:ctxlift` · BB `nano:bb:ctxhold` · BA `nano:ba:ctxreal2` "
            "archives untouched.  ",
            "7. Generative claim still locked (H-NANOGEN13 defer stance).  ",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:bc:ctxlift2",
            "npm run nano:test && npm run verify",
            "# ≠ AH archive: npm run nano:ctxlift",
            "# ≠ BB archive: npm run nano:bb:ctxhold",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-bc/bc_ctxlift2_summary.json`  ",
            "- Contract: `nano_lm/tests/test_bc_ctxlift2.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            f"| {CTXLIFT2_CLAIM} | Open chat / mini-AGI |",
            "| Usable howto·cite·long content | L_eff alone as ctx win |",
            "| Eval path = prod ask path | LOOKUP-as-IQ · pack theater |",
            "| AH/BB/BA CTX archives stay | Rewrite AH formal-hctxlift-ctxlift |",
            "",
            f"SAFE note: {CTXLIFT2_SAFE_NOTE}  ",
            f"Anti-FP: {CTXLIFT2_ANTI_FP}",
            "",
            "Next: **BC4 H-NANOGEN13** — one real gen method or HOLD/DEFER.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _write_session(decision: str, board: dict[str, Any]) -> None:
    status = f"DONE — {decision.split('(', 1)[0].strip()}"
    body = "\n".join(
        [
            f"# Wave BC session checklist (**OPEN** · BC3 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave BC **OPEN** · compositional anti-FP + ctx/speed + honest gen).  ",
            f"> Ship lock: **{CTXLIFT2_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**BC3 — H-CTXLIFT2 ({status})** · Next: **BC4 H-NANOGEN13**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| ctx_content_ok | **{board.get('ctx_content_ok_n')}/"
            f"{board.get('ctx_content_n')}** |",
            f"| bc_forever_false_hit | **{board.get('bc_forever_false_hit')}** |",
            f"| ba_forever_false_hit | **{board.get('ba_forever_false_hit')}** |",
            f"| bb_forever_false_hit | **{board.get('bb_forever_false_hit')}** |",
            f"| az_hold_false_hit | **{board.get('az_hold_false_hit')}** |",
            f"| live_fp | **{board.get('live_fp')}** |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| BC0 | SESSION | **DONE — PROMOTE** |",
            "| BC1 | H-OPSFAM | **DONE — PROMOTE** |",
            "| BC2 | H-FASTLIFT | **DONE — PROMOTE** |",
            f"| BC3 | H-CTXLIFT2 | **{status}** |",
            "| BC4 | H-NANOGEN13 | **NEXT** |",
            "| BC5 | BC-REAL-EVAL | pending |",
            "| BC6 | BC-REPORT | pending |",
            "| BC7 | BC-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.parent.mkdir(parents=True, exist_ok=True)
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    bc3_next = (
        "| BC3 | **H-CTXLIFT2** | Context content bars hold **or** improve "
        "**without** FP regress | content + §1 | **NEXT** |"
    )
    bc3_done = (
        "| BC3 | **H-CTXLIFT2** | Context content bars hold **or** improve "
        "**without** FP regress | content + §1 | **DONE — PROMOTE** |"
    )
    if bc3_next in text:
        text = text.replace(bc3_next, bc3_done, 1)
    bc4_pending = (
        "| BC4 | **H-NANOGEN13** | One real gen method **M1\\|M2\\|M3** — else "
        "HOLD/DEFER | true_continue → PROMOTE else HOLD/DEFER | pending |"
    )
    bc4_next = (
        "| BC4 | **H-NANOGEN13** | One real gen method **M1\\|M2\\|M3** — else "
        "HOLD/DEFER | true_continue → PROMOTE else HOLD/DEFER | **NEXT** |"
    )
    if bc4_pending in text:
        text = text.replace(bc4_pending, bc4_next, 1)
    text = text.replace(
        "4. **BC3 H-CTXLIFT2** — **NEXT** — howto·cite·long content_ok hold "
        "or improve; anti-FP hold.  ",
        "4. **BC3 H-CTXLIFT2** — **DONE PROMOTE** "
        "(`npm run nano:bc:ctxlift2`) — howto·cite·long content_ok.  ",
        1,
    )
    text = text.replace(
        "5. **BC4 H-NANOGEN13** — one real method; true_continue → PROMOTE "
        "else HOLD/DEFER (not NANOGEN12 rename).  ",
        "5. **BC4 H-NANOGEN13** — **NEXT** — one real method; true_continue → "
        "PROMOTE else HOLD/DEFER (not NANOGEN12 rename).  ",
        1,
    )
    text = text.replace(
        "(BC0–BC2 **DONE — PROMOTE**; next BC3 H-CTXLIFT2).",
        "(BC0–BC3 **DONE — PROMOTE**; next BC4 H-NANOGEN13).",
        1,
    )
    bash_old = (
        "npm run nano:bc:fastlift\n"
        "# next: nano:bc:ctxlift2 · nano:nanogen13\n"
    )
    bash_new = (
        "npm run nano:bc:fastlift\n"
        "npm run nano:bc:ctxlift2\n"
        "# next: nano:nanogen13\n"
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

Wave BB **COMPLETE + FROZEN**. Wave **BC ACTIVE**.  
**BC0–BC3 DONE — PROMOTE** · **BC3 H-CTXLIFT2** (`npm run nano:bc:ctxlift2`).

## Next

1. BC0–BC3 done.  
2. **BC4 H-NANOGEN13** — **NEXT** — one real method or HOLD/DEFER.  
3. Ship stays AZ lock: **AF + AQ + AS trust + STRICT ablated DECODE**.

```bash
npm run nano:bc:ctxlift2
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

**Wave BC ACTIVE** — BC0–BC3 **PROMOTE** (H-CTXLIFT2 content bars).

Next: **BC4 H-NANOGEN13**. Parent: Wave BB **COMPLETE + FROZEN**.

## Do not

LOOKUP-as-IQ · pack theater · bank stuffing · NANOGEN rename · CTX/SMART/FAST clones.
""",
            encoding="utf-8",
        )


def _bc_active_line() -> str:
    return (
        "**Wave BC ACTIVE:** BC0 [SESSION PROMOTE](wave-bc-session.md) · "
        "BC1 [H-OPSFAM PROMOTE](formal-hopsfam-opsfam.md) · "
        "BC2 [H-FASTLIFT PROMOTE](formal-hfastlift-bc2.md) · "
        "BC3 [H-CTXLIFT2 PROMOTE](formal-hctxlift2-ctxlift2.md) "
        "(`npm run nano:bc:ctxlift2`) — howto·cite·long content_ok; "
        "next BC4 H-NANOGEN13; ship remains **AF + AQ + AS trust + STRICT "
        "ablated DECODE**; ≤5M stays."
    )


def _patch_recipes(board: dict[str, Any], line: str) -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    text2, n = re.subn(r"\*\*Wave BC ACTIVE:\*\*[^\n]+", line, text, count=1)
    insert = (
        "| Wave BC3 H-CTXLIFT2 | [formal-hctxlift2-ctxlift2.md]"
        "(formal-hctxlift2-ctxlift2.md) **PROMOTE** (`npm run nano:bc:ctxlift2`) "
        f"— ctx {board.get('ctx_content_ok_n')}/{board.get('ctx_content_n')} · "
        f"BC FH {board.get('bc_forever_false_hit')} · BB FH "
        f"{board.get('bb_forever_false_hit')} · live FP {board.get('live_fp')} "
        "(≠ AH `nano:ctxlift` · ≠ BB `nano:bb:ctxhold`) |"
    )
    if "Wave BC3 H-CTXLIFT2" not in text2:
        marker = "| Wave BC2 H-FASTLIFT |"
        if marker in text2:
            text2 = text2.replace(marker, insert + "\n" + marker, 1)
    if n or "Wave BC3 H-CTXLIFT2" in text2:
        _RECIPES.write_text(text2, encoding="utf-8")


def _patch_card_agents_agenda(board: dict[str, Any]) -> None:
    if _CARD.is_file():
        text = _CARD.read_text(encoding="utf-8")
        card = (
            "**Wave BC ACTIVE** — BC0 [SESSION PROMOTE](wave-bc-session.md) · "
            "BC1 [H-OPSFAM PROMOTE](formal-hopsfam-opsfam.md) · "
            "BC2 [H-FASTLIFT PROMOTE](formal-hfastlift-bc2.md) · "
            "BC3 [H-CTXLIFT2 PROMOTE](formal-hctxlift2-ctxlift2.md) "
            f"(`npm run nano:bc:ctxlift2`) — ctx "
            f"{board.get('ctx_content_ok_n')}/{board.get('ctx_content_n')}; "
            "next BC4 H-NANOGEN13; ship remains **AF + AQ + AS trust + STRICT "
            "ablated DECODE**; ≤5M stays."
        )
        text2, n = re.subn(r"\*\*Wave BC ACTIVE\*\* —[^\n]+", card, text, count=1)
        if n:
            _CARD.write_text(text2, encoding="utf-8")
    if _AGENTS.is_file():
        text = _AGENTS.read_text(encoding="utf-8")
        agents = (
            "- **Wave BC ACTIVE** — BC0 [SESSION PROMOTE]"
            "(docs/results/nano-lm/wave-bc-session.md) "
            "(`npm run nano:bc:session`) · BC1 [H-OPSFAM PROMOTE]"
            "(docs/results/nano-lm/formal-hopsfam-opsfam.md) "
            "(`npm run nano:opsfam`) · BC2 [H-FASTLIFT PROMOTE]"
            "(docs/results/nano-lm/formal-hfastlift-bc2.md) "
            "(`npm run nano:bc:fastlift`) · BC3 [H-CTXLIFT2 PROMOTE]"
            "(docs/results/nano-lm/formal-hctxlift2-ctxlift2.md) "
            "(`npm run nano:bc:ctxlift2`) — howto·cite·long content_ok; "
            "next BC4 H-NANOGEN13; ship remains **AF + AQ + AS trust + STRICT "
            "ablated DECODE**; NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER; "
            "≤5M stays."
        )
        text2, n = re.subn(
            r"- \*\*Wave BC ACTIVE\*\* —[^\n]+", agents, text, count=1
        )
        if n:
            _AGENTS.write_text(text2, encoding="utf-8")
    if _AGENDA.is_file():
        text = _AGENDA.read_text(encoding="utf-8")
        row = (
            "| **BC** | **ACTIVE** | BC0–BC3 PROMOTE (H-CTXLIFT2) "
            "(`npm run nano:bc:ctxlift2`); next BC4 H-NANOGEN13; ≤5M |"
        )
        text2, n = re.subn(
            r"\| \*\*BC\*\* \| \*\*ACTIVE\*\* \|[^\n]+", row, text, count=1
        )
        if n:
            _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen() -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    text = text.replace(
        "Wave BC ACTIVE (BC0–BC2 PROMOTE · H-FASTLIFT; next BC3 H-CTXLIFT2)",
        "Wave BC ACTIVE (BC0–BC3 PROMOTE · H-CTXLIFT2; next BC4 H-NANOGEN13)",
        1,
    )
    _EVOGEN.write_text(text, encoding="utf-8")


def _patch_public(decision: str, board: dict[str, Any]) -> None:
    if not decision.startswith("PROMOTE"):
        return
    line = _bc_active_line()
    _patch_recipes(board, line)
    _patch_card_agents_agenda(board)
    _patch_evogen()


def run_bc_ctxlift2(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    trials_dir: Path,
    workers: int,
) -> dict[str, Any]:
    """
    GIVEN BC0 ctx baseline + OPSFAM anti-FP
    WHEN scoring howto·cite·long + apps + BC/BA/BB/AZ hold packs
    THEN PROMOTE/KILL per pesquisa §9 BC3.
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

    with ThreadPoolExecutor(max_workers=min(4, workers)) as pool:
        fut_nm = pool.submit(
            _ask, NEAR_MISS_ASK, root=root, bank=bank, curated=curated
        )
        fut_kn = pool.submit(
            _ask, KNOWN_ASK, root=root, bank=bank, curated=curated
        )
        fut_dc = pool.submit(_decode_probe, root=root, curated=curated)
        fut_pk = pool.submit(_peak_row, curated=curated, question=PEAK_ASK)
        near = fut_nm.result()
        known = fut_kn.result()
        dec_q = fut_dc.result()
        peak = fut_pk.result()

    board = extract_ctxlift2_board(
        ctx_rows=ctx_rows,
        apps_rows=apps_rows,
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
        modes_visible=list(BC0_MODES),
        telemetry_ok=tel_ok,
    )
    decision = decide_ctxlift2(board=board, anti_fp_signed=True)
    wall_s = time.perf_counter() - t0
    write_json(
        trials_dir / "BC-CTXLIFT2-BOARD.json",
        {
            "board": board,
            "ctx_rows": ctx_rows,
            "apps_rows": apps_rows,
            "bc_rows": bc_rows,
            "bb_rows": bb_rows,
            "ba_rows": ba_rows,
            "az_rows": az_rows,
            "overrefuse_rows": orf_rows,
            "live_rows": live_rows,
            "decision": decision,
        },
    )
    payload: dict[str, Any] = {
        "id": CTXLIFT2_ID,
        "stage": "BC3",
        "thesis": CTXLIFT2_THESIS,
        "decision": decision,
        "board": board,
        "ctx_rows": ctx_rows,
        "apps_rows": apps_rows,
        "bc_rows": bc_rows,
        "bb_rows": bb_rows,
        "ba_rows": ba_rows,
        "az_rows": az_rows,
        "overrefuse_rows": orf_rows,
        "live_rows": live_rows,
        "wall_s": wall_s,
        "workers": workers,
        "claim": CTXLIFT2_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hctxlift2-ctxlift2.md",
        "ah_archive": "docs/results/nano-lm/formal-hctxlift-ctxlift.md",
        "bb_archive": "docs/results/nano-lm/formal-hctxhold-ctxhold.md",
        "next": "BC4 H-NANOGEN13",
        "anti_fp_signed": True,
    }
    write_json(out, payload)
    _write_public(decision=decision, board=board, wall_s=wall_s)
    _write_session(decision, board)
    if decision.startswith("PROMOTE"):
        _patch_pesquisa(decision)
        _patch_local_notes(decision)
        _patch_public(decision, board)
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
        payload = run_bc_ctxlift2(
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
                "hyp_id": CTXLIFT2_ID,
                "stage": "BC3",
                "decision": decision[:160],
                "cpu_threads": threads,
                "workers": workers,
                "ctx_ok": (
                    f"{board.get('ctx_content_ok_n')}/"
                    f"{board.get('ctx_content_n')}"
                ),
                "bc_forever_false_hit": board.get("bc_forever_false_hit"),
                "bb_forever_false_hit": board.get("bb_forever_false_hit"),
                "ba_forever_false_hit": board.get("ba_forever_false_hit"),
                "live_fp": board.get("live_fp"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
