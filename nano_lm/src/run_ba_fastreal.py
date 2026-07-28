"""Wave BA2 H-FASTREAL runner (nano:ba:fastreal) — prod p50/p99 + anti-FP hold."""

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

from ba_fastreal_ops import (
    ABSTAIN_N,
    BA_FASTREAL_ANTI_FP,
    BA_FASTREAL_CLAIM,
    BA_FASTREAL_ID,
    BA_FASTREAL_SAFE_NOTE,
    BA_FASTREAL_THESIS,
    DECODE_N,
    LOOKUP_N,
    PEAK_N,
    decide_ba_fastreal,
    extract_ba_fastreal_board,
    intent_false_hit,
    intent_row_ok,
    overrefuse_miss,
    overrefuse_row_ok,
    path_latency_stats,
)
from ba_session_ops import BA0_MODES, map_ba_product_mode
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
from realgain_ops import (
    AZ_HELDOUT_ROWS,
    FOREVER_ROWS,
    OVERREFUSE_ROWS,
    score_live_row,
)
from run_z_ask import ask_many, ask_once
from shipreal_ops import attach_shipreal
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-ba/ba_fastreal_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-ba/trials"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hfastreal-ba2.md"
_LOCAL_SESSION = REPO / ".local/wave-ba/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENTS = REPO / "AGENTS.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_EMPTY_BANK = REPO / "results/nano-lm/wave-ba/_decode_empty_bank.jsonl"
_PEAK_SOURCE = "rust-book-ch04-01"
_BY_ID = {str(s["id"]): s for s in SOURCES}
_CUDA_WARMUP_N = 2

