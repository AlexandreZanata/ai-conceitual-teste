"""Wave BD0 SESSION: freeze BD-FOREVER · BA/BB/BC/AZ hold · scoreboard · gen-defer."""

from __future__ import annotations

from typing import Mapping, Sequence

from au_session_ops import AU0_MODES, map_au_product_mode
from az_session_ops import AZ0_HELDOUT_FP_ROWS, AZ0_OVERREFUSE_ROWS
from ba_session_ops import BA0_FOREVER_ROWS, BA0_SHIP_LOCK
from bb_session_ops import BB0_FOREVER_ROWS
from bc_session_ops import BC0_FOREVER_ROWS, BC0_SPEED_BASELINE

__all__ = [
    "BD0_ID",
    "BD0_THESIS",
    "BD0_MODES",
    "BD0_LATENCY_PATHS",
    "BD0_CITED_BC_LOCKS",
    "BD0_SCOREBOARD",
    "BD0_FOREVER_PROTOCOL",
    "BD0_FOREVER_ROWS",
    "BD0_BA_HOLD_PROTOCOL",
    "BD0_BB_HOLD_PROTOCOL",
    "BD0_BC_HOLD_PROTOCOL",
    "BD0_AZ_HOLD_PROTOCOL",
    "BD0_CTX_BASELINE",
    "BD0_SPEED_BASELINE",
    "BD0_GEN_STANCE",
    "BD0_TRUE_GEN_JUDGE",
    "BD0_REAL_EVAL_PROTOCOL",
    "BD0_ASK_BATTERY",
    "BD0_SAFE_NOTE",
    "BD0_ANTI_FP",
    "BD0_NORTH_STAR",
    "BD0_SHIP_LOCK",
    "map_bd_product_mode",
    "decide_bd0_session",
]

BD0_ID = "BD0-SESSION"
BD0_THESIS = (
    "Wave BD ACTIVE: freeze BD-FOREVER (reverse≠f-string · mul≠add + "
    "paraphrases · wrong-bank neighbors) · BA/BB/BC-FOREVER hold · AZ hold · "
    "§1 anti-FP scoreboard · ctx/speed baselines from BC · gen method stance "
    "= defer (M1|M2|M3|defer; H-NANOGEN14; not NANOGEN13+rename) · "
    "real-eval; next BD1 H-SEMINT (not CTX/SMART/FAST clone)"
)

BD0_MODES: frozenset[str] = AU0_MODES
BD0_LATENCY_PATHS: tuple[str, ...] = (
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
)

BD0_CITED_BC_LOCKS: frozenset[str] = frozenset(
    {
        "H-OPSFAM",
        "H-FASTLIFT",
        "H-CTXLIFT2",
        "H-NANOGEN13",
        "BC-REAL-EVAL",
        "BC-FREEZE",
    }
)

BD0_SHIP_LOCK = BA0_SHIP_LOCK

BD0_NORTH_STAR = (
    "Nano generative / mini-AGI-inspired ≤5M: semantic/wrong-bank anti-FP "
    "(BD-FOREVER FH 0 + BA/BB/BC forever hold + AZ hold + novel probes) + "
    "measurable context & speed on prod path + one honest generative "
    "method (M1|M2|M3) — else HOLD/DEFER; never pack theater · never "
    "LOOKUP-as-IQ · never NANOGEN14 = NANOGEN13+rename"
)

BD0_GEN_STANCE: Mapping[str, object] = {
    "stage": "BD0 freezes stance; BD4 H-NANOGEN14 applies or HOLD/DEFER",
    "stance": "defer",
    "allowed_stances": ["M1", "M2", "M3", "defer"],
    "method_candidates": {
        "M1": "teacher distill continue + anti-copy-gold loss",
        "M2": "student draft + bank/teacher rejector (hybrid)",
        "M3": "named CAPCHECK (raise params with ablations)",
    },
    "capcheck": "closed",
    "named_hyp": "H-NANOGEN14",
    "named_semint": "H-SEMINT",
    "named_fast": "H-FASTGAIN",
    "named_ctx": "H-CTXGAIN",
    "nanogen6_hold_cited": True,
    "nanogen7_hold_cited": True,
    "nanogen8_defer_cited": True,
    "nanogen9_defer_cited": True,
    "nanogen10_defer_cited": True,
    "nanogen11_defer_cited": True,
    "nanogen12_defer_cited": True,
    "nanogen13_defer_cited": True,
    "nanogen14_rename_forbidden": True,
    "true_continue_required_for_promote": True,
    "span_fallback_neq_gen": True,
    "rationale": (
        "No real new train/data/arch method ready at BD0; "
        "NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12·13 DEFER stand; CAPCHECK stays "
        "closed; prefer semantic intent/SEMWRAP gate (H-SEMINT) + ctx/speed "
        "hold + honest paper over vanity NANOGEN14 clone; BD4 PROMOTE "
        "only under true_continue else HOLD/DEFER"
    ),
    "bd4_gate": "true_continue → PROMOTE else HOLD/DEFER",
}

BD0_SAFE_NOTE = (
    "SAFE / ADVSAFE false-hit score ≠ answer quality; "
    "SAFE = no wrong gold only (anti-FP); "
    "pack FH 0 ≠ forever held-out generalization; "
    "semantic wrong-bank LOOKUP = false-hit "
    "(reverse→f-string · mul→add); "
    "BA+BB+BC forever PASS with BD-FOREVER FP = PACK THEATER; "
    "exact-gold ABSTAIN = product miss; "
    "gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE"
)

