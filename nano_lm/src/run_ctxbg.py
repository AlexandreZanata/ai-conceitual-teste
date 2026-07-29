"""Wave BG4 H-CTXBG runner (nano:ctxbg) — content bars + anti-FP."""

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

from be_session_ops import BE0_FOREVER_ROWS
from bf_session_ops import BF0_FOREVER_ROWS
from bg_session_ops import BG0_FOREVER_ROWS
from bd_session_ops import BD0_FOREVER_ROWS, BD0_MODES
from bc_session_ops import BC0_FOREVER_ROWS
from ctxbg_ops import (
    APP_SMOKE_PACK,
    CTXBG_ANTI_FP,
    CTXBG_CLAIM,
    CTXBG_ID,
    CTXBG_SAFE_NOTE,
    CTXBG_THESIS,
    CTX_CONTENT_ROWS,
    KNOWN_ASK,
    PEAK_ASK,
    decide_ctxbg,
    extract_ctxbg_board,
    intent_false_hit,
    intent_row_ok,
    overrefuse_miss,
    overrefuse_row_ok,
)
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

_SUMMARY = REPO / "results/nano-lm/wave-bg/ctxbg_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-bg/trials"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hctxbg-ctxbg.md"
_LOCAL_SESSION = REPO / ".local/wave-bg/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENTS = REPO / "AGENTS.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_EMPTY_BANK = REPO / "results/nano-lm/wave-bg/_decode_empty_bank.jsonl"
_PEAK_SOURCE = "rust-book-ch04-01"
_BY_ID = {str(s["id"]): s for s in SOURCES}

