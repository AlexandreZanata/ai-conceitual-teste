"""Wave BB0 SESSION: freeze BB-FOREVER · BA/AZ hold · scoreboard · gen-defer."""

from __future__ import annotations

from typing import Mapping, Sequence

from au_session_ops import AU0_MODES, map_au_product_mode
from az_session_ops import AZ0_HELDOUT_FP_ROWS, AZ0_OVERREFUSE_ROWS
from ba_session_ops import BA0_FOREVER_ROWS, BA0_SHIP_LOCK

__all__ = [
    "BB0_ID",
    "BB0_THESIS",
    "BB0_MODES",
    "BB0_LATENCY_PATHS",
    "BB0_CITED_BA_LOCKS",
    "BB0_SCOREBOARD",
    "BB0_FOREVER_PROTOCOL",
    "BB0_FOREVER_ROWS",
    "BB0_BA_HOLD_PROTOCOL",
    "BB0_AZ_HOLD_PROTOCOL",
    "BB0_CTX_BASELINE",
    "BB0_SPEED_BASELINE",
    "BB0_GEN_STANCE",
    "BB0_TRUE_GEN_JUDGE",
    "BB0_REAL_EVAL_PROTOCOL",
    "BB0_ASK_BATTERY",
    "BB0_SAFE_NOTE",
    "BB0_ANTI_FP",
    "BB0_NORTH_STAR",
    "BB0_SHIP_LOCK",
    "map_bb_product_mode",
    "decide_bb0_session",
]

BB0_ID = "BB0-SESSION"
BB0_THESIS = (
    "Wave BB OPEN: freeze BB-FOREVER (min·xor·absdiff·and·or + paraphrases) · "
    "BA-FOREVER hold (pow·mod·max·sort·len FH0) · AZ hold (div·sub·BIP · "
    "a.clear()) · §1 anti-FP scoreboard · ctx/speed baselines from BA · "
    "gen method stance = defer (M1|M2|M3|defer; H-NANOGEN12; not "
    "NANOGEN11+rename) · real-eval; next BB1 H-INTENTGEN "
    "(not CTX/SMART/FAST clone)"
)

BB0_MODES: frozenset[str] = AU0_MODES
BB0_LATENCY_PATHS: tuple[str, ...] = (
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
)

BB0_CITED_BA_LOCKS: frozenset[str] = frozenset(
    {
        "H-REALGAIN",
        "H-FASTREAL",
        "H-CTXREAL2",
        "H-NANOGEN11",
        "BA-REAL-EVAL",
        "BA-FREEZE",
    }
)

BB0_SHIP_LOCK = BA0_SHIP_LOCK

BB0_NORTH_STAR = (
    "Nano generative / mini-AGI-inspired ≤5M: compositional anti-FP "
    "(BB-FOREVER FH 0 + BA-FOREVER hold + AZ hold + live ask) + "
    "measurable context & speed on prod path + one honest generative "
    "method (M1|M2|M3) — else HOLD/DEFER; never pack theater · never "
    "LOOKUP-as-IQ · never NANOGEN12 = NANOGEN11+rename"
)

BB0_GEN_STANCE: Mapping[str, object] = {
    "stage": "BB0 freezes stance; BB4 H-NANOGEN12 applies or HOLD/DEFER",
    "stance": "defer",
    "allowed_stances": ["M1", "M2", "M3", "defer"],
    "method_candidates": {
        "M1": "teacher distill continue + anti-copy-gold loss",
        "M2": "student draft + bank/teacher rejector (hybrid)",
        "M3": "named CAPCHECK (raise params with ablations)",
    },
    "capcheck": "closed",
    "named_hyp": "H-NANOGEN12",
    "named_intentgen": "H-INTENTGEN",
    "named_fast": "H-FASTHOLD",
    "named_ctx": "H-CTXHOLD",
    "nanogen6_hold_cited": True,
    "nanogen7_hold_cited": True,
    "nanogen8_defer_cited": True,
    "nanogen9_defer_cited": True,
    "nanogen10_defer_cited": True,
    "nanogen11_defer_cited": True,
    "nanogen12_rename_forbidden": True,
    "true_continue_required_for_promote": True,
    "span_fallback_neq_gen": True,
    "rationale": (
        "No real new train/data/arch method ready at BB0; "
        "NANOGEN6·7 HOLD · NANOGEN8·9·10·11 DEFER stand; CAPCHECK stays "
        "closed; prefer compositional anti-FP (H-INTENTGEN) + ctx/speed "
        "hold + honest paper over vanity NANOGEN12 clone; BB4 PROMOTE "
        "only under true_continue else HOLD/DEFER"
    ),
    "bb4_gate": "true_continue → PROMOTE else HOLD/DEFER",
}

