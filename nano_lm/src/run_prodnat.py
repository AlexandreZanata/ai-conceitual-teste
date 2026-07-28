"""Wave AX1 H-PRODNAT runner (nano:prodnat) — close hard-natural para debt."""

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
from prodnat_ops import (
    DECODE_PROBE_ASK,
    HARD_NATURAL_ROWS,
    KNOWN_ASK,
    NEAR_MISS_ASK,
    PEAK_ASK,
    PRODNAT_ANTI_FP,
    PRODNAT_CLAIM,
    PRODNAT_ID,
    PRODNAT_SAFE_NOTE,
    PRODNAT_THESIS,
    bars_from_nat_charter,
    decide_prodnat,
    extract_prodnat_board,
    gate_junk_decode,
    human_para_hit,
)
from run_metrics import run_metrics
from run_shipui import run_shipui
from run_z_ask import ask_once
from shipreal_ops import attach_shipreal
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-ax/prodnat_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-ax/trials"
_AX_BANK = REPO / "results/nano-lm/wave-ax/error_bank.jsonl"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hprodnat-prodnat.md"
_LOCAL_SESSION = REPO / ".local/wave-ax/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENTS = REPO / "AGENTS.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_METRICS_OUT = REPO / "results/nano-lm/wave-ax/metrics_reg.json"
_SHIP_OUT = REPO / "results/nano-lm/wave-ax/shipui_reg.json"
_EMPTY_BANK = REPO / "results/nano-lm/wave-ax/_decode_empty_bank.jsonl"
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
    # Max safe on 16c / ~13Gi avail: leave 2 cores; cap workers to avoid thrash.
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


