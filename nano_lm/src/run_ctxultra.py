"""Wave AF1 H-CTXULTRA runner: triple-doc beyond CTXMAX (nano:ctxultra)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from af_session_ops import AF0_PACK
from askfast_ops import AskCompletionCache
from curated_sources import SOURCES
from ctxultra_ops import (
    CTXULTRA_ID,
    CTXULTRA_N,
    ctxultra_doc_meta,
    ctxultra_stats,
    decide_ctxultra,
    score_ctxultra_trial,
    secondary_for,
    tertiary_for,
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
_AF_BANK = REPO / "results/nano-lm/wave-af/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-af/trials"
_SUMMARY = REPO / "results/nano-lm/wave-af/ctxultra_summary.json"
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


def _seed_pack_golds(bank_path: Path, af_bank: Path) -> int:
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    af_bank.parent.mkdir(parents=True, exist_ok=True)
    if not af_bank.is_file():
        af_bank.write_text("", encoding="utf-8")
    existing = {
        str(r.get("question", "")).strip()
        for r in load_bank_rows(bank_path)
    }
    n = 0
    for i, item in enumerate(AF0_PACK, start=1):
        q = str(item["question"]).strip()
        if q in existing:
            continue
        row = alias_bank_row(
            trial_id=f"AF-CTXULTRA-SEED-{i:02d}",
            question=q,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = CTXULTRA_ID
        row["judge_notes"] = [
            "CTXULTRA seed alias for held-out AF ask",
            "scoped to curated source_id",
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
    tid = f"AF-CTXULTRA-HITL-{i:02d}"
    mode = str(payload.get("mode", ""))
    score, err, notes, usable = score_ctxultra_trial(
        mode=mode,
        completion=str(payload.get("completion", "")),
        expected_gold=str(item["gold"]),
        lookup_kind=lookup_kind,
        meta=ctx,
    )
    trial: dict[str, Any] = {
        "trial_id": tid,
        "stage": "AF1",
        "hyp_id": CTXULTRA_ID,
        "app_id": item["app_id"],
        "question": item["question"],
        "source_id": item["source_id"],
        "secondary_source": ctx.get("secondary_source"),
        "tertiary_source": ctx.get("tertiary_source"),
        "recipe_id": payload.get("recipe_id"),
        "ckpt": None,
        "completion": payload.get("completion"),
        "wall_ms": payload.get("wall_ms"),
        "n_new": payload.get("n_new"),
        "seed": payload.get("seed", 0),
        "mode": mode,
        "lookup_kind": lookup_kind,
        "semwrap": sem_meta,
        "ctxultra": ctx,
        "usable": usable,
        "score": score,
        "error": err,
        "fix_pass": int(fix_pass),
        "judge_model_name": _JUDGE,
        "judge_notes": notes,
        "manual_adjust": (
            "no change — CTXULTRA usable"
            if usable
            else "FIX: triple-doc/ctx or SEMWRAP gold"
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
    def _read(item: dict[str, str]) -> tuple[dict[str, str], str, str, str]:
        primary = item["source_id"]
        return (
            item,
            _load_doc(primary, curated_root),
            _load_doc(secondary_for(primary), curated_root),
            _load_doc(tertiary_for(primary), curated_root),
        )

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        quads = list(pool.map(_read, [dict(p) for p in AF0_PACK]))
    ctxs: list[dict[str, Any]] = []
    for item, p_text, s_text, t_text in quads:
        p_ids = list(tok.encode(p_text, add_special_tokens=False))
        s_ids = list(tok.encode(s_text, add_special_tokens=False))
        t_ids = list(tok.encode(t_text, add_special_tokens=False))
        q_ids = list(tok.encode(item["question"], add_special_tokens=False))
        sec = secondary_for(item["source_id"])
        ter = tertiary_for(item["source_id"])
        meta = ctxultra_doc_meta(
            p_ids,
            s_ids,
            t_ids,
            q_ids,
            primary_source=item["source_id"],
            secondary_source=sec,
            tertiary_source=ter,
        )
        meta["primary_chars"] = len(p_text)
        meta["secondary_chars"] = len(s_text)
        meta["tertiary_chars"] = len(t_text)
        ctxs.append(meta)
    return ctxs


def _fix_and_reask(
    *,
    i: int,
    item: dict[str, str],
    bank_path: Path,
    af_bank: Path,
    root: Path,
    curated_root: Path,
    seed: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], int]:
    row = alias_bank_row(
        trial_id=f"AF-CTXULTRA-FIX-{i:02d}",
        question=item["question"],
        source_id=item["source_id"],
        gold=item["gold"],
    )
    row["hyp_id"] = CTXULTRA_ID
    append_error_row(bank_path, row)
    append_error_row(af_bank, row)
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


def run_ctxultra(
    *,
    bank_path: Path,
    af_bank: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
    workers: int = 8,
) -> dict[str, Any]:
    """
    GIVEN AF0 held-out asks + triple curated docs
    WHEN K=7 multi-slice SUMCACHE/ROLL + ASKFAST/SEMWRAP
    THEN L_eff↑ vs CTXMAX · ≥7/10 usable → PROMOTE|HOLD|KILL.
    """
    if len(AF0_PACK) != CTXULTRA_N:
        raise ValueError("AF0 pack must be 10")
    trials_dir.mkdir(parents=True, exist_ok=True)
    seeded = _seed_pack_golds(bank_path, af_bank)
    cfg = matrix_cfg()
    tok = load_tokenizer(str(cfg["tokenizer_id"]), cfg["cache"])
    bank = load_bank_rows(bank_path)
    ctxs = _build_ctxs(curated_root=curated_root, workers=workers, tok=tok)

    questions = [p["question"] for p in AF0_PACK]
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
    if len(payloads) != CTXULTRA_N:
        raise RuntimeError(f"expected 10 payloads, got {len(payloads)}")

    trials: list[dict[str, Any]] = []
    fix_count = 0
    for i, (item, payload, ctx) in enumerate(
        zip(AF0_PACK, payloads, ctxs, strict=True), start=1
    ):
        kind, sem_meta = _classify(dict(item), payload, bank, curated_root)
        fix_pass = 0
        if kind != "TRUE_HIT":
            payload, bank, fix_pass = _fix_and_reask(
                i=i,
                item=dict(item),
                bank_path=bank_path,
                af_bank=af_bank,
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
    mean_l = float(sum(float(c["l_eff"]) for c in ctxs) / CTXULTRA_N)
    mean_a = float(
        sum(float(c["sumcache_active"]) for c in ctxs) / CTXULTRA_N
    )
    mean_s = float(sum(float(c["n_slices"]) for c in ctxs) / CTXULTRA_N)
    mean_src = float(sum(float(c["n_sources"]) for c in ctxs) / CTXULTRA_N)
    n_multi = sum(1 for c in ctxs if c.get("multi_source"))
    stats = ctxultra_stats(
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
    decision = decide_ctxultra(stats)
    summary: dict[str, Any] = {
        "hyp_id": CTXULTRA_ID,
        "stage": "AF1",
        "decision": decision,
        "compose": [
            "SUMCACHE",
            "ROLL-multi-K7",
            "triple-doc",
            "SEMWRAP",
            "ASKFAST",
        ],
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
                "tertiary_source": t["tertiary_source"],
                "app_id": t["app_id"],
                "mode": t["mode"],
                "lookup_kind": t["lookup_kind"],
                "score": t["score"],
                "error": t["error"],
                "usable": t["usable"],
                "fix_pass": t["fix_pass"],
                "l_eff": t["ctxultra"]["l_eff"],
                "n_slices": t["ctxultra"]["n_slices"],
                "n_sources": t["ctxultra"]["n_sources"],
                "active": t["ctxultra"]["sumcache_active"],
            }
            for t in trials
        ],
        "finding": (
            f"{CTXULTRA_ID}: usable={stats['n_usable']}/10 "
            f"L_eff={mean_l:.0f} (>CTXMAX {stats['ctxmax_mean_leff']:.0f}) "
            f"slices={mean_s:.1f} sources={mean_src:.1f} "
            f"active={mean_a:.0f} mean={stats['mean']:.1f} "
            f"false_hit={n_false} fix={fix_count} decision={decision}."
        ),
        "public_note": "docs/results/nano-lm/formal-hctxultra-ctxultra.md",
        "claim": "deeper triple-doc curated ask — not open chat / STREAM",
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
    workers = min(12, max(4, cpus - 4))
    try:
        summary = run_ctxultra(
            bank_path=Path(args.bank),
            af_bank=Path(args.af_bank),
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
                "hyp_id": CTXULTRA_ID,
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
