"""Wave AT1 H-PRODREG runner (nano:prodreg) — Caminho A regression."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from at_session_ops import AT0_PRODREG_SUITE
from matrix_common import REPO, write_json
from prodreg_ops import (
    PRODREG_ANTI_FP,
    PRODREG_CLAIM,
    PRODREG_ID,
    PRODREG_PILLARS,
    PRODREG_SAFE_NOTE,
    PRODREG_THESIS,
    bars_from_suite,
    decide_prodreg,
    extract_prodreg_metrics,
)
from run_advsafe import run_advsafe
from run_askabstain import run_askabstain
from run_metrics import run_metrics
from run_paraext2 import run_paraext2
from run_shipui import run_shipui
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-at/prodreg_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-at/trials"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AS_BANK = REPO / "results/nano-lm/wave-as/error_bank.jsonl"
_AT_BANK = REPO / "results/nano-lm/wave-at/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hprodreg-prodreg.md"
_LOCAL_SESSION = REPO / ".local/wave-at/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_ASK_OUT = REPO / "results/nano-lm/wave-at/askabstain_reg.json"
_ADV_OUT = REPO / "results/nano-lm/wave-at/advsafe_reg.json"
_PARA_OUT = REPO / "results/nano-lm/wave-at/paraext2_reg.json"
_METRICS_OUT = REPO / "results/nano-lm/wave-at/metrics_reg.json"
_SHIP_OUT = REPO / "results/nano-lm/wave-at/shipui_reg.json"


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
    # Max safe: leave 2 cores; ~10Gi avail — avoid thrash on metrics PEAK×256.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 2))
    workers = min(12, max(4, cpus - 2))
    return threads, workers


def _write_public(
    *,
    decision: str,
    pillars: dict[str, str],
    board: dict[str, Any],
    wall_s: float,
) -> None:
    bars = bars_from_suite()
    lat_rows = []
    for name, row in (board.get("latency") or {}).items():
        lat_rows.append(
            f"| {name} | **{row.get('p50_wall_ms')}** | "
            f"**{row.get('p99_wall_ms')}** |"
        )
    holes = board.get("kb_hole_list") or []
    hole_lines = [f"- `{h}`" for h in holes] or ["_(none / see AS METRICS)_"]
    body = "\n".join(
        [
            f"# H-PRODREG — Caminho A regression (**DONE** — "
            f"{decision.split('(', 1)[0].strip()})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AT1 · Session: "
            "`.local/wave-at/SESSION.md`  ",
            "> Parent: [wave-at-session.md](wave-at-session.md) · "
            "Suite: AT0 PRODREG  ",
            "> Module: `nano_lm/src/prodreg_ops.py` · "
            "Runner: `npm run nano:prodreg`",
            "",
            "## Hypothesis",
            "",
            PRODREG_THESIS,
            "",
            "## Gate",
            "",
            "| Pillar | Decision |",
            "|--------|----------|",
            *[
                f"| {name} | **{pillars.get(name, 'MISSING')}** |"
                for name in PRODREG_PILLARS
            ],
            "",
            "| Metric | Result | Bar |",
            "|--------|-------:|-----|",
            f"| para_hit | **{board.get('para_hit')}** "
            f"({board.get('para_n_true')}/{board.get('para_n')}) | "
            f"≥ {bars.get('para_hit_min')} |",
            f"| false_hit | **{board.get('false_hit')}** | "
            f"**{bars.get('false_hit_max')}** |",
            f"| modes_visible | **{' · '.join(board.get('modes_visible') or [])}** "
            f"({board.get('modes_n')}/4) | LOOKUP·PEAK·DECODE·ABSTAIN |",
            f"| default_ask_abstain_rate | "
            f"**{board.get('default_ask_abstain_rate')}** | ABSTAIN |",
            f"| kb_coverage_pct | **{board.get('kb_coverage_pct')}** | "
            "publish + holes |",
            f"| Decision | **{decision.split('(', 1)[0].strip()}** | — |",
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
            "1. Live remeasure of AS product pillars under `write_docs=False` "
            "(AS formal archives stay frozen).  ",
            "2. Bars from AT0 PRODREG suite (para≥0.70 · FH0 · modes · "
            "abstain · latency/KB publish).  ",
            "3. No vanity re-SEMFIX / re-ADVSAFE unless this gate fails.  ",
            f"4. Wall clock ~{wall_s:.1f}s · max safe CPU (`cpus-2`).  ",
            "5. Generative claim still locked until AT3 H-NANOGEN4.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:prodreg",
            "npm run nano:at:session",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-at/prodreg_summary.json`  ",
            "- Pillar regs: `results/nano-lm/wave-at/*_reg.json`  ",
            "- Contract: `nano_lm/tests/test_prodreg.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            f"| {PRODREG_CLAIM} | Open chat / mini-AGI |",
            "| Honest HOLD/KILL on bar fail | LOOKUP-as-IQ · SAFE-as-quality |",
            "| Republish p50/p99 + KB holes | Rewrite AS locked formals |",
            "",
            f"SAFE note: {PRODREG_SAFE_NOTE}  ",
            f"Anti-FP: {PRODREG_ANTI_FP}",
            "",
            "Next: **AT2 H-SHIPAPP** — human demo/apps always show mode.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _update_local_session(decision: str, pillars: dict[str, str]) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    status = f"DONE — {decision.split('(', 1)[0].strip()}"
    body = "\n".join(
        [
            f"# Wave AT session checklist (**OPEN** · AT1 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AT **OPEN** · Caminho A ship + Nano Generative).  ",
            "> Parent: AS COMPLETE + FROZEN · Ship: **AF + AQ + AS trust "
            "path — not open chat LM** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AT1 — H-PRODREG ({status})** · Next: **AT2 H-SHIPAPP**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AT OPEN** |",
            f"| ASKABSTAIN / ADVSAFE | **{pillars.get('askabstain')}** / "
            f"**{pillars.get('advsafe')}** |",
            f"| PARAEXT2 / METRICS | **{pillars.get('paraext2')}** / "
            f"**{pillars.get('metrics')}** |",
            f"| SHIPUI modes | **{pillars.get('shipui')}** |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AT0 | SESSION | **DONE — PROMOTE** |",
            f"| AT1 | H-PRODREG | **{status}** |",
            "| AT2 | H-SHIPAPP | **NEXT** |",
            "| AT3 | H-NANOGEN4 | pending (generative north-star gate) |",
            "| AT4 | AT-REAL-EVAL | pending |",
            "| AT5 | AT-REPORT | pending |",
            "| AT6 | AT-FREEZE | pending |",
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
        "| AT1 | **H-PRODREG** | Caminho A regression: para hit · FH · "
        "p50/p99 · KB holes · modes · default-ask abstain | all AS product "
        "bars hold else **HOLD**/fix | pending |"
    )
    new = (
        "| AT1 | **H-PRODREG** | Caminho A regression: para hit · FH · "
        "p50/p99 · KB holes · modes · default-ask abstain | all AS product "
        f"bars hold else **HOLD**/fix | **DONE — {status}** |"
    )
    if old in text:
        text = text.replace(old, new, 1)
    old_next = (
        "2. **H-PRODREG** then **H-SHIPAPP** — ship Caminho A "
        "(metrics + mode UI always)."
    )
    new_next = (
        f"2. **H-PRODREG** — **DONE {status}** (`npm run nano:prodreg`) · "
        "next **AT2 H-SHIPAPP**."
    )
    if old_next in text:
        text = text.replace(old_next, new_next, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def run_prodreg(
    *,
    root: Path,
    bank: Path,
    as_bank: Path,
    curated: Path,
    out: Path,
    trials_dir: Path,
    workers: int,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN AT0 PRODREG suite + AS packs
    WHEN remeasuring five product pillars (no AS doc rewrite)
    THEN PROMOTE/HOLD/KILL per pesquisa §5 AT1.
    """
    t0 = time.perf_counter()
    trials_dir.mkdir(parents=True, exist_ok=True)
    _AT_BANK.parent.mkdir(parents=True, exist_ok=True)
    if not _AT_BANK.is_file():
        _AT_BANK.write_text("", encoding="utf-8")

    ask = run_askabstain(
        bank_path=bank,
        root=root,
        out=_ASK_OUT,
        trials_dir=trials_dir,
        curated_root=curated,
        seed=seed,
        write_docs=False,
    )
    adv = run_advsafe(
        bank_path=bank,
        root=root,
        out=_ADV_OUT,
        trials_dir=trials_dir,
        curated_root=curated,
        seed=seed,
        write_docs=False,
    )
    para = run_paraext2(
        bank_path=bank,
        as_bank=as_bank,
        root=root,
        out=_PARA_OUT,
        trials_dir=trials_dir,
        curated_root=curated,
        seed=seed,
        write_docs=False,
    )
    metrics = run_metrics(
        root=root,
        bank=bank,
        curated=curated,
        out=_METRICS_OUT,
        workers=workers,
        seed=seed,
        write_docs=False,
    )
    ship = run_shipui(
        root=root,
        bank=bank,
        curated=curated,
        out=_SHIP_OUT,
        write_docs=False,
    )
    pillars = {
        "askabstain": str(ask.get("decision", "")),
        "advsafe": str(adv.get("decision", "")),
        "paraext2": str(para.get("decision", "")),
        "metrics": str(metrics.get("decision", "")),
        "shipui": str(ship.get("decision", "")),
    }
    board = extract_prodreg_metrics(
        para=para, adv=adv, metrics=metrics, ask=ask, ship=ship
    )
    decision = decide_prodreg(
        pillars=pillars,
        metrics_board=board,
        bars=bars_from_suite(AT0_PRODREG_SUITE),
        anti_fp_signed=True,
    )
    wall_s = time.perf_counter() - t0
    _write_public(
        decision=decision, pillars=pillars, board=board, wall_s=wall_s
    )
    _update_local_session(decision, pillars)
    _patch_pesquisa(decision)
    summary: dict[str, Any] = {
        "hyp_id": PRODREG_ID,
        "stage": "AT1",
        "thesis": PRODREG_THESIS,
        "decision": decision,
        "pillars": pillars,
        "metrics_board": board,
        "bars": bars_from_suite(),
        "claim": PRODREG_CLAIM,
        "safe_note": PRODREG_SAFE_NOTE,
        "anti_fp": PRODREG_ANTI_FP,
        "suite": dict(AT0_PRODREG_SUITE),
        "cpu_threads": None,
        "workers": workers,
        "wall_s": round(wall_s, 3),
        "public_note": "docs/results/nano-lm/formal-hprodreg-prodreg.md",
        "next": "AT2 H-SHIPAPP",
        "no_reopen_unless_fail": AT0_PRODREG_SUITE.get(
            "no_reopen_unless_fail"
        ),
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--as-bank", type=Path, default=_AS_BANK)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    threads, workers = _hardware()
    try:
        summary = run_prodreg(
            root=Path(args.root),
            bank=Path(args.bank),
            as_bank=Path(args.as_bank),
            curated=Path(args.curated),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            workers=workers,
            seed=int(args.seed),
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    summary["cpu_threads"] = threads
    write_json(Path(args.out), summary)
    ok = str(summary.get("decision", "")).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": PRODREG_ID,
                "decision": str(summary.get("decision", ""))[:120],
                "cpu_threads": threads,
                "workers": workers,
                "wall_s": summary.get("wall_s"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