BD0_ANTI_FP = (
    "LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; "
    "never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; "
    "semantic wrong-bank LOOKUP = false-hit (BD-FOREVER reverse→f-string / "
    "mul→add); exact-gold ABSTAIN = miss (a.clear()); "
    "BA-FOREVER pow·mod·max·sort·len FH must stay 0; "
    "BB-FOREVER min·xor·absdiff·and·or FH must stay 0; "
    "BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; "
    "AZ hold div·sub·BIP FH must stay 0; "
    "BA+BB+BC PASS with BD FP = PACK THEATER; "
    "truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; "
    "eval path = prod ask path; "
    "generative bar = BD4 only under real new method; "
    "no NANOGEN14 = NANOGEN13+rename; no CTX/SMART/FAST clone; "
    "no invent Wave BE without lab-book reopen; "
    "prefer HOLD/defer over fake PROMOTE"
)

BD0_TRUE_GEN_JUDGE: Mapping[str, object] = {
    "stage": "BD4 H-NANOGEN14 applies only if stance≠defer or new method; "
    "BD0 freezes judge law",
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
    "nanogen12_defer_archived": True,
    "nanogen13_defer_archived": True,
    "nanogen14_rename_forbidden": True,
    "scoring": "short_answer_f1_or_hitl_true_continue_only",
    "promote_bar": "true_continue else HOLD/DEFER",
}

# H-FASTLIFT measured latency republished (speed baseline for BD2).
BD0_SPEED_BASELINE: Mapping[str, object] = {
    "source": "H-FASTLIFT / formal-hfastlift-bc2.md (prod ask path)",
    "path": "nano:z:ask prod path",
    "unit": "wall_ms",
    "paths": {
        "LOOKUP": {"p50": 0.0, "p99": 0.0},
        "PEAK": {
            "p50": 0.009197996405418962,
            "p99": 0.04120658952160745,
        },
        "DECODE": {
            "p50": 10.685407502023736,
            "p99": 11.968237772889552,
        },
        "ABSTAIN": {
            "p50": 92.71498299858649,
            "p99": 130.66686314792605,
        },
    },
    "quality_regress_forbidden": True,
    "warm_cache_vanity_forbidden": True,
    "bd2_gate": (
        "speed PROMOTE only if §1 anti-FP bars hold (incl BD-FOREVER)"
    ),
    "parent_bc0_baseline_cited": True,
    "parent_bc0_paths": dict(BC0_SPEED_BASELINE["paths"]),  # type: ignore[arg-type]
}

# Context baseline: content bars required (L_eff alone ≠ win).
BD0_CTX_BASELINE: Mapping[str, object] = {
    "source": "H-CTXLIFT2 / H-CTXHOLD / H-CTXREAL2 (content-first)",
    "l_eff_alone_insufficient": True,
    "content_bars_required": True,
    "modes_visible_required": True,
    "long_cite_howto_pack": True,
    "honest_abstain_when_missing": True,
    "bd3_gate": (
        "H-CTXGAIN PROMOTE only if content_ok + no new intent FP "
        "(incl BD-FOREVER) + p50/p99 published + modes visible"
    ),
}