BB0_SAFE_NOTE = (
    "SAFE / ADVSAFE false-hit score ≠ answer quality; "
    "SAFE = no wrong gold only (anti-FP); "
    "pack FH 0 ≠ forever held-out generalization; "
    "intent-mismatch LOOKUP = false-hit (min/xor/absdiff/and/or); "
    "BA-FOREVER PASS with BB-FOREVER FP = PACK THEATER; "
    "exact-gold ABSTAIN = product miss; "
    "gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE"
)

BB0_ANTI_FP = (
    "LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; "
    "never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; "
    "intent-mismatch LOOKUP = false-hit (BB-FOREVER min/xor/absdiff/"
    "and/or → add); exact-gold ABSTAIN = miss (a.clear()); "
    "BA-FOREVER pow·mod·max·sort·len FH must stay 0; "
    "AZ hold div·sub·BIP FH must stay 0; "
    "BA PASS with BB FP = PACK THEATER; "
    "truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; "
    "eval path = prod ask path; "
    "generative bar = BB4 only under real new method; "
    "no NANOGEN12 = NANOGEN11+rename; no CTX/SMART/FAST clone; "
    "no invent Wave BC without lab-book reopen; "
    "prefer HOLD/defer over fake PROMOTE"
)

BB0_TRUE_GEN_JUDGE: Mapping[str, object] = {
    "stage": "BB4 H-NANOGEN12 applies only if stance≠defer or new method; "
    "BB0 freezes judge law",
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
    "nanogen11_defer_archived": True,
    "nanogen12_rename_forbidden": True,
    "scoring": "short_answer_f1_or_hitl_true_continue_only",
    "promote_bar": "true_continue else HOLD/DEFER",
}

# BA FASTREAL republished latency (speed baseline for BB2).
BB0_SPEED_BASELINE: Mapping[str, object] = {
    "source": "H-FASTREAL / formal-hfastreal-ba2.md",
    "path": "nano:z:ask prod path",
    "unit": "wall_ms",
    "paths": {
        "LOOKUP": {"p50": 0.0, "p99": 0.0},
        "PEAK": {
            "p50": 0.00948000160860829,
            "p99": 0.016213351700571366,
        },
        "DECODE": {
            "p50": 12.682843498623697,
            "p99": 17.01244352661888,
        },
        "ABSTAIN": {
            "p50": 95.4394950022106,
            "p99": 125.30305242056787,
        },
    },
    "quality_regress_forbidden": True,
    "warm_cache_vanity_forbidden": True,
    "bb2_gate": "speed PROMOTE only if §1 anti-FP bars hold (incl BB-FOREVER)",
}

# Context baseline: content bars required (L_eff alone ≠ win).
BB0_CTX_BASELINE: Mapping[str, object] = {
    "source": "H-CTXREAL2 / formal-hctxreal2-ctxreal2.md (content-first)",
    "l_eff_alone_insufficient": True,
    "content_bars_required": True,
    "modes_visible_required": True,
    "long_cite_howto_pack": True,
    "honest_abstain_when_missing": True,
    "bb3_gate": (
        "H-CTXHOLD PROMOTE only if content_ok + no new intent FP "
        "(incl BB-FOREVER) + p50/p99 published + modes visible"
    ),
}

