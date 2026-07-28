"""Wave BA0 SESSION: freeze BA-FOREVER · AZ hold · scoreboard · gen-defer."""

from __future__ import annotations

from typing import Mapping, Sequence

from au_session_ops import AU0_MODES, map_au_product_mode
from az_session_ops import (
    AZ0_HELDOUT_FP_ROWS,
    AZ0_OVERREFUSE_ROWS,
    AZ0_SHIP_LOCK,
)

__all__ = [
    "BA0_ID",
    "BA0_THESIS",
    "BA0_MODES",
    "BA0_LATENCY_PATHS",
    "BA0_CITED_AZ_LOCKS",
    "BA0_SCOREBOARD",
    "BA0_FOREVER_PROTOCOL",
    "BA0_FOREVER_ROWS",
    "BA0_AZ_HOLD_PROTOCOL",
    "BA0_CTX_BASELINE",
    "BA0_SPEED_BASELINE",
    "BA0_GEN_STANCE",
    "BA0_TRUE_GEN_JUDGE",
    "BA0_REAL_EVAL_PROTOCOL",
    "BA0_ASK_BATTERY",
    "BA0_SAFE_NOTE",
    "BA0_ANTI_FP",
    "BA0_NORTH_STAR",
    "BA0_SHIP_LOCK",
    "map_ba_product_mode",
    "decide_ba0_session",
]

BA0_ID = "BA0-SESSION"
BA0_THESIS = (
    "Wave BA OPEN: freeze BA-FOREVER (pow·mod·max·sort·len + paraphrases) · "
    "AZ hold (div·sub·BIP · a.clear()) · §1 anti-FP scoreboard · "
    "ctx/speed baselines from AZ · gen method stance = defer "
    "(M1|M2|M3|defer; H-NANOGEN11; not NANOGEN10+rename) · real-eval; "
    "next BA1 H-REALGAIN (not CTX/SMART/FAST clone)"
)

BA0_MODES: frozenset[str] = AU0_MODES
BA0_LATENCY_PATHS: tuple[str, ...] = (
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
)

BA0_CITED_AZ_LOCKS: frozenset[str] = frozenset(
    {
        "H-PRODGEN",
        "H-SHIPAZ",
        "H-NANOGEN10",
        "AZ-REAL-EVAL",
        "AZ-FREEZE",
    }
)

BA0_SHIP_LOCK = AZ0_SHIP_LOCK

BA0_NORTH_STAR = (
    "Nano generative / mini-AGI-inspired ≤5M: real intelligence scoreboard "
    "(BA-FOREVER FH 0 + AZ hold + live ask) + measurable context & speed "
    "on prod path + one honest generative method (M1|M2|M3) — else "
    "HOLD/DEFER; never pack theater · never LOOKUP-as-IQ · never "
    "NANOGEN11 = NANOGEN10+rename"
)

BA0_GEN_STANCE: Mapping[str, object] = {
    "stage": "BA0 freezes stance; BA4 H-NANOGEN11 applies or HOLD/DEFER",
    "stance": "defer",
    "allowed_stances": ["M1", "M2", "M3", "defer"],
    "method_candidates": {
        "M1": "teacher distill continue + anti-copy-gold loss",
        "M2": "student draft + bank/teacher rejector (hybrid)",
        "M3": "named CAPCHECK (raise params with ablations)",
    },
    "capcheck": "closed",
    "named_hyp": "H-NANOGEN11",
    "named_realgain": "H-REALGAIN",
    "named_fast": "H-FASTREAL",
    "named_ctx": "H-CTXREAL2",
    "nanogen6_hold_cited": True,
    "nanogen7_hold_cited": True,
    "nanogen8_defer_cited": True,
    "nanogen9_defer_cited": True,
    "nanogen10_defer_cited": True,
    "nanogen11_rename_forbidden": True,
    "true_continue_required_for_promote": True,
    "span_fallback_neq_gen": True,
    "rationale": (
        "No real new train/data/arch method ready at BA0; "
        "NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER stand; CAPCHECK stays closed; "
        "prefer forever anti-FP (H-REALGAIN) + ctx/speed measure + honest "
        "paper over vanity NANOGEN11 clone; BA4 PROMOTE only under "
        "true_continue else HOLD/DEFER"
    ),
    "ba4_gate": "true_continue → PROMOTE else HOLD/DEFER",
}

BA0_SAFE_NOTE = (
    "SAFE / ADVSAFE false-hit score ≠ answer quality; "
    "SAFE = no wrong gold only (anti-FP); "
    "pack FH 0 ≠ forever held-out generalization; "
    "intent-mismatch LOOKUP = false-hit (pow/mod/max/sort/len); "
    "exact-gold ABSTAIN = product miss; "
    "gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE"
)