BD0_SCOREBOARD: Mapping[str, object] = {
    "stage": "BD1 H-SEMINT closes bars; BD0 freezes §1 scoreboard",
    "cite_bc_locks": sorted(BD0_CITED_BC_LOCKS),
    "accept_artifact": (
        "AF+AQ+AS trust + STRICT ablated DECODE (BC H-OPSFAM·H-FASTLIFT·"
        "H-CTXLIFT2); NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12·13 DEFER; "
        "not TAC unlocked"
    ),
    "debts": [
        {
            "id": "bd_forever_false_hit_zero",
            "evidence": (
                "Live FP: reverse string→f-string; multiply→def add LOOKUP"
            ),
            "fix": "BD-FOREVER semantic FH 0 via intent gate (not bank-stuff)",
            "bar": "bd_forever_false_hit_max=0",
        },
        {
            "id": "ba_forever_hold_zero",
            "evidence": "BA pow·mod·max·sort·len FH 0 must hold",
            "fix": "BA-FOREVER regression hold",
            "bar": "ba_forever_false_hit_max=0",
        },
        {
            "id": "bb_forever_hold_zero",
            "evidence": "BB min·xor·absdiff·and·or FH 0 must hold",
            "fix": "BB-FOREVER regression hold",
            "bar": "bb_forever_false_hit_max=0",
        },
        {
            "id": "bc_forever_hold_zero",
            "evidence": "BC floordiv·neg·gcd·lshift·rshift·nand FH 0 must hold",
            "fix": "BC-FOREVER regression hold",
            "bar": "bc_forever_false_hit_max=0",
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
            "fix": "live nano:z:ask on BD+BA+BB+BC+AZ + ≥10 novel probes",
            "bar": "live_ask_scored True",
        },
        {
            "id": "speed_baseline_publish",
            "evidence": "BC FASTLIFT p50/p99 republished at BD0",
            "fix": "BD2 measures prod wall without FP regress",
            "bar": "speed_baseline_published True",
        },
        {
            "id": "ctx_baseline_publish",
            "evidence": "content bars required; L_eff alone forbidden",
            "fix": "BD3 measures usable long/cite/howto",
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
                "NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12·13 DEFER; no new method"
            ),
            "fix": "stance defer · CAPCHECK closed · no NANOGEN14 rename",
            "bar": "gen_stance=defer; nanogen14_rename_forbidden",
        },
        {
            "id": "paraphrase_eval_rule",
            "evidence": "BD-FOREVER seeds + held-out paraphrases at eval",
            "fix": "never bank-stuff exact seed strings",
            "bar": "paraphrase_required True; bank_stuff_forbidden",
        },
    ],
    "metrics": [
        "bd_forever_false_hit",
        "ba_forever_false_hit",
        "bb_forever_false_hit",
        "bc_forever_false_hit",
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
        "bd_forever_false_hit_max": 0,
        "ba_forever_false_hit_max": 0,
        "bb_forever_false_hit_max": 0,
        "bc_forever_false_hit_max": 0,
        "az_hold_false_hit_max": 0,
        "overrefuse_miss_max": 0,
        "bd_forever_min_n": 12,
        "bd_forever_classes_min": 3,
        "modes_required": list(BD0_LATENCY_PATHS),
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
        "ba_bb_bc_pass_neq_bd_forever": True,
        "bank_stuff_forbidden": True,
        "paraphrase_required": True,
        "regression_hold": True,
        "speed_baseline_published": True,
        "ctx_baseline_published": True,
        "live_ask_scored": True,
        "novel_probes_min": 10,
    },
    "baselines": {
        "ba_forever_fh": 0,
        "bb_forever_fh": 0,
        "bc_forever_fh": 0,
        "az_heldout_fh": 0,
        "az_overrefuse_miss": 0,
        "fastlift_latency": {
            "LOOKUP": {"p50": 0.0, "p99": 0.0},
            "PEAK": {
                "p50": 0.009197996405418962,
                "p99": 0.04120658952160745,
            },
            "DECODE": {
                "p50": 10.685407502023736,
                "p99": 11.968237772889552,
            },
            "ABSTAIN": {
                "p50": 92.71498299858649,
                "p99": 130.66686314792605,
            },
        },
        "ctxlift2_content": "PROMOTE",
        "nanogen6_decision": "HOLD",
        "nanogen7_decision": "HOLD",
        "nanogen8_decision": "DEFER",
        "nanogen9_decision": "DEFER",
        "nanogen10_decision": "DEFER",
        "nanogen11_decision": "DEFER",
        "nanogen12_decision": "DEFER",
        "nanogen13_decision": "DEFER",
        "bc_real_eval_battery": "13/13",
        "live_audit_bd_forever_fp": (
            "reverse string → f-string FP; multiply → def add FP observed"
        ),
        "forever_classes": [
            "semantic_reverse",
            "semantic_mul",
            "wrong_bank_neighbor",
        ],
        "ship_lock": BD0_SHIP_LOCK,
    },
    "runners": [
        "nano:z:ask",
        "nano:opsfam",
        "nano:bc:fastlift",
        "nano:bc:ctxlift2",
        "nano:nanogen13",
        "nano:advsafe",
        "nano:metrics",
        "nano:askabstain",
    ],
    "no_reopen_unless_fail": [
        "H-OPSFAM",
        "H-FASTLIFT",
        "H-CTXLIFT2",
        "H-INTENTGEN",
        "H-FASTHOLD",
        "H-CTXHOLD",
        "H-REALGAIN",
        "H-FASTREAL",
        "H-CTXREAL2",
        "H-PRODGEN",
        "H-SHIPAZ",
        "H-ADVSAFE",
    ],
    "complete_kb_claim_forbidden": True,
}

# Forever held-out residual FP (semantic wrong-bank ≠ BA/BB/BC/AZ packs).
BD0_FOREVER_ROWS: tuple[dict[str, str], ...] = (
    {
        "id": "BD-FH-01",
        "class": "semantic_reverse",
        "expect_mode": "ABSTAIN",
        "question": "How do I reverse a string in Python?",
    },
    {
        "id": "BD-FH-02",
        "class": "semantic_reverse",
        "expect_mode": "ABSTAIN",
        "question": (
            "How can I get the reversed version of string s in Python?"
        ),
    },
    {
        "id": "BD-FH-03",
        "class": "semantic_reverse",
        "expect_mode": "ABSTAIN",
        "question": "Show me s[::-1] usage — reverse string s.",
    },
    {
        "id": "BD-FH-04",
        "class": "semantic_reverse",
        "expect_mode": "ABSTAIN",
        "question": (
            "Python: reverse the characters of a text string without "
            "using f-strings."
        ),
    },
    {
        "id": "BD-FH-05",
        "class": "semantic_mul",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a Python function that multiplies a and b and returns "
            "the product."
        ),
    },
    {
        "id": "BD-FH-06",
        "class": "semantic_mul",
        "expect_mode": "ABSTAIN",
        "question": "Please write multiply(a, b) returning a times b.",
    },
    {
        "id": "BD-FH-07",
        "class": "semantic_mul",
        "expect_mode": "ABSTAIN",
        "question": (
            "Python: product of two ints a and b as a one-liner function."
        ),
    },
    {
        "id": "BD-FH-08",
        "class": "semantic_mul",
        "expect_mode": "ABSTAIN",
        "question": (
            "Implement mul2(a, b) that returns a * b — not a + b."
        ),
    },
    {
        "id": "BD-FH-09",
        "class": "wrong_bank_neighbor",
        "expect_mode": "ABSTAIN",
        "question": "Clamp x between lo and hi in Python — one expression.",
    },
    {
        "id": "BD-FH-10",
        "class": "wrong_bank_neighbor",
        "expect_mode": "ABSTAIN",
        "question": "What does list.sort() return in Python?",
    },
    {
        "id": "BD-FH-11",
        "class": "wrong_bank_neighbor",
        "expect_mode": "ABSTAIN",
        "question": (
            "How do I convert a string to title case in Python without "
            "using format/f-string rules?"
        ),
    },
    {
        "id": "BD-FH-12",
        "class": "semantic_mul",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write product(a, b) returning the multiplication of two "
            "integers — do not return a+b."
        ),
    },
)

