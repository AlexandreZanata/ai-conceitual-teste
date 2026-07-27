"""Wave AQ2 H-ADVFP runner (nano:advfp) — adversary SEMWRAP false-hit suite."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping

from advfp_ops import (
    ADVFP_ID,
    ADVFP_N,
    ADVFP_PACK,
    ADVFP_THESIS,
    advfp_stats,
    classify_advfp,
    decide_advfp,
    false_hit_ids,
    pack_ok,
    score_advfp_trial,
)
from aq_session_ops import map_product_mode
from matrix_common import REPO, write_json
from run_z_ask import ask_many
from semwrap_ops import semantic_lookup
from tipd_pair import tune_cpu_threads
from z_trial import validate_trial
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-aq/trials"
_SUMMARY = REPO / "results/nano-lm/wave-aq/advfp_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hadvfp-advfp.md"
_JUDGE = "cursor-composer-frontier-chat"


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


def _ask_text(item: Mapping[str, str]) -> str:
    """Whitespace trap uses a labeled placeholder for decode path only."""
    ask = str(item.get("ask", ""))
    if str(item.get("id")) == "AQ-ADV-19" and not ask.strip():
        return "[ADVFP whitespace-only trap — must not LOOKUP any gold]"
    return ask


def _classify_item(
    item: dict[str, str],
    payload: dict[str, Any],
    bank: list[dict[str, Any]],
    curated: Path,
) -> tuple[str, dict[str, Any]]:
    ask = str(item.get("ask", ""))
    # Classify against the real adversary text (incl. whitespace trap).
    looked, meta = semantic_lookup(ask, bank, curated_root=curated)
    outcome = classify_advfp(item=item, looked_up=looked)
    return outcome, meta


def _build_trial(
    *,
    item: dict[str, str],
    payload: dict[str, Any],
    outcome: str,
    sem_meta: dict[str, Any],
) -> dict[str, Any]:
    tid = str(item["id"])
    mode = str(payload.get("mode", ""))
    kind = str(item["kind"])
    score, err, notes = score_advfp_trial(mode=mode, kind=kind, outcome=outcome)
    trial: dict[str, Any] = {
        "trial_id": tid,
        "stage": "AQ2",
        "hyp_id": ADVFP_ID,
        "pack": "adversary-20",
        "kind": kind,
        "question": item["ask"],
        "source_id": item["source_id"],
        "expect": item["expect"],
        "note": item["note"],
        "recipe_id": payload.get("recipe_id"),
        "ckpt": None,
        "completion": payload.get("completion"),
        "wall_ms": payload.get("wall_ms"),
        "n_new": payload.get("n_new"),
        "seed": payload.get("seed", 0),
        "mode": mode,
        "product_mode": map_product_mode(mode),
        "outcome": outcome,
        "semwrap": sem_meta,
        "score": score,
        "error": err,
        "judge_model_name": _JUDGE,
        "judge_notes": notes,
        "manual_adjust": (
            "no change — ADVFP safe (no false-hit)"
            if outcome == "SAFE"
            else "FIX: SEMWRAP margin/threshold — adversary must not LOOKUP"
        ),
        "gold": "",
        "repaired": "",
        "wrap_id": payload.get("wrap_id"),
        "weight_update": False,
    }
    errs = validate_trial(trial)
    if errs:
        raise ValueError(f"{tid}: " + "; ".join(errs))
    return trial


def _write_public(
    *,
    decision: str,
    stats: dict[str, Any],
    hits: list[str],
) -> None:
    hit_lines = "\n".join(f"- `{h}`" for h in hits) if hits else "- (none)"
    by_kind = stats.get("false_hit_by_kind") or {}
    kind_rows = "\n".join(
        f"| {k} | {by_kind.get(k, 0)} |" for k in ("near-miss", "ood", "trap")
    )
    body = "\n".join(
        [
            f"# H-ADVFP — adversary false-hit suite (**DONE** — {decision})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AQ2 · Session: "
            "`.local/wave-aq/SESSION.md`  ",
            "> Parent: [formal-hparahit-parahit.md](formal-hparahit-parahit.md) · "
            "Pack: AQ0 adversary-20  ",
            "> Module: `nano_lm/src/advfp_ops.py` · "
            "Runner: `npm run nano:advfp`",
            "",
            "## Hypothesis",
            "",
            "Near-miss · OOD · trap asks must **not** retrieve a wrong bank gold "
            "via SEMWRAP (false-hit **0**). Miss/DECODE is acceptable; "
            "silent LOOKUP of a near gold is **KILL**.",
            "",
            "## Gate",
            "",
            "| Metric | Result | Pass bar / rule |",
            "|--------|-------:|-----------------|",
            f"| FALSE_HIT | **{stats['n_false_hit']}**/{stats['n_trials']} | "
            "**0** (any → KILL) |",
            f"| SAFE | **{stats['n_safe']}**/{stats['n_trials']} | — |",
            f"| mean score | **{stats['mean']:.2f}** | informational |",
            f"| Decision | **{decision}** | false-hit=0 → PROMOTE |",
            "",
            "## False-hit by kind",
            "",
            "| kind | false-hits |",
            "|------|----------:|",
            kind_rows,
            "",
            "## False-hit report",
            "",
            hit_lines,
            "",
            "## Finding",
            "",
            "1. Adversary pack run through SEMWRAP with max CPU threads.  ",
            "2. Any LOOKUP / bank gold on an adversary ask counts as FALSE_HIT.  ",
            "3. Product safety metric only — **not** generative IQ / mini-AGI.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:advfp",
            "npm run nano:z:ask -- --semwrap --question \"Who won the 2014 FIFA World Cup final?\"",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-aq/advfp_summary.json`  ",
            "- Trials: `results/nano-lm/wave-aq/trials/AQ-ADV-*.json`  ",
            "- Contract: `nano_lm/tests/test_advfp.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| false-hit 0 on adversary-20 | Silent wrong-gold LOOKUP |",
            "| MISS/DECODE on OOD/trap | Claiming refuse = generative IQ |",
            "| Product safety gate | Wave AR invent |",
            "",
            "Next: **AQ3 H-LATP** — latency p50/p99 for LOOKUP · PEAK · DECODE.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def run_advfp(
    *,
    bank_path: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN AQ0 adversary-20
    WHEN SEMWRAP ask on each adversary text
    THEN false-hit 0 → PROMOTE else KILL.
    """
    if not pack_ok():
        raise ValueError("ADVFP pack invalid (need AQ0 adversary-20)")
    trials_dir.mkdir(parents=True, exist_ok=True)
    bank = load_bank_rows(bank_path)
    questions = [_ask_text(p) for p in ADVFP_PACK]
    payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        semwrap=True,
        bank_path=bank_path,
        curated_root=curated_root,
    )
    if len(payloads) != ADVFP_N:
        raise RuntimeError(f"expected {ADVFP_N} payloads, got {len(payloads)}")

    trials: list[dict[str, Any]] = []
    kind_false: dict[str, int] = {"near-miss": 0, "ood": 0, "trap": 0}
    for item, payload in zip(ADVFP_PACK, payloads, strict=True):
        outcome, sem_meta = _classify_item(
            dict(item), payload, bank, curated_root
        )
        if outcome == "FALSE_HIT":
            kind_false[str(item["kind"])] = kind_false.get(str(item["kind"]), 0) + 1
        trial = _build_trial(
            item=dict(item),
            payload=payload,
            outcome=outcome,
            sem_meta=sem_meta,
        )
        write_json(trials_dir / f"{trial['trial_id']}.json", trial)
        trials.append(trial)

    scores = [float(t["score"]) for t in trials]
    errors = [bool(t["error"]) for t in trials]
    n_false = sum(1 for t in trials if t["outcome"] == "FALSE_HIT")
    n_safe = sum(1 for t in trials if t["outcome"] == "SAFE")
    stats = advfp_stats(
        scores,
        errors,
        n_safe=n_safe,
        n_false_hit=n_false,
        kind_false=kind_false,
    )
    decision = decide_advfp(stats)
    hits = false_hit_ids(trials)
    _write_public(decision=decision, stats=stats, hits=hits)
    summary: dict[str, Any] = {
        "hyp_id": ADVFP_ID,
        "stage": "AQ2",
        "thesis": ADVFP_THESIS,
        "decision": decision,
        "stats": stats,
        "false_hit_ids": hits,
        "compose": ["SEMWRAP", "AQ0-adversary-20"],
        "forbidden": [
            "silent wrong-gold LOOKUP",
            "LOOKUP-as-IQ",
            "open-chat claim",
            "Wave AR invent",
        ],
        "public_note": "docs/results/nano-lm/formal-hadvfp-advfp.md",
        "next": "AQ3 H-LATP",
        "anti_fp": "adversary false-hit 0; generative bar remains AQ6",
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    threads = _hardware()
    try:
        summary = run_advfp(
            bank_path=Path(args.bank),
            root=Path(args.root),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            curated_root=Path(args.curated),
            seed=int(args.seed),
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    decision = str(summary.get("decision", ""))
    ok = decision == "PROMOTE"
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": ADVFP_ID,
                "decision": decision,
                "n_false_hit": summary["stats"]["n_false_hit"],
                "n_safe": summary["stats"]["n_safe"],
                "cpu_threads": threads,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