BB0_SCOREBOARD: Mapping[str, object] = {
    "stage": "BB1 H-INTENTGEN closes bars; BB0 freezes §1 scoreboard",
    "cite_ba_locks": sorted(BB0_CITED_BA_LOCKS),
    "accept_artifact": (
        "AF+AQ+AS trust + STRICT ablated DECODE (BA H-REALGAIN·H-FASTREAL·"
        "H-CTXREAL2); NANOGEN6·7 HOLD · NANOGEN8·9·10·11 DEFER; "
        "not TAC unlocked"
    ),
    "debts": [
        {
            "id": "bb_forever_false_hit_zero",
            "evidence": (
                "Live FP: min2/xor2/absdiff→add LOOKUP (binop ≠ add family)"
            ),
            "fix": "BB-FOREVER intent FH 0 via gate (not bank-stuff)",
            "bar": "bb_forever_false_hit_max=0",
        },
        {
            "id": "ba_forever_hold_zero",
            "evidence": "BA pow·mod·max·sort·len FH 0 must hold",
            "fix": "BA-FOREVER regression hold",
            "bar": "ba_forever_false_hit_max=0",
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
            "fix": "live nano:z:ask on BB+BA+AZ + novel probes",
            "bar": "live_ask_scored True",
        },
        {
            "id": "speed_baseline_publish",
            "evidence": "BA FASTREAL p50/p99 republished at BB0",
            "fix": "BB2 measures prod wall without FP regress",
            "bar": "speed_baseline_published True",
        },
        {
            "id": "ctx_baseline_publish",
            "evidence": "content bars required; L_eff alone forbidden",
            "fix": "BB3 measures usable long/cite/howto",
            "bar": "ctx_baseline_published True",
        },
        {
            "id": "mode_ui_always",
            "evidence": "modes+content PROMOTE archive",
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
            "evidence": (
                "NANOGEN6·7 HOLD · NANOGEN8·9·10·11 DEFER; no new method"
            ),
            "fix": "stance defer · CAPCHECK closed · no NANOGEN12 rename",
            "bar": "gen_stance=defer; nanogen12_rename_forbidden",
        },
        {
            "id": "paraphrase_eval_rule",
            "evidence": "BB-FOREVER seeds + held-out paraphrases at eval",
            "fix": "never bank-stuff exact seed strings",
            "bar": "paraphrase_required True; bank_stuff_forbidden",
        },
    ],
    "metrics": [
        "bb_forever_false_hit",
        "ba_forever_false_hit",
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
        "bb_forever_false_hit_max": 0,
        "ba_forever_false_hit_max": 0,
        "az_hold_false_hit_max": 0,
        "overrefuse_miss_max": 0,
        "bb_forever_min_n": 15,
        "bb_forever_classes_min": 5,
        "modes_required": list(BB0_LATENCY_PATHS),
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
        "ba_pass_neq_bb_forever": True,
        "bank_stuff_forbidden": True,
        "paraphrase_required": True,
        "regression_hold": True,
        "speed_baseline_published": True,
        "ctx_baseline_published": True,
        "live_ask_scored": True,
    },
    "baselines": {
        "ba_forever_fh": 0,
        "az_heldout_fh": 0,
        "az_overrefuse_miss": 0,
        "fastreal_latency": dict(BB0_SPEED_BASELINE["paths"]),  # type: ignore[arg-type]
        "ctxreal2_content": "PROMOTE",
        "nanogen6_decision": "HOLD",
        "nanogen7_decision": "HOLD",
        "nanogen8_decision": "DEFER",
        "nanogen9_decision": "DEFER",
        "nanogen10_decision": "DEFER",
        "nanogen11_decision": "DEFER",
        "ba_real_eval_battery": "10/10",
        "live_audit_bb_forever_fp": "min2/xor2/absdiff → add FP observed",
        "forever_classes": [
            "ops_min",
            "ops_xor",
            "ops_absdiff",
            "ops_and",
            "ops_or",
        ],
        "ship_lock": BB0_SHIP_LOCK,
    },
    "runners": [
        "nano:z:ask",
        "nano:realgain",
        "nano:ba:fastreal",
        "nano:ba:ctxreal2",
        "nano:nanogen11",
        "nano:advsafe",
        "nano:metrics",
        "nano:askabstain",
    ],
    "no_reopen_unless_fail": [
        "H-REALGAIN",
        "H-FASTREAL",
        "H-CTXREAL2",
        "H-PRODGEN",
        "H-SHIPAZ",
        "H-ADVSAFE",
    ],
    "complete_kb_claim_forbidden": True,
}

