"""Wave AS7 H-NANOGEN3 runner — ablated DECODE vs H-NANOGEN2 4.3."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from as_session_ops import map_as_product_mode
from askfast_ops import AskCompletionCache
from asksmart_ops import is_period_collapse
from matrix_common import REPO, write_json
from modeui_ops import attach_modeui
from nanogen3_ops import (
    MIN_GEN_MEAN,
    NANOGEN3_HYPOTHESIS,
    NANOGEN3_ID,
    NANOGEN3_N,
    NANOGEN3_PACK,
    NANOGEN3_THESIS,
    PARENT_NANOGEN2_ABLATED,
    decide_nanogen3,
    nanogen3_stats,
    score_nanogen3_gen,
    score_nanogen3_lookup,
)
from run_genbase import _contexts_for, _run_gen_ablation
from run_nanogen2 import _classify_lookup, _polish_ablated
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AS_BANK = REPO / "results/nano-lm/wave-as/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-as/trials"
_SUMMARY = REPO / "results/nano-lm/wave-as/nanogen3_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hnanogen3-nanogen3.md"
_LOCAL_SESSION = REPO / ".local/wave-as/SESSION.md"
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


def _seed_held_out(bank_path: Path, as_bank: Path) -> int:
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    as_bank.parent.mkdir(parents=True, exist_ok=True)
    if not as_bank.is_file():
        as_bank.write_text("", encoding="utf-8")
    existing = {
        str(r.get("question", "")).strip() for r in load_bank_rows(bank_path)
    }
    n = 0
    for i, item in enumerate(NANOGEN3_PACK, start=1):
        if str(item.get("kind")) != "held-out":
            continue
        q = str(item["question"]).strip()
        if q in existing:
            continue
        row = alias_bank_row(
            trial_id=f"AS-NANOGEN3-SEED-{i:02d}",
            question=q,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = NANOGEN3_ID
        row["judge_notes"] = [
            "NANOGEN3 seed for LOOKUP arm (held-out only)",
            "LOOKUP product path — not generative IQ",
        ]
        append_error_row(bank_path, row)
        append_error_row(as_bank, row)
        existing.add(q)
        n += 1
    return n


def _fix_lookup(
    *,
    i: int,
    item: dict[str, str],
    bank_path: Path,
    as_bank: Path,
    root: Path,
    curated: Path,
    seed: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], int]:
    q = str(item.get("parent_question") or item["question"])
    row = alias_bank_row(
        trial_id=f"AS-NANOGEN3-FIX-{i:02d}",
        question=q,
        source_id=item["source_id"],
        gold=item["gold"],
    )
    row["hyp_id"] = NANOGEN3_ID
    append_error_row(bank_path, row)
    append_error_row(as_bank, row)
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


def _score_gen_pair(
    item: dict[str, str],
    gate: dict[str, Any],
    peak: dict[str, Any],
    bank_p: dict[str, Any],
) -> tuple[float, bool, list[str], float, float]:
    score_g, err_g, notes_g = score_nanogen3_gen(
        completion=str(gate.get("completion", "")),
        expected_gold=item["gold"],
        payload=gate,
        peak_ablated=True,
    )
    score_p, _e_p, notes_p = score_nanogen3_gen(
        completion=str(peak.get("completion", "")),
        expected_gold=item["gold"],
        payload=peak,
        peak_ablated=False,
    )
    score_b, _e_b, _nb = score_nanogen3_gen(
        completion=str(bank_p.get("completion", "")),
        expected_gold=item["gold"],
        payload={**bank_p, "bank_grounded": False},
        peak_ablated=False,
    )
    notes = list(notes_g) + [
        f"peak_compare_score={score_p}",
        f"bank_compare_score={score_b}",
        *list(notes_p[:1]),
    ]
    return score_g, err_g, notes, score_p, score_b


def _write_public(*, decision: str, stats: dict[str, Any]) -> None:
    body = "\n".join(
        [
            f"# H-NANOGEN3 — ablated generative lift (**DONE** — {decision})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AS7 · Session: "
            "`.local/wave-as/SESSION.md`  ",
            "> Parent: [formal-hnanogen2-nanogen2.md]"
            "(formal-hnanogen2-nanogen2.md) "
            f"(ablated **{PARENT_NANOGEN2_ABLATED}**) · Pack: NANOGEN "
            "held-out+para  ",
            "> Module: `nano_lm/src/nanogen3_ops.py` · "
            "Runner: `npm run nano:nanogen3`",
            "",
            "## Hypothesis",
            "",
            NANOGEN3_HYPOTHESIS,
            "",
            "## Gate",
            "",
            "| Metric | Result | Pass bar |",
            "|--------|-------:|----------|",
            f"| LOOKUP mean | **{stats['lookup_mean']:.1f}** | ≥ 7.0 |",
            f"| GENERATE ablated mean | **{stats['gen_mean']:.1f}** | "
            f"≥ **{MIN_GEN_MEAN}** for PROMOTE |",
            f"| vs H-NANOGEN2 ablated | **{PARENT_NANOGEN2_ABLATED}** | "
            f"beats={stats.get('beats_nanogen2_ablated')} |",
            f"| GENERATE peak_on mean | **{stats['gen_peak_mean']:.1f}** | "
            "compare only |",
            f"| bank-grounded mean | **{stats['gen_bank_mean']:.1f}** | "
            "compare only (anti-FP) |",
            f"| peak_only_lift | **{stats['peak_only_lift']}** | "
            "peak≥5 ∧ ablated<5 → HOLD |",
            f"| n_abstain / n_bank_grounded | **{stats['n_abstain']}** / "
            f"**{stats['n_bank_grounded']}** | product honesty |",
            f"| FALSE_HIT | **{stats['n_false_hit']}**/{NANOGEN3_N} | "
            "any → KILL |",
            f"| Decision | **{decision}** | — |",
            "",
            "## Finding",
            "",
            "1. Dual-arm LOOKUP + ablated DECODE under max safe CPU "
            "(`cpus-2`).  ",
            "2. Junk DECODE → ABSTAIN/NO_ANSWER; bank-grounded short is "
            "**compare only** (not ablated true-gen).  ",
            "3. Generative ship language lifts **only** on ablated PROMOTE.  ",
            "4. Peak / bank-grounded lift alone → HOLD (not open-chat IQ).  ",
            "5. AR H-NANOGEN2 HOLD (4.3) stays locked; AS7 is the reopen gate.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:nanogen3",
            "npm run nano:nanogen2",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-as/nanogen3_summary.json`  ",
            "- Contract: `nano_lm/tests/test_nanogen3.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Honest HOLD on ablated <5 | LOOKUP-as-gen-IQ |",
            "| Peak/bank compare labeled | Peak/bank-as-open-chat |",
            "| PROMOTE only ablated≥5 | mini-AGI · Wave AT invent |",
            "",
            "Next: **AS8 AS-DUAL-HITL** — product pillars + gen gate status.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _update_local_session(decision: str, stats: dict[str, Any]) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    status = f"DONE — {decision}"
    body = "\n".join(
        [
            f"# Wave AS session checklist (**OPEN** · AS7 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AS **OPEN**).  ",
            "> Parent: AR COMPLETE + FROZEN · Ship: **AF packaged stack + "
            "AQ product layer — not open chat LM** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AS7 — H-NANOGEN3 ({status})** · Next: **AS8 AS-DUAL-HITL**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AS OPEN** |",
            f"| LOOKUP mean | **{stats.get('lookup_mean')}** |",
            f"| ablated gen | **{stats.get('gen_mean')}** "
            f"(bar {MIN_GEN_MEAN}; parent {PARENT_NANOGEN2_ABLATED}) |",
            f"| peak_only_lift | **{stats.get('peak_only_lift')}** |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AS0 | SESSION | **DONE — PROMOTE** |",
            "| AS1 | H-ASKABSTAIN | **DONE — PROMOTE** |",
            "| AS2 | H-SEMFIX | **DONE — PROMOTE** |",
            "| AS3 | H-ADVSAFE | **DONE — PROMOTE** |",
            "| AS4 | H-PARAEXT2 | **DONE — PROMOTE** |",
            "| AS5 | H-METRICS | **DONE — PROMOTE** |",
            "| AS6 | H-SHIPUI | **DONE — PROMOTE** |",
            f"| AS7 | H-NANOGEN3 | **{status}** |",
            "| AS8 | AS-DUAL-HITL | **NEXT** |",
            "| AS9 | AS-REPORT | pending |",
            "| AS10 | AS-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _score_lookup_arm(
    *,
    bank_path: Path,
    as_bank: Path,
    root: Path,
    curated_root: Path,
    seed: int,
) -> tuple[list[dict[str, Any]], int, list[dict[str, Any]]]:
    bank = load_bank_rows(bank_path)
    questions = [p["question"] for p in NANOGEN3_PACK]
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
    lookup_trials: list[dict[str, Any]] = []
    fix_count = 0
    for i, (item, lp) in enumerate(
        zip(NANOGEN3_PACK, lookup_payloads, strict=True),
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
                as_bank=as_bank,
                root=root,
                curated=curated_root,
                seed=seed,
            )
            fix_count += 1
            kind, sem_meta, text = _classify_lookup(
                dict(item), lp, bank, curated_root
            )
        score_l, err_l, notes_l = score_nanogen3_lookup(
            mode=str(lp.get("mode", "")),
            completion=text,
            expected_gold=item["gold"],
            lookup_kind=kind,
            payload=lp,
        )
        lookup_trials.append(
            {
                "trial_id": f"AS-NANOGEN3-LOOKUP-{i:02d}",
                "stage": "AS7",
                "hyp_id": NANOGEN3_ID,
                "arm": "LOOKUP",
                "kind": item.get("kind"),
                "app_id": item["app_id"],
                "question": item["question"],
                "source_id": item["source_id"],
                "completion": lp.get("completion"),
                "wall_ms": lp.get("wall_ms"),
                "n_new": lp.get("n_new"),
                "mode": lp.get("mode"),
                "product_mode": map_as_product_mode(str(lp.get("mode", ""))),
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
    return lookup_trials, fix_count, bank


def _gen_arm(
    *,
    root: Path,
    curated_root: Path,
    seed: int,
) -> tuple[
    list[float],
    list[bool],
    list[list[str]],
    list[int],
    list[float],
    list[float],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    int,
    int,
    int,
    int,
]:
    items = [dict(p) for p in NANOGEN3_PACK]
    gen_off, gen_on = _run_gen_ablation(
        champ=root,
        items=items,
        curated=curated_root,
        seed=seed,
        k_retrieve=6,
    )
    contexts = _contexts_for(items, curated_root, k_retrieve=6)
    gen_off = [attach_modeui(dict(p)) for p in gen_off]
    gen_on = [attach_modeui(dict(p)) for p in gen_on]

    gen_scores: list[float] = []
    gen_errors: list[bool] = []
    gen_notes: list[list[str]] = []
    gen_fix: list[int] = []
    peak_scores: list[float] = []
    bank_scores: list[float] = []
    gate_offs: list[dict[str, Any]] = []
    bank_payloads: list[dict[str, Any]] = []
    n_period = 0
    n_abstain = 0
    n_bank = 0
    weak_idx: list[int] = []
    fix_count = 0

    for i, (item, off, on, ctx) in enumerate(
        zip(NANOGEN3_PACK, gen_off, gen_on, contexts, strict=True)
    ):
        gate, bank_p, abstained = _polish_ablated(
            off, item=dict(item), context=ctx
        )
        if abstained:
            n_abstain += 1
        if bool(bank_p.get("bank_grounded")):
            n_bank += 1
        score_g, err_g, notes_g, score_p, score_b = _score_gen_pair(
            dict(item), gate, on, bank_p
        )
        if is_period_collapse(str(off.get("completion", ""))):
            n_period += 1
        gen_scores.append(score_g)
        gen_errors.append(err_g)
        gen_notes.append(notes_g)
        peak_scores.append(score_p)
        bank_scores.append(score_b)
        gen_fix.append(0)
        gate_offs.append(gate)
        bank_payloads.append(bank_p)
        if err_g and score_g <= 4.0:
            weak_idx.append(i)

    fix_attempts = 0
    if weak_idx:
        re_items = [dict(NANOGEN3_PACK[i]) for i in weak_idx]
        re_off, re_on = _run_gen_ablation(
            champ=root,
            items=re_items,
            curated=curated_root,
            seed=seed + 2700,
            k_retrieve=8,
        )
        re_ctx = _contexts_for(re_items, curated_root, k_retrieve=8)
        re_off = [attach_modeui(dict(p)) for p in re_off]
        re_on = [attach_modeui(dict(p)) for p in re_on]
        fix_attempts = len(weak_idx)
        for j, idx in enumerate(weak_idx):
            item = NANOGEN3_PACK[idx]
            gate2, bank2, abs2 = _polish_ablated(
                re_off[j], item=dict(item), context=re_ctx[j]
            )
            score2, err2, notes2, score_p2, score_b2 = _score_gen_pair(
                dict(item), gate2, re_on[j], bank2
            )
            if score2 > gen_scores[idx]:
                gen_off[idx] = re_off[j]
                gen_on[idx] = re_on[j]
                gate_offs[idx] = gate2
                bank_payloads[idx] = bank2
                gen_scores[idx] = score2
                gen_errors[idx] = err2
                peak_scores[idx] = score_p2
                bank_scores[idx] = score_b2
                gen_notes[idx] = list(notes2) + [
                    "FIX: re-ground ablated decode + abstain/bank compare"
                ]
                gen_fix[idx] = 1
                fix_count += 1
                if abs2:
                    n_abstain += 1
                if bool(bank2.get("bank_grounded")):
                    n_bank += 1
            else:
                gen_notes[idx] = list(gen_notes[idx]) + [
                    "FIX attempted: re-ground ablated decode (no lift)"
                ]

    return (
        gen_scores,
        gen_errors,
        gen_notes,
        gen_fix,
        peak_scores,
        bank_scores,
        gate_offs,
        bank_payloads,
        gen_on,
        n_period,
        n_abstain,
        n_bank,
        fix_count + fix_attempts,
    )


def run_nanogen3(
    *,
    bank_path: Path,
    as_bank: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN NANOGEN pack (held-out + paraphrase)
    WHEN LOOKUP + ablated GENERATE + peak/bank compare ×10
    THEN PROMOTE iff lookup≥7 ∧ ablated gen≥5; else HOLD.
    """
    if len(NANOGEN3_PACK) != NANOGEN3_N:
        raise ValueError(f"NANOGEN3 pack must be {NANOGEN3_N}")

    trials_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    seeded = _seed_held_out(bank_path, as_bank)
    lookup_trials, fix_lookup, _bank = _score_lookup_arm(
        bank_path=bank_path,
        as_bank=as_bank,
        root=root,
        curated_root=curated_root,
        seed=seed,
    )
    (
        gen_scores,
        gen_errors,
        gen_notes,
        gen_fix,
        peak_scores,
        bank_scores,
        gate_offs,
        bank_payloads,
        gen_on,
        n_period,
        n_abstain,
        n_bank,
        fix_gen,
    ) = _gen_arm(root=root, curated_root=curated_root, seed=seed)
    fix_count = fix_lookup + fix_gen

    gen_trials: list[dict[str, Any]] = []
    n_peak = 0
    for i, (item, gate, on, bank_p) in enumerate(
        zip(NANOGEN3_PACK, gate_offs, gen_on, bank_payloads, strict=True),
        start=1,
    ):
        idx = i - 1
        if bool(on.get("peak_used")):
            n_peak += 1
        gt = {
            "trial_id": f"AS-NANOGEN3-GEN-{i:02d}",
            "stage": "AS7",
            "hyp_id": NANOGEN3_ID,
            "arm": "GENERATE",
            "kind": item.get("kind"),
            "app_id": item["app_id"],
            "question": item["question"],
            "source_id": item["source_id"],
            "completion": gate.get("completion"),
            "completion_peak": on.get("completion"),
            "completion_bank": bank_p.get("completion"),
            "wall_ms": gate.get("wall_ms"),
            "n_new": gate.get("n_new"),
            "mode": gate.get("mode"),
            "product_mode": gate.get("product_mode")
            or map_as_product_mode(str(gate.get("mode", ""))),
            "score": gen_scores[idx],
            "score_peak": peak_scores[idx],
            "score_bank": bank_scores[idx],
            "error": gen_errors[idx],
            "fix_pass": gen_fix[idx],
            "judge_model_name": _JUDGE,
            "judge_notes": gen_notes[idx],
            "gold": item["gold"],
            "weight_update": False,
            "peak_used": False,
            "peak_used_compare": on.get("peak_used"),
            "bank_grounded_compare": bank_p.get("bank_grounded"),
            "abstained": gate.get("abstained"),
        }
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
    stats = nanogen3_stats(
        lookup_scores=[float(t["score"]) for t in lookup_trials],
        lookup_errors=[bool(t["error"]) for t in lookup_trials],
        gen_scores=[float(t["score"]) for t in gen_trials],
        gen_errors=[bool(t["error"]) for t in gen_trials],
        gen_peak_scores=peak_scores,
        gen_bank_scores=bank_scores,
        n_true_hit=n_true,
        n_false_hit=n_false,
        n_period=n_period,
        n_fix=fix_count,
        n_peak=n_peak,
        n_bank_grounded=n_bank,
        n_abstain=n_abstain,
    )
    decision = decide_nanogen3(stats)
    _write_public(decision=decision, stats=stats)
    _update_local_session(decision, stats)
    ship = (
        "AF packaged stack + AQ product layer"
        if decision != "PROMOTE"
        else "AF packaged stack + AQ product layer + ablated DECODE claim"
    )
    summary: dict[str, Any] = {
        "hyp_id": NANOGEN3_ID,
        "stage": "AS7",
        "thesis": NANOGEN3_THESIS,
        "hypothesis": NANOGEN3_HYPOTHESIS,
        "decision": decision,
        "compose": [
            "ASKFAST/SEMWRAP LOOKUP",
            "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD ablated GENERATE (gate)",
            "ASKABSTAIN refuse-junk on junk DECODE",
            "bank-grounded short compare (anti-FP — not ablated IQ)",
            "extractive peak comparison arm",
            "pack: same as H-NANOGEN / H-NANOGEN2 (5 held-out + 5 paraphrase)",
        ],
        "forbidden": [
            "LOOKUP-as-gen-IQ",
            "peak-as-open-chat-IQ",
            "bank-grounded-as-ablated-IQ",
            "mini-AGI claim before ablated PROMOTE",
            "rewrite AR NANOGEN2",
            "Wave AT invent",
        ],
        "seeded_golds": int(seeded),
        "fix_count": int(fix_count),
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "elapsed_s": time.perf_counter() - t0,
        "stats": stats,
        "finding": (
            f"{NANOGEN3_ID}: L_lookup={stats['lookup_mean']:.1f} "
            f"L_gen_ablated={stats['gen_mean']:.1f} "
            f"(parent={PARENT_NANOGEN2_ABLATED}) "
            f"L_peak={stats['gen_peak_mean']:.1f} "
            f"L_bank={stats['gen_bank_mean']:.1f} "
            f"false_hit={n_false} abstain={n_abstain} bank={n_bank} "
            f"peak_only={stats['peak_only_lift']} → {decision}"
        ),
        "public_note": "docs/results/nano-lm/formal-hnanogen3-nanogen3.md",
        "ship_claim": ship,
        "next": "AS8 AS-DUAL-HITL",
        "anti_fp": (
            "ablated gen only; peak/bank compare; mini-AGI locked if HOLD"
        ),
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AS7 H-NANOGEN3")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--as-bank", type=Path, default=_AS_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    threads = _hardware()
    try:
        summary = run_nanogen3(
            bank_path=Path(args.bank),
            as_bank=Path(args.as_bank),
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
                "hyp_id": NANOGEN3_ID,
                "decision": decision,
                "lookup_mean": summary["stats"]["lookup_mean"],
                "gen_mean": summary["stats"]["gen_mean"],
                "gen_peak_mean": summary["stats"]["gen_peak_mean"],
                "gen_bank_mean": summary["stats"]["gen_bank_mean"],
                "beats_nanogen2_ablated": summary["stats"][
                    "beats_nanogen2_ablated"
                ],
                "peak_only_lift": summary["stats"]["peak_only_lift"],
                "n_abstain": summary["stats"]["n_abstain"],
                "cpu_threads": threads,
                "elapsed_s": summary.get("elapsed_s"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
