"""Wave BF0 SESSION: freeze BF-FOREVER · BA…BE/AZ hold · util · gen-SKIP."""

from __future__ import annotations

from typing import Mapping, Sequence

from au_session_ops import AU0_MODES, map_au_product_mode
from az_session_ops import AZ0_HELDOUT_FP_ROWS, AZ0_OVERREFUSE_ROWS
from ba_session_ops import BA0_FOREVER_ROWS, BA0_SHIP_LOCK
from bb_session_ops import BB0_FOREVER_ROWS
from bc_session_ops import BC0_FOREVER_ROWS
from bd_session_ops import BD0_FOREVER_ROWS
from be_session_ops import BE0_FOREVER_ROWS, BE0_SPEED_BASELINE

__all__ = [
    "BF0_ID",
    "BF0_THESIS",
    "BF0_MODES",
    "BF0_LATENCY_PATHS",
    "BF0_CITED_BE_LOCKS",
    "BF0_SCOREBOARD",
    "BF0_FOREVER_PROTOCOL",
    "BF0_FOREVER_ROWS",
    "BF0_BA_HOLD_PROTOCOL",
    "BF0_BB_HOLD_PROTOCOL",
    "BF0_BC_HOLD_PROTOCOL",
    "BF0_BD_HOLD_PROTOCOL",
    "BF0_BE_HOLD_PROTOCOL",
    "BF0_AZ_HOLD_PROTOCOL",
    "BF0_CTX_BASELINE",
    "BF0_SPEED_BASELINE",
    "BF0_UTIL_TRACK",
    "BF0_GEN_STANCE",
    "BF0_TRUE_GEN_JUDGE",
    "BF0_REAL_EVAL_PROTOCOL",
    "BF0_ASK_BATTERY",
    "BF0_SAFE_NOTE",
    "BF0_ANTI_FP",
    "BF0_NORTH_STAR",
    "BF0_SHIP_LOCK",
    "map_bf_product_mode",
    "decide_bf0_session",
]

BF0_ID = "BF0-SESSION"
BF0_THESIS = (
    "Wave BF ACTIVE: freeze BF-FOREVER (predicate/boolean even≠add + "
    "paraphrases · bool/arity neighbors) · BA/BB/BC/BD/BE-FOREVER hold · "
    "AZ hold · §1 anti-FP scoreboard · Track A+ utilization · ctx/speed "
    "baselines from BE · gen stance = SKIP (no written M1|M2|M3 plan; "
    "not NANOGEN16 rename) · real-eval; next BF1 H-PREDINT "
    "(not CTX/SMART/FAST clone)"
)

BF0_MODES: frozenset[str] = AU0_MODES
BF0_LATENCY_PATHS: tuple[str, ...] = (
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
)

BF0_CITED_BE_LOCKS: frozenset[str] = frozenset(
    {
        "H-COMPINT",
        "H-SHIPUSE",
        "H-FASTBE",
        "H-CTXBE",
        "H-NANOGEN15",
        "BE-REAL-EVAL",
        "BE-FREEZE",
    }
)

BF0_SHIP_LOCK = BA0_SHIP_LOCK

BF0_NORTH_STAR = (
    "Nano generative / mini-AGI-inspired ≤5M: predicate/boolean anti-FP "
    "(BF-FOREVER FH 0 + BA…BE forever hold + AZ hold + novel probes) + "
    "ship/utilize proven AF+AQ+AS stack + measurable context & speed + "
    "one honest generative method (M1|M2|M3) — else SKIP gen letters; never "
    "pack theater · never LOOKUP-as-IQ · never NANOGEN16 without method plan"
)

BF0_GEN_STANCE: Mapping[str, object] = {
    "stage": "BF0 freezes stance; BF5 H-NANOGEN16 SKIP without method plan",
    "stance": "skip",
    "allowed_stances": ["M1", "M2", "M3", "skip"],
    "method_candidates": {
        "M1": "teacher distill continue + anti-copy-gold loss",
        "M2": "student draft + bank/teacher rejector (hybrid)",
        "M3": "named CAPCHECK (raise params with ablations)",
    },
    "method_plan_attached": False,
    "capcheck": "closed",
    "named_hyp": "H-NANOGEN16",
    "named_predint": "H-PREDINT",
    "named_shipuse2": "H-SHIPUSE2",
    "named_fast": "H-FASTBF",
    "named_ctx": "H-CTXBF",
    "nanogen6_hold_cited": True,
    "nanogen7_hold_cited": True,
    "nanogen8_defer_cited": True,
    "nanogen9_defer_cited": True,
    "nanogen10_defer_cited": True,
    "nanogen11_defer_cited": True,
    "nanogen12_defer_cited": True,
    "nanogen13_defer_cited": True,
    "nanogen14_defer_cited": True,
    "nanogen15_defer_cited": True,
    "nanogen16_rename_forbidden": True,
    "nanogen16_without_plan_forbidden": True,
    "skip_gen_stop_rule": True,
    "true_continue_required_for_promote": True,
    "span_fallback_neq_gen": True,
    "rationale": (
        "No written M1|M2|M3 method plan at BF0; H-NANOGEN15 already "
        "DEFER once — stop rule forbids empty NANOGEN16 letter; "
        "NANOGEN6·7 HOLD · NANOGEN8…15 DEFER stand; CAPCHECK stays closed; "
        "prefer predicate/schema gate (H-PREDINT) + Track A+ utilization "
        "(H-SHIPUSE2) over vanity NANOGEN16 rename; BF5 = SKIP stage"
    ),
    "bf5_gate": "SKIP stage (no written M1|M2|M3 plan at BF0)",
}

