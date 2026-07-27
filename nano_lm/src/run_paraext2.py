"""Wave AS4 H-PARAEXT2 runner — external paraphrase after SEMFIX."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from as_session_ops import map_as_product_mode
from matrix_common import REPO, write_json
from paraext2_ops import (
    MIN_HIT_RATE,
    MIN_MEAN,
    PARAEXT2_ID,
    PARAEXT2_N,
    PARAEXT2_PACK,
    PARAEXT2_THESIS,
    decide_paraext2,
    miss_ids,
    pack_ok,
    paraext2_stats,
    parent_already_normalized,
    score_paraext2_trial,
)
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row, classify_semwrap, semantic_lookup
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_trial import validate_trial
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AS_BANK = REPO / "results/nano-lm/wave-as/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-as/trials"
_SUMMARY = REPO / "results/nano-lm/wave-as/paraext2_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hparaext2-paraext2.md"
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


def _seed_parents_only(bank_path: Path, as_bank: Path) -> int:
    """Seed parent known-asks only — never paraphrase text."""
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    as_bank.parent.mkdir(parents=True, exist_ok=True)
    if not as_bank.is_file():
        as_bank.write_text("", encoding="utf-8")
    existing = {
        str(r.get("question", "")).strip() for r in load_bank_rows(bank_path)
    }
    n = 0
    for i, item in enumerate(PARAEXT2_PACK, start=1):
        parent = str(item["parent_question"]).strip()
        if parent_already_normalized(existing, parent):
            continue
        row = alias_bank_row(
            trial_id=f"AS-PARAEXT2-SEED-PARENT-{i:02d}",
            question=parent,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = PARAEXT2_ID
        row["judge_notes"] = [
            "PARAEXT2 parent seed only — paraphrase not banked",
            "product SEMWRAP measure — not generative IQ",
            "no student weight update",
        ]
        append_error_row(bank_path, row)
        append_error_row(as_bank, row)
        existing.add(parent)
        n += 1
    return n


def _classify(
    item: dict[str, str],
    payload: dict[str, Any],
    bank: list[dict[str, Any]],
    curated: Path,
) -> tuple[str, dict[str, Any], str]:
    completion = str(payload.get("completion", ""))
    mode = str(payload.get("mode", ""))
    _g, meta = semantic_lookup(
        item["paraphrase"], bank, curated_root=curated
    )
    looked = (
        completion
        if mode in {"SEMWRAP_LOOKUP", "WRAP_LOOKUP"}
        else _g
    )
    kind = classify_semwrap(
        looked,
        expected_gold=item["gold"],
        expected_source_id=item["source_id"],
        hit_source_id=str(meta.get("source_id") or "") or None,
    )
    return kind, meta, completion


def _build_trial(
    *,
    item: dict[str, str],
    payload: dict[str, Any],
    lookup_kind: str,
    sem_meta: dict[str, Any],
    text: str,
) -> dict[str, Any]:
    tid = str(item["id"])
    mode = str(payload.get("mode", ""))
    score, err, notes = score_paraext2_trial(
        mode=mode,
        completion=text,
        expected_gold=str(item["gold"]),
        lookup_kind=lookup_kind,
    )
    trial: dict[str, Any] = {
        "trial_id": tid,
        "stage": "AS4",
        "hyp_id": PARAEXT2_ID,
        "pack": "paraext2-20",
        "question": item["paraphrase"],
        "parent_question": item["parent_question"],
        "source_id": item["source_id"],
        "recipe_id": payload.get("recipe_id"),
        "ckpt": None,
        "completion": text,
        "wall_ms": payload.get("wall_ms"),
        "n_new": payload.get("n_new"),
        "seed": payload.get("seed", 0),
        "mode": mode,
        "product_mode": map_as_product_mode(mode),
        "lookup_kind": lookup_kind,
        "semwrap": sem_meta,
        "score": score,
        "error": err,
        "judge_model_name": _JUDGE,
        "judge_notes": notes,
        "manual_adjust": (
            "no change — PARAEXT2 true-hit"
            if lookup_kind == "TRUE_HIT"
            else "report miss — no paraphrase bank expand (anti theater)"
        ),
        "gold": str(item["gold"]).strip(),
        "repaired": str(item["gold"]).strip(),
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
    misses: list[str],
) -> None:
    miss_lines = (
        "\n".join(f"- `{m}`" for m in misses) if misses else "- (none)"
    )
    body = "\n".join(
        [
            f"# H-PARAEXT2 — external paraphrase after SEMFIX "
            f"(**DONE** — {decision})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AS4 · Session: "
            "`.local/wave-as/SESSION.md`  ",
            "> Parent: [formal-hadvsafe-advsafe.md](formal-hadvsafe-advsafe.md) "
            "· Pack: AS0 PARAEXT2-20  ",
            "> Module: `nano_lm/src/paraext2_ops.py` · "
            "Runner: `npm run nano:paraext2`",
            "",
            "## Hypothesis",
            "",
            "Fresh AS0 PARAEXT2 paraphrases (≠ AQ-PARA / AR-EXT / AP-HITL) "
            "recover via **SEMWRAP** after SEMFIX without false-hits — "
            "real paraphrase robustness, **not** bank-stuffed theater and "
            "**not** generative IQ.",
            "",
            "## Gate",
            "",
            "| Metric | Result | Pass bar / rule |",
            "|--------|-------:|-----------------|",
            f"| hit_rate (TRUE_HIT) | **{stats['hit_rate']}** "
            f"({stats['n_true_hit']}/{stats['n_trials']}) | "
            f"≥ **{MIN_HIT_RATE}** |",
            f"| mean score | **{stats['mean']:.2f}** | ≥ **{MIN_MEAN}** |",
            f"| FALSE_HIT | **{stats['n_false_hit']}**/{stats['n_trials']} | "
            "**0** (any → KILL) |",
            f"| MISS | **{stats['n_miss']}**/{stats['n_trials']} | report |",
            f"| Decision | **{decision}** | hit∧mean ∧ false-hit=0 |",
            "",
            "## Miss report",
            "",
            miss_lines,
            "",
            "## Finding",
            "",
            "1. Parents seeded only when missing; paraphrases **not** "
            "pre-banked (anti memorization theater).  ",
            "2. Pack disjoint from AQ-PARA · AR-EXT · AP-HITL exact text.  ",
            "3. Product path labeled LOOKUP / SEMWRAP_LOOKUP — "
            "**not** generative IQ.  ",
            "4. AR H-PARAEXT HOLD (0.65) stays locked; AS4 is a fresh pack.  ",
            "5. Generative claim still gated by **AS7 H-NANOGEN3**.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:paraext2",
            "npm run nano:z:ask -- --semwrap --question "
            '"Para-ext2: BIP-39 checksum length — write CS in terms of ENT."',
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-as/paraext2_summary.json`  ",
            "- Trials: `results/nano-lm/wave-as/trials/AS-EXT2-*.json`  ",
            "- Contract: `nano_lm/tests/test_paraext2.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| External paraphrase hit-rate on SEMWRAP | LOOKUP-as-IQ |",
            "| Honest HOLD when hit_rate < bar | Bank stuffing |",
            "| false-hit 0 as hard law | Rewrite AR PARAEXT |",
            "",
            "Next: **AS5 H-METRICS** — latency p50/p99 + KB coverage refresh.",
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
            f"# Wave AS session checklist (**OPEN** · AS4 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AS **OPEN**).  ",
            "> Parent: AR COMPLETE + FROZEN · Ship: **AF packaged stack + "
            "AQ product layer — not open chat LM** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AS4 — H-PARAEXT2 ({status})** · Next: **AS5 H-METRICS**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AS OPEN** |",
            f"| hit_rate | **{stats.get('hit_rate')}** "
            f"({stats.get('n_true_hit')}/{stats.get('n_trials')}) |",
            f"| FALSE_HIT | **{stats.get('n_false_hit')}** |",
            f"| MISS | **{stats.get('n_miss')}** |",
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
            f"| AS4 | H-PARAEXT2 | **{status}** |",
            "| AS5 | H-METRICS | **NEXT** |",
            "| AS6 | H-SHIPUI | pending |",
            "| AS7 | H-NANOGEN3 | pending |",
            "| AS8 | AS-DUAL-HITL | pending |",
            "| AS9 | AS-REPORT | pending |",
            "| AS10 | AS-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def run_paraext2(
    *,
    bank_path: Path,
    as_bank: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN AS0 PARAEXT2-20
    WHEN SEMWRAP ask (parents seeded; paras not banked)
    THEN hit_rate≥0.70 ∧ mean≥7 ∧ false-hit=0 → PROMOTE|HOLD|KILL.
    """
    if not pack_ok():
        raise ValueError("PARAEXT2 pack invalid (need AS0 PARAEXT2-20)")
    trials_dir.mkdir(parents=True, exist_ok=True)
    seeded = _seed_parents_only(bank_path, as_bank)
    bank = load_bank_rows(bank_path)
    questions = [str(p["paraphrase"]) for p in PARAEXT2_PACK]
    payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        semwrap=True,
        bank_path=bank_path,
        curated_root=curated_root,
    )
    if len(payloads) != PARAEXT2_N:
        raise RuntimeError(
            f"expected {PARAEXT2_N} payloads, got {len(payloads)}"
        )

    trials: list[dict[str, Any]] = []
    for item, payload in zip(PARAEXT2_PACK, payloads, strict=True):
        kind, sem_meta, text = _classify(
            dict(item), payload, bank, curated_root
        )
        trial = _build_trial(
            item=dict(item),
            payload=payload,
            lookup_kind=kind,
            sem_meta=sem_meta,
            text=text,
        )
        write_json(trials_dir / f"{trial['trial_id']}.json", trial)
        trials.append(trial)

    scores = [float(t["score"]) for t in trials]
    errors = [bool(t["error"]) for t in trials]
    n_true = sum(1 for t in trials if t["lookup_kind"] == "TRUE_HIT")
    n_false = sum(1 for t in trials if t["lookup_kind"] == "FALSE_HIT")
    n_miss = sum(1 for t in trials if t["lookup_kind"] == "MISS")
    stats = paraext2_stats(
        scores,
        errors,
        n_true_hit=n_true,
        n_false_hit=n_false,
        n_miss=n_miss,
    )
    decision = decide_paraext2(stats)
    misses = miss_ids(trials)
    _write_public(decision=decision, stats=stats, misses=misses)
    _update_local_session(decision, stats)
    summary: dict[str, Any] = {
        "hyp_id": PARAEXT2_ID,
        "stage": "AS4",
        "thesis": PARAEXT2_THESIS,
        "decision": decision,
        "stats": stats,
        "miss_ids": misses,
        "seeded_parents": int(seeded),
        "paraphrases_banked": False,
        "compose": ["SEMWRAP", "SEMFIX", "AS0-PARAEXT2-20"],
        "forbidden": [
            "LOOKUP-as-IQ",
            "bank stuffing",
            "paraphrase bank expand before measure",
            "rewrite AR PARAEXT",
            "open-chat claim",
            "Wave AT invent",
        ],
        "public_note": "docs/results/nano-lm/formal-hparaext2-paraext2.md",
        "next": "AS5 H-METRICS",
        "anti_fp": (
            "product SEMWRAP hit-rate only; generative bar remains AS7"
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
    ap.add_argument("--as-bank", type=Path, default=_AS_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        summary = run_paraext2(
            bank_path=Path(args.bank),
            as_bank=Path(args.as_bank),
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
    ok = decision in {"PROMOTE", "HOLD"}
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": PARAEXT2_ID,
                "decision": decision,
                "hit_rate": summary["stats"]["hit_rate"],
                "mean": summary["stats"]["mean"],
                "n_false_hit": summary["stats"]["n_false_hit"],
                "miss_ids": summary.get("miss_ids"),
                "cpu_threads": threads,
                "workers": workers,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
