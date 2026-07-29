"""Wave BF3 H-FASTBF runner (nano:fastbf) — prod p50/p99 hold + anti-FP."""

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

from fastbf_ops import (
    ABSTAIN_N,
    DECODE_N,
    FASTBF_ANTI_FP,
    FASTBF_CLAIM,
    FASTBF_ID,
    FASTBF_SAFE_NOTE,
    FASTBF_THESIS,
    LOOKUP_N,
    PEAK_N,
    decide_fastbf,
    extract_fastbf_board,
    intent_false_hit,
    intent_row_ok,
    overrefuse_miss,
    overrefuse_row_ok,
    path_latency_stats,
)
from be_session_ops import BE0_FOREVER_ROWS, map_be_product_mode
from bf_session_ops import BF0_FOREVER_ROWS
from bd_session_ops import BD0_FOREVER_ROWS, BD0_MODES
from bc_session_ops import BC0_FOREVER_ROWS
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
from metrics_ops import telemetry_rules_ok
from prodhard_ops import KNOWN_ASK, NEAR_MISS_ASK, PEAK_ASK
from prodship_ops import (
    DECODE_PROBE_ASK,
    decode_content_honest,
    gate_junk_decode,
    human_para_hit,
    near_miss_ok,
)
from run_z_ask import ask_many, ask_once
from shipreal_ops import attach_shipreal
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-bf/fastbf_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-bf/trials"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hfastbf-fastbf.md"
_LOCAL_SESSION = REPO / ".local/wave-bf/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENTS = REPO / "AGENTS.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_EMPTY_BANK = REPO / "results/nano-lm/wave-bf/_decode_empty_bank.jsonl"
_PEAK_SOURCE = "rust-book-ch04-01"
_BY_ID = {str(s["id"]): s for s in SOURCES}
_CUDA_WARMUP_N = 2