BA0_ANTI_FP = (
    "LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; "
    "never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; "
    "intent-mismatch LOOKUP = false-hit (BA-FOREVER pow/mod/max/sort/len); "
    "exact-gold ABSTAIN = miss (a.clear()); "
    "AZ hold div·sub·BIP FH must stay 0; "
    "truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; "
    "eval path = prod ask path; pack PASS with forever FP = PACK THEATER; "
    "generative bar = BA4 only under real new method; "
    "no NANOGEN11 = NANOGEN10+rename; no CTX/SMART/FAST clone; "
    "no invent Wave BB without lab-book reopen; "
    "prefer HOLD/defer over fake PROMOTE"
)

BA0_TRUE_GEN_JUDGE: Mapping[str, object] = {
    "stage": "BA4 H-NANOGEN11 applies only if stance≠defer or new method; "
    "BA0 freezes judge law",
    "gold_substring_insufficient": True,
    "gibberish_tail_fails": True,
    "span_fallback_neq_gen": True,
    "telemetry_neq_content_ok": True,
    "usable_continue_required": True,
    "nanogen6_hold_archived": True,
    "nanogen7_tac_hold_archived": True,
    "nanogen8_defer_archived": True,
    "nanogen9_defer_archived": True,
    "nanogen10_defer_archived": True,
    "nanogen11_rename_forbidden": True,
    "scoring": "short_answer_f1_or_hitl_true_continue_only",
    "promote_bar": "true_continue else HOLD/DEFER",
}

# AZ PRODGEN republished latency (speed baseline for BA2).
BA0_SPEED_BASELINE: Mapping[str, object] = {
    "source": "H-PRODGEN / formal-hprodgen-prodgen.md",
    "path": "nano:z:ask prod path",
    "unit": "wall_ms",
    "paths": {
        "LOOKUP": {"p50": 0.0, "p99": 0.0},
        "PEAK": {"p50": 0.02575, "p99": 0.04586},
        "DECODE": {"p50": 11.37002, "p99": 13.25987},
        "ABSTAIN": {"p50": 95.44715, "p99": 119.44308},
    },
    "quality_regress_forbidden": True,
    "warm_cache_vanity_forbidden": True,
    "ba2_gate": "speed PROMOTE only if §1 anti-FP bars hold",
}

# Context baseline: content bars required (L_eff alone ≠ win).
BA0_CTX_BASELINE: Mapping[str, object] = {
    "source": "H-SHIPAZ / prior CTX* PROMOTE archive (content-first)",
    "l_eff_alone_insufficient": True,
    "content_bars_required": True,
    "modes_visible_required": True,
    "long_cite_howto_pack": True,
    "honest_abstain_when_missing": True,
    "ba3_gate": (
        "H-CTXREAL2 PROMOTE only if content_ok + no new intent FP + "
        "p50/p99 published + modes visible"
    ),
}