# Forever held-out residual FP (binop ≠ add; ≠ BA pow/mod/max/sort/len).
BB0_FOREVER_ROWS: tuple[dict[str, str], ...] = (
    {
        "id": "BB-FH-01",
        "class": "ops_min",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named min2 that returns "
            "the smaller of two integers a and b."
        ),
    },
    {
        "id": "BB-FH-02",
        "class": "ops_min",
        "expect_mode": "ABSTAIN",
        "question": (
            "I need min2(a, b) in Python — smaller of two ints, "
            "not add them."
        ),
    },
    {
        "id": "BB-FH-03",
        "class": "ops_min",
        "expect_mode": "ABSTAIN",
        "question": (
            "Show min2 for integers a and b returning the lesser value. "
            "Do not return a+b."
        ),
    },
    {
        "id": "BB-FH-04",
        "class": "ops_xor",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named xor2 that returns "
            "the bitwise XOR of two integers a and b."
        ),
    },
    {
        "id": "BB-FH-05",
        "class": "ops_xor",
        "expect_mode": "ABSTAIN",
        "question": (
            "I need xor2(a, b) in Python — bitwise xor of two ints, "
            "not add them."
        ),
    },
    {
        "id": "BB-FH-06",
        "class": "ops_xor",
        "expect_mode": "ABSTAIN",
        "question": (
            "Show xor2 for integers a and b returning a ^ b. "
            "Do not return a+b."
        ),
    },
    {
        "id": "BB-FH-07",
        "class": "ops_absdiff",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named absdiff that returns "
            "the absolute difference of two integers a and b."
        ),
    },
    {
        "id": "BB-FH-08",
        "class": "ops_absdiff",
        "expect_mode": "ABSTAIN",
        "question": (
            "I need absdiff(a, b) in Python — |a-b| of two ints, "
            "not add them."
        ),
    },
    {
        "id": "BB-FH-09",
        "class": "ops_absdiff",
        "expect_mode": "ABSTAIN",
        "question": (
            "Show absdiff for integers a and b returning abs(a-b). "
            "Do not return a+b."
        ),
    },
    {
        "id": "BB-FH-10",
        "class": "ops_and",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named and2 that returns "
            "the bitwise AND of two integers a and b."
        ),
    },
    {
        "id": "BB-FH-11",
        "class": "ops_and",
        "expect_mode": "ABSTAIN",
        "question": (
            "I need and2(a, b) in Python — bitwise and of two ints, "
            "not add them."
        ),
    },
    {
        "id": "BB-FH-12",
        "class": "ops_and",
        "expect_mode": "ABSTAIN",
        "question": (
            "Show and2 for integers a and b returning a & b. "
            "Do not return a+b."
        ),
    },
    {
        "id": "BB-FH-13",
        "class": "ops_or",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named or2 that returns "
            "the bitwise OR of two integers a and b."
        ),
    },
    {
        "id": "BB-FH-14",
        "class": "ops_or",
        "expect_mode": "ABSTAIN",
        "question": (
            "I need or2(a, b) in Python — bitwise or of two ints, "
            "not add them."
        ),
    },
    {
        "id": "BB-FH-15",
        "class": "ops_or",
        "expect_mode": "ABSTAIN",
        "question": (
            "Show or2 for integers a and b returning a | b. "
            "Do not return a+b."
        ),
    },
)

BB0_FOREVER_PROTOCOL: Mapping[str, object] = {
    "stage": "BB1 H-INTENTGEN scores; BB0 freezes protocol",
    "held_out": True,
    "forever": True,
    "bank_stuff_forbidden": True,
    "paraphrase_required": True,
    "neq_ba_forever": True,
    "neq_az_heldout": True,
    "intent_mismatch_is_false_hit": True,
    "source": (
        "live forever FP (min≠add · xor≠add · absdiff≠add · "
        "and≠add · or≠add)"
    ),
    "min_n": 15,
    "classes_min": 5,
    "required_classes": [
        "ops_min",
        "ops_xor",
        "ops_absdiff",
        "ops_and",
        "ops_or",
    ],
    "scoring": "false-hit rate on default ask path (mismatch → ABSTAIN)",
    "path": "nano:z:ask --wrap --semwrap",
    "pack_pass_neq_forever": True,
    "ba_pass_neq_bb_forever": True,
    "live_fp_id": "BB-FH-01",
    "rows": list(BB0_FOREVER_ROWS),
}

BB0_BA_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BB1 must hold BA bars; BB0 freezes regression pack",
    "source": "BA0_FOREVER_ROWS",
    "heldout_n": len(BA0_FOREVER_ROWS),
    "forever_false_hit_max": 0,
    "required_classes": [
        "ops_pow",
        "ops_mod",
        "ops_max",
        "list_sort",
        "list_len",
    ],
    "path": "nano:z:ask --wrap --semwrap",
    "regression_hold": True,
}

BB0_AZ_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BB1 must hold AZ bars; BB0 freezes regression pack",
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

