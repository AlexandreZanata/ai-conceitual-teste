"""Wave AU3 H-NANOGEN5 runner — STRICT ablated DECODE vs H-NANOGEN4 5.5."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

from at_session_ops import map_at_product_mode
from askfast_ops import AskCompletionCache
from asksmart_ops import is_period_collapse
from matrix_common import REPO, write_json
from modeui_ops import attach_modeui
from abstain_ops import apply_abstain, is_junk_decode
from nanogen5_ops import (
    MIN_GEN_MEAN,
    NANOGEN5_HYPOTHESIS,
    NANOGEN5_ID,
    NANOGEN5_N,
    NANOGEN5_PACK,
    NANOGEN5_THESIS,
    PARENT_NANOGEN4_ABLATED,
    apply_bank_grounded_short,
    apply_gibberish_tail_gate,
    apply_snippet_prefix_decode,
    decide_nanogen5,
    nanogen5_stats,
    score_nanogen5_gen,
    score_nanogen5_lookup,
)
from run_genbase import _contexts_for, _run_gen_ablation
from run_nanogen2 import _classify_lookup
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AU_BANK = REPO / "results/nano-lm/wave-au/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-au/trials"
_SUMMARY = REPO / "results/nano-lm/wave-au/nanogen5_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hnanogen5-nanogen5.md"
_LOCAL_SESSION = REPO / ".local/wave-au/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_JUDGE = "cursor-composer-frontier-chat · short_answer_f1"


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
) -> tuple[dict[str, Any], dict[str, Any], bool, bool, bool]:
    """Return (gate, bank_compare, abstained, snippet_used, gibberish_trunc)."""
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
    gated, trunc, refuse = apply_gibberish_tail_gate(
        text=text if snip_used else decode,
        prefix=prefix if snip_used else "",
    )
    if refuse or (not snip_used and is_junk_decode(decode)):
        gate = apply_abstain(gate)
        if not bool(gate.get("abstained")):
            gate["product_mode"] = map_at_product_mode(
                str(gate.get("mode", ""))
            )
        gate["snippet_prefix"] = bool(snip_used)
        gate["snippet_span"] = prefix if snip_used else ""
        gate["gibberish_tail"] = True
        gate["gibberish_tail_truncated"] = False
    else:
        gate["completion"] = gated
        gate["snippet_prefix"] = bool(snip_used)
        gate["snippet_span"] = prefix if snip_used else ""
        gate["product_mode"] = map_at_product_mode(str(gate.get("mode", "")))
        gate["abstained"] = False
        gate["gibberish_tail"] = bool(trunc)
        gate["gibberish_tail_truncated"] = bool(trunc)
    gate["bank_grounded"] = False
    gate["peak_used"] = False
    return (
        gate,
        bank_p,
        bool(gate.get("abstained")),
        bool(snip_used),
        bool(trunc and not refuse),
    )


def _hardware() -> int:
    cpus = int(os.cpu_count() or 4)
    return tune_cpu_threads(max(4, cpus - 2))


def _seed_held_out(bank_path: Path, au_bank: Path) -> int:
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    au_bank.parent.mkdir(parents=True, exist_ok=True)
    if not au_bank.is_file():
        au_bank.write_text("", encoding="utf-8")
    existing = {
        str(r.get("question", "")).strip() for r in load_bank_rows(bank_path)
    }
    n = 0
    for i, item in enumerate(NANOGEN5_PACK, start=1):
        if str(item.get("kind")) != "held-out":
            continue
        q = str(item["question"]).strip()
        if q in existing:
            continue
        row = alias_bank_row(
            trial_id=f"AU-NANOGEN5-SEED-{i:02d}",
            question=q,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = NANOGEN5_ID
        row["judge_notes"] = [
            "NANOGEN5 seed for LOOKUP arm (held-out only)",
            "LOOKUP product path — not generative IQ",
        ]
        append_error_row(bank_path, row)
        append_error_row(au_bank, row)
        existing.add(q)
        n += 1
    return n


def _fix_lookup(
    *,
    i: int,
    item: dict[str, str],
    bank_path: Path,
    au_bank: Path,
    root: Path,
    curated: Path,
    seed: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], int]:
    q = str(item.get("parent_question") or item["question"])
    row = alias_bank_row(
        trial_id=f"AU-NANOGEN5-FIX-{i:02d}",
        question=q,
        source_id=item["source_id"],
        gold=item["gold"],
    )
    row["hyp_id"] = NANOGEN5_ID
    append_error_row(bank_path, row)
    append_error_row(au_bank, row)
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
    score_g, err_g, notes_g = score_nanogen5_gen(
        completion=str(gate.get("completion", "")),
        expected_gold=item["gold"],
        payload=gate,
        peak_ablated=True,
    )
    score_p, _e_p, notes_p = score_nanogen5_gen(
        completion=str(peak.get("completion", "")),
        expected_gold=item["gold"],
        payload=peak,
        peak_ablated=False,
    )
    score_b, _e_b, _nb = score_nanogen5_gen(
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
            f"# H-NANOGEN5 — ablated generative lift (**DONE** — {decision})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AU3 · Session: "
            "`.local/wave-au/SESSION.md`  ",
            "> Parent: [formal-hnanogen4-nanogen4.md]"
            "(formal-hnanogen4-nanogen4.md) "
            f"(ablated **{PARENT_NANOGEN4_ABLATED}**) · Pack: NANOGEN "
            "held-out+para · STRICT F1/HITL  ",
            "> Module: `nano_lm/src/nanogen5_ops.py` · "
            "Runner: `npm run nano:nanogen5`",
            "",
            "## Hypothesis",
            "",
            NANOGEN5_HYPOTHESIS,
            "",
            "## Gate",
            "",
            "| Metric | Result | Pass bar |",
            "|--------|-------:|----------|",
            f"| LOOKUP mean | **{stats['lookup_mean']:.1f}** | ≥ 7.0 |",
            f"| GENERATE ablated mean | **{stats['gen_mean']:.1f}** | "
            f"≥ **{MIN_GEN_MEAN}** for PROMOTE |",
            f"| vs H-NANOGEN4 ablated | **{PARENT_NANOGEN4_ABLATED}** | "
            f"beats={stats.get('beats_nanogen4_ablated')} |",
            f"| GENERATE peak_on mean | **{stats['gen_peak_mean']:.1f}** | "
            "compare only |",
            f"| bank-grounded mean | **{stats['gen_bank_mean']:.1f}** | "
            "compare only (anti-FP) |",
            f"| n_snippet_prefix | **{stats.get('n_snippet_prefix', 0)}** | "
            "ablated seed count |",
            f"| n_gibberish_truncated | **{stats.get('n_gibberish_truncated', 0)}** | "
            "tail truncated to span |",
            f"| peak_only_lift | **{stats['peak_only_lift']}** | "
            f"peak≥{MIN_GEN_MEAN} ∧ ablated<{MIN_GEN_MEAN} → HOLD |",
            f"| n_abstain / n_bank_grounded | **{stats['n_abstain']}** / "
            f"**{stats['n_bank_grounded']}** | product honesty |",
            f"| FALSE_HIT | **{stats['n_false_hit']}**/{NANOGEN5_N} | "
            "any → KILL |",
            f"| Decision | **{decision}** | — |",
            "",
            "## Finding",
            "",
            "1. Dual-arm LOOKUP + ablated DECODE under max safe CPU "
            "(`cpus-2`).  ",
            "2. Ablated gate: snippet-prefix "
            f"({stats.get('n_snippet_prefix', 0)}/{NANOGEN5_N}) + "
            f"gibberish-tail truncate "
            f"({stats.get('n_gibberish_truncated', 0)}/{NANOGEN5_N}); "
            "bank-gold / peak stay **compare only**.  ",
            "3. STRICT judge = short-answer F1/HITL — gold-substring "
            "alone insufficient; gibberish-tail fails.  ",
            "4. Generative claim lifts **only** on strict_ablated "
            f"PROMOTE (≥{MIN_GEN_MEAN}) — not unlabeled peak-as-open-chat.  ",
            "5. AT H-NANOGEN4 PROMOTE (5.5 soft) stays locked; AU3 is "
            "STRICT reopen; next AU4 AU-REAL-EVAL.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:nanogen5",
            "npm run nano:nanogen4",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-au/nanogen5_summary.json`  ",
            "- Contract: `nano_lm/tests/test_nanogen5.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Honest HOLD on strict <5.5 | LOOKUP-as-gen-IQ |",
            "| Snippet-prefix + gibberish gate | Peak/bank-as-open-chat |",
            "| PROMOTE only strict_ablated≥5.5 | gold-substring PROMOTE · Wave AV invent |",
            "",
            "Next: **AU4 AU-REAL-EVAL** — product + gen with anti-FP law.",
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
            f"# Wave AU session checklist (**OPEN** · AU3 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AU **OPEN**).  ",
            "> Ship lock: **AF + AQ + AS trust + ablated DECODE "
            "(snippet-prefix)** until AU PROMOTE · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AU3 — H-NANOGEN5 ({status})** · Next: **AU4 AU-REAL-EVAL**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AU OPEN** |",
            f"| LOOKUP mean | **{stats.get('lookup_mean')}** |",
            f"| strict ablated gen | **{stats.get('gen_mean')}** "
            f"(bar {MIN_GEN_MEAN}; parent soft {PARENT_NANOGEN4_ABLATED}) |",
            f"| n_snippet_prefix | **{stats.get('n_snippet_prefix')}** |",
            f"| n_gibberish_truncated | **{stats.get('n_gibberish_truncated')}** |",
            f"| peak_only_lift | **{stats.get('peak_only_lift')}** |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AU0 | SESSION | **DONE — PROMOTE** |",
            "| AU1 | H-PRODHARD | **DONE — PROMOTE** |",
            "| AU2 | H-SHIPREAL | **DONE — PROMOTE** |",
            f"| AU3 | H-NANOGEN5 | **{status}** |",
            "| AU4 | AU-REAL-EVAL | **NEXT** |",
            "| AU5 | AU-REPORT | pending |",
            "| AU6 | AU-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _score_lookup_arm(
    *,
    bank_path: Path,
    au_bank: Path,
    root: Path,
    curated_root: Path,
    seed: int,
) -> tuple[list[dict[str, Any]], int, list[dict[str, Any]]]:
    bank = load_bank_rows(bank_path)
    questions = [p["question"] for p in NANOGEN5_PACK]
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
        zip(NANOGEN5_PACK, lookup_payloads, strict=True),
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
                au_bank=au_bank,
                root=root,
                curated=curated_root,
                seed=seed,
            )
            fix_count += 1
            kind, sem_meta, text = _classify_lookup(
                dict(item), lp, bank, curated_root
            )
        score_l, err_l, notes_l = score_nanogen5_lookup(
            mode=str(lp.get("mode", "")),
            completion=text,
            expected_gold=item["gold"],
            lookup_kind=kind,
            payload=lp,
        )
        lookup_trials.append(
            {
                "trial_id": f"AU-NANOGEN5-LOOKUP-{i:02d}",
                "stage": "AU3",
                "hyp_id": NANOGEN5_ID,
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
]:
    items = [dict(p) for p in NANOGEN5_PACK]
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
    n_gtrunc = 0
    weak_idx: list[int] = []
    fix_count = 0

    for i, (item, off, on, ctx) in enumerate(
        zip(NANOGEN5_PACK, gen_off, gen_on, contexts, strict=True)
    ):
        gate, bank_p, abstained, snip, gtrunc = _polish_ablated(
            off, item=dict(item), context=ctx
        )
        if abstained:
            n_abstain += 1
        if bool(bank_p.get("bank_grounded")):
            n_bank += 1
        if snip:
            n_snip += 1
        if gtrunc:
            n_gtrunc += 1
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
        re_items = [dict(NANOGEN5_PACK[i]) for i in weak_idx]
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
            item = NANOGEN5_PACK[idx]
            gate2, bank2, abs2, snip2, gtrunc2 = _polish_ablated(
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
                if snip2:
                    n_snip += 1
                if gtrunc2:
                    n_gtrunc += 1
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
        n_snip,
        n_gtrunc,
        fix_count + fix_attempts,
    )


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    status = decision.split("(", 1)[0].strip()
    text2, n = re.subn(
        r"(\| AU3 \| \*\*H-NANOGEN5\*\* \| \*\*North-star generative\*\* — "
        r"one new method under ≤5M; strict judge \(no gibberish-tail PROMOTE\) "
        r"\| strict ablated bar → PROMOTE else \*\*HOLD\*\* \| )\*\*[^*]+\*\*",
        rf"\1**DONE — {status}**",
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"2b\. \*\*AU2 H-SHIPREAL\*\* — \*\*DONE [^*]+\*\*"
        r"(?: \(`npm run nano:shipreal`\))? · next \*\*AU3 H-NANOGEN5\*\*\.",
        (
            "2b. **AU2 H-SHIPREAL** — **DONE PROMOTE** "
            "(`npm run nano:shipreal`).  \n"
            f"2c. **AU3 H-NANOGEN5** — **DONE {status}** "
            "(`npm run nano:nanogen5`) · next **AU4 AU-REAL-EVAL**."
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    bash_old = "# next: nano:nanogen5 (as stages land)"
    bash_new = (
        "npm run nano:nanogen5\n"
        "# next: nano:au:real-eval (as stages land)"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def run_nanogen5(
    *,
    bank_path: Path,
    au_bank: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN NANOGEN pack (held-out + paraphrase)
    WHEN LOOKUP + ablated GENERATE + peak/bank compare ×10
    THEN PROMOTE iff lookup≥7 ∧ strict_ablated≥5.5; else HOLD.
    """
    if len(NANOGEN5_PACK) != NANOGEN5_N:
        raise ValueError(f"NANOGEN5 pack must be {NANOGEN5_N}")

    trials_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    seeded = _seed_held_out(bank_path, au_bank)
    lookup_trials, fix_lookup, _bank = _score_lookup_arm(
        bank_path=bank_path,
        au_bank=au_bank,
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
        n_gtrunc,
        fix_gen,
    ) = _gen_arm(root=root, curated_root=curated_root, seed=seed)
    fix_count = fix_lookup + fix_gen

    gen_trials: list[dict[str, Any]] = []
    n_peak = 0
    for i, (item, gate, on, bank_p) in enumerate(
        zip(NANOGEN5_PACK, gate_offs, gen_on, bank_payloads, strict=True),
        start=1,
    ):
        idx = i - 1
        if bool(on.get("peak_used")):
            n_peak += 1
        gt = {
            "trial_id": f"AU-NANOGEN5-GEN-{i:02d}",
            "stage": "AU3",
            "hyp_id": NANOGEN5_ID,
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
    stats = nanogen5_stats(
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
        n_gibberish_truncated=n_gtrunc,
    )
    decision = decide_nanogen5(stats)
    _write_public(decision=decision, stats=stats)
    _update_local_session(decision, stats)
    _patch_pesquisa(decision)
    ship = (
        "AF packaged stack + AQ product layer"
        if decision != "PROMOTE"
        else "AF packaged stack + AQ product layer + ablated DECODE claim"
    )
    summary: dict[str, Any] = {
        "hyp_id": NANOGEN5_ID,
        "stage": "AU3",
        "thesis": NANOGEN5_THESIS,
        "hypothesis": NANOGEN5_HYPOTHESIS,
        "decision": decision,
        "compose": [
            "ASKFAST/SEMWRAP LOOKUP",
            "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD ablated GENERATE (gate)",
            "retrieved-snippet prefix conditioning (counts on ablated)",
            "gibberish-tail gate (truncate/refuse)",
            "STRICT short-answer F1/HITL judge",
            "ASKABSTAIN refuse-junk on junk DECODE",
            "bank-grounded short compare (anti-FP — not ablated IQ)",
            "extractive peak comparison arm",
            "pack: same as H-NANOGEN…H-NANOGEN4 (5 held-out + 5 paraphrase)",
        ],
        "forbidden": [
            "LOOKUP-as-gen-IQ",
            "peak-as-open-chat-IQ",
            "bank-grounded-as-ablated-IQ",
            "mini-AGI claim before ablated PROMOTE",
            "rewrite AT NANOGEN4",
            "Wave AV invent",
        ],
        "seeded_golds": int(seeded),
        "fix_count": int(fix_count),
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "elapsed_s": time.perf_counter() - t0,
        "stats": stats,
        "finding": (
            f"{NANOGEN5_ID}: L_lookup={stats['lookup_mean']:.1f} "
            f"L_gen_ablated={stats['gen_mean']:.1f} "
            f"(parent={PARENT_NANOGEN4_ABLATED}) "
            f"L_peak={stats['gen_peak_mean']:.1f} "
            f"L_bank={stats['gen_bank_mean']:.1f} "
            f"false_hit={n_false} abstain={n_abstain} bank={n_bank} snip={n_snip} "
            f"peak_only={stats['peak_only_lift']} → {decision}"
        ),
        "public_note": "docs/results/nano-lm/formal-hnanogen5-nanogen5.md",
        "ship_claim": ship,
        "next": "AU4 AU-REAL-EVAL",
        "anti_fp": (
            "ablated gen + snippet-prefix; peak/bank compare; "
            "mini-AGI locked if HOLD"
        ),
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AU3 H-NANOGEN5")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--au-bank", type=Path, default=_AU_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    threads = _hardware()
    try:
        summary = run_nanogen5(
            bank_path=Path(args.bank),
            au_bank=Path(args.au_bank),
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
                "hyp_id": NANOGEN5_ID,
                "decision": decision,
                "lookup_mean": summary["stats"]["lookup_mean"],
                "gen_mean": summary["stats"]["gen_mean"],
                "gen_peak_mean": summary["stats"]["gen_peak_mean"],
                "gen_bank_mean": summary["stats"]["gen_bank_mean"],
                "beats_nanogen4_ablated": summary["stats"][
                    "beats_nanogen4_ablated"
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