BF0_SAFE_NOTE = (
    "SAFE / ADVSAFE false-hit score ≠ answer quality; "
    "SAFE = no wrong gold only (anti-FP); "
    "pack FH 0 ≠ forever held-out generalization; "
    "predicate/boolean wrong-bank LOOKUP = false-hit "
    "(even→def add); "
    "BA…BE forever PASS with BF-FOREVER FP = PACK THEATER; "
    "exact-gold ABSTAIN = product miss; "
    "gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE"
)

BF0_ANTI_FP = (
    "LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; "
    "never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; "
    "predicate/boolean LOOKUP = false-hit (BF-FOREVER even→add); "
    "type/coercion LOOKUP = false-hit (BE-FOREVER str→int→add); "
    "exact-gold ABSTAIN = miss (a.clear()); "
    "BA-FOREVER pow·mod·max·sort·len FH must stay 0; "
    "BB-FOREVER min·xor·absdiff·and·or FH must stay 0; "
    "BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; "
    "BD-FOREVER reverse≠f-string · mul≠add FH must stay 0; "
    "BE-FOREVER str→int / type-coercion FH must stay 0; "
    "AZ hold div·sub·BIP FH must stay 0; "
    "BA…BE PASS with BF FP = PACK THEATER; "
    "truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; "
    "eval path = prod ask path; "
    "generative bar = BF5 only under written method plan; "
    "no NANOGEN16 without M1|M2|M3 plan; no CTX/SMART/FAST clone; "
    "no invent Wave BG without lab-book reopen; "
    "prefer predicate/schema gate over bank stuffing; "
    "prefer HOLD/SKIP over fake PROMOTE"
)

BF0_TRUE_GEN_JUDGE: Mapping[str, object] = {
    "stage": "BF5 H-NANOGEN16 SKIP without method plan; BF0 freezes judge",
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
    "nanogen14_defer_archived": True,
    "nanogen15_defer_archived": True,
    "nanogen16_rename_forbidden": True,
    "nanogen16_without_plan_forbidden": True,
    "scoring": "short_answer_f1_or_hitl_true_continue_only",
    "promote_bar": "true_continue else SKIP (no empty DEFER letter)",
}

# H-FASTBE measured latency republished (speed baseline for BF3).
BF0_SPEED_BASELINE: Mapping[str, object] = {
    "source": "H-FASTBE / formal-hfastbe-fastbe.md (prod ask path)",
    "path": "nano:z:ask prod path",
    "unit": "wall_ms",
    "paths": {
        "LOOKUP": {"p50": 0.0, "p99": 0.0},
        "PEAK": {
            "p50": 0.009324998245574534,
            "p99": 0.015838620602153245,
        },
        "DECODE": {
            "p50": 10.75098400178831,
            "p99": 11.185807651199866,
        },
        "ABSTAIN": {
            "p50": 93.31420949456515,
            "p99": 126.17945601174145,
        },
    },
    "quality_regress_forbidden": True,
    "warm_cache_vanity_forbidden": True,
    "bf3_gate": (
        "speed PROMOTE only if §1 anti-FP bars hold (incl BF-FOREVER)"
    ),
    "parent_be0_baseline_cited": True,
    "parent_be0_paths": dict(BE0_SPEED_BASELINE["paths"]),  # type: ignore[arg-type]
}

BF0_CTX_BASELINE: Mapping[str, object] = {
    "source": "H-CTXBE / H-CTXGAIN / H-CTXLIFT2 (content-first)",
    "l_eff_alone_insufficient": True,
    "content_bars_required": True,
    "modes_visible_required": True,
    "long_cite_howto_pack": True,
    "honest_abstain_when_missing": True,
    "bf4_gate": (
        "H-CTXBF PROMOTE only if content_ok + no new intent FP "
        "(incl BF-FOREVER) + p50/p99 published + modes visible"
    ),
}

BF0_UTIL_TRACK: Mapping[str, object] = {
    "stage": "BF2 H-SHIPUSE2 executes; BF0 freezes Track A+ checklist",
    "known_ask_hitl": True,
    "ship_surface_doc": True,
    "paper_archive": True,
    "operator_card": True,
    "claim_matches_live": True,
    "gpt_claim_forbidden": True,
    "modes_visible_required": True,
    "h_shipuse_hold": True,
    "checklist": [
        "demo smoke: npm run nano:z:ask -- --wrap --semwrap",
        "RECIPES + champion-card operator sync",
        "paper:build claim = selective retriever + refuse ≤5M",
        "modes always LOOKUP|PEAK|DECODE|ABSTAIN",
        "H-SHIPUSE hold; deepen operator path + live smoke",
    ],
    "path": "nano:z:ask --wrap --semwrap",
    "bf2_gate": "Track A+ done before utilization PROMOTE (H-SHIPUSE2)",
}