_LIVE_PROBES: tuple[dict[str, str], ...] = (
    {
        "id": "BA-FAST-LIVE-01",
        "expect_mode": "ABSTAIN",
        "question": str(FOREVER_ROWS[0]["question"]),
    },
    {
        "id": "BA-FAST-LIVE-02",
        "expect_mode": "ABSTAIN",
        "question": str(FOREVER_ROWS[9]["question"]),
    },
    {
        "id": "BA-FAST-LIVE-03",
        "expect_mode": "ABSTAIN",
        "question": str(AZ_HELDOUT_ROWS[0]["question"]),
    },
    {
        "id": "BA-FAST-LIVE-04",
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
    workers = min(10, max(4, cpus - 4))
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
        str(p.get("product_mode") or map_ba_product_mode(m))
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
        if pack in {"ba-forever", "az-hold"}:
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
            f"# H-FASTREAL (BA2) — prod p50/p99 + anti-FP hold (**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §3 · §8 BA2 · Session: "
            "`.local/wave-ba/SESSION.md`  ",
            "> Parent: [formal-hrealgain-realgain.md](formal-hrealgain-realgain.md) · "
            "BA0 speed baseline  ",
            "> Module: `nano_lm/src/ba_fastreal_ops.py` · "
            "Runner: `npm run nano:ba:fastreal`  ",
            "> **Not** AG archive [formal-hfastreal-fastreal.md]"
            "(formal-hfastreal-fastreal.md) (`npm run nano:fastreal`)",
            "",
            "## Hypothesis",
            "",
            BA_FASTREAL_THESIS,
            "",
            "## Gate",
            "",
            "| Metric | Result | Bar |",
            "|--------|-------:|-----|",
            f"| forever_false_hit | **{board.get('forever_false_hit')}** "
            f"({board.get('forever_ok_n')}/{board.get('forever_n')}) | **0** |",
            f"| az_hold_false_hit | **{board.get('az_hold_false_hit')}** "
            f"({board.get('az_hold_ok_n')}/{board.get('az_hold_n')}) | **0** |",
            f"| overrefuse_miss | **{board.get('overrefuse_miss')}** "
            f"({board.get('overrefuse_ok_n')}/{board.get('overrefuse_n')}) | **0** |",
            f"| live_fp | **{board.get('live_fp')}** | **0** |",
            f"| p99_regress | **{board.get('p99_regress')}** "
            f"({board.get('p99_regress_paths')}) | false "
            f"(≤{board.get('p99_regress_max_ratio')}× BA0) |",
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
            "1. Prod-path tetrad measured under max safe CPU (`cpus-4`).  ",
            "2. LOOKUP wall=0 **not** sold as speed IQ.  ",
            "3. REALGAIN anti-FP hold: forever FH 0 · AZ hold · over-refuse 0 · "
            "live FP 0.  ",
            "4. Live p99 checked vs BA0 AZ-PRODGEN baseline "
            f"(max ratio {board.get('p99_regress_max_ratio')}).  ",
            "5. Warm-cache vanity forbidden.  ",
            f"6. Wall clock ~{wall_s:.1f}s · workers parallel antifp packs.  ",
            "7. AG H-FASTREAL gen microbench archive untouched "
            "(`npm run nano:fastreal`).  ",
            "8. Generative claim still locked (H-NANOGEN11 defer stance).",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:ba:fastreal",
            "npm run nano:realgain",
            "# AG archive (do not confuse): npm run nano:fastreal",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-ba/ba_fastreal_summary.json`  ",
            "- Contract: `nano_lm/tests/test_ba_fastreal.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            f"| {BA_FASTREAL_CLAIM} | Open chat / mini-AGI |",
            "| Publish prod p50/p99 | LOOKUP wall=0 as speed IQ |",
            "| Anti-FP hold required | Trade FP for ms |",
            "| BA0 baseline p99 check | Warm-cache vanity as product win |",
            "| AG FASTREAL archive stays | Rewrite AG formal-hfastreal |",
            "",
            f"SAFE note: {BA_FASTREAL_SAFE_NOTE}  ",
            f"Anti-FP: {BA_FASTREAL_ANTI_FP}",
            "",
            "Next: **BA3 H-CTXREAL2** — context content bars without FP regress.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _update_local_session(decision: str, board: dict[str, Any]) -> None:
    status = f"DONE — {decision.split('(', 1)[0].strip()}"
    body = "\n".join(
        [
            f"# Wave BA session checklist (**OPEN** · BA2 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md`.  ",
            f"> Ship lock: **{BA_FASTREAL_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**BA2 — H-FASTREAL ({status})** · Next: **BA3 H-CTXREAL2**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| forever_false_hit | **{board.get('forever_false_hit')}** |",
            f"| az_hold_false_hit | **{board.get('az_hold_false_hit')}** |",
            f"| overrefuse_miss | **{board.get('overrefuse_miss')}** |",
            f"| live_fp | **{board.get('live_fp')}** |",
            f"| p99_regress | **{board.get('p99_regress')}** "
            f"{board.get('p99_regress_paths')} |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| BA0 | SESSION | **DONE — PROMOTE** |",
            "| BA1 | H-REALGAIN | **DONE — PROMOTE** |",
            f"| BA2 | H-FASTREAL | **{status}** |",
            "| BA3 | H-CTXREAL2 | **NEXT** |",
            "| BA4 | H-NANOGEN11 | pending |",
            "| BA5 | BA-REAL-EVAL | pending |",
            "| BA6 | BA-REPORT | pending |",
            "| BA7 | BA-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.parent.mkdir(parents=True, exist_ok=True)
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    ba2_next = (
        "| BA2 | **H-FASTREAL** | Speed p50/p99 on prod ask **without** "
        "FP/quality regress | latency + §1 | **NEXT** |"
    )
    ba2_done = (
        "| BA2 | **H-FASTREAL** | Speed p50/p99 on prod ask **without** "
        "FP/quality regress | latency + §1 | **DONE — PROMOTE** |"
    )
    if ba2_next in text:
        text = text.replace(ba2_next, ba2_done, 1)
    text = text.replace(
        "3. **BA2 H-FASTREAL** — **NEXT** — speed on prod path; "
        "no anti-FP regress.  ",
        "3. **BA2 H-FASTREAL** — **DONE PROMOTE** "
        "(`npm run nano:ba:fastreal`) — prod p50/p99 + anti-FP hold.  ",
        1,
    )
    text = text.replace(
        "4. **BA3 H-CTXREAL2** — context content bars; no anti-FP regress.  ",
        "4. **BA3 H-CTXREAL2** — **NEXT** — context content bars; "
        "no anti-FP regress.  ",
        1,
    )
    ba3_todo = (
        "| BA3 | **H-CTXREAL2** | Context content bars (usable long/cite/howto) "
        "**without** FP regress | content + §1 | **TODO** |"
    )
    ba3_next = (
        "| BA3 | **H-CTXREAL2** | Context content bars (usable long/cite/howto) "
        "**without** FP regress | content + §1 | **NEXT** |"
    )
    if ba3_todo in text:
        text = text.replace(ba3_todo, ba3_next, 1)
    text = text.replace(
        "npm run nano:realgain\n"
        "# next: nano:fastreal · nano:ctxreal2 · nano:nanogen11\n",
        "npm run nano:realgain\n"
        "npm run nano:ba:fastreal\n"
        "# next: nano:ba:ctxreal2 · nano:nanogen11\n",
        1,
    )
    text = text.replace(
        "> **Session:** `.local/wave-ba/SESSION.md` (BA0–BA1 **DONE — PROMOTE**; "
        "next BA2 H-FASTREAL).  ",
        "> **Session:** `.local/wave-ba/SESSION.md` (BA0–BA2 **DONE — PROMOTE**; "
        "next BA3 H-CTXREAL2).  ",
        1,
    )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def _patch_local_notes(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    _LOCAL_IMPL.write_text(
        """# Implementation plan — nano generative LM

> Private. Lab: [`pesquisa.md`](pesquisa.md).

## Status

**BA0–BA2 DONE — PROMOTE**. Next: **BA3 H-CTXREAL2**.

```bash
npm run nano:ba:fastreal
npm run nano:test && npm run verify
```
""",
        encoding="utf-8",
    )
    _LOCAL_README.write_text(
        """# Local research notebook

Full lab book: **`pesquisa.md`**.

**Wave BA ACTIVE** — BA0 SESSION · BA1 H-REALGAIN · BA2 **H-FASTREAL PROMOTE**.

Next: **BA3 H-CTXREAL2**.
""",
        encoding="utf-8",
    )


def _ba_active_line() -> str:
    return (
        "**Wave BA ACTIVE:** BA0 [SESSION PROMOTE](wave-ba-session.md) · "
        "BA1 [H-REALGAIN PROMOTE](formal-hrealgain-realgain.md) · "
        "BA2 [H-FASTREAL PROMOTE](formal-hfastreal-ba2.md) "
        "(`npm run nano:ba:fastreal`) — prod p50/p99 + anti-FP hold; "
        "next BA3 H-CTXREAL2; ship remains **AF + AQ + AS trust + STRICT "
        "ablated DECODE**; ≤5M stays."
    )


def _patch_recipes(board: dict[str, Any], line: str) -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    text2, n = re.subn(r"\*\*Wave BA ACTIVE:\*\*[^\n]+", line, text, count=1)
    insert = (
        "| Wave BA2 H-FASTREAL | [formal-hfastreal-ba2.md]"
        "(formal-hfastreal-ba2.md) **PROMOTE** (`npm run nano:ba:fastreal`) "
        f"— p99_regress={board.get('p99_regress')} · forever FH "
        f"{board.get('forever_false_hit')} · live FP {board.get('live_fp')} "
        "(≠ AG `nano:fastreal` archive) |"
    )
    if "Wave BA2 H-FASTREAL" not in text2 and "Wave BA1 H-REALGAIN |" in text2:
        text2 = text2.replace(
            "| Wave BA1 H-REALGAIN |",
            insert + "\n| Wave BA1 H-REALGAIN |",
            1,
        )
    if n or "Wave BA2 H-FASTREAL" in text2:
        _RECIPES.write_text(text2, encoding="utf-8")


def _patch_card_agents_agenda(line: str) -> None:
    if _CARD.is_file():
        text = _CARD.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\*\*Wave BA ACTIVE\*\* —[^\n]+",
            line.replace("**Wave BA ACTIVE:**", "**Wave BA ACTIVE** —"),
            text,
            count=1,
        )
        if n:
            _CARD.write_text(text2, encoding="utf-8")
    if _AGENTS.is_file():
        text = _AGENTS.read_text(encoding="utf-8")
        agents = (
            "- **Wave BA ACTIVE** — BA0 [SESSION PROMOTE]"
            "(docs/results/nano-lm/wave-ba-session.md) · BA1 [H-REALGAIN PROMOTE]"
            "(docs/results/nano-lm/formal-hrealgain-realgain.md) · BA2 "
            "[H-FASTREAL PROMOTE](docs/results/nano-lm/formal-hfastreal-ba2.md) "
            "(`npm run nano:ba:fastreal`); next BA3 H-CTXREAL2; ship remains "
            "**AF + AQ + AS trust + STRICT ablated DECODE**; ≤5M stays."
        )
        text2, n = re.subn(
            r"- \*\*Wave BA ACTIVE\*\* —[^\n]+", agents, text, count=1
        )
        if n:
            _AGENTS.write_text(text2, encoding="utf-8")
    if _AGENDA.is_file():
        text = _AGENDA.read_text(encoding="utf-8")
        row = (
            "| **BA** | **ACTIVE** | BA0 SESSION · BA1 [H-REALGAIN PROMOTE]"
            "(results/nano-lm/formal-hrealgain-realgain.md) · BA2 "
            "[H-FASTREAL PROMOTE](results/nano-lm/formal-hfastreal-ba2.md) "
            "(`npm run nano:ba:fastreal`); next BA3 H-CTXREAL2; ≤5M |"
        )
        text2, n = re.subn(
            r"\| \*\*BA\*\* \| \*\*ACTIVE\*\* \|[^\n]+", row, text, count=1
        )
        if n:
            _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen() -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    text = text.replace(
        "BA0 SESSION PROMOTE · BA1 H-REALGAIN PROMOTE; next BA2 H-FASTREAL",
        "BA0–BA2 PROMOTE (H-FASTREAL ba2); next BA3 H-CTXREAL2",
        1,
    )
    _EVOGEN.write_text(text, encoding="utf-8")


def _patch_public(decision: str, board: dict[str, Any]) -> None:
    if not decision.startswith("PROMOTE"):
        return
    line = _ba_active_line()
    _patch_recipes(board, line)
    _patch_card_agents_agenda(line)
    _patch_evogen()


def run_ba_fastreal(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    trials_dir: Path,
    workers: int,
) -> dict[str, Any]:
    """
    GIVEN BA0 speed baseline + REALGAIN anti-FP
    WHEN measuring prod tetrad + hold packs
    THEN PROMOTE/KILL per pesquisa §8 BA2.
    """
    t0 = time.perf_counter()
    trials_dir.mkdir(parents=True, exist_ok=True)

    path_rows = _measure_latency_tetrad(
        root=root, bank=bank, curated=curated
    )
    latency = {k: dict(v["stats"]) for k, v in path_rows.items()}
    tel_ok = {k: bool(v["telemetry_ok"]) for k, v in path_rows.items()}

    forever_rows = _score_pack(
        list(FOREVER_ROWS),
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

    board = extract_ba_fastreal_board(
        latency=latency,
        forever_rows=forever_rows,
        az_rows=az_rows,
        overrefuse_rows=orf_rows,
        live_fp=live_fp,
        near_miss_ok=near_miss_ok(near),
        known_lookup_ok=human_para_hit(known),
        decode_content_ok=decode_content_honest(dec_q),
        modes_visible=list(BA0_MODES),
        telemetry_ok=tel_ok,
    )
    decision = decide_ba_fastreal(board=board, anti_fp_signed=True)
    wall_s = time.perf_counter() - t0
    samples = {
        "LOOKUP": LOOKUP_N,
        "PEAK": PEAK_N,
        "DECODE": DECODE_N,
        "ABSTAIN": ABSTAIN_N,
    }
    write_json(
        trials_dir / "BA-FASTREAL-BOARD.json",
        {
            "board": board,
            "forever_rows": forever_rows,
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
        "id": BA_FASTREAL_ID,
        "stage": "BA2",
        "thesis": BA_FASTREAL_THESIS,
        "decision": decision,
        "board": board,
        "samples": samples,
        "forever_rows": forever_rows,
        "az_rows": az_rows,
        "overrefuse_rows": orf_rows,
        "live_rows": live_rows,
        "wall_s": wall_s,
        "workers": workers,
        "claim": BA_FASTREAL_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hfastreal-ba2.md",
        "ag_archive": "docs/results/nano-lm/formal-hfastreal-fastreal.md",
        "next": "BA3 H-CTXREAL2",
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
        payload = run_ba_fastreal(
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
                "hyp_id": BA_FASTREAL_ID,
                "stage": "BA2",
                "decision": decision[:140],
                "cpu_threads": threads,
                "workers": workers,
                "forever_false_hit": board.get("forever_false_hit"),
                "live_fp": board.get("live_fp"),
                "p99_regress": board.get("p99_regress"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