BB0_REAL_EVAL_PROTOCOL: Mapping[str, object] = {
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
    "ba_pass_neq_bb_forever": True,
    "eval_eq_prod_ask": True,
    "answer_usability_scored": True,
    "score_labels": ["OK", "FP", "MISS", "ABSTAIN-OK"],
    "gen_claim_rule": (
        "only if BB4 H-NANOGEN12 PROMOTE (true_continue; "
        "real new method M1|M2|M3; never NANOGEN11+rename; "
        "span-fallback ≠ gen)"
    ),
    "mini_agi_rule": (
        "forbidden while gen stance defer or NANOGEN12 HOLD/DEFER"
    ),
    "stage": "BB5 BB-REAL-EVAL scores; BB0 freezes protocol",
}

BB0_ASK_BATTERY: tuple[dict[str, str], ...] = (
    {
        "id": "BB-ASK-01",
        "kind": "known_lookup",
        "expect_mode": "LOOKUP",
        "question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
    },
    {
        "id": "BB-ASK-02",
        "kind": "ood_abstain",
        "expect_mode": "ABSTAIN",
        "question": "Which chef won the 2019 World Cup of Baking?",
    },
    {
        "id": "BB-ASK-03",
        "kind": "near_miss",
        "expect_mode": "ABSTAIN",
        "question": (
            "BIP-39 entropy formula is CS = ENT / 32 — confirm for "
            "SegWit witness discount?"
        ),
    },
    {
        "id": "BB-ASK-04",
        "kind": "labeled_peak",
        "expect_mode": "PEAK",
        "question": (
            "From the curated Rust book intro, extract one sentence "
            "on ownership (label PEAK, not open chat)."
        ),
    },
    {
        "id": "BB-ASK-05",
        "kind": "decode_content",
        "expect_mode": "DECODE",
        "question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
    },
    {
        "id": "BB-ASK-06",
        "kind": "junk_trap",
        "expect_mode": "ABSTAIN",
        "question": ".",
    },
    {
        "id": "BB-ASK-07",
        "kind": "bb_forever_intent_fp",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named min2 that returns "
            "the smaller of two integers a and b."
        ),
    },
    {
        "id": "BB-ASK-08",
        "kind": "overrefuse_gold",
        "expect_mode": "LOOKUP",
        "question": "Remove all items from list `a` — one method call.",
    },
    {
        "id": "BB-ASK-09",
        "kind": "az_hold_div",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named div that returns "
            "the quotient of two integers a and b."
        ),
    },
    {
        "id": "BB-ASK-10",
        "kind": "ba_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named pow2 that returns "
            "a raised to the power of b for two integers."
        ),
    },
    {
        "id": "BB-ASK-11",
        "kind": "bb_forever_xor_fp",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named xor2 that returns "
            "the bitwise XOR of two integers a and b."
        ),
    },
    {
        "id": "BB-ASK-12",
        "kind": "bb_forever_absdiff_fp",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named absdiff that returns "
            "the absolute difference of two integers a and b."
        ),
    },
)


def map_bb_product_mode(raw_mode: str) -> str:
    """
    GIVEN raw telemetry mode string
    WHEN applying BB0 mode charter (inherits AU0 aliases)
    THEN return LOOKUP | PEAK | DECODE | ABSTAIN | UNKNOWN.
    """
    return map_au_product_mode(raw_mode)


def _gate_modes() -> str | None:
    if set(BB0_LATENCY_PATHS) != BB0_MODES:
        return "KILL (latency paths ≠ mode charter)"
    if "ABSTAIN" not in BB0_MODES:
        return "KILL (ABSTAIN missing from modes)"
    return None


def _gate_cited_ba() -> str | None:
    cited = BB0_SCOREBOARD.get("cite_ba_locks")
    if not isinstance(cited, list):
        return "KILL (scoreboard must cite BA locks)"
    if set(cited) != BB0_CITED_BA_LOCKS:
        return "KILL (scoreboard BA lock citations incomplete)"
    return None


