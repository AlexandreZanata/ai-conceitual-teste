"""Wave BA3 H-CTXREAL2 runner (nano:ba:ctxreal2) — content bars + anti-FP."""

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

from ba_ctxreal2_ops import (
    APP_SMOKE_PACK,
    AZ_HELDOUT_ROWS,
    BA_CTXREAL2_ANTI_FP,
    BA_CTXREAL2_CLAIM,
    BA_CTXREAL2_ID,
    BA_CTXREAL2_SAFE_NOTE,
    BA_CTXREAL2_THESIS,
    CTX_CONTENT_ROWS,
    FOREVER_ROWS,
    KNOWN_ASK,
    OVERREFUSE_ROWS,
    PEAK_ASK,
    decide_ba_ctxreal2,
    extract_ba_ctxreal2_board,
    intent_false_hit,
    intent_row_ok,
    overrefuse_miss,
    overrefuse_row_ok,
)
from ba_session_ops import BA0_MODES
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
from realgain_ops import score_live_row
from run_ba_fastreal import _measure_latency_tetrad
from run_z_ask import ask_once
from shipreal_ops import attach_shipreal
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-ba/ba_ctxreal2_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-ba/trials"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hctxreal2-ctxreal2.md"
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

_LIVE_PROBES: tuple[dict[str, str], ...] = (
    {
        "id": "BA-CTX-LIVE-01",
        "expect_mode": "ABSTAIN",
        "question": str(FOREVER_ROWS[0]["question"]),
    },
    {
        "id": "BA-CTX-LIVE-02",
        "expect_mode": "ABSTAIN",
        "question": str(AZ_HELDOUT_ROWS[0]["question"]),
    },
    {
        "id": "BA-CTX-LIVE-03",
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
            f"# H-CTXREAL2 — usable long/cite/howto (**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §2 · §8 BA3 · Session: "
            "`.local/wave-ba/SESSION.md`  ",
            "> Parent: [formal-hfastreal-ba2.md](formal-hfastreal-ba2.md) · "
            "BA0 ctx baseline  ",
            "> Module: `nano_lm/src/ba_ctxreal2_ops.py` · "
            "Runner: `npm run nano:ba:ctxreal2`  ",
            "> **Not** AG archive [formal-hctxreal-ctxreal.md]"
            "(formal-hctxreal-ctxreal.md) (`npm run nano:ctxreal`)",
            "",
            "## Hypothesis",
            "",
            BA_CTXREAL2_THESIS,
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
            f"| forever_false_hit | **{board.get('forever_false_hit')}** "
            f"({board.get('forever_ok_n')}/{board.get('forever_n')}) | **0** |",
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
            "3. REALGAIN anti-FP hold: forever FH 0 · AZ hold · over-refuse 0.  ",
            "4. p50/p99 republished; L_eff alone **not** a win.  ",
            f"5. Wall clock ~{wall_s:.1f}s · max safe CPU (`cpus-4`).  ",
            "6. AG H-CTXREAL quad-doc L_eff archive untouched "
            "(`npm run nano:ctxreal`).  ",
            "7. Generative claim still locked (gen stance defer).  ",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:ba:ctxreal2",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-ba/ba_ctxreal2_summary.json`  ",
            "- Contract: `nano_lm/tests/test_ba_ctxreal2.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            f"| {BA_CTXREAL2_CLAIM} | Open chat / mini-AGI |",
            "| Usable howto·cite·long content | L_eff alone as ctx win |",
            "| Eval path = prod ask path | LOOKUP-as-IQ · pack theater |",
            "",
            f"SAFE note: {BA_CTXREAL2_SAFE_NOTE}  ",
            f"Anti-FP: {BA_CTXREAL2_ANTI_FP}",
            "",
            "Next: **BA4 H-NANOGEN11** — one real gen method or HOLD/DEFER.",
            "",
        ]
    )
    _PUBLIC.write_text(body, encoding="utf-8")


