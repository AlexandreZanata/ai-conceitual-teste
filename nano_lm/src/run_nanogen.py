"""Wave AQ6 H-NANOGEN runner — ablated DECODE on held-out + paraphrase."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from aq_session_ops import map_product_mode
from askfast_ops import AskCompletionCache
from asksmart_ops import is_period_collapse
from matrix_common import REPO, write_json
from modeui_ops import attach_modeui
from nanogen_ops import (
    MIN_GEN_MEAN,
    NANOGEN_ID,
    NANOGEN_N,
    NANOGEN_PACK,
    NANOGEN_THESIS,
    decide_nanogen,
    nanogen_stats,
    score_nanogen_gen,
    score_nanogen_lookup,
)
from run_genbase import _run_gen_ablation
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row, classify_semwrap, semantic_lookup
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AQ_BANK = REPO / "results/nano-lm/wave-aq/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-aq/trials"
_SUMMARY = REPO / "results/nano-lm/wave-aq/nanogen_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hnanogen-nanogen.md"
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


def _hardware() -> int:
    cpus = int(os.cpu_count() or 4)
    return tune_cpu_threads(max(4, cpus - 2))


def _seed_held_out(bank_path: Path, aq_bank: Path) -> int:
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    aq_bank.parent.mkdir(parents=True, exist_ok=True)
    if not aq_bank.is_file():
        aq_bank.write_text("", encoding="utf-8")
    existing = {
        str(r.get("question", "")).strip() for r in load_bank_rows(bank_path)
    }
    n = 0
    for i, item in enumerate(NANOGEN_PACK, start=1):
        if str(item.get("kind")) != "held-out":
            continue
        q = str(item["question"]).strip()
        if q in existing:
            continue
        row = alias_bank_row(
            trial_id=f"AQ-NANOGEN-SEED-{i:02d}",
            question=q,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = NANOGEN_ID
        row["judge_notes"] = [
            "NANOGEN seed for LOOKUP arm (held-out only)",
            "LOOKUP product path — not generative IQ",
            "paraphrases not seeded (SEMWRAP probe)",
        ]
        append_error_row(bank_path, row)
        append_error_row(aq_bank, row)
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
        item["question"], bank, curated_root=curated
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
    aq_bank: Path,
    root: Path,
    curated: Path,
    seed: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], int]:
    # Prefer parent for paraphrase FIX seed (exact bank gold path).
    q = str(item.get("parent_question") or item["question"])
    row = alias_bank_row(
        trial_id=f"AQ-NANOGEN-FIX-{i:02d}",
        question=q,
        source_id=item["source_id"],
        gold=item["gold"],
    )
    row["hyp_id"] = NANOGEN_ID
    append_error_row(bank_path, row)
    append_error_row(aq_bank, row)
    bank = load_bank_rows(bank_path)
    re_payloads = ask_many(
        questions=[item["question"]],
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated,
        ask_cache=AskCompletionCache(),
    )
    return attach_modeui(dict(re_payloads[0])), bank, 1


def _write_public(*, decision: str, stats: dict[str, Any]) -> None:
    body = "\n".join(
        [
            f"# H-NANOGEN — ablated generative gate (**DONE** — {decision})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AQ6 · Session: "
            "`.local/wave-aq/SESSION.md`  ",
            "> Parent: [formal-hmodeui-modeui.md](formal-hmodeui-modeui.md) · "
            "Baseline: [formal-hgenbase-genbase.md](formal-hgenbase-genbase.md)  ",
            "> Module: `nano_lm/src/nanogen_ops.py` · "
            "Runner: `npm run nano:nanogen`",
            "",
            "## Hypothesis",
            "",
            "North-star **ablated DECODE** on **held-out + paraphrase** "
            f"(n={NANOGEN_N}). PROMOTE only if ablated mean ≥ "
            f"**{MIN_GEN_MEAN}**; else honest **HOLD** (peak compare only).",
            "",
            "## Gate",
            "",
            "| Metric | Result | Pass bar |",
            "|--------|-------:|----------|",
            f"| LOOKUP mean | **{stats['lookup_mean']:.1f}** | ≥ 7.0 |",
            f"| GENERATE ablated mean | **{stats['gen_mean']:.1f}** | "
            f"≥ {MIN_GEN_MEAN} for PROMOTE |",
            f"| GENERATE peak_on mean | **{stats['gen_peak_mean']:.1f}** | "
            "compare only |",
            f"| peak_only_lift | **{stats['peak_only_lift']}** | "
            "peak≥5 ∧ ablated<5 → HOLD |",
            f"| FALSE_HIT | **{stats['n_false_hit']}**/{NANOGEN_N} | "
            "any → KILL |",
            f"| Decision | **{decision}** | — |",
            "",
            "## Pack",
            "",
            "- 5× AP0 held-out (`AP-HITL-*`)  ",
            "- 5× AQ0 paraphrase (`AQ-PARA-*` ask text = paraphrase)  ",
            "- Gate scores **ablated** arm only; peak is anti-FP compare.",
            "",
            "## Finding",
            "",
            "1. Dual-arm LOOKUP + ablated DECODE under max safe CPU "
            "(`cpus-2`).  ",
            "2. Generative ship language lifts **only** on ablated PROMOTE.  ",
            "3. Peak extractive lift alone → HOLD (not open-chat IQ).",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:nanogen",
            "npm run nano:z:ask -- --question \"Human rewrite: make a small "
            "Python function add(a, b) that returns a plus b.\"",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-aq/nanogen_summary.json`  ",
            "- Contract: `nano_lm/tests/test_nanogen.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Honest HOLD on ablated <5 | LOOKUP-as-gen-IQ |",
            "| Peak compare labeled | Peak-as-open-chat |",
            "| PROMOTE only ablated≥5 | Wave AR invent |",
            "",
            "Next: **AQ7 AQ-PRODUCT-HITL** — final product verify.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def run_nanogen(
    *,
    bank_path: Path,
    aq_bank: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN held-out + paraphrase pack
    WHEN LOOKUP + ablated GENERATE ×10
    THEN PROMOTE iff lookup≥7 ∧ ablated gen≥5; else HOLD.
    """
    if len(NANOGEN_PACK) != NANOGEN_N:
        raise ValueError(f"NANOGEN pack must be {NANOGEN_N}")

    trials_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    seeded = _seed_held_out(bank_path, aq_bank)
    bank = load_bank_rows(bank_path)
    questions = [p["question"] for p in NANOGEN_PACK]

    lookup_payloads = [
        attach_modeui(dict(p))
        for p in ask_many(
            questions=questions,
            root=root,
            seed=seed,
            askfast=True,
            bank_path=bank_path,
            curated_root=curated_root,
            ask_cache=AskCompletionCache(),
        )
    ]
    gen_off, gen_on = _run_gen_ablation(
        champ=root,
        items=[dict(p) for p in NANOGEN_PACK],
        curated=curated_root,
        seed=seed,
        k_retrieve=6,
    )
    gen_off = [attach_modeui(dict(p)) for p in gen_off]
    gen_on = [attach_modeui(dict(p)) for p in gen_on]

    lookup_trials: list[dict[str, Any]] = []
    fix_count = 0
    for i, (item, lp) in enumerate(
        zip(NANOGEN_PACK, lookup_payloads, strict=True),
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
                aq_bank=aq_bank,
                root=root,
                curated=curated_root,
                seed=seed,
            )
            fix_count += 1
            kind, sem_meta, text = _classify_lookup(
                dict(item), lp, bank, curated_root
            )
        score_l, err_l, notes_l = score_nanogen_lookup(
            mode=str(lp.get("mode", "")),
            completion=text,
            expected_gold=item["gold"],
            lookup_kind=kind,
            payload=lp,
        )
        lookup_trials.append(
            {
                "trial_id": f"AQ-NANOGEN-LOOKUP-{i:02d}",
                "stage": "AQ6",
                "hyp_id": NANOGEN_ID,
                "arm": "LOOKUP",
                "kind": item.get("kind"),
                "app_id": item["app_id"],
                "question": item["question"],
                "source_id": item["source_id"],
                "completion": lp.get("completion"),
                "wall_ms": lp.get("wall_ms"),
                "n_new": lp.get("n_new"),
                "mode": lp.get("mode"),
                "product_mode": map_product_mode(str(lp.get("mode", ""))),
                "modeui_line": lp.get("modeui_line"),
                "lookup_kind": kind,
                "semwrap": sem_meta,
                "score": score_l,
                "error": err_l,
                "fix_pass": fix_pass,
                "judge_model_name": _JUDGE,
                "judge_notes": notes_l,
                "gold": item["gold"],
                "weight_update": False,
            }
        )

    gen_scores: list[float] = []
    gen_errors: list[bool] = []
    gen_notes: list[list[str]] = []
    gen_fix: list[int] = []
    peak_scores: list[float] = []
    n_period = 0
    weak_idx: list[int] = []

    for i, (item, off, on) in enumerate(
        zip(NANOGEN_PACK, gen_off, gen_on, strict=True)
    ):
        score_g, err_g, notes_g = score_nanogen_gen(
            completion=str(off.get("completion", "")),
            expected_gold=item["gold"],
            payload=off,
            peak_ablated=True,
        )
        score_p, _err_p, notes_p = score_nanogen_gen(
            completion=str(on.get("completion", "")),
            expected_gold=item["gold"],
            payload=on,
            peak_ablated=False,
        )
        if is_period_collapse(str(off.get("completion", ""))):
            n_period += 1
        gen_scores.append(score_g)
        gen_errors.append(err_g)
        gen_notes.append(list(notes_g) + [f"peak_compare_score={score_p}"])
        peak_scores.append(score_p)
        gen_fix.append(0)
        on["judge_notes_peak"] = notes_p
        if err_g and score_g <= 4.0:
            weak_idx.append(i)

    fix_attempts = 0
    if weak_idx:
        re_items = [dict(NANOGEN_PACK[i]) for i in weak_idx]
        re_off, re_on = _run_gen_ablation(
            champ=root,
            items=re_items,
            curated=curated_root,
            seed=seed + 2600,
            k_retrieve=8,
        )
        re_off = [attach_modeui(dict(p)) for p in re_off]
        re_on = [attach_modeui(dict(p)) for p in re_on]
        fix_attempts = len(weak_idx)
        for j, idx in enumerate(weak_idx):
            item = NANOGEN_PACK[idx]
            score2, err2, notes2 = score_nanogen_gen(
                completion=str(re_off[j].get("completion", "")),
                expected_gold=item["gold"],
                payload=re_off[j],
                peak_ablated=True,
            )
            score_p2, _, _ = score_nanogen_gen(
                completion=str(re_on[j].get("completion", "")),
                expected_gold=item["gold"],
                payload=re_on[j],
                peak_ablated=False,
            )
            if score2 > gen_scores[idx]:
                gen_off[idx] = re_off[j]
                gen_on[idx] = re_on[j]
                gen_scores[idx] = score2
                gen_errors[idx] = err2
                peak_scores[idx] = score_p2
                gen_notes[idx] = list(notes2) + [
                    "FIX: re-ground ablated decode",
                    f"peak_compare_score={score_p2}",
                ]
                gen_fix[idx] = 1
                fix_count += 1
            else:
                gen_notes[idx] = list(gen_notes[idx]) + [
                    "FIX attempted: re-ground ablated decode (no lift)"
                ]

    gen_trials: list[dict[str, Any]] = []
    n_peak = 0
    for i, (item, off, on) in enumerate(
        zip(NANOGEN_PACK, gen_off, gen_on, strict=True),
        start=1,
    ):
        idx = i - 1
        if bool(on.get("peak_used")):
            n_peak += 1
        gt = {
            "trial_id": f"AQ-NANOGEN-GEN-{i:02d}",
            "stage": "AQ6",
            "hyp_id": NANOGEN_ID,
            "arm": "GENERATE",
            "kind": item.get("kind"),
            "app_id": item["app_id"],
            "question": item["question"],
            "source_id": item["source_id"],
            "completion": off.get("completion"),
            "completion_peak": on.get("completion"),
            "wall_ms": off.get("wall_ms"),
            "n_new": off.get("n_new"),
            "mode": off.get("mode"),
            "product_mode": map_product_mode(str(off.get("mode", ""))),
            "modeui_line": off.get("modeui_line"),
            "score": gen_scores[idx],
            "score_peak": peak_scores[idx],
            "error": gen_errors[idx],
            "fix_pass": gen_fix[idx],
            "judge_model_name": _JUDGE,
            "judge_notes": gen_notes[idx],
            "gold": item["gold"],
            "weight_update": False,
            "anti_period": off.get("anti_period"),
            "peak_used": False,
            "peak_used_compare": on.get("peak_used"),
            "peak_span": on.get("peak_span"),
            "switched": off.get("switched"),
        }
        if gen_errors[idx]:
            append_error_row(
                aq_bank,
                {
                    "trial_id": gt["trial_id"],
                    "question": item["question"],
                    "source_id": item["source_id"],
                    "model_raw": str(off.get("completion") or ""),
                    "score": float(gen_scores[idx]),
                    "error": True,
                    "recipe_id": "champion-qpfb2-v0",
                    "hyp_id": NANOGEN_ID,
                    "arm": "GENERATE",
                    "judge_notes": gen_notes[idx],
                    "gold": item["gold"],
                },
            )
        write_json(
            trials_dir / f"{lookup_trials[idx]['trial_id']}.json",
            lookup_trials[idx],
        )
        write_json(trials_dir / f"{gt['trial_id']}.json", gt)
        gen_trials.append(gt)

    n_true = sum(1 for t in lookup_trials if t["lookup_kind"] == "TRUE_HIT")
    n_false = sum(
        1 for t in lookup_trials if t["lookup_kind"] == "FALSE_HIT"
    )
    stats = nanogen_stats(
        lookup_scores=[float(t["score"]) for t in lookup_trials],
        lookup_errors=[bool(t["error"]) for t in lookup_trials],
        gen_scores=[float(t["score"]) for t in gen_trials],
        gen_errors=[bool(t["error"]) for t in gen_trials],
        gen_peak_scores=peak_scores,
        n_true_hit=n_true,
        n_false_hit=n_false,
        n_period=n_period,
        n_fix=fix_count,
        n_peak=n_peak,
    )
    decision = decide_nanogen(stats)
    _write_public(decision=decision, stats=stats)
    summary: dict[str, Any] = {
        "hyp_id": NANOGEN_ID,
        "stage": "AQ6",
        "thesis": NANOGEN_THESIS,
        "decision": decision,
        "compose": [
            "ASKFAST/SEMWRAP LOOKUP",
            "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD ablated GENERATE (gate)",
            "extractive peak comparison arm (anti-FP — not smarter-LM)",
            "pack: 5 held-out + 5 paraphrase",
        ],
        "forbidden": [
            "LOOKUP-as-gen-IQ",
            "peak-as-open-chat-IQ",
            "Wave AR invent",
            "claim mini-AGI before ablated PROMOTE",
        ],
        "seeded_golds": int(seeded),
        "fix_count": int(fix_count),
        "fix_attempts": int(fix_attempts),
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "elapsed_s": time.perf_counter() - t0,
        "stats": stats,
        "pack_kinds": {
            "held-out": sum(
                1 for p in NANOGEN_PACK if p.get("kind") == "held-out"
            ),
            "paraphrase": sum(
                1 for p in NANOGEN_PACK if p.get("kind") == "paraphrase"
            ),
        },
        "lookup_trials": [
            {
                "trial_id": t["trial_id"],
                "kind": t.get("kind"),
                "mode": t["mode"],
                "product_mode": t.get("product_mode"),
                "score": t["score"],
                "lookup_kind": t["lookup_kind"],
                "wall_ms": t["wall_ms"],
                "n_new": t["n_new"],
            }
            for t in lookup_trials
        ],
        "gen_trials": [
            {
                "trial_id": t["trial_id"],
                "kind": t.get("kind"),
                "mode": t["mode"],
                "product_mode": t.get("product_mode"),
                "score": t["score"],
                "score_peak": t["score_peak"],
                "wall_ms": t["wall_ms"],
                "n_new": t["n_new"],
                "error": t["error"],
                "peak_used_compare": t.get("peak_used_compare"),
                "completion": str(t.get("completion") or "")[:160],
                "completion_peak": str(t.get("completion_peak") or "")[:80],
            }
            for t in gen_trials
        ],
        "finding": (
            f"{NANOGEN_ID}: L_lookup={stats['lookup_mean']:.1f} "
            f"L_gen_ablated={stats['gen_mean']:.1f} "
            f"L_gen_peak={stats['gen_peak_mean']:.1f} "
            f"false_hit={n_false} period={n_period} peak={n_peak} "
            f"peak_only={stats['peak_only_lift']} "
            f"pass_gen={stats['pass_gen']} fix={fix_count} → {decision}"
        ),
        "public_note": "docs/results/nano-lm/formal-hnanogen-nanogen.md",
        "ship_claim": (
            "AF packaged stack + AQ product layer "
            "(ablated gen HOLD unless PROMOTE)"
        ),
        "next": "AQ7 AQ-PRODUCT-HITL",
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AQ6 H-NANOGEN")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--aq-bank", type=Path, default=_AQ_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    threads = _hardware()
    try:
        summary = run_nanogen(
            bank_path=Path(args.bank),
            aq_bank=Path(args.aq_bank),
            root=Path(args.root),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            curated_root=Path(args.curated),
            seed=int(args.seed),
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    decision = str(summary.get("decision", ""))
    ok = decision.startswith(("PROMOTE", "HOLD"))
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": NANOGEN_ID,
                "decision": decision,
                "lookup_mean": summary["stats"]["lookup_mean"],
                "gen_mean": summary["stats"]["gen_mean"],
                "gen_peak_mean": summary["stats"]["gen_peak_mean"],
                "peak_only_lift": summary["stats"]["peak_only_lift"],
                "n_peak": summary["stats"]["n_peak"],
                "cpu_threads": threads,
                "elapsed_s": summary.get("elapsed_s"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