BD0_FOREVER_PROTOCOL: Mapping[str, object] = {
    "stage": "BD1 H-SEMINT scores; BD0 freezes protocol",
    "held_out": True,
    "forever": True,
    "bank_stuff_forbidden": True,
    "paraphrase_required": True,
    "neq_ba_forever": True,
    "neq_bb_forever": True,
    "neq_bc_forever": True,
    "neq_az_heldout": True,
    "intent_mismatch_is_false_hit": True,
    "semantic_wrong_bank_is_false_hit": True,
    "source": (
        "live residual FP (reverse≠f-string · mul≠add · wrong-bank neighbors)"
    ),
    "min_n": 12,
    "classes_min": 3,
    "required_classes": [
        "semantic_reverse",
        "semantic_mul",
        "wrong_bank_neighbor",
    ],
    "scoring": "false-hit rate on default ask path (mismatch → ABSTAIN)",
    "path": "nano:z:ask --wrap --semwrap",
    "pack_pass_neq_forever": True,
    "ba_bb_bc_pass_neq_bd_forever": True,
    "live_fp_id": "BD-FH-01",
    "rows": list(BD0_FOREVER_ROWS),
}

BD0_BA_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BD1 must hold BA bars; BD0 freezes regression pack",
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

BD0_BB_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BD1 must hold BB bars; BD0 freezes regression pack",
    "source": "BB0_FOREVER_ROWS",
    "heldout_n": len(BB0_FOREVER_ROWS),
    "forever_false_hit_max": 0,
    "required_classes": [
        "ops_min",
        "ops_xor",
        "ops_absdiff",
        "ops_and",
        "ops_or",
    ],
    "path": "nano:z:ask --wrap --semwrap",
    "regression_hold": True,
}

BD0_BC_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BD1 must hold BC bars; BD0 freezes regression pack",
    "source": "BC0_FOREVER_ROWS",
    "heldout_n": len(BC0_FOREVER_ROWS),
    "forever_false_hit_max": 0,
    "required_classes": [
        "ops_floordiv",
        "ops_neg",
        "ops_gcd",
        "ops_lshift",
        "ops_rshift",
        "ops_nand",
    ],
    "path": "nano:z:ask --wrap --semwrap",
    "regression_hold": True,
}

BD0_AZ_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BD1 must hold AZ bars; BD0 freezes regression pack",
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

BD0_REAL_EVAL_PROTOCOL: Mapping[str, object] = {
    "live_ask_battery": True,
    "summary_only_forbidden": True,
    "product_mode_required": True,
    "wall_ms_n_new_mandatory": True,
    "wall_ms_n_new_insufficient_for_decode_quality": True,
    "lookup_neq_iq": True,
    "peak_neq_open_chat": True,
    "safe_neq_quality": True,
    "intent_mismatch_is_false_hit": True,
    "semantic_wrong_bank_is_false_hit": True,
    "exact_gold_abstain_is_miss": True,
    "gold_substring_neq_gen": True,
    "gibberish_tail_fails": True,
    "span_fallback_neq_gen": True,
    "pack_pass_neq_forever": True,
    "ba_bb_bc_pass_neq_bd_forever": True,
    "eval_eq_prod_ask": True,
    "answer_usability_scored": True,
    "novel_probes_min": 10,
    "score_labels": ["OK", "FP", "MISS", "ABSTAIN-OK"],
    "gen_claim_rule": (
        "only if BD4 H-NANOGEN14 PROMOTE (true_continue; "
        "real new method M1|M2|M3; never NANOGEN13+rename; "
        "span-fallback ≠ gen)"
    ),
    "mini_agi_rule": (
        "forbidden while gen stance defer or NANOGEN14 HOLD/DEFER"
    ),
    "stage": "BD5 BD-REAL-EVAL scores; BD0 freezes protocol",
}

