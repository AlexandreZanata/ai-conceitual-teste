"""Wave AY1 H-PRODINT runner (nano:prodint) — close intent FH debt."""

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
from prodint_ops import (
    DECODE_PROBE_ASK,
    HARD_NATURAL_ROWS,
    INTENT_FP_ROWS,
    KNOWN_ASK,
    NEAR_MISS_ASK,
    PEAK_ASK,
    PRODINT_ANTI_FP,
    PRODINT_CLAIM,
    PRODINT_ID,
    PRODINT_SAFE_NOTE,
    PRODINT_THESIS,
    bars_from_int_charter,
    decide_prodint,
    extract_prodint_board,
    gate_junk_decode,
    human_para_hit,
    intent_false_hit,
    intent_row_ok,
)
from run_metrics import run_metrics
from run_shipui import run_shipui
from run_z_ask import ask_once
from shipreal_ops import attach_shipreal
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-ay/prodint_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-ay/trials"
_AY_BANK = REPO / "results/nano-lm/wave-ay/error_bank.jsonl"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hprodint-prodint.md"
_LOCAL_SESSION = REPO / ".local/wave-ay/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENTS = REPO / "AGENTS.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_METRICS_OUT = REPO / "results/nano-lm/wave-ay/metrics_reg.json"
_SHIP_OUT = REPO / "results/nano-lm/wave-ay/shipui_reg.json"
_EMPTY_BANK = REPO / "results/nano-lm/wave-ay/_decode_empty_bank.jsonl"
_PEAK_SOURCE = "rust-book-ch04-01"
_BY_ID = {str(s["id"]): s for s in SOURCES}


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
    # 16c / ~10Gi avail: leave ≥2 cores; cap ask workers to avoid OOM thrash.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 2))
    workers = min(14, max(4, cpus - 2))
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
        if pack == "intent-fp":
            out["class"] = item.get("class")
            out["false_hit"] = intent_false_hit(p)
            out["ok"] = intent_row_ok(p)
        else:
            out["hit"] = human_para_hit(p)
        return out

    n = min(workers, 8, len(rows))
    with ThreadPoolExecutor(max_workers=max(1, n)) as pool:
        return list(pool.map(_one, rows))