def _gate_debt_ids() -> str | None:
    debts = BB0_SCOREBOARD.get("debts")
    if not isinstance(debts, list) or len(debts) < 11:
        return "KILL (scoreboard must list ≥11 post-BA debts)"
    ids = {str(d.get("id", "")) for d in debts if isinstance(d, dict)}
    need = {
        "bb_forever_false_hit_zero",
        "ba_forever_hold_zero",
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
    if int(bars.get("bb_forever_false_hit_max", 1)) != 0:
        return "KILL (bb_forever_false_hit_max must be 0)"
    if int(bars.get("ba_forever_false_hit_max", 1)) != 0:
        return "KILL (ba_forever_false_hit_max must be 0)"
    if int(bars.get("az_hold_false_hit_max", 1)) != 0:
        return "KILL (az_hold_false_hit_max must be 0)"
    if int(bars.get("overrefuse_miss_max", 1)) != 0:
        return "KILL (overrefuse_miss_max must be 0)"
    if int(bars.get("bb_forever_min_n", 0)) < 15:
        return "KILL (bb_forever_min_n must be ≥15)"
    if int(bars.get("bb_forever_classes_min", 0)) < 5:
        return "KILL (bb_forever_classes_min must be ≥5)"
    return None


def _gate_debt_bar_flags(bars: Mapping[str, object]) -> str | None:
    flags = (
        ("decode_gibberish_neq_content_ok", "KILL (DECODE gibberish≠content_ok)"),
        ("eval_eq_prod_ask", "KILL (eval path must equal prod ask path)"),
        ("pack_pass_neq_forever", "KILL (pack PASS ≠ forever bar missing)"),
        ("ba_pass_neq_bb_forever", "KILL (BA PASS ≠ BB forever bar missing)"),
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
    if not isinstance(modes, list) or set(modes) != BB0_MODES:
        return "KILL (scoreboard modes_required incomplete)"
    return None


def _gate_debt_bars() -> str | None:
    bars = BB0_SCOREBOARD.get("bars")
    if not isinstance(bars, dict):
        return "KILL (scoreboard bars missing)"
    return _gate_debt_bar_nums(bars) or _gate_debt_bar_flags(bars)


def _gate_debt_metrics() -> str | None:
    metrics = BB0_SCOREBOARD.get("metrics")
    need_m = {
        "bb_forever_false_hit",
        "ba_forever_false_hit",
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


def _prior_questions() -> set[str]:
    rows = (
        list(BA0_FOREVER_ROWS)
        + list(AZ0_HELDOUT_FP_ROWS)
        + list(AZ0_OVERREFUSE_ROWS)
    )
    return {str(p.get("question", "")).strip() for p in rows}


def _gate_fh_rows() -> str | None:
    ids: set[str] = set()
    classes: set[str] = set()
    prior = _prior_questions()
    for item in BB0_FOREVER_ROWS:
        tid = str(item.get("id", ""))
        if not tid.startswith("BB-FH-"):
            return f"KILL (bad forever id: {tid})"
        if tid in ids:
            return f"KILL (duplicate forever id: {tid})"
        ids.add(tid)
        q = str(item.get("question", "")).strip()
        if not q:
            return f"KILL (empty forever question: {tid})"
        if q in prior:
            return f"KILL (forever reuses BA/AZ held-out: {tid})"
        if str(item.get("expect_mode", "")) != "ABSTAIN":
            return f"KILL (forever expect_mode must be ABSTAIN: {tid})"
        classes.add(str(item.get("class", "")))
    need = {"ops_min", "ops_xor", "ops_absdiff", "ops_and", "ops_or"}
    if not need.issubset(classes):
        return "KILL (forever classes incomplete)"
    return None


def _gate_forever_flags(proto: Mapping[str, object]) -> str | None:
    flags = (
        ("held_out", "KILL (forever must be held-out)"),
        ("forever", "KILL (forever flag missing)"),
        ("bank_stuff_forbidden", "KILL (forever must forbid bank stuffing)"),
        ("paraphrase_required", "KILL (forever must require paraphrases)"),
        ("neq_ba_forever", "KILL (forever must ≠ BA-FOREVER)"),
        ("neq_az_heldout", "KILL (forever must ≠ AZ held-out)"),
        (
            "intent_mismatch_is_false_hit",
            "KILL (forever must mark mismatch as false-hit)",
        ),
        (
            "pack_pass_neq_forever",
            "KILL (forever must mark pack PASS ≠ forever)",
        ),
        (
            "ba_pass_neq_bb_forever",
            "KILL (forever must mark BA PASS ≠ BB forever)",
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
    if len(BB0_FOREVER_ROWS) < min_n:
        return "KILL (BB0_FOREVER_ROWS below min_n)"
    if str(proto.get("live_fp_id", "")) != "BB-FH-01":
        return "KILL (forever must pin live_fp_id=BB-FH-01)"
    req = proto.get("required_classes")
    if not isinstance(req, list) or len(req) < 5:
        return "KILL (forever required_classes incomplete)"
    return _gate_fh_rows()


def _gate_forever() -> str | None:
    proto = BB0_FOREVER_PROTOCOL
    return _gate_forever_flags(proto) or _gate_forever_sizes(proto)


def _gate_ba_hold() -> str | None:
    proto = BB0_BA_HOLD_PROTOCOL
    if int(proto.get("forever_false_hit_max", 1)) != 0:
        return "KILL (BA hold forever_false_hit_max must be 0)"
    if not bool(proto.get("regression_hold")):
        return "KILL (BA hold must require regression_hold)"
    if int(proto.get("heldout_n", 0)) < 15:
        return "KILL (BA hold must cite ≥15 forever rows)"
    req = proto.get("required_classes")
    need = {"ops_pow", "ops_mod", "ops_max", "list_sort", "list_len"}
    if not isinstance(req, list) or not need.issubset(set(req)):
        return "KILL (BA hold required_classes incomplete)"
    return None


def _gate_az_hold() -> str | None:
    proto = BB0_AZ_HOLD_PROTOCOL
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
    paths = BB0_SPEED_BASELINE.get("paths")
    if not isinstance(paths, dict) or set(paths) != BB0_MODES:
        return "KILL (speed baseline paths incomplete)"
    if not bool(BB0_SPEED_BASELINE.get("quality_regress_forbidden")):
        return "KILL (speed baseline must forbid quality regress)"
    if not bool(BB0_CTX_BASELINE.get("l_eff_alone_insufficient")):
        return "KILL (ctx baseline must mark L_eff alone insufficient)"
    if not bool(BB0_CTX_BASELINE.get("content_bars_required")):
        return "KILL (ctx baseline must require content bars)"
    return None


def _gate_gen_stance_core() -> str | None:
    stance = str(BB0_GEN_STANCE.get("stance", ""))
    allowed = BB0_GEN_STANCE.get("allowed_stances")
    if not isinstance(allowed, list):
        return "KILL (gen stance allowed_stances missing)"
    if stance not in allowed:
        return "KILL (gen stance must be M1|M2|M3|defer)"
    if stance != "defer":
        return "KILL (BB0 gen stance must be defer until real new method)"
    if str(BB0_GEN_STANCE.get("capcheck", "")) != "closed":
        return "KILL (BB0 CAPCHECK must stay closed)"
    names = (
        ("named_hyp", "H-NANOGEN12"),
        ("named_intentgen", "H-INTENTGEN"),
        ("named_fast", "H-FASTHOLD"),
        ("named_ctx", "H-CTXHOLD"),
    )
    for key, want in names:
        if str(BB0_GEN_STANCE.get(key, "")) != want:
            return f"KILL (BB0 must name {want})"
    methods = BB0_GEN_STANCE.get("method_candidates")
    if not isinstance(methods, dict) or set(methods) != {"M1", "M2", "M3"}:
        return "KILL (gen stance method_candidates incomplete)"
    return None


def _gate_gen_stance_cites() -> str | None:
    cites = (
        ("nanogen12_rename_forbidden", "KILL (forbid NANOGEN12 rename)"),
        ("nanogen6_hold_cited", "KILL (cite NANOGEN6 HOLD)"),
        ("nanogen7_hold_cited", "KILL (cite NANOGEN7 HOLD)"),
        ("nanogen8_defer_cited", "KILL (cite NANOGEN8 DEFER)"),
        ("nanogen9_defer_cited", "KILL (cite NANOGEN9 DEFER)"),
        ("nanogen10_defer_cited", "KILL (cite NANOGEN10 DEFER)"),
        ("nanogen11_defer_cited", "KILL (cite NANOGEN11 DEFER)"),
    )
    for key, msg in cites:
        if not bool(BB0_GEN_STANCE.get(key)):
            return msg
    rat = str(BB0_GEN_STANCE.get("rationale", "")).lower()
    if "nanogen" not in rat or "defer" not in rat:
        return "KILL (gen stance rationale incomplete)"
    return None


def _gate_gen_stance() -> str | None:
    return _gate_gen_stance_core() or _gate_gen_stance_cites()


def _gate_gen_judge() -> str | None:
    judge = BB0_TRUE_GEN_JUDGE
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
        "nanogen11_defer_archived",
        "nanogen12_rename_forbidden",
    )
    for key in flags:
        if not bool(judge.get(key)):
            return f"KILL (true judge must set {key})"
    if "true_continue" not in str(judge.get("scoring", "")):
        return "KILL (true judge scoring must be true_continue only)"
    return None


def _gate_real_eval_flags() -> str | None:
    proto = BB0_REAL_EVAL_PROTOCOL
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
            "ba_pass_neq_bb_forever",
            "KILL (real-eval must mark BA PASS ≠ BB forever)",
        ),
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
    claim = str(BB0_REAL_EVAL_PROTOCOL.get("gen_claim_rule", "")).lower()
    if "nanogen12" not in claim:
        return "KILL (real-eval gen_claim_rule incomplete)"
    if "rename" not in claim:
        return "KILL (real-eval must forbid NANOGEN12 rename)"
    labels = BB0_REAL_EVAL_PROTOCOL.get("score_labels")
    need = {"OK", "FP", "MISS", "ABSTAIN-OK"}
    if not isinstance(labels, list) or not need.issubset(set(labels)):
        return "KILL (real-eval score_labels incomplete)"
    return None


def _scan_battery_row(
    item: Mapping[str, str], ids: set[str]
) -> tuple[str | None, str, str]:
    tid = str(item.get("id", ""))
    if not tid.startswith("BB-ASK-"):
        return f"KILL (bad battery id: {tid})", "", ""
    if tid in ids:
        return f"KILL (duplicate battery id: {tid})", "", ""
    q = str(item.get("question", ""))
    if tid != "BB-ASK-06" and not q.strip():
        return f"KILL (empty battery question: {tid})", "", ""
    mode = str(item.get("expect_mode", ""))
    if mode not in BB0_MODES:
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
    if modes_seen != BB0_MODES:
        return f"KILL (ask battery modes incomplete: {sorted(modes_seen)})"
    need_kinds = {
        "near_miss",
        "bb_forever_intent_fp",
        "bb_forever_xor_fp",
        "bb_forever_absdiff_fp",
        "ba_forever_hold",
        "overrefuse_gold",
        "az_hold_div",
        "labeled_peak",
        "junk_trap",
        "decode_content",
    }
    if not need_kinds.issubset(kinds):
        return "KILL (ask battery must cover BB scoreboard kinds)"
    return None


def _gate_safe_anti_fp() -> str | None:
    if "≠" not in BB0_SAFE_NOTE and "!=" not in BB0_SAFE_NOTE:
        return "KILL (SAFE≠quality note missing)"
    if "LOOKUP" not in BB0_ANTI_FP:
        return "KILL (anti-FP charter incomplete)"
    if "eval path = prod" not in BB0_ANTI_FP.lower():
        return "KILL (anti-FP must require eval=prod ask)"
    if "min" not in BB0_ANTI_FP.lower() and "BB-FOREVER" not in BB0_ANTI_FP:
        return "KILL (anti-FP must mark BB forever intent FP)"
    if "NANOGEN12" not in BB0_ANTI_FP and "nanogen12" not in BB0_ANTI_FP.lower():
        return "KILL (anti-FP must forbid NANOGEN12 rename)"
    return None


def _gate_north_ship() -> str | None:
    if "≤5M" not in BB0_NORTH_STAR:
        return "KILL (north-star charter incomplete)"
    if "defer" not in BB0_NORTH_STAR.lower():
        return "KILL (north-star must allow HOLD/defer)"
    if "gibberish-tail" not in BB0_SHIP_LOCK:
        return "KILL (ship lock must keep STRICT gibberish-tail claim)"
    if "TAC unlocked" not in BB0_SHIP_LOCK and "not TAC" not in BB0_SHIP_LOCK:
        return "KILL (ship lock must state not TAC unlocked)"
    return None


def _gate_notes() -> str | None:
    return _gate_safe_anti_fp() or _gate_north_ship()


def _gate_charters() -> str | None:
    return (
        _gate_modes()
        or _gate_cited_ba()
        or _gate_scoreboard()
        or _gate_forever()
        or _gate_ba_hold()
        or _gate_az_hold()
        or _gate_baselines()
        or _gate_gen_stance()
        or _gate_gen_judge()
        or _gate_real_eval()
        or _gate_notes()
    )


def decide_bb0_session(
    *,
    trials_dir_ready: bool,
    anti_fp_signed: bool,
    battery: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN BB-FOREVER/BA-hold/AZ-hold/scoreboard/gen-defer/real-eval + trials
    WHEN applying BB0 SESSION gate
    THEN PROMOTE iff BA locks cited, stance=defer, battery covers 4 modes,
         trials ready, anti-FP signed.
    """
    rows = list(battery) if battery is not None else list(BB0_ASK_BATTERY)
    err = _gate_charters() or _gate_battery(rows)
    if err:
        return err
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-bb/trials/ not ready)"
    return f"PROMOTE ({BB0_ID}: {BB0_THESIS})"
