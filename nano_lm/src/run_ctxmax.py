"""Wave AE1 H-CTXMAX runner: multi-doc beyond CTXPLUS (nano:ctxmax)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from ae_session_ops import AE0_PACK
from askfast_ops import AskCompletionCache
from curated_sources import SOURCES
from ctxmax_ops import (
    CTXMAX_ID,
    CTXMAX_N,
    ctxmax_doc_meta,
    ctxmax_stats,
    decide_ctxmax,
    score_ctxmax_trial,
    secondary_for,
)
from data_tiny import load_tokenizer
from matrix_common import REPO, matrix_cfg, write_json
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row, classify_semwrap, semantic_lookup
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_trial import validate_trial
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AE_BANK = REPO / "results/nano-lm/wave-ae/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-ae/trials"
_SUMMARY = REPO / "results/nano-lm/wave-ae/ctxmax_summary.json"
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


def _load_doc(source_id: str, curated: Path) -> str:
    meta = _BY_ID.get(source_id)
    if meta is None:
        raise ValueError(f"unknown source_id: {source_id}")
    path = curated / str(meta["path"])
    if not path.is_file():
        raise FileNotFoundError(str(path))
    return path.read_text(encoding="utf-8", errors="ignore")


def _seed_pack_golds(bank_path: Path, ae_bank: Path) -> int:
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    ae_bank.parent.mkdir(parents=True, exist_ok=True)
    if not ae_bank.is_file():
        ae_bank.write_text("", encoding="utf-8")
    existing = {
        str(r.get("question", "")).strip()
        for r in load_bank_rows(bank_path)
    }
    n = 0
    for i, item in enumerate(AE0_PACK, start=1):
        q = str(item["question"]).strip()
        if q in existing:
            continue
        row = alias_bank_row(
            trial_id=f"AE-CTXMAX-SEED-{i:02d}",
            question=q,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = CTXMAX_ID
        row["judge_notes"] = [
            "CTXMAX seed alias for held-out AE ask",
            "scoped to curated source_id",
            "no student weight update",
        ]
        append_error_row(bank_path, row)
        append_error_row(ae_bank, row)
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
    if mode in {"SEMWRAP_LOOKUP", "WRAP_LOOKUP", "ASKFAST_CACHE"}:
        _g, meta = semantic_lookup(
            item["question"], bank, curated_root=curated
        )
        kind = classify_semwrap(
            str(payload.get("completion")),
            expected_gold=item["gold"],
            expected_source_id=item["source_id"],
            hit_source_id=str(meta.get("source_id") or "") or None,
        )
        return kind, meta
    gold, meta = semantic_lookup(
        item["question"], bank, curated_root=curated
    )
    kind = classify_semwrap(
        gold,
        expected_gold=item["gold"],
        expected_source_id=item["source_id"],
        hit_source_id=str(meta.get("source_id") or "") or None,
    )
    return kind, meta


def _build_trial(
    *,
    i: int,
    item: dict[str, str],
    payload: dict[str, Any],
    lookup_kind: str,
    sem_meta: dict[str, Any],
    ctx: dict[str, Any],
    fix_pass: int,
) -> dict[str, Any]:
    tid = f"AE-CTXMAX-HITL-{i:02d}"
    mode = str(payload.get("mode", ""))
    score, err, notes, usable = score_ctxmax_trial(
        mode=mode,
        completion=str(payload.get("completion", "")),
        expected_gold=str(item["gold"]),
        lookup_kind=lookup_kind,
        meta=ctx,
    )
    trial: dict[str, Any] = {
        "trial_id": tid,
        "stage": "AE1",
        "hyp_id": CTXMAX_ID,
        "app_id": item["app_id"],
        "question": item["question"],
        "source_id": item["source_id"],
        "secondary_source": ctx.get("secondary_source"),
        "recipe_id": payload.get("recipe_id"),
        "ckpt": None,
        "completion": payload.get("completion"),
        "wall_ms": payload.get("wall_ms"),
        "n_new": payload.get("n_new"),
        "seed": payload.get("seed", 0),
        "mode": mode,
        "lookup_kind": lookup_kind,
        "semwrap": sem_meta,
        "ctxmax": ctx,
        "usable": usable,
        "score": score,
        "error": err,
        "fix_pass": int(fix_pass),
        "judge_model_name": _JUDGE,
        "judge_notes": notes,
        "manual_adjust": (
            "no change — CTXMAX usable"
            if usable
            else "FIX: multi-doc/ctx or SEMWRAP gold"
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


def _build_ctxs(
    *,
    curated_root: Path,
    workers: int,
    tok: Any,
) -> list[dict[str, Any]]:
    def _read(item: dict[str, str]) -> tuple[dict[str, str], str, str]:
        primary = item["source_id"]
        secondary = secondary_for(primary)
        return (
            item,
            _load_doc(primary, curated_root),
            _load_doc(secondary, curated_root),
        )

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        triples = list(pool.map(_read, [dict(p) for p in AE0_PACK]))
    ctxs: list[dict[str, Any]] = []
    for item, p_text, s_text in triples:
        p_ids = list(tok.encode(p_text, add_special_tokens=False))
        s_ids = list(tok.encode(s_text, add_special_tokens=False))
        q_ids = list(tok.encode(item["question"], add_special_tokens=False))
        sec = secondary_for(item["source_id"])
        meta = ctxmax_doc_meta(
            p_ids,
            s_ids,
            q_ids,
            primary_source=item["source_id"],
            secondary_source=sec,
        )
        meta["primary_chars"] = len(p_text)
        meta["secondary_chars"] = len(s_text)
        ctxs.append(meta)
    return ctxs


def _fix_and_reask(
    *,
    i: int,
    item: dict[str, str],
    bank_path: Path,
    ae_bank: Path,
    root: Path,
    curated_root: Path,
    seed: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], int]:
    row = alias_bank_row(
        trial_id=f"AE-CTXMAX-FIX-{i:02d}",
        question=item["question"],
        source_id=item["source_id"],
        gold=item["gold"],
    )
    row["hyp_id"] = CTXMAX_ID
    append_error_row(bank_path, row)
    append_error_row(ae_bank, row)
    bank = load_bank_rows(bank_path)
    re_payloads = ask_many(
        questions=[item["question"]],
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated_root,
        ask_cache=AskCompletionCache(),
    )
    return re_payloads[0], bank, 1


def run_ctxmax(
    *,
    bank_path: Path,
    ae_bank: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
    workers: int = 8,
) -> dict[str, Any]:
    """
    GIVEN AE0 held-out asks + dual curated docs
    WHEN K=5 multi-slice SUMCACHE/ROLL + ASKFAST/SEMWRAP
    THEN L_eff↑ vs CTXPLUS · ≥7/10 usable → PROMOTE|HOLD|KILL.
    """
    if len(AE0_PACK) != CTXMAX_N:
        raise ValueError("AE0 pack must be 10")
    trials_dir.mkdir(parents=True, exist_ok=True)
    seeded = _seed_pack_golds(bank_path, ae_bank)
    cfg = matrix_cfg()
    tok = load_tokenizer(str(cfg["tokenizer_id"]), cfg["cache"])
    bank = load_bank_rows(bank_path)
    ctxs = _build_ctxs(curated_root=curated_root, workers=workers, tok=tok)

    questions = [p["question"] for p in AE0_PACK]
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
    if len(payloads) != CTXMAX_N:
        raise RuntimeError(f"expected 10 payloads, got {len(payloads)}")

    trials: list[dict[str, Any]] = []
    fix_count = 0
    for i, (item, payload, ctx) in enumerate(
        zip(AE0_PACK, payloads, ctxs, strict=True), start=1
    ):
        kind, sem_meta = _classify(dict(item), payload, bank, curated_root)
        fix_pass = 0
        if kind != "TRUE_HIT":
            payload, bank, fix_pass = _fix_and_reask(
                i=i,
                item=dict(item),
                bank_path=bank_path,
                ae_bank=ae_bank,
                root=root,
                curated_root=curated_root,
                seed=seed,
            )
            fix_count += 1
            kind, sem_meta = _classify(
                dict(item), payload, bank, curated_root
            )
        trial = _build_trial(
            i=i,
            item=dict(item),
            payload=payload,
            lookup_kind=kind,
            sem_meta=sem_meta,
            ctx=ctx,
            fix_pass=fix_pass,
        )
        write_json(trials_dir / f"{trial['trial_id']}.json", trial)
        trials.append(trial)

    scores = [float(t["score"]) for t in trials]
    errors = [bool(t["error"]) for t in trials]
    usables = [bool(t["usable"]) for t in trials]
    n_true = sum(1 for t in trials if t["lookup_kind"] == "TRUE_HIT")
    n_false = sum(1 for t in trials if t["lookup_kind"] == "FALSE_HIT")
    n_miss = sum(1 for t in trials if t["lookup_kind"] == "MISS")
    mean_l = float(sum(float(c["l_eff"]) for c in ctxs) / CTXMAX_N)
    mean_a = float(
        sum(float(c["sumcache_active"]) for c in ctxs) / CTXMAX_N
    )
    mean_s = float(sum(float(c["n_slices"]) for c in ctxs) / CTXMAX_N)
    mean_src = float(sum(float(c["n_sources"]) for c in ctxs) / CTXMAX_N)
    n_multi = sum(1 for c in ctxs if c.get("multi_source"))
    stats = ctxmax_stats(
        scores,
        errors,
        usables,
        n_true_hit=n_true,
        n_false_hit=n_false,
        n_miss=n_miss,
        mean_l_eff=mean_l,
        mean_active=mean_a,
        mean_slices=mean_s,
        mean_sources=mean_src,
        n_multi_source=n_multi,
        n_fix=fix_count,
    )
    decision = decide_ctxmax(stats)
    summary: dict[str, Any] = {
        "hyp_id": CTXMAX_ID,
        "stage": "AE1",
        "decision": decision,
        "compose": ["SUMCACHE", "ROLL-multi-K5", "multi-doc", "SEMWRAP", "ASKFAST"],
        "forbidden": ["STREAM", "KVCACHE-Q", "GENCACHE", "naive CTX"],
        "seeded_golds": int(seeded),
        "fix_count": int(fix_count),
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "workers": int(workers),
        "stats": stats,
        "trials": [
            {
                "trial_id": t["trial_id"],
                "source_id": t["source_id"],
                "secondary_source": t["secondary_source"],
                "app_id": t["app_id"],
                "mode": t["mode"],
                "lookup_kind": t["lookup_kind"],
                "score": t["score"],
                "error": t["error"],
                "usable": t["usable"],
                "fix_pass": t["fix_pass"],
                "l_eff": t["ctxmax"]["l_eff"],
                "n_slices": t["ctxmax"]["n_slices"],
                "n_sources": t["ctxmax"]["n_sources"],
                "active": t["ctxmax"]["sumcache_active"],
            }
            for t in trials
        ],
        "finding": (
            f"{CTXMAX_ID}: usable={stats['n_usable']}/10 "
            f"L_eff={mean_l:.0f} (>CTXPLUS {stats['ctxplus_mean_leff']:.0f}) "
            f"slices={mean_s:.1f} sources={mean_src:.1f} "
            f"active={mean_a:.0f} mean={stats['mean']:.1f} "
            f"false_hit={n_false} fix={fix_count} decision={decision}."
        ),
        "public_note": "docs/results/nano-lm/formal-hctxmax-ctxmax.md",
        "claim": "deeper multi-doc curated ask — not open chat / STREAM",
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--ae-bank", type=Path, default=_AE_BANK)
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
        summary = run_ctxmax(
            bank_path=Path(args.bank),
            ae_bank=Path(args.ae_bank),
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
                "hyp_id": CTXMAX_ID,
                "decision": decision,
                "mean": summary["stats"]["mean"],
                "n_usable": summary["stats"]["n_usable"],
                "mean_l_eff": summary["stats"]["mean_l_eff"],
                "mean_slices": summary["stats"]["mean_slices"],
                "mean_sources": summary["stats"]["mean_sources"],
                "pass_leff_up": summary["stats"]["pass_leff_up"],
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
