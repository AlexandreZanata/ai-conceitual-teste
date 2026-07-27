"""Wave AU1 H-PRODHARD runner (nano:prodhard) — close live-audit debts."""

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
from prodhard_ops import (
    HUMAN_PARA_ROWS,
    KNOWN_ASK,
    NEAR_MISS_ASK,
    PEAK_ASK,
    PRODHARD_ANTI_FP,
    PRODHARD_CLAIM,
    PRODHARD_ID,
    PRODHARD_SAFE_NOTE,
    PRODHARD_THESIS,
    bars_from_debt_suite,
    decide_prodhard,
    extract_prodhard_board,
    human_para_hit,
)
from run_metrics import run_metrics
from run_shipui import run_shipui
from run_z_ask import ask_once
from shipui_ops import attach_shipui
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-au/prodhard_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-au/trials"
_AU_BANK = REPO / "results/nano-lm/wave-au/error_bank.jsonl"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hprodhard-prodhard.md"
_LOCAL_SESSION = REPO / ".local/wave-au/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_METRICS_OUT = REPO / "results/nano-lm/wave-au/metrics_reg.json"
_SHIP_OUT = REPO / "results/nano-lm/wave-au/shipui_reg.json"
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
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 2))
    workers = min(12, max(4, cpus - 2))
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
    return attach_shipui(dict(payload))


def _peak_row(*, curated: Path, question: str) -> dict[str, Any]:
    meta = _BY_ID.get(_PEAK_SOURCE)
    if meta is None:
        raise ValueError(f"unknown source_id: {_PEAK_SOURCE}")
    path = curated / str(meta["path"])
    doc = path.read_text(encoding="utf-8", errors="ignore")
    chunks = chunk_doc(doc, win=400, stride=160)
    payload = fastbase_generate(question=question, chunks=chunks, doc=doc)
    row = attach_shipui(dict(payload))
    row["arm"] = "PEAK"
    row["question"] = question
    return row


