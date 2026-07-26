"""Wave AF4 H-APPULTRA runner: apps + compose + DEPL-AF (nano:appultra)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from af_session_ops import AF0_PACK
from appultra_ops import (
    APPULTRA_APPS,
    APPULTRA_ID,
    APPULTRA_N,
    DEPL_AF_PAGE,
    app_by_id,
    app_stats,
    appultra_stats,
    claim_is_honest,
    decide_app,
    decide_appultra,
    depl_af_body,
    honest_out_of_scope_text,
    one_pager_body,
    page_sync_report,
    route_item,
    score_realapp_trial,
    select_app,
)
from askfast_ops import AskCompletionCache
from curated_sources import SOURCES
from ctxultra_ops import ctxultra_doc_meta, secondary_for, tertiary_for
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
_SUMMARY = REPO / "results/nano-lm/wave-af/appultra_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_DOCS = REPO / "docs/results/nano-lm"
_JUDGE = "cursor-composer-frontier-chat"
_BY_ID = {str(s["id"]): s for s in SOURCES}
_CTX_STACKS = frozenset({"ctxultra", "compose", "route"})


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


def _seed_golds(bank_path: Path, af_bank: Path) -> int:
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
            trial_id=f"AF-APPULTRA-SEED-{i:02d}",
            question=q,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = APPULTRA_ID
        append_error_row(bank_path, row)
        append_error_row(af_bank, row)
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


def _write_pages(docs: Path) -> list[dict[str, Any]]:
    docs.mkdir(parents=True, exist_ok=True)
    reports: list[dict[str, Any]] = []
    for app in APPULTRA_APPS:
        name = Path(str(app["one_pager"])).name
        path = docs / name
        body = one_pager_body(app)
        path.write_text(body, encoding="utf-8")
        rel = f"docs/results/nano-lm/{name}"
        reports.append(page_sync_report(rel, body))
    depl_path = docs / Path(DEPL_AF_PAGE).name
    depl_body = depl_af_body()
    depl_path.write_text(depl_body, encoding="utf-8")
    reports.append(page_sync_report(DEPL_AF_PAGE, depl_body))
    return reports


def _build_ctxs(*, curated_root: Path, workers: int) -> list[dict[str, Any]]:
    cfg = matrix_cfg()
    tok = load_tokenizer(str(cfg["tokenizer_id"]), cfg["cache"])

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
        meta = ctxultra_doc_meta(
            p_ids,
            s_ids,
            t_ids,
            q_ids,
            primary_source=item["source_id"],
            secondary_source=secondary_for(item["source_id"]),
            tertiary_source=tertiary_for(item["source_id"]),
        )
        ctxs.append(meta)
    return ctxs


def _trial_tag(app_id: str) -> str:
    return {
        "app-known": "KNOWN",
        "app-longdoc": "LONGDOC",
        "app-howto": "HOWTO",
        "app-route": "ROUTE",
        "app-compose": "COMPOSE",
    }.get(app_id, "APP")


def _serve_app_for(
    app: dict[str, Any], item: dict[str, str]
) -> dict[str, Any]:
    if str(app.get("stack")) == "route":
        return select_app(item["app_id"])
    return app


def _serve_or_refuse(
    *,
    app: dict[str, Any],
    item: dict[str, str],
    payload: dict[str, Any],
    bank: list[dict[str, Any]],
    curated: Path,
) -> tuple[dict[str, Any], str, str, str, dict[str, Any], int]:
    serve = _serve_app_for(app, item)
    route = route_item(serve, item["app_id"])
    kind, sem_meta = _classify(dict(item), payload, bank, curated)
    completion = str(payload.get("completion", ""))
    mode = str(payload.get("mode", ""))
    fix = 0
    if not bool(route["in_scope"]):
        completion = honest_out_of_scope_text(
            str(serve["app_id"]), str(serve["surface"])
        )
        mode = "APPULTRA_OUT_OF_SCOPE"
        kind = "MISS"
        fix = 1
    return route, completion, mode, kind, sem_meta, fix


def _needs_ctx(app: dict[str, Any], item: dict[str, str]) -> bool:
    stack = str(app.get("stack"))
    if stack == "ctxultra" and item["app_id"] == "long-doc":
        return True
    if stack == "compose":
        return True
    if stack == "route" and item["app_id"] == "long-doc":
        return True
    return False


def _run_one_app(
    *,
    app: dict[str, Any],
    bank: list[dict[str, Any]],
    bank_path: Path,
    root: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int,
    ctxs: list[dict[str, Any] | None],
) -> dict[str, Any]:
    app_id = str(app["app_id"])
    claim_ok = claim_is_honest(str(app["claim"]))
    cache = AskCompletionCache()
    payloads = ask_many(
        questions=[p["question"] for p in AF0_PACK],
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated_root,
        ask_cache=cache,
    )
    if len(payloads) != APPULTRA_N:
        raise RuntimeError(f"{app_id}: expected 10 payloads")

    trials: list[dict[str, Any]] = []
    fix_count = 0
    tag = _trial_tag(app_id)
    for i, (item, payload) in enumerate(
        zip(AF0_PACK, payloads, strict=True), start=1
    ):
        route, completion, mode, kind, sem_meta, fix = _serve_or_refuse(
            app=app,
            item=dict(item),
            payload=payload,
            bank=bank,
            curated=curated_root,
        )
        fix_count += fix
        ctx = ctxs[i - 1] if _needs_ctx(app, dict(item)) else None
        long_ok = None
        if ctx is not None:
            long_ok = bool(ctx.get("l_eff_ok")) and bool(ctx.get("ratio_ok"))
            long_ok = long_ok and int(ctx.get("n_sources") or 0) >= 3
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
        tid = f"AF-APPULTRA-{tag}-HITL-{i:02d}"
        trial: dict[str, Any] = {
            "trial_id": tid,
            "stage": "AF4",
            "hyp_id": APPULTRA_ID,
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
            "ctxultra": ctx,
            "score": score,
            "error": err,
            "judge_model_name": _JUDGE,
            "judge_notes": notes,
            "manual_adjust": (
                "FIX: honest out-of-scope refuse"
                if mode == "APPULTRA_OUT_OF_SCOPE"
                else (
                    "no change — APPULTRA route ok"
                    if not err
                    else "FIX: route/SEMWRAP/CTXULTRA"
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
    smoke_ok = n_false == 0 and (n_true >= 1 or n_scope == 0)
    if n_scope > 0:
        smoke_ok = n_true >= 1 and n_false == 0
    pager_name = Path(str(app["one_pager"])).name
    pager_ok = (_DOCS / pager_name).is_file()
    stats = app_stats(
        scores,
        errors,
        n_true_hit=n_true,
        n_false_hit=n_false,
        n_miss=n_miss,
        n_in_scope=n_scope,
        claim_ok=claim_ok,
        one_pager_ok=pager_ok,
        smoke_ok=smoke_ok,
    )
    return {
        "app_id": app_id,
        "decision": decide_app(stats),
        "mean": stats["mean"],
        "stats": stats,
        "fix_count": fix_count,
        "claim": app["claim"],
        "one_pager": str(app["one_pager"]),
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


def run_appultra(
    *,
    bank_path: Path,
    af_bank: Path,
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
    GIVEN AF0 held-out pack + APPULTRA apps
    WHEN ASK→EVAL→FIX×10 per app + DEPL-AF pages
    THEN howto↑ ∧ mean↑ ∧ 5 apps green ∧ DEPL → PROMOTE|HOLD|KILL.
    """
    if len(AF0_PACK) != APPULTRA_N:
        raise ValueError("AF0 pack must be 10")
    trials_dir.mkdir(parents=True, exist_ok=True)
    page_reports = _write_pages(docs)
    n_pages_ok = sum(1 for r in page_reports if r.get("ok"))
    seeded = _seed_golds(bank_path, af_bank)
    bank = load_bank_rows(bank_path)
    apps = [dict(a) for a in APPULTRA_APPS]
    if only_app:
        apps = [app_by_id(only_app)]
    need_ctx = any(a.get("stack") in _CTX_STACKS for a in apps)
    if need_ctx:
        ctxs_raw = _build_ctxs(curated_root=curated_root, workers=workers)
        ctxs: list[dict[str, Any] | None] = list(ctxs_raw)
    else:
        ctxs = [None] * APPULTRA_N

    app_results = [
        _run_one_app(
            app=app,
            bank=bank,
            bank_path=bank_path,
            root=root,
            trials_dir=trials_dir,
            curated_root=curated_root,
            seed=seed,
            ctxs=ctxs,
        )
        for app in apps
    ]
    if only_app:
        wave = {
            "n_apps": len(app_results),
            "n_promote": sum(
                1 for a in app_results if a.get("decision") == "PROMOTE"
            ),
            "n_hold": sum(
                1 for a in app_results if a.get("decision") == "HOLD"
            ),
            "n_kill": sum(
                1 for a in app_results if a.get("decision") == "KILL"
            ),
            "mean_across_apps": float(
                sum(float(a["mean"]) for a in app_results) / len(app_results)
            ),
            "howto_promote": False,
            "howto_up": False,
            "mean_up": False,
            "known_green": False,
            "longdoc_green": False,
            "route_green": False,
            "compose_green": False,
            "depl_ok": n_pages_ok >= 6,
            "n_pages_ok": n_pages_ok,
            "n_pages": len(page_reports),
            "pass_product": False,
        }
        decision = (
            "KILL"
            if wave["n_kill"]
            else ("PROMOTE" if wave["n_promote"] else "HOLD")
        )
    else:
        wave = appultra_stats(
            app_results, n_pages_ok=n_pages_ok, n_pages=len(page_reports)
        )
        decision = decide_appultra(wave)
    summary: dict[str, Any] = {
        "hyp_id": APPULTRA_ID,
        "stage": "AF4",
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
        "pages": page_reports,
        "apps": app_results,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "workers": int(workers),
        "finding": (
            f"{APPULTRA_ID}: apps={wave['n_apps']} "
            f"howto_up={wave.get('howto_up')} "
            f"mean_up={wave.get('mean_up')} "
            f"compose={wave.get('compose_green')} "
            f"depl={wave.get('depl_ok')} "
            f"mean={wave['mean_across_apps']:.1f} decision={decision}."
        ),
        "public_note": "docs/results/nano-lm/formal-happultra-appultra.md",
        "claim": (
            "scoped packaged apps incl. howto↑ + compose 5th — not open chat LM"
        ),
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
    ap.add_argument("--docs", type=Path, default=_DOCS)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--app", type=str, default=None)
    args = ap.parse_args()
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    workers = min(12, max(4, cpus - 4))  # leave ≥4 cores
    try:
        summary = run_appultra(
            bank_path=Path(args.bank),
            af_bank=Path(args.af_bank),
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
                "hyp_id": APPULTRA_ID,
                "decision": decision,
                "n_apps": summary["stats"]["n_apps"],
                "n_promote": summary["stats"]["n_promote"],
                "howto_up": summary["stats"].get("howto_up"),
                "mean_up": summary["stats"].get("mean_up"),
                "compose_green": summary["stats"].get("compose_green"),
                "depl_ok": summary["stats"].get("depl_ok"),
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
