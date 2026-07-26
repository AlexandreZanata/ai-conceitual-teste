"""Wave AL5 H-APPFRESH runner: dual-arm apps + DEPL-AL (nano:appfresh)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from al_session_ops import AL0_PACK
from antifp_ops import classify_arm, extract_telemetry
from appfresh_ops import (
    APPFRESH_APPS,
    APPFRESH_ID,
    APPFRESH_N,
    DEPL_AL_PAGE,
    app_by_id,
    app_dual_stats,
    appfresh_stats,
    claim_is_honest,
    decide_app,
    decide_appfresh,
    depl_al_body,
    honest_out_of_scope_text,
    one_pager_body,
    page_sync_report,
    route_item,
    score_appfresh_gen,
    score_appfresh_lookup,
)
from askfast_ops import AskCompletionCache
from matrix_common import REPO, write_json
from run_genfresh import _run_gen_ablation
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row, classify_semwrap, semantic_lookup
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AL_BANK = REPO / "results/nano-lm/wave-al/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-al/trials"
_SUMMARY = REPO / "results/nano-lm/wave-al/appfresh_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_DOCS = REPO / "docs/results/nano-lm"
_JUDGE = "cursor-composer-frontier-chat"
MIN_PAGES_SINGLE = 1


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


def _seed_pack(bank_path: Path, al_bank: Path) -> int:
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    al_bank.parent.mkdir(parents=True, exist_ok=True)
    if not al_bank.is_file():
        al_bank.write_text("", encoding="utf-8")
    existing = {
        str(r.get("question", "")).strip() for r in load_bank_rows(bank_path)
    }
    n = 0
    for i, item in enumerate(AL0_PACK, start=1):
        q = str(item["question"]).strip()
        if q in existing:
            continue
        row = alias_bank_row(
            trial_id=f"AL-APPFRESH-SEED-{i:02d}",
            question=q,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = APPFRESH_ID
        row["judge_notes"] = [
            "APPFRESH seed for AL held-out ask",
            "LOOKUP product path — not generative IQ",
            "no student weight update",
        ]
        append_error_row(bank_path, row)
        append_error_row(al_bank, row)
        existing.add(q)
        n += 1
    return n


def _write_pages(docs: Path) -> list[dict[str, Any]]:
    docs.mkdir(parents=True, exist_ok=True)
    reports: list[dict[str, Any]] = []
    for app in APPFRESH_APPS:
        name = Path(str(app["one_pager"])).name
        path = docs / name
        body = one_pager_body(app)
        path.write_text(body, encoding="utf-8")
        rel = f"docs/results/nano-lm/{name}"
        reports.append(page_sync_report(rel, body))
    depl_path = docs / Path(DEPL_AL_PAGE).name
    depl_body = depl_al_body()
    depl_path.write_text(depl_body, encoding="utf-8")
    reports.append(page_sync_report(DEPL_AL_PAGE, depl_body))
    return reports


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


def _trial_tag(app_id: str) -> str:
    return {
        "app-known": "KNOWN",
        "app-howto": "HOWTO",
        "app-longdoc": "LONGDOC",
    }.get(app_id, "APP")


def _run_one_app(
    *,
    app: dict[str, Any],
    bank: list[dict[str, Any]],
    bank_path: Path,
    al_bank: Path,
    root: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int,
    shared_gen: list[dict[str, Any]],
) -> dict[str, Any]:
    app_id = str(app["app_id"])
    claim_ok = claim_is_honest(str(app["claim"]))
    questions = [p["question"] for p in AL0_PACK]
    tag = _trial_tag(app_id)

    lookup_payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated_root,
        ask_cache=AskCompletionCache(),
    )
    if len(lookup_payloads) != APPFRESH_N or len(shared_gen) != APPFRESH_N:
        raise RuntimeError(f"{app_id}: expected 10 dual-arm payloads")

    lookup_trials: list[dict[str, Any]] = []
    gen_trials: list[dict[str, Any]] = []
    fix_count = 0
    n_lookup_labeled = 0
    n_gen_wall_ok = 0
    n_in_scope = 0

    for i, item in enumerate(AL0_PACK, start=1):
        route = route_item(app, item["app_id"])
        if bool(route["in_scope"]):
            n_in_scope += 1

        l_pay = dict(lookup_payloads[i - 1])
        kind, sem_meta = _classify(dict(item), l_pay, bank, curated_root)
        l_comp = str(l_pay.get("completion", ""))
        l_mode = str(l_pay.get("mode", ""))
        if not bool(route["in_scope"]):
            l_comp = honest_out_of_scope_text(app_id, str(app["surface"]))
            l_mode = "APPFRESH_OUT_OF_SCOPE"
            kind = "MISS"
            fix_count += 1
            l_pay = {
                **l_pay,
                "completion": l_comp,
                "mode": l_mode,
                "wall_ms": 0.0,
                "n_new": 0,
            }
        elif kind != "TRUE_HIT":
            row = alias_bank_row(
                trial_id=f"AL-APPFRESH-FIX-{tag}-{i:02d}",
                question=item["question"],
                source_id=item["source_id"],
                gold=item["gold"],
            )
            row["hyp_id"] = APPFRESH_ID
            append_error_row(bank_path, row)
            append_error_row(al_bank, row)
            bank = load_bank_rows(bank_path)
            fix_count += 1
            l_pay = ask_many(
                questions=[item["question"]],
                root=root,
                seed=seed,
                askfast=True,
                bank_path=bank_path,
                curated_root=curated_root,
                ask_cache=AskCompletionCache(),
            )[0]
            kind, sem_meta = _classify(
                dict(item), l_pay, bank, curated_root
            )
            l_comp = str(l_pay.get("completion", ""))
            l_mode = str(l_pay.get("mode", ""))

        l_score, l_err, l_notes = score_appfresh_lookup(
            mode=l_mode,
            completion=l_comp,
            expected_gold=str(item["gold"]),
            lookup_kind=kind,
            route=route,
            payload=l_pay,
        )
        if bool(route["in_scope"]) and classify_arm(l_pay) == "LOOKUP":
            n_lookup_labeled += 1
        l_tel = extract_telemetry(l_pay)
        l_trial = {
            "trial_id": f"AL-APPFRESH-{tag}-LOOKUP-HITL-{i:02d}",
            "stage": "AL5",
            "hyp_id": APPFRESH_ID,
            "arm": "LOOKUP",
            "realapp_id": app_id,
            "app_id": item["app_id"],
            "question": item["question"],
            "source_id": item["source_id"],
            "completion": l_comp,
            "mode": l_tel["mode"] if bool(route["in_scope"]) else l_mode,
            "wall_ms": l_tel["wall_ms"],
            "n_new": l_tel["n_new"],
            "lookup_kind": kind,
            "semwrap": sem_meta,
            "route": route,
            "score": l_score,
            "error": l_err,
            "judge_model_name": _JUDGE,
            "judge_notes": l_notes,
            "gold": str(item["gold"]).strip(),
            "weight_update": False,
        }
        write_json(trials_dir / f"{l_trial['trial_id']}.json", l_trial)
        lookup_trials.append(l_trial)

        g_pay = dict(shared_gen[i - 1])
        if not bool(route["in_scope"]):
            g_comp = honest_out_of_scope_text(app_id, str(app["surface"]))
            g_pay = {
                "completion": g_comp,
                "mode": "APPFRESH_OUT_OF_SCOPE",
                "wall_ms": 0.0,
                "n_new": 0,
            }
            fix_count += 1
        else:
            tel = extract_telemetry(g_pay)
            if tel["wall_ms"] > 0.0 and tel["n_new"] > 0:
                n_gen_wall_ok += 1

        g_score, g_err, g_notes = score_appfresh_gen(
            completion=str(g_pay.get("completion", "")),
            expected_gold=str(item["gold"]),
            route=route,
            payload=g_pay,
        )
        g_tel = extract_telemetry(g_pay)
        g_trial = {
            "trial_id": f"AL-APPFRESH-{tag}-GEN-HITL-{i:02d}",
            "stage": "AL5",
            "hyp_id": APPFRESH_ID,
            "arm": "GENERATE",
            "realapp_id": app_id,
            "app_id": item["app_id"],
            "question": item["question"],
            "source_id": item["source_id"],
            "completion": g_pay.get("completion"),
            "mode": g_tel["mode"]
            if bool(route["in_scope"])
            else "APPFRESH_OUT_OF_SCOPE",
            "wall_ms": g_tel["wall_ms"],
            "n_new": g_tel["n_new"],
            "peak_used": bool(g_pay.get("peak_used")),
            "route": route,
            "score": g_score,
            "error": g_err,
            "judge_model_name": _JUDGE,
            "judge_notes": g_notes,
            "gold": str(item["gold"]).strip(),
            "weight_update": False,
        }
        write_json(trials_dir / f"{g_trial['trial_id']}.json", g_trial)
        gen_trials.append(g_trial)

    n_true = sum(1 for t in lookup_trials if t["lookup_kind"] == "TRUE_HIT")
    n_false = sum(
        1 for t in lookup_trials if t["lookup_kind"] == "FALSE_HIT"
    )
    serve_gen = [
        float(t["score"])
        for t in gen_trials
        if bool(t["route"]["in_scope"])
    ]
    pager_name = Path(str(app["one_pager"])).name
    pager_ok = (_DOCS / pager_name).is_file()
    stats = app_dual_stats(
        lookup_scores=[float(t["score"]) for t in lookup_trials],
        lookup_errors=[bool(t["error"]) for t in lookup_trials],
        gen_scores=[float(t["score"]) for t in gen_trials],
        gen_errors=[bool(t["error"]) for t in gen_trials],
        serve_gen_scores=serve_gen,
        n_true_hit=n_true,
        n_false_hit=n_false,
        n_lookup_labeled=n_lookup_labeled,
        n_gen_wall_ok=n_gen_wall_ok,
        n_in_scope=n_in_scope,
        claim_ok=claim_ok,
        one_pager_ok=pager_ok,
    )
    return {
        "app_id": app_id,
        "decision": decide_app(stats),
        "lookup_mean": stats["lookup_mean"],
        "gen_mean": stats["gen_mean"],
        "dual_arm_ok": stats["dual_arm_ok"],
        "stats": stats,
        "fix_count": fix_count,
        "claim": app["claim"],
        "one_pager": str(app["one_pager"]),
        "npm": app["npm"],
        "spine": list(app["spine"]),
        "lookup_trials": [
            {
                "trial_id": t["trial_id"],
                "route": t["route"]["route"],
                "lookup_kind": t["lookup_kind"],
                "mode": t["mode"],
                "score": t["score"],
                "wall_ms": t["wall_ms"],
            }
            for t in lookup_trials
        ],
        "gen_trials": [
            {
                "trial_id": t["trial_id"],
                "route": t["route"]["route"],
                "mode": t["mode"],
                "score": t["score"],
                "wall_ms": t["wall_ms"],
                "n_new": t["n_new"],
                "peak_used": t.get("peak_used"),
                "completion": str(t.get("completion") or "")[:80],
            }
            for t in gen_trials
        ],
    }


def run_appfresh(
    *,
    bank_path: Path,
    al_bank: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    docs: Path,
    seed: int = 0,
    only_app: str | None = None,
) -> dict[str, Any]:
    """
    GIVEN AL0 pack + APPFRESH apps
    WHEN ASK→EVAL→FIX×10 dual-arm per surface + DEPL-AL
    THEN expose LOOKUP|GENERATE ∧ DEPL → PROMOTE|HOLD|KILL.
    """
    if len(AL0_PACK) != APPFRESH_N:
        raise ValueError("AL0 pack must be 10")
    trials_dir.mkdir(parents=True, exist_ok=True)
    page_reports = _write_pages(docs)
    n_pages_ok = sum(1 for r in page_reports if r.get("ok"))
    seeded = _seed_pack(bank_path, al_bank)
    bank = load_bank_rows(bank_path)
    apps = [dict(a) for a in APPFRESH_APPS]
    if only_app:
        apps = [app_by_id(only_app)]

    # Shared GENFRESH peak GENERATE once — max HW without 3× CUDA reload.
    gen_items = [dict(p) for p in AL0_PACK]
    _ablated, shared_gen = _run_gen_ablation(
        champ=root,
        items=gen_items,
        curated=curated_root,
        seed=seed,
        k_retrieve=6,
    )
    del _ablated

    app_results = [
        _run_one_app(
            app=app,
            bank=bank,
            bank_path=bank_path,
            al_bank=al_bank,
            root=root,
            trials_dir=trials_dir,
            curated_root=curated_root,
            seed=seed,
            shared_gen=shared_gen,
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
            "lookup_mean_across": float(app_results[0]["lookup_mean"]),
            "gen_mean_across": float(app_results[0]["gen_mean"]),
            "dual_arm_all": bool(app_results[0]["dual_arm_ok"]),
            "depl_ok": n_pages_ok >= MIN_PAGES_SINGLE,
            "n_pages_ok": n_pages_ok,
            "n_pages": len(page_reports),
            "pass_expose": False,
            "pass_lookup": False,
            "pass_gen": False,
            "pass_product": False,
            "beats_apppush_gen": float(app_results[0]["gen_mean"]) > 4.0,
        }
        decision = (
            "KILL"
            if wave["n_kill"]
            else ("PROMOTE" if wave["n_promote"] else "HOLD")
        )
    else:
        wave = appfresh_stats(
            app_results, n_pages_ok=n_pages_ok, n_pages=len(page_reports)
        )
        decision = decide_appfresh(wave)

    summary: dict[str, Any] = {
        "hyp_id": APPFRESH_ID,
        "stage": "AL5",
        "decision": decision,
        "seeded_golds": int(seeded),
        "forbidden": [
            "STREAM",
            "KVCACHE-Q",
            "GENCACHE",
            "ZPREF",
            "LOOKUP-only smarter LM",
            "open chat claim",
            "peak-as-open-chat-IQ",
        ],
        "stats": wave,
        "pages": page_reports,
        "apps": [
            {
                "app_id": a["app_id"],
                "decision": a["decision"],
                "lookup_mean": a["lookup_mean"],
                "gen_mean": a["gen_mean"],
                "dual_arm_ok": a["dual_arm_ok"],
                "fix_count": a["fix_count"],
                "one_pager": a["one_pager"],
            }
            for a in app_results
        ],
        "app_detail": app_results,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "finding": (
            f"{APPFRESH_ID}: apps={wave['n_apps']} "
            f"L={wave.get('lookup_mean_across', 0):.1f} "
            f"G={wave.get('gen_mean_across', 0):.1f} "
            f"expose={wave.get('pass_expose')} "
            f"depl={wave.get('depl_ok')} "
            f"beats_apppush={wave.get('beats_apppush_gen')} → {decision}"
        ),
        "public_note": "docs/results/nano-lm/formal-happfresh-appfresh.md",
        "ship_claim": "AF packaged stack until AL6 gen bar",
        "claim": (
            "scoped apps expose LOOKUP vs GENERATE — not open chat LM"
        ),
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--al-bank", type=Path, default=_AL_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--docs", type=Path, default=_DOCS)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--app", type=str, default=None)
    args = ap.parse_args()
    cpus = int(os.cpu_count() or 4)
    # Max safe: leave 2 cores free (CUDA gen + LOOKUP).
    threads = tune_cpu_threads(max(4, cpus - 2))
    try:
        summary = run_appfresh(
            bank_path=Path(args.bank),
            al_bank=Path(args.al_bank),
            root=Path(args.root),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            curated_root=Path(args.curated),
            docs=Path(args.docs),
            seed=int(args.seed),
            only_app=args.app,
        )
    except (OSError, RuntimeError, ValueError, KeyError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    decision = str(summary["decision"])
    st = summary["stats"]
    print(
        json.dumps(
            {
                "ok": True,
                "hyp_id": APPFRESH_ID,
                "decision": decision,
                "n_apps": st["n_apps"],
                "n_promote": st.get("n_promote"),
                "n_hold": st.get("n_hold"),
                "lookup_mean_across": st.get("lookup_mean_across"),
                "gen_mean_across": st.get("gen_mean_across"),
                "pass_expose": st.get("pass_expose"),
                "pass_gen": st.get("pass_gen"),
                "beats_apppush_gen": st.get("beats_apppush_gen"),
                "depl_ok": st.get("depl_ok"),
                "cpu_threads": threads,
                "out": str(args.out),
            }
        )
    )
    return 0 if decision in {"PROMOTE", "HOLD"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
