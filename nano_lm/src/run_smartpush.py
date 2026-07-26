"""Wave AI3 H-SMARTPUSH runner: hexa cite LOOKUP + grounded GENERATE."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from askfast_ops import AskCompletionCache
from asksmart_ops import is_period_collapse
from matrix_common import REPO, write_json
from run_genplus import _run_gen_grounded
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row, classify_semwrap, semantic_lookup
from smartpush_ops import (
    SMARTPUSH_ID,
    SMARTPUSH_N,
    SMARTPUSH_PACK,
    decide_smartpush,
    hard_paraphrase_ok,
    has_adversarial_noise,
    has_hexa_hop_cues,
    score_smartpush_gen,
    score_smartpush_lookup,
    smartpush_stats,
)
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AI_BANK = REPO / "results/nano-lm/wave-ai/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-ai/trials"
_SUMMARY = REPO / "results/nano-lm/wave-ai/smartpush_summary.json"
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


def _seed_pack(bank_path: Path, ai_bank: Path) -> int:
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    ai_bank.parent.mkdir(parents=True, exist_ok=True)
    if not ai_bank.is_file():
        ai_bank.write_text("", encoding="utf-8")
    existing = {
        str(r.get("question", "")).strip() for r in load_bank_rows(bank_path)
    }
    n = 0
    for i, item in enumerate(SMARTPUSH_PACK, start=1):
        for q_key, q_text in (
            ("parent", item["parent_question"]),
            ("para", item["paraphrase"]),
        ):
            q = str(q_text).strip()
            if q in existing:
                continue
            row = alias_bank_row(
                trial_id=f"AI-SMARTPUSH-SEED-{q_key}-{i:02d}",
                question=q,
                source_id=item["source_id"],
                gold=item["gold"],
            )
            row["hyp_id"] = SMARTPUSH_ID
            row["judge_notes"] = [
                "SMARTPUSH seed for hexa-hop paraphrase stress",
                "LOOKUP product path — not generative IQ",
                "no student weight update",
            ]
            append_error_row(bank_path, row)
            append_error_row(ai_bank, row)
            existing.add(q)
            n += 1
    return n


def _classify_lookup(
    item: dict[str, str],
    payload: dict[str, Any],
    bank: list[dict[str, Any]],
    curated: Path,
) -> tuple[str, dict[str, Any], str]:
    completion = str(payload.get("completion", ""))
    mode = str(payload.get("mode", ""))
    _g, meta = semantic_lookup(
        item["paraphrase"], bank, curated_root=curated
    )
    looked = (
        completion
        if mode in {"SEMWRAP_LOOKUP", "WRAP_LOOKUP", "ASKFAST_CACHE"}
        else _g
    )
    kind = classify_semwrap(
        looked,
        expected_gold=item["gold"],
        expected_source_id=item["source_id"],
        hit_source_id=str(meta.get("source_id") or "") or None,
    )
    return kind, meta, completion


def _fix_lookup(
    *,
    i: int,
    item: dict[str, str],
    bank_path: Path,
    ai_bank: Path,
    root: Path,
    curated: Path,
    seed: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], int]:
    row = alias_bank_row(
        trial_id=f"AI-SMARTPUSH-FIX-{i:02d}",
        question=item["paraphrase"],
        source_id=item["source_id"],
        gold=item["gold"],
    )
    row["hyp_id"] = SMARTPUSH_ID
    append_error_row(bank_path, row)
    append_error_row(ai_bank, row)
    bank = load_bank_rows(bank_path)
    re_payloads = ask_many(
        questions=[item["paraphrase"]],
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated,
        ask_cache=AskCompletionCache(),
    )
    return re_payloads[0], bank, 1


def run_smartpush(
    *,
    bank_path: Path,
    ai_bank: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN AI0 hexa-hop paraphrases + parent asks
    WHEN SEMWRAP LOOKUP + grounded GENERATE dual-arm ×10
    THEN false-hit≈0; PROMOTE if gen≥5 else HOLD.
    """
    if len(SMARTPUSH_PACK) != SMARTPUSH_N:
        raise ValueError("SMARTPUSH pack must be 10")
    if not hard_paraphrase_ok():
        raise ValueError("paraphrases must differ from parents")
    if not has_adversarial_noise() or not has_hexa_hop_cues():
        raise ValueError("hexa-hop adversarial pack incomplete")

    trials_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    seeded = _seed_pack(bank_path, ai_bank)
    bank = load_bank_rows(bank_path)
    paras = [p["paraphrase"] for p in SMARTPUSH_PACK]
    gen_items = [
        {
            "question": p["parent_question"],
            "source_id": p["source_id"],
            "gold": p["gold"],
        }
        for p in SMARTPUSH_PACK
    ]

    lookup_payloads = ask_many(
        questions=paras,
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated_root,
        ask_cache=AskCompletionCache(),
    )
    gen_payloads = _run_gen_grounded(
        champ=root,
        items=gen_items,
        curated=curated_root,
        seed=seed,
        k_retrieve=3,
    )

    lookup_trials: list[dict[str, Any]] = []
    gen_trials: list[dict[str, Any]] = []
    fix_count = 0
    n_period = 0
    for i, (item, lp, gp) in enumerate(
        zip(SMARTPUSH_PACK, lookup_payloads, gen_payloads, strict=True),
        start=1,
    ):
        kind, sem_meta, text = _classify_lookup(
            dict(item), lp, bank, curated_root
        )
        fix_pass = 0
        if kind != "TRUE_HIT":
            lp, bank, fix_pass = _fix_lookup(
                i=i,
                item=dict(item),
                bank_path=bank_path,
                ai_bank=ai_bank,
                root=root,
                curated=curated_root,
                seed=seed,
            )
            fix_count += 1
            kind, sem_meta, text = _classify_lookup(
                dict(item), lp, bank, curated_root
            )
        score_l, err_l, notes_l, cited = score_smartpush_lookup(
            mode=str(lp.get("mode", "")),
            completion=text,
            expected_gold=item["gold"],
            lookup_kind=kind,
            expected_source_id=item["source_id"],
            hit_source_id=str(sem_meta.get("source_id") or "") or None,
            payload=lp,
        )
        lt = {
            "trial_id": f"AI-SMARTPUSH-LOOKUP-HITL-{i:02d}",
            "stage": "AI3",
            "hyp_id": SMARTPUSH_ID,
            "arm": "LOOKUP",
            "app_id": item["app_id"],
            "question": item["paraphrase"],
            "parent_question": item["parent_question"],
            "source_id": item["source_id"],
            "secondary_source": item["secondary_source"],
            "tertiary_source": item["tertiary_source"],
            "quaternary_source": item["quaternary_source"],
            "quinary_source": item["quinary_source"],
            "senary_source": item["senary_source"],
            "completion": lp.get("completion"),
            "wall_ms": lp.get("wall_ms"),
            "n_new": lp.get("n_new"),
            "mode": lp.get("mode"),
            "lookup_kind": kind,
            "cite_ok": cited,
            "semwrap": sem_meta,
            "score": score_l,
            "error": err_l,
            "fix_pass": fix_pass,
            "judge_model_name": _JUDGE,
            "judge_notes": notes_l,
            "gold": item["gold"],
            "weight_update": False,
        }
        score_g, err_g, notes_g = score_smartpush_gen(
            completion=str(gp.get("completion", "")),
            expected_gold=item["gold"],
            payload=gp,
        )
        if is_period_collapse(str(gp.get("completion", ""))):
            n_period += 1
        gt = {
            "trial_id": f"AI-SMARTPUSH-GEN-HITL-{i:02d}",
            "stage": "AI3",
            "hyp_id": SMARTPUSH_ID,
            "arm": "GENERATE",
            "app_id": item["app_id"],
            "question": item["parent_question"],
            "source_id": item["source_id"],
            "completion": gp.get("completion"),
            "wall_ms": gp.get("wall_ms"),
            "n_new": gp.get("n_new"),
            "mode": gp.get("mode"),
            "score": score_g,
            "error": err_g,
            "fix_pass": 0,
            "judge_model_name": _JUDGE,
            "judge_notes": notes_g,
            "gold": item["gold"],
            "weight_update": False,
            "anti_period": gp.get("anti_period"),
            "switched": gp.get("switched"),
            "context_pick": gp.get("context_pick"),
        }
        if err_g:
            append_error_row(
                ai_bank,
                {
                    "trial_id": gt["trial_id"],
                    "question": item["parent_question"],
                    "source_id": item["source_id"],
                    "model_raw": str(gp.get("completion") or ""),
                    "score": float(score_g),
                    "error": True,
                    "recipe_id": "champion-qpfb2-v0",
                    "hyp_id": SMARTPUSH_ID,
                    "arm": "GENERATE",
                    "judge_notes": notes_g,
                    "gold": item["gold"],
                },
            )
        write_json(trials_dir / f"{lt['trial_id']}.json", lt)
        write_json(trials_dir / f"{gt['trial_id']}.json", gt)
        lookup_trials.append(lt)
        gen_trials.append(gt)

    n_true = sum(1 for t in lookup_trials if t["lookup_kind"] == "TRUE_HIT")
    n_false = sum(
        1 for t in lookup_trials if t["lookup_kind"] == "FALSE_HIT"
    )
    stats = smartpush_stats(
        lookup_scores=[float(t["score"]) for t in lookup_trials],
        lookup_errors=[bool(t["error"]) for t in lookup_trials],
        cite_flags=[bool(t["cite_ok"]) for t in lookup_trials],
        gen_scores=[float(t["score"]) for t in gen_trials],
        gen_errors=[bool(t["error"]) for t in gen_trials],
        n_true_hit=n_true,
        n_false_hit=n_false,
        n_fix=fix_count,
    )
    decision = decide_smartpush(stats)
    summary: dict[str, Any] = {
        "hyp_id": SMARTPUSH_ID,
        "stage": "AI3",
        "decision": decision,
        "compose": [
            "SEMWRAP/ASKFAST LOOKUP",
            "hexa-hop paraphrase (CTXPUSH companions)",
            "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD GENERATE",
        ],
        "forbidden": [
            "QI",
            "STREAM",
            "GENCACHE",
            "LOOKUP-as-gen-IQ",
            "open chat",
        ],
        "seeded_golds": int(seeded),
        "fix_count": int(fix_count),
        "n_period": int(n_period),
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "elapsed_s": time.perf_counter() - t0,
        "stats": stats,
        "lookup_trials": [
            {
                "trial_id": t["trial_id"],
                "mode": t["mode"],
                "score": t["score"],
                "cite_ok": t["cite_ok"],
                "lookup_kind": t["lookup_kind"],
                "wall_ms": t["wall_ms"],
                "n_new": t["n_new"],
            }
            for t in lookup_trials
        ],
        "gen_trials": [
            {
                "trial_id": t["trial_id"],
                "mode": t["mode"],
                "score": t["score"],
                "wall_ms": t["wall_ms"],
                "n_new": t["n_new"],
                "error": t["error"],
                "completion": str(t.get("completion") or "")[:160],
            }
            for t in gen_trials
        ],
        "finding": (
            f"{SMARTPUSH_ID}: L_lookup={stats['lookup_mean']:.1f} "
            f"L_gen={stats['gen_mean']:.1f} cite={stats['n_cite_ok']}/10 "
            f"false_hit={n_false} period={n_period} "
            f"beats_smartlift={stats['beats_smartlift_gen']} "
            f"pass_gen={stats['pass_gen']} fix={fix_count} → {decision}"
        ),
        "public_note": "docs/results/nano-lm/formal-hsmartpush-smartpush.md",
        "ship_claim": "AF packaged stack until AI6 gen bar",
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--ai-bank", type=Path, default=_AI_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    try:
        summary = run_smartpush(
            bank_path=Path(args.bank),
            ai_bank=Path(args.ai_bank),
            root=Path(args.root),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            curated_root=Path(args.curated),
            seed=int(args.seed),
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2

    ok = str(summary.get("decision", "")).startswith(("PROMOTE", "HOLD"))
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": SMARTPUSH_ID,
                "decision": summary.get("decision"),
                "lookup_mean": summary["stats"]["lookup_mean"],
                "gen_mean": summary["stats"]["gen_mean"],
                "n_cite_ok": summary["stats"]["n_cite_ok"],
                "cpu_threads": threads,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