BD0_ASK_BATTERY: tuple[dict[str, str], ...] = (
    {
        "id": "BD-ASK-01",
        "kind": "known_lookup",
        "expect_mode": "LOOKUP",
        "question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
    },
    {
        "id": "BD-ASK-02",
        "kind": "ood_abstain",
        "expect_mode": "ABSTAIN",
        "question": "Who won the 2022 FIFA World Cup?",
    },
    {
        "id": "BD-ASK-03",
        "kind": "near_miss",
        "expect_mode": "ABSTAIN",
        "question": (
            "BIP-39 entropy formula is CS = ENT / 32 — confirm for "
            "SegWit witness discount?"
        ),
    },
    {
        "id": "BD-ASK-04",
        "kind": "labeled_peak",
        "expect_mode": "PEAK",
        "question": (
            "From the curated Rust book intro, extract one sentence "
            "on ownership (label PEAK, not open chat)."
        ),
    },
    {
        "id": "BD-ASK-05",
        "kind": "decode_content",
        "expect_mode": "DECODE",
        "question": "Explain Merkle trees briefly",
    },
    {
        "id": "BD-ASK-06",
        "kind": "junk_trap",
        "expect_mode": "ABSTAIN",
        "question": ".",
    },
    {
        "id": "BD-ASK-07",
        "kind": "bd_forever_reverse_fp",
        "expect_mode": "ABSTAIN",
        "question": "How do I reverse a string in Python?",
    },
    {
        "id": "BD-ASK-08",
        "kind": "overrefuse_gold",
        "expect_mode": "LOOKUP",
        "question": "Remove all items from list `a` — one method call.",
    },
    {
        "id": "BD-ASK-09",
        "kind": "az_hold_div",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named div that returns "
            "the quotient of two integers a and b."
        ),
    },
    {
        "id": "BD-ASK-10",
        "kind": "ba_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named pow2 that returns "
            "a raised to the power of b for two integers."
        ),
    },
    {
        "id": "BD-ASK-11",
        "kind": "bb_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named min2 that returns "
            "the smaller of two integers a and b."
        ),
    },
    {
        "id": "BD-ASK-12",
        "kind": "bc_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a Python function floordiv(a, b) that returns a // b."
        ),
    },
    {
        "id": "BD-ASK-13",
        "kind": "bd_forever_mul_fp",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a Python function that multiplies a and b and returns "
            "the product."
        ),
    },
    {
        "id": "BD-ASK-14",
        "kind": "bd_forever_neighbor_fp",
        "expect_mode": "ABSTAIN",
        "question": "What does list.sort() return in Python?",
    },
)


def map_bd_product_mode(raw_mode: str) -> str:
    """
    GIVEN raw telemetry mode string
    WHEN applying BD0 mode charter (inherits AU0 aliases)
    THEN return LOOKUP | PEAK | DECODE | ABSTAIN | UNKNOWN.
    """
    return map_au_product_mode(raw_mode)


def _gate_modes() -> str | None:
    if set(BD0_LATENCY_PATHS) != BD0_MODES:
        return "KILL (latency paths ≠ mode charter)"
    if "ABSTAIN" not in BD0_MODES:
        return "KILL (ABSTAIN missing from modes)"
    return None


def _gate_cited_bc() -> str | None:
    cited = BD0_SCOREBOARD.get("cite_bc_locks")
    if not isinstance(cited, list):
        return "KILL (scoreboard must cite BC locks)"
    if set(cited) != BD0_CITED_BC_LOCKS:
        return "KILL (scoreboard BC lock citations incomplete)"
    return None


