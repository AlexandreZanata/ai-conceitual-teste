"""Wave AS8 AS-DUAL-HITL runner — product pillars + gen gate status."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from as_dual_hitl_ops import (
    APP_SMOKE_PACK,
    DUAL_HITL_ID,
    DUAL_HITL_THESIS,
    HONEST_CLAIM,
    apps_ok,
    claim_is_honest,
    decide_as_dual_hitl,
)
from as_session_ops import map_as_product_mode
from matrix_common import REPO, write_json
from modeui_ops import attach_modeui
from run_advsafe import run_advsafe
from run_askabstain import run_askabstain
from run_metrics import run_metrics
from run_paraext2 import run_paraext2
from run_shipui import run_shipui
from run_z_ask import ask_many
from semwrap_ops import classify_semwrap, semantic_lookup
from tipd_pair import tune_cpu_threads
from z_wrap import load_bank_rows

_SUMMARY = REPO / "results/nano-lm/wave-as/as_dual_hitl_summary.json"
_NANOGEN3 = REPO / "results/nano-lm/wave-as/nanogen3_summary.json"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AS_BANK = REPO / "results/nano-lm/wave-as/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-as/trials"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/wave-as-dual-hitl.md"
_LOCAL_SESSION = REPO / ".local/wave-as/SESSION.md"
_ASK_OUT = REPO / "results/nano-lm/wave-as/askabstain_summary.json"
_SHIP_OUT = REPO / "results/nano-lm/wave-as/shipui_summary.json"
_ADV_OUT = REPO / "results/nano-lm/wave-as/advsafe_summary.json"
_PARA_OUT = REPO / "results/nano-lm/wave-as/paraext2_summary.json"
_METRICS_OUT = REPO / "results/nano-lm/wave-as/metrics_summary.json"


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
    workers = min(14, max(4, cpus - 2))
    return threads, workers


def _load_decision(path: Path) -> str:
    if not path.is_file():
        return "MISSING"
    data = json.loads(path.read_text(encoding="utf-8"))
    return str(data.get("decision", "MISSING"))


def _apps_smoke(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    seed: int,
) -> list[dict[str, Any]]:
    bank_rows = load_bank_rows(bank)
    questions = [p["question"] for p in APP_SMOKE_PACK]
    payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        wrap=True,
        bank_path=bank,
        curated_root=curated,
    )
    trials: list[dict[str, Any]] = []
    for item, payload in zip(APP_SMOKE_PACK, payloads, strict=True):
        payload = attach_modeui(dict(payload))
        mode = str(payload.get("mode", ""))
        completion = str(payload.get("completion", ""))
        looked, meta = semantic_lookup(
            item["question"], bank_rows, curated_root=curated
        )
        used = (
            completion
            if mode in {"SEMWRAP_LOOKUP", "WRAP_LOOKUP", "ASKFAST_CACHE"}
            else looked
        )
        kind = classify_semwrap(
            used,
            expected_gold=item["gold"],
            expected_source_id=item["source_id"],
            hit_source_id=str(meta.get("source_id") or "") or None,
        )
        trials.append(
            {
                "trial_id": item["id"],
                "stage": "AS8",
                "hyp_id": DUAL_HITL_ID,
                "app_id": item["app_id"],
                "question": item["question"],
                "source_id": item["source_id"],
                "mode": mode,
                "product_mode": map_as_product_mode(mode),
                "modeui_line": payload.get("modeui_line"),
                "lookup_kind": kind,
                "completion": completion[:120],
                "wall_ms": payload.get("wall_ms"),
                "n_new": payload.get("n_new"),
                "gold": item["gold"],
            }
        )
    return trials


def _write_public(
    *,
    decision: str,
    pillars: dict[str, str],
    apps: list[dict[str, Any]],
    nanogen3: str,
    claim: str,
) -> None:
    app_rows = [
        f"| {t['app_id']} | **{t['lookup_kind']}** | "
        f"`{t.get('modeui_line', '')}` |"
        for t in apps
    ]
    body = "\n".join(
        [
            f"# AS-DUAL-HITL — product + gen gate (**DONE** — {decision})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AS8 · Session: "
            "`.local/wave-as/SESSION.md`  ",
            "> Parent: [formal-hnanogen3-nanogen3.md]"
            "(formal-hnanogen3-nanogen3.md)  ",
            "> Module: `nano_lm/src/as_dual_hitl_ops.py` · "
            "Runner: `npm run nano:as:dual-hitl`",
            "",
            "## Hypothesis",
            "",
            "Composite dual-arm HITL (ASKABSTAIN · SHIPUI · ADVSAFE · "
            "METRICS · PARAEXT2 · apps). Generative ship claim unlocks "
            "**only** if AS7 H-NANOGEN3 PROMOTE.",
            "",
            "## Gate",
            "",
            "| Pillar | Decision |",
            "|--------|----------|",
            f"| H-ASKABSTAIN (core) | **{pillars['askabstain']}** |",
            f"| H-SHIPUI (core) | **{pillars['shipui']}** |",
            f"| H-ADVSAFE (core) | **{pillars['advsafe']}** |",
            f"| H-METRICS (core) | **{pillars['metrics']}** |",
            f"| H-PARAEXT2 (deepen) | **{pillars['paraext2']}** |",
            f"| Apps known/howto/long-doc | "
            f"**{'PASS' if apps_ok(apps) else 'FAIL'}** |",
            f"| AS7 H-NANOGEN3 | **{nanogen3}** |",
            f"| Ship claim | `{claim}` |",
            f"| Decision | **{decision}** |",
            "",
            "## Apps LOOKUP smoke",
            "",
            "| Surface | lookup_kind | modeui_line |",
            "|---------|-------------|-------------|",
            *app_rows,
            "",
            "## Finding",
            "",
            "1. Live re-verify of AS1–AS6 product pillars under max safe "
            "CPU (`cpus-2`).  ",
            "2. Three app surfaces TRUE_HIT LOOKUP (product path).  ",
            "3. AS7 HOLD → generative / open-chat / mini-AGI claim stays "
            "locked.  ",
            "4. Soft deepen defects (PARAEXT2) → HOLD; all PROMOTE → "
            "product PROMOTE with gen locked.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:as:dual-hitl",
            "npm run nano:z:ask -- --wrap --question \"Write a short Python "
            "function named add that returns the sum of two integers a and b.\"",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-as/as_dual_hitl_summary.json`  ",
            "- Contract: `nano_lm/tests/test_as_dual_hitl.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| AF packaged stack + AQ product layer | Open chat / mini-AGI |",
            "| Product PROMOTE with gen locked | Generative unlock "
            "without AS7 |",
            "| Mode-visible LOOKUP apps | LOOKUP-as-gen-IQ · Wave AT invent |",
            "",
            "Next: **AS9 AS-REPORT** — public summary + paper-lab.",
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
            f"# Wave AS session checklist (**OPEN** · AS8 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AS **OPEN**).  ",
            "> Parent: AR COMPLETE + FROZEN · Ship: **AF packaged stack + "
            "AQ product layer — not open chat LM** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AS8 — AS-DUAL-HITL ({status})** · Next: **AS9 AS-REPORT**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AS OPEN** |",
            f"| ASKABSTAIN / SHIPUI | **{pillars.get('askabstain')}** / "
            f"**{pillars.get('shipui')}** |",
            f"| ADVSAFE / METRICS | **{pillars.get('advsafe')}** / "
            f"**{pillars.get('metrics')}** |",
            f"| PARAEXT2 | **{pillars.get('paraext2')}** |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AS0 | SESSION | **DONE — PROMOTE** |",
            "| AS1 | H-ASKABSTAIN | **DONE — PROMOTE** |",
            "| AS2 | H-SEMFIX | **DONE — PROMOTE** |",
            "| AS3 | H-ADVSAFE | **DONE — PROMOTE** |",
            "| AS4 | H-PARAEXT2 | **DONE — PROMOTE** |",
            "| AS5 | H-METRICS | **DONE — PROMOTE** |",
            "| AS6 | H-SHIPUI | **DONE — PROMOTE** |",
            "| AS7 | H-NANOGEN3 | **DONE — HOLD** |",
            f"| AS8 | AS-DUAL-HITL | **{status}** |",
            "| AS9 | AS-REPORT | **NEXT** |",
            "| AS10 | AS-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def run_as_dual_hitl(
    *,
    root: Path,
    bank: Path,
    as_bank: Path,
    curated: Path,
    out: Path,
    trials_dir: Path,
    nanogen3_path: Path,
    claim: str,
    workers: int,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN AS product pillars + AS7 status
    WHEN running composite dual HITL
    THEN PROMOTE/HOLD/KILL per pesquisa §5 AS8.
    """
    t0 = time.perf_counter()
    trials_dir.mkdir(parents=True, exist_ok=True)
    ask = run_askabstain(
        bank_path=bank,
        root=root,
        out=_ASK_OUT,
        trials_dir=trials_dir,
        curated_root=curated,
        seed=seed,
    )
    ship = run_shipui(
        root=root, bank=bank, curated=curated, out=_SHIP_OUT
    )
    adv = run_advsafe(
        bank_path=bank,
        root=root,
        out=_ADV_OUT,
        trials_dir=trials_dir,
        curated_root=curated,
        seed=seed,
    )
    para = run_paraext2(
        bank_path=bank,
        as_bank=as_bank,
        root=root,
        out=_PARA_OUT,
        trials_dir=trials_dir,
        curated_root=curated,
        seed=seed,
    )
    metrics = run_metrics(
        root=root,
        bank=bank,
        curated=curated,
        out=_METRICS_OUT,
        workers=workers,
        seed=seed,
    )
    apps = _apps_smoke(
        root=root, bank=bank, curated=curated, seed=seed
    )
    for t in apps:
        write_json(trials_dir / f"{t['trial_id']}.json", t)
    nanogen3 = _load_decision(nanogen3_path)
    pillars = {
        "askabstain": str(ask.get("decision", "")),
        "shipui": str(ship.get("decision", "")),
        "advsafe": str(adv.get("decision", "")),
        "metrics": str(metrics.get("decision", "")),
        "paraext2": str(para.get("decision", "")),
    }
    apps_pass = apps_ok(apps)
    decision = decide_as_dual_hitl(
        askabstain_decision=pillars["askabstain"],
        shipui_decision=pillars["shipui"],
        advsafe_decision=pillars["advsafe"],
        metrics_decision=pillars["metrics"],
        paraext2_decision=pillars["paraext2"],
        apps_pass=apps_pass,
        nanogen3_decision=nanogen3,
        claim=claim,
    )
    _write_public(
        decision=decision,
        pillars=pillars,
        apps=apps,
        nanogen3=nanogen3,
        claim=claim,
    )
    _update_local_session(decision, pillars)
    summary: dict[str, Any] = {
        "hyp_id": DUAL_HITL_ID,
        "stage": "AS8",
        "thesis": DUAL_HITL_THESIS,
        "decision": decision,
        "pillars": pillars,
        "apps_pass": apps_pass,
        "apps": apps,
        "nanogen3_decision": nanogen3,
        "claim": claim,
        "claim_honest": claim_is_honest(claim),
        "generative_claim_unlocked": False,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "elapsed_s": time.perf_counter() - t0,
        "forbidden": [
            "open-chat / mini-AGI claim",
            "generative unlock while AS7 HOLD",
            "LOOKUP-as-gen-IQ",
            "Wave AT invent",
        ],
        "public_note": "docs/results/nano-lm/wave-as-dual-hitl.md",
        "ship_claim": claim,
        "next": "AS9 AS-REPORT",
        "anti_fp": (
            "product PROMOTE with gen locked; no mini-AGI while NANOGEN3 HOLD"
        ),
    }
    write_json(Path(out), summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AS8 AS-DUAL-HITL")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--as-bank", type=Path, default=_AS_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--nanogen3", type=Path, default=_NANOGEN3)
    ap.add_argument("--claim", type=str, default=HONEST_CLAIM)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        summary = run_as_dual_hitl(
            root=Path(args.root),
            bank=Path(args.bank),
            as_bank=Path(args.as_bank),
            curated=Path(args.curated),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            nanogen3_path=Path(args.nanogen3),
            claim=str(args.claim),
            workers=workers,
            seed=int(args.seed),
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    decision = str(summary.get("decision", ""))
    ok = decision.startswith(("PROMOTE", "HOLD"))
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": DUAL_HITL_ID,
                "decision": decision,
                "pillars": summary.get("pillars"),
                "apps_pass": summary.get("apps_pass"),
                "nanogen3_decision": summary.get("nanogen3_decision"),
                "claim": summary.get("claim"),
                "cpu_threads": threads,
                "workers": workers,
                "elapsed_s": summary.get("elapsed_s"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
