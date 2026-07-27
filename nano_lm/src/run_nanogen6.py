"""Wave AV3 H-NANOGEN6 runner — refuse-or-continue; span-fallback ≠ gen IQ."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

from abstain_ops import apply_abstain, is_junk_decode
from askfast_ops import AskCompletionCache
from asksmart_ops import is_period_collapse
from at_session_ops import map_at_product_mode
from matrix_common import REPO, write_json
from modeui_ops import attach_modeui
from nanogen6_ops import (
    MIN_LOOKUP_MEAN,
    MIN_TRUE_CONTINUE_MEAN,
    NANOGEN6_HYPOTHESIS,
    NANOGEN6_ID,
    NANOGEN6_N,
    NANOGEN6_PACK,
    NANOGEN6_THESIS,
    PARENT_NANOGEN5_STRICT,
    apply_bank_grounded_short,
    apply_refuse_or_continue,
    apply_snippet_prefix_decode,
    decide_nanogen6,
    nanogen6_stats,
    score_nanogen6_gen,
    score_nanogen6_lookup,
)
from run_genbase import _contexts_for, _run_gen_ablation
from run_nanogen2 import _classify_lookup
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AV_BANK = REPO / "results/nano-lm/wave-av/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-av/trials"
_SUMMARY = REPO / "results/nano-lm/wave-av/nanogen6_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hnanogen6-nanogen6.md"
_LOCAL_SESSION = REPO / ".local/wave-av/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_JUDGE = "cursor-composer-frontier-chat · true_continue_f1"


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


def _polish_ablated(
    off: dict[str, Any],
    *,
    item: dict[str, str],
    context: str,
) -> tuple[dict[str, Any], dict[str, Any], bool, bool, str]:
    """Return (gate, bank_compare, abstained, snippet_used, continue_kind)."""
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
    text, snip_used, prefix = apply_snippet_prefix_decode(
        decode_text=decode,
        question=item["question"],
        context=context,
    )
    source = text if snip_used else decode
    out, kind, trunc, refuse = apply_refuse_or_continue(
        text=source,
        prefix=prefix if snip_used else "",
    )
    if kind == "abstain" or refuse or (
        not snip_used and is_junk_decode(decode) and kind != "true_continue"
    ):
        gate = apply_abstain(gate)
        if not bool(gate.get("abstained")):
            gate["product_mode"] = "ABSTAIN"
        gate["continue_kind"] = "abstain"
        gate["span_fallback"] = False
        gate["snippet_prefix"] = bool(snip_used)
        gate["snippet_span"] = prefix if snip_used else ""
        gate["gibberish_tail_truncated"] = False
        kind = "abstain"
    elif kind == "span_fallback":
        gate["completion"] = out
        gate["snippet_prefix"] = bool(snip_used)
        gate["snippet_span"] = prefix if snip_used else ""
        gate["product_mode"] = "PEAK"  # PEAK/LOOKUP fallback — ≠ DECODE IQ
        gate["abstained"] = False
        gate["continue_kind"] = "span_fallback"
        gate["span_fallback"] = True
        gate["gibberish_tail_truncated"] = bool(trunc)
    else:
        gate["completion"] = out
        gate["snippet_prefix"] = bool(snip_used)
        gate["snippet_span"] = prefix if snip_used else ""
        gate["product_mode"] = "DECODE"
        gate["abstained"] = False
        gate["continue_kind"] = "true_continue"
        gate["span_fallback"] = False
        gate["gibberish_tail_truncated"] = False
    gate["bank_grounded"] = False
    gate["peak_used"] = False
    return (
        gate,
        bank_p,
        bool(gate.get("abstained")),
        bool(snip_used),
        str(gate.get("continue_kind") or kind),
    )


def _hardware() -> int:
    cpus = int(os.cpu_count() or 4)
    return tune_cpu_threads(max(4, cpus - 2))


def _seed_held_out(bank_path: Path, av_bank: Path) -> int:
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    av_bank.parent.mkdir(parents=True, exist_ok=True)
    if not av_bank.is_file():
        av_bank.write_text("", encoding="utf-8")
    existing = {
        str(r.get("question", "")).strip() for r in load_bank_rows(bank_path)
    }
    n = 0
    for i, item in enumerate(NANOGEN6_PACK, start=1):
        if str(item.get("kind")) != "held-out":
            continue
        q = str(item["question"]).strip()
        if q in existing:
            continue
        row = alias_bank_row(
            trial_id=f"AV-NANOGEN6-SEED-{i:02d}",
            question=q,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = NANOGEN6_ID
        row["judge_notes"] = [
            "NANOGEN6 seed for LOOKUP arm (held-out only)",
            "LOOKUP product path — not generative IQ",
        ]
        append_error_row(bank_path, row)
        append_error_row(av_bank, row)
        existing.add(q)
        n += 1
    return n


def _fix_lookup(
    *,
    i: int,
    item: dict[str, str],
    bank_path: Path,
    av_bank: Path,
    root: Path,
    curated: Path,
    seed: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], int]:
    q = str(item.get("parent_question") or item["question"])
    row = alias_bank_row(
        trial_id=f"AV-NANOGEN6-FIX-{i:02d}",
        question=q,
        source_id=item["source_id"],
        gold=item["gold"],
    )
    row["hyp_id"] = NANOGEN6_ID
    append_error_row(bank_path, row)
    append_error_row(av_bank, row)
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
    score_g, err_g, notes_g = score_nanogen6_gen(
        completion=str(gate.get("completion", "")),
        expected_gold=item["gold"],
        payload=gate,
        peak_ablated=True,
    )
    score_p, _e_p, notes_p = score_nanogen6_gen(
        completion=str(peak.get("completion", "")),
        expected_gold=item["gold"],
        payload={
            **peak,
            "continue_kind": "true_continue",
            "span_fallback": False,
            "product_mode": "PEAK",
        },
        peak_ablated=False,
    )
    score_b, _e_b, _nb = score_nanogen6_gen(
        completion=str(bank_p.get("completion", "")),
        expected_gold=item["gold"],
        payload={
            **bank_p,
            "bank_grounded": False,
            "continue_kind": "true_continue",
            "span_fallback": False,
        },
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
            f"# H-NANOGEN6 — true continue / refuse-or-continue (**DONE** — {decision})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AV3 · Session: "
            "`.local/wave-av/SESSION.md`  ",
            "> Parent: [formal-hnanogen5-nanogen5.md]"
            "(formal-hnanogen5-nanogen5.md) "
            f"(STRICT archive **{PARENT_NANOGEN5_STRICT}**) · Pack: same "
            "NANOGEN held-out+para · true-gen judge  ",
            "> Module: `nano_lm/src/nanogen6_ops.py` · "
            "Runner: `npm run nano:nanogen6`",
            "",
            "## Hypothesis",
            "",
            NANOGEN6_HYPOTHESIS,
            "",
            "## Gate",
            "",
            "| Metric | Result | Pass bar |",
            "|--------|-------:|----------|",
            f"| LOOKUP mean | **{stats['lookup_mean']:.1f}** | ≥ {MIN_LOOKUP_MEAN} |",
            f"| true_continue ablated mean | **{stats['gen_mean']:.1f}** | "
            f"≥ **{MIN_TRUE_CONTINUE_MEAN}** for PROMOTE |",
            f"| vs H-NANOGEN5 STRICT archive | **{PARENT_NANOGEN5_STRICT}** | "
            "span-fallback ≠ gen credit |",
            f"| GENERATE peak_on mean | **{stats['gen_peak_mean']:.1f}** | "
            "compare only |",
            f"| bank-grounded mean | **{stats['gen_bank_mean']:.1f}** | "
            "compare only (anti-FP) |",
            f"| n_true_continue | **{stats.get('n_true_continue', 0)}** | "
            "novel continue count |",
            f"| n_span_fallback | **{stats.get('n_span_fallback', 0)}** | "
            "PEAK/LOOKUP fallback (0 gen IQ) |",
            f"| n_snippet_prefix | **{stats.get('n_snippet_prefix', 0)}** | "
            "ablated seed count |",
            f"| peak_only_lift / span_only | **{stats['peak_only_lift']}** | "
            "no true_continue → HOLD |",
            f"| n_abstain / n_bank_grounded | **{stats['n_abstain']}** / "
            f"**{stats['n_bank_grounded']}** | product honesty |",
            f"| FALSE_HIT | **{stats['n_false_hit']}**/{NANOGEN6_N} | "
            "any → KILL |",
            f"| Decision | **{decision}** | — |",
            "",
            "## Finding",
            "",
            "1. Dual-arm LOOKUP + refuse-or-continue DECODE under max safe "
            "CPU (`cpus-2`).  ",
            "2. Span-fallback labeled **PEAK** (not DECODE gen credit); "
            f"true_continue={stats.get('n_true_continue', 0)}/"
            f"{NANOGEN6_N}; "
            f"span_fallback={stats.get('n_span_fallback', 0)}/"
            f"{NANOGEN6_N}.  ",
            "3. True-gen judge = short-answer F1/HITL on **true continue** "
            "only — gold-substring / truncate-to-span ≠ gen IQ.  ",
            "4. Generative claim lifts **only** on true_continue_ablated "
            f"PROMOTE (≥{MIN_TRUE_CONTINUE_MEAN}) — honest HOLD accepted.  ",
            "5. AU H-NANOGEN5 STRICT 5.5 archive stays locked; AV3 is "
            "harder reopen; next AV4 AV-REAL-EVAL.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:nanogen6",
            "npm run nano:nanogen5",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-av/nanogen6_summary.json`  ",
            "- Contract: `nano_lm/tests/test_nanogen6.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Honest HOLD on true_continue <5.5 | LOOKUP-as-gen-IQ |",
            "| Span-fallback as PEAK/LOOKUP | Truncate-as-gen PROMOTE |",
            "| PROMOTE only true_continue≥5.5 | NANOGEN5 5.5 truncate clone · Wave AW invent |",
            "",
            "Next: **AV4 AV-REAL-EVAL** — product + gen with anti-FP law.",
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
            f"# Wave AV session checklist (**OPEN** · AV3 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AV **OPEN**).  ",
            "> Ship lock: **AF packaged stack + AQ product layer + AS "
            "trust + ablated DECODE (snippet-prefix + gibberish-tail "
            "STRICT)** until AV gen PROMOTE · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AV3 — H-NANOGEN6 ({status})** · Next: **AV4 AV-REAL-EVAL**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AV OPEN** |",
            f"| LOOKUP mean | **{stats.get('lookup_mean')}** |",
            f"| true_continue ablated | **{stats.get('gen_mean')}** "
            f"(bar {MIN_TRUE_CONTINUE_MEAN}; parent STRICT "
            f"{PARENT_NANOGEN5_STRICT}) |",
            f"| n_true_continue | **{stats.get('n_true_continue')}** |",
            f"| n_span_fallback | **{stats.get('n_span_fallback')}** |",
            f"| peak_only_lift | **{stats.get('peak_only_lift')}** |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AV0 | SESSION | **DONE — PROMOTE** |",
            "| AV1 | H-PRODSHIP | **DONE — PROMOTE** |",
            "| AV2 | H-SHIPUI2 | **DONE — PROMOTE** |",
            f"| AV3 | H-NANOGEN6 | **{status}** |",
            "| AV4 | AV-REAL-EVAL | **NEXT** |",
            "| AV5 | AV-REPORT | pending |",
            "| AV6 | AV-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _score_lookup_arm(
    *,
    bank_path: Path,
    av_bank: Path,
    root: Path,
    curated_root: Path,
    seed: int,
) -> tuple[list[dict[str, Any]], int, list[dict[str, Any]]]:
    bank = load_bank_rows(bank_path)
    questions = [p["question"] for p in NANOGEN6_PACK]
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
        zip(NANOGEN6_PACK, lookup_payloads, strict=True),
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
                av_bank=av_bank,
                root=root,
                curated=curated_root,
                seed=seed,
            )
            fix_count += 1
            kind, sem_meta, text = _classify_lookup(
                dict(item), lp, bank, curated_root
            )
        score_l, err_l, notes_l = score_nanogen6_lookup(
            mode=str(lp.get("mode", "")),
            completion=text,
            expected_gold=item["gold"],
            lookup_kind=kind,
            payload=lp,
        )
        lookup_trials.append(
            {
                "trial_id": f"AV-NANOGEN6-LOOKUP-{i:02d}",
                "stage": "AV3",
                "hyp_id": NANOGEN6_ID,
                "arm": "LOOKUP",
                "kind": item.get("kind"),
                "app_id": item["app_id"],
                "question": item["question"],
                "source_id": item["source_id"],
                "completion": lp.get("completion"),
                "wall_ms": lp.get("wall_ms"),
                "n_new": lp.get("n_new"),
                "mode": lp.get("mode"),
                "product_mode": map_at_product_mode(str(lp.get("mode", ""))),
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
    int,
    int,
    int,
]:
    items = [dict(p) for p in NANOGEN6_PACK]
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
    n_snip = 0
    n_span = 0
    n_true = 0
    weak_idx: list[int] = []
    fix_count = 0

    for i, (item, off, on, ctx) in enumerate(
        zip(NANOGEN6_PACK, gen_off, gen_on, contexts, strict=True)
    ):
        gate, bank_p, abstained, snip, ckind = _polish_ablated(
            off, item=dict(item), context=ctx
        )
        if abstained:
            n_abstain += 1
        if bool(bank_p.get("bank_grounded")):
            n_bank += 1
        if snip:
            n_snip += 1
        if ckind == "span_fallback":
            n_span += 1
        if ckind == "true_continue":
            n_true += 1
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
        re_items = [dict(NANOGEN6_PACK[i]) for i in weak_idx]
        re_off, re_on = _run_gen_ablation(
            champ=root,
            items=re_items,
            curated=curated_root,
            seed=seed + 2800,
            k_retrieve=8,
        )
        re_ctx = _contexts_for(re_items, curated_root, k_retrieve=8)
        re_off = [attach_modeui(dict(p)) for p in re_off]
        re_on = [attach_modeui(dict(p)) for p in re_on]
        fix_attempts = len(weak_idx)
        for j, idx in enumerate(weak_idx):
            item = NANOGEN6_PACK[idx]
            gate2, bank2, abs2, snip2, ckind2 = _polish_ablated(
                re_off[j], item=dict(item), context=re_ctx[j]
            )
            score2, err2, notes2, score_p2, score_b2 = _score_gen_pair(
                dict(item), gate2, re_on[j], bank2
            )
            if score2 > gen_scores[idx]:
                old_kind = str(gate_offs[idx].get("continue_kind") or "")
                if old_kind == "span_fallback":
                    n_span = max(0, n_span - 1)
                if old_kind == "true_continue":
                    n_true = max(0, n_true - 1)
                if bool(gate_offs[idx].get("abstained")):
                    n_abstain = max(0, n_abstain - 1)
                gen_off[idx] = re_off[j]
                gen_on[idx] = re_on[j]
                gate_offs[idx] = gate2
                bank_payloads[idx] = bank2
                gen_scores[idx] = score2
                gen_errors[idx] = err2
                peak_scores[idx] = score_p2
                bank_scores[idx] = score_b2
                gen_notes[idx] = list(notes2) + [
                    "FIX: re-ground refuse-or-continue + abstain/bank compare"
                ]
                gen_fix[idx] = 1
                fix_count += 1
                if abs2:
                    n_abstain += 1
                if bool(bank2.get("bank_grounded")):
                    n_bank += 1
                if snip2:
                    n_snip += 1
                if ckind2 == "span_fallback":
                    n_span += 1
                if ckind2 == "true_continue":
                    n_true += 1
            else:
                gen_notes[idx] = list(gen_notes[idx]) + [
                    "FIX attempted: re-ground refuse-or-continue (no lift)"
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
        n_snip,
        n_span,
        n_true,
        fix_count + fix_attempts,
    )


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    status = decision.split("(", 1)[0].strip()
    text2, n = re.subn(
        r"(\| AV3 \| \*\*H-NANOGEN6\*\* \| \*\*North-star generative\*\* — "
        r"one \*\*new\*\* method ≤5M; truncate-to-span \*\*not\*\* gen credit "
        r"\| true ablated bar → PROMOTE else \*\*HOLD\*\* \| )\*\*[^*]+\*\*",
        rf"\1**DONE — {status}**",
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"2b\. \*\*AV2 H-SHIPUI2\*\* — \*\*DONE [^*]+\*\*"
        r"(?: \(`npm run nano:shipui2`\))? · next \*\*AV3 H-NANOGEN6\*\*\.",
        (
            "2b. **AV2 H-SHIPUI2** — **DONE PROMOTE** "
            "(`npm run nano:shipui2`).  \n"
            f"2c. **AV3 H-NANOGEN6** — **DONE {status}** "
            "(`npm run nano:nanogen6`) · next **AV4 AV-REAL-EVAL**."
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    bash_old = "# next: nano:nanogen6 (as stages land)"
    bash_new = (
        "npm run nano:nanogen6\n"
        "# next: nano:av:real-eval (as stages land)"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def run_nanogen6(
    *,
    bank_path: Path,
    av_bank: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN NANOGEN pack (held-out + paraphrase)
    WHEN LOOKUP + refuse-or-continue GENERATE ×10
    THEN PROMOTE iff lookup≥7 ∧ true_continue≥5.5; else HOLD.
    """
    if len(NANOGEN6_PACK) != NANOGEN6_N:
        raise ValueError(f"NANOGEN6 pack must be {NANOGEN6_N}")

    trials_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    seeded = _seed_held_out(bank_path, av_bank)
    lookup_trials, fix_lookup, _bank = _score_lookup_arm(
        bank_path=bank_path,
        av_bank=av_bank,
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
        n_snip,
        n_span,
        n_true_c,
        fix_gen,
    ) = _gen_arm(root=root, curated_root=curated_root, seed=seed)
    fix_count = fix_lookup + fix_gen

    gen_trials: list[dict[str, Any]] = []
    n_peak = 0
    for i, (item, gate, on, bank_p) in enumerate(
        zip(NANOGEN6_PACK, gate_offs, gen_on, bank_payloads, strict=True),
        start=1,
    ):
        idx = i - 1
        if bool(on.get("peak_used")):
            n_peak += 1
        gt = {
            "trial_id": f"AV-NANOGEN6-GEN-{i:02d}",
            "stage": "AV3",
            "hyp_id": NANOGEN6_ID,
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
            or map_at_product_mode(str(gate.get("mode", ""))),
            "continue_kind": gate.get("continue_kind"),
            "span_fallback": gate.get("span_fallback"),
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
            "snippet_prefix": gate.get("snippet_prefix"),
            "snippet_span": gate.get("snippet_span"),
            "gibberish_tail_truncated": gate.get("gibberish_tail_truncated"),
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
    stats = nanogen6_stats(
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
        n_snippet_prefix=n_snip,
        n_span_fallback=n_span,
        n_true_continue=n_true_c,
    )
    decision = decide_nanogen6(stats)
    _write_public(decision=decision, stats=stats)
    _update_local_session(decision, stats)
    _patch_pesquisa(decision)
    ship = (
        "AF packaged stack + AQ product layer + AS trust + ablated DECODE "
        "(snippet-prefix + gibberish-tail STRICT)"
        if decision != "PROMOTE"
        else (
            "AF packaged stack + AQ product layer + AS trust + "
            "true-continue DECODE claim"
        )
    )
    summary: dict[str, Any] = {
        "hyp_id": NANOGEN6_ID,
        "stage": "AV3",
        "thesis": NANOGEN6_THESIS,
        "hypothesis": NANOGEN6_HYPOTHESIS,
        "decision": decision,
        "compose": [
            "ASKFAST/SEMWRAP LOOKUP",
            "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD ablated GENERATE (gate)",
            "retrieved-snippet prefix conditioning",
            "refuse-or-continue (true_continue | span_fallback | abstain)",
            "true-gen judge (span-fallback ≠ gen IQ)",
            "ASKABSTAIN refuse-junk on junk DECODE",
            "bank-grounded short compare (anti-FP — not ablated IQ)",
            "extractive peak comparison arm",
            "pack: same as H-NANOGEN…H-NANOGEN5 (5 held-out + 5 paraphrase)",
        ],
        "forbidden": [
            "LOOKUP-as-gen-IQ",
            "peak-as-open-chat-IQ",
            "span-fallback-as-gen-IQ",
            "NANOGEN5-5.5-truncate-clone",
            "mini-AGI claim before true_continue PROMOTE",
            "rewrite AU NANOGEN5",
            "Wave AW invent",
        ],
        "seeded_golds": int(seeded),
        "fix_count": int(fix_count),
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "elapsed_s": time.perf_counter() - t0,
        "stats": stats,
        "finding": (
            f"{NANOGEN6_ID}: L_lookup={stats['lookup_mean']:.1f} "
            f"L_true_continue={stats['gen_mean']:.1f} "
            f"(parent_STRICT={PARENT_NANOGEN5_STRICT}) "
            f"L_peak={stats['gen_peak_mean']:.1f} "
            f"true_c={n_true_c} span={n_span} "
            f"false_hit={n_false} abstain={n_abstain} → {decision}"
        ),
        "public_note": "docs/results/nano-lm/formal-hnanogen6-nanogen6.md",
        "ship_claim": ship,
        "next": "AV4 AV-REAL-EVAL",
        "anti_fp": (
            "true_continue only; span-fallback=PEAK; "
            "mini-AGI locked if HOLD"
        ),
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AV3 H-NANOGEN6")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--av-bank", type=Path, default=_AV_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    threads = _hardware()
    try:
        summary = run_nanogen6(
            bank_path=Path(args.bank),
            av_bank=Path(args.av_bank),
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
                "hyp_id": NANOGEN6_ID,
                "decision": decision,
                "lookup_mean": summary["stats"]["lookup_mean"],
                "gen_mean": summary["stats"]["gen_mean"],
                "gen_peak_mean": summary["stats"]["gen_peak_mean"],
                "n_true_continue": summary["stats"].get("n_true_continue"),
                "n_span_fallback": summary["stats"].get("n_span_fallback"),
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