def _gate_debt_ids() -> str | None:
    debts = BD0_SCOREBOARD.get("debts")
    if not isinstance(debts, list) or len(debts) < 13:
        return "KILL (scoreboard must list ≥13 post-BC debts)"
    ids = {str(d.get("id", "")) for d in debts if isinstance(d, dict)}
    need = {
        "bd_forever_false_hit_zero",
        "ba_forever_hold_zero",
        "bb_forever_hold_zero",
        "bc_forever_hold_zero",
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
    checks = (
        ("bd_forever_false_hit_max", 0, "bd_forever_false_hit_max must be 0"),
        ("ba_forever_false_hit_max", 0, "ba_forever_false_hit_max must be 0"),
        ("bb_forever_false_hit_max", 0, "bb_forever_false_hit_max must be 0"),
        ("bc_forever_false_hit_max", 0, "bc_forever_false_hit_max must be 0"),
        ("az_hold_false_hit_max", 0, "az_hold_false_hit_max must be 0"),
        ("overrefuse_miss_max", 0, "overrefuse_miss_max must be 0"),
    )
    for key, want, msg in checks:
        if int(bars.get(key, 1 if want == 0 else -1)) != want:
            return f"KILL ({msg})"
    if int(bars.get("bd_forever_min_n", 0)) < 12:
        return "KILL (bd_forever_min_n must be ≥12)"
    if int(bars.get("bd_forever_classes_min", 0)) < 3:
        return "KILL (bd_forever_classes_min must be ≥3)"
    if int(bars.get("novel_probes_min", 0)) < 10:
        return "KILL (novel_probes_min must be ≥10)"
    return None


def _gate_debt_bar_flags(bars: Mapping[str, object]) -> str | None:
    flags = (
        ("decode_gibberish_neq_content_ok", "KILL (DECODE gibberish≠content_ok)"),
        ("eval_eq_prod_ask", "KILL (eval path must equal prod ask path)"),
        ("pack_pass_neq_forever", "KILL (pack PASS ≠ forever bar missing)"),
        (
            "ba_bb_bc_pass_neq_bd_forever",
            "KILL (BA+BB+BC PASS ≠ BD forever bar missing)",
        ),
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
    if not isinstance(modes, list) or set(modes) != BD0_MODES:
        return "KILL (scoreboard modes_required incomplete)"
    return None


def _gate_debt_bars() -> str | None:
    bars = BD0_SCOREBOARD.get("bars")
    if not isinstance(bars, dict):
        return "KILL (scoreboard bars missing)"
    return _gate_debt_bar_nums(bars) or _gate_debt_bar_flags(bars)


def _gate_debt_metrics() -> str | None:
    metrics = BD0_SCOREBOARD.get("metrics")
    need_m = {
        "bd_forever_false_hit",
        "ba_forever_false_hit",
        "bb_forever_false_hit",
        "bc_forever_false_hit",
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
        + list(BB0_FOREVER_ROWS)
        + list(BC0_FOREVER_ROWS)
        + list(AZ0_HELDOUT_FP_ROWS)
        + list(AZ0_OVERREFUSE_ROWS)
    )
    return {str(p.get("question", "")).strip() for p in rows}


def _gate_fh_rows() -> str | None:
    ids: set[str] = set()
    classes: set[str] = set()
    prior = _prior_questions()
    for item in BD0_FOREVER_ROWS:
        tid = str(item.get("id", ""))
        if not tid.startswith("BD-FH-"):
            return f"KILL (bad forever id: {tid})"
        if tid in ids:
            return f"KILL (duplicate forever id: {tid})"
        ids.add(tid)
        q = str(item.get("question", "")).strip()
        if not q:
            return f"KILL (empty forever question: {tid})"
        if q in prior:
            return f"KILL (forever reuses BA/BB/BC/AZ held-out: {tid})"
        if str(item.get("expect_mode", "")) != "ABSTAIN":
            return f"KILL (forever expect_mode must be ABSTAIN: {tid})"
        classes.add(str(item.get("class", "")))
    need = {
        "semantic_reverse",
        "semantic_mul",
        "wrong_bank_neighbor",
    }
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
        ("neq_bb_forever", "KILL (forever must ≠ BB-FOREVER)"),
        ("neq_bc_forever", "KILL (forever must ≠ BC-FOREVER)"),
        ("neq_az_heldout", "KILL (forever must ≠ AZ held-out)"),
        (
            "intent_mismatch_is_false_hit",
            "KILL (forever must mark mismatch as false-hit)",
        ),
        (
            "semantic_wrong_bank_is_false_hit",
            "KILL (forever must mark semantic wrong-bank as false-hit)",
        ),
        (
            "pack_pass_neq_forever",
            "KILL (forever must mark pack PASS ≠ forever)",
        ),
        (
            "ba_bb_bc_pass_neq_bd_forever",
            "KILL (forever must mark BA+BB+BC PASS ≠ BD forever)",
        ),
    )
    for key, msg in flags:
        if not bool(proto.get(key)):
            return msg
    return None


def _gate_forever_sizes(proto: Mapping[str, object]) -> str | None:
    rows = proto.get("rows")
    min_n = int(proto.get("min_n", 12))
    if min_n < 12:
        return "KILL (forever min_n must be ≥12)"
    if not isinstance(rows, list) or len(rows) < min_n:
        return f"KILL (forever must have ≥{min_n} rows)"
    if len(BD0_FOREVER_ROWS) < min_n:
        return "KILL (BD0_FOREVER_ROWS below min_n)"
    if str(proto.get("live_fp_id", "")) != "BD-FH-01":
        return "KILL (forever must pin live_fp_id=BD-FH-01)"
    req = proto.get("required_classes")
    if not isinstance(req, list) or len(req) < 3:
        return "KILL (forever required_classes incomplete)"
    return _gate_fh_rows()


def _gate_forever() -> str | None:
    proto = BD0_FOREVER_PROTOCOL
    return _gate_forever_flags(proto) or _gate_forever_sizes(proto)


def _gate_hold_pack(
    *,
    proto: Mapping[str, object],
    label: str,
    min_n: int,
    need: set[str],
    max_key: str = "forever_false_hit_max",
) -> str | None:
    if int(proto.get(max_key, 1)) != 0:
        return f"KILL ({label} {max_key} must be 0)"
    if not bool(proto.get("regression_hold")):
        return f"KILL ({label} must require regression_hold)"
    n_key = "heldout_n"
    if int(proto.get(n_key, 0)) < min_n:
        return f"KILL ({label} must cite ≥{min_n} forever rows)"
    req = proto.get("required_classes")
    if not isinstance(req, list) or not need.issubset(set(req)):
        return f"KILL ({label} required_classes incomplete)"
    return None


def _gate_ba_hold() -> str | None:
    return _gate_hold_pack(
        proto=BD0_BA_HOLD_PROTOCOL,
        label="BA hold",
        min_n=15,
        need={"ops_pow", "ops_mod", "ops_max", "list_sort", "list_len"},
    )


def _gate_bb_hold() -> str | None:
    return _gate_hold_pack(
        proto=BD0_BB_HOLD_PROTOCOL,
        label="BB hold",
        min_n=15,
        need={"ops_min", "ops_xor", "ops_absdiff", "ops_and", "ops_or"},
    )


def _gate_bc_hold() -> str | None:
    return _gate_hold_pack(
        proto=BD0_BC_HOLD_PROTOCOL,
        label="BC hold",
        min_n=18,
        need={
            "ops_floordiv",
            "ops_neg",
            "ops_gcd",
            "ops_lshift",
            "ops_rshift",
            "ops_nand",
        },
    )


def _gate_az_hold() -> str | None:
    proto = BD0_AZ_HOLD_PROTOCOL
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
    paths = BD0_SPEED_BASELINE.get("paths")
    if not isinstance(paths, dict) or set(paths) != BD0_MODES:
        return "KILL (speed baseline paths incomplete)"
    if not bool(BD0_SPEED_BASELINE.get("quality_regress_forbidden")):
        return "KILL (speed baseline must forbid quality regress)"
    if "FASTLIFT" not in str(BD0_SPEED_BASELINE.get("source", "")):
        return "KILL (speed baseline must cite H-FASTLIFT)"
    if not bool(BD0_CTX_BASELINE.get("l_eff_alone_insufficient")):
        return "KILL (ctx baseline must mark L_eff alone insufficient)"
    if not bool(BD0_CTX_BASELINE.get("content_bars_required")):
        return "KILL (ctx baseline must require content bars)"
    return None


def _gate_gen_stance_core() -> str | None:
    stance = str(BD0_GEN_STANCE.get("stance", ""))
    allowed = BD0_GEN_STANCE.get("allowed_stances")
    if not isinstance(allowed, list):
        return "KILL (gen stance allowed_stances missing)"
    if stance not in allowed:
        return "KILL (gen stance must be M1|M2|M3|defer)"
    if stance != "defer":
        return "KILL (BD0 gen stance must be defer until real new method)"
    if str(BD0_GEN_STANCE.get("capcheck", "")) != "closed":
        return "KILL (BD0 CAPCHECK must stay closed)"
    names = (
        ("named_hyp", "H-NANOGEN14"),
        ("named_semint", "H-SEMINT"),
        ("named_fast", "H-FASTGAIN"),
        ("named_ctx", "H-CTXGAIN"),
    )
    for key, want in names:
        if str(BD0_GEN_STANCE.get(key, "")) != want:
            return f"KILL (BD0 must name {want})"
    methods = BD0_GEN_STANCE.get("method_candidates")
    if not isinstance(methods, dict) or set(methods) != {"M1", "M2", "M3"}:
        return "KILL (gen stance method_candidates incomplete)"
    return None


def _gate_gen_stance_cites() -> str | None:
    cites = (
        ("nanogen14_rename_forbidden", "KILL (forbid NANOGEN14 rename)"),
        ("nanogen6_hold_cited", "KILL (cite NANOGEN6 HOLD)"),
        ("nanogen7_hold_cited", "KILL (cite NANOGEN7 HOLD)"),
        ("nanogen8_defer_cited", "KILL (cite NANOGEN8 DEFER)"),
        ("nanogen9_defer_cited", "KILL (cite NANOGEN9 DEFER)"),
        ("nanogen10_defer_cited", "KILL (cite NANOGEN10 DEFER)"),
        ("nanogen11_defer_cited", "KILL (cite NANOGEN11 DEFER)"),
        ("nanogen12_defer_cited", "KILL (cite NANOGEN12 DEFER)"),
        ("nanogen13_defer_cited", "KILL (cite NANOGEN13 DEFER)"),
    )
    for key, msg in cites:
        if not bool(BD0_GEN_STANCE.get(key)):
            return msg
    rat = str(BD0_GEN_STANCE.get("rationale", "")).lower()
    if "nanogen" not in rat or "defer" not in rat:
        return "KILL (gen stance rationale incomplete)"
    return None


def _gate_gen_stance() -> str | None:
    return _gate_gen_stance_core() or _gate_gen_stance_cites()


def _gate_gen_judge() -> str | None:
    judge = BD0_TRUE_GEN_JUDGE
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
        "nanogen12_defer_archived",
        "nanogen13_defer_archived",
        "nanogen14_rename_forbidden",
    )
    for key in flags:
        if not bool(judge.get(key)):
            return f"KILL (true judge must set {key})"
    if "true_continue" not in str(judge.get("scoring", "")):
        return "KILL (true judge scoring must be true_continue only)"
    return None


