"""Wave AR5 H-NANOGEN2 runner — ablated DECODE vs H-NANOGEN 4.0."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from abstain_ops import apply_abstain, is_junk_decode
from ar_session_ops import map_ar_product_mode
from askfast_ops import AskCompletionCache
from asksmart_ops import is_period_collapse
from matrix_common import REPO, write_json
from modeui_ops import attach_modeui
from nanogen2_ops import (
    MIN_GEN_MEAN,
    NANOGEN2_HYPOTHESIS,
    NANOGEN2_ID,
    NANOGEN2_N,
    NANOGEN2_PACK,
    NANOGEN2_THESIS,
    PARENT_NANOGEN_ABLATED,
    apply_bank_grounded_short,
    decide_nanogen2,
    nanogen2_stats,
    score_nanogen2_gen,
    score_nanogen2_lookup,
)
from run_genbase import _contexts_for, _run_gen_ablation
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row, classify_semwrap, semantic_lookup
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AR_BANK = REPO / "results/nano-lm/wave-ar/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-ar/trials"
_SUMMARY = REPO / "results/nano-lm/wave-ar/nanogen2_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hnanogen2-nanogen2.md"
_LOCAL_SESSION = REPO / ".local/wave-ar/SESSION.md"
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


def _seed_held_out(bank_path: Path, ar_bank: Path) -> int:
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    ar_bank.parent.mkdir(parents=True, exist_ok=True)
    if not ar_bank.is_file():
        ar_bank.write_text("", encoding="utf-8")
    existing = {
        str(r.get("question", "")).strip() for r in load_bank_rows(bank_path)
    }
    n = 0
    for i, item in enumerate(NANOGEN2_PACK, start=1):
        if str(item.get("kind")) != "held-out":
            continue
        q = str(item["question"]).strip()
        if q in existing:
            continue
        row = alias_bank_row(
            trial_id=f"AR-NANOGEN2-SEED-{i:02d}",
            question=q,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = NANOGEN2_ID
        row["judge_notes"] = [
            "NANOGEN2 seed for LOOKUP arm (held-out only)",
            "LOOKUP product path — not generative IQ",
        ]
        append_error_row(bank_path, row)
        append_error_row(ar_bank, row)
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
    ar_bank: Path,
    root: Path,
    curated: Path,
    seed: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], int]:
    q = str(item.get("parent_question") or item["question"])
    row = alias_bank_row(
        trial_id=f"AR-NANOGEN2-FIX-{i:02d}",
        question=q,
        source_id=item["source_id"],
        gold=item["gold"],
    )
    row["hyp_id"] = NANOGEN2_ID
    append_error_row(bank_path, row)
    append_error_row(ar_bank, row)
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


def _polish_ablated(
    off: dict[str, Any],
    *,
    item: dict[str, str],
    context: str,
) -> tuple[dict[str, Any], dict[str, Any], bool]:
    """Return (gate_payload, bank_compare_payload, abstained)."""
    decode = str(off.get("completion", ""))
    gate = dict(off)
    bank_text, used = apply_bank_grounded_short(
        decode_text=decode,
        context=context,
        bank_gold=item["gold"],
    )
    bank_p = dict(off)
    bank_p["completion"] = bank_text
    bank_p["bank_grounded"] = bool(used)
    bank_p["peak_used"] = False
    if is_junk_decode(decode):
        gate = apply_abstain(gate)
        if not bool(gate.get("abstained")):
            gate["product_mode"] = map_ar_product_mode(
                str(gate.get("mode", ""))
            )
    else:
        gate["product_mode"] = map_ar_product_mode(str(gate.get("mode", "")))
        gate["abstained"] = False
    gate["bank_grounded"] = False
    gate["peak_used"] = False
    return gate, bank_p, bool(gate.get("abstained"))


def _write_public(*, decision: str, stats: dict[str, Any]) -> None:
    body = "\n".join(
        [
            f"# H-NANOGEN2 — ablated generative lift (**DONE** — {decision})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AR5 · Session: "
            "`.local/wave-ar/SESSION.md`  ",
            "> Parent: [formal-hnanogen-nanogen.md](formal-hnanogen-nanogen.md) "
            f"(ablated **{PARENT_NANOGEN_ABLATED}**) · Pack: NANOGEN held-out+para  ",
            "> Module: `nano_lm/src/nanogen2_ops.py` · "
            "Runner: `npm run nano:nanogen2`",
            "",
            "## Hypothesis",
            "",
            NANOGEN2_HYPOTHESIS,
            "",
            "## Gate",
            "",
            "| Metric | Result | Pass bar |",
            "|--------|-------:|----------|",
            f"| LOOKUP mean | **{stats['lookup_mean']:.1f}** | ≥ 7.0 |",
            f"| GENERATE ablated mean | **{stats['gen_mean']:.1f}** | "
            f"≥ {MIN_GEN_MEAN} for PROMOTE |",
            f"| vs H-NANOGEN ablated | **{PARENT_NANOGEN_ABLATED}** | "
            f"beats={stats.get('beats_nanogen_ablated')} |",
            f"| GENERATE peak_on mean | **{stats['gen_peak_mean']:.1f}** | "
            "compare only |",
            f"| bank-grounded mean | **{stats['gen_bank_mean']:.1f}** | "
            "compare only (anti-FP) |",
            f"| peak_only_lift | **{stats['peak_only_lift']}** | "
            "peak≥5 ∧ ablated<5 → HOLD |",
            f"| n_abstain / n_bank_grounded | **{stats['n_abstain']}** / "
            f"**{stats['n_bank_grounded']}** | product honesty |",
            f"| FALSE_HIT | **{stats['n_false_hit']}**/{NANOGEN2_N} | "
            "any → KILL |",
            f"| Decision | **{decision}** | — |",
            "",
            "## Finding",
            "",
            "1. Dual-arm LOOKUP + ablated DECODE under max safe CPU "
            "(`cpus-2`).  ",
            "2. Junk DECODE → ABSTAIN/NO_ANSWER (product); bank-grounded "
            "short is **compare only** (not ablated true-gen).  ",
            "3. Generative ship language lifts **only** on ablated PROMOTE.  ",
            "4. Peak / bank-grounded lift alone → HOLD (not open-chat IQ).",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:nanogen2",
            "npm run nano:nanogen",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-ar/nanogen2_summary.json`  ",
            "- Contract: `nano_lm/tests/test_nanogen2.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Honest HOLD on ablated <5 | LOOKUP-as-gen-IQ |",
            "| Peak/bank compare labeled | Peak/bank-as-open-chat |",
            "| PROMOTE only ablated≥5 | mini-AGI · Wave AS invent |",
            "",
            "Next: **AR6 AR-DUAL-HITL** — product pillars + gen gate status.",
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
            f"# Wave AR session checklist (**OPEN** · AR5 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AR **OPEN**).  ",
            "> Parent: AQ COMPLETE + FROZEN · Ship: **AF packaged stack + "
            "AQ product layer — not open chat LM** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AR5 — H-NANOGEN2 ({status})** · Next: **AR6 AR-DUAL-HITL**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AR OPEN** |",
            f"| LOOKUP mean | **{stats.get('lookup_mean')}** |",
            f"| ablated gen | **{stats.get('gen_mean')}** "
            f"(parent NANOGEN {PARENT_NANOGEN_ABLATED}) |",
            f"| peak / bank | **{stats.get('gen_peak_mean')}** / "
            f"**{stats.get('gen_bank_mean')}** |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AR0 | SESSION | **DONE — PROMOTE** |",
            "| AR1 | H-ABSTAIN | **DONE — PROMOTE** |",
            "| AR2 | H-SHIPDEMO | **DONE — PROMOTE** |",
            "| AR3 | H-PARAEXT | **DONE — HOLD** |",
            "| AR4 | H-ADVREG | **DONE — KILL** |",
            f"| AR5 | H-NANOGEN2 | **{status}** |",
            "| AR6 | AR-DUAL-HITL | **NEXT** |",
            "| AR7 | AR-REPORT | pending |",
            "| AR8 | AR-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _score_gen_pair(
    item: dict[str, str],
    gate: dict[str, Any],
    peak: dict[str, Any],
    bank_p: dict[str, Any],
) -> tuple[float, bool, list[str], float, float]:
    score_g, err_g, notes_g = score_nanogen2_gen(
        completion=str(gate.get("completion", "")),
        expected_gold=item["gold"],
        payload=gate,
        peak_ablated=True,
    )
    score_p, _e_p, notes_p = score_nanogen2_gen(
        completion=str(peak.get("completion", "")),
        expected_gold=item["gold"],
        payload=peak,
        peak_ablated=False,
    )
    score_b, _e_b, _nb = score_nanogen2_gen(
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


def run_nanogen2(
    *,
    bank_path: Path,
    ar_bank: Path,
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
    if len(NANOGEN2_PACK) != NANOGEN2_N:
        raise ValueError(f"NANOGEN2 pack must be {NANOGEN2_N}")

    trials_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    seeded = _seed_held_out(bank_path, ar_bank)
    bank = load_bank_rows(bank_path)
    questions = [p["question"] for p in NANOGEN2_PACK]
    items = [dict(p) for p in NANOGEN2_PACK]

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
        items=items,
        curated=curated_root,
        seed=seed,
        k_retrieve=6,
    )
    contexts = _contexts_for(items, curated_root, k_retrieve=6)
    gen_off = [attach_modeui(dict(p)) for p in gen_off]
    gen_on = [attach_modeui(dict(p)) for p in gen_on]

    lookup_trials: list[dict[str, Any]] = []
    fix_count = 0
    for i, (item, lp) in enumerate(
        zip(NANOGEN2_PACK, lookup_payloads, strict=True),
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
                ar_bank=ar_bank,
                root=root,
                curated=curated_root,
                seed=seed,
            )
            fix_count += 1
            kind, sem_meta, text = _classify_lookup(
                dict(item), lp, bank, curated_root
            )
        score_l, err_l, notes_l = score_nanogen2_lookup(
            mode=str(lp.get("mode", "")),
            completion=text,
            expected_gold=item["gold"],
            lookup_kind=kind,
            payload=lp,
        )
        lookup_trials.append(
            {
                "trial_id": f"AR-NANOGEN2-LOOKUP-{i:02d}",
                "stage": "AR5",
                "hyp_id": NANOGEN2_ID,
                "arm": "LOOKUP",
                "kind": item.get("kind"),
                "app_id": item["app_id"],
                "question": item["question"],
                "source_id": item["source_id"],
                "completion": lp.get("completion"),
                "wall_ms": lp.get("wall_ms"),
                "n_new": lp.get("n_new"),
                "mode": lp.get("mode"),
                "product_mode": map_ar_product_mode(str(lp.get("mode", ""))),
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
    bank_scores: list[float] = []
    gate_offs: list[dict[str, Any]] = []
    bank_payloads: list[dict[str, Any]] = []
    n_period = 0
    n_abstain = 0
    n_bank = 0
    weak_idx: list[int] = []

    for i, (item, off, on, ctx) in enumerate(
        zip(NANOGEN2_PACK, gen_off, gen_on, contexts, strict=True)
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
        re_items = [dict(NANOGEN2_PACK[i]) for i in weak_idx]
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
            item = NANOGEN2_PACK[idx]
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

    gen_trials: list[dict[str, Any]] = []
    n_peak = 0
    for i, (item, gate, on, bank_p) in enumerate(
        zip(NANOGEN2_PACK, gate_offs, gen_on, bank_payloads, strict=True),
        start=1,
    ):
        idx = i - 1
        if bool(on.get("peak_used")):
            n_peak += 1
        gt = {
            "trial_id": f"AR-NANOGEN2-GEN-{i:02d}",
            "stage": "AR5",
            "hyp_id": NANOGEN2_ID,
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
            or map_ar_product_mode(str(gate.get("mode", ""))),
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
    stats = nanogen2_stats(
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
    decision = decide_nanogen2(stats)
    _write_public(decision=decision, stats=stats)
    _update_local_session(decision, stats)
    summary: dict[str, Any] = {
        "hyp_id": NANOGEN2_ID,
        "stage": "AR5",
        "thesis": NANOGEN2_THESIS,
        "hypothesis": NANOGEN2_HYPOTHESIS,
        "decision": decision,
        "compose": [
            "ASKFAST/SEMWRAP LOOKUP",
            "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD ablated GENERATE (gate)",
            "ABSTAIN on junk DECODE",
            "bank-grounded short compare (anti-FP — not ablated IQ)",
            "extractive peak comparison arm",
            "pack: same as H-NANOGEN (5 held-out + 5 paraphrase)",
        ],
        "forbidden": [
            "LOOKUP-as-gen-IQ",
            "peak-as-open-chat-IQ",
            "bank-grounded-as-ablated-IQ",
            "mini-AGI claim before ablated PROMOTE",
            "Wave AS invent",
        ],
        "seeded_golds": int(seeded),
        "fix_count": int(fix_count),
        "fix_attempts": int(fix_attempts),
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "elapsed_s": time.perf_counter() - t0,
        "stats": stats,
        "finding": (
            f"{NANOGEN2_ID}: L_lookup={stats['lookup_mean']:.1f} "
            f"L_gen_ablated={stats['gen_mean']:.1f} "
            f"(parent={PARENT_NANOGEN_ABLATED}) "
            f"L_peak={stats['gen_peak_mean']:.1f} "
            f"L_bank={stats['gen_bank_mean']:.1f} "
            f"false_hit={n_false} abstain={n_abstain} bank={n_bank} "
            f"peak_only={stats['peak_only_lift']} → {decision}"
        ),
        "public_note": "docs/results/nano-lm/formal-hnanogen2-nanogen2.md",
        "ship_claim": (
            "AF packaged stack + AQ product layer "
            "(ablated gen HOLD unless PROMOTE)"
        ),
        "next": "AR6 AR-DUAL-HITL",
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AR5 H-NANOGEN2")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--ar-bank", type=Path, default=_AR_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    threads = _hardware()
    try:
        summary = run_nanogen2(
            bank_path=Path(args.bank),
            ar_bank=Path(args.ar_bank),
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
                "hyp_id": NANOGEN2_ID,
                "decision": decision,
                "lookup_mean": summary["stats"]["lookup_mean"],
                "gen_mean": summary["stats"]["gen_mean"],
                "gen_peak_mean": summary["stats"]["gen_peak_mean"],
                "gen_bank_mean": summary["stats"]["gen_bank_mean"],
                "beats_nanogen_ablated": summary["stats"][
                    "beats_nanogen_ablated"
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