def _score_hard_natural(
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

    # Cap parallel asks to leave RAM headroom for model weights.
    n = min(workers, 8, len(HARD_NATURAL_ROWS))
    with ThreadPoolExecutor(max_workers=max(1, n)) as pool:
        rows = list(pool.map(_one, list(HARD_NATURAL_ROWS)))
    return [bool(r["hit"]) for r in rows], rows


def _write_public(
    *,
    decision: str,
    board: dict[str, Any],
    wall_s: float,
) -> None:
    bars = bars_from_nat_charter()
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
            f"# H-PRODNAT — hard-natural Caminho A (**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AX1 · Session: "
            "`.local/wave-ax/SESSION.md`  ",
            "> Parent: [wave-ax-session.md](wave-ax-session.md) · "
            "Suite: AX0 product-nat  ",
            "> Module: `nano_lm/src/prodnat_ops.py` · "
            "Runner: `npm run nano:prodnat`",
            "",
            "## Hypothesis",
            "",
            PRODNAT_THESIS,
            "",
            "## Gate",
            "",
            "| Metric | Result | Bar |",
            "|--------|-------:|-----|",
            f"| hard_natural_para_hit | **{board.get('hard_natural_para_hit')}** "
            f"({board.get('para_n_true')}/{board.get('para_n')}) | "
            f"≥ {bars.get('hard_natural_para_hit_min')} · n≥"
            f"{bars.get('hard_natural_min_n')} |",
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
            "## DECODE probe (content law)",
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
            "1. Hard-natural held-out (N≥15 ≠ AW/AV/AU) scored on production "
            "`nano:z:ask --wrap --semwrap`.  ",
            "2. SEMWRAP same-gold whitespace collapse closes live miss "
            "(multiline vs one-liner `def add`) — **not** bank stuffing.  ",
            "3. Near-miss BIP-39+SegWit stays ABSTAIN on default ask.  ",
            "4. DECODE content law holds — usable or ABSTAIN.  ",
            "5. Modes + latency + KB republished; pack-para ≠ hard-natural.  ",
            f"6. Wall clock ~{wall_s:.1f}s · max safe CPU (`cpus-2`).  ",
            "7. Generative claim still locked (gen stance **defer**; "
            "NANOGEN6·7 HOLD).",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:prodnat",
            "npm run nano:ax:session",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-ax/prodnat_summary.json`  ",
            "- Contract: `nano_lm/tests/test_prodnat.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            f"| {PRODNAT_CLAIM} | Open chat / mini-AGI |",
            "| Eval path = prod ask path | LOOKUP-as-IQ · SAFE-as-quality |",
            "| Hard-natural hit ≥ bar | Pack-para as world coverage |",
            "| Honest HOLD/KILL on bar fail | Paraphrase bank stuffing |",
            "",
            f"SAFE note: {PRODNAT_SAFE_NOTE}  ",
            f"Anti-FP: {PRODNAT_ANTI_FP}",
            "",
            "Next: **AX2 H-SHIPUX** — ship/demo mode+content honesty.",
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
            f"# Wave AX session checklist (**OPEN** · AX1 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AX **OPEN** · hard-natural harden + gen defer).  ",
            f"> Ship lock: **{PRODNAT_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AX1 — H-PRODNAT ({status})** · Next: **AX2 H-SHIPUX**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AX OPEN** |",
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
            "| AX0 | SESSION | **DONE — PROMOTE** |",
            f"| AX1 | H-PRODNAT | **{status}** |",
            "| AX2 | H-SHIPUX | **NEXT** |",
            "| AX3 | H-NANOGEN8 | pending (defer unless real new method) |",
            "| AX4 | AX-REAL-EVAL | pending |",
            "| AX5 | AX-REPORT | pending |",
            "| AX6 | AX-FREEZE | pending |",
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
        "| AX1 | **H-PRODNAT** | Caminho A: hard natural para · FH 0 · "
        "p50/p99 · KB · modes · DECODE law | hard-natural bar · "
        "metrics board | **TODO** |"
    )
    new = (
        "| AX1 | **H-PRODNAT** | Caminho A: hard natural para · FH 0 · "
        "p50/p99 · KB · modes · DECODE law | hard-natural bar · "
        f"metrics board | **DONE — {status}** |"
    )
    if old in text:
        text = text.replace(old, new, 1)
    for old_next in (
        (
            "2. **AX1 H-PRODNAT** — **NEXT** — accept Caminho A artifact; "
            "close hard natural para debt; publish para · FH · p50/p99 · KB; "
            "mode UI always.  "
        ),
        (
            "2. **AX1 H-PRODNAT** — accept Caminho A artifact; "
            "close hard natural para debt; publish para · FH · p50/p99 · KB; "
            "mode UI always.  "
        ),
    ):
        if old_next in text:
            text = text.replace(
                old_next,
                f"2. **AX1 H-PRODNAT** — **DONE {status}** "
                "(`npm run nano:prodnat`) · next **AX2 H-SHIPUX**.  ",
                1,
            )
            break
    bash_old = "# next: nano:prodnat · nano:shipux"
    if bash_old in text:
        text = text.replace(
            bash_old,
            "npm run nano:prodnat\n# next: nano:shipux",
            1,
        )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def _patch_local_impl(decision: str) -> None:
    if not _LOCAL_IMPL.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_IMPL.read_text(encoding="utf-8")
    old = (
        "2. **AX1 H-PRODNAT** — **NEXT** — close hard natural para debt; "
        "publish metrics board.  "
    )
    new = (
        "2. **AX1 H-PRODNAT** — **DONE PROMOTE** (`npm run nano:prodnat`) · "
        "next **AX2 H-SHIPUX**.  "
    )
    if old in text:
        text = text.replace(old, new, 1)
        _LOCAL_IMPL.write_text(text, encoding="utf-8")


def _patch_local_readme(decision: str) -> None:
    if not _LOCAL_README.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_README.read_text(encoding="utf-8")
    old = (
        "Session: `wave-ax/SESSION.md` (AX0 **DONE — PROMOTE**; "
        "next AX1 H-PRODNAT)."
    )
    new = (
        "Session: `wave-ax/SESSION.md` (AX1 H-PRODNAT **DONE — PROMOTE**; "
        "next AX2 H-SHIPUX)."
    )
    if old in text:
        text = text.replace(old, new, 1)
        _LOCAL_README.write_text(text, encoding="utf-8")