def _gate_real_eval_flags() -> str | None:
    proto = BD0_REAL_EVAL_PROTOCOL
    flags = (
        ("live_ask_battery", "KILL (real-eval must require live ask battery)"),
        ("summary_only_forbidden", "KILL (real-eval must forbid summary-only)"),
        ("wall_ms_n_new_mandatory", "KILL (real-eval must require wall_ms/n_new)"),
        ("eval_eq_prod_ask", "KILL (real-eval must require eval=prod ask)"),
        ("intent_mismatch_is_false_hit", "KILL (real-eval must mark intent FP)"),
        (
            "semantic_wrong_bank_is_false_hit",
            "KILL (real-eval must mark semantic wrong-bank FP)",
        ),
        (
            "exact_gold_abstain_is_miss",
            "KILL (real-eval must mark exact-gold ABSTAIN as miss)",
        ),
        ("gold_substring_neq_gen", "KILL (real-eval must reject gold-substring)"),
        ("gibberish_tail_fails", "KILL (real-eval must fail gibberish tail)"),
        ("span_fallback_neq_gen", "KILL (real-eval must reject span-fallback)"),
        ("pack_pass_neq_forever", "KILL (real-eval must mark pack≠forever)"),
        (
            "ba_bb_bc_pass_neq_bd_forever",
            "KILL (real-eval must mark BA+BB+BC PASS ≠ BD forever)",
        ),
        (
            "wall_ms_n_new_insufficient_for_decode_quality",
            "KILL (real-eval must mark wall_ms/n_new insufficient for DECODE)",
        ),
    )
    for key, msg in flags:
        if not bool(proto.get(key)):
            return msg
    if int(proto.get("novel_probes_min", 0)) < 10:
        return "KILL (real-eval novel_probes_min must be ≥10)"
    return None