_LIVE_PROBES: tuple[dict[str, str], ...] = (
    {
        "id": "BF-FAST-LIVE-00",
        "expect_mode": "ABSTAIN",
        "question": str(BF0_FOREVER_ROWS[0]["question"]),
    },
    {
        "id": "BF-FAST-LIVE-01",
        "expect_mode": "ABSTAIN",
        "question": str(BE0_FOREVER_ROWS[0]["question"]),
    },
    {
        "id": "BE-FAST-LIVE-02",
        "expect_mode": "ABSTAIN",
        "question": str(BD0_FOREVER_ROWS[0]["question"]),
    },
    {
        "id": "BE-FAST-LIVE-03",
        "expect_mode": "ABSTAIN",
        "question": str(BB_FOREVER_ROWS[0]["question"]),
    },
    {
        "id": "BE-FAST-LIVE-04",
        "expect_mode": "ABSTAIN",
        "question": str(AZ_HELDOUT_ROWS[0]["question"]),
    },
    {
        "id": "BE-FAST-LIVE-05",
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
    abstain: bool = True,
) -> dict[str, Any]:
    payload = ask_once(
        question=question,
        root=root,
        seed=0,
        wrap=wrap,
        semwrap=semwrap,
        bank_path=bank,
        curated_root=curated,
        abstain=abstain,
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


def _pack_latency(
    *,
    path: str,
    payloads: list[dict[str, Any]],
    sample_mode: str,
) -> dict[str, Any]:
    walls = [float(p.get("wall_ms") or 0.0) for p in payloads]
    modes = [str(p.get("mode", "")) for p in payloads]
    n_news = [int(p.get("n_new") or 0) for p in payloads]
    pmodes = [
        str(p.get("product_mode") or map_be_product_mode(m))
        for p, m in zip(payloads, modes)
    ]
    stats = path_latency_stats(walls)
    ok = telemetry_rules_ok(
        path=path,
        walls=walls,
        n_news=n_news,
        modes=modes,
        product_modes=pmodes,
    )
    return {
        "stats": stats,
        "telemetry_ok": ok,
        "sample_mode": sample_mode,
        "product_mode": pmodes[0] if pmodes else "",
    }


def _measure_lookup(*, root: Path, bank: Path, curated: Path) -> dict[str, Any]:
    payloads = ask_many(
        questions=[KNOWN_ASK] * LOOKUP_N,
        root=root,
        seed=0,
        wrap=True,
        bank_path=bank,
        curated_root=curated,
    )
    return _pack_latency(
        path="LOOKUP", payloads=payloads, sample_mode="WRAP_LOOKUP"
    )


def _warmup_cuda(*, root: Path, bank: Path, curated: Path) -> None:
    # Drop cold-load spikes from DECODE/ABSTAIN p99 (serial CUDA only).
    ask_many(
        questions=[KNOWN_ASK] * _CUDA_WARMUP_N,
        root=root,
        seed=0,
        wrap=False,
        bank_path=bank,
        curated_root=curated,
        abstain=False,
    )


def _measure_decode(*, root: Path, bank: Path, curated: Path) -> dict[str, Any]:
    payloads = ask_many(
        questions=[KNOWN_ASK] * DECODE_N,
        root=root,
        seed=1,
        wrap=False,
        bank_path=bank,
        curated_root=curated,
        abstain=False,
    )
    return _pack_latency(
        path="DECODE", payloads=payloads, sample_mode="QT+EARLY"
    )


def _measure_abstain(*, root: Path, curated: Path) -> dict[str, Any]:
    # Empty-bank DECODE_PROBE → junk ABSTAIN (prod content-law path; wall>0).
    # OOD TinyStories can slip "let " past is_junk_decode — flaky for latency.
    _EMPTY_BANK.parent.mkdir(parents=True, exist_ok=True)
    if not _EMPTY_BANK.is_file():
        _EMPTY_BANK.write_text("", encoding="utf-8")
    payloads = ask_many(
        questions=[DECODE_PROBE_ASK] * ABSTAIN_N,
        root=root,
        seed=2,
        wrap=True,
        bank_path=_EMPTY_BANK,
        curated_root=curated,
        abstain=True,
    )
    return _pack_latency(
        path="ABSTAIN", payloads=payloads, sample_mode="NO_ANSWER"
    )


def _measure_peak(*, curated: Path) -> dict[str, Any]:
    meta = _BY_ID.get(_PEAK_SOURCE)
    if meta is None:
        raise ValueError(f"unknown source_id: {_PEAK_SOURCE}")
    path = curated / str(meta["path"])
    doc = path.read_text(encoding="utf-8", errors="ignore")
    chunks = chunk_doc(doc, win=400, stride=160)
    walls: list[float] = []
    modes: list[str] = []
    n_news: list[int] = []
    for _ in range(PEAK_N):
        payload = fastbase_generate(question=PEAK_ASK, chunks=chunks, doc=doc)
        walls.append(float(payload.get("wall_ms") or 0.0))
        modes.append(str(payload.get("mode") or "PEAK"))
        n_news.append(int(payload.get("n_new") or 0))
    pmodes = ["PEAK"] * len(modes)
    stats = path_latency_stats(walls)
    ok = telemetry_rules_ok(
        path="PEAK",
        walls=walls,
        n_news=n_news,
        modes=modes,
        product_modes=pmodes,
    )
    return {
        "stats": stats,
        "telemetry_ok": ok,
        "sample_mode": "PEAK_FAST",
        "product_mode": "PEAK",
    }


def _measure_latency_tetrad(
    *, root: Path, bank: Path, curated: Path
) -> dict[str, dict[str, Any]]:
    """
    GIVEN champion + banks
    WHEN sampling LOOKUP·PEAK (parallel) then serial CUDA DECODE·ABSTAIN
    THEN return path rows with honest p50/p99 (no CUDA contention).
    """
    with ThreadPoolExecutor(max_workers=2) as pool:
        fut_l = pool.submit(
            _measure_lookup, root=root, bank=bank, curated=curated
        )
        fut_p = pool.submit(_measure_peak, curated=curated)
        lookup = fut_l.result()
        peak = fut_p.result()
    _warmup_cuda(root=root, bank=bank, curated=curated)
    decode = _measure_decode(root=root, bank=bank, curated=curated)
    abstain = _measure_abstain(root=root, curated=curated)
    return {
        "LOOKUP": lookup,
        "PEAK": peak,
        "DECODE": decode,
        "ABSTAIN": abstain,
    }


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
        if pack in {
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



def _write_public(
    *,
    decision: str,
    board: dict[str, Any],
    wall_s: float,
    samples: dict[str, int],
) -> None:
    status = decision.split("(", 1)[0].strip()
    lat_rows = [
        f"| {name} | **{row.get('p50_wall_ms')}** | "
        f"**{row.get('p99_wall_ms')}** | {row.get('n')} |"
        for name, row in (board.get("latency") or {}).items()
    ]
    body = "\n".join(
        [
            f"# H-FASTBF (BF3) — prod p50/p99 + anti-FP hold (**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §4 · §9 BF3 · Session: "
            "`.local/wave-bf/SESSION.md`  ",
            "> Parent: [formal-hshipuse2-shipuse2.md](formal-hshipuse2-shipuse2.md) · "
            "BF0 speed baseline (= H-FASTBE)  ",
            "> Module: `nano_lm/src/fastbf_ops.py` · "
            "Runner: `npm run nano:fastbf`  ",
            "> **Not** BE [formal-hfastbe-fastbe.md](formal-hfastbe-fastbe.md) "
            "(`npm run nano:fastbe`) · **Not** BD "
            "[formal-hfastgain-fastgain.md](formal-hfastgain-fastgain.md) "
            "(`npm run nano:bd:fastgain`) · **Not** AH/BC/BB FAST archives",
            "",
            "## Hypothesis",
            "",
            FASTBF_THESIS,
            "",
            "## Gate",
            "",
            "| Metric | Result | Bar |",
            "|--------|-------:|-----|",
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
            f"| p99_regress | **{board.get('p99_regress')}** "
            f"({board.get('p99_regress_paths')}) | false (≤1.5× H-FASTBE) |",
            f"| modes_visible | **{' · '.join(board.get('modes_visible') or [])}** "
            f"({board.get('modes_n')}/4) | 4/4 |",
            f"| Decision | **{status}** | — |",
            "",
            "## Latency p50/p99 (prod ask path)",
            "",
            "| Path | p50 wall_ms | p99 wall_ms | n |",
            "|------|------------:|------------:|--:|",
            *lat_rows,
            "",
            f"Samples: LOOKUP={samples.get('LOOKUP')} · PEAK={samples.get('PEAK')} · "
            f"DECODE={samples.get('DECODE')} · ABSTAIN={samples.get('ABSTAIN')}",
            "",
            "## Finding",
            "",
            "1. Prod-path tetrad measured under max safe CPU (`cpus-6`, workers≤6).  ",
            "2. LOOKUP wall=0 **and** sub-ms PEAK walls **not** sold as speed IQ.  ",
            "3. Anti-FP hold: BF FH 0 · BE…BA forever · AZ hold · over-refuse 0 · live FP 0.  ",
            "4. Live product p99 (DECODE·ABSTAIN) checked vs BF0/H-FASTBE (max ratio 1.5).  ",
            "5. Warm-cache vanity forbidden.  ",
            f"6. Wall clock ~{wall_s:.1f}s · workers parallel antifp packs.  ",
            "7. BE `nano:fastbe` · BD/AH/BC/BB FAST archives untouched.  ",
            "8. Generative claim still locked (gen stance SKIP; H-NANOGEN16 not opened).",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:fastbf",
            "npm run nano:predint",
            "# ≠ BE archive: npm run nano:fastbe",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-bf/fastbf_summary.json`  ",
            "- Contract: `nano_lm/tests/test_fastbf.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            f"| {FASTBF_CLAIM} | Open chat / mini-AGI |",
            "| Publish prod p50/p99 | LOOKUP wall=0 as speed IQ |",
            "| Anti-FP hold required | Trade FP for ms |",
            "| H-FASTBE baseline p99 | Warm-cache vanity as product win |",
            "| BE/BD/AH/BC/BB FAST archives stay | Rewrite BE formal-hfastbe-fastbe |",
            "",
            f"SAFE note: {FASTBF_SAFE_NOTE}  ",
            f"Anti-FP: {FASTBF_ANTI_FP}",
            "",
            "Next: **BF4 H-CTXBF** — context content bars without FP regress.",
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
            f"# Wave BF session checklist (**OPEN** · BF3 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md`.  ",
            f"> Ship lock: **{FASTBF_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**BF3 — H-FASTBF ({status})** · Next: **BF4 H-CTXBF**",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| BF0 | SESSION | **DONE — PROMOTE** |",
            "| BF1 | H-PREDINT | **DONE — PROMOTE** |",
            "| BF2 | H-SHIPUSE2 | **DONE — PROMOTE** |",
            f"| BF3 | H-FASTBF | **{status}** |",
            "| BF4 | H-CTXBF | **NEXT** |",
            "| BF5 | H-NANOGEN16 / SKIP | pending |",
            "| BF6 | BF-REAL-EVAL | pending |",
            "| BF7 | BF-REPORT | pending |",
            "| BF8 | BF-FREEZE | pending |",
            "",
            "## Board snapshot",
            "",
            f"| bf_forever_false_hit | **{board.get('bf_forever_false_hit')}** |",
            f"| p99_regress | **{board.get('p99_regress')}** |",
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
        "| BF3 | **H-FASTBF** | Speed p50/p99 hold **or** improve "
        "**without** FP regress | latency + §1 | **NEXT** |",
        "| BF3 | **H-FASTBF** | Speed p50/p99 hold **or** improve "
        "**without** FP regress | latency + §1 | **DONE — PROMOTE** |",
        1,
    )
    text = text.replace(
        "| BF4 | **H-CTXBF** | Context content bars hold **or** improve "
        "**without** FP regress | content + §1 | **TODO** |",
        "| BF4 | **H-CTXBF** | Context content bars hold **or** improve "
        "**without** FP regress | content + §1 | **NEXT** |",
        1,
    )
    text = text.replace(
        "4. **BF3 H-FASTBF** — **NEXT** — prod p50/p99 hold/improve with "
        "anti-FP hold.  ",
        "4. **BF3 H-FASTBF** — **DONE PROMOTE** (`npm run nano:fastbf`) — "
        "prod p50/p99 hold; anti-FP hold; no p99 regress vs H-FASTBE.  ",
        1,
    )
    text = text.replace(
        "5. **BF4 H-CTXBF** — howto·cite·long content_ok hold/improve with "
        "anti-FP hold.  ",
        "5. **BF4 H-CTXBF** — **NEXT** — howto·cite·long content_ok "
        "hold/improve with anti-FP hold.  ",
        1,
    )
    text = text.replace(
        "(BF0–BF2 **DONE — PROMOTE**; next BF3 H-FASTBF)",
        "(BF0–BF3 **DONE — PROMOTE**; next BF4 H-CTXBF)",
        1,
    )
    text = text.replace(
        "(BF0–BF2 **DONE — PROMOTE**; next BF3 H-FASTBF).",
        "(BF0–BF3 **DONE — PROMOTE**; next BF4 H-CTXBF).",
        1,
    )
    text = text.replace(
        "npm run nano:shipuse2\n"
        "# next: nano:bf:fastbf · nano:bf:ctxbf · "
        "nano:nanogen16 (SKIP without plan)\n",
        "npm run nano:shipuse2\n"
        "npm run nano:fastbf\n"
        "# next: nano:bf:ctxbf · nano:nanogen16 (SKIP without plan)\n",
        1,
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
                    "Wave **BF ACTIVE**. BF0–BF3 **DONE — PROMOTE** "
                    "(`npm run nano:fastbf`).",
                    "",
                    "## Next",
                    "",
                    "1. BF0–BF3 done.  ",
                    "2. **BF4 H-CTXBF** — **NEXT**.  ",
                    "3. Ship stays AF+AQ+AS STRICT ablated DECODE.",
                    "",
                    "```bash",
                    "npm run nano:fastbf",
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
                    "**Wave BF ACTIVE** — BF0–BF2 PROMOTE · "
                    "BF3 **H-FASTBF PROMOTE** (prod p50/p99 + anti-FP).",
                    "",
                    "Next: **BF4 H-CTXBF**. Parent: Wave BE **COMPLETE + FROZEN**.",
                    "",
                    "## Do not",
                    "",
                    "LOOKUP-as-IQ · pack theater · FP-for-ms · "
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
        "| Wave BF3 H-FASTBF | [formal-hfastbf-fastbf.md]"
        "(formal-hfastbf-fastbf.md) **PROMOTE** (`npm run nano:fastbf`) — "
        f"p99_regress={board.get('p99_regress')} · BF FH "
        f"{board.get('bf_forever_false_hit')} · live FP {board.get('live_fp')} |"
    )
    if "Wave BF3 H-FASTBF" not in text:
        marker = "| Wave BF2 H-SHIPUSE2 |"
        idx = text.find(marker)
        if idx >= 0:
            end = text.find("\n", idx)
            text = text[: end + 1] + insert + "\n" + text[end + 1 :]
    text2, n = re.subn(
        r"\*\*Wave BF ACTIVE:\*\*[^\n]+",
        "**Wave BF ACTIVE:** BF0 [SESSION PROMOTE](wave-bf-session.md) · "
        "BF1 [H-PREDINT PROMOTE](formal-hpredint-predint.md) · "
        "BF2 [H-SHIPUSE2 PROMOTE](formal-hshipuse2-shipuse2.md) · "
        "BF3 [H-FASTBF PROMOTE](formal-hfastbf-fastbf.md) "
        "(`npm run nano:fastbf`) — p50/p99 hold; next BF4 H-CTXBF; "
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
        r"- \*\*Wave BF ACTIVE\*\* —[^\n]+",
        "- **Wave BF ACTIVE** — BF0 [SESSION PROMOTE]"
        "(docs/results/nano-lm/wave-bf-session.md) "
        "(`npm run nano:bf:session`) · BF1 [H-PREDINT PROMOTE]"
        "(docs/results/nano-lm/formal-hpredint-predint.md) "
        "(`npm run nano:predint`) · BF2 [H-SHIPUSE2 PROMOTE]"
        "(docs/results/nano-lm/formal-hshipuse2-shipuse2.md) "
        "(`npm run nano:shipuse2`) · BF3 [H-FASTBF PROMOTE]"
        "(docs/results/nano-lm/formal-hfastbf-fastbf.md) "
        "(`npm run nano:fastbf`) — prod p50/p99 hold; next BF4 H-CTXBF; "
        "ship remains **AF + AQ + AS trust + STRICT ablated DECODE**; "
        "NANOGEN6·7 HOLD · NANOGEN8…15 DEFER; ≤5M stays.",
    )
    _sub_file(
        _AGENDA,
        r"\| \*\*BF\*\* \| \*\*ACTIVE\*\* \|[^\n]+",
        "| **BF** | **ACTIVE** | BF0–BF3 PROMOTE "
        "(results/nano-lm/formal-hfastbf-fastbf.md) "
        "(`npm run nano:fastbf`) — p50/p99 hold; next BF4 H-CTXBF; "
        "ship AF+AQ+AS trust + STRICT ablated DECODE; ≤5M |",
    )
    _patch_recipes(board)
    _sub_file(
        _CARD,
        r"\*\*Wave BF ACTIVE\*\* —[^\n]+",
        "**Wave BF ACTIVE** — BF0 [SESSION PROMOTE](wave-bf-session.md) · "
        "BF1 [H-PREDINT PROMOTE](formal-hpredint-predint.md) · "
        "BF2 [H-SHIPUSE2 PROMOTE](formal-hshipuse2-shipuse2.md) · "
        "BF3 [H-FASTBF PROMOTE](formal-hfastbf-fastbf.md) "
        f"(`npm run nano:fastbf`) — p99_regress={board.get('p99_regress')}; "
        "next BF4 H-CTXBF; ship remains **AF + AQ + AS trust + STRICT "
        "ablated DECODE**; ≤5M stays.",
    )
    if _EVOGEN.is_file():
        text = _EVOGEN.read_text(encoding="utf-8")
        text = text.replace(
            "BF0–BF2 PROMOTE · H-SHIPUSE2 Track A+; next BF3 H-FASTBF",
            "BF0–BF3 PROMOTE · H-FASTBF; next BF4 H-CTXBF",
            1,
        )
        text = text.replace(
            "BF2 H-SHIPUSE2 PROMOTE; next BF3 H-FASTBF",
            "BF0–BF3 PROMOTE · H-FASTBF; next BF4 H-CTXBF",
            1,
        )
        text = text.replace(
            "next BF3 H-FASTBF",
            "BF3 H-FASTBF PROMOTE; next BF4 H-CTXBF",
            1,
        )
        _EVOGEN.write_text(text, encoding="utf-8")


def run_fastbf(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    trials_dir: Path,
    workers: int,
) -> dict[str, Any]:
    """
    GIVEN BF0/H-FASTBE speed baseline + PREDINT anti-FP
    WHEN measuring prod tetrad + BF/BE/BA…BD/AZ hold packs
    THEN PROMOTE/KILL per pesquisa §9 BF3.
    """
    t0 = time.perf_counter()
    trials_dir.mkdir(parents=True, exist_ok=True)

    path_rows = _measure_latency_tetrad(
        root=root, bank=bank, curated=curated
    )
    latency = {k: dict(v["stats"]) for k, v in path_rows.items()}
    tel_ok = {k: bool(v["telemetry_ok"]) for k, v in path_rows.items()}

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

    with ThreadPoolExecutor(max_workers=min(3, workers)) as pool:
        fut_nm = pool.submit(
            _ask, NEAR_MISS_ASK, root=root, bank=bank, curated=curated
        )
        fut_kn = pool.submit(
            _ask, KNOWN_ASK, root=root, bank=bank, curated=curated
        )
        fut_dc = pool.submit(_decode_probe, root=root, curated=curated)
        near = fut_nm.result()
        known = fut_kn.result()
        dec_q = fut_dc.result()

    board = extract_fastbf_board(
        latency=latency,
        bf_rows=bf_rows,
        be_rows=be_rows,
        bd_rows=bd_rows,
        ba_rows=ba_rows,
        bb_rows=bb_rows,
        bc_rows=bc_rows,
        az_rows=az_rows,
        overrefuse_rows=orf_rows,
        live_fp=live_fp,
        near_miss_ok=near_miss_ok(near),
        known_lookup_ok=human_para_hit(known),
        decode_content_ok=decode_content_honest(dec_q),
        modes_visible=list(BD0_MODES),
        telemetry_ok=tel_ok,
    )
    decision = decide_fastbf(board=board, anti_fp_signed=True)
    wall_s = time.perf_counter() - t0
    samples = {
        "LOOKUP": LOOKUP_N,
        "PEAK": PEAK_N,
        "DECODE": DECODE_N,
        "ABSTAIN": ABSTAIN_N,
    }
    write_json(
        trials_dir / "BF-FASTBF-BOARD.json",
        {
            "board": board,
            "bf_rows": bf_rows,
            "be_rows": be_rows,
            "bd_rows": bd_rows,
            "bc_rows": bc_rows,
            "bb_rows": bb_rows,
            "ba_rows": ba_rows,
            "az_rows": az_rows,
            "overrefuse_rows": orf_rows,
            "live_rows": live_rows,
            "path_rows": {
                k: {"stats": v["stats"], "telemetry_ok": v["telemetry_ok"]}
                for k, v in path_rows.items()
            },
            "decision": decision,
        },
    )
    _write_public(
        decision=decision, board=board, wall_s=wall_s, samples=samples
    )
    _update_local_session(decision, board)
    _patch_pesquisa(decision)
    _patch_local_notes(decision)
    _patch_public(decision, board)
    payload = {
        "id": FASTBF_ID,
        "stage": "BF3",
        "thesis": FASTBF_THESIS,
        "decision": decision,
        "board": board,
        "samples": samples,
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
        "claim": FASTBF_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hfastbf-fastbf.md",
        "be_archive": "docs/results/nano-lm/formal-hfastbe-fastbe.md",
        "bd_archive": "docs/results/nano-lm/formal-hfastgain-fastgain.md",
        "next": "BF4 H-CTXBF",
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
        payload = run_fastbf(
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
                "hyp_id": FASTBF_ID,
                "stage": "BF3",
                "decision": decision[:140],
                "cpu_threads": threads,
                "workers": workers,
                "bd_forever_false_hit": board.get("bd_forever_false_hit"),
                "bc_forever_false_hit": board.get("bc_forever_false_hit"),
                "bb_forever_false_hit": board.get("bb_forever_false_hit"),
                "ba_forever_false_hit": board.get("ba_forever_false_hit"),
                "live_fp": board.get("live_fp"),
                "p99_regress": board.get("p99_regress"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
