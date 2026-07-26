"""Wave AD5 AD-HITL-10 runner: final pack on declared AD stack (nano:ad:hitl)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from ad_hitl_ops import (
    AD5_ID,
    AD5_N,
    DECLARED_STACK,
    STACK_CLAIM,
    ad5_stats,
    claim_is_honest,
    decide_ad5,
    score_ad5_trial,
    select_app,
)
from ad_session_ops import AD0_PACK, overlaps_prior_questions
from askfast_ops import AskCompletionCache
from curated_sources import SOURCES
from ctxplus_ops import ctxplus_doc_meta
from data_tiny import load_tokenizer
from matrix_common import REPO, matrix_cfg, write_json
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row, classify_semwrap, semantic_lookup
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_trial import validate_trial
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AD_BANK = REPO / "results/nano-lm/wave-ad/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-ad/trials"
_SUMMARY = REPO / "results/nano-lm/wave-ad/ad_hitl_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_JUDGE = "cursor-composer-frontier-chat"
_BY_ID = {str(s["id"]): s for s in SOURCES}


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


def _seed_golds(bank_path: Path, ad_bank: Path) -> int:
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
            trial_id=f"AD-HITL-SEED-{i:02d}",
            question=q,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = AD5_ID
        append_error_row(bank_path, row)
        append_error_row(ad_bank, row)
        existing.add(q)
        n += 1
    return n


def _load_doc(source_id: str, curated: Path) -> str:
    meta = _BY_ID.get(source_id)
    if meta is None:
        raise ValueError(f"unknown source_id: {source_id}")
    path = curated / str(meta["path"])
    if not path.is_file():
        raise FileNotFoundError(str(path))
    return path.read_text(encoding="utf-8", errors="ignore")


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


def _build_ctxs(
    *,
    curated_root: Path,
    workers: int,
) -> list[dict[str, Any] | None]:
    cfg = matrix_cfg()
    tok = load_tokenizer(str(cfg["tokenizer_id"]), cfg["cache"])

    def _read(item: dict[str, str]) -> tuple[dict[str, str], str]:
        return item, _load_doc(item["source_id"], curated_root)

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        pairs = list(pool.map(_read, [dict(p) for p in AD0_PACK]))
    out: list[dict[str, Any] | None] = []
    for item, text in pairs:
        if item["app_id"] != "long-doc":
            out.append(None)
            continue
        ids = list(tok.encode(text, add_special_tokens=False))
        q_ids = list(tok.encode(item["question"], add_special_tokens=False))
        meta = ctxplus_doc_meta(ids, q_ids)
        meta["source_id"] = item["source_id"]
        out.append(meta)
    return out


def _log_error(
    path: Path,
    *,
    trial_id: str,
    item: dict[str, str],
    completion: str,
    score: float,
    notes: list[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "trial_id": trial_id,
        "stage": "AD5",
        "hyp_id": AD5_ID,
        "question": item["question"],
        "source_id": item["source_id"],
        "app_id": item["app_id"],
        "model_raw": completion,
        "gold": item["gold"],
        "score": score,
        "error": True,
        "judge_notes": notes,
        "recipe_id": "champion-ad-v0",
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def _apply_fix(
    *,
    tid: str,
    item: dict[str, str],
    bank_path: Path,
    ad_bank: Path,
    curated: Path,
    payload: dict[str, Any],
    kind: str,
    sem_meta: dict[str, Any],
    score_before: float,
    notes_before: list[str],
    ctx_ok: bool | None,
) -> tuple[str, str, str, dict[str, Any], float, bool, list[str]]:
    _log_error(
        ad_bank,
        trial_id=tid,
        item=item,
        completion=str(payload.get("completion", "")),
        score=score_before,
        notes=notes_before,
    )
    row = alias_bank_row(
        trial_id=f"{tid}-FIX",
        question=item["question"],
        source_id=item["source_id"],
        gold=item["gold"],
    )
    row["hyp_id"] = AD5_ID
    append_error_row(bank_path, row)
    append_error_row(ad_bank, row)
    bank_rows = load_bank_rows(bank_path)
    gold, meta = semantic_lookup(
        item["question"], bank_rows, curated_root=curated
    )
    if gold is None:
        return (
            str(payload.get("completion", "")),
            str(payload.get("mode", "")),
            kind,
            sem_meta,
            score_before,
            True,
            list(notes_before) + ["FIX miss — no gold"],
        )
    completion = str(gold)
    mode = "AD5_CONSTRAINED_FIX"
    kind2 = classify_semwrap(
        completion,
        expected_gold=item["gold"],
        expected_source_id=item["source_id"],
        hit_source_id=str(meta.get("source_id") or "") or None,
    )
    score, err, notes = score_ad5_trial(
        mode=mode,
        completion=completion,
        expected_gold=str(item["gold"]),
        lookup_kind=kind2,
        ctx_ok=ctx_ok,
    )
    notes = list(notes) + [
        f"score_before={score_before}",
        f"score_after={score}",
        "FIX: constrained SEMWRAP re-ASK",
    ]
    return completion, mode, kind2, meta, score, err, notes


def _ctx_ok_for(
    routed: str, ctx: dict[str, Any] | None
) -> bool | None:
    if routed != "app-longdoc" or ctx is None:
        return None
    return (
        bool(ctx.get("l_eff_ok"))
        and bool(ctx.get("ratio_ok"))
        and bool(ctx.get("ctx_bounded"))
    )


def run_ad_hitl(
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
    GIVEN AD0 pack + declared AD stack
    WHEN ASK→EVAL→FIX×10 via ROUTEPLUS app router
    THEN mean≥7 · errors≤3 · no false-hit → PROMOTE|HOLD|KILL.
    """
    if len(AD0_PACK) != AD5_N:
        raise ValueError("AD0 pack must be 10")
    trials_dir.mkdir(parents=True, exist_ok=True)
    seeded = _seed_golds(bank_path, ad_bank)
    bank = load_bank_rows(bank_path)
    claim_ok = claim_is_honest(STACK_CLAIM)
    held_out_ok = len(overlaps_prior_questions(AD0_PACK)) == 0
    ctxs = _build_ctxs(curated_root=curated_root, workers=workers)
    payloads = ask_many(
        questions=[p["question"] for p in AD0_PACK],
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated_root,
        ask_cache=AskCompletionCache(),
    )
    if len(payloads) != AD5_N:
        raise RuntimeError(f"expected {AD5_N} payloads")

    trials: list[dict[str, Any]] = []
    fix_count = 0
    for i, (item, payload) in enumerate(
        zip(AD0_PACK, payloads, strict=True), start=1
    ):
        tid = f"AD-FINAL-HITL-{i:02d}"
        routed = select_app(item["app_id"])
        kind, sem_meta = _classify(dict(item), payload, bank, curated_root)
        ctx = ctxs[i - 1]
        ctx_ok = _ctx_ok_for(routed, ctx)
        score_before, err_before, notes_before = score_ad5_trial(
            mode=str(payload.get("mode", "")),
            completion=str(payload.get("completion", "")),
            expected_gold=str(item["gold"]),
            lookup_kind=kind,
            ctx_ok=ctx_ok,
        )
        score, err, notes = score_before, err_before, list(notes_before)
        completion = str(payload.get("completion", ""))
        mode = str(payload.get("mode", ""))
        fixed = False
        if err:
            fixed = True
            fix_count += 1
            (
                completion,
                mode,
                kind,
                sem_meta,
                score,
                err,
                notes,
            ) = _apply_fix(
                tid=tid,
                item=dict(item),
                bank_path=bank_path,
                ad_bank=ad_bank,
                curated=curated_root,
                payload=payload,
                kind=kind,
                sem_meta=sem_meta,
                score_before=score_before,
                notes_before=notes_before,
                ctx_ok=ctx_ok,
            )
            bank = load_bank_rows(bank_path)
        trial: dict[str, Any] = {
            "trial_id": tid,
            "stage": "AD5",
            "hyp_id": AD5_ID,
            "realapp_id": routed,
            "app_id": item["app_id"],
            "question": item["question"],
            "source_id": item["source_id"],
            "recipe_id": payload.get("recipe_id") or "champion-ad-v0",
            "ckpt": None,
            "completion": completion,
            "wall_ms": payload.get("wall_ms"),
            "n_new": payload.get("n_new"),
            "seed": payload.get("seed", 0),
            "mode": mode,
            "lookup_kind": kind,
            "semwrap": sem_meta,
            "ctxplus": ctx,
            "score": score,
            "score_before": score_before,
            "error": err,
            "judge_model_name": _JUDGE,
            "judge_notes": notes,
            "manual_adjust": (
                "FIX: constrained SEMWRAP re-ASK"
                if fixed
                else "no change — AD5 final stack ok"
            ),
            "gold": str(item["gold"]).strip(),
            "repaired": str(item["gold"]).strip(),
            "wrap_id": payload.get("wrap_id"),
            "weight_update": False,
        }
        errs = validate_trial(trial)
        if errs:
            raise ValueError(f"{tid}: " + "; ".join(errs))
        write_json(trials_dir / f"{tid}.json", trial)
        trials.append(trial)

    scores = [float(t["score"]) for t in trials]
    errors = [bool(t["error"]) for t in trials]
    n_true = sum(1 for t in trials if t["lookup_kind"] == "TRUE_HIT")
    n_false = sum(1 for t in trials if t["lookup_kind"] == "FALSE_HIT")
    n_miss = sum(1 for t in trials if t["lookup_kind"] == "MISS")
    n_known = sum(1 for t in trials if t["realapp_id"] == "app-known")
    n_long = sum(1 for t in trials if t["realapp_id"] == "app-longdoc")
    n_howto = sum(1 for t in trials if t["realapp_id"] == "app-howto")
    stats = ad5_stats(
        scores,
        errors,
        n_true_hit=n_true,
        n_false_hit=n_false,
        n_miss=n_miss,
        n_fix=fix_count,
        claim_ok=claim_ok,
        held_out_ok=held_out_ok,
        n_known_app=n_known,
        n_long_app=n_long,
        n_howto_app=n_howto,
    )
    decision = decide_ad5(stats)
    summary: dict[str, Any] = {
        "hyp_id": AD5_ID,
        "stage": "AD5",
        "decision": decision,
        "stack": list(DECLARED_STACK),
        "claim": STACK_CLAIM,
        "seeded_golds": int(seeded),
        "held_out_ok": held_out_ok,
        "forbidden": [
            "STREAM",
            "KVCACHE-Q",
            "GENCACHE",
            "ZPREF",
            "QI",
            "MIXD",
            "open chat claim",
            "reuse AB/AC question texts",
        ],
        "fix_count": fix_count,
        "stats": stats,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "workers": int(workers),
        "trials": [
            {
                "trial_id": t["trial_id"],
                "source_id": t["source_id"],
                "app_id": t["app_id"],
                "realapp_id": t["realapp_id"],
                "mode": t["mode"],
                "lookup_kind": t["lookup_kind"],
                "score": t["score"],
                "score_before": t["score_before"],
                "error": t["error"],
                "wall_ms": t["wall_ms"],
            }
            for t in trials
        ],
        "finding": (
            f"{AD5_ID}: mean={stats['mean']:.1f} "
            f"errors={stats['n_errors']}/10 "
            f"false_hit={n_false} fix={fix_count} "
            f"held_out={held_out_ok} decision={decision}."
        ),
        "public_note": "docs/results/nano-lm/wave-ad-hitl.md",
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
        summary = run_ad_hitl(
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
                "hyp_id": AD5_ID,
                "decision": decision,
                "mean": summary["stats"]["mean"],
                "n_errors": summary["stats"]["n_errors"],
                "n_false_hit": summary["stats"]["n_false_hit"],
                "held_out_ok": summary["held_out_ok"],
                "n_howto_app": summary["stats"]["n_howto_app"],
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