def _gate_real_eval() -> str | None:
    err = _gate_real_eval_flags()
    if err:
        return err
    claim = str(BD0_REAL_EVAL_PROTOCOL.get("gen_claim_rule", "")).lower()
    if "nanogen14" not in claim:
        return "KILL (real-eval gen_claim_rule incomplete)"
    if "rename" not in claim:
        return "KILL (real-eval must forbid NANOGEN14 rename)"
    labels = BD0_REAL_EVAL_PROTOCOL.get("score_labels")
    need = {"OK", "FP", "MISS", "ABSTAIN-OK"}
    if not isinstance(labels, list) or not need.issubset(set(labels)):
        return "KILL (real-eval score_labels incomplete)"
    return None


def _scan_battery_row(
    item: Mapping[str, str], ids: set[str]
) -> tuple[str | None, str, str]:
    tid = str(item.get("id", ""))
    if not tid.startswith("BD-ASK-"):
        return f"KILL (bad battery id: {tid})", "", ""
    if tid in ids:
        return f"KILL (duplicate battery id: {tid})", "", ""
    q = str(item.get("question", ""))
    if tid != "BD-ASK-06" and not q.strip():
        return f"KILL (empty battery question: {tid})", "", ""
    mode = str(item.get("expect_mode", ""))
    if mode not in BD0_MODES:
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
    if modes_seen != BD0_MODES:
        return f"KILL (ask battery modes incomplete: {sorted(modes_seen)})"
    need_kinds = {
        "near_miss",
        "bd_forever_reverse_fp",
        "bd_forever_mul_fp",
        "bd_forever_neighbor_fp",
        "ba_forever_hold",
        "bb_forever_hold",
        "bc_forever_hold",
        "overrefuse_gold",
        "az_hold_div",
        "labeled_peak",
        "junk_trap",
        "decode_content",
    }
    if not need_kinds.issubset(kinds):
        return "KILL (ask battery must cover BD scoreboard kinds)"
    return None


def _gate_safe_anti_fp() -> str | None:
    if "≠" not in BD0_SAFE_NOTE and "!=" not in BD0_SAFE_NOTE:
        return "KILL (SAFE≠quality note missing)"
    if "LOOKUP" not in BD0_ANTI_FP:
        return "KILL (anti-FP charter incomplete)"
    if "eval path = prod" not in BD0_ANTI_FP.lower():
        return "KILL (anti-FP must require eval=prod ask)"
    anti = BD0_ANTI_FP.lower()
    if "reverse" not in anti and "bd-forever" not in anti:
        return "KILL (anti-FP must mark BD forever semantic FP)"
    if "NANOGEN14" not in BD0_ANTI_FP and "nanogen14" not in anti:
        return "KILL (anti-FP must forbid NANOGEN14 rename)"
    return None


def _gate_north_ship() -> str | None:
    if "≤5M" not in BD0_NORTH_STAR:
        return "KILL (north-star charter incomplete)"
    if "defer" not in BD0_NORTH_STAR.lower():
        return "KILL (north-star must allow HOLD/defer)"
    if "gibberish-tail" not in BD0_SHIP_LOCK:
        return "KILL (ship lock must keep STRICT gibberish-tail claim)"
    if "TAC unlocked" not in BD0_SHIP_LOCK and "not TAC" not in BD0_SHIP_LOCK:
        return "KILL (ship lock must state not TAC unlocked)"
    return None


def _gate_notes() -> str | None:
    return _gate_safe_anti_fp() or _gate_north_ship()


def _gate_charters() -> str | None:
    return (
        _gate_modes()
        or _gate_cited_bc()
        or _gate_scoreboard()
        or _gate_forever()
        or _gate_ba_hold()
        or _gate_bb_hold()
        or _gate_bc_hold()
        or _gate_az_hold()
        or _gate_baselines()
        or _gate_gen_stance()
        or _gate_gen_judge()
        or _gate_real_eval()
        or _gate_notes()
    )


def decide_bd0_session(
    *,
    trials_dir_ready: bool,
    anti_fp_signed: bool,
    battery: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN BD-FOREVER/BA/BB/BC/AZ-hold/scoreboard/gen-defer/real-eval + trials
    WHEN applying BD0 SESSION gate
    THEN PROMOTE iff BC locks cited, stance=defer, battery covers 4 modes,
         trials ready, anti-FP signed.
    """
    rows = list(battery) if battery is not None else list(BD0_ASK_BATTERY)
    err = _gate_charters() or _gate_battery(rows)
    if err:
        return err
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-bd/trials/ not ready)"
    return f"PROMOTE ({BD0_ID}: {BD0_THESIS})"
