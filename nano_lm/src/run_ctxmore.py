"""Wave AK2 H-CTXMORE runner: octa-doc dual-arm ASK→EVAL→FIX×10."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from ak_session_ops import AK0_PACK
from askfast_ops import AskCompletionCache
from curated_sources import SOURCES
from ctxmore_ops import (
    CTXMORE_ID,
    CTXMORE_N,
    companions_for,
    ctxmore_doc_meta,
    ctxmore_stats,
    decide_ctxmore,
    score_ctxmore_gen,
    score_ctxmore_lookup,
)
from data_tiny import load_tokenizer
from matrix_common import REPO, matrix_cfg, write_json
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row, classify_semwrap, semantic_lookup
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AK_BANK = REPO / "results/nano-lm/wave-ak/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-ak/trials"
_SUMMARY = REPO / "results/nano-lm/wave-ak/ctxmore_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_JUDGE = "cursor-composer-frontier-chat"
_BY_ID = {str(s["id"]): s for s in SOURCES}
_SRC_KEYS = (
    "secondary_source",
    "tertiary_source",
    "quaternary_source",
    "quinary_source",
    "senary_source",
    "septenary_source",
    "octonary_source",
)


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


def _seed_pack_golds(bank_path: Path, ak_bank: Path) -> int:
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    ak_bank.parent.mkdir(parents=True, exist_ok=True)
    if not ak_bank.is_file():
        ak_bank.write_text("", encoding="utf-8")
    existing = {
        str(r.get("question", "")).strip() for r in load_bank_rows(bank_path)
    }
    n = 0
    for i, item in enumerate(AK0_PACK, start=1):
        q = str(item["question"]).strip()
        if q in existing:
            continue
        row = alias_bank_row(
            trial_id=f"AK-CTXMORE-SEED-{i:02d}",
            question=q,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = CTXMORE_ID
        row["judge_notes"] = [
            "CTXMORE seed alias for held-out AK ask",
            "LOOKUP product path — not generative IQ",
            "no student weight update",
        ]
        append_error_row(bank_path, row)
        append_error_row(ak_bank, row)
        existing.add(q)
        n += 1
    return n


def _classify_lookup(
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
    *, curated_root: Path, workers: int, tok: Any
) -> list[dict[str, Any]]:
    def _read(item: dict[str, str]) -> tuple[dict[str, str], list[str]]:
        primary = item["source_id"]
        comps = list(companions_for(primary))
        ids = [primary, *comps]
        texts = [_load_doc(sid, curated_root) for sid in ids]
        return item, texts

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        rows = list(pool.map(_read, [dict(p) for p in AK0_PACK]))
    ctxs: list[dict[str, Any]] = []
    for item, texts in rows:
        token_docs = [
            list(tok.encode(t, add_special_tokens=False)) for t in texts
        ]
        q_ids = list(tok.encode(item["question"], add_special_tokens=False))
        sid = item["source_id"]
        comps = list(companions_for(sid))
        meta = ctxmore_doc_meta(
            token_docs,
            q_ids,
            source_ids=[sid, *comps],
        )
        ctxs.append(meta)
    return ctxs


def _fix_lookup(
    *,
    i: int,
    item: dict[str, str],
    bank_path: Path,
    ak_bank: Path,
    root: Path,
    curated_root: Path,
    seed: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], int]:
    row = alias_bank_row(
        trial_id=f"AK-CTXMORE-FIX-{i:02d}",
        question=item["question"],
        source_id=item["source_id"],
        gold=item["gold"],
    )
    row["hyp_id"] = CTXMORE_ID
    append_error_row(bank_path, row)
    append_error_row(ak_bank, row)
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


def _src_fields(ctx: dict[str, Any]) -> dict[str, Any]:
    return {k: ctx.get(k) for k in _SRC_KEYS}


def _lookup_trial(
    *,
    i: int,
    item: dict[str, str],
    payload: dict[str, Any],
    kind: str,
    sem_meta: dict[str, Any],
    ctx: dict[str, Any],
    fix_pass: int,
) -> dict[str, Any]:
    tid = f"AK-CTXMORE-LOOKUP-HITL-{i:02d}"
    mode = str(payload.get("mode", ""))
    score, err, notes, usable = score_ctxmore_lookup(
        mode=mode,
        completion=str(payload.get("completion", "")),
        expected_gold=str(item["gold"]),
        lookup_kind=kind,
        meta=ctx,
        payload=payload,
    )
    return {
        "trial_id": tid,
        "stage": "AK2",
        "hyp_id": CTXMORE_ID,
        "arm": "LOOKUP",
        "app_id": item["app_id"],
        "question": item["question"],
        "source_id": item["source_id"],
        **_src_fields(ctx),
        "completion": payload.get("completion"),
        "wall_ms": payload.get("wall_ms"),
        "n_new": payload.get("n_new"),
        "mode": mode,
        "lookup_kind": kind,
        "semwrap": sem_meta,
        "ctxmore": ctx,
        "usable": usable,
        "score": score,
        "error": err,
        "fix_pass": int(fix_pass),
        "judge_model_name": _JUDGE,
        "judge_notes": notes,
        "gold": str(item["gold"]).strip(),
        "weight_update": False,
    }


def _gen_trial(
    *,
    i: int,
    item: dict[str, str],
    payload: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    tid = f"AK-CTXMORE-GEN-HITL-{i:02d}"
    score, err, notes, usable = score_ctxmore_gen(
        completion=str(payload.get("completion", "")),
        expected_gold=str(item["gold"]),
        meta=ctx,
        payload=payload,
    )
    return {
        "trial_id": tid,
        "stage": "AK2",
        "hyp_id": CTXMORE_ID,
        "arm": "GENERATE",
        "app_id": item["app_id"],
        "question": item["question"],
        "source_id": item["source_id"],
        **_src_fields(ctx),
        "completion": payload.get("completion"),
        "wall_ms": payload.get("wall_ms"),
        "n_new": payload.get("n_new"),
        "mode": payload.get("mode"),
        "ctxmore": ctx,
        "usable": usable,
        "score": score,
        "error": err,
        "fix_pass": 0,
        "judge_model_name": _JUDGE,
        "judge_notes": notes,
        "gold": str(item["gold"]).strip(),
        "weight_update": False,
    }


def run_ctxmore(
    *,
    bank_path: Path,
    ak_bank: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
    workers: int = 8,
) -> dict[str, Any]:
    """
    GIVEN AK0 held-out asks + octa curated docs
    WHEN K=17 ROLL/SUMCACHE + LOOKUP askfast + GENERATE raw
    THEN L_eff↑ vs CTXPEAK · gen usable≥5 → PROMOTE|HOLD|KILL.
    """
    if len(AK0_PACK) != CTXMORE_N:
        raise ValueError("AK0 pack must be 10")
    trials_dir.mkdir(parents=True, exist_ok=True)
    seeded = _seed_pack_golds(bank_path, ak_bank)
    cfg = matrix_cfg()
    tok = load_tokenizer(str(cfg["tokenizer_id"]), cfg["cache"])
    bank = load_bank_rows(bank_path)
    ctxs = _build_ctxs(curated_root=curated_root, workers=workers, tok=tok)
    questions = [p["question"] for p in AK0_PACK]

    lookup_payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated_root,
        ask_cache=AskCompletionCache(),
    )
    gen_payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        wrap=False,
        bank_path=bank_path,
        curated_root=curated_root,
    )

    lookup_trials: list[dict[str, Any]] = []
    gen_trials: list[dict[str, Any]] = []
    fix_count = 0
    for i, (item, lp, gp, ctx) in enumerate(
        zip(AK0_PACK, lookup_payloads, gen_payloads, ctxs, strict=True),
        start=1,
    ):
        kind, sem_meta = _classify_lookup(
            dict(item), lp, bank, curated_root
        )
        fix_pass = 0
        if kind != "TRUE_HIT":
            lp, bank, fix_pass = _fix_lookup(
                i=i,
                item=dict(item),
                bank_path=bank_path,
                ak_bank=ak_bank,
                root=root,
                curated_root=curated_root,
                seed=seed,
            )
            fix_count += 1
            kind, sem_meta = _classify_lookup(
                dict(item), lp, bank, curated_root
            )
        lt = _lookup_trial(
            i=i,
            item=dict(item),
            payload=lp,
            kind=kind,
            sem_meta=sem_meta,
            ctx=ctx,
            fix_pass=fix_pass,
        )
        gt = _gen_trial(i=i, item=dict(item), payload=gp, ctx=ctx)
        if gt["error"]:
            append_error_row(
                ak_bank,
                {
                    "trial_id": gt["trial_id"],
                    "question": item["question"],
                    "source_id": item["source_id"],
                    "model_raw": str(gt.get("completion") or ""),
                    "score": float(gt["score"]),
                    "error": True,
                    "recipe_id": "champion-qt-early-v0",
                    "hyp_id": CTXMORE_ID,
                    "arm": "GENERATE",
                    "fix": "before",
                    "judge_notes": gt["judge_notes"],
                    "gold": item["gold"],
                },
            )
        write_json(trials_dir / f"{lt['trial_id']}.json", lt)
        write_json(trials_dir / f"{gt['trial_id']}.json", gt)
        lookup_trials.append(lt)
        gen_trials.append(gt)

    mean_l = float(sum(float(c["l_eff"]) for c in ctxs) / CTXMORE_N)
    mean_a = float(
        sum(float(c["sumcache_active"]) for c in ctxs) / CTXMORE_N
    )
    mean_s = float(sum(float(c["n_slices"]) for c in ctxs) / CTXMORE_N)
    mean_src = float(sum(float(c["n_sources"]) for c in ctxs) / CTXMORE_N)
    n_true = sum(1 for t in lookup_trials if t["lookup_kind"] == "TRUE_HIT")
    n_false = sum(
        1 for t in lookup_trials if t["lookup_kind"] == "FALSE_HIT"
    )
    stats = ctxmore_stats(
        lookup_scores=[float(t["score"]) for t in lookup_trials],
        lookup_errors=[bool(t["error"]) for t in lookup_trials],
        lookup_usables=[bool(t["usable"]) for t in lookup_trials],
        gen_scores=[float(t["score"]) for t in gen_trials],
        gen_errors=[bool(t["error"]) for t in gen_trials],
        gen_usables=[bool(t["usable"]) for t in gen_trials],
        n_true_hit=n_true,
        n_false_hit=n_false,
        mean_l_eff=mean_l,
        mean_active=mean_a,
        mean_slices=mean_s,
        mean_sources=mean_src,
        n_fix=fix_count,
    )
    decision = decide_ctxmore(stats)
    summary: dict[str, Any] = {
        "hyp_id": CTXMORE_ID,
        "stage": "AK2",
        "decision": decision,
        "compose": [
            "SUMCACHE",
            "ROLL-multi-K17",
            "octa-doc",
            "SEMWRAP/ASKFAST LOOKUP",
            "GENERATE raw",
        ],
        "forbidden": [
            "STREAM",
            "KVCACHE-Q",
            "GENCACHE",
            "naive CTX",
            "invent Wave AL",
        ],
        "seeded_golds": int(seeded),
        "fix_count": int(fix_count),
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "workers": int(workers),
        "stats": stats,
        "lookup_trials": [
            {
                "trial_id": t["trial_id"],
                "mode": t["mode"],
                "wall_ms": t["wall_ms"],
                "n_new": t["n_new"],
                "score": t["score"],
                "usable": t["usable"],
                "lookup_kind": t["lookup_kind"],
                "l_eff": t["ctxmore"]["l_eff"],
            }
            for t in lookup_trials
        ],
        "gen_trials": [
            {
                "trial_id": t["trial_id"],
                "mode": t["mode"],
                "wall_ms": t["wall_ms"],
                "n_new": t["n_new"],
                "score": t["score"],
                "usable": t["usable"],
                "l_eff": t["ctxmore"]["l_eff"],
                "completion": str(t.get("completion") or "")[:120],
            }
            for t in gen_trials
        ],
        "finding": (
            f"{CTXMORE_ID}: L_lookup={stats['lookup_mean']:.1f} "
            f"L_gen={stats['gen_mean']:.1f} "
            f"usable_L={stats['n_lookup_usable']}/10 "
            f"usable_G={stats['n_gen_usable']}/10 "
            f"L_eff={mean_l:.0f} (>CTXPEAK {stats['ctxpeak_mean_leff']:.0f}) "
            f"sources={mean_src:.1f} slices={mean_s:.1f} "
            f"false_hit={n_false} fix={fix_count} decision={decision}."
        ),
        "public_note": "docs/results/nano-lm/formal-hctxmore-ctxmore.md",
        "ship_claim": "AF packaged stack (octa long-ctx; LOOKUP≠gen IQ)",
        "claim": (
            "octa-doc longer usable ctx beyond CTXPEAK — "
            "not open chat / LOOKUP≠gen IQ"
        ),
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--ak-bank", type=Path, default=_AK_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    cpus = int(os.cpu_count() or 4)
    # Max safe: leave 2 cores free (desktop responsive + GPU decode).
    threads = tune_cpu_threads(max(4, cpus - 2))
    workers = min(14, max(4, cpus - 2))
    try:
        summary = run_ctxmore(
            bank_path=Path(args.bank),
            ak_bank=Path(args.ak_bank),
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
                "hyp_id": CTXMORE_ID,
                "decision": decision,
                "lookup_mean": summary["stats"]["lookup_mean"],
                "gen_mean": summary["stats"]["gen_mean"],
                "n_lookup_usable": summary["stats"]["n_lookup_usable"],
                "n_gen_usable": summary["stats"]["n_gen_usable"],
                "mean_l_eff": summary["stats"]["mean_l_eff"],
                "pass_leff_up": summary["stats"]["pass_leff_up"],
                "cpu_threads": threads,
                "workers": workers,
                "out": str(args.out),
            }
        )
    )
    return 0 if decision in {"PROMOTE", "HOLD"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
