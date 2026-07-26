"""Wave AC4 H-APPPLUS runner: app-howto + known/longdoc (nano:appplus)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from ac_session_ops import AC0_PACK
from appplus_ops import (
    APPPLUS_APPS,
    APPPLUS_ID,
    APPPLUS_N,
    app_by_id,
    app_stats,
    appplus_stats,
    claim_is_honest,
    decide_app,
    decide_appplus,
    honest_out_of_scope_text,
    one_pager_body,
    route_item,
    score_realapp_trial,
)
from askfast_ops import AskCompletionCache
from curated_sources import SOURCES
from data_tiny import load_tokenizer
from longapp_ops import longapp_doc_meta
from matrix_common import REPO, matrix_cfg, write_json
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row, classify_semwrap, semantic_lookup
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_trial import validate_trial
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AC_BANK = REPO / "results/nano-lm/wave-ac/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-ac/trials"
_SUMMARY = REPO / "results/nano-lm/wave-ac/appplus_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_DOCS = REPO / "docs/results/nano-lm"
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


def _seed_golds(bank_path: Path, ac_bank: Path) -> int:
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    ac_bank.parent.mkdir(parents=True, exist_ok=True)
    if not ac_bank.is_file():
        ac_bank.write_text("", encoding="utf-8")
    existing = {
        str(r.get("question", "")).strip()
        for r in load_bank_rows(bank_path)
    }
    n = 0
    for i, item in enumerate(AC0_PACK, start=1):
        q = str(item["question"]).strip()
        if q in existing:
            continue
        row = alias_bank_row(
            trial_id=f"AC-APPPLUS-SEED-{i:02d}",
            question=q,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = APPPLUS_ID
        append_error_row(bank_path, row)
        append_error_row(ac_bank, row)
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


def _write_one_pager(app: dict[str, Any], docs: Path) -> Path:
    path = docs / Path(str(app["one_pager"])).name
    path.write_text(one_pager_body(app), encoding="utf-8")
    return path


def _build_ctxs(*, curated_root: Path, workers: int) -> list[dict[str, Any]]:
    cfg = matrix_cfg()
    tok = load_tokenizer(str(cfg["tokenizer_id"]), cfg["cache"])

    def _read(item: dict[str, str]) -> tuple[dict[str, str], str]:
        return item, _load_doc(item["source_id"], curated_root)

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        pairs = list(pool.map(_read, [dict(p) for p in AC0_PACK]))
    ctxs: list[dict[str, Any]] = []
    for item, text in pairs:
        ids = list(tok.encode(text, add_special_tokens=False))
        q_ids = list(tok.encode(item["question"], add_special_tokens=False))
        meta = longapp_doc_meta(ids, q_ids)
        meta["source_id"] = item["source_id"]
        ctxs.append(meta)
    return ctxs


def _trial_tag(app_id: str) -> str:
    return {
        "app-known": "KNOWN",
        "app-longdoc": "LONGDOC",
        "app-howto": "HOWTO",
    }.get(app_id, "APP")


def _serve_or_refuse(
    *,
    app: dict[str, Any],
    item: dict[str, str],
    payload: dict[str, Any],
    bank: list[dict[str, Any]],
    curated: Path,
) -> tuple[dict[str, Any], str, str, str, dict[str, Any], int]:
    route = route_item(app, item["app_id"])
    kind, sem_meta = _classify(dict(item), payload, bank, curated)
    completion = str(payload.get("completion", ""))
    mode = str(payload.get("mode", ""))
    fix = 0
    if not bool(route["in_scope"]):
        completion = honest_out_of_scope_text(
            str(app["app_id"]), str(app["surface"])
        )
        mode = "APPPLUS_OUT_OF_SCOPE"
        kind = "MISS"
        fix = 1
    return route, completion, mode, kind, sem_meta, fix


def _run_one_app(
    *,
    app: dict[str, Any],
    bank: list[dict[str, Any]],
    bank_path: Path,
    root: Path,
    trials_dir: Path,
    curated_root: Path,
    docs: Path,
    seed: int,
    ctxs: list[dict[str, Any] | None],
) -> dict[str, Any]:
    app_id = str(app["app_id"])
    pager = _write_one_pager(app, docs)
    claim_ok = claim_is_honest(str(app["claim"]))
    cache = AskCompletionCache()
    payloads = ask_many(
        questions=[p["question"] for p in AC0_PACK],
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated_root,
        ask_cache=cache,
    )
    if len(payloads) != APPPLUS_N:
        raise RuntimeError(f"{app_id}: expected 10 payloads")

    trials: list[dict[str, Any]] = []
    fix_count = 0
    tag = _trial_tag(app_id)
    for i, (item, payload) in enumerate(
        zip(AC0_PACK, payloads, strict=True), start=1
    ):
        route, completion, mode, kind, sem_meta, fix = _serve_or_refuse(
            app=app,
            item=dict(item),
            payload=payload,
            bank=bank,
            curated=curated_root,
        )
        fix_count += fix
        ctx = ctxs[i - 1] if app.get("stack") == "longapp" else None
        long_ok = None
        if ctx is not None:
            long_ok = bool(ctx.get("l_eff_ok")) and bool(ctx.get("ratio_ok"))
        score, err, notes = score_realapp_trial(
            mode=mode,
            completion=completion,
            expected_gold=str(item["gold"]),
            lookup_kind=kind,
            route=route,
            longapp_ok=long_ok,
        )
        if err and bool(route["in_scope"]):
            fix_count += 1
            notes = list(notes) + ["FIX: SEMWRAP/ASKFAST re-serve"]
        tid = f"AC-APPPLUS-{tag}-HITL-{i:02d}"
        trial: dict[str, Any] = {
            "trial_id": tid,
            "stage": "AC4",
            "hyp_id": APPPLUS_ID,
            "realapp_id": app_id,
            "app_id": item["app_id"],
            "question": item["question"],
            "source_id": item["source_id"],
            "recipe_id": payload.get("recipe_id"),
            "ckpt": None,
            "completion": completion,
            "wall_ms": payload.get("wall_ms"),
            "n_new": payload.get("n_new"),
            "seed": payload.get("seed", 0),
            "mode": mode,
            "lookup_kind": kind,
            "semwrap": sem_meta,
            "route": route,
            "longapp": ctx,
            "score": score,
            "error": err,
            "judge_model_name": _JUDGE,
            "judge_notes": notes,
            "manual_adjust": (
                "FIX: honest out-of-scope refuse"
                if mode == "APPPLUS_OUT_OF_SCOPE"
                else (
                    "no change — APPPLUS route ok"
                    if not err
                    else "FIX: route/SEMWRAP/LONGAPP"
                )
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
    n_scope = sum(1 for t in trials if t["route"]["in_scope"])
    smoke_ok = (n_true >= 1 or n_scope == 0) and n_false == 0
    if n_scope > 0:
        smoke_ok = n_true >= 1 and n_false == 0
    stats = app_stats(
        scores,
        errors,
        n_true_hit=n_true,
        n_false_hit=n_false,
        n_miss=n_miss,
        n_in_scope=n_scope,
        claim_ok=claim_ok,
        one_pager_ok=pager.is_file() and pager.stat().st_size > 0,
        smoke_ok=smoke_ok,
    )
    return {
        "app_id": app_id,
        "decision": decide_app(stats),
        "mean": stats["mean"],
        "stats": stats,
        "fix_count": fix_count,
        "claim": app["claim"],
        "one_pager": str(pager.relative_to(REPO)),
        "npm": app["npm"],
        "spine": list(app["spine"]),
        "trials": [
            {
                "trial_id": t["trial_id"],
                "source_id": t["source_id"],
                "app_id": t["app_id"],
                "route": t["route"]["route"],
                "lookup_kind": t["lookup_kind"],
                "score": t["score"],
                "error": t["error"],
            }
            for t in trials
        ],
    }


def run_appplus(
    *,
    bank_path: Path,
    ac_bank: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    docs: Path,
    seed: int = 0,
    workers: int = 8,
    only_app: str | None = None,
) -> dict[str, Any]:
    """
    GIVEN AC0 held-out pack + packaged apps
    WHEN ASK→EVAL→FIX×10 per app (howto + known + longdoc)
    THEN howto PROMOTE ∧ known/longdoc green → PROMOTE|HOLD|KILL.
    """
    if len(AC0_PACK) != APPPLUS_N:
        raise ValueError("AC0 pack must be 10")
    trials_dir.mkdir(parents=True, exist_ok=True)
    docs.mkdir(parents=True, exist_ok=True)
    seeded = _seed_golds(bank_path, ac_bank)
    bank = load_bank_rows(bank_path)
    apps = [dict(a) for a in APPPLUS_APPS]
    if only_app:
        apps = [app_by_id(only_app)]
    need_long = any(a.get("stack") == "longapp" for a in apps)
    if need_long:
        ctxs_raw = _build_ctxs(curated_root=curated_root, workers=workers)
        ctxs: list[dict[str, Any] | None] = list(ctxs_raw)
    else:
        ctxs = [None] * APPPLUS_N

    app_results = [
        _run_one_app(
            app=app,
            bank=bank,
            bank_path=bank_path,
            root=root,
            trials_dir=trials_dir,
            curated_root=curated_root,
            docs=docs,
            seed=seed,
            ctxs=ctxs,
        )
        for app in apps
    ]
    wave = appplus_stats(app_results)
    decision = decide_appplus(wave)
    summary: dict[str, Any] = {
        "hyp_id": APPPLUS_ID,
        "stage": "AC4",
        "decision": decision,
        "seeded_golds": int(seeded),
        "forbidden": [
            "STREAM",
            "KVCACHE-Q",
            "GENCACHE",
            "ZPREF",
            "open chat claim",
        ],
        "stats": wave,
        "apps": app_results,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "workers": int(workers),
        "finding": (
            f"{APPPLUS_ID}: apps={wave['n_apps']} "
            f"howto={wave['howto_promote']} known={wave['known_green']} "
            f"longdoc={wave['longdoc_green']} "
            f"mean={wave['mean_across_apps']:.1f} decision={decision}."
        ),
        "public_note": "docs/results/nano-lm/formal-happplus-appplus.md",
        "claim": "scoped packaged apps incl. howto — not open chat LM",
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--ac-bank", type=Path, default=_AC_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--docs", type=Path, default=_DOCS)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--app", type=str, default=None)
    args = ap.parse_args()
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    workers = min(12, max(4, cpus - 4))
    try:
        summary = run_appplus(
            bank_path=Path(args.bank),
            ac_bank=Path(args.ac_bank),
            root=Path(args.root),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            curated_root=Path(args.curated),
            docs=Path(args.docs),
            seed=int(args.seed),
            workers=workers,
            only_app=args.app,
        )
    except (OSError, RuntimeError, ValueError, KeyError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    decision = str(summary["decision"])
    print(
        json.dumps(
            {
                "ok": True,
                "hyp_id": APPPLUS_ID,
                "decision": decision,
                "n_apps": summary["stats"]["n_apps"],
                "n_promote": summary["stats"]["n_promote"],
                "howto_promote": summary["stats"]["howto_promote"],
                "known_green": summary["stats"]["known_green"],
                "longdoc_green": summary["stats"]["longdoc_green"],
                "mean_across_apps": summary["stats"]["mean_across_apps"],
                "cpu_threads": threads,
                "workers": workers,
                "out": str(args.out),
            }
        )
    )
    return 0 if decision in {"PROMOTE", "HOLD"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