BF0_SCOREBOARD: Mapping[str, object] = {
    "stage": "BF1 H-PREDINT closes bars; BF0 freezes §1 scoreboard",
    "cite_be_locks": sorted(BF0_CITED_BE_LOCKS),
    "accept_artifact": (
        "AF+AQ+AS trust + STRICT ablated DECODE (BE H-COMPINT·H-SHIPUSE·"
        "H-FASTBE·H-CTXBE); NANOGEN6·7 HOLD · NANOGEN8…15 DEFER; "
        "not TAC unlocked"
    ),
    "debts": [
        {
            "id": "bf_forever_false_hit_zero",
            "evidence": "Live FP: returns True if a is even → def add LOOKUP",
            "fix": "BF-FOREVER predicate FH 0 via schema/arity gate",
            "bar": "bf_forever_false_hit_max=0",
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
            "id": "bd_forever_hold_zero",
            "evidence": "BD reverse≠f-string · mul≠add FH 0 must hold",
            "fix": "BD-FOREVER regression hold",
            "bar": "bd_forever_false_hit_max=0",
        },
        {
            "id": "be_forever_hold_zero",
            "evidence": "BE str→int / type-coercion FH 0 must hold",
            "fix": "BE-FOREVER regression hold",
            "bar": "be_forever_false_hit_max=0",
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
            "fix": "live nano:z:ask on BF+BA…BE+AZ + ≥10 novel probes",
            "bar": "live_ask_scored True",
        },
        {
            "id": "speed_baseline_publish",
            "evidence": "BE FASTBE p50/p99 republished at BF0",
            "fix": "BF3 measures prod wall without FP regress",
            "bar": "speed_baseline_published True",
        },
        {
            "id": "ctx_baseline_publish",
            "evidence": "content bars required; L_eff alone forbidden",
            "fix": "BF4 measures usable long/cite/howto",
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
            "id": "gen_skip_stance",
            "evidence": (
                "NANOGEN6·7 HOLD · NANOGEN8…15 DEFER; no method plan at BF0"
            ),
            "fix": "stance SKIP · CAPCHECK closed · no NANOGEN16 without plan",
            "bar": "gen_stance=skip; nanogen16_without_plan_forbidden",
        },
        {
            "id": "paraphrase_eval_rule",
            "evidence": "BF-FOREVER seeds + held-out paraphrases at eval",
            "fix": "never bank-stuff exact seed strings",
            "bar": "paraphrase_required True; bank_stuff_forbidden",
        },
        {
            "id": "utilization_track_a_plus",
            "evidence": "Track A+: demo + recipes + paper + deepen H-SHIPUSE",
            "fix": "BF2 H-SHIPUSE2 utilization checklist",
            "bar": "utilization_track_frozen True",
        },
    ],
    "metrics": [
        "bf_forever_false_hit",
        "ba_forever_false_hit",
        "bb_forever_false_hit",
        "bc_forever_false_hit",
        "bd_forever_false_hit",
        "be_forever_false_hit",
        "az_hold_false_hit",
        "overrefuse_miss",
        "live_ask_ok_fp_miss",
        "p50_wall_ms",
        "p99_wall_ms",
        "ctx_content_ok",
        "modes_visible",
        "decode_content_ok",
        "true_continue_ablated",
        "utilization_ok",
    ],
    "bars": {
        "bf_forever_false_hit_max": 0,
        "ba_forever_false_hit_max": 0,
        "bb_forever_false_hit_max": 0,
        "bc_forever_false_hit_max": 0,
        "bd_forever_false_hit_max": 0,
        "be_forever_false_hit_max": 0,
        "az_hold_false_hit_max": 0,
        "overrefuse_miss_max": 0,
        "bf_forever_min_n": 12,
        "bf_forever_classes_min": 3,
        "modes_required": list(BF0_LATENCY_PATHS),
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
        "ba_bb_bc_bd_be_pass_neq_bf_forever": True,
        "bank_stuff_forbidden": True,
        "paraphrase_required": True,
        "predicate_gate_preferred": True,
        "regression_hold": True,
        "speed_baseline_published": True,
        "ctx_baseline_published": True,
        "utilization_track_frozen": True,
        "live_ask_scored": True,
        "novel_probes_min": 10,
    },
    "baselines": {
        "ba_forever_fh": 0,
        "bb_forever_fh": 0,
        "bc_forever_fh": 0,
        "bd_forever_fh": 0,
        "be_forever_fh": 0,
        "az_heldout_fh": 0,
        "az_overrefuse_miss": 0,
        "fastbe_latency": {
            "LOOKUP": {"p50": 0.0, "p99": 0.0},
            "PEAK": {
                "p50": 0.009324998245574534,
                "p99": 0.015838620602153245,
            },
            "DECODE": {
                "p50": 10.75098400178831,
                "p99": 11.185807651199866,
            },
            "ABSTAIN": {
                "p50": 93.31420949456515,
                "p99": 126.17945601174145,
            },
        },
        "ctxbe_content": "PROMOTE",
        "nanogen6_decision": "HOLD",
        "nanogen7_decision": "HOLD",
        "nanogen8_decision": "DEFER",
        "nanogen9_decision": "DEFER",
        "nanogen10_decision": "DEFER",
        "nanogen11_decision": "DEFER",
        "nanogen12_decision": "DEFER",
        "nanogen13_decision": "DEFER",
        "nanogen14_decision": "DEFER",
        "nanogen15_decision": "DEFER",
        "be_real_eval_battery": "15/15",
        "live_audit_bf_forever_fp": (
            "returns True if a is even → def add FP observed"
        ),
        "forever_classes": [
            "predicate_boolean",
            "predicate_boolean_para",
            "predicate_schema_neighbor",
        ],
        "ship_lock": BF0_SHIP_LOCK,
    },
    "runners": [
        "nano:z:ask",
        "nano:compint",
        "nano:shipuse",
        "nano:fastbe",
        "nano:ctxbe",
        "nano:nanogen15",
        "nano:advsafe",
        "nano:metrics",
        "nano:askabstain",
        "nano:be:freeze",
    ],
    "no_reopen_unless_fail": [
        "H-COMPINT",
        "H-SHIPUSE",
        "H-FASTBE",
        "H-CTXBE",
        "H-SEMINT",
        "H-FASTGAIN",
        "H-CTXGAIN",
        "H-OPSFAM",
        "H-INTENTGEN",
        "H-REALGAIN",
        "H-PRODGEN",
        "H-ADVSAFE",
    ],
    "complete_kb_claim_forbidden": True,
}

