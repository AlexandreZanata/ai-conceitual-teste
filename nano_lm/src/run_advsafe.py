"""Wave AS3 H-ADVSAFE runner — adversary regression after SEMFIX."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping

from advsafe_ops import (
    ADVSAFE_ID,
    ADVSAFE_N,
    ADVSAFE_PACK,
    ADVSAFE_THESIS,
    SAFE_NOTE,
    advsafe_stats,
    classify_advsafe,
    decide_advsafe,
    false_hit_ids,
    pack_ok,
    score_advsafe_trial,
)
from as_session_ops import map_as_product_mode
from matrix_common import REPO, write_json
from run_z_ask import ask_many
from semwrap_ops import semantic_lookup
from tipd_pair import tune_cpu_threads
from z_trial import validate_trial
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-as/trials"
_SUMMARY = REPO / "results/nano-lm/wave-as/advsafe_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hadvsafe-advsafe.md"
_LOCAL_SESSION = REPO / ".local/wave-as/SESSION.md"
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


def _hardware() -> tuple[int, int]:
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 2))
    workers = min(14, max(4, cpus - 2))
    return threads, workers


def _ask_text(item: Mapping[str, str]) -> str:
    ask = str(item.get("ask", ""))
    if str(item.get("id")) == "AS-ADVSAFE-19" and not ask.strip():
        return "[ADVSAFE whitespace-only trap — must not LOOKUP any gold]"
    return ask


def _classify_item(
    item: dict[str, str],
    bank: list[dict[str, Any]],
    curated: Path,
) -> tuple[str, dict[str, Any]]:
    ask = str(item.get("ask", ""))
    looked, meta = semantic_lookup(ask, bank, curated_root=curated)
    outcome = classify_advsafe(item=item, looked_up=looked)
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
    score, err, notes = score_advsafe_trial(
        mode=mode, kind=kind, outcome=outcome
    )
    trial: dict[str, Any] = {
        "trial_id": tid,
        "stage": "AS3",
        "hyp_id": ADVSAFE_ID,
        "pack": "advsafe-20",
        "kind": kind,
        "parent_id": item.get("parent_id"),
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
        "product_mode": map_as_product_mode(mode),
        "outcome": outcome,
        "semwrap": sem_meta,
        "score": score,
        "error": err,
        "judge_model_name": _JUDGE,
        "judge_notes": notes,
        "safe_note": SAFE_NOTE,
        "mean_is_quality": False,
        "manual_adjust": (
            "no change — ADVSAFE safe (no false-hit)"
            if outcome == "SAFE"
            else "FIX: SEMWRAP contrast/margin — adversary must not LOOKUP"
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
            f"# H-ADVSAFE — adversary regression (**DONE** — {decision})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AS3 · Session: "
            "`.local/wave-as/SESSION.md`  ",
            "> Parent: [formal-hsemfix-semfix.md](formal-hsemfix-semfix.md) · "
            "Pack: AS0 ADVSAFE-20  ",
            "> Module: `nano_lm/src/advsafe_ops.py` · "
            "Runner: `npm run nano:advsafe`",
            "",
            "## Hypothesis",
            "",
            "Near-miss · OOD · trap asks (AS0 ADVSAFE citing AR-ADVREG-01/05) "
            "must **not** retrieve a wrong bank gold via SEMWRAP after "
            "SEMFIX (false-hit **0**). SAFE / mean score is **not** answer "
            "quality.",
            "",
            "## Gate",
            "",
            "| Metric | Result | Pass bar / rule |",
            "|--------|-------:|-----------------|",
            f"| FALSE_HIT | **{stats['n_false_hit']}**/{stats['n_trials']} | "
            "**0** (any → KILL) |",
            f"| SAFE | **{stats['n_safe']}**/{stats['n_trials']} | — |",
            f"| mean score | **{stats['mean']:.2f}** | informational only |",
            f"| mean_is_quality | **{stats['mean_is_quality']}** | "
            "must be False |",
            f"| Parents cited | **{', '.join(stats.get('cited_parents', []))}** | "
            "AR-ADVREG-01/05 |",
            f"| Decision | **{decision}** | false-hit=0 → PROMOTE |",
            "",
            "## SAFE ≠ quality",
            "",
            SAFE_NOTE,
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
            "1. AS0 ADVSAFE-20 through SEMWRAP under max safe CPU "
            "(`cpus-2`).  ",
            "2. SEMFIX polarity/negation/REST contrast keeps AR-ADVREG-01/05 "
            "class + siblings FH 0.  ",
            "3. Any LOOKUP / bank gold on adversary ask → FALSE_HIT.  ",
            "4. SAFE/mean documented as **not** answer quality / IQ.  ",
            "5. Product safety only — generative bar remains **AS7**.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:advsafe",
            "npm run nano:z:ask -- --semwrap --question "
            '"ADVSAFE REST: GET path for fee estimates (not /rest/tx/<hash>)."',
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-as/advsafe_summary.json`  ",
            "- Trials: `results/nano-lm/wave-as/trials/AS-ADVSAFE-*.json`  ",
            "- Contract: `nano_lm/tests/test_advsafe.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| false-hit 0 on ADVSAFE-20 | Silent wrong-gold LOOKUP |",
            "| SAFE≠quality documented | SAFE-mean sold as IQ |",
            "| Product safety after SEMFIX | mini-AGI / Wave AT invent |",
            "",
            "Next: **AS4 H-PARAEXT2** — external paraphrase hit ≥ **0.70**.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _update_local_session(decision: str, stats: dict[str, Any]) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    status = f"DONE — {decision}"
    body = "\n".join(
        [
            f"# Wave AS session checklist (**OPEN** · AS3 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AS **OPEN**).  ",
            "> Parent: AR COMPLETE + FROZEN · Ship: **AF packaged stack + "
            "AQ product layer — not open chat LM** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AS3 — H-ADVSAFE ({status})** · Next: **AS4 H-PARAEXT2**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AS OPEN** |",
            f"| FALSE_HIT | **{stats.get('n_false_hit')}**/"
            f"{stats.get('n_trials')} |",
            f"| SAFE | **{stats.get('n_safe')}** |",
            f"| mean (≠ quality) | **{stats.get('mean')}** |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AS0 | SESSION | **DONE — PROMOTE** |",
            "| AS1 | H-ASKABSTAIN | **DONE — PROMOTE** |",
            "| AS2 | H-SEMFIX | **DONE — PROMOTE** |",
            f"| AS3 | H-ADVSAFE | **{status}** |",
            "| AS4 | H-PARAEXT2 | **NEXT** |",
            "| AS5 | H-METRICS | pending |",
            "| AS6 | H-SHIPUI | pending |",
            "| AS7 | H-NANOGEN3 | pending |",
            "| AS8 | AS-DUAL-HITL | pending |",
            "| AS9 | AS-REPORT | pending |",
            "| AS10 | AS-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def run_advsafe(
    *,
    bank_path: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN AS0 ADVSAFE-20
    WHEN SEMWRAP ask on each adversary text
    THEN false-hit 0 + SAFE≠quality → PROMOTE else KILL.
    """
    if not pack_ok():
        raise ValueError("ADVSAFE pack invalid (need AS0 ADVSAFE-20)")
    trials_dir.mkdir(parents=True, exist_ok=True)
    bank = load_bank_rows(bank_path)
    questions = [_ask_text(p) for p in ADVSAFE_PACK]
    payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        semwrap=True,
        bank_path=bank_path,
        curated_root=curated_root,
    )
    if len(payloads) != ADVSAFE_N:
        raise RuntimeError(
            f"expected {ADVSAFE_N} payloads, got {len(payloads)}"
        )

    trials: list[dict[str, Any]] = []
    kind_false: dict[str, int] = {"near-miss": 0, "ood": 0, "trap": 0}
    parents: list[str] = []
    for item, payload in zip(ADVSAFE_PACK, payloads, strict=True):
        outcome, sem_meta = _classify_item(dict(item), bank, curated_root)
        if outcome == "FALSE_HIT":
            kind_false[str(item["kind"])] = (
                kind_false.get(str(item["kind"]), 0) + 1
            )
        pid = str(item.get("parent_id") or "")
        if pid:
            parents.append(pid)
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
    stats = advsafe_stats(
        scores,
        errors,
        n_safe=n_safe,
        n_false_hit=n_false,
        kind_false=kind_false,
        parents_cited=parents,
    )
    decision = decide_advsafe(stats)
    hits = false_hit_ids(trials)
    _write_public(decision=decision, stats=stats, hits=hits)
    _update_local_session(decision, stats)
    summary: dict[str, Any] = {
        "hyp_id": ADVSAFE_ID,
        "stage": "AS3",
        "thesis": ADVSAFE_THESIS,
        "decision": decision,
        "stats": stats,
        "false_hit_ids": hits,
        "safe_note": SAFE_NOTE,
        "compose": ["SEMWRAP", "SEMFIX", "AS0-ADVSAFE-20"],
        "forbidden": [
            "silent wrong-gold LOOKUP",
            "SAFE-mean-as-quality",
            "LOOKUP-as-IQ",
            "open-chat claim",
            "Wave AT invent",
        ],
        "public_note": "docs/results/nano-lm/formal-hadvsafe-advsafe.md",
        "next": "AS4 H-PARAEXT2",
        "anti_fp": (
            "adversary false-hit 0; SAFE≠quality; generative bar = AS7"
        ),
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
    threads, workers = _hardware()
    try:
        summary = run_advsafe(
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
                "hyp_id": ADVSAFE_ID,
                "decision": decision,
                "n_false_hit": summary["stats"]["n_false_hit"],
                "n_safe": summary["stats"]["n_safe"],
                "mean_is_quality": summary["stats"]["mean_is_quality"],
                "cpu_threads": threads,
                "workers": workers,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
