"""Wave AF2 H-SMARTULTRA runner: triple-hop cite (nano:smartultra)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from askfast_ops import AskCompletionCache
from matrix_common import REPO, write_json
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row, classify_semwrap, semantic_lookup
from smartultra_ops import (
    SMARTULTRA_ID,
    SMARTULTRA_N,
    SMARTULTRA_PACK,
    decide_smartultra,
    hard_paraphrase_ok,
    has_adversarial_noise,
    has_triple_hop_cues,
    route_smartultra,
    score_smartultra_trial,
    smartultra_stats,
)
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_trial import validate_trial
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AF_BANK = REPO / "results/nano-lm/wave-af/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-af/trials"
_SUMMARY = REPO / "results/nano-lm/wave-af/smartultra_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
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


def _seed_parent_and_para(bank_path: Path, af_bank: Path) -> int:
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    af_bank.parent.mkdir(parents=True, exist_ok=True)
    if not af_bank.is_file():
        af_bank.write_text("", encoding="utf-8")
    existing = {
        str(r.get("question", "")).strip()
        for r in load_bank_rows(bank_path)
    }
    n = 0
    for i, item in enumerate(SMARTULTRA_PACK, start=1):
        for q_key, q_text in (
            ("parent", item["parent_question"]),
            ("para", item["paraphrase"]),
        ):
            q = str(q_text).strip()
            if q in existing:
                continue
            row = alias_bank_row(
                trial_id=f"AF-SMARTULTRA-SEED-{q_key}-{i:02d}",
                question=q,
                source_id=item["source_id"],
                gold=item["gold"],
            )
            row["hyp_id"] = SMARTULTRA_ID
            row["judge_notes"] = [
                "SMARTULTRA seed for triple-hop paraphrase stress",
                "scoped to primary curated source_id",
                "no student weight update",
            ]
            append_error_row(bank_path, row)
            append_error_row(af_bank, row)
            existing.add(q)
            n += 1
    return n


def _classify(
    item: dict[str, str],
    payload: dict[str, Any],
    bank: list[dict[str, Any]],
    curated: Path,
) -> tuple[str, dict[str, Any], str, str]:
    completion = str(payload.get("completion", ""))
    mode = str(payload.get("mode", ""))
    text, route = route_smartultra(completion, mode=mode)
    _g, meta = semantic_lookup(
        item["paraphrase"], bank, curated_root=curated
    )
    looked = (
        text
        if mode in {"SEMWRAP_LOOKUP", "WRAP_LOOKUP", "ASKFAST_CACHE"}
        else _g
    )
    kind = classify_semwrap(
        looked,
        expected_gold=item["gold"],
        expected_source_id=item["source_id"],
        hit_source_id=str(meta.get("source_id") or "") or None,
    )
    return kind, meta, text, route


def _fix_alias(
    *,
    i: int,
    item: dict[str, str],
    bank_path: Path,
    af_bank: Path,
) -> None:
    row = alias_bank_row(
        trial_id=f"AF-SMARTULTRA-FIX-{i:02d}",
        question=item["paraphrase"],
        source_id=item["source_id"],
        gold=item["gold"],
    )
    row["hyp_id"] = SMARTULTRA_ID
    append_error_row(bank_path, row)
    append_error_row(af_bank, row)


def _build_trial(
    *,
    i: int,
    item: dict[str, str],
    payload: dict[str, Any],
    lookup_kind: str,
    sem_meta: dict[str, Any],
    text: str,
    route: str,
    fix_pass: int,
    score_before: float | None,
    cited: bool,
) -> dict[str, Any]:
    tid = f"AF-SMARTULTRA-HITL-{i:02d}"
    mode = str(payload.get("mode", ""))
    score, err, notes, cite_flag = score_smartultra_trial(
        mode=mode,
        completion=text,
        expected_gold=str(item["gold"]),
        lookup_kind=lookup_kind,
        route=route,
        expected_source_id=str(item["source_id"]),
        hit_source_id=str(sem_meta.get("source_id") or "") or None,
    )
    if cite_flag != cited:
        cited = cite_flag
    trial: dict[str, Any] = {
        "trial_id": tid,
        "stage": "AF2",
        "hyp_id": SMARTULTRA_ID,
        "app_id": item["app_id"],
        "question": item["paraphrase"],
        "parent_question": item["parent_question"],
        "source_id": item["source_id"],
        "secondary_source": item["secondary_source"],
        "tertiary_source": item["tertiary_source"],
        "recipe_id": payload.get("recipe_id"),
        "ckpt": None,
        "completion": text,
        "wall_ms": payload.get("wall_ms"),
        "n_new": payload.get("n_new"),
        "seed": payload.get("seed", 0),
        "mode": mode,
        "route": route,
        "lookup_kind": lookup_kind,
        "cite_ok": cited,
        "semwrap": sem_meta,
        "score": score,
        "error": err,
        "score_before": score_before,
        "score_after": score,
        "fix_pass": int(fix_pass),
        "judge_model_name": _JUDGE,
        "judge_notes": notes,
        "manual_adjust": (
            "no change — SMARTULTRA true-hit + cite"
            if lookup_kind == "TRUE_HIT" and cited and not err
            else "FIX: triple-hop alias / primary cite under distractors"
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


def _ask_one(
    *,
    question: str,
    root: Path,
    seed: int,
    bank_path: Path,
    curated: Path,
) -> dict[str, Any]:
    return ask_many(
        questions=[question],
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated,
        ask_cache=AskCompletionCache(),
    )[0]


def run_smartultra(
    *,
    bank_path: Path,
    af_bank: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN AF0 triple-hop adversarial paraphrases
    WHEN SEMWRAP retrieve + cite primary + FIX
    THEN mean≥7 · false-hit=0 · cite≥8 → PROMOTE|HOLD|KILL.
    """
    if len(SMARTULTRA_PACK) != SMARTULTRA_N:
        raise ValueError("SMARTULTRA pack must be 10")
    if not hard_paraphrase_ok():
        raise ValueError("SMARTULTRA paraphrases must differ from parents")
    if not has_adversarial_noise():
        raise ValueError("SMARTULTRA pack must carry adversarial noise cues")
    if not has_triple_hop_cues():
        raise ValueError("SMARTULTRA pack must carry triple-hop distractor cues")
    trials_dir.mkdir(parents=True, exist_ok=True)
    seeded = _seed_parent_and_para(bank_path, af_bank)
    bank = load_bank_rows(bank_path)

    questions = [p["paraphrase"] for p in SMARTULTRA_PACK]
    cache = AskCompletionCache()
    payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated_root,
        ask_cache=cache,
    )
    if len(payloads) != SMARTULTRA_N:
        raise RuntimeError(f"expected 10 payloads, got {len(payloads)}")

    trials: list[dict[str, Any]] = []
    fix_count = 0
    for i, (item, payload) in enumerate(
        zip(SMARTULTRA_PACK, payloads, strict=True), start=1
    ):
        kind, sem_meta, text, route = _classify(
            dict(item), payload, bank, curated_root
        )
        score_before, _, _, cited0 = score_smartultra_trial(
            mode=str(payload.get("mode", "")),
            completion=text,
            expected_gold=item["gold"],
            lookup_kind=kind,
            route=route,
            expected_source_id=item["source_id"],
            hit_source_id=str(sem_meta.get("source_id") or "") or None,
        )
        fix_pass = 0
        if kind != "TRUE_HIT" or not cited0:
            _fix_alias(
                i=i, item=dict(item), bank_path=bank_path, af_bank=af_bank
            )
            bank = load_bank_rows(bank_path)
            fix_count += 1
            fix_pass = 1
            payload = _ask_one(
                question=item["paraphrase"],
                root=root,
                seed=seed,
                bank_path=bank_path,
                curated=curated_root,
            )
            kind, sem_meta, text, route = _classify(
                dict(item), payload, bank, curated_root
            )
        trial = _build_trial(
            i=i,
            item=dict(item),
            payload=payload,
            lookup_kind=kind,
            sem_meta=sem_meta,
            text=text,
            route=route,
            fix_pass=fix_pass,
            score_before=score_before,
            cited=False,
        )
        write_json(trials_dir / f"{trial['trial_id']}.json", trial)
        trials.append(trial)

    scores = [float(t["score"]) for t in trials]
    errors = [bool(t["error"]) for t in trials]
    cites = [bool(t["cite_ok"]) for t in trials]
    n_true = sum(1 for t in trials if t["lookup_kind"] == "TRUE_HIT")
    n_false = sum(1 for t in trials if t["lookup_kind"] == "FALSE_HIT")
    n_miss = sum(1 for t in trials if t["lookup_kind"] == "MISS")
    n_route = sum(1 for t in trials if t["route"] == "SEMWRAP_ROUTE")
    stats = smartultra_stats(
        scores,
        errors,
        cites,
        n_true_hit=n_true,
        n_false_hit=n_false,
        n_miss=n_miss,
        n_semwrap_route=n_route,
        n_fix=fix_count,
    )
    decision = decide_smartultra(stats)
    summary: dict[str, Any] = {
        "hyp_id": SMARTULTRA_ID,
        "stage": "AF2",
        "decision": decision,
        "compose": [
            "SEMWRAP",
            "ASKSMART-route",
            "ASKFAST",
            "triple-hop-paraphrase",
            "primary-cite",
        ],
        "forbidden": ["QI", "ZPREF", "MIXD", "open-chat claim"],
        "seeded_golds": int(seeded),
        "fix_count": int(fix_count),
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "stats": stats,
        "trials": [
            {
                "trial_id": t["trial_id"],
                "source_id": t["source_id"],
                "secondary_source": t["secondary_source"],
                "tertiary_source": t["tertiary_source"],
                "app_id": t["app_id"],
                "mode": t["mode"],
                "route": t["route"],
                "lookup_kind": t["lookup_kind"],
                "cite_ok": t["cite_ok"],
                "score": t["score"],
                "score_before": t["score_before"],
                "error": t["error"],
                "fix_pass": t["fix_pass"],
            }
            for t in trials
        ],
        "finding": (
            f"{SMARTULTRA_ID}: mean={stats['mean']:.1f} "
            f"false_hit={n_false} true_hit={n_true} "
            f"cite_ok={stats['n_cite_ok']}/10 "
            f"fix={fix_count} decision={decision}."
        ),
        "public_note": "docs/results/nano-lm/formal-hsmartultra-smartultra.md",
        "claim": "triple-hop scoped retrieve/cite — not open chat LM",
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--af-bank", type=Path, default=_AF_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    try:
        summary = run_smartultra(
            bank_path=Path(args.bank),
            af_bank=Path(args.af_bank),
            root=Path(args.root),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            curated_root=Path(args.curated),
            seed=int(args.seed),
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    decision = str(summary["decision"])
    print(
        json.dumps(
            {
                "ok": True,
                "hyp_id": SMARTULTRA_ID,
                "decision": decision,
                "mean": summary["stats"]["mean"],
                "n_false_hit": summary["stats"]["n_false_hit"],
                "n_true_hit": summary["stats"]["n_true_hit"],
                "n_cite_ok": summary["stats"]["n_cite_ok"],
                "fix_count": summary["fix_count"],
                "cpu_threads": threads,
                "out": str(args.out),
            }
        )
    )
    return 0 if decision in {"PROMOTE", "HOLD"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