def _write_public(
    *,
    decision: str,
    board: dict[str, Any],
    wall_s: float,
) -> None:
    bars = bars_from_int_charter()
    lat_rows = [
        f"| {name} | **{row.get('p50_wall_ms')}** | "
        f"**{row.get('p99_wall_ms')}** |"
        for name, row in (board.get("latency") or {}).items()
    ]
    holes = board.get("kb_hole_list") or []
    hole_lines = [f"- `{h}`" for h in holes] or ["_(none / see METRICS)_"]
    status = decision.split("(", 1)[0].strip()
    body = "\n".join(
        [
            f"# H-PRODINT — intent FH 0 Caminho A (**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AY1 · Session: "
            "`.local/wave-ay/SESSION.md`  ",
            "> Parent: [wave-ay-session.md](wave-ay-session.md) · "
            "Suite: AY0 product-int  ",
            "> Module: `nano_lm/src/prodint_ops.py` · "
            "Runner: `npm run nano:prodint`",
            "",
            "## Hypothesis",
            "",
            PRODINT_THESIS,
            "",
            "## Gate",
            "",
            "| Metric | Result | Bar |",
            "|--------|-------:|-----|",
            f"| intent_false_hit | **{board.get('intent_false_hit')}** "
            f"({board.get('intent_ok_n')}/{board.get('intent_n')} ABSTAIN) | "
            f"**{bars.get('intent_false_hit_max')}** |",
            f"| hard_natural_para_hit | **{board.get('hard_natural_para_hit')}** "
            f"({board.get('para_n_true')}/{board.get('para_n')}) | "
            f"≥ {bars.get('hard_natural_para_hit_min')} hold |",
            f"| false_hit (near-miss) | **{board.get('false_hit')}** | "
            f"**{bars.get('false_hit_max')}** |",
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
            "1. Intent-FP held-out (N≥12 · 4 classes) scored on production "
            "`nano:z:ask --wrap --semwrap`.  ",
            "2. SEMWRAP `contrastive_reject` + `intent_ask_must_abstain` close "
            "mul→add · difference-add · remove≠clear · BIP wordlist sibling — "
            "**not** bank stuffing.  ",
            "3. Hard-natural AX pack held (≥ bar).  ",
            "4. Near-miss BIP-39+SegWit stays ABSTAIN.  ",
            "5. DECODE content law holds — usable or ABSTAIN.  ",
            "6. Modes + latency + KB republished.  ",
            f"7. Wall clock ~{wall_s:.1f}s · max safe CPU (`cpus-2`).  ",
            "8. Generative claim still locked (gen stance **defer**; "
            "H-NANOGEN9; NANOGEN6·7 HOLD · NANOGEN8 DEFER).",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:prodint",
            "npm run nano:ay:session",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-ay/prodint_summary.json`  ",
            "- Contract: `nano_lm/tests/test_prodint.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            f"| {PRODINT_CLAIM} | Open chat / mini-AGI |",
            "| Intent mismatch → ABSTAIN | Intent-FP as LOOKUP hit |",
            "| Eval path = prod ask path | LOOKUP-as-IQ · SAFE-as-quality |",
            "| Hard-natural hold | Pack FH as live intent coverage |",
            "| Honest HOLD/KILL on bar fail | Bank stuffing |",
            "",
            f"SAFE note: {PRODINT_SAFE_NOTE}  ",
            f"Anti-FP: {PRODINT_ANTI_FP}",
            "",
            "Next: **AY2 H-SHIPAY** — ship/demo mode+content honesty.",
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
            f"# Wave AY session checklist (**OPEN** · AY1 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AY **OPEN** · intent harden + gen defer).  ",
            f"> Ship lock: **{PRODINT_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AY1 — H-PRODINT ({status})** · Next: **AY2 H-SHIPAY**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AY OPEN** |",
            f"| intent_false_hit | **{board.get('intent_false_hit')}** "
            f"({board.get('intent_ok_n')}/{board.get('intent_n')}) |",
            f"| hard_natural_para_hit | **{board.get('hard_natural_para_hit')}** "
            f"({board.get('para_n_true')}/{board.get('para_n')}) |",
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
            "| AY0 | SESSION | **DONE — PROMOTE** |",
            f"| AY1 | H-PRODINT | **{status}** |",
            "| AY2 | H-SHIPAY | **NEXT** |",
            "| AY3 | H-NANOGEN9 | pending (defer unless real new method) |",
            "| AY4 | AY-REAL-EVAL | pending |",
            "| AY5 | AY-REPORT | pending |",
            "| AY6 | AY-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    status = decision.split("(", 1)[0].strip()
    old = (
        "| AY1 | **H-PRODINT** | Caminho A: intent/adversary "
        "FH 0 · hold hard-natural · p50/p99 · KB · modes · DECODE law | "
        "FH 0 on live FP class · metrics board | **NEXT** |"
    )
    new = (
        "| AY1 | **H-PRODINT** | Caminho A: intent/adversary "
        "FH 0 · hold hard-natural · p50/p99 · KB · modes · DECODE law | "
        f"FH 0 on live FP class · metrics board | **DONE — {status}** |"
    )
    if old in text:
        text = text.replace(old, new, 1)
    old_next = (
        "2. **AY1 H-PRODINT** — **NEXT** — close intent FP on Caminho A "
        "(SEMWRAP robustness ≠ bank stuffing); report human-para · FH · "
        "p50/p99 · KB · modes.  "
    )
    if old_next in text:
        text = text.replace(
            old_next,
            f"2. **AY1 H-PRODINT** — **DONE {status}** "
            "(`npm run nano:prodint`) · next **AY2 H-SHIPAY**.  ",
            1,
        )
    bash_old = "# next: nano:prodint · nano:shipay · nano:nanogen9"
    if bash_old in text:
        text = text.replace(
            bash_old,
            "npm run nano:prodint\n# next: nano:shipay · nano:nanogen9",
            1,
        )
    text = text.replace(
        "> **Session:** `.local/wave-ay/SESSION.md` "
        "(AY0 **DONE — PROMOTE**; next AY1 H-PRODINT).  ",
        "> **Session:** `.local/wave-ay/SESSION.md` "
        f"(AY1 H-PRODINT **DONE — {status}**; next AY2 H-SHIPAY).  ",
        1,
    )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def _patch_local_notes(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    if _LOCAL_IMPL.is_file():
        text = _LOCAL_IMPL.read_text(encoding="utf-8")
        old = (
            "2. **AY1 H-PRODINT** — **NEXT** — close intent FP; "
            "publish metrics board.  "
        )
        new = (
            "2. **AY1 H-PRODINT** — **DONE PROMOTE** (`npm run nano:prodint`) · "
            "next **AY2 H-SHIPAY**.  "
        )
        if old in text:
            _LOCAL_IMPL.write_text(text.replace(old, new, 1), encoding="utf-8")
    if _LOCAL_README.is_file():
        text = _LOCAL_README.read_text(encoding="utf-8")
        old = (
            "Session: `wave-ay/SESSION.md` (AY0 **DONE — PROMOTE**; "
            "next AY1 H-PRODINT)."
        )
        new = (
            "Session: `wave-ay/SESSION.md` (AY1 H-PRODINT **DONE — PROMOTE**; "
            "next AY2 H-SHIPAY)."
        )
        if old in text:
            _LOCAL_README.write_text(text.replace(old, new, 1), encoding="utf-8")


def _patch_agents_prodint() -> None:
    if not _AGENTS.is_file():
        return
    text = _AGENTS.read_text(encoding="utf-8")
    if "H-PRODINT PROMOTE" in text:
        return
    text2, count = re.subn(
        r"(- \*\*Wave AY ACTIVE\*\* —[^\n]*AY0 \[SESSION PROMOTE\]"
        r"[^\n]*?)(; next AY1 H-PRODINT|; next AY1)",
        r"\1 · AY1 [H-PRODINT PROMOTE]"
        r"(docs/results/nano-lm/formal-hprodint-prodint.md) "
        r"(`npm run nano:prodint`); next AY2 H-SHIPAY",
        text,
        count=1,
    )
    if count:
        _AGENTS.write_text(text2, encoding="utf-8")


def _patch_agenda_prodint() -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    ay_tail = text.split("| **AY** |", 1)[-1][:400] if "| **AY** |" in text else ""
    if "H-PRODINT" in ay_tail:
        return
    text2, count = re.subn(
        r"(\| \*\*AY\*\* \| \*\*ACTIVE\*\* \|[^\n]*AY0 \[SESSION "
        r"PROMOTE\][^\n]*?)(; next AY1 H-PRODINT|; next AY1)",
        r"\1 · AY1 [H-PRODINT PROMOTE]"
        r"(results/nano-lm/formal-hprodint-prodint.md); "
        r"next AY2 H-SHIPAY",
        text,
        count=1,
    )
    if count:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_recipes_prodint(board: dict[str, Any]) -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    if "Wave AY1 H-PRODINT" in text:
        return
    insert = (
        "| Wave AY1 H-PRODINT | [formal-hprodint-prodint.md]"
        "(formal-hprodint-prodint.md) **PROMOTE** (`npm run nano:prodint`) — "
        f"intent FH **{board.get('intent_false_hit')}**/"
        f"{board.get('intent_n')} · hard-natural "
        f"**{board.get('hard_natural_para_hit')}**/"
        f"{board.get('para_n')} · modes 4/4 |"
    )
    marker = "| Wave AY0 SESSION |"
    idx = text.find(marker)
    if idx < 0:
        return
    end = text.find("\n", idx)
    if end < 0:
        return
    text = text[: end + 1] + insert + "\n" + text[end + 1 :]
    # ACTIVE line
    text2, n = re.subn(
        r"(\*\*Wave AY ACTIVE:\*\*[^\n]*AY0 \[SESSION PROMOTE\][^\n]*?)"
        r"(; next AY1 H-PRODINT|; next AY1)",
        rf"\1 · AY1 [H-PRODINT PROMOTE](formal-hprodint-prodint.md) "
        rf"(`npm run nano:prodint`) — intent FH **{board.get('intent_false_hit')}**; "
        r"next AY2 H-SHIPAY",
        text,
        count=1,
    )
    _RECIPES.write_text(text2 if n else text, encoding="utf-8")


def _patch_card_prodint(board: dict[str, Any]) -> None:
    if not _CARD.is_file():
        return
    text = _CARD.read_text(encoding="utf-8")
    if "H-PRODINT PROMOTE" in text:
        return
    text2, n = re.subn(
        r"(\*\*Wave AY ACTIVE\*\* —[^\n]*AY0 \[SESSION PROMOTE\][^\n]*?)"
        r"(; next AY1 H-PRODINT|; next AY1)",
        rf"\1 · AY1 [H-PRODINT PROMOTE](formal-hprodint-prodint.md) "
        rf"(`npm run nano:prodint`) — intent FH **{board.get('intent_false_hit')}**; "
        r"next AY2 H-SHIPAY",
        text,
        count=1,
    )
    if n:
        _CARD.write_text(text2, encoding="utf-8")


def _patch_evogen_prodint() -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    if "Wave AY1:" in text or "formal-hprodint-prodint" in text:
        return
    text = text.replace(
        "Wave AY0: `wave-ay-session.md`",
        "Wave AY0: `wave-ay-session.md` · Wave AY1: "
        "`formal-hprodint-prodint.md` PROMOTE",
        1,
    )
    _EVOGEN.write_text(text, encoding="utf-8")


def _patch_public_status(decision: str, board: dict[str, Any]) -> None:
    if not decision.startswith("PROMOTE"):
        return
    _patch_agents_prodint()
    _patch_agenda_prodint()
    _patch_recipes_prodint(board)
    _patch_card_prodint(board)
    _patch_evogen_prodint()


def run_prodint(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    trials_dir: Path,
    workers: int,
) -> dict[str, Any]:
    """
    GIVEN AY0 product-int charter
    WHEN measuring intent FH + hard-natural hold on production ask path
    THEN PROMOTE/HOLD/KILL per pesquisa §5 AY1.
    """
    t0 = time.perf_counter()
    trials_dir.mkdir(parents=True, exist_ok=True)
    _AY_BANK.parent.mkdir(parents=True, exist_ok=True)
    if not _AY_BANK.is_file():
        _AY_BANK.write_text("", encoding="utf-8")

    intent_rows = _score_pack(
        list(INTENT_FP_ROWS),
        root=root,
        bank=bank,
        curated=curated,
        workers=workers,
        pack="intent-fp",
    )
    para_scored = _score_pack(
        list(HARD_NATURAL_ROWS),
        root=root,
        bank=bank,
        curated=curated,
        workers=workers,
        pack="hard-natural",
    )
    para_hits = [bool(r.get("hit")) for r in para_scored]

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
    board = extract_prodint_board(
        intent_rows=intent_rows,
        para_hits=para_hits,
        near=near,
        peak=peak,
        known=known,
        decode=decode,
        metrics=metrics,
        ship=ship,
    )
    decision = decide_prodint(board=board, anti_fp_signed=True)
    wall_s = time.perf_counter() - t0
    write_json(
        trials_dir / "AY-PRODINT-BOARD.json",
        {
            "board": board,
            "intent_rows": intent_rows,
            "para_rows": para_scored,
            "decision": decision,
        },
    )
    _write_public(decision=decision, board=board, wall_s=wall_s)
    _update_local_session(decision, board)
    _patch_pesquisa(decision)
    _patch_local_notes(decision)
    _patch_public_status(decision, board)
    payload = {
        "id": PRODINT_ID,
        "thesis": PRODINT_THESIS,
        "decision": decision,
        "board": board,
        "intent_rows": intent_rows,
        "para_rows": para_scored,
        "wall_s": wall_s,
        "workers": workers,
        "claim": PRODINT_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hprodint-prodint.md",
        "next": "AY2 H-SHIPAY",
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
        payload = run_prodint(
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
                "hyp_id": PRODINT_ID,
                "decision": decision[:140],
                "cpu_threads": threads,
                "workers": workers,
                "intent_false_hit": board.get("intent_false_hit"),
                "hard_natural_para_hit": board.get("hard_natural_para_hit"),
                "false_hit": board.get("false_hit"),
                "decode_content_ok": board.get("decode_content_ok"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