# Forever held-out residual FP (predicate/boolean ≠ BA…BE/AZ packs).
BF0_FOREVER_ROWS: tuple[dict[str, str], ...] = (
    {
        "id": "BF-FH-01",
        "class": "predicate_boolean",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a Python function that returns True if a is even."
        ),
    },
    {
        "id": "BF-FH-02",
        "class": "predicate_boolean_para",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a function that returns whether integer a is even."
        ),
    },
    {
        "id": "BF-FH-03",
        "class": "predicate_boolean_para",
        "expect_mode": "ABSTAIN",
        "question": "Python: return True when a is an even number.",
    },
    {
        "id": "BF-FH-04",
        "class": "predicate_boolean_para",
        "expect_mode": "ABSTAIN",
        "question": (
            "How do I check if integer a is even and return a bool?"
        ),
    },
    {
        "id": "BF-FH-05",
        "class": "predicate_boolean_para",
        "expect_mode": "ABSTAIN",
        "question": (
            "Implement is_even(a) that returns True for even integers."
        ),
    },
    {
        "id": "BF-FH-06",
        "class": "predicate_schema_neighbor",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a Python function that returns True if a is odd."
        ),
    },
    {
        "id": "BF-FH-07",
        "class": "predicate_schema_neighbor",
        "expect_mode": "ABSTAIN",
        "question": (
            "Return a boolean indicating whether n is positive."
        ),
    },
    {
        "id": "BF-FH-08",
        "class": "predicate_schema_neighbor",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a function that returns True if a equals zero."
        ),
    },
    {
        "id": "BF-FH-09",
        "class": "predicate_schema_neighbor",
        "expect_mode": "ABSTAIN",
        "question": (
            "How do I test if integer a is divisible by 2 (boolean)?"
        ),
    },
    {
        "id": "BF-FH-10",
        "class": "predicate_schema_neighbor",
        "expect_mode": "ABSTAIN",
        "question": (
            "Python predicate: is a less than b? return bool only."
        ),
    },
    {
        "id": "BF-FH-11",
        "class": "predicate_schema_neighbor",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a function returning True iff a and b have same parity."
        ),
    },
    {
        "id": "BF-FH-12",
        "class": "predicate_boolean",
        "expect_mode": "ABSTAIN",
        "question": (
            "Boolean check — does integer a have remainder 0 mod 2?"
        ),
    },
)

BF0_FOREVER_PROTOCOL: Mapping[str, object] = {
    "stage": "BF1 H-PREDINT scores; BF0 freezes protocol",
    "held_out": True,
    "forever": True,
    "bank_stuff_forbidden": True,
    "paraphrase_required": True,
    "predicate_gate_preferred": True,
    "neq_ba_forever": True,
    "neq_bb_forever": True,
    "neq_bc_forever": True,
    "neq_bd_forever": True,
    "neq_be_forever": True,
    "neq_az_heldout": True,
    "intent_mismatch_is_false_hit": True,
    "predicate_mismatch_is_false_hit": True,
    "source": (
        "live residual FP (even≠add · bool/predicate/arity neighbors + paras)"
    ),
    "min_n": 12,
    "classes_min": 3,
    "required_classes": [
        "predicate_boolean",
        "predicate_boolean_para",
        "predicate_schema_neighbor",
    ],
    "scoring": "false-hit rate on default ask path (mismatch → ABSTAIN)",
    "path": "nano:z:ask --wrap --semwrap",
    "pack_pass_neq_forever": True,
    "ba_bb_bc_bd_be_pass_neq_bf_forever": True,
    "live_fp_id": "BF-FH-01",
    "rows": list(BF0_FOREVER_ROWS),
}

BF0_BA_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BF1 must hold BA bars; BF0 freezes regression pack",
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

BF0_BB_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BF1 must hold BB bars; BF0 freezes regression pack",
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

BF0_BC_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BF1 must hold BC bars; BF0 freezes regression pack",
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

BF0_BD_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BF1 must hold BD bars; BF0 freezes regression pack",
    "source": "BD0_FOREVER_ROWS",
    "heldout_n": len(BD0_FOREVER_ROWS),
    "forever_false_hit_max": 0,
    "required_classes": [
        "semantic_reverse",
        "semantic_mul",
        "wrong_bank_neighbor",
    ],
    "path": "nano:z:ask --wrap --semwrap",
    "regression_hold": True,
}

BF0_BE_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BF1 must hold BE bars; BF0 freezes regression pack",
    "source": "BE0_FOREVER_ROWS",
    "heldout_n": len(BE0_FOREVER_ROWS),
    "forever_false_hit_max": 0,
    "required_classes": [
        "type_coercion",
        "type_coercion_para",
        "type_schema_neighbor",
    ],
    "path": "nano:z:ask --wrap --semwrap",
    "regression_hold": True,
}

BF0_AZ_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BF1 must hold AZ bars; BF0 freezes regression pack",
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

BF0_REAL_EVAL_PROTOCOL: Mapping[str, object] = {
    "live_ask_battery": True,
    "summary_only_forbidden": True,
    "product_mode_required": True,
    "wall_ms_n_new_mandatory": True,
    "wall_ms_n_new_insufficient_for_decode_quality": True,
    "lookup_neq_iq": True,
    "peak_neq_open_chat": True,
    "safe_neq_quality": True,
    "intent_mismatch_is_false_hit": True,
    "predicate_mismatch_is_false_hit": True,
    "type_coercion_mismatch_is_false_hit": True,
    "exact_gold_abstain_is_miss": True,
    "gold_substring_neq_gen": True,
    "gibberish_tail_fails": True,
    "span_fallback_neq_gen": True,
    "pack_pass_neq_forever": True,
    "ba_bb_bc_bd_be_pass_neq_bf_forever": True,
    "eval_eq_prod_ask": True,
    "answer_usability_scored": True,
    "utilization_scored": True,
    "novel_probes_min": 10,
    "score_labels": ["OK", "FP", "MISS", "ABSTAIN-OK"],
    "gen_claim_rule": (
        "only if BF5 H-NANOGEN16 PROMOTE (true_continue; "
        "written M1|M2|M3 plan; never NANOGEN15+rename; "
        "span-fallback ≠ gen) — else SKIP gen claim"
    ),
    "mini_agi_rule": (
        "forbidden while gen stance skip or NANOGEN16 SKIP/HOLD/DEFER"
    ),
    "stage": "BF6 BF-REAL-EVAL scores; BF0 freezes protocol",
}