BA0_SCOREBOARD: Mapping[str, object] = {
    "stage": "BA1 H-REALGAIN closes bars; BA0 freezes §1 scoreboard",
    "cite_az_locks": sorted(BA0_CITED_AZ_LOCKS),
    "accept_artifact": (
        "AF+AQ+AS trust + STRICT ablated DECODE (AZ H-PRODGEN·H-SHIPAZ); "
        "NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER; not TAC unlocked"
    ),
    "debts": [
        {
            "id": "forever_false_hit_zero",
            "evidence": (
                "Live FP: pow/mod/max→add LOOKUP; sort→reverse; "
                "len→junk/unrelated gold"
            ),
            "fix": "forever intent FH 0 via gate (not bank-stuff)",
            "bar": "forever_false_hit_max=0",
        },
        {
            "id": "az_hold_zero",
            "evidence": "AZ div·sub·BIP FH 0 + a.clear() LOOKUP must hold",
            "fix": "AZ held-out + over-refuse regression",
            "bar": "az_hold_false_hit_max=0; overrefuse_miss_max=0",
        },
        {
            "id": "overrefuse_exact_gold",
            "evidence": "exact clear gold must LOOKUP",
            "fix": "exact / high-margin gold → LOOKUP",
            "bar": "overrefuse_miss_max=0",
        },
        {
            "id": "live_ask_scoreboard",
            "evidence": "ok:true ≠ content correct; score OK|FP|MISS|ABSTAIN-OK",
            "fix": "live nano:z:ask on BA-FOREVER + AZ hold + novel probes",
            "bar": "live_ask_scored True",
        },
        {
            "id": "speed_baseline_publish",
            "evidence": "AZ PRODGEN p50/p99 republished at BA0",
            "fix": "BA2 measures prod wall without FP regress",
            "bar": "speed_baseline_published True",
        },
        {
            "id": "ctx_baseline_publish",
            "evidence": "content bars required; L_eff alone forbidden",
            "fix": "BA3 measures usable long/cite/howto",
            "bar": "ctx_baseline_published True",
        },
        {
            "id": "mode_ui_always",
            "evidence": "SHIPAZ modes+content PROMOTE",
            "fix": "always print mode=LOOKUP|PEAK|DECODE|ABSTAIN",
            "bar": "modes_visible 4/4",
        },
        {
            "id": "decode_content_law",
            "evidence": "STRICT ablated DECODE; gibberish ≠ content_ok",
            "fix": "DECODE usable or ABSTAIN; no fake DECODE IQ",
            "bar": "decode_gibberish_neq_content_ok True",
        },
        {
            "id": "gen_defer_stance",
            "evidence": "NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER; no new method",
            "fix": "stance defer · CAPCHECK closed · no NANOGEN11 rename",
            "bar": "gen_stance=defer; nanogen11_rename_forbidden",
        },
        {
            "id": "paraphrase_eval_rule",
            "evidence": "BA-FOREVER seeds + held-out paraphrases at eval",
            "fix": "never bank-stuff exact seed strings",
            "bar": "paraphrase_required True; bank_stuff_forbidden",
        },
    ],
    "metrics": [
        "forever_false_hit",
        "az_hold_false_hit",
        "overrefuse_miss",
        "live_ask_ok_fp_miss",
        "p50_wall_ms",
        "p99_wall_ms",
        "ctx_content_ok",
        "modes_visible",
        "decode_content_ok",
        "true_continue_ablated",
    ],
    "bars": {
        "forever_false_hit_max": 0,
        "az_hold_false_hit_max": 0,
        "overrefuse_miss_max": 0,
        "forever_min_n": 15,
        "forever_classes_min": 5,
        "modes_required": list(BA0_LATENCY_PATHS),
        "decode_gibberish_neq_content_ok": True,
        "default_ask_intent_mismatch": "ABSTAIN",
        "default_ask_near_miss": "ABSTAIN",
        "default_ask_ood": "ABSTAIN",
        "default_ask_exact_gold": "LOOKUP",
        "latency_publish": True,
        "ctx_content_bars": True,
        "l_eff_alone_forbidden": True,
        "eval_eq_prod_ask": True,
        "pack_pass_neq_forever": True,
        "bank_stuff_forbidden": True,
        "paraphrase_required": True,
        "regression_hold": True,
        "speed_baseline_published": True,
        "ctx_baseline_published": True,
        "live_ask_scored": True,
    },
    "baselines": {
        "az_heldout_fh": 0,
        "az_overrefuse_miss": 0,
        "prodgen_latency": dict(BA0_SPEED_BASELINE["paths"]),  # type: ignore[arg-type]
        "shipaz_modes_content": "PROMOTE",
        "nanogen6_decision": "HOLD",
        "nanogen7_decision": "HOLD",
        "nanogen8_decision": "DEFER",
        "nanogen9_decision": "DEFER",
        "nanogen10_decision": "DEFER",
        "az_real_eval_battery": "9/9",
        "live_audit_ba_forever_fp": "pow/mod/max/sort/len FP observed",
        "forever_classes": [
            "ops_pow",
            "ops_mod",
            "ops_max",
            "list_sort",
            "list_len",
        ],
        "ship_lock": BA0_SHIP_LOCK,
    },
    "runners": [
        "nano:z:ask",
        "nano:prodgen",
        "nano:shipaz",
        "nano:nanogen10",
        "nano:advsafe",
        "nano:metrics",
        "nano:askabstain",
    ],
    "no_reopen_unless_fail": [
        "H-PRODGEN",
        "H-SHIPAZ",
        "H-PRODINT",
        "H-SHIPAY",
        "H-PRODNAT",
        "H-ADVSAFE",
    ],
    "complete_kb_claim_forbidden": True,
}

# Forever held-out residual FP (≠ AZ div·sub·wrong-slot).
BA0_FOREVER_ROWS: tuple[dict[str, str], ...] = (
    {
        "id": "BA-FH-01",
        "class": "ops_pow",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named pow2 that returns "
            "a raised to the power of b for two integers."
        ),
    },
    {
        "id": "BA-FH-02",
        "class": "ops_pow",
        "expect_mode": "ABSTAIN",
        "question": (
            "I need power(a, b) in Python — exponentiate two ints, "
            "not add them."
        ),
    },
    {
        "id": "BA-FH-03",
        "class": "ops_pow",
        "expect_mode": "ABSTAIN",
        "question": (
            "Show pow2 for integers a and b returning a**b. "
            "Do not return a+b."
        ),
    },
    {
        "id": "BA-FH-04",
        "class": "ops_mod",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named mod that returns "
            "the remainder of a divided by b."
        ),
    },
    {
        "id": "BA-FH-05",
        "class": "ops_mod",
        "expect_mode": "ABSTAIN",
        "question": (
            "I need mod(a, b) in Python — remainder of two ints, "
            "not add them."
        ),
    },
    {
        "id": "BA-FH-06",
        "class": "ops_mod",
        "expect_mode": "ABSTAIN",
        "question": (
            "Show mod for integers a and b returning a % b. "
            "Do not return a+b."
        ),
    },
    {
        "id": "BA-FH-07",
        "class": "ops_max",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named max2 that returns "
            "the larger of two integers a and b."
        ),
    },
    {
        "id": "BA-FH-08",
        "class": "ops_max",
        "expect_mode": "ABSTAIN",
        "question": (
            "I need max2(a, b) in Python — larger of two ints, "
            "not add them."
        ),
    },
    {
        "id": "BA-FH-09",
        "class": "ops_max",
        "expect_mode": "ABSTAIN",
        "question": (
            "Show max2 for integers a and b returning the greater value. "
            "Do not return a+b."
        ),
    },
    {
        "id": "BA-FH-10",
        "class": "list_sort",
        "expect_mode": "ABSTAIN",
        "question": (
            "Sort list `a` ascending in place — one method call. "
            "Do not reverse it."
        ),
    },
    {
        "id": "BA-FH-11",
        "class": "list_sort",
        "expect_mode": "ABSTAIN",
        "question": (
            "How do I sort Python list a ascending in place "
            "without reversing?"
        ),
    },
    {
        "id": "BA-FH-12",
        "class": "list_sort",
        "expect_mode": "ABSTAIN",
        "question": (
            "Python: order list a from smallest to largest in place — "
            "not a.reverse()."
        ),
    },
    {
        "id": "BA-FH-13",
        "class": "list_len",
        "expect_mode": "ABSTAIN",
        "question": (
            "What is the length of Python list a — one builtin call?"
        ),
    },
    {
        "id": "BA-FH-14",
        "class": "list_len",
        "expect_mode": "ABSTAIN",
        "question": (
            "How many elements does list a contain? "
            "Do not invent unrelated range junk."
        ),
    },
    {
        "id": "BA-FH-15",
        "class": "list_len",
        "expect_mode": "ABSTAIN",
        "question": (
            "Python: report len(a) for list a — not a reverse or add."
        ),
    },
)