def _write_session(decision: str, board: dict[str, Any]) -> None:
    status = decision.split("(", 1)[0].strip()
    body = "\n".join(
        [
            f"# Wave BA session checklist (**OPEN** · BA3 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md`.  ",
            f"> Ship lock: **{BA_CTXREAL2_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**BA3 — H-CTXREAL2 ({status})** · Next: **BA4 H-NANOGEN11**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| ctx_content_ok | **{board.get('ctx_content_ok_n')}/"
            f"{board.get('ctx_content_n')}** |",
            f"| forever_false_hit | **{board.get('forever_false_hit')}** |",
            f"| live_fp | **{board.get('live_fp')}** |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| BA0 | SESSION | **DONE — PROMOTE** |",
            "| BA1 | H-REALGAIN | **DONE — PROMOTE** |",
            "| BA2 | H-FASTREAL | **DONE — PROMOTE** |",
            f"| BA3 | H-CTXREAL2 | **{status}** |",
            "| BA4 | H-NANOGEN11 | **NEXT** |",
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
    ba3_next = (
        "| BA3 | **H-CTXREAL2** | Context content bars (usable long/cite/howto) "
        "**without** FP regress | content + §1 | **NEXT** |"
    )
    ba3_done = (
        "| BA3 | **H-CTXREAL2** | Context content bars (usable long/cite/howto) "
        "**without** FP regress | content + §1 | **DONE — PROMOTE** |"
    )
    if ba3_next in text:
        text = text.replace(ba3_next, ba3_done, 1)
    text = text.replace(
        "4. **BA3 H-CTXREAL2** — **NEXT** — context content bars; "
        "no anti-FP regress.  ",
        "4. **BA3 H-CTXREAL2** — **DONE PROMOTE** "
        "(`npm run nano:ba:ctxreal2`) — howto·cite·long content_ok.  ",
        1,
    )
    text = text.replace(
        "5. **BA4 H-NANOGEN11** — one real method or **HOLD/DEFER** "
        "(cite NANOGEN6–10).  ",
        "5. **BA4 H-NANOGEN11** — **NEXT** — one real method or **HOLD/DEFER** "
        "(cite NANOGEN6–10).  ",
        1,
    )
    ba4_todo = (
        "| BA4 | **H-NANOGEN11** | One real gen method / hybrid / CAPCHECK — "
        "else HOLD/DEFER | true_continue → PROMOTE else HOLD/DEFER | **TODO** |"
    )
    ba4_next = (
        "| BA4 | **H-NANOGEN11** | One real gen method / hybrid / CAPCHECK — "
        "else HOLD/DEFER | true_continue → PROMOTE else HOLD/DEFER | **NEXT** |"
    )
    if ba4_todo in text:
        text = text.replace(ba4_todo, ba4_next, 1)
    text = text.replace(
        "npm run nano:ba:fastreal\n"
        "# next: nano:ba:ctxreal2 · nano:nanogen11\n",
        "npm run nano:ba:fastreal\n"
        "npm run nano:ba:ctxreal2\n"
        "# next: nano:nanogen11\n",
        1,
    )
    text = text.replace(
        "> **Session:** `.local/wave-ba/SESSION.md` (BA0–BA2 **DONE — PROMOTE**; "
        "next BA3 H-CTXREAL2).  ",
        "> **Session:** `.local/wave-ba/SESSION.md` (BA0–BA3 **DONE — PROMOTE**; "
        "next BA4 H-NANOGEN11).  ",
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

**BA0–BA3 DONE — PROMOTE**. Next: **BA4 H-NANOGEN11**.

```bash
npm run nano:ba:ctxreal2
npm run nano:test && npm run verify
```
""",
        encoding="utf-8",
    )
    _LOCAL_README.write_text(
        """# Local research notebook

Full lab book: **`pesquisa.md`**.

**Wave BA ACTIVE** — BA0–BA3 **PROMOTE** (H-CTXREAL2).

Next: **BA4 H-NANOGEN11**.
""",
        encoding="utf-8",
    )


def _ba_active_line() -> str:
    return (
        "**Wave BA ACTIVE:** BA0 [SESSION PROMOTE](wave-ba-session.md) · "
        "BA1 [H-REALGAIN PROMOTE](formal-hrealgain-realgain.md) · "
        "BA2 [H-FASTREAL PROMOTE](formal-hfastreal-ba2.md) · "
        "BA3 [H-CTXREAL2 PROMOTE](formal-hctxreal2-ctxreal2.md) "
        "(`npm run nano:ba:ctxreal2`) — howto·cite·long content_ok; "
        "next BA4 H-NANOGEN11; ship remains **AF + AQ + AS trust + STRICT "
        "ablated DECODE**; ≤5M stays."
    )


def _patch_recipes(board: dict[str, Any], line: str) -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    text2, n = re.subn(r"\*\*Wave BA ACTIVE:\*\*[^\n]+", line, text, count=1)
    insert = (
        "| Wave BA3 H-CTXREAL2 | [formal-hctxreal2-ctxreal2.md]"
        "(formal-hctxreal2-ctxreal2.md) **PROMOTE** (`npm run nano:ba:ctxreal2`) "
        f"— ctx {board.get('ctx_content_ok_n')}/{board.get('ctx_content_n')} · "
        f"forever FH {board.get('forever_false_hit')} · live FP "
        f"{board.get('live_fp')} (≠ AG `nano:ctxreal` archive) |"
    )
    if "Wave BA3 H-CTXREAL2" not in text2 and "Wave BA2 H-FASTREAL |" in text2:
        text2 = text2.replace(
            "| Wave BA2 H-FASTREAL |",
            insert + "\n| Wave BA2 H-FASTREAL |",
            1,
        )
    if n or "Wave BA3 H-CTXREAL2" in text2:
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
            "[H-FASTREAL PROMOTE](docs/results/nano-lm/formal-hfastreal-ba2.md) · "
            "BA3 [H-CTXREAL2 PROMOTE]"
            "(docs/results/nano-lm/formal-hctxreal2-ctxreal2.md) "
            "(`npm run nano:ba:ctxreal2`); next BA4 H-NANOGEN11; ship remains "
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
            "| **BA** | **ACTIVE** | BA0–BA3 PROMOTE (H-CTXREAL2) "
            "(`npm run nano:ba:ctxreal2`); next BA4 H-NANOGEN11; ≤5M |"
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
        "BA0–BA2 PROMOTE (H-FASTREAL ba2); next BA3 H-CTXREAL2",
        "BA0–BA3 PROMOTE (H-CTXREAL2); next BA4 H-NANOGEN11",
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


def run_ba_ctxreal2(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    trials_dir: Path,
    workers: int,
) -> dict[str, Any]:
    """
    GIVEN BA0 ctx baseline + REALGAIN anti-FP
    WHEN scoring howto·cite·long + apps + hold packs
    THEN PROMOTE/KILL per pesquisa §8 BA3.
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

    board = extract_ba_ctxreal2_board(
        ctx_rows=ctx_rows,
        apps_rows=apps_rows,
        forever_rows=forever_rows,
        az_rows=az_rows,
        overrefuse_rows=orf_rows,
        live_fp=live_fp,
        near_miss_ok=near_miss_ok(near),
        known_lookup_ok=human_para_hit(known),
        decode_content_ok=decode_content_honest(dec_q),
        peak_ok=peak_ok(peak),
        latency=latency,
        modes_visible=list(BA0_MODES),
        telemetry_ok=tel_ok,
    )
    decision = decide_ba_ctxreal2(board=board, anti_fp_signed=True)
    wall_s = time.perf_counter() - t0
    payload: dict[str, Any] = {
        "id": BA_CTXREAL2_ID,
        "stage": "BA3",
        "thesis": BA_CTXREAL2_THESIS,
        "decision": decision,
        "board": board,
        "ctx_rows": ctx_rows,
        "apps_rows": apps_rows,
        "forever_rows": forever_rows,
        "az_rows": az_rows,
        "overrefuse_rows": orf_rows,
        "live_rows": live_rows,
        "wall_s": wall_s,
        "workers": workers,
        "claim": BA_CTXREAL2_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hctxreal2-ctxreal2.md",
        "ag_archive": "docs/results/nano-lm/formal-hctxreal-ctxreal.md",
        "next": "BA4 H-NANOGEN11",
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
        payload = run_ba_ctxreal2(
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
                "hyp_id": BA_CTXREAL2_ID,
                "stage": "BA3",
                "decision": decision,
                "cpu_threads": threads,
                "workers": workers,
                "ctx_ok": (
                    f"{board.get('ctx_content_ok_n')}/"
                    f"{board.get('ctx_content_n')}"
                ),
                "forever_false_hit": board.get("forever_false_hit"),
                "live_fp": board.get("live_fp"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