BF0_ASK_BATTERY: tuple[dict[str, str], ...] = (
    {
        "id": "BF-ASK-01",
        "kind": "known_lookup",
        "expect_mode": "LOOKUP",
        "question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
    },
    {
        "id": "BF-ASK-02",
        "kind": "ood_abstain",
        "expect_mode": "ABSTAIN",
        "question": "Who won the 2022 FIFA World Cup?",
    },
    {
        "id": "BF-ASK-03",
        "kind": "near_miss",
        "expect_mode": "ABSTAIN",
        "question": (
            "BIP-39 entropy formula is CS = ENT / 32 — confirm for "
            "SegWit witness discount?"
        ),
    },
    {
        "id": "BF-ASK-04",
        "kind": "labeled_peak",
        "expect_mode": "PEAK",
        "question": (
            "From the curated Rust book intro, extract one sentence "
            "on ownership (label PEAK, not open chat)."
        ),
    },
    {
        "id": "BF-ASK-05",
        "kind": "decode_content",
        "expect_mode": "DECODE",
        "question": "Explain Merkle trees briefly",
    },
    {
        "id": "BF-ASK-06",
        "kind": "junk_trap",
        "expect_mode": "ABSTAIN",
        "question": ".",
    },
    {
        "id": "BF-ASK-07",
        "kind": "bf_forever_predicate_fp",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a Python function that returns True if a is even."
        ),
    },
    {
        "id": "BF-ASK-08",
        "kind": "overrefuse_gold",
        "expect_mode": "LOOKUP",
        "question": "Remove all items from list `a` — one method call.",
    },
    {
        "id": "BF-ASK-09",
        "kind": "az_hold_div",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named div that returns "
            "the quotient of two integers a and b."
        ),
    },
    {
        "id": "BF-ASK-10",
        "kind": "ba_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named pow2 that returns "
            "a raised to the power of b for two integers."
        ),
    },
    {
        "id": "BF-ASK-11",
        "kind": "bb_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named min2 that returns "
            "the smaller of two integers a and b."
        ),
    },
    {
        "id": "BF-ASK-12",
        "kind": "bc_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a Python function floordiv(a, b) that returns a // b."
        ),
    },
    {
        "id": "BF-ASK-13",
        "kind": "bd_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": "How do I reverse a string in Python?",
    },
    {
        "id": "BF-ASK-14",
        "kind": "be_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": "How do I convert string s to integer in Python?",
    },
    {
        "id": "BF-ASK-15",
        "kind": "bf_forever_neighbor_fp",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a Python function that returns True if a is odd."
        ),
    },
    {
        "id": "BF-ASK-16",
        "kind": "utilization_smoke",
        "expect_mode": "LOOKUP",
        "question": "How do I append x to list a in one Python method call?",
    },
)


def map_bf_product_mode(raw_mode: str) -> str:
    """
    GIVEN raw telemetry mode string
    WHEN applying BF0 mode charter (inherits AU0 aliases)
    THEN return LOOKUP | PEAK | DECODE | ABSTAIN | UNKNOWN.
    """
    return map_au_product_mode(raw_mode)


def _gate_modes() -> str | None:
    if set(BF0_LATENCY_PATHS) != BF0_MODES:
        return "KILL (latency paths ≠ mode charter)"
    if "ABSTAIN" not in BF0_MODES:
        return "KILL (ABSTAIN missing from modes)"
    return None


def _gate_cited_be() -> str | None:
    cited = BF0_SCOREBOARD.get("cite_be_locks")
    if not isinstance(cited, list):
        return "KILL (scoreboard must cite BE locks)"
    if set(cited) != BF0_CITED_BE_LOCKS:
        return "KILL (scoreboard BE lock citations incomplete)"
    return None


def _gate_debt_ids() -> str | None:
    debts = BF0_SCOREBOARD.get("debts")
    if not isinstance(debts, list) or len(debts) < 15:
        return "KILL (scoreboard must list ≥15 post-BE debts)"
    ids = {str(d.get("id", "")) for d in debts if isinstance(d, dict)}
    need = {
        "bf_forever_false_hit_zero",
        "ba_forever_hold_zero",
        "bb_forever_hold_zero",
        "bc_forever_hold_zero",
        "bd_forever_hold_zero",
        "be_forever_hold_zero",
        "az_hold_zero",
        "overrefuse_exact_gold",
        "live_ask_scoreboard",
        "speed_baseline_publish",
        "ctx_baseline_publish",
        "mode_ui_always",
        "decode_content_law",
        "gen_skip_stance",
        "paraphrase_eval_rule",
        "utilization_track_a_plus",
    }
    if not need.issubset(ids):
        return "KILL (scoreboard debt ids incomplete)"
    return None