def _score_human_para(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    workers: int,
) -> tuple[list[bool], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []

    def _one(item: dict[str, str]) -> dict[str, Any]:
        p = _ask(
            item["question"], root=root, bank=bank, curated=curated
        )
        return {
            "id": item["id"],
            "hit": human_para_hit(p),
            "mode": p.get("mode"),
            "product_mode": p.get("product_mode"),
            "completion": str(p.get("completion", ""))[:120],
        }

    with ThreadPoolExecutor(max_workers=min(workers, 8)) as pool:
        rows = list(pool.map(_one, list(HUMAN_PARA_ROWS)))
    return [bool(r["hit"]) for r in rows], rows


def _write_public(
    *,
    decision: str,
    board: dict[str, Any],
    wall_s: float,
) -> None:
    bars = bars_from_debt_suite()
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
            f"# H-PRODHARD — live-audit close (**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AU1 · Session: "
            "`.local/wave-au/SESSION.md`  ",
            "> Parent: [wave-au-session.md](wave-au-session.md) · "
            "Suite: AU0 product-debt  ",
            "> Module: `nano_lm/src/prodhard_ops.py` · "
            "Runner: `npm run nano:prodhard`",
            "",
            "## Hypothesis",
            "",
            PRODHARD_THESIS,
            "",
            "## Gate",
            "",
            "| Metric | Result | Bar |",
            "|--------|-------:|-----|",
            f"| human_para_hit | **{board.get('para_hit')}** "
            f"({board.get('para_n_true')}/{board.get('para_n')}) | "
            f"≥ {bars.get('para_hit_min')} |",
            f"| false_hit (near-miss) | **{board.get('false_hit')}** | "
            f"**{bars.get('false_hit_max')}** |",
            f"| near_miss_ok | **{board.get('near_miss_ok')}** "
            f"({board.get('near_miss_mode')}) | ABSTAIN |",
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
            "## PEAK sample",
            "",
            f"`{board.get('peak_completion')}`",
            "",
            "## Finding",
            "",
            "1. Near-miss BIP-39+SegWit refuses on **default** "
            "`nano:z:ask --wrap --semwrap` (not eval-only).  ",
            "2. Held-out human para of `add` scored on production SEMWRAP.  ",
            "3. PEAK returns usable ownership span (or ABSTAIN).  ",
            "4. Modes + latency + KB republished.  ",
            f"5. Wall clock ~{wall_s:.1f}s · max safe CPU (`cpus-2`).  ",
            "6. Generative claim still locked until AU3 H-NANOGEN5.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:prodhard",
            "npm run nano:au:session",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-au/prodhard_summary.json`  ",
            "- Contract: `nano_lm/tests/test_prodhard.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            f"| {PRODHARD_CLAIM} | Open chat / mini-AGI |",
            "| Eval path = prod ask path | LOOKUP-as-IQ · SAFE-as-quality |",
            "| Honest HOLD/KILL on bar fail | Eval-only near-miss patch |",
            "",
            f"SAFE note: {PRODHARD_SAFE_NOTE}  ",
            f"Anti-FP: {PRODHARD_ANTI_FP}",
            "",
            "Next: **AU2 H-SHIPREAL** — human ship/demo mode honesty.",
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
            f"# Wave AU session checklist (**OPEN** · AU1 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AU **OPEN**).  ",
            f"> Ship lock: **{PRODHARD_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AU1 — H-PRODHARD ({status})** · Next: **AU2 H-SHIPREAL**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AU OPEN** |",
            f"| para_hit | **{board.get('para_hit')}** |",
            f"| near_miss_ok / FH | **{board.get('near_miss_ok')}** / "
            f"**{board.get('false_hit')}** |",
            f"| peak_ok | **{board.get('peak_ok')}** |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AU0 | SESSION | **DONE — PROMOTE** |",
            f"| AU1 | H-PRODHARD | **{status}** |",
            "| AU2 | H-SHIPREAL | **NEXT** |",
            "| AU3 | H-NANOGEN5 | pending |",
            "| AU4 | AU-REAL-EVAL | pending |",
            "| AU5 | AU-REPORT | pending |",
            "| AU6 | AU-FREEZE | pending |",
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
        "| AU1 | **H-PRODHARD** | Close live-audit debts: near-miss on "
        "default ask · human para held-out · PEAK usable span · metrics "
        "board | FH **0** on ask path · para bar · modes 4/4 · "
        "p50/p99+KB | **TODO** |"
    )
    new = (
        "| AU1 | **H-PRODHARD** | Close live-audit debts: near-miss on "
        "default ask · human para held-out · PEAK usable span · metrics "
        "board | FH **0** on ask path · para bar · modes 4/4 · "
        f"p50/p99+KB | **DONE — {status}** |"
    )
    if old in text:
        text = text.replace(old, new, 1)
    old_next = (
        "2. **AU1 H-PRODHARD** — close near-miss on `nano:z:ask`; "
        "held-out human paraphrase; PEAK usable; publish para · FH · "
        "p50/p99 · KB.  "
    )
    new_next = (
        f"2. **AU1 H-PRODHARD** — **DONE {status}** "
        "(`npm run nano:prodhard`) · next **AU2 H-SHIPREAL**.  "
    )
    if old_next in text:
        text = text.replace(old_next, new_next, 1)
    bash_old = (
        "# next: nano:prodhard · nano:shipreal · nano:nanogen5 "
        "(as stages land)"
    )
    bash_new = (
        "npm run nano:prodhard\n"
        "# next: nano:shipreal · nano:nanogen5 (as stages land)"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def run_prodhard(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    trials_dir: Path,
    workers: int,
) -> dict[str, Any]:
    """
    GIVEN AU0 product-debt suite
    WHEN measuring live-audit debts on production ask path
    THEN PROMOTE/HOLD/KILL per pesquisa §5 AU1.
    """
    t0 = time.perf_counter()
    trials_dir.mkdir(parents=True, exist_ok=True)
    _AU_BANK.parent.mkdir(parents=True, exist_ok=True)
    if not _AU_BANK.is_file():
        _AU_BANK.write_text("", encoding="utf-8")

    para_hits, para_rows = _score_human_para(
        root=root, bank=bank, curated=curated, workers=workers
    )
    with ThreadPoolExecutor(max_workers=min(3, workers)) as pool:
        fut_nm = pool.submit(
            _ask, NEAR_MISS_ASK, root=root, bank=bank, curated=curated
        )
        fut_kn = pool.submit(
            _ask, KNOWN_ASK, root=root, bank=bank, curated=curated
        )
        fut_pk = pool.submit(_peak_row, curated=curated, question=PEAK_ASK)
        near = fut_nm.result()
        known = fut_kn.result()
        peak = fut_pk.result()

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
    board = extract_prodhard_board(
        para_hits=para_hits,
        near=near,
        peak=peak,
        known=known,
        metrics=metrics,
        ship=ship,
    )
    decision = decide_prodhard(board=board, anti_fp_signed=True)
    wall_s = time.perf_counter() - t0
    write_json(
        trials_dir / "AU-PRODHARD-BOARD.json",
        {"board": board, "para_rows": para_rows, "decision": decision},
    )
    _write_public(decision=decision, board=board, wall_s=wall_s)
    _update_local_session(decision, board)
    _patch_pesquisa(decision)
    payload = {
        "id": PRODHARD_ID,
        "thesis": PRODHARD_THESIS,
        "decision": decision,
        "board": board,
        "para_rows": para_rows,
        "wall_s": wall_s,
        "workers": workers,
        "claim": PRODHARD_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hprodhard-prodhard.md",
        "next": "AU2 H-SHIPREAL",
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
        payload = run_prodhard(
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
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": PRODHARD_ID,
                "decision": decision[:140],
                "cpu_threads": threads,
                "workers": workers,
                "para_hit": (payload.get("board") or {}).get("para_hit"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