BA0_FOREVER_PROTOCOL: Mapping[str, object] = {
    "stage": "BA1 H-REALGAIN scores; BA0 freezes protocol",
    "held_out": True,
    "forever": True,
    "bank_stuff_forbidden": True,
    "paraphrase_required": True,
    "neq_az_heldout": True,
    "intent_mismatch_is_false_hit": True,
    "source": (
        "live forever FP (pow≠add · mod≠add · max≠add · "
        "sort≠reverse · len≠junk)"
    ),
    "min_n": 15,
    "classes_min": 5,
    "required_classes": [
        "ops_pow",
        "ops_mod",
        "ops_max",
        "list_sort",
        "list_len",
    ],
    "scoring": "false-hit rate on default ask path (mismatch → ABSTAIN)",
    "path": "nano:z:ask --wrap --semwrap",
    "pack_pass_neq_forever": True,
    "live_fp_id": "BA-FH-01",
    "rows": list(BA0_FOREVER_ROWS),
}

BA0_AZ_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BA1 must hold AZ bars; BA0 freezes regression pack",
    "heldout_source": "AZ0_HELDOUT_FP_ROWS",
    "overrefuse_source": "AZ0_OVERREFUSE_ROWS",
    "heldout_n": len(AZ0_HELDOUT_FP_ROWS),
    "overrefuse_n": len(AZ0_OVERREFUSE_ROWS),
    "heldout_false_hit_max": 0,
    "overrefuse_miss_max": 0,
    "required_classes": ["ops_div", "ops_sub", "wrong_slot", "exact_clear"],
    "path": "nano:z:ask --wrap --semwrap",
    "regression_hold": True,
}

BA0_REAL_EVAL_PROTOCOL: Mapping[str, object] = {
    "live_ask_battery": True,
    "summary_only_forbidden": True,
    "product_mode_required": True,
    "wall_ms_n_new_mandatory": True,
    "wall_ms_n_new_insufficient_for_decode_quality": True,
    "lookup_neq_iq": True,
    "peak_neq_open_chat": True,
    "safe_neq_quality": True,
    "intent_mismatch_is_false_hit": True,
    "exact_gold_abstain_is_miss": True,
    "gold_substring_neq_gen": True,
    "gibberish_tail_fails": True,
    "span_fallback_neq_gen": True,
    "pack_pass_neq_forever": True,
    "eval_eq_prod_ask": True,
    "answer_usability_scored": True,
    "score_labels": ["OK", "FP", "MISS", "ABSTAIN-OK"],
    "gen_claim_rule": (
        "only if BA4 H-NANOGEN11 PROMOTE (true_continue; "
        "real new method M1|M2|M3; never NANOGEN10+rename; "
        "span-fallback ≠ gen)"
    ),
    "mini_agi_rule": (
        "forbidden while gen stance defer or NANOGEN11 HOLD/DEFER"
    ),
    "stage": "BA5 BA-REAL-EVAL scores; BA0 freezes protocol",
}