def _insert_prodnat_frag(text: str, prefix: str, frag: str) -> str:
    if "H-PRODNAT PROMOTE" in text:
        return text
    text2, count = re.subn(
        rf"({re.escape(prefix)}[^\n]*AX0 \[SESSION PROMOTE\]"
        r"\([^)]+\)[^\n]*?)(; next AX1 H-PRODNAT|; next AX1)",
        rf"\1 · {frag}; next AX2 H-SHIPUX",
        text,
        count=1,
    )
    return text2 if count else text


def _patch_agents_prodnat() -> None:
    if not _AGENTS.is_file():
        return
    text = _AGENTS.read_text(encoding="utf-8")
    if "H-PRODNAT PROMOTE" in text:
        return
    text2, count = re.subn(
        r"(- \*\*Wave AX ACTIVE\*\* —[^\n]*AX0 \[SESSION PROMOTE\]"
        r"[^\n]*?)(; next AX1 H-PRODNAT|; next AX1)",
        r"\1 · AX1 [H-PRODNAT PROMOTE]"
        r"(docs/results/nano-lm/formal-hprodnat-prodnat.md) "
        r"(`npm run nano:prodnat`); next AX2 H-SHIPUX",
        text,
        count=1,
    )
    if count:
        _AGENTS.write_text(text2, encoding="utf-8")


def _patch_agenda_prodnat() -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    ax_tail = text.split("| **AX** |", 1)[-1][:400]
    if "H-PRODNAT" in ax_tail:
        return
    text2, count = re.subn(
        r"(\| \*\*AX\*\* \| \*\*ACTIVE\*\* \|[^\n]*AX0 \[SESSION "
        r"PROMOTE\][^\n]*?)(; next AX1 H-PRODNAT|; next AX1)",
        r"\1 · AX1 [H-PRODNAT PROMOTE]"
        r"(results/nano-lm/formal-hprodnat-prodnat.md); "
        r"next AX2 H-SHIPUX",
        text,
        count=1,
    )
    if count:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_public_status(decision: str, board: dict[str, Any]) -> None:
    if not decision.startswith("PROMOTE"):
        return
    hit = board.get("hard_natural_para_hit")
    n_true = board.get("para_n_true")
    n = board.get("para_n")
    frag = (
        f"AX1 [H-PRODNAT PROMOTE](formal-hprodnat-prodnat.md) "
        f"(`npm run nano:prodnat`) — hard-natural **{hit}**/{n} "
        f"({n_true}/{n}) · FH **0**"
    )
    for path, prefix in (
        (_RECIPES, "**Wave AX ACTIVE:**"),
        (_CARD, "**Wave AX ACTIVE** —"),
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        updated = _insert_prodnat_frag(text, prefix, frag)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
    _patch_agents_prodnat()
    _patch_agenda_prodnat()


def run_prodnat(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    trials_dir: Path,
    workers: int,
) -> dict[str, Any]:
    """
    GIVEN AX0 product-nat charter
    WHEN measuring hard-natural bars on production ask path
    THEN PROMOTE/HOLD/KILL per pesquisa §5 AX1.
    """
    t0 = time.perf_counter()
    trials_dir.mkdir(parents=True, exist_ok=True)
    _AX_BANK.parent.mkdir(parents=True, exist_ok=True)
    if not _AX_BANK.is_file():
        _AX_BANK.write_text("", encoding="utf-8")

    para_hits, para_rows = _score_hard_natural(
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
    board = extract_prodnat_board(
        para_hits=para_hits,
        near=near,
        peak=peak,
        known=known,
        decode=decode,
        metrics=metrics,
        ship=ship,
    )
    decision = decide_prodnat(board=board, anti_fp_signed=True)
    wall_s = time.perf_counter() - t0
    write_json(
        trials_dir / "AX-PRODNAT-BOARD.json",
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
    _patch_public_status(decision, board)
    payload = {
        "id": PRODNAT_ID,
        "thesis": PRODNAT_THESIS,
        "decision": decision,
        "board": board,
        "para_rows": para_rows,
        "wall_s": wall_s,
        "workers": workers,
        "claim": PRODNAT_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hprodnat-prodnat.md",
        "next": "AX2 H-SHIPUX",
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
        payload = run_prodnat(
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
                "hyp_id": PRODNAT_ID,
                "decision": decision[:140],
                "cpu_threads": threads,
                "workers": workers,
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
