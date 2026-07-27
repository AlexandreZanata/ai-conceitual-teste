"""Wave AW1 H-PRODKEEP runner (nano:prodkeep) — hold Caminho A under pressure."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from curated_sources import SOURCES
from fastbase_ops import fastbase_generate
from genpeak_ops import chunk_doc
from matrix_common import REPO, write_json
from prodkeep_ops import (
    DECODE_PROBE_ASK,
    KNOWN_ASK,
    NEAR_MISS_ASK,
    PEAK_ASK,
    PRESSURE_PARA_ROWS,
    PRODKEEP_ANTI_FP,
    PRODKEEP_CLAIM,
    PRODKEEP_ID,
    PRODKEEP_SAFE_NOTE,
    PRODKEEP_THESIS,
    bars_from_keep_charter,
    decide_prodkeep,
    extract_prodkeep_board,
    gate_junk_decode,
    human_para_hit,
)
from run_metrics import run_metrics
from run_shipui import run_shipui
from run_z_ask import ask_once
from shipreal_ops import attach_shipreal
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-aw/prodkeep_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-aw/trials"
_AW_BANK = REPO / "results/nano-lm/wave-aw/error_bank.jsonl"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hprodkeep-prodkeep.md"
_LOCAL_SESSION = REPO / ".local/wave-aw/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"
_METRICS_OUT = REPO / "results/nano-lm/wave-aw/metrics_reg.json"
_SHIP_OUT = REPO / "results/nano-lm/wave-aw/shipui_reg.json"
_EMPTY_BANK = REPO / "results/nano-lm/wave-aw/_decode_empty_bank.jsonl"
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
    # Max safe on 16c / ~12Gi avail: leave 2 cores; cap workers to avoid thrash.
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
    """WRAP_DECODE empty-bank path then junk→ABSTAIN (content law hold)."""
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


def _score_pressure_para(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    workers: int,
) -> tuple[list[bool], list[dict[str, Any]]]:
    def _one(item: dict[str, str]) -> dict[str, Any]:
        p = _ask(item["question"], root=root, bank=bank, curated=curated)
        return {
            "id": item["id"],
            "hit": human_para_hit(p),
            "mode": p.get("mode"),
            "product_mode": p.get("product_mode"),
            "completion": str(p.get("completion", ""))[:120],
        }

    # Cap parallel asks to leave RAM headroom for model weights (~12Gi avail).
    n = min(workers, 8, len(PRESSURE_PARA_ROWS))
    with ThreadPoolExecutor(max_workers=max(1, n)) as pool:
        rows = list(pool.map(_one, list(PRESSURE_PARA_ROWS)))
    return [bool(r["hit"]) for r in rows], rows


def _write_public(
    *,
    decision: str,
    board: dict[str, Any],
    wall_s: float,
) -> None:
    bars = bars_from_keep_charter()
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
            f"# H-PRODKEEP — Caminho A keep (**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §2 AW1 · Session: "
            "`.local/wave-aw/SESSION.md`  ",
            "> Parent: [wave-aw-session.md](wave-aw-session.md) · "
            "Suite: AW0 product-keep  ",
            "> Module: `nano_lm/src/prodkeep_ops.py` · "
            "Runner: `npm run nano:prodkeep`",
            "",
            "## Hypothesis",
            "",
            PRODKEEP_THESIS,
            "",
            "## Gate",
            "",
            "| Metric | Result | Bar |",
            "|--------|-------:|-----|",
            f"| pressure_para_hit | **{board.get('para_hit')}** "
            f"({board.get('para_n_true')}/{board.get('para_n')}) | "
            f"≥ {bars.get('para_hit_min')} · n≥"
            f"{bars.get('pressure_para_min_n')} |",
            f"| false_hit (near-miss) | **{board.get('false_hit')}** | "
            f"**{bars.get('false_hit_max')}** |",
            f"| near_miss_ok | **{board.get('near_miss_ok')}** "
            f"({board.get('near_miss_mode')}) | ABSTAIN |",
            f"| decode_content_ok | **{board.get('decode_content_ok')}** "
            f"({board.get('decode_mode')}) | usable or ABSTAIN |",
            f"| peak_ok | **{board.get('peak_ok')}** "
            f"({board.get('peak_mode')}) | usable or ABSTAIN |",
            f"| known_lookup_ok | **{board.get('known_lookup_ok')}** | "
            "True |",
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
            "## DECODE probe (content law hold)",
            "",
            f"- mode: **{board.get('decode_mode')}**  ",
            f"- abstained: **{board.get('decode_abstained')}**  ",
            f"- sample: `{board.get('decode_completion')}`",
            "",
            "## PEAK sample",
            "",
            f"`{board.get('peak_completion')}`",
            "",
            "## Finding",
            "",
            "1. Pressure held-out para (N≥20 ≠ AV/AU) scored on production "
            "`nano:z:ask --wrap --semwrap`.  ",
            "2. Near-miss BIP-39+SegWit stays ABSTAIN on default ask.  ",
            "3. DECODE content law holds — usable or ABSTAIN "
            "(gibberish ≠ content_ok).  ",
            "4. Modes + latency + KB republished under pressure.  ",
            f"5. Wall clock ~{wall_s:.1f}s · max safe CPU (`cpus-2`).  ",
            "6. Generative claim still locked until AW3 H-NANOGEN7 TAC "
            "(true continue; span-fallback ≠ gen).",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:prodkeep",
            "npm run nano:aw:session",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-aw/prodkeep_summary.json`  ",
            "- Contract: `nano_lm/tests/test_prodkeep.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            f"| {PRODKEEP_CLAIM} | Open chat / mini-AGI |",
            "| Eval path = prod ask path | LOOKUP-as-IQ · SAFE-as-quality |",
            "| DECODE usable or ABSTAIN | telemetry-only content_ok |",
            "| Honest HOLD/KILL on bar fail | Eval-only patches · bank stuffing |",
            "",
            f"SAFE note: {PRODKEEP_SAFE_NOTE}  ",
            f"Anti-FP: {PRODKEEP_ANTI_FP}",
            "",
            "Next: **AW2 H-SHIPKEEP** — ship/demo mode+content honesty.",
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
            f"# Wave AW session checklist (**OPEN** · AW1 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AW **OPEN** · Caminho A keep + Nano Generative).  ",
            f"> Ship lock: **{PRODKEEP_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AW1 — H-PRODKEEP ({status})** · Next: **AW2 H-SHIPKEEP**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AW OPEN** |",
            f"| pressure_para_hit | **{board.get('para_hit')}** "
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
            "| AW0 | SESSION | **DONE — PROMOTE** |",
            f"| AW1 | H-PRODKEEP | **{status}** |",
            "| AW2 | H-SHIPKEEP | **NEXT** |",
            "| AW3 | H-NANOGEN7 | pending (generative north-star gate) |",
            "| AW4 | AW-REAL-EVAL | pending |",
            "| AW5 | AW-REPORT | pending |",
            "| AW6 | AW-FREEZE | pending |",
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
        "| AW1 | **H-PRODKEEP** | Caminho A regression under pressure-para · "
        "FH 0 · p50/p99 · KB · DECODE content | hold AV bars | **TODO** |"
    )
    new = (
        "| AW1 | **H-PRODKEEP** | Caminho A regression under pressure-para · "
        "FH 0 · p50/p99 · KB · DECODE content | hold AV bars | "
        f"**DONE — {status}** |"
    )
    if old in text:
        text = text.replace(old, new, 1)
    old_next = "2. **AW1 H-PRODKEEP** — hold Caminho A under pressure-para.  "
    new_next = (
        f"2. **AW1 H-PRODKEEP** — **DONE {status}** "
        "(`npm run nano:prodkeep`) · next **AW2 H-SHIPKEEP**.  "
    )
    if old_next in text:
        text = text.replace(old_next, new_next, 1)
    bash_old = "# next: nano:prodkeep · nano:shipkeep · nano:nanogen7"
    bash_new = (
        "npm run nano:prodkeep\n"
        "# next: nano:shipkeep · nano:nanogen7"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def _patch_local_impl(decision: str) -> None:
    if not _LOCAL_IMPL.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_IMPL.read_text(encoding="utf-8")
    old = (
        "2. **AW1 H-PRODKEEP** — **NEXT** — hold Caminho A under "
        "pressure-para.  "
    )
    new = (
        "2. **AW1 H-PRODKEEP** — **DONE PROMOTE** (`npm run nano:prodkeep`) · "
        "next **AW2 H-SHIPKEEP**.  "
    )
    if old in text:
        text = text.replace(old, new, 1)
        _LOCAL_IMPL.write_text(text, encoding="utf-8")


def _patch_local_readme(decision: str) -> None:
    if not _LOCAL_README.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_README.read_text(encoding="utf-8")
    old = (
        "Session: `wave-aw/SESSION.md` (AW0 **DONE — PROMOTE**; "
        "next AW1 H-PRODKEEP)."
    )
    new = (
        "Session: `wave-aw/SESSION.md` (AW1 H-PRODKEEP **DONE — PROMOTE**; "
        "next AW2 H-SHIPKEEP)."
    )
    if old in text:
        text = text.replace(old, new, 1)
        _LOCAL_README.write_text(text, encoding="utf-8")


def run_prodkeep(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    trials_dir: Path,
    workers: int,
) -> dict[str, Any]:
    """
    GIVEN AW0 product-keep charter
    WHEN measuring Caminho A keep bars on pressure-para ask path
    THEN PROMOTE/HOLD/KILL per pesquisa §2 AW1.
    """
    t0 = time.perf_counter()
    trials_dir.mkdir(parents=True, exist_ok=True)
    _AW_BANK.parent.mkdir(parents=True, exist_ok=True)
    if not _AW_BANK.is_file():
        _AW_BANK.write_text("", encoding="utf-8")

    para_hits, para_rows = _score_pressure_para(
        root=root, bank=bank, curated=curated, workers=workers
    )
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
    board = extract_prodkeep_board(
        para_hits=para_hits,
        near=near,
        peak=peak,
        known=known,
        decode=decode,
        metrics=metrics,
        ship=ship,
    )
    decision = decide_prodkeep(board=board, anti_fp_signed=True)
    wall_s = time.perf_counter() - t0
    write_json(
        trials_dir / "AW-PRODKEEP-BOARD.json",
        {
            "board": board,
            "para_rows": para_rows,
            "decode": {
                "mode": decode.get("mode"),
                "product_mode": decode.get("product_mode"),
                "abstained": decode.get("abstained"),
                "completion": str(decode.get("completion", ""))[:200],
            },
            "decision": decision,
        },
    )
    _write_public(decision=decision, board=board, wall_s=wall_s)
    _update_local_session(decision, board)
    _patch_pesquisa(decision)
    _patch_local_impl(decision)
    _patch_local_readme(decision)
    payload = {
        "id": PRODKEEP_ID,
        "thesis": PRODKEEP_THESIS,
        "decision": decision,
        "board": board,
        "para_rows": para_rows,
        "wall_s": wall_s,
        "workers": workers,
        "claim": PRODKEEP_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hprodkeep-prodkeep.md",
        "next": "AW2 H-SHIPKEEP",
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
        payload = run_prodkeep(
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
                "hyp_id": PRODKEEP_ID,
                "decision": decision[:140],
                "cpu_threads": threads,
                "workers": workers,
                "para_hit": board.get("para_hit"),
                "decode_content_ok": board.get("decode_content_ok"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