BA0_ASK_BATTERY: tuple[dict[str, str], ...] = (
    {
        "id": "BA-ASK-01",
        "kind": "known_lookup",
        "expect_mode": "LOOKUP",
        "question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
    },
    {
        "id": "BA-ASK-02",
        "kind": "ood_abstain",
        "expect_mode": "ABSTAIN",
        "question": "Which chef won the 2019 World Cup of Baking?",
    },
    {
        "id": "BA-ASK-03",
        "kind": "near_miss",
        "expect_mode": "ABSTAIN",
        "question": (
            "BIP-39 entropy formula is CS = ENT / 32 — confirm for "
            "SegWit witness discount?"
        ),
    },
    {
        "id": "BA-ASK-04",
        "kind": "labeled_peak",
        "expect_mode": "PEAK",
        "question": (
            "From the curated Rust book intro, extract one sentence "
            "on ownership (label PEAK, not open chat)."
        ),
    },
    {
        "id": "BA-ASK-05",
        "kind": "decode_content",
        "expect_mode": "DECODE",
        "question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
    },
    {
        "id": "BA-ASK-06",
        "kind": "junk_trap",
        "expect_mode": "ABSTAIN",
        "question": ".",
    },
    {
        "id": "BA-ASK-07",
        "kind": "forever_intent_fp",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named pow2 that returns "
            "a raised to the power of b for two integers."
        ),
    },
    {
        "id": "BA-ASK-08",
        "kind": "overrefuse_gold",
        "expect_mode": "LOOKUP",
        "question": "Remove all items from list `a` — one method call.",
    },
    {
        "id": "BA-ASK-09",
        "kind": "az_hold_div",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named div that returns "
            "the quotient of two integers a and b."
        ),
    },
    {
        "id": "BA-ASK-10",
        "kind": "forever_list_fp",
        "expect_mode": "ABSTAIN",
        "question": (
            "Sort list `a` ascending in place — one method call. "
            "Do not reverse it."
        ),
    },
)


def map_ba_product_mode(raw_mode: str) -> str:
    """
    GIVEN raw telemetry mode string
    WHEN applying BA0 mode charter (inherits AU0 aliases)
    THEN return LOOKUP | PEAK | DECODE | ABSTAIN | UNKNOWN.
    """
    return map_au_product_mode(raw_mode)


def _gate_modes() -> str | None:
    if set(BA0_LATENCY_PATHS) != BA0_MODES:
        return "KILL (latency paths ≠ mode charter)"
    if "ABSTAIN" not in BA0_MODES:
        return "KILL (ABSTAIN missing from modes)"
    return None


def _gate_cited_az() -> str | None:
    cited = BA0_SCOREBOARD.get("cite_az_locks")
    if not isinstance(cited, list):
        return "KILL (scoreboard must cite AZ locks)"
    if set(cited) != BA0_CITED_AZ_LOCKS:
        return "KILL (scoreboard AZ lock citations incomplete)"
    return None


def _gate_debt_ids() -> str | None:
    debts = BA0_SCOREBOARD.get("debts")
    if not isinstance(debts, list) or len(debts) < 10:
        return "KILL (scoreboard must list ≥10 post-AZ debts)"
    ids = {str(d.get("id", "")) for d in debts if isinstance(d, dict)}
    need = {
        "forever_false_hit_zero",
        "az_hold_zero",
        "overrefuse_exact_gold",
        "live_ask_scoreboard",
        "speed_baseline_publish",
        "ctx_baseline_publish",
        "mode_ui_always",
        "decode_content_law",
        "gen_defer_stance",
        "paraphrase_eval_rule",
    }
    if not need.issubset(ids):
        return "KILL (scoreboard debt ids incomplete)"
    return None


def _gate_debt_bar_nums(bars: Mapping[str, object]) -> str | None:
    if int(bars.get("forever_false_hit_max", 1)) != 0:
        return "KILL (forever_false_hit_max must be 0)"
    if int(bars.get("az_hold_false_hit_max", 1)) != 0:
        return "KILL (az_hold_false_hit_max must be 0)"
    if int(bars.get("overrefuse_miss_max", 1)) != 0:
        return "KILL (overrefuse_miss_max must be 0)"
    if int(bars.get("forever_min_n", 0)) < 15:
        return "KILL (forever_min_n must be ≥15)"
    if int(bars.get("forever_classes_min", 0)) < 5:
        return "KILL (forever_classes_min must be ≥5)"
    return None


def _gate_debt_bar_flags(bars: Mapping[str, object]) -> str | None:
    flags = (
        ("decode_gibberish_neq_content_ok", "KILL (DECODE gibberish≠content_ok)"),
        ("eval_eq_prod_ask", "KILL (eval path must equal prod ask path)"),
        ("pack_pass_neq_forever", "KILL (pack PASS ≠ forever bar missing)"),
        ("bank_stuff_forbidden", "KILL (scoreboard must forbid bank stuffing)"),
        ("paraphrase_required", "KILL (scoreboard must require paraphrases)"),
        ("regression_hold", "KILL (scoreboard must require regression_hold)"),
        ("speed_baseline_published", "KILL (speed baseline must be published)"),
        ("ctx_baseline_published", "KILL (ctx baseline must be published)"),
        ("l_eff_alone_forbidden", "KILL (L_eff alone must be forbidden)"),
        ("live_ask_scored", "KILL (live ask scoreboard required)"),
    )
    for key, msg in flags:
        if not bool(bars.get(key)):
            return msg
    if str(bars.get("default_ask_intent_mismatch", "")) != "ABSTAIN":
        return "KILL (intent mismatch on default ask must be ABSTAIN)"
    if str(bars.get("default_ask_exact_gold", "")) != "LOOKUP":
        return "KILL (exact gold on default ask must be LOOKUP)"
    modes = bars.get("modes_required")
    if not isinstance(modes, list) or set(modes) != BA0_MODES:
        return "KILL (scoreboard modes_required incomplete)"
    return None


