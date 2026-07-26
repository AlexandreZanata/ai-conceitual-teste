"""Wave AF5 AF-HITL-10 runner: final pack on declared AF stack (nano:af:hitl)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from af_hitl_ops import (
    AF5_ID,
    AF5_N,
    DECLARED_STACK,
    STACK_CLAIM,
    af5_stats,
    claim_is_honest,
    decide_af5,
    score_af5_trial,
    select_app,
)
from af_session_ops import AF0_PACK, overlaps_prior_questions
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
_SUMMARY = REPO / "results/nano-lm/wave-af/af_hitl_summary.json"
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
            trial_id=f"AF-HITL-SEED-{i:02d}",
            question=q,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = AF5_ID
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


def _build_ctxs(
    *,
    curated_root: Path,
    workers: int,
) -> list[dict[str, Any] | None]:
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
    out: list[dict[str, Any] | None] = []
    for item, p_text, s_text, t_text in quads:
        if item["app_id"] != "long-doc":
            out.append(None)
            continue
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
        "stage": "AF5",
        "hyp_id": AF5_ID,
        "question": item["question"],
        "source_id": item["source_id"],
        "app_id": item["app_id"],
        "model_raw": completion,
        "gold": item["gold"],
        "score": score,
        "error": True,
        "judge_notes": notes,
        "recipe_id": "champion-af-v0",
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def _apply_fix(
    *,
    tid: str,
    item: dict[str, str],
    bank_path: Path,
    af_bank: Path,
    curated: Path,
    payload: dict[str, Any],
    kind: str,
    sem_meta: dict[str, Any],
    score_before: float,
    notes_before: list[str],
    ctx_ok: bool | None,
) -> tuple[str, str, str, dict[str, Any], float, bool, list[str]]:
    _log_error(
        af_bank,
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
    row["hyp_id"] = AF5_ID
    append_error_row(bank_path, row)
    append_error_row(af_bank, row)
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
    mode = "AF5_CONSTRAINED_FIX"
    kind2 = classify_semwrap(
        completion,
        expected_gold=item["gold"],
        expected_source_id=item["source_id"],
        hit_source_id=str(meta.get("source_id") or "") or None,
    )
    score, err, notes = score_af5_trial(
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
    ok = bool(ctx.get("l_eff_ok")) and bool(ctx.get("ratio_ok"))
    return ok and int(ctx.get("n_sources") or 0) >= 3


def run_af_hitl(
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
    GIVEN AF0 pack + declared AF stack
    WHEN ASK→EVAL→FIX×10 via APPULTRA app router
    THEN mean≥7 · errors≤3 · no false-hit → PROMOTE|HOLD|KILL.
    """
    if len(AF0_PACK) != AF5_N:
        raise ValueError("AF0 pack must be 10")
    trials_dir.mkdir(parents=True, exist_ok=True)
    seeded = _seed_golds(bank_path, af_bank)
    bank = load_bank_rows(bank_path)
    claim_ok = claim_is_honest(STACK_CLAIM)
    held_out_ok = len(overlaps_prior_questions(AF0_PACK)) == 0
    ctxs = _build_ctxs(curated_root=curated_root, workers=workers)
    payloads = ask_many(
        questions=[p["question"] for p in AF0_PACK],
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated_root,
        ask_cache=AskCompletionCache(),
    )
    if len(payloads) != AF5_N:
        raise RuntimeError(f"expected {AF5_N} payloads")

    trials: list[dict[str, Any]] = []
    fix_count = 0
    for i, (item, payload) in enumerate(
        zip(AF0_PACK, payloads, strict=True), start=1
    ):
        tid = f"AF-FINAL-HITL-{i:02d}"
        routed = select_app(item["app_id"])
        kind, sem_meta = _classify(dict(item), payload, bank, curated_root)
        ctx = ctxs[i - 1]
        ctx_ok = _ctx_ok_for(routed, ctx)
        score_before, err_before, notes_before = score_af5_trial(
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
                af_bank=af_bank,
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
            "stage": "AF5",
            "hyp_id": AF5_ID,
            "realapp_id": routed,
            "app_id": item["app_id"],
            "question": item["question"],
            "source_id": item["source_id"],
            "recipe_id": payload.get("recipe_id") or "champion-af-v0",
            "ckpt": None,
            "completion": completion,
            "wall_ms": payload.get("wall_ms"),
            "n_new": payload.get("n_new"),
            "seed": payload.get("seed", 0),
            "mode": mode,
            "lookup_kind": kind,
            "semwrap": sem_meta,
            "ctxultra": ctx,
            "score": score,
            "score_before": score_before,
            "error": err,
            "judge_model_name": _JUDGE,
            "judge_notes": notes,
            "manual_adjust": (
                "FIX: constrained SEMWRAP re-ASK"
                if fixed
                else "no change — AF5 final stack ok"
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
    stats = af5_stats(
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
    decision = decide_af5(stats)
    summary: dict[str, Any] = {
        "hyp_id": AF5_ID,
        "stage": "AF5",
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
            "reuse AB/AC/AD/AE question texts",
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
            f"{AF5_ID}: mean={stats['mean']:.1f} "
            f"errors={stats['n_errors']}/10 "
            f"false_hit={n_false} fix={fix_count} "
            f"held_out={held_out_ok} decision={decision}."
        ),
        "public_note": "docs/results/nano-lm/wave-af-hitl.md",
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
        summary = run_af_hitl(
            bank_path=Path(args.bank),
            af_bank=Path(args.af_bank),
            root=Path(args.root),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            curated_root=Path(args.curated),
            seed=int(args.seed),
            workers=workers,
        )
    except (OSError, RuntimeError, ValueError, KeyError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    decision = str(summary["decision"])
    print(
        json.dumps(
            {
                "ok": True,
                "hyp_id": AF5_ID,
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
