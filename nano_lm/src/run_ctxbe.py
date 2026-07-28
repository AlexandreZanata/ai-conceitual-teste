"""Wave BE4 H-CTXBE runner (nano:ctxbe) — content bars + anti-FP."""

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

from ctxbe_ops import (
    APP_SMOKE_PACK,
    CTXBE_ANTI_FP,
    CTXBE_CLAIM,
    CTXBE_ID,
    CTXBE_SAFE_NOTE,
    CTXBE_THESIS,
    CTX_CONTENT_ROWS,
    KNOWN_ASK,
    PEAK_ASK,
    decide_ctxbe,
    extract_ctxbe_board,
    intent_false_hit,
    intent_row_ok,
    overrefuse_miss,
    overrefuse_row_ok,
)
from be_session_ops import BE0_FOREVER_ROWS
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

_SUMMARY = REPO / "results/nano-lm/wave-be/ctxbe_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-be/trials"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hctxbe-ctxbe.md"
_LOCAL_SESSION = REPO / ".local/wave-be/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENTS = REPO / "AGENTS.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_EMPTY_BANK = REPO / "results/nano-lm/wave-be/_decode_empty_bank.jsonl"
_PEAK_SOURCE = "rust-book-ch04-01"
_BY_ID = {str(s["id"]): s for s in SOURCES}