def _gate_debt_bars() -> str | None:
    bars = BA0_SCOREBOARD.get("bars")
    if not isinstance(bars, dict):
        return "KILL (scoreboard bars missing)"
    return _gate_debt_bar_nums(bars) or _gate_debt_bar_flags(bars)


def _gate_debt_metrics() -> str | None:
    metrics = BA0_SCOREBOARD.get("metrics")
    need_m = {
        "forever_false_hit",
        "az_hold_false_hit",
        "overrefuse_miss",
        "p50_wall_ms",
        "p99_wall_ms",
        "ctx_content_ok",
        "true_continue_ablated",
    }
    if not isinstance(metrics, list) or not need_m.issubset(set(metrics)):
        return "KILL (scoreboard metrics incomplete)"
    return None


def _gate_scoreboard() -> str | None:
    return _gate_debt_ids() or _gate_debt_bars() or _gate_debt_metrics()


def _az_questions() -> set[str]:
    rows = list(AZ0_HELDOUT_FP_ROWS) + list(AZ0_OVERREFUSE_ROWS)
    return {str(p.get("question", "")).strip() for p in rows}


def _gate_fh_rows() -> str | None:
    ids: set[str] = set()
    classes: set[str] = set()
    prior = _az_questions()
    for item in BA0_FOREVER_ROWS:
        tid = str(item.get("id", ""))
        if not tid.startswith("BA-FH-"):
            return f"KILL (bad forever id: {tid})"
        if tid in ids:
            return f"KILL (duplicate forever id: {tid})"
        ids.add(tid)
        q = str(item.get("question", "")).strip()
        if not q:
            return f"KILL (empty forever question: {tid})"
        if q in prior:
            return f"KILL (forever reuses AZ held-out: {tid})"
        if str(item.get("expect_mode", "")) != "ABSTAIN":
            return f"KILL (forever expect_mode must be ABSTAIN: {tid})"
        classes.add(str(item.get("class", "")))
    need = {"ops_pow", "ops_mod", "ops_max", "list_sort", "list_len"}
    if not need.issubset(classes):
        return "KILL (forever classes incomplete)"
    return None


def _gate_forever_flags(proto: Mapping[str, object]) -> str | None:
    flags = (
        ("held_out", "KILL (forever must be held-out)"),
        ("forever", "KILL (forever flag missing)"),
        ("bank_stuff_forbidden", "KILL (forever must forbid bank stuffing)"),
        ("paraphrase_required", "KILL (forever must require paraphrases)"),
        ("neq_az_heldout", "KILL (forever must ≠ AZ held-out)"),
        (
            "intent_mismatch_is_false_hit",
            "KILL (forever must mark mismatch as false-hit)",
        ),
        (
            "pack_pass_neq_forever",
            "KILL (forever must mark pack PASS ≠ forever)",
        ),
    )
    for key, msg in flags:
        if not bool(proto.get(key)):
            return msg
    return None


def _gate_forever_sizes(proto: Mapping[str, object]) -> str | None:
    rows = proto.get("rows")
    min_n = int(proto.get("min_n", 15))
    if min_n < 15:
        return "KILL (forever min_n must be ≥15)"
    if not isinstance(rows, list) or len(rows) < min_n:
        return f"KILL (forever must have ≥{min_n} rows)"
    if len(BA0_FOREVER_ROWS) < min_n:
        return "KILL (BA0_FOREVER_ROWS below min_n)"
    if str(proto.get("live_fp_id", "")) != "BA-FH-01":
        return "KILL (forever must pin live_fp_id=BA-FH-01)"
    req = proto.get("required_classes")
    if not isinstance(req, list) or len(req) < 5:
        return "KILL (forever required_classes incomplete)"
    return _gate_fh_rows()


def _gate_forever() -> str | None:
    proto = BA0_FOREVER_PROTOCOL
    return _gate_forever_flags(proto) or _gate_forever_sizes(proto)


def _gate_az_hold() -> str | None:
    proto = BA0_AZ_HOLD_PROTOCOL
    if int(proto.get("heldout_false_hit_max", 1)) != 0:
        return "KILL (AZ hold heldout_false_hit_max must be 0)"
    if int(proto.get("overrefuse_miss_max", 1)) != 0:
        return "KILL (AZ hold overrefuse_miss_max must be 0)"
    if not bool(proto.get("regression_hold")):
        return "KILL (AZ hold must require regression_hold)"
    if int(proto.get("heldout_n", 0)) < 12:
        return "KILL (AZ hold must cite ≥12 held-out rows)"
    if int(proto.get("overrefuse_n", 0)) < 3:
        return "KILL (AZ hold must cite ≥3 over-refuse rows)"
    req = proto.get("required_classes")
    need = {"ops_div", "ops_sub", "wrong_slot", "exact_clear"}
    if not isinstance(req, list) or not need.issubset(set(req)):
        return "KILL (AZ hold required_classes incomplete)"
    return None