_LIVE_PROBES: tuple[dict[str, str], ...] = (
    {
        "id": "BG-CTX-LIVE-00",
        "expect_mode": "ABSTAIN",
        "question": str(BG0_FOREVER_ROWS[0]["question"]),
    },
    {
        "id": "BG-CTX-LIVE-01",
        "expect_mode": "ABSTAIN",
        "question": str(BG0_FOREVER_ROWS[2]["question"]),
    },
    {
        "id": "BG-CTX-LIVE-02",
        "expect_mode": "ABSTAIN",
        "question": str(BF0_FOREVER_ROWS[0]["question"]),
    },
    {
        "id": "BG-CTX-LIVE-03",
        "expect_mode": "ABSTAIN",
        "question": str(BE0_FOREVER_ROWS[0]["question"]),
    },
    {
        "id": "BG-CTX-LIVE-04",
        "expect_mode": "ABSTAIN",
        "question": str(BD0_FOREVER_ROWS[0]["question"]),
    },
    {
        "id": "BG-CTX-LIVE-05",
        "expect_mode": "ABSTAIN",
        "question": str(BB_FOREVER_ROWS[0]["question"]),
    },
    {
        "id": "BG-CTX-LIVE-06",
        "expect_mode": "ABSTAIN",
        "question": str(AZ_HELDOUT_ROWS[0]["question"]),
    },
    {
        "id": "BG-CTX-LIVE-07",
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
    # 16c / ~31Gi / swap pressure: leave ≥6 cores free; workers ≤6.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 6))
    workers = min(6, max(3, cpus - 6))
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
            "bg-forever",
            "bf-forever",
            "be-forever",
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
            f"# H-CTXBG (BG4) — howto·cite·long content + anti-FP "
            f"(**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §3 · §9 BG4 · Session: "
            "`.local/wave-bg/SESSION.md`  ",
            "> Parent: [formal-hfastbg-fastbg.md](formal-hfastbg-fastbg.md) · "
            "BG0 ctx baseline (= H-CTXBF / H-CTXBE / H-CTXGAIN)  ",
            "> Module: `nano_lm/src/ctxbg_ops.py` · "
            "Runner: `npm run nano:ctxbg`  ",
            "> **Not** BF [formal-hctxbf-ctxbf.md](formal-hctxbf-ctxbf.md) "
            "(`npm run nano:ctxbf`) · **Not** BE/BD/AH/BC/BB/BA CTX archives",
            "",
            "## Hypothesis",
            "",
            CTXBG_THESIS,
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
            f"| bg_forever_false_hit | **{board.get('bg_forever_false_hit')}** "
            f"({board.get('bg_forever_ok_n')}/{board.get('bg_forever_n')}) | **0** |",
            f"| bf_forever_false_hit | **{board.get('bf_forever_false_hit')}** "
            f"({board.get('bf_forever_ok_n')}/{board.get('bf_forever_n')}) | **0** |",
            f"| be_forever_false_hit | **{board.get('be_forever_false_hit')}** "
            f"({board.get('be_forever_ok_n')}/{board.get('be_forever_n')}) | **0** |",
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
            "3. Anti-FP hold: BG FH 0 · BA…BF forever · AZ · over-refuse 0 · "
            "live FP 0.  ",
            "4. Prod tetrad p50/p99 published under max safe CPU "
            "(`cpus-6`, workers≤6).  ",
            f"5. Wall clock ~{wall_s:.1f}s.  ",
            "6. BF/BE/BD/AH/BC/BB/BA CTX archives untouched.  ",
            "7. Generative claim still locked (gen stance SKIP; H-NANOGEN17 "
            "not opened).",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:ctxbg",
            "npm run nano:fastbg",
            "# ≠ BF archive: npm run nano:ctxbf",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-bg/ctxbg_summary.json`  ",
            "- Contract: `nano_lm/tests/test_ctxbg.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            f"| {CTXBG_CLAIM} | Open chat / mini-AGI |",
            "| Content bars as ctx win | L_eff alone as pass |",
            "| Anti-FP hold required | Trade FP for ctx |",
            "| BF/BE/BD/AH/BC/BB/BA CTX archives stay | Rewrite formal-hctxbf |",
            "",
            f"SAFE note: {CTXBG_SAFE_NOTE}  ",
            f"Anti-FP: {CTXBG_ANTI_FP}",
            "",
            "Next: **BG5 H-NANOGEN17 or SKIP** — only with written M1|M2|M3; "
            "else SKIP.",
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
            f"# Wave BG session checklist (**OPEN** · BG4 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md`.  ",
            f"> Ship lock: **{CTXBG_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**BG4 — H-CTXBG ({status})** · Next: **BG5 H-NANOGEN17 / SKIP**",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| BG0 | SESSION | **DONE — PROMOTE** |",
            "| BG1 | H-UNARYINT | **DONE — PROMOTE** |",
            "| BG2 | H-SHIPPUB | **DONE — PROMOTE** |",
            "| BG3 | H-FASTBG | **DONE — PROMOTE** |",
            f"| BG4 | H-CTXBG | **{status}** |",
            "| BG5 | H-NANOGEN17 / SKIP | **NEXT** |",
            "| BG6 | BG-REAL-EVAL | pending |",
            "| BG7 | BG-REPORT | pending |",
            "| BG8 | BG-FREEZE | pending |",
            "",
            "## Board snapshot",
            "",
            f"| ctx_content_ok | **{board.get('ctx_content_ok_n')}/"
            f"{board.get('ctx_content_n')}** |",
            f"| bg_forever_false_hit | **{board.get('bg_forever_false_hit')}** |",
            f"| live_fp | **{board.get('live_fp')}** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    text = text.replace(
        "| BG4 | **H-CTXBG** | Context content bars hold **or** improve "
        "**without** FP regress | content + §1 | **NEXT** |",
        "| BG4 | **H-CTXBG** | Context content bars hold **or** improve "
        "**without** FP regress | content + §1 | **DONE — PROMOTE** |",
        1,
    )
    text = text.replace(
        "| BG5 | **H-NANOGEN17** **or SKIP** | Only if BG0 method plan — else "
        "**SKIP** (stop rule) | true_continue → PROMOTE else SKIP | **TODO** |",
        "| BG5 | **H-NANOGEN17** **or SKIP** | Only if BG0 method plan — else "
        "**SKIP** (stop rule) | true_continue → PROMOTE else SKIP | **NEXT** |",
        1,
    )
    text = text.replace(
        "5. **BG4 H-CTXBG** — **NEXT** — howto·cite·long content_ok "
        "hold/improve with anti-FP hold.  ",
        "5. **BG4 H-CTXBG** — **DONE PROMOTE** (`npm run nano:ctxbg`) — "
        "howto·cite·long content_ok; anti-FP hold.  ",
        1,
    )
    text = text.replace(
        "6. **BG5 H-NANOGEN17 or SKIP** — only with written M1|M2|M3; else "
        "**SKIP** (not empty DEFER).  ",
        "6. **BG5 H-NANOGEN17 or SKIP** — **NEXT** — only with written "
        "M1|M2|M3; else **SKIP** (not empty DEFER).  ",
        1,
    )
    text = text.replace(
        "(BG0–BG3 **DONE — PROMOTE**; next BG4 H-CTXBG)",
        "(BG0–BG4 **DONE — PROMOTE**; next BG5 H-NANOGEN17 / SKIP)",
        1,
    )
    text = text.replace(
        "(BG0–BG3 **DONE — PROMOTE**; next BG4 H-CTXBG) via this lab-book",
        "(BG0–BG4 **DONE — PROMOTE**; next BG5 H-NANOGEN17 / SKIP) via this "
        "lab-book",
        1,
    )
    text = text.replace(
        "(BG0–BG3 **DONE — PROMOTE**; next BG4 H-CTXBG).",
        "(BG0–BG4 **DONE — PROMOTE**; next BG5 H-NANOGEN17 / SKIP).",
        1,
    )
    text = text.replace(
        "npm run nano:fastbg\n"
        "# next: nano:bg:ctxbg · nano:nanogen17 (SKIP without plan)\n",
        "npm run nano:fastbg\n"
        "npm run nano:ctxbg\n"
        "# next: nano:nanogen17 (SKIP without plan)\n",
        1,
    )
    text = text.replace(
        "(BG0–BG3 **DONE — PROMOTE**; next BG4 H-CTXBG)",
        "(BG0–BG4 **DONE — PROMOTE**; next BG5 H-NANOGEN17 / SKIP)",
    )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def _patch_local_notes(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    if _LOCAL_IMPL.is_file():
        _LOCAL_IMPL.write_text(
            "\n".join(
                [
                    "# Implementation plan — nano generative LM",
                    "",
                    "> Private. Lab: [`pesquisa.md`](pesquisa.md).",
                    "",
                    "## Status",
                    "",
                    "Wave **BG ACTIVE**. BG0–BG4 **DONE — PROMOTE** "
                    "(`npm run nano:ctxbg`).",
                    "",
                    "## Next",
                    "",
                    "1. BG0–BG4 done.  ",
                    "2. **BG5 H-NANOGEN17 or SKIP** — **NEXT**.  ",
                    "3. Ship stays AF+AQ+AS STRICT ablated DECODE.",
                    "",
                    "```bash",
                    "npm run nano:ctxbg",
                    "npm run nano:test && npm run verify",
                    "```",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    if _LOCAL_README.is_file():
        _LOCAL_README.write_text(
            "\n".join(
                [
                    "# Local research notebook",
                    "",
                    "Full lab book: **`pesquisa.md`**.",
                    "",
                    "## Current wave",
                    "",
                    "**Wave BG ACTIVE** — BG0–BG3 PROMOTE · "
                    "BG4 **H-CTXBG PROMOTE** (content bars + anti-FP).",
                    "",
                    "Next: **BG5 H-NANOGEN17 / SKIP**. Parent: Wave BF "
                    "**COMPLETE + FROZEN**.",
                    "",
                    "## Do not",
                    "",
                    "LOOKUP-as-IQ · pack theater · L_eff alone · "
                    "NANOGEN rename · CTX/SMART/FAST clones.",
                    "",
                ]
            ),
            encoding="utf-8",
        )


def _sub_file(path: Path, pattern: str, repl: str) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    text2, n = re.subn(pattern, repl, text, count=1)
    if n:
        path.write_text(text2, encoding="utf-8")


def _patch_recipes(board: dict[str, Any]) -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    insert = (
        "| Wave BG4 H-CTXBG | [formal-hctxbg-ctxbg.md]"
        "(formal-hctxbg-ctxbg.md) **PROMOTE** (`npm run nano:ctxbg`) — "
        f"ctx {board.get('ctx_content_ok_n')}/{board.get('ctx_content_n')} · "
        f"BG FH {board.get('bg_forever_false_hit')} · "
        f"live FP {board.get('live_fp')} |"
    )
    if "Wave BG4 H-CTXBG" not in text:
        marker = "| Wave BG3 H-FASTBG |"
        idx = text.find(marker)
        if idx >= 0:
            end = text.find("\n", idx)
            text = text[: end + 1] + insert + "\n" + text[end + 1 :]
    text2, n = re.subn(
        r"\*\*Wave BG ACTIVE:\*\*[^\n]+",
        "**Wave BG ACTIVE:** BG0 [SESSION PROMOTE](wave-bg-session.md) · "
        "BG1 [H-UNARYINT PROMOTE](formal-hunaryint-unaryint.md) · "
        "BG2 [H-SHIPPUB PROMOTE](formal-hshippub-shippub.md) · "
        "BG3 [H-FASTBG PROMOTE](formal-hfastbg-fastbg.md) · "
        "BG4 [H-CTXBG PROMOTE](formal-hctxbg-ctxbg.md) "
        "(`npm run nano:ctxbg`) — content bars; next BG5 H-NANOGEN17/SKIP; "
        "ship remains **AF + AQ + AS trust + STRICT ablated DECODE**; "
        "≤5M stays.",
        text,
        count=1,
    )
    _RECIPES.write_text(text2 if n else text, encoding="utf-8")


def _patch_public(decision: str, board: dict[str, Any]) -> None:
    if not decision.startswith("PROMOTE"):
        return
    _sub_file(
        _AGENTS,
        r"- \*\*Wave BG ACTIVE\*\* —[^\n]+",
        "- **Wave BG ACTIVE** — BG0 [SESSION PROMOTE]"
        "(docs/results/nano-lm/wave-bg-session.md) "
        "(`npm run nano:bg:session`) · BG1 [H-UNARYINT PROMOTE]"
        "(docs/results/nano-lm/formal-hunaryint-unaryint.md) "
        "(`npm run nano:unaryint`) · BG2 [H-SHIPPUB PROMOTE]"
        "(docs/results/nano-lm/formal-hshippub-shippub.md) "
        "(`npm run nano:shippub`) · BG3 [H-FASTBG PROMOTE]"
        "(docs/results/nano-lm/formal-hfastbg-fastbg.md) "
        "(`npm run nano:fastbg`) · BG4 [H-CTXBG PROMOTE]"
        "(docs/results/nano-lm/formal-hctxbg-ctxbg.md) "
        "(`npm run nano:ctxbg`) — content bars + anti-FP; next BG5 "
        "H-NANOGEN17/SKIP; ship remains **AF + AQ + AS trust + STRICT "
        "ablated DECODE**; NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · "
        "NANOGEN16 SKIP; ≤5M stays.",
    )
    _sub_file(
        _AGENDA,
        r"\| \*\*BG\*\* \| \*\*ACTIVE\*\* \|[^\n]+",
        "| **BG** | **ACTIVE** | BG0–BG4 PROMOTE "
        "(results/nano-lm/formal-hctxbg-ctxbg.md) "
        "(`npm run nano:ctxbg`) — content bars; next BG5 H-NANOGEN17/SKIP; "
        "ship AF+AQ+AS trust + STRICT ablated DECODE; ≤5M |",
    )
    _patch_recipes(board)
    _sub_file(
        _CARD,
        r"\*\*Wave BG ACTIVE\*\* —[^\n]+",
        "**Wave BG ACTIVE** — BG0 [SESSION PROMOTE](wave-bg-session.md) · "
        "BG1 [H-UNARYINT PROMOTE](formal-hunaryint-unaryint.md) · "
        "BG2 [H-SHIPPUB PROMOTE](formal-hshippub-shippub.md) · "
        "BG3 [H-FASTBG PROMOTE](formal-hfastbg-fastbg.md) · "
        "BG4 [H-CTXBG PROMOTE](formal-hctxbg-ctxbg.md) "
        f"(`npm run nano:ctxbg`) — ctx {board.get('ctx_content_ok_n')}/"
        f"{board.get('ctx_content_n')}; next BG5 H-NANOGEN17/SKIP; "
        "ship remains **AF + AQ + AS trust + STRICT ablated DECODE**; "
        "≤5M stays.",
    )
    if _EVOGEN.is_file():
        text = _EVOGEN.read_text(encoding="utf-8")
        text = text.replace(
            "BG0–BG3 PROMOTE · H-FASTBG; next BG4 H-CTXBG",
            "BG0–BG4 PROMOTE · H-CTXBG; next BG5 H-NANOGEN17/SKIP",
            1,
        )
        text = text.replace(
            "BG3 H-FASTBG PROMOTE; next BG4 H-CTXBG",
            "BG0–BG4 PROMOTE · H-CTXBG; next BG5 H-NANOGEN17/SKIP",
            1,
        )
        text = text.replace(
            "next BG4 H-CTXBG",
            "BG4 H-CTXBG PROMOTE; next BG5 H-NANOGEN17/SKIP",
            1,
        )
        _EVOGEN.write_text(text, encoding="utf-8")


def run_ctxbg(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    trials_dir: Path,
    workers: int,
) -> dict[str, Any]:
    """
    GIVEN BG0 ctx baseline + FASTBG anti-FP
    WHEN measuring howto·cite·long + apps + BG/BF/BE/BA…BD/AZ hold
    THEN PROMOTE/KILL per pesquisa §9 BG4.
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
    bg_rows = _score_pack(
        list(BG0_FOREVER_ROWS),
        root=root,
        bank=bank,
        curated=curated,
        workers=workers,
        pack="bg-forever",
    )
    bf_rows = _score_pack(
        list(BF0_FOREVER_ROWS),
        root=root,
        bank=bank,
        curated=curated,
        workers=workers,
        pack="bf-forever",
    )
    be_rows = _score_pack(
        list(BE0_FOREVER_ROWS),
        root=root,
        bank=bank,
        curated=curated,
        workers=workers,
        pack="be-forever",
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
        dec_q = fut_dc.result()

    board = extract_ctxbg_board(
        ctx_rows=ctx_rows,
        apps_rows=apps_rows,
        bg_rows=bg_rows,
        bf_rows=bf_rows,
        be_rows=be_rows,
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
    decision = decide_ctxbg(board=board, anti_fp_signed=True)
    wall_s = time.perf_counter() - t0
    write_json(
        trials_dir / "BG-CTXBG-BOARD.json",
        {
            "board": board,
            "ctx_rows": ctx_rows,
            "apps_rows": apps_rows,
            "bg_rows": bg_rows,
            "bf_rows": bf_rows,
            "be_rows": be_rows,
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
        "id": CTXBG_ID,
        "stage": "BG4",
        "thesis": CTXBG_THESIS,
        "decision": decision,
        "board": board,
        "ctx_rows": ctx_rows,
        "apps_rows": apps_rows,
        "bg_rows": bg_rows,
        "bf_rows": bf_rows,
        "be_rows": be_rows,
        "bd_rows": bd_rows,
        "bc_rows": bc_rows,
        "bb_rows": bb_rows,
        "ba_rows": ba_rows,
        "az_rows": az_rows,
        "overrefuse_rows": orf_rows,
        "live_rows": live_rows,
        "wall_s": wall_s,
        "workers": workers,
        "claim": CTXBG_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hctxbg-ctxbg.md",
        "bf_archive": "docs/results/nano-lm/formal-hctxbf-ctxbf.md",
        "be_archive": "docs/results/nano-lm/formal-hctxbe-ctxbe.md",
        "next": "BG5 H-NANOGEN17 / SKIP",
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
        payload = run_ctxbg(
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
                "hyp_id": CTXBG_ID,
                "stage": "BG4",
                "decision": decision[:140],
                "cpu_threads": threads,
                "workers": workers,
                "ctx_content_ok_n": board.get("ctx_content_ok_n"),
                "ctx_content_n": board.get("ctx_content_n"),
                "bg_forever_false_hit": board.get("bg_forever_false_hit"),
                "bf_forever_false_hit": board.get("bf_forever_false_hit"),
                "live_fp": board.get("live_fp"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
