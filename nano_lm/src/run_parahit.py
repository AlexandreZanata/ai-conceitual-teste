"""Wave AQ1 H-PARAHIT runner (nano:parahit) — SEMWRAP paraphrase hit-rate."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from aq_session_ops import map_product_mode
from matrix_common import REPO, write_json
from parahit_ops import (
    MIN_HIT_RATE,
    MIN_MEAN,
    PARAHIT_ID,
    PARAHIT_N,
    PARAHIT_PACK,
    PARAHIT_THESIS,
    decide_parahit,
    miss_ids,
    pack_ok,
    parent_already_normalized,
    parahit_stats,
    score_parahit_trial,
)
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row, classify_semwrap, semantic_lookup
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_trial import validate_trial
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AQ_BANK = REPO / "results/nano-lm/wave-aq/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-aq/trials"
_SUMMARY = REPO / "results/nano-lm/wave-aq/parahit_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hparahit-parahit.md"
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


def _seed_parents_only(bank_path: Path, aq_bank: Path) -> int:
    """
    Seed parent known-asks only — never paraphrase text.
    (Avoids memorization theater; SEMWRAP must fuzzy-hit.)
    """
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    aq_bank.parent.mkdir(parents=True, exist_ok=True)
    if not aq_bank.is_file():
        aq_bank.write_text("", encoding="utf-8")
    existing = {str(r.get("question", "")).strip() for r in load_bank_rows(bank_path)}
    n = 0
    for i, item in enumerate(PARAHIT_PACK, start=1):
        parent = str(item["parent_question"]).strip()
        if parent_already_normalized(existing, parent):
            continue
        row = alias_bank_row(
            trial_id=f"AQ-PARAHIT-SEED-PARENT-{i:02d}",
            question=parent,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = PARAHIT_ID
        row["judge_notes"] = [
            "PARAHIT parent seed only — paraphrase not banked",
            "product SEMWRAP measure — not generative IQ",
            "no student weight update",
        ]
        append_error_row(bank_path, row)
        append_error_row(aq_bank, row)
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
    score, err, notes = score_parahit_trial(
        mode=mode,
        completion=text,
        expected_gold=str(item["gold"]),
        lookup_kind=lookup_kind,
    )
    trial: dict[str, Any] = {
        "trial_id": tid,
        "stage": "AQ1",
        "hyp_id": PARAHIT_ID,
        "pack": "paraphrase-20",
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
        "product_mode": map_product_mode(mode),
        "lookup_kind": lookup_kind,
        "semwrap": sem_meta,
        "score": score,
        "error": err,
        "judge_model_name": _JUDGE,
        "judge_notes": notes,
        "manual_adjust": (
            "no change — PARAHIT true-hit"
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
            f"# H-PARAHIT — paraphrase SEMWRAP hit-rate (**DONE** — {decision})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AQ1 · Session: "
            "`.local/wave-aq/SESSION.md`  ",
            "> Parent: [wave-aq-session.md](wave-aq-session.md) (AQ0 packs) · "
            "**H-SEMWRAP**  ",
            "> Module: `nano_lm/src/parahit_ops.py` · "
            "Runner: `npm run nano:parahit`",
            "",
            "## Hypothesis",
            "",
            "Human-written paraphrases of known golds (AQ0 paraphrase-20) "
            "recover via **SEMWRAP** without false-hits — measuring real "
            "paraphrase robustness, **not** LOOKUP-as-IQ and **not** "
            "by banking the paraphrase text first.",
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
            "2. Product path labeled LOOKUP / SEMWRAP_LOOKUP — "
            "**not** generative IQ.  ",
            "3. Next generative claim still gated by **AQ6 H-NANOGEN** "
            "ablated bar.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:parahit",
            "npm run nano:z:ask -- --semwrap --question \"<AQ-PARA paraphrase>\"",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-aq/parahit_summary.json`  ",
            "- Trials: `results/nano-lm/wave-aq/trials/AQ-PARA-*.json`  ",
            "- Contract: `nano_lm/tests/test_parahit.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Product paraphrase hit-rate on SEMWRAP | LOOKUP mean as generative IQ |",
            "| Honest HOLD when hit_rate < bar | Expand bank until HITL memorizes paras |",
            "| false-hit 0 as hard law | Open chat / mini-AGI claim |",
            "",
            "Next: **AQ2 H-ADVFP** — adversary / near-miss / OOD false-hit suite.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def run_parahit(
    *,
    bank_path: Path,
    aq_bank: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN AQ0 paraphrase-20
    WHEN SEMWRAP ask (parents seeded; paras not banked)
    THEN hit_rate≥0.70 ∧ mean≥7 ∧ false-hit=0 → PROMOTE|HOLD|KILL.
    """
    if not pack_ok():
        raise ValueError("PARAHIT pack invalid (need AQ0 paraphrase-20)")
    trials_dir.mkdir(parents=True, exist_ok=True)
    seeded = _seed_parents_only(bank_path, aq_bank)
    bank = load_bank_rows(bank_path)
    questions = [str(p["paraphrase"]) for p in PARAHIT_PACK]
    payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        semwrap=True,
        bank_path=bank_path,
        curated_root=curated_root,
    )
    if len(payloads) != PARAHIT_N:
        raise RuntimeError(f"expected {PARAHIT_N} payloads, got {len(payloads)}")

    trials: list[dict[str, Any]] = []
    for item, payload in zip(PARAHIT_PACK, payloads, strict=True):
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
    stats = parahit_stats(
        scores,
        errors,
        n_true_hit=n_true,
        n_false_hit=n_false,
        n_miss=n_miss,
    )
    decision = decide_parahit(stats)
    misses = miss_ids(trials)
    _write_public(decision=decision, stats=stats, misses=misses)
    summary: dict[str, Any] = {
        "hyp_id": PARAHIT_ID,
        "stage": "AQ1",
        "thesis": PARAHIT_THESIS,
        "decision": decision,
        "stats": stats,
        "miss_ids": misses,
        "seeded_parents": int(seeded),
        "paraphrases_banked": False,
        "compose": ["SEMWRAP", "AQ0-paraphrase-20"],
        "forbidden": [
            "LOOKUP-as-IQ",
            "paraphrase bank expand before measure",
            "open-chat claim",
            "Wave AR invent",
        ],
        "public_note": "docs/results/nano-lm/formal-hparahit-parahit.md",
        "next": "AQ2 H-ADVFP",
        "anti_fp": (
            "product SEMWRAP hit-rate only; generative bar remains AQ6"
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
    ap.add_argument("--aq-bank", type=Path, default=_AQ_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    threads = _hardware()
    try:
        summary = run_parahit(
            bank_path=Path(args.bank),
            aq_bank=Path(args.aq_bank),
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
                "hyp_id": PARAHIT_ID,
                "decision": decision,
                "hit_rate": summary["stats"]["hit_rate"],
                "mean": summary["stats"]["mean"],
                "n_false_hit": summary["stats"]["n_false_hit"],
                "cpu_threads": threads,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