def _gate_baselines() -> str | None:
    paths = BA0_SPEED_BASELINE.get("paths")
    if not isinstance(paths, dict) or set(paths) != BA0_MODES:
        return "KILL (speed baseline paths incomplete)"
    if not bool(BA0_SPEED_BASELINE.get("quality_regress_forbidden")):
        return "KILL (speed baseline must forbid quality regress)"
    if not bool(BA0_CTX_BASELINE.get("l_eff_alone_insufficient")):
        return "KILL (ctx baseline must mark L_eff alone insufficient)"
    if not bool(BA0_CTX_BASELINE.get("content_bars_required")):
        return "KILL (ctx baseline must require content bars)"
    return None


def _gate_gen_stance_core() -> str | None:
    stance = str(BA0_GEN_STANCE.get("stance", ""))
    allowed = BA0_GEN_STANCE.get("allowed_stances")
    if not isinstance(allowed, list):
        return "KILL (gen stance allowed_stances missing)"
    if stance not in allowed:
        return "KILL (gen stance must be M1|M2|M3|defer)"
    if stance != "defer":
        return "KILL (BA0 gen stance must be defer until real new method)"
    if str(BA0_GEN_STANCE.get("capcheck", "")) != "closed":
        return "KILL (BA0 CAPCHECK must stay closed)"
    names = (
        ("named_hyp", "H-NANOGEN11"),
        ("named_realgain", "H-REALGAIN"),
        ("named_fast", "H-FASTREAL"),
        ("named_ctx", "H-CTXREAL2"),
    )
    for key, want in names:
        if str(BA0_GEN_STANCE.get(key, "")) != want:
            return f"KILL (BA0 must name {want})"
    methods = BA0_GEN_STANCE.get("method_candidates")
    if not isinstance(methods, dict) or set(methods) != {"M1", "M2", "M3"}:
        return "KILL (gen stance method_candidates incomplete)"
    return None


def _gate_gen_stance_cites() -> str | None:
    cites = (
        ("nanogen11_rename_forbidden", "KILL (forbid NANOGEN11 rename)"),
        ("nanogen6_hold_cited", "KILL (cite NANOGEN6 HOLD)"),
        ("nanogen7_hold_cited", "KILL (cite NANOGEN7 HOLD)"),
        ("nanogen8_defer_cited", "KILL (cite NANOGEN8 DEFER)"),
        ("nanogen9_defer_cited", "KILL (cite NANOGEN9 DEFER)"),
        ("nanogen10_defer_cited", "KILL (cite NANOGEN10 DEFER)"),
    )
    for key, msg in cites:
        if not bool(BA0_GEN_STANCE.get(key)):
            return msg
    rat = str(BA0_GEN_STANCE.get("rationale", "")).lower()
    if "nanogen" not in rat or "defer" not in rat:
        return "KILL (gen stance rationale incomplete)"
    return None


def _gate_gen_stance() -> str | None:
    return _gate_gen_stance_core() or _gate_gen_stance_cites()


def _gate_gen_judge() -> str | None:
    judge = BA0_TRUE_GEN_JUDGE
    flags = (
        "span_fallback_neq_gen",
        "gold_substring_insufficient",
        "gibberish_tail_fails",
        "telemetry_neq_content_ok",
        "nanogen6_hold_archived",
        "nanogen7_tac_hold_archived",
        "nanogen8_defer_archived",
        "nanogen9_defer_archived",
        "nanogen10_defer_archived",
        "nanogen11_rename_forbidden",
    )
    for key in flags:
        if not bool(judge.get(key)):
            return f"KILL (true judge must set {key})"
    if "true_continue" not in str(judge.get("scoring", "")):
        return "KILL (true judge scoring must be true_continue only)"
    return None


def _gate_real_eval_flags() -> str | None:
    proto = BA0_REAL_EVAL_PROTOCOL
    flags = (
        ("live_ask_battery", "KILL (real-eval must require live ask battery)"),
        ("summary_only_forbidden", "KILL (real-eval must forbid summary-only)"),
        ("wall_ms_n_new_mandatory", "KILL (real-eval must require wall_ms/n_new)"),
        ("eval_eq_prod_ask", "KILL (real-eval must require eval=prod ask)"),
        ("intent_mismatch_is_false_hit", "KILL (real-eval must mark intent FP)"),
        (
            "exact_gold_abstain_is_miss",
            "KILL (real-eval must mark exact-gold ABSTAIN as miss)",
        ),
        ("gold_substring_neq_gen", "KILL (real-eval must reject gold-substring)"),
        ("gibberish_tail_fails", "KILL (real-eval must fail gibberish tail)"),
        ("span_fallback_neq_gen", "KILL (real-eval must reject span-fallback)"),
        ("pack_pass_neq_forever", "KILL (real-eval must mark pack≠forever)"),
        (
            "wall_ms_n_new_insufficient_for_decode_quality",
            "KILL (real-eval must mark wall_ms/n_new insufficient for DECODE)",
        ),
    )
    for key, msg in flags:
        if not bool(proto.get(key)):
            return msg
    return None


