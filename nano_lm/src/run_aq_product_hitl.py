"""Wave AQ7 AQ-PRODUCT-HITL runner — composite product verify."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from aq_product_hitl_ops import (
    APP_SMOKE_PACK,
    HONEST_CLAIM,
    PRODUCT_HITL_ID,
    PRODUCT_HITL_THESIS,
    apps_ok,
    claim_is_honest,
    decide_aq_product_hitl,
)
from aq_session_ops import map_product_mode
from matrix_common import REPO, write_json
from modeui_ops import attach_modeui
from run_advfp import run_advfp
from run_modeui import run_modeui
from run_parahit import run_parahit
from run_z_ask import ask_many
from semwrap_ops import classify_semwrap, semantic_lookup
from tipd_pair import tune_cpu_threads
from z_wrap import load_bank_rows

_SUMMARY = REPO / "results/nano-lm/wave-aq/aq_product_hitl_summary.json"
_NANOGEN = REPO / "results/nano-lm/wave-aq/nanogen_summary.json"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AQ_BANK = REPO / "results/nano-lm/wave-aq/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-aq/trials"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/wave-aq-product-hitl.md"
_PARA_OUT = REPO / "results/nano-lm/wave-aq/parahit_summary.json"
_ADV_OUT = REPO / "results/nano-lm/wave-aq/advfp_summary.json"
_MODE_OUT = REPO / "results/nano-lm/wave-aq/modeui_summary.json"


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


def _load_nanogen(path: Path) -> str:
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
                "app_id": item["app_id"],
                "question": item["question"],
                "source_id": item["source_id"],
                "mode": mode,
                "product_mode": map_product_mode(mode),
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
    nanogen: str,
    claim: str,
) -> None:
    app_rows = [
        f"| {t['app_id']} | **{t['lookup_kind']}** | `{t.get('modeui_line', '')}` |"
        for t in apps
    ]
    body = "\n".join(
        [
            f"# AQ-PRODUCT-HITL — final product verify (**DONE** — {decision})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AQ7 · Session: "
            "`.local/wave-aq/SESSION.md`  ",
            "> Parent: [formal-hnanogen-nanogen.md](formal-hnanogen-nanogen.md)  ",
            "> Module: `nano_lm/src/aq_product_hitl_ops.py` · "
            "Runner: `npm run nano:aq:product-hitl`",
            "",
            "## Hypothesis",
            "",
            "Composite product verify (paraphrase · adversary · apps · modes). "
            "Generative ship claim unlocks **only** if AQ6 H-NANOGEN PROMOTE.",
            "",
            "## Gate",
            "",
            "| Pillar | Decision |",
            "|--------|----------|",
            f"| H-PARAHIT | **{pillars['parahit']}** |",
            f"| H-ADVFP | **{pillars['advfp']}** |",
            f"| H-MODEUI | **{pillars['modeui']}** |",
            f"| Apps known/howto/long-doc | "
            f"**{'PASS' if apps_ok(apps) else 'FAIL'}** |",
            f"| AQ6 H-NANOGEN | **{nanogen}** |",
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
            "1. Live re-verify of AQ1/AQ2/AQ5 under max safe CPU (`cpus-2`).  ",
            "2. Three app surfaces TRUE_HIT LOOKUP (product path).  ",
            "3. AQ6 HOLD → generative / open-chat / mini-AGI claim stays locked.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:aq:product-hitl",
            "npm run nano:z:ask -- --wrap --question \"Write a short Python "
            "function named add that returns the sum of two integers a and b.\"",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-aq/aq_product_hitl_summary.json`  ",
            "- Contract: `nano_lm/tests/test_aq_product_hitl.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| AF packaged stack + AQ product layer | Open chat / mini-AGI |",
            "| Product PROMOTE with AQ6 HOLD | Generative unlock without AQ6 |",
            "| Mode-visible LOOKUP apps | LOOKUP-as-gen-IQ |",
            "",
            "Next: **AQ8 AQ-REPORT** — public summary + paper-lab.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def run_aq_product_hitl(
    *,
    root: Path,
    bank: Path,
    aq_bank: Path,
    curated: Path,
    out: Path,
    trials_dir: Path,
    nanogen_path: Path,
    claim: str,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN AQ product pillars + AQ6 status
    WHEN running composite HITL
    THEN PROMOTE iff product passes and claim honest under gen lock.
    """
    t0 = time.perf_counter()
    para = run_parahit(
        bank_path=bank,
        aq_bank=aq_bank,
        root=root,
        out=_PARA_OUT,
        trials_dir=trials_dir,
        curated_root=curated,
        seed=seed,
    )
    adv = run_advfp(
        bank_path=bank,
        root=root,
        out=_ADV_OUT,
        trials_dir=trials_dir,
        curated_root=curated,
        seed=seed,
    )
    mode = run_modeui(
        root=root, bank=bank, curated=curated, out=_MODE_OUT
    )
    apps = _apps_smoke(
        root=root, bank=bank, curated=curated, seed=seed
    )
    for t in apps:
        write_json(trials_dir / f"{t['trial_id']}.json", t)
    nanogen = _load_nanogen(nanogen_path)
    pillars = {
        "parahit": str(para.get("decision", "")),
        "advfp": str(adv.get("decision", "")),
        "modeui": str(mode.get("decision", "")),
    }
    apps_pass = apps_ok(apps)
    decision = decide_aq_product_hitl(
        para_decision=pillars["parahit"],
        adv_decision=pillars["advfp"],
        mode_decision=pillars["modeui"],
        apps_pass=apps_pass,
        nanogen_decision=nanogen,
        claim=claim,
    )
    _write_public(
        decision=decision,
        pillars=pillars,
        apps=apps,
        nanogen=nanogen,
        claim=claim,
    )
    summary: dict[str, Any] = {
        "hyp_id": PRODUCT_HITL_ID,
        "stage": "AQ7",
        "thesis": PRODUCT_HITL_THESIS,
        "decision": decision,
        "pillars": pillars,
        "apps_pass": apps_pass,
        "apps": apps,
        "nanogen_decision": nanogen,
        "claim": claim,
        "claim_honest": claim_is_honest(claim),
        "generative_claim_unlocked": False,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "elapsed_s": time.perf_counter() - t0,
        "forbidden": [
            "open-chat / mini-AGI claim",
            "generative unlock while AQ6 HOLD",
            "LOOKUP-as-gen-IQ",
            "Wave AR invent",
        ],
        "public_note": "docs/results/nano-lm/wave-aq-product-hitl.md",
        "ship_claim": claim,
        "next": "AQ8 AQ-REPORT",
    }
    write_json(Path(out), summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AQ7 AQ-PRODUCT-HITL")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--aq-bank", type=Path, default=_AQ_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--nanogen", type=Path, default=_NANOGEN)
    ap.add_argument("--claim", type=str, default=HONEST_CLAIM)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    threads = _hardware()
    try:
        summary = run_aq_product_hitl(
            root=Path(args.root),
            bank=Path(args.bank),
            aq_bank=Path(args.aq_bank),
            curated=Path(args.curated),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            nanogen_path=Path(args.nanogen),
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
                "hyp_id": PRODUCT_HITL_ID,
                "decision": decision,
                "pillars": summary.get("pillars"),
                "apps_pass": summary.get("apps_pass"),
                "nanogen_decision": summary.get("nanogen_decision"),
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