def _gate_debt_bar_nums(bars: Mapping[str, object]) -> str | None:
    checks = (
        ("bf_forever_false_hit_max", 0, "bf_forever_false_hit_max must be 0"),
        ("ba_forever_false_hit_max", 0, "ba_forever_false_hit_max must be 0"),
        ("bb_forever_false_hit_max", 0, "bb_forever_false_hit_max must be 0"),
        ("bc_forever_false_hit_max", 0, "bc_forever_false_hit_max must be 0"),
        ("bd_forever_false_hit_max", 0, "bd_forever_false_hit_max must be 0"),
        ("be_forever_false_hit_max", 0, "be_forever_false_hit_max must be 0"),
        ("az_hold_false_hit_max", 0, "az_hold_false_hit_max must be 0"),
        ("overrefuse_miss_max", 0, "overrefuse_miss_max must be 0"),
    )
    for key, want, msg in checks:
        if int(bars.get(key, 1 if want == 0 else -1)) != want:
            return f"KILL ({msg})"
    if int(bars.get("bf_forever_min_n", 0)) < 12:
        return "KILL (bf_forever_min_n must be ≥12)"
    if int(bars.get("bf_forever_classes_min", 0)) < 3:
        return "KILL (bf_forever_classes_min must be ≥3)"
    if int(bars.get("novel_probes_min", 0)) < 10:
        return "KILL (novel_probes_min must be ≥10)"
    return None