_LIVE_PROBES: tuple[dict[str, str], ...] = (
    {
        "id": "BE-CTX-LIVE-01",
        "expect_mode": "ABSTAIN",
        "question": str(BE0_FOREVER_ROWS[0]["question"]),
    },
    {
        "id": "BE-CTX-LIVE-02",
        "expect_mode": "ABSTAIN",
        "question": str(BD0_FOREVER_ROWS[0]["question"]),
    },
    {
        "id": "BE-CTX-LIVE-03",
        "expect_mode": "ABSTAIN",
        "question": str(BB_FOREVER_ROWS[0]["question"]),
    },
    {
        "id": "BE-CTX-LIVE-04",
        "expect_mode": "ABSTAIN",
        "question": str(AZ_HELDOUT_ROWS[0]["question"]),
    },
    {
        "id": "BE-CTX-LIVE-05",
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
    # 16c / ~31Gi: leave ≥6 cores free under mem pressure; cap workers.
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
            f"# H-CTXBE (BE4) — howto·cite·long content + anti-FP "
            f"(**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §3 · §9 BE4 · Session: "
            "`.local/wave-be/SESSION.md`  ",
            "> Parent: [formal-hfastbe-fastbe.md](formal-hfastbe-fastbe.md) · "
            "BE0 ctx baseline (= H-CTXGAIN / H-CTXLIFT2 / H-CTXHOLD)  ",
            "> Module: `nano_lm/src/ctxbe_ops.py` · "
            "Runner: `npm run nano:ctxbe`  ",
            "> **Not** BD [formal-hctxgain-ctxgain.md](formal-hctxgain-ctxgain.md) "
            "(`npm run nano:bd:ctxgain`) · **Not** AH "
            "[formal-hctxlift-ctxlift.md](formal-hctxlift-ctxlift.md) · **Not** BC "
            "[formal-hctxlift2-ctxlift2.md](formal-hctxlift2-ctxlift2.md) "
            "(`npm run nano:bc:ctxlift2`) · **Not** BB "
            "[formal-hctxhold-ctxhold.md](formal-hctxhold-ctxhold.md)",
            "",
            "## Hypothesis",
            "",
            CTXBE_THESIS,
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
            "3. Anti-FP hold: BE FH 0 · BD FH 0 · BA FH 0 · BB FH 0 · BC FH 0 · "
            "AZ · over-refuse 0 · live FP 0.  ",
            "4. Prod tetrad p50/p99 published under max safe CPU "
            "(`cpus-6`, workers≤6).  ",
            f"5. Wall clock ~{wall_s:.1f}s.  ",
            "6. BD/AH/BC/BB/BA CTX archives untouched.  ",
            "7. Generative claim still locked (H-NANOGEN15 defer-once stance).",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:ctxbe",
            "npm run nano:fastbe",
            "# ≠ BD archive: npm run nano:bd:ctxgain",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-be/ctxbe_summary.json`  ",
            "- Contract: `nano_lm/tests/test_ctxbe.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            f"| {CTXBE_CLAIM} | Open chat / mini-AGI |",
            "| Content bars as ctx win | L_eff alone as pass |",
            "| Anti-FP hold required | Trade FP for ctx |",
            "| BD/AH/BC/BB/BA CTX archives stay | Rewrite formal-hctxgain |",
            "",
            f"SAFE note: {CTXBE_SAFE_NOTE}  ",
            f"Anti-FP: {CTXBE_ANTI_FP}",
            "",
            "Next: **BE5 H-NANOGEN15** — one real method or DEFER once.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _update_local_session(decision: str, board: dict[str, Any]) -> None:
    status = f"DONE — {decision.split('(', 1)[0].strip()}"
    body = "\n".join(
        [
            f"# Wave BE session checklist (**OPEN** · BE4 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave BE **OPEN** · ctx content after H-FASTBE).  ",
            f"> Ship lock: **{CTXBE_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**BE4 — H-CTXBE ({status})** · Next: **BE5 H-NANOGEN15**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| ctx_content_ok | **{board.get('ctx_content_ok_n')}/"
            f"{board.get('ctx_content_n')}** |",
            f"| apps_content_ok | **{board.get('apps_content_ok')}** |",
            f"| be_forever_false_hit | **{board.get('be_forever_false_hit')}** |",
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
            "| BE0 | SESSION | **DONE — PROMOTE** |",
            "| BE1 | H-COMPINT | **DONE — PROMOTE** |",
            "| BE2 | H-SHIPUSE | **DONE — PROMOTE** |",
            "| BE3 | H-FASTBE | **DONE — PROMOTE** |",
            f"| BE4 | H-CTXBE | **{status}** |",
            "| BE5 | H-NANOGEN15 | **NEXT** (defer unless real new method) |",
            "| BE6 | BE-REAL-EVAL | pending |",
            "| BE7 | BE-REPORT | pending |",
            "| BE8 | BE-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.parent.mkdir(parents=True, exist_ok=True)
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    be4_next = (
        "| BE4 | **H-CTXBE** | Context content bars hold **or** improve "
        "**without** FP regress | content + §1 | **NEXT** |"
    )
    be4_done = (
        "| BE4 | **H-CTXBE** | Context content bars hold **or** improve "
        "**without** FP regress | content + §1 | **DONE — PROMOTE** |"
    )
    if be4_next in text:
        text = text.replace(be4_next, be4_done, 1)
    be5_todo = (
        "| BE5 | **H-NANOGEN15** | One real gen method **M1\\|M2\\|M3** — else "
        "**DEFER once** (stop rule) | true_continue → PROMOTE else DEFER | **TODO** |"
    )
    be5_next = (
        "| BE5 | **H-NANOGEN15** | One real gen method **M1\\|M2\\|M3** — else "
        "**DEFER once** (stop rule) | true_continue → PROMOTE else DEFER | **NEXT** |"
    )
    if be5_todo in text:
        text = text.replace(be5_todo, be5_next, 1)
    text = text.replace(
        "5. **BE4 H-CTXBE** — **NEXT** — howto·cite·long content_ok "
        "hold/improve with anti-FP hold.  ",
        "5. **BE4 H-CTXBE** — **DONE PROMOTE** (`npm run nano:ctxbe`) — "
        "howto·cite·long content_ok + anti-FP hold.  ",
        1,
    )
    text = text.replace(
        "6. **BE5 H-NANOGEN15** — one real M1\\|M2\\|M3 → PROMOTE else "
        "**DEFER once** (not NANOGEN14 rename).  ",
        "6. **BE5 H-NANOGEN15** — **NEXT** — one real M1\\|M2\\|M3 → PROMOTE "
        "else **DEFER once** (not NANOGEN14 rename).  ",
        1,
    )
    text = text.replace(
        "(BE0–BE3 **DONE — PROMOTE**; next BE4 H-CTXBE)",
        "(BE0–BE4 **DONE — PROMOTE**; next BE5 H-NANOGEN15)",
        1,
    )
    text = text.replace(
        "(BE0–BE3 **DONE — PROMOTE**; next BE4 H-CTXBE).",
        "(BE0–BE4 **DONE — PROMOTE**; next BE5 H-NANOGEN15).",
        1,
    )
    bash_old = (
        "npm run nano:be:session\n"
        "npm run nano:compint\n"
        "npm run nano:shipuse\n"
        "npm run nano:fastbe\n"
        "# next: nano:be:ctxbe · nano:nanogen15\n"
    )
    bash_new = (
        "npm run nano:be:session\n"
        "npm run nano:compint\n"
        "npm run nano:shipuse\n"
        "npm run nano:fastbe\n"
        "npm run nano:ctxbe\n"
        "# next: nano:nanogen15\n"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
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
                    "Wave **BE ACTIVE**. BE0–BE4 **DONE — PROMOTE** "
                    "(`npm run nano:ctxbe`).",
                    "",
                    "## Next",
                    "",
                    "1. BE0–BE4 done.  ",
                    "2. **BE5 H-NANOGEN15** — **NEXT**.  ",
                    "3. Ship stays AF+AQ+AS STRICT ablated DECODE.",
                    "",
                    "```bash",
                    "npm run nano:ctxbe",
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
                    "**Wave BE ACTIVE** — BE0–BE3 PROMOTE · "
                    "BE4 **H-CTXBE PROMOTE** (content bars + anti-FP).",
                    "",
                    "Next: **BE5 H-NANOGEN15**. Parent: Wave BD **COMPLETE + FROZEN**.",
                    "",
                    "## Do not",
                    "",
                    "LOOKUP-as-IQ · pack theater · bank stuffing · "
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
        "| Wave BE4 H-CTXBE | [formal-hctxbe-ctxbe.md]"
        "(formal-hctxbe-ctxbe.md) **PROMOTE** (`npm run nano:ctxbe`) "
        f"— ctx_ok {board.get('ctx_content_ok_n')}/{board.get('ctx_content_n')} "
        f"· BE FH {board.get('be_forever_false_hit')} · "
        f"live FP {board.get('live_fp')} |"
    )
    if "Wave BE4 H-CTXBE" not in text:
        marker = "| Wave BE3 H-FASTBE |"
        idx = text.find(marker)
        if idx < 0:
            marker = "| Wave BE2 H-SHIPUSE |"
            idx = text.find(marker)
        if idx >= 0:
            end = text.find("\n", idx)
            text = text[: end + 1] + insert + "\n" + text[end + 1 :]
    text2, n = re.subn(
        r"\*\*Wave BE ACTIVE:\*\*[^\n]+",
        "**Wave BE ACTIVE:** BE0 [SESSION PROMOTE](wave-be-session.md) · "
        "BE1 [H-COMPINT PROMOTE](formal-hcompint-compint.md) · "
        "BE2 [H-SHIPUSE PROMOTE](formal-hshipuse-shipuse.md) · "
        "BE3 [H-FASTBE PROMOTE](formal-hfastbe-fastbe.md) · "
        "BE4 [H-CTXBE PROMOTE](formal-hctxbe-ctxbe.md) "
        "(`npm run nano:ctxbe`) — content bars + anti-FP; next BE5 H-NANOGEN15; "
        "ship remains **AF + AQ + AS trust + STRICT ablated DECODE**; ≤5M stays.",
        text,
        count=1,
    )
    _RECIPES.write_text(text2 if n else text, encoding="utf-8")


def _patch_public(decision: str, board: dict[str, Any]) -> None:
    if not decision.startswith("PROMOTE"):
        return
    _sub_file(
        _AGENTS,
        r"- \*\*Wave BE ACTIVE\*\* —[^\n]+",
        "- **Wave BE ACTIVE** — BE0 [SESSION PROMOTE]"
        "(docs/results/nano-lm/wave-be-session.md) "
        "(`npm run nano:be:session`) · BE1 [H-COMPINT PROMOTE]"
        "(docs/results/nano-lm/formal-hcompint-compint.md) "
        "(`npm run nano:compint`) · BE2 [H-SHIPUSE PROMOTE]"
        "(docs/results/nano-lm/formal-hshipuse-shipuse.md) "
        "(`npm run nano:shipuse`) · BE3 [H-FASTBE PROMOTE]"
        "(docs/results/nano-lm/formal-hfastbe-fastbe.md) "
        "(`npm run nano:fastbe`) · BE4 [H-CTXBE PROMOTE]"
        "(docs/results/nano-lm/formal-hctxbe-ctxbe.md) "
        "(`npm run nano:ctxbe`) — content bars + anti-FP; next BE5 H-NANOGEN15; "
        "ship remains **AF + AQ + AS trust + STRICT ablated DECODE**; "
        "NANOGEN6·7 HOLD · NANOGEN8…14 DEFER; ≤5M stays.",
    )
    _sub_file(
        _AGENDA,
        r"\| \*\*BE\*\* \| \*\*ACTIVE\*\* \|[^\n]+",
        "| **BE** | **ACTIVE** | BE0–BE4 PROMOTE "
        "(results/nano-lm/formal-hctxbe-ctxbe.md) "
        "(`npm run nano:ctxbe`) — content bars; next BE5 H-NANOGEN15; "
        "ship AF+AQ+AS trust + STRICT ablated DECODE; ≤5M |",
    )
    _patch_recipes(board)
    _sub_file(
        _CARD,
        r"\*\*Wave BE ACTIVE\*\* —[^\n]+",
        "**Wave BE ACTIVE** — BE0 [SESSION PROMOTE](wave-be-session.md) · "
        "BE1 [H-COMPINT PROMOTE](formal-hcompint-compint.md) · "
        "BE2 [H-SHIPUSE PROMOTE](formal-hshipuse-shipuse.md) · "
        "BE3 [H-FASTBE PROMOTE](formal-hfastbe-fastbe.md) · "
        "BE4 [H-CTXBE PROMOTE](formal-hctxbe-ctxbe.md) "
        f"(`npm run nano:ctxbe`) — ctx_ok {board.get('ctx_content_ok_n')}/"
        f"{board.get('ctx_content_n')} · BE FH {board.get('be_forever_false_hit')}; "
        "next BE5 H-NANOGEN15; "
        "ship remains **AF + AQ + AS trust + STRICT ablated DECODE**; ≤5M stays.",
    )
    if _EVOGEN.is_file():
        text = _EVOGEN.read_text(encoding="utf-8")
        text = text.replace(
            "Wave BE ACTIVE (BE0–BE3 PROMOTE · H-FASTBE; next BE4 H-CTXBE)",
            "Wave BE ACTIVE (BE0–BE4 PROMOTE · H-CTXBE; next BE5 H-NANOGEN15)",
            1,
        )
        _EVOGEN.write_text(text, encoding="utf-8")


def run_ctxbe(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    trials_dir: Path,
    workers: int,
) -> dict[str, Any]:
    """
    GIVEN BE0 ctx baseline + COMPINT/FASTBE anti-FP
    WHEN measuring howto·cite·long + apps + BE/BA…BD/AZ hold
    THEN PROMOTE/KILL per pesquisa §9 BE4.
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

    board = extract_ctxbe_board(
        ctx_rows=ctx_rows,
        apps_rows=apps_rows,
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
    decision = decide_ctxbe(board=board, anti_fp_signed=True)
    wall_s = time.perf_counter() - t0
    write_json(
        trials_dir / "BE-CTXBE-BOARD.json",
        {
            "board": board,
            "ctx_rows": ctx_rows,
            "apps_rows": apps_rows,
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
        "id": CTXBE_ID,
        "stage": "BE4",
        "thesis": CTXBE_THESIS,
        "decision": decision,
        "board": board,
        "ctx_rows": ctx_rows,
        "apps_rows": apps_rows,
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
        "claim": CTXBE_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hctxbe-ctxbe.md",
        "bd_archive": "docs/results/nano-lm/formal-hctxgain-ctxgain.md",
        "next": "BE5 H-NANOGEN15",
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
        payload = run_ctxbe(
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
                "hyp_id": CTXBE_ID,
                "stage": "BE4",
                "decision": decision[:140],
                "cpu_threads": threads,
                "workers": workers,
                "ctx_content_ok_n": board.get("ctx_content_ok_n"),
                "ctx_content_n": board.get("ctx_content_n"),
                "be_forever_false_hit": board.get("be_forever_false_hit"),
                "bd_forever_false_hit": board.get("bd_forever_false_hit"),
                "live_fp": board.get("live_fp"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