def _gate_real_eval() -> str | None:
    err = _gate_real_eval_flags()
    if err:
        return err
    claim = str(BA0_REAL_EVAL_PROTOCOL.get("gen_claim_rule", "")).lower()
    if "nanogen11" not in claim:
        return "KILL (real-eval gen_claim_rule incomplete)"
    if "rename" not in claim:
        return "KILL (real-eval must forbid NANOGEN11 rename)"
    labels = BA0_REAL_EVAL_PROTOCOL.get("score_labels")
    need = {"OK", "FP", "MISS", "ABSTAIN-OK"}
    if not isinstance(labels, list) or not need.issubset(set(labels)):
        return "KILL (real-eval score_labels incomplete)"
    return None


def _scan_battery_row(
    item: Mapping[str, str], ids: set[str]
) -> tuple[str | None, str, str]:
    tid = str(item.get("id", ""))
    if not tid.startswith("BA-ASK-"):
        return f"KILL (bad battery id: {tid})", "", ""
    if tid in ids:
        return f"KILL (duplicate battery id: {tid})", "", ""
    q = str(item.get("question", ""))
    if tid != "BA-ASK-06" and not q.strip():
        return f"KILL (empty battery question: {tid})", "", ""
    mode = str(item.get("expect_mode", ""))
    if mode not in BA0_MODES:
        return f"KILL (bad expect_mode: {tid})", "", ""
    return None, mode, str(item.get("kind", ""))


def _gate_battery(rows: Sequence[Mapping[str, str]]) -> str | None:
    if len(rows) < 4:
        return "KILL (ask battery must cover ≥4 live rows)"
    ids: set[str] = set()
    modes_seen: set[str] = set()
    kinds: set[str] = set()
    for item in rows:
        err, mode, kind = _scan_battery_row(item, ids)
        if err:
            return err
        ids.add(str(item.get("id", "")))
        modes_seen.add(mode)
        kinds.add(kind)
    if modes_seen != BA0_MODES:
        return f"KILL (ask battery modes incomplete: {sorted(modes_seen)})"
    need_kinds = {
        "near_miss",
        "forever_intent_fp",
        "forever_list_fp",
        "overrefuse_gold",
        "az_hold_div",
        "labeled_peak",
        "junk_trap",
        "decode_content",
    }
    if not need_kinds.issubset(kinds):
        return "KILL (ask battery must cover BA scoreboard kinds)"
    return None


def _gate_safe_anti_fp() -> str | None:
    if "≠" not in BA0_SAFE_NOTE and "!=" not in BA0_SAFE_NOTE:
        return "KILL (SAFE≠quality note missing)"
    if "LOOKUP" not in BA0_ANTI_FP:
        return "KILL (anti-FP charter incomplete)"
    if "eval path = prod" not in BA0_ANTI_FP.lower():
        return "KILL (anti-FP must require eval=prod ask)"
    if "forever" not in BA0_ANTI_FP.lower() and "BA-FOREVER" not in BA0_ANTI_FP:
        if "pow" not in BA0_ANTI_FP.lower():
            return "KILL (anti-FP must mark forever intent FP)"
    if "NANOGEN11" not in BA0_ANTI_FP and "nanogen11" not in BA0_ANTI_FP.lower():
        return "KILL (anti-FP must forbid NANOGEN11 rename)"
    return None


def _gate_north_ship() -> str | None:
    if "≤5M" not in BA0_NORTH_STAR:
        return "KILL (north-star charter incomplete)"
    if "defer" not in BA0_NORTH_STAR.lower():
        return "KILL (north-star must allow HOLD/defer)"
    if "gibberish-tail" not in BA0_SHIP_LOCK:
        return "KILL (ship lock must keep STRICT gibberish-tail claim)"
    if "TAC unlocked" not in BA0_SHIP_LOCK and "not TAC" not in BA0_SHIP_LOCK:
        return "KILL (ship lock must state not TAC unlocked)"
    return None


def _gate_notes() -> str | None:
    return _gate_safe_anti_fp() or _gate_north_ship()


def _gate_charters() -> str | None:
    return (
        _gate_modes()
        or _gate_cited_az()
        or _gate_scoreboard()
        or _gate_forever()
        or _gate_az_hold()
        or _gate_baselines()
        or _gate_gen_stance()
        or _gate_gen_judge()
        or _gate_real_eval()
        or _gate_notes()
    )


def decide_ba0_session(
    *,
    trials_dir_ready: bool,
    anti_fp_signed: bool,
    battery: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN BA-FOREVER/AZ-hold/scoreboard/gen-defer/real-eval charters + trials
    WHEN applying BA0 SESSION gate
    THEN PROMOTE iff AZ locks cited, stance=defer, battery covers 4 modes,
         trials ready, anti-FP signed.
    """
    rows = list(battery) if battery is not None else list(BA0_ASK_BATTERY)
    err = _gate_charters() or _gate_battery(rows)
    if err:
        return err
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-ba/trials/ not ready)"
    return f"PROMOTE ({BA0_ID}: {BA0_THESIS})"
