"""Wave AR6 AR-DUAL-HITL runner — product pillars + gen gate status."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from ar_dual_hitl_ops import (
    APP_SMOKE_PACK,
    DUAL_HITL_ID,
    DUAL_HITL_THESIS,
    HONEST_CLAIM,
    apps_ok,
    claim_is_honest,
    decide_ar_dual_hitl,
)
from ar_session_ops import map_ar_product_mode
from matrix_common import REPO, write_json
from modeui_ops import attach_modeui
from run_abstain import run_abstain
from run_advreg import run_advreg
from run_paraext import run_paraext
from run_shipdemo import run_shipdemo
from run_z_ask import ask_many
from semwrap_ops import classify_semwrap, semantic_lookup
from tipd_pair import tune_cpu_threads
from z_wrap import load_bank_rows

_SUMMARY = REPO / "results/nano-lm/wave-ar/ar_dual_hitl_summary.json"
_NANOGEN2 = REPO / "results/nano-lm/wave-ar/nanogen2_summary.json"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AR_BANK = REPO / "results/nano-lm/wave-ar/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-ar/trials"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/wave-ar-dual-hitl.md"
_LOCAL_SESSION = REPO / ".local/wave-ar/SESSION.md"
_ABSTAIN_OUT = REPO / "results/nano-lm/wave-ar/abstain_summary.json"
_SHIP_OUT = REPO / "results/nano-lm/wave-ar/shipdemo_summary.json"
_PARA_OUT = REPO / "results/nano-lm/wave-ar/paraext_summary.json"
_ADV_OUT = REPO / "results/nano-lm/wave-ar/advreg_summary.json"


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


def _hardware() -> int:
    cpus = int(os.cpu_count() or 4)
    return tune_cpu_threads(max(4, cpus - 2))


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
                "stage": "AR6",
                "hyp_id": DUAL_HITL_ID,
                "app_id": item["app_id"],
                "question": item["question"],
                "source_id": item["source_id"],
                "mode": mode,
                "product_mode": map_ar_product_mode(mode),
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
    nanogen2: str,
    claim: str,
) -> None:
    app_rows = [
        f"| {t['app_id']} | **{t['lookup_kind']}** | "
        f"`{t.get('modeui_line', '')}` |"
        for t in apps
    ]
    body = "\n".join(
        [
            f"# AR-DUAL-HITL — product + gen gate (**DONE** — {decision})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AR6 · Session: "
            "`.local/wave-ar/SESSION.md`  ",
            "> Parent: [formal-hnanogen2-nanogen2.md]"
            "(formal-hnanogen2-nanogen2.md)  ",
            "> Module: `nano_lm/src/ar_dual_hitl_ops.py` · "
            "Runner: `npm run nano:ar:dual-hitl`",
            "",
            "## Hypothesis",
            "",
            "Composite dual-arm HITL (ABSTAIN · SHIPDEMO · PARAEXT · ADVREG · "
            "apps). Generative ship claim unlocks **only** if AR5 H-NANOGEN2 "
            "PROMOTE.",
            "",
            "## Gate",
            "",
            "| Pillar | Decision |",
            "|--------|----------|",
            f"| H-ABSTAIN (core) | **{pillars['abstain']}** |",
            f"| H-SHIPDEMO (core) | **{pillars['shipdemo']}** |",
            f"| H-PARAEXT (deepen) | **{pillars['paraext']}** |",
            f"| H-ADVREG (deepen) | **{pillars['advreg']}** |",
            f"| Apps known/howto/long-doc | "
            f"**{'PASS' if apps_ok(apps) else 'FAIL'}** |",
            f"| AR5 H-NANOGEN2 | **{nanogen2}** |",
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
            "1. Live re-verify of AR1–AR4 under max safe CPU (`cpus-2`).  ",
            "2. Three app surfaces TRUE_HIT LOOKUP (product path).  ",
            "3. AR5 HOLD → generative / open-chat / mini-AGI claim stays "
            "locked.  ",
            "4. Soft deepen defects (PARAEXT/ADVREG) → HOLD, not silent "
            "PROMOTE.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:ar:dual-hitl",
            "npm run nano:z:ask -- --wrap --question \"Write a short Python "
            "function named add that returns the sum of two integers a and b.\"",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-ar/ar_dual_hitl_summary.json`  ",
            "- Contract: `nano_lm/tests/test_ar_dual_hitl.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| AF packaged stack + AQ product layer | Open chat / mini-AGI |",
            "| Product HOLD with soft deepen defects | Generative unlock "
            "without AR5 |",
            "| Mode-visible LOOKUP apps | LOOKUP-as-gen-IQ · Wave AS invent |",
            "",
            "Next: **AR7 AR-REPORT** — public summary + paper-lab.",
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
            f"# Wave AR session checklist (**OPEN** · AR6 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AR **OPEN**).  ",
            "> Parent: AQ COMPLETE + FROZEN · Ship: **AF packaged stack + "
            "AQ product layer — not open chat LM** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AR6 — AR-DUAL-HITL ({status})** · Next: **AR7 AR-REPORT**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AR OPEN** |",
            f"| ABSTAIN / SHIPDEMO | **{pillars.get('abstain')}** / "
            f"**{pillars.get('shipdemo')}** |",
            f"| PARAEXT / ADVREG | **{pillars.get('paraext')}** / "
            f"**{pillars.get('advreg')}** |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AR0 | SESSION | **DONE — PROMOTE** |",
            "| AR1 | H-ABSTAIN | **DONE — PROMOTE** |",
            "| AR2 | H-SHIPDEMO | **DONE — PROMOTE** |",
            "| AR3 | H-PARAEXT | **DONE — HOLD** |",
            "| AR4 | H-ADVREG | **DONE — KILL** |",
            "| AR5 | H-NANOGEN2 | **DONE — HOLD** |",
            f"| AR6 | AR-DUAL-HITL | **{status}** |",
            "| AR7 | AR-REPORT | **NEXT** |",
            "| AR8 | AR-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def run_ar_dual_hitl(
    *,
    root: Path,
    bank: Path,
    ar_bank: Path,
    curated: Path,
    out: Path,
    trials_dir: Path,
    nanogen2_path: Path,
    claim: str,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN AR product pillars + AR5 status
    WHEN running composite dual HITL
    THEN PROMOTE/HOLD/KILL per pesquisa §5 AR6.
    """
    t0 = time.perf_counter()
    trials_dir.mkdir(parents=True, exist_ok=True)
    abstain = run_abstain(
        bank_path=bank,
        root=root,
        out=_ABSTAIN_OUT,
        trials_dir=trials_dir,
        curated_root=curated,
        seed=seed,
    )
    ship = run_shipdemo(
        root=root, bank=bank, curated=curated, out=_SHIP_OUT
    )
    para = run_paraext(
        bank_path=bank,
        ar_bank=ar_bank,
        root=root,
        out=_PARA_OUT,
        trials_dir=trials_dir,
        curated_root=curated,
        seed=seed,
    )
    adv = run_advreg(
        bank_path=bank,
        root=root,
        out=_ADV_OUT,
        trials_dir=trials_dir,
        curated_root=curated,
        seed=seed,
    )
    apps = _apps_smoke(
        root=root, bank=bank, curated=curated, seed=seed
    )
    for t in apps:
        write_json(trials_dir / f"{t['trial_id']}.json", t)
    nanogen2 = _load_decision(nanogen2_path)
    pillars = {
        "abstain": str(abstain.get("decision", "")),
        "shipdemo": str(ship.get("decision", "")),
        "paraext": str(para.get("decision", "")),
        "advreg": str(adv.get("decision", "")),
    }
    apps_pass = apps_ok(apps)
    decision = decide_ar_dual_hitl(
        abstain_decision=pillars["abstain"],
        shipdemo_decision=pillars["shipdemo"],
        paraext_decision=pillars["paraext"],
        advreg_decision=pillars["advreg"],
        apps_pass=apps_pass,
        nanogen2_decision=nanogen2,
        claim=claim,
    )
    _write_public(
        decision=decision,
        pillars=pillars,
        apps=apps,
        nanogen2=nanogen2,
        claim=claim,
    )
    _update_local_session(decision, pillars)
    summary: dict[str, Any] = {
        "hyp_id": DUAL_HITL_ID,
        "stage": "AR6",
        "thesis": DUAL_HITL_THESIS,
        "decision": decision,
        "pillars": pillars,
        "apps_pass": apps_pass,
        "apps": apps,
        "nanogen2_decision": nanogen2,
        "claim": claim,
        "claim_honest": claim_is_honest(claim),
        "generative_claim_unlocked": False,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "elapsed_s": time.perf_counter() - t0,
        "forbidden": [
            "open-chat / mini-AGI claim",
            "generative unlock while AR5 HOLD",
            "LOOKUP-as-gen-IQ",
            "Wave AS invent",
        ],
        "public_note": "docs/results/nano-lm/wave-ar-dual-hitl.md",
        "ship_claim": claim,
        "next": "AR7 AR-REPORT",
    }
    write_json(Path(out), summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AR6 AR-DUAL-HITL")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--ar-bank", type=Path, default=_AR_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--nanogen2", type=Path, default=_NANOGEN2)
    ap.add_argument("--claim", type=str, default=HONEST_CLAIM)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    threads = _hardware()
    try:
        summary = run_ar_dual_hitl(
            root=Path(args.root),
            bank=Path(args.bank),
            ar_bank=Path(args.ar_bank),
            curated=Path(args.curated),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            nanogen2_path=Path(args.nanogen2),
            claim=str(args.claim),
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
                "nanogen2_decision": summary.get("nanogen2_decision"),
                "claim": summary.get("claim"),
                "cpu_threads": threads,
                "elapsed_s": summary.get("elapsed_s"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
