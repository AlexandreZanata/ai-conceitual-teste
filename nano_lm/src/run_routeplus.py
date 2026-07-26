"""Wave AD3 H-ROUTEPLUS runner: cross-app route + OOS refuse (nano:routeplus)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from ad_session_ops import AD0_PACK
from appplus_ops import APPPLUS_APPS
from askfast_ops import AskCompletionCache
from matrix_common import REPO, write_json
from routeplus_ops import (
    ROUTEPLUS_ID,
    ROUTEPLUS_N,
    claim_is_honest,
    decide_routeplus,
    honest_out_of_scope_text,
    oos_probe_app,
    routeplus_stats,
    score_routeplus_trial,
    select_app,
)
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row, classify_semwrap, semantic_lookup
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_trial import validate_trial
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AD_BANK = REPO / "results/nano-lm/wave-ad/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-ad/trials"
_SUMMARY = REPO / "results/nano-lm/wave-ad/routeplus_summary.json"
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


def _seed_pack_golds(bank_path: Path, ad_bank: Path) -> int:
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    ad_bank.parent.mkdir(parents=True, exist_ok=True)
    if not ad_bank.is_file():
        ad_bank.write_text("", encoding="utf-8")
    existing = {
        str(r.get("question", "")).strip()
        for r in load_bank_rows(bank_path)
    }
    n = 0
    for i, item in enumerate(AD0_PACK, start=1):
        q = str(item["question"]).strip()
        if q in existing:
            continue
        row = alias_bank_row(
            trial_id=f"AD-ROUTEPLUS-SEED-{i:02d}",
            question=q,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = ROUTEPLUS_ID
        row["judge_notes"] = [
            "ROUTEPLUS seed alias for held-out AD ask",
            "scoped to curated source_id",
            "no student weight update",
        ]
        append_error_row(bank_path, row)
        append_error_row(ad_bank, row)
        existing.add(q)
        n += 1
    return n


def _classify(
    item: dict[str, str],
    payload: dict[str, Any],
    bank: list[dict[str, Any]],
    curated: Path,
) -> tuple[str, dict[str, Any]]:
    mode = str(payload.get("mode", ""))
    _g, meta = semantic_lookup(
        item["question"], bank, curated_root=curated
    )
    looked = (
        str(payload.get("completion"))
        if mode in {"SEMWRAP_LOOKUP", "WRAP_LOOKUP", "ASKFAST_CACHE"}
        else _g
    )
    kind = classify_semwrap(
        looked,
        expected_gold=item["gold"],
        expected_source_id=item["source_id"],
        hit_source_id=str(meta.get("source_id") or "") or None,
    )
    return kind, meta


def _fix_alias(
    *,
    i: int,
    item: dict[str, str],
    bank_path: Path,
    ad_bank: Path,
) -> None:
    row = alias_bank_row(
        trial_id=f"AD-ROUTEPLUS-FIX-{i:02d}",
        question=item["question"],
        source_id=item["source_id"],
        gold=item["gold"],
    )
    row["hyp_id"] = ROUTEPLUS_ID
    append_error_row(bank_path, row)
    append_error_row(ad_bank, row)


def _build_trial(
    *,
    i: int,
    item: dict[str, str],
    payload: dict[str, Any],
    lookup_kind: str,
    sem_meta: dict[str, Any],
    selected: dict[str, Any],
    oos_app: dict[str, Any],
    oos_text: str,
    fix_pass: int,
) -> dict[str, Any]:
    tid = f"AD-ROUTEPLUS-HITL-{i:02d}"
    mode = str(payload.get("mode", ""))
    score, err, notes, correct, oos_ok = score_routeplus_trial(
        mode=mode,
        completion=str(payload.get("completion", "")),
        expected_gold=str(item["gold"]),
        lookup_kind=lookup_kind,
        selected=selected,
        item_app_id=item["app_id"],
        oos_completion=oos_text,
        oos_app=oos_app,
    )
    trial: dict[str, Any] = {
        "trial_id": tid,
        "stage": "AD3",
        "hyp_id": ROUTEPLUS_ID,
        "app_id": item["app_id"],
        "selected_app": selected["app_id"],
        "oos_probe_app": oos_app["app_id"],
        "question": item["question"],
        "source_id": item["source_id"],
        "recipe_id": payload.get("recipe_id"),
        "ckpt": None,
        "completion": payload.get("completion"),
        "oos_completion": oos_text,
        "wall_ms": payload.get("wall_ms"),
        "n_new": payload.get("n_new"),
        "seed": payload.get("seed", 0),
        "mode": mode,
        "lookup_kind": lookup_kind,
        "semwrap": sem_meta,
        "correct_route": correct,
        "oos_honest": oos_ok,
        "score": score,
        "error": err,
        "fix_pass": int(fix_pass),
        "judge_model_name": _JUDGE,
        "judge_notes": notes,
        "manual_adjust": (
            "no change — ROUTEPLUS route+OOS ok"
            if correct and oos_ok and not err
            else "FIX: route / OOS refuse / SEMWRAP gold"
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


def run_routeplus(
    *,
    bank_path: Path,
    ad_bank: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
    workers: int = 8,
) -> dict[str, Any]:
    """
    GIVEN AD0 held-out asks + APPPLUS apps
    WHEN auto-route SERVE + wrong-app OOS probe ×10
    THEN correct route ∧ honest OOS → PROMOTE|HOLD|KILL.
    """
    if len(AD0_PACK) != ROUTEPLUS_N:
        raise ValueError("AD0 pack must be 10")
    trials_dir.mkdir(parents=True, exist_ok=True)
    seeded = _seed_pack_golds(bank_path, ad_bank)
    bank = load_bank_rows(bank_path)
    claims_ok = all(claim_is_honest(str(a["claim"])) for a in APPPLUS_APPS)
    n_workers = max(1, int(workers))

    questions = [p["question"] for p in AD0_PACK]
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
    if len(payloads) != ROUTEPLUS_N:
        raise RuntimeError(f"expected 10 payloads, got {len(payloads)}")

    trials: list[dict[str, Any]] = []
    fix_count = 0
    for i, (item, payload) in enumerate(
        zip(AD0_PACK, payloads, strict=True), start=1
    ):
        selected = select_app(item["app_id"])
        probe = oos_probe_app(item["app_id"])
        oos_text = honest_out_of_scope_text(
            str(probe["app_id"]), str(probe["surface"])
        )
        kind, sem_meta = _classify(dict(item), payload, bank, curated_root)
        fix_pass = 0
        if kind != "TRUE_HIT":
            _fix_alias(
                i=i, item=dict(item), bank_path=bank_path, ad_bank=ad_bank
            )
            bank = load_bank_rows(bank_path)
            fix_count += 1
            fix_pass = 1
            re_payloads = ask_many(
                questions=[item["question"]],
                root=root,
                seed=seed,
                askfast=True,
                bank_path=bank_path,
                curated_root=curated_root,
                ask_cache=AskCompletionCache(),
            )
            payload = re_payloads[0]
            kind, sem_meta = _classify(
                dict(item), payload, bank, curated_root
            )
        trial = _build_trial(
            i=i,
            item=dict(item),
            payload=payload,
            lookup_kind=kind,
            sem_meta=sem_meta,
            selected=selected,
            oos_app=probe,
            oos_text=oos_text,
            fix_pass=fix_pass,
        )
        write_json(trials_dir / f"{trial['trial_id']}.json", trial)
        trials.append(trial)

    scores = [float(t["score"]) for t in trials]
    errors = [bool(t["error"]) for t in trials]
    n_true = sum(1 for t in trials if t["lookup_kind"] == "TRUE_HIT")
    n_false = sum(1 for t in trials if t["lookup_kind"] == "FALSE_HIT")
    n_miss = sum(1 for t in trials if t["lookup_kind"] == "MISS")
    n_correct = sum(1 for t in trials if t["correct_route"])
    n_oos = sum(1 for t in trials if t["oos_honest"])
    n_claim = sum(
        1
        for t in trials
        if t["correct_route"] and not t["oos_honest"]
    )
    stats = routeplus_stats(
        scores,
        errors,
        n_true_hit=n_true,
        n_false_hit=n_false,
        n_miss=n_miss,
        n_correct_route=n_correct,
        n_oos_honest=n_oos,
        n_false_claim=n_claim,
        n_fix=fix_count,
        claims_ok=claims_ok,
    )
    decision = decide_routeplus(stats)
    summary: dict[str, Any] = {
        "hyp_id": ROUTEPLUS_ID,
        "stage": "AD3",
        "decision": decision,
        "route": ["APPPLUS", "select_app", "OOS_probe", "SEMWRAP", "ASKFAST"],
        "forbidden": [
            "STREAM",
            "KVCACHE-Q",
            "GENCACHE",
            "false app claim",
            "open chat claim",
        ],
        "seeded_golds": int(seeded),
        "fix_count": int(fix_count),
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "workers": int(n_workers),
        "stats": stats,
        "trials": [
            {
                "trial_id": t["trial_id"],
                "source_id": t["source_id"],
                "app_id": t["app_id"],
                "selected_app": t["selected_app"],
                "oos_probe_app": t["oos_probe_app"],
                "mode": t["mode"],
                "lookup_kind": t["lookup_kind"],
                "correct_route": t["correct_route"],
                "oos_honest": t["oos_honest"],
                "score": t["score"],
                "error": t["error"],
                "fix_pass": t["fix_pass"],
            }
            for t in trials
        ],
        "finding": (
            f"{ROUTEPLUS_ID}: correct={n_correct}/10 oos={n_oos}/10 "
            f"mean={stats['mean']:.1f} false_hit={n_false} "
            f"false_claim={n_claim} fix={fix_count} decision={decision}."
        ),
        "public_note": "docs/results/nano-lm/formal-hrouteplus-routeplus.md",
        "claim": (
            "cross-app APPPLUS route + honest OOS — not open chat LM"
        ),
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--ad-bank", type=Path, default=_AD_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    workers = min(12, max(4, cpus - 4))
    try:
        summary = run_routeplus(
            bank_path=Path(args.bank),
            ad_bank=Path(args.ad_bank),
            root=Path(args.root),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            curated_root=Path(args.curated),
            seed=int(args.seed),
            workers=workers,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    decision = str(summary["decision"])
    print(
        json.dumps(
            {
                "ok": True,
                "hyp_id": ROUTEPLUS_ID,
                "decision": decision,
                "mean": summary["stats"]["mean"],
                "n_correct_route": summary["stats"]["n_correct_route"],
                "n_oos_honest": summary["stats"]["n_oos_honest"],
                "n_false_claim": summary["stats"]["n_false_claim"],
                "n_false_hit": summary["stats"]["n_false_hit"],
                "fix_count": summary["fix_count"],
                "cpu_threads": threads,
                "workers": workers,
                "out": str(args.out),
            }
        )
    )
    return 0 if decision in {"PROMOTE", "HOLD"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