def _gate_debt_bar_flags(bars: Mapping[str, object]) -> str | None:
    flags = (
        ("decode_gibberish_neq_content_ok", "KILL (DECODE gibberish≠content_ok)"),
        ("eval_eq_prod_ask", "KILL (eval path must equal prod ask path)"),
        ("pack_pass_neq_forever", "KILL (pack PASS ≠ forever bar missing)"),
        (
            "ba_bb_bc_bd_be_pass_neq_bf_forever",
            "KILL (BA…BE PASS ≠ BF forever bar missing)",
        ),
        ("bank_stuff_forbidden", "KILL (scoreboard must forbid bank stuffing)"),
        ("paraphrase_required", "KILL (scoreboard must require paraphrases)"),
        (
            "predicate_gate_preferred",
            "KILL (scoreboard must prefer predicate gate)",
        ),
        ("regression_hold", "KILL (scoreboard must require regression_hold)"),
        ("speed_baseline_published", "KILL (speed baseline must be published)"),
        ("ctx_baseline_published", "KILL (ctx baseline must be published)"),
        ("utilization_track_frozen", "KILL (utilization track must be frozen)"),
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
    if not isinstance(modes, list) or set(modes) != BF0_MODES:
        return "KILL (scoreboard modes_required incomplete)"
    return None


def _gate_debt_bars() -> str | None:
    bars = BF0_SCOREBOARD.get("bars")
    if not isinstance(bars, dict):
        return "KILL (scoreboard bars missing)"
    return _gate_debt_bar_nums(bars) or _gate_debt_bar_flags(bars)


def _gate_debt_metrics() -> str | None:
    metrics = BF0_SCOREBOARD.get("metrics")
    need_m = {
        "bf_forever_false_hit",
        "ba_forever_false_hit",
        "bb_forever_false_hit",
        "bc_forever_false_hit",
        "bd_forever_false_hit",
        "be_forever_false_hit",
        "az_hold_false_hit",
        "overrefuse_miss",
        "p50_wall_ms",
        "p99_wall_ms",
        "ctx_content_ok",
        "true_continue_ablated",
        "utilization_ok",
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
        + list(BD0_FOREVER_ROWS)
        + list(BE0_FOREVER_ROWS)
        + list(AZ0_HELDOUT_FP_ROWS)
        + list(AZ0_OVERREFUSE_ROWS)
    )
    return {str(p.get("question", "")).strip() for p in rows}


def _gate_fh_rows() -> str | None:
    ids: set[str] = set()
    classes: set[str] = set()
    prior = _prior_questions()
    for item in BF0_FOREVER_ROWS:
        tid = str(item.get("id", ""))
        if not tid.startswith("BF-FH-"):
            return f"KILL (bad forever id: {tid})"
        if tid in ids:
            return f"KILL (duplicate forever id: {tid})"
        ids.add(tid)
        q = str(item.get("question", "")).strip()
        if not q:
            return f"KILL (empty forever question: {tid})"
        if q in prior:
            return f"KILL (forever reuses BA…BE/AZ held-out: {tid})"
        if str(item.get("expect_mode", "")) != "ABSTAIN":
            return f"KILL (forever expect_mode must be ABSTAIN: {tid})"
        classes.add(str(item.get("class", "")))
    need = {
        "predicate_boolean",
        "predicate_boolean_para",
        "predicate_schema_neighbor",
    }
    if not need.issubset(classes):
        return "KILL (forever classes incomplete)"
    live = str(BF0_FOREVER_ROWS[0].get("question", "")).lower()
    if "even" not in live or "true" not in live:
        return "KILL (BF-FH-01 must be live even≠add residual)"
    return None


def _gate_forever_flags(proto: Mapping[str, object]) -> str | None:
    flags = (
        ("held_out", "KILL (forever must be held-out)"),
        ("forever", "KILL (forever flag missing)"),
        ("bank_stuff_forbidden", "KILL (forever must forbid bank stuffing)"),
        ("paraphrase_required", "KILL (forever must require paraphrases)"),
        (
            "predicate_gate_preferred",
            "KILL (forever must prefer predicate gate)",
        ),
        ("neq_ba_forever", "KILL (forever must ≠ BA-FOREVER)"),
        ("neq_bb_forever", "KILL (forever must ≠ BB-FOREVER)"),
        ("neq_bc_forever", "KILL (forever must ≠ BC-FOREVER)"),
        ("neq_bd_forever", "KILL (forever must ≠ BD-FOREVER)"),
        ("neq_be_forever", "KILL (forever must ≠ BE-FOREVER)"),
        ("neq_az_heldout", "KILL (forever must ≠ AZ held-out)"),
        (
            "intent_mismatch_is_false_hit",
            "KILL (forever must mark mismatch as false-hit)",
        ),
        (
            "predicate_mismatch_is_false_hit",
            "KILL (forever must mark predicate mismatch as false-hit)",
        ),
        (
            "pack_pass_neq_forever",
            "KILL (forever must mark pack PASS ≠ forever)",
        ),
        (
            "ba_bb_bc_bd_be_pass_neq_bf_forever",
            "KILL (forever must mark BA…BE PASS ≠ BF forever)",
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
    if len(BF0_FOREVER_ROWS) < min_n:
        return "KILL (BF0_FOREVER_ROWS below min_n)"
    if str(proto.get("live_fp_id", "")) != "BF-FH-01":
        return "KILL (forever must pin live_fp_id=BF-FH-01)"
    req = proto.get("required_classes")
    if not isinstance(req, list) or len(req) < 3:
        return "KILL (forever required_classes incomplete)"
    return _gate_fh_rows()


def _gate_forever() -> str | None:
    return _gate_forever_flags(BF0_FOREVER_PROTOCOL) or _gate_forever_sizes(
        BF0_FOREVER_PROTOCOL
    )


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
    if int(proto.get("heldout_n", 0)) < min_n:
        return f"KILL ({label} must cite ≥{min_n} forever rows)"
    req = proto.get("required_classes")
    if not isinstance(req, list) or not need.issubset(set(req)):
        return f"KILL ({label} required_classes incomplete)"
    return None


def _gate_holds() -> str | None:
    packs = (
        (
            BF0_BA_HOLD_PROTOCOL,
            "BA hold",
            15,
            {"ops_pow", "ops_mod", "ops_max", "list_sort", "list_len"},
        ),
        (
            BF0_BB_HOLD_PROTOCOL,
            "BB hold",
            15,
            {"ops_min", "ops_xor", "ops_absdiff", "ops_and", "ops_or"},
        ),
        (
            BF0_BC_HOLD_PROTOCOL,
            "BC hold",
            18,
            {
                "ops_floordiv",
                "ops_neg",
                "ops_gcd",
                "ops_lshift",
                "ops_rshift",
                "ops_nand",
            },
        ),
        (
            BF0_BD_HOLD_PROTOCOL,
            "BD hold",
            12,
            {"semantic_reverse", "semantic_mul", "wrong_bank_neighbor"},
        ),
        (
            BF0_BE_HOLD_PROTOCOL,
            "BE hold",
            12,
            {
                "type_coercion",
                "type_coercion_para",
                "type_schema_neighbor",
            },
        ),
    )
    for proto, label, min_n, need in packs:
        err = _gate_hold_pack(
            proto=proto, label=label, min_n=min_n, need=need
        )
        if err:
            return err
    az = BF0_AZ_HOLD_PROTOCOL
    if int(az.get("heldout_false_hit_max", 1)) != 0:
        return "KILL (AZ heldout_false_hit_max must be 0)"
    if int(az.get("overrefuse_miss_max", 1)) != 0:
        return "KILL (AZ overrefuse_miss_max must be 0)"
    if not bool(az.get("regression_hold")):
        return "KILL (AZ must require regression_hold)"
    if int(az.get("heldout_n", 0)) < 12:
        return "KILL (AZ must cite ≥12 held-out rows)"
    if int(az.get("overrefuse_n", 0)) < 3:
        return "KILL (AZ must cite ≥3 over-refuse rows)"
    return None


def _gate_baselines() -> str | None:
    paths = BF0_SPEED_BASELINE.get("paths")
    if not isinstance(paths, dict) or set(paths) != BF0_MODES:
        return "KILL (speed baseline paths incomplete)"
    if not bool(BF0_SPEED_BASELINE.get("quality_regress_forbidden")):
        return "KILL (speed must forbid quality regress)"
    if "FASTBE" not in str(BF0_SPEED_BASELINE.get("source", "")):
        return "KILL (speed baseline must cite H-FASTBE)"
    if not bool(BF0_CTX_BASELINE.get("l_eff_alone_insufficient")):
        return "KILL (ctx must forbid L_eff alone)"
    if not bool(BF0_CTX_BASELINE.get("content_bars_required")):
        return "KILL (ctx must require content bars)"
    if "CTXBF" not in str(BF0_CTX_BASELINE.get("bf4_gate", "")):
        return "KILL (ctx gate must name H-CTXBF)"
    return None


def _gate_util() -> str | None:
    if not bool(BF0_UTIL_TRACK.get("gpt_claim_forbidden")):
        return "KILL (util must forbid GPT claim)"
    if not bool(BF0_UTIL_TRACK.get("known_ask_hitl")):
        return "KILL (util must require known-ask HITL)"
    checklist = BF0_UTIL_TRACK.get("checklist")
    if not isinstance(checklist, list) or len(checklist) < 4:
        return "KILL (util checklist incomplete)"
    if "SHIPUSE2" not in str(BF0_UTIL_TRACK.get("bf2_gate", "")):
        return "KILL (util gate must name H-SHIPUSE2)"
    return None


def _gate_gen_stance() -> str | None:
    if str(BF0_GEN_STANCE.get("stance", "")) != "skip":
        return "KILL (gen stance must be skip at BF0)"
    allowed = BF0_GEN_STANCE.get("allowed_stances")
    if not isinstance(allowed, list) or set(allowed) != {
        "M1",
        "M2",
        "M3",
        "skip",
    }:
        return "KILL (allowed_stances must be M1|M2|M3|skip)"
    if bool(BF0_GEN_STANCE.get("method_plan_attached")):
        return "KILL (no method plan attached at BF0 — stance must stay skip)"
    if str(BF0_GEN_STANCE.get("capcheck", "")) != "closed":
        return "KILL (CAPCHECK must stay closed)"
    if str(BF0_GEN_STANCE.get("named_hyp", "")) != "H-NANOGEN16":
        return "KILL (named_hyp must be H-NANOGEN16)"
    if str(BF0_GEN_STANCE.get("named_predint", "")) != "H-PREDINT":
        return "KILL (named_predint must be H-PREDINT)"
    if not bool(BF0_GEN_STANCE.get("nanogen16_without_plan_forbidden")):
        return "KILL (NANOGEN16 without plan must be forbidden)"
    if not bool(BF0_GEN_STANCE.get("skip_gen_stop_rule")):
        return "KILL (skip gen stop rule required)"
    methods = BF0_GEN_STANCE.get("method_candidates")
    if not isinstance(methods, dict) or set(methods) != {"M1", "M2", "M3"}:
        return "KILL (method_candidates must name M1|M2|M3)"
    return None


def _gate_gen_judge() -> str | None:
    judge = BF0_TRUE_GEN_JUDGE
    if not bool(judge.get("span_fallback_neq_gen")):
        return "KILL (span-fallback ≠ gen required)"
    if not bool(judge.get("nanogen16_without_plan_forbidden")):
        return "KILL (judge must forbid NANOGEN16 without plan)"
    if "true_continue" not in str(judge.get("scoring", "")):
        return "KILL (judge scoring must cite true_continue)"
    return None


def _gate_real_eval() -> str | None:
    proto = BF0_REAL_EVAL_PROTOCOL
    flags = (
        "live_ask_battery",
        "summary_only_forbidden",
        "wall_ms_n_new_mandatory",
        "eval_eq_prod_ask",
        "intent_mismatch_is_false_hit",
        "predicate_mismatch_is_false_hit",
        "exact_gold_abstain_is_miss",
        "gold_substring_neq_gen",
        "gibberish_tail_fails",
        "span_fallback_neq_gen",
        "pack_pass_neq_forever",
        "ba_bb_bc_bd_be_pass_neq_bf_forever",
        "utilization_scored",
    )
    for key in flags:
        if not bool(proto.get(key)):
            return f"KILL (real-eval missing {key})"
    if int(proto.get("novel_probes_min", 0)) < 10:
        return "KILL (real-eval novel_probes_min must be ≥10)"
    labels = proto.get("score_labels")
    need = {"OK", "FP", "MISS", "ABSTAIN-OK"}
    if not isinstance(labels, list) or not need.issubset(set(labels)):
        return "KILL (real-eval score_labels incomplete)"
    claim = str(proto.get("gen_claim_rule", "")).lower()
    if "nanogen16" not in claim or "skip" not in claim:
        return "KILL (gen_claim_rule must gate NANOGEN16 / SKIP)"
    return None


def _gate_notes() -> str | None:
    if "≠" not in BF0_SAFE_NOTE:
        return "KILL (SAFE note must contrast ≠)"
    if "LOOKUP" not in BF0_ANTI_FP:
        return "KILL (anti-FP must mention LOOKUP)"
    if "eval path = prod" not in BF0_ANTI_FP.lower():
        return "KILL (anti-FP must require eval=prod)"
    if "NANOGEN16" not in BF0_ANTI_FP and "nanogen16" not in BF0_ANTI_FP.lower():
        return "KILL (anti-FP must cite NANOGEN16)"
    if "≤5M" not in BF0_NORTH_STAR:
        return "KILL (north star must cite ≤5M)"
    if "skip" not in BF0_NORTH_STAR.lower():
        return "KILL (north star must cite SKIP)"
    if "gibberish-tail" not in BF0_SHIP_LOCK:
        return "KILL (ship lock must cite gibberish-tail)"
    if "TAC" not in BF0_SHIP_LOCK:
        return "KILL (ship lock must cite TAC)"
    return None


def _gate_battery(rows: Sequence[Mapping[str, str]]) -> str | None:
    if len(rows) < 4:
        return "KILL (ask battery too small)"
    modes = {str(p.get("expect_mode", "")) for p in rows}
    if modes != BF0_MODES:
        return "KILL (ask battery must cover all product modes)"
    kinds = {str(p.get("kind", "")) for p in rows}
    need = {
        "near_miss",
        "bf_forever_predicate_fp",
        "bf_forever_neighbor_fp",
        "be_forever_hold",
        "bd_forever_hold",
        "ba_forever_hold",
        "bb_forever_hold",
        "bc_forever_hold",
        "overrefuse_gold",
        "az_hold_div",
        "labeled_peak",
        "junk_trap",
        "decode_content",
        "utilization_smoke",
    }
    if not need.issubset(kinds):
        return "KILL (ask battery kinds incomplete)"
    ids = [str(p.get("id", "")) for p in rows]
    if len(ids) != len(set(ids)):
        return "KILL (ask battery duplicate ids)"
    if not all(i.startswith("BF-ASK-") for i in ids):
        return "KILL (ask battery ids must start with BF-ASK-)"
    return None


def _gate_charters() -> str | None:
    return (
        _gate_modes()
        or _gate_cited_be()
        or _gate_scoreboard()
        or _gate_forever()
        or _gate_holds()
        or _gate_baselines()
        or _gate_util()
        or _gate_gen_stance()
        or _gate_gen_judge()
        or _gate_real_eval()
        or _gate_notes()
    )


def decide_bf0_session(
    *,
    trials_dir_ready: bool,
    anti_fp_signed: bool,
    battery: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN BF-FOREVER/BA…BE/AZ-hold/util/scoreboard/gen-SKIP/real-eval + trials
    WHEN applying BF0 SESSION gate
    THEN PROMOTE iff BE locks cited, stance=skip, battery covers 4 modes,
         util track frozen, trials ready, anti-FP signed.
    """
    rows = list(battery) if battery is not None else list(BF0_ASK_BATTERY)
    err = _gate_charters() or _gate_battery(rows)
    if err:
        return err
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-bf/trials/ not ready)"
    return f"PROMOTE ({BF0_ID}: {BF0_THESIS})"
