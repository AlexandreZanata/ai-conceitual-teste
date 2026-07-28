"""Wave BE0 SESSION: freeze BE-FOREVER · BA…BD/AZ hold · util · gen-defer."""

from __future__ import annotations

from typing import Mapping, Sequence

from au_session_ops import AU0_MODES, map_au_product_mode
from az_session_ops import AZ0_HELDOUT_FP_ROWS, AZ0_OVERREFUSE_ROWS
from ba_session_ops import BA0_FOREVER_ROWS, BA0_SHIP_LOCK
from bb_session_ops import BB0_FOREVER_ROWS
from bc_session_ops import BC0_FOREVER_ROWS
from bd_session_ops import BD0_FOREVER_ROWS, BD0_SPEED_BASELINE

__all__ = [
    "BE0_ID",
    "BE0_THESIS",
    "BE0_MODES",
    "BE0_LATENCY_PATHS",
    "BE0_CITED_BD_LOCKS",
    "BE0_SCOREBOARD",
    "BE0_FOREVER_PROTOCOL",
    "BE0_FOREVER_ROWS",
    "BE0_BA_HOLD_PROTOCOL",
    "BE0_BB_HOLD_PROTOCOL",
    "BE0_BC_HOLD_PROTOCOL",
    "BE0_BD_HOLD_PROTOCOL",
    "BE0_AZ_HOLD_PROTOCOL",
    "BE0_CTX_BASELINE",
    "BE0_SPEED_BASELINE",
    "BE0_UTIL_TRACK",
    "BE0_GEN_STANCE",
    "BE0_TRUE_GEN_JUDGE",
    "BE0_REAL_EVAL_PROTOCOL",
    "BE0_ASK_BATTERY",
    "BE0_SAFE_NOTE",
    "BE0_ANTI_FP",
    "BE0_NORTH_STAR",
    "BE0_SHIP_LOCK",
    "map_be_product_mode",
    "decide_be0_session",
]

BE0_ID = "BE0-SESSION"
BE0_THESIS = (
    "Wave BE ACTIVE: freeze BE-FOREVER (type/coercion str→int≠add + "
    "paraphrases · type-schema neighbors) · BA/BB/BC/BD-FOREVER hold · "
    "AZ hold · §1 anti-FP scoreboard · Track A utilization · ctx/speed "
    "baselines from BD · gen stance = defer once (M1|M2|M3|defer; "
    "H-NANOGEN15; not NANOGEN14+rename) · real-eval; next BE1 H-COMPINT "
    "(not CTX/SMART/FAST clone)"
)

BE0_MODES: frozenset[str] = AU0_MODES
BE0_LATENCY_PATHS: tuple[str, ...] = (
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
)

BE0_CITED_BD_LOCKS: frozenset[str] = frozenset(
    {
        "H-SEMINT",
        "H-FASTGAIN",
        "H-CTXGAIN",
        "H-NANOGEN14",
        "BD-REAL-EVAL",
        "BD-FREEZE",
    }
)

BE0_SHIP_LOCK = BA0_SHIP_LOCK

BE0_NORTH_STAR = (
    "Nano generative / mini-AGI-inspired ≤5M: compositional anti-FP "
    "(BE-FOREVER FH 0 + BA…BD forever hold + AZ hold + novel probes) + "
    "ship/utilize proven AF+AQ+AS stack + measurable context & speed + "
    "one honest generative method (M1|M2|M3) — else DEFER once; never "
    "pack theater · never LOOKUP-as-IQ · never NANOGEN15 = NANOGEN14+rename"
)

BE0_GEN_STANCE: Mapping[str, object] = {
    "stage": "BE0 freezes stance; BE5 H-NANOGEN15 applies or DEFER once",
    "stance": "defer",
    "allowed_stances": ["M1", "M2", "M3", "defer"],
    "method_candidates": {
        "M1": "teacher distill continue + anti-copy-gold loss",
        "M2": "student draft + bank/teacher rejector (hybrid)",
        "M3": "named CAPCHECK (raise params with ablations)",
    },
    "capcheck": "closed",
    "named_hyp": "H-NANOGEN15",
    "named_compint": "H-COMPINT",
    "named_shipuse": "H-SHIPUSE",
    "named_fast": "H-FASTBE",
    "named_ctx": "H-CTXBE",
    "nanogen6_hold_cited": True,
    "nanogen7_hold_cited": True,
    "nanogen8_defer_cited": True,
    "nanogen9_defer_cited": True,
    "nanogen10_defer_cited": True,
    "nanogen11_defer_cited": True,
    "nanogen12_defer_cited": True,
    "nanogen13_defer_cited": True,
    "nanogen14_defer_cited": True,
    "nanogen15_rename_forbidden": True,
    "defer_once_stop_rule": True,
    "true_continue_required_for_promote": True,
    "span_fallback_neq_gen": True,
    "rationale": (
        "No real new train/data/arch method ready at BE0; "
        "NANOGEN6·7 HOLD · NANOGEN8…14 DEFER stand; CAPCHECK stays closed; "
        "prefer compositional type/schema gate (H-COMPINT) + Track A "
        "utilization (H-SHIPUSE) over vanity NANOGEN15 rename; DEFER once "
        "— do not open NANOGEN16 without written M1|M2|M3 plan; BE5 "
        "PROMOTE only under true_continue else DEFER"
    ),
    "be5_gate": "true_continue → PROMOTE else DEFER once",
}

BE0_SAFE_NOTE = (
    "SAFE / ADVSAFE false-hit score ≠ answer quality; "
    "SAFE = no wrong gold only (anti-FP); "
    "pack FH 0 ≠ forever held-out generalization; "
    "type/coercion wrong-bank LOOKUP = false-hit "
    "(str→int→def add); "
    "BA…BD forever PASS with BE-FOREVER FP = PACK THEATER; "
    "exact-gold ABSTAIN = product miss; "
    "gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE"
)

BE0_ANTI_FP = (
    "LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; "
    "never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; "
    "type/coercion LOOKUP = false-hit (BE-FOREVER str→int→add); "
    "exact-gold ABSTAIN = miss (a.clear()); "
    "BA-FOREVER pow·mod·max·sort·len FH must stay 0; "
    "BB-FOREVER min·xor·absdiff·and·or FH must stay 0; "
    "BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; "
    "BD-FOREVER reverse≠f-string · mul≠add FH must stay 0; "
    "AZ hold div·sub·BIP FH must stay 0; "
    "BA…BD PASS with BE FP = PACK THEATER; "
    "truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; "
    "eval path = prod ask path; "
    "generative bar = BE5 only under real new method; "
    "no NANOGEN15 = NANOGEN14+rename; no CTX/SMART/FAST clone; "
    "no invent Wave BF without lab-book reopen; "
    "prefer compositional gate over bank stuffing; "
    "prefer HOLD/defer over fake PROMOTE"
)

BE0_TRUE_GEN_JUDGE: Mapping[str, object] = {
    "stage": "BE5 H-NANOGEN15 applies only if stance≠defer or new method; "
    "BE0 freezes judge law",
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
    "nanogen15_rename_forbidden": True,
    "scoring": "short_answer_f1_or_hitl_true_continue_only",
    "promote_bar": "true_continue else DEFER once",
}

# H-FASTGAIN measured latency republished (speed baseline for BE3).
BE0_SPEED_BASELINE: Mapping[str, object] = {
    "source": "H-FASTGAIN / formal-hfastgain-fastgain.md (prod ask path)",
    "path": "nano:z:ask prod path",
    "unit": "wall_ms",
    "paths": {
        "LOOKUP": {"p50": 0.0, "p99": 0.0},
        "PEAK": {
            "p50": 0.009622501238482073,
            "p99": 0.0291081194154686,
        },
        "DECODE": {
            "p50": 10.909949502092786,
            "p99": 13.754690963978646,
        },
        "ABSTAIN": {
            "p50": 90.72191749874037,
            "p99": 119.30380412799425,
        },
    },
    "quality_regress_forbidden": True,
    "warm_cache_vanity_forbidden": True,
    "be3_gate": (
        "speed PROMOTE only if §1 anti-FP bars hold (incl BE-FOREVER)"
    ),
    "parent_bd0_baseline_cited": True,
    "parent_bd0_paths": dict(BD0_SPEED_BASELINE["paths"]),  # type: ignore[arg-type]
}

BE0_CTX_BASELINE: Mapping[str, object] = {
    "source": "H-CTXGAIN / H-CTXLIFT2 / H-CTXHOLD (content-first)",
    "l_eff_alone_insufficient": True,
    "content_bars_required": True,
    "modes_visible_required": True,
    "long_cite_howto_pack": True,
    "honest_abstain_when_missing": True,
    "be4_gate": (
        "H-CTXBE PROMOTE only if content_ok + no new intent FP "
        "(incl BE-FOREVER) + p50/p99 published + modes visible"
    ),
}

BE0_UTIL_TRACK: Mapping[str, object] = {
    "stage": "BE2 H-SHIPUSE executes; BE0 freezes Track A checklist",
    "known_ask_hitl": True,
    "ship_surface_doc": True,
    "paper_archive": True,
    "operator_card": True,
    "claim_matches_live": True,
    "gpt_claim_forbidden": True,
    "modes_visible_required": True,
    "checklist": [
        "demo smoke: npm run nano:z:ask -- --wrap --semwrap",
        "RECIPES + champion-card operator sync",
        "paper:build claim = selective retriever + refuse ≤5M",
        "modes always LOOKUP|PEAK|DECODE|ABSTAIN",
    ],
    "path": "nano:z:ask --wrap --semwrap",
    "be2_gate": "Track A done before utilization PROMOTE (H-SHIPUSE)",
}

BE0_SCOREBOARD: Mapping[str, object] = {
    "stage": "BE1 H-COMPINT closes bars; BE0 freezes §1 scoreboard",
    "cite_bd_locks": sorted(BE0_CITED_BD_LOCKS),
    "accept_artifact": (
        "AF+AQ+AS trust + STRICT ablated DECODE (BD H-SEMINT·H-FASTGAIN·"
        "H-CTXGAIN); NANOGEN6·7 HOLD · NANOGEN8…14 DEFER; not TAC unlocked"
    ),
    "debts": [
        {
            "id": "be_forever_false_hit_zero",
            "evidence": "Live FP: convert string s to integer → def add LOOKUP",
            "fix": "BE-FOREVER type/coercion FH 0 via compositional gate",
            "bar": "be_forever_false_hit_max=0",
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
            "fix": "live nano:z:ask on BE+BA…BD+AZ + ≥10 novel probes",
            "bar": "live_ask_scored True",
        },
        {
            "id": "speed_baseline_publish",
            "evidence": "BD FASTGAIN p50/p99 republished at BE0",
            "fix": "BE3 measures prod wall without FP regress",
            "bar": "speed_baseline_published True",
        },
        {
            "id": "ctx_baseline_publish",
            "evidence": "content bars required; L_eff alone forbidden",
            "fix": "BE4 measures usable long/cite/howto",
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
                "NANOGEN6·7 HOLD · NANOGEN8…14 DEFER; no new method at BE0"
            ),
            "fix": "stance defer once · CAPCHECK closed · no NANOGEN15 rename",
            "bar": "gen_stance=defer; nanogen15_rename_forbidden",
        },
        {
            "id": "paraphrase_eval_rule",
            "evidence": "BE-FOREVER seeds + held-out paraphrases at eval",
            "fix": "never bank-stuff exact seed strings",
            "bar": "paraphrase_required True; bank_stuff_forbidden",
        },
        {
            "id": "utilization_track_a",
            "evidence": "Track A: demo + recipes + paper claim match live",
            "fix": "BE2 H-SHIPUSE utilization checklist",
            "bar": "utilization_track_frozen True",
        },
    ],
    "metrics": [
        "be_forever_false_hit",
        "ba_forever_false_hit",
        "bb_forever_false_hit",
        "bc_forever_false_hit",
        "bd_forever_false_hit",
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
        "be_forever_false_hit_max": 0,
        "ba_forever_false_hit_max": 0,
        "bb_forever_false_hit_max": 0,
        "bc_forever_false_hit_max": 0,
        "bd_forever_false_hit_max": 0,
        "az_hold_false_hit_max": 0,
        "overrefuse_miss_max": 0,
        "be_forever_min_n": 12,
        "be_forever_classes_min": 3,
        "modes_required": list(BE0_LATENCY_PATHS),
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
        "ba_bb_bc_bd_pass_neq_be_forever": True,
        "bank_stuff_forbidden": True,
        "paraphrase_required": True,
        "compositional_gate_preferred": True,
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
        "az_heldout_fh": 0,
        "az_overrefuse_miss": 0,
        "fastgain_latency": {
            "LOOKUP": {"p50": 0.0, "p99": 0.0},
            "PEAK": {
                "p50": 0.009622501238482073,
                "p99": 0.0291081194154686,
            },
            "DECODE": {
                "p50": 10.909949502092786,
                "p99": 13.754690963978646,
            },
            "ABSTAIN": {
                "p50": 90.72191749874037,
                "p99": 119.30380412799425,
            },
        },
        "ctxgain_content": "PROMOTE",
        "nanogen6_decision": "HOLD",
        "nanogen7_decision": "HOLD",
        "nanogen8_decision": "DEFER",
        "nanogen9_decision": "DEFER",
        "nanogen10_decision": "DEFER",
        "nanogen11_decision": "DEFER",
        "nanogen12_decision": "DEFER",
        "nanogen13_decision": "DEFER",
        "nanogen14_decision": "DEFER",
        "bd_real_eval_battery": "14/14",
        "live_audit_be_forever_fp": (
            "convert string s to integer → def add FP observed"
        ),
        "forever_classes": [
            "type_coercion",
            "type_coercion_para",
            "type_schema_neighbor",
        ],
        "ship_lock": BE0_SHIP_LOCK,
    },
    "runners": [
        "nano:z:ask",
        "nano:semint",
        "nano:bd:fastgain",
        "nano:bd:ctxgain",
        "nano:nanogen14",
        "nano:advsafe",
        "nano:metrics",
        "nano:askabstain",
        "nano:bd:freeze",
    ],
    "no_reopen_unless_fail": [
        "H-SEMINT",
        "H-FASTGAIN",
        "H-CTXGAIN",
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

# Forever held-out residual FP (type/coercion ≠ BA/BB/BC/BD/AZ packs).
BE0_FOREVER_ROWS: tuple[dict[str, str], ...] = (
    {
        "id": "BE-FH-01",
        "class": "type_coercion",
        "expect_mode": "ABSTAIN",
        "question": "How do I convert string s to integer in Python?",
    },
    {
        "id": "BE-FH-02",
        "class": "type_coercion_para",
        "expect_mode": "ABSTAIN",
        "question": "Convert string s to an int in Python — one expression.",
    },
    {
        "id": "BE-FH-03",
        "class": "type_coercion_para",
        "expect_mode": "ABSTAIN",
        "question": "Parse s as an integer from a text string in Python.",
    },
    {
        "id": "BE-FH-04",
        "class": "type_coercion_para",
        "expect_mode": "ABSTAIN",
        "question": "How can I cast string s to int without using add(a, b)?",
    },
    {
        "id": "BE-FH-05",
        "class": "type_coercion_para",
        "expect_mode": "ABSTAIN",
        "question": "Python: turn text variable s into an integer value.",
    },
    {
        "id": "BE-FH-06",
        "class": "type_schema_neighbor",
        "expect_mode": "ABSTAIN",
        "question": "How do I convert integer n to a string in Python?",
    },
    {
        "id": "BE-FH-07",
        "class": "type_schema_neighbor",
        "expect_mode": "ABSTAIN",
        "question": "How do I convert float f to int in Python?",
    },
    {
        "id": "BE-FH-08",
        "class": "type_schema_neighbor",
        "expect_mode": "ABSTAIN",
        "question": "How do I convert a list to a tuple in Python?",
    },
    {
        "id": "BE-FH-09",
        "class": "type_schema_neighbor",
        "expect_mode": "ABSTAIN",
        "question": "How do I convert bytes b to a string in Python?",
    },
    {
        "id": "BE-FH-10",
        "class": "type_schema_neighbor",
        "expect_mode": "ABSTAIN",
        "question": "How do I check if string s is numeric in Python?",
    },
    {
        "id": "BE-FH-11",
        "class": "type_schema_neighbor",
        "expect_mode": "ABSTAIN",
        "question": "Python: coerce boolean flag to integer 0 or 1.",
    },
    {
        "id": "BE-FH-12",
        "class": "type_coercion",
        "expect_mode": "ABSTAIN",
        "question": (
            "I need int from string s in Python — not a sum of two ints."
        ),
    },
)

BE0_FOREVER_PROTOCOL: Mapping[str, object] = {
    "stage": "BE1 H-COMPINT scores; BE0 freezes protocol",
    "held_out": True,
    "forever": True,
    "bank_stuff_forbidden": True,
    "paraphrase_required": True,
    "compositional_gate_preferred": True,
    "neq_ba_forever": True,
    "neq_bb_forever": True,
    "neq_bc_forever": True,
    "neq_bd_forever": True,
    "neq_az_heldout": True,
    "intent_mismatch_is_false_hit": True,
    "type_coercion_mismatch_is_false_hit": True,
    "source": (
        "live residual FP (str→int≠add · type/schema neighbors + paraphrases)"
    ),
    "min_n": 12,
    "classes_min": 3,
    "required_classes": [
        "type_coercion",
        "type_coercion_para",
        "type_schema_neighbor",
    ],
    "scoring": "false-hit rate on default ask path (mismatch → ABSTAIN)",
    "path": "nano:z:ask --wrap --semwrap",
    "pack_pass_neq_forever": True,
    "ba_bb_bc_bd_pass_neq_be_forever": True,
    "live_fp_id": "BE-FH-01",
    "rows": list(BE0_FOREVER_ROWS),
}

BE0_BA_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BE1 must hold BA bars; BE0 freezes regression pack",
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

BE0_BB_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BE1 must hold BB bars; BE0 freezes regression pack",
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

BE0_BC_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BE1 must hold BC bars; BE0 freezes regression pack",
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

BE0_BD_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BE1 must hold BD bars; BE0 freezes regression pack",
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

BE0_AZ_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BE1 must hold AZ bars; BE0 freezes regression pack",
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

BE0_REAL_EVAL_PROTOCOL: Mapping[str, object] = {
    "live_ask_battery": True,
    "summary_only_forbidden": True,
    "product_mode_required": True,
    "wall_ms_n_new_mandatory": True,
    "wall_ms_n_new_insufficient_for_decode_quality": True,
    "lookup_neq_iq": True,
    "peak_neq_open_chat": True,
    "safe_neq_quality": True,
    "intent_mismatch_is_false_hit": True,
    "type_coercion_mismatch_is_false_hit": True,
    "exact_gold_abstain_is_miss": True,
    "gold_substring_neq_gen": True,
    "gibberish_tail_fails": True,
    "span_fallback_neq_gen": True,
    "pack_pass_neq_forever": True,
    "ba_bb_bc_bd_pass_neq_be_forever": True,
    "eval_eq_prod_ask": True,
    "answer_usability_scored": True,
    "utilization_scored": True,
    "novel_probes_min": 10,
    "score_labels": ["OK", "FP", "MISS", "ABSTAIN-OK"],
    "gen_claim_rule": (
        "only if BE5 H-NANOGEN15 PROMOTE (true_continue; "
        "real new method M1|M2|M3; never NANOGEN14+rename; "
        "span-fallback ≠ gen)"
    ),
    "mini_agi_rule": (
        "forbidden while gen stance defer or NANOGEN15 HOLD/DEFER"
    ),
    "stage": "BE6 BE-REAL-EVAL scores; BE0 freezes protocol",
}

BE0_ASK_BATTERY: tuple[dict[str, str], ...] = (
    {
        "id": "BE-ASK-01",
        "kind": "known_lookup",
        "expect_mode": "LOOKUP",
        "question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
    },
    {
        "id": "BE-ASK-02",
        "kind": "ood_abstain",
        "expect_mode": "ABSTAIN",
        "question": "Who won the 2022 FIFA World Cup?",
    },
    {
        "id": "BE-ASK-03",
        "kind": "near_miss",
        "expect_mode": "ABSTAIN",
        "question": (
            "BIP-39 entropy formula is CS = ENT / 32 — confirm for "
            "SegWit witness discount?"
        ),
    },
    {
        "id": "BE-ASK-04",
        "kind": "labeled_peak",
        "expect_mode": "PEAK",
        "question": (
            "From the curated Rust book intro, extract one sentence "
            "on ownership (label PEAK, not open chat)."
        ),
    },
    {
        "id": "BE-ASK-05",
        "kind": "decode_content",
        "expect_mode": "DECODE",
        "question": "Explain Merkle trees briefly",
    },
    {
        "id": "BE-ASK-06",
        "kind": "junk_trap",
        "expect_mode": "ABSTAIN",
        "question": ".",
    },
    {
        "id": "BE-ASK-07",
        "kind": "be_forever_type_fp",
        "expect_mode": "ABSTAIN",
        "question": "How do I convert string s to integer in Python?",
    },
    {
        "id": "BE-ASK-08",
        "kind": "overrefuse_gold",
        "expect_mode": "LOOKUP",
        "question": "Remove all items from list `a` — one method call.",
    },
    {
        "id": "BE-ASK-09",
        "kind": "az_hold_div",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named div that returns "
            "the quotient of two integers a and b."
        ),
    },
    {
        "id": "BE-ASK-10",
        "kind": "ba_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named pow2 that returns "
            "a raised to the power of b for two integers."
        ),
    },
    {
        "id": "BE-ASK-11",
        "kind": "bb_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named min2 that returns "
            "the smaller of two integers a and b."
        ),
    },
    {
        "id": "BE-ASK-12",
        "kind": "bc_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a Python function floordiv(a, b) that returns a // b."
        ),
    },
    {
        "id": "BE-ASK-13",
        "kind": "bd_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": "How do I reverse a string in Python?",
    },
    {
        "id": "BE-ASK-14",
        "kind": "be_forever_neighbor_fp",
        "expect_mode": "ABSTAIN",
        "question": "How do I convert integer n to a string in Python?",
    },
    {
        "id": "BE-ASK-15",
        "kind": "utilization_smoke",
        "expect_mode": "LOOKUP",
        "question": "How do I append x to list a in one Python method call?",
    },
)


def map_be_product_mode(raw_mode: str) -> str:
    """
    GIVEN raw telemetry mode string
    WHEN applying BE0 mode charter (inherits AU0 aliases)
    THEN return LOOKUP | PEAK | DECODE | ABSTAIN | UNKNOWN.
    """
    return map_au_product_mode(raw_mode)


def _gate_modes() -> str | None:
    if set(BE0_LATENCY_PATHS) != BE0_MODES:
        return "KILL (latency paths ≠ mode charter)"
    if "ABSTAIN" not in BE0_MODES:
        return "KILL (ABSTAIN missing from modes)"
    return None


def _gate_cited_bd() -> str | None:
    cited = BE0_SCOREBOARD.get("cite_bd_locks")
    if not isinstance(cited, list):
        return "KILL (scoreboard must cite BD locks)"
    if set(cited) != BE0_CITED_BD_LOCKS:
        return "KILL (scoreboard BD lock citations incomplete)"
    return None


def _gate_debt_ids() -> str | None:
    debts = BE0_SCOREBOARD.get("debts")
    if not isinstance(debts, list) or len(debts) < 14:
        return "KILL (scoreboard must list ≥14 post-BD debts)"
    ids = {str(d.get("id", "")) for d in debts if isinstance(d, dict)}
    need = {
        "be_forever_false_hit_zero",
        "ba_forever_hold_zero",
        "bb_forever_hold_zero",
        "bc_forever_hold_zero",
        "bd_forever_hold_zero",
        "az_hold_zero",
        "overrefuse_exact_gold",
        "live_ask_scoreboard",
        "speed_baseline_publish",
        "ctx_baseline_publish",
        "mode_ui_always",
        "decode_content_law",
        "gen_defer_stance",
        "paraphrase_eval_rule",
        "utilization_track_a",
    }
    if not need.issubset(ids):
        return "KILL (scoreboard debt ids incomplete)"
    return None


def _gate_debt_bar_nums(bars: Mapping[str, object]) -> str | None:
    checks = (
        ("be_forever_false_hit_max", 0, "be_forever_false_hit_max must be 0"),
        ("ba_forever_false_hit_max", 0, "ba_forever_false_hit_max must be 0"),
        ("bb_forever_false_hit_max", 0, "bb_forever_false_hit_max must be 0"),
        ("bc_forever_false_hit_max", 0, "bc_forever_false_hit_max must be 0"),
        ("bd_forever_false_hit_max", 0, "bd_forever_false_hit_max must be 0"),
        ("az_hold_false_hit_max", 0, "az_hold_false_hit_max must be 0"),
        ("overrefuse_miss_max", 0, "overrefuse_miss_max must be 0"),
    )
    for key, want, msg in checks:
        if int(bars.get(key, 1 if want == 0 else -1)) != want:
            return f"KILL ({msg})"
    if int(bars.get("be_forever_min_n", 0)) < 12:
        return "KILL (be_forever_min_n must be ≥12)"
    if int(bars.get("be_forever_classes_min", 0)) < 3:
        return "KILL (be_forever_classes_min must be ≥3)"
    if int(bars.get("novel_probes_min", 0)) < 10:
        return "KILL (novel_probes_min must be ≥10)"
    return None


def _gate_debt_bar_flags(bars: Mapping[str, object]) -> str | None:
    flags = (
        ("decode_gibberish_neq_content_ok", "KILL (DECODE gibberish≠content_ok)"),
        ("eval_eq_prod_ask", "KILL (eval path must equal prod ask path)"),
        ("pack_pass_neq_forever", "KILL (pack PASS ≠ forever bar missing)"),
        (
            "ba_bb_bc_bd_pass_neq_be_forever",
            "KILL (BA…BD PASS ≠ BE forever bar missing)",
        ),
        ("bank_stuff_forbidden", "KILL (scoreboard must forbid bank stuffing)"),
        ("paraphrase_required", "KILL (scoreboard must require paraphrases)"),
        (
            "compositional_gate_preferred",
            "KILL (scoreboard must prefer compositional gate)",
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
    if not isinstance(modes, list) or set(modes) != BE0_MODES:
        return "KILL (scoreboard modes_required incomplete)"
    return None


def _gate_debt_bars() -> str | None:
    bars = BE0_SCOREBOARD.get("bars")
    if not isinstance(bars, dict):
        return "KILL (scoreboard bars missing)"
    return _gate_debt_bar_nums(bars) or _gate_debt_bar_flags(bars)


def _gate_debt_metrics() -> str | None:
    metrics = BE0_SCOREBOARD.get("metrics")
    need_m = {
        "be_forever_false_hit",
        "ba_forever_false_hit",
        "bb_forever_false_hit",
        "bc_forever_false_hit",
        "bd_forever_false_hit",
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
        + list(AZ0_HELDOUT_FP_ROWS)
        + list(AZ0_OVERREFUSE_ROWS)
    )
    return {str(p.get("question", "")).strip() for p in rows}


def _gate_fh_rows() -> str | None:
    ids: set[str] = set()
    classes: set[str] = set()
    prior = _prior_questions()
    for item in BE0_FOREVER_ROWS:
        tid = str(item.get("id", ""))
        if not tid.startswith("BE-FH-"):
            return f"KILL (bad forever id: {tid})"
        if tid in ids:
            return f"KILL (duplicate forever id: {tid})"
        ids.add(tid)
        q = str(item.get("question", "")).strip()
        if not q:
            return f"KILL (empty forever question: {tid})"
        if q in prior:
            return f"KILL (forever reuses BA/BB/BC/BD/AZ held-out: {tid})"
        if str(item.get("expect_mode", "")) != "ABSTAIN":
            return f"KILL (forever expect_mode must be ABSTAIN: {tid})"
        classes.add(str(item.get("class", "")))
    need = {
        "type_coercion",
        "type_coercion_para",
        "type_schema_neighbor",
    }
    if not need.issubset(classes):
        return "KILL (forever classes incomplete)"
    live = str(BE0_FOREVER_ROWS[0].get("question", "")).lower()
    if "convert" not in live or "string" not in live or "integer" not in live:
        return "KILL (BE-FH-01 must be live str→int residual)"
    return None


def _gate_forever_flags(proto: Mapping[str, object]) -> str | None:
    flags = (
        ("held_out", "KILL (forever must be held-out)"),
        ("forever", "KILL (forever flag missing)"),
        ("bank_stuff_forbidden", "KILL (forever must forbid bank stuffing)"),
        ("paraphrase_required", "KILL (forever must require paraphrases)"),
        (
            "compositional_gate_preferred",
            "KILL (forever must prefer compositional gate)",
        ),
        ("neq_ba_forever", "KILL (forever must ≠ BA-FOREVER)"),
        ("neq_bb_forever", "KILL (forever must ≠ BB-FOREVER)"),
        ("neq_bc_forever", "KILL (forever must ≠ BC-FOREVER)"),
        ("neq_bd_forever", "KILL (forever must ≠ BD-FOREVER)"),
        ("neq_az_heldout", "KILL (forever must ≠ AZ held-out)"),
        (
            "intent_mismatch_is_false_hit",
            "KILL (forever must mark mismatch as false-hit)",
        ),
        (
            "type_coercion_mismatch_is_false_hit",
            "KILL (forever must mark type/coercion as false-hit)",
        ),
        (
            "pack_pass_neq_forever",
            "KILL (forever must mark pack PASS ≠ forever)",
        ),
        (
            "ba_bb_bc_bd_pass_neq_be_forever",
            "KILL (forever must mark BA…BD PASS ≠ BE forever)",
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
    if len(BE0_FOREVER_ROWS) < min_n:
        return "KILL (BE0_FOREVER_ROWS below min_n)"
    if str(proto.get("live_fp_id", "")) != "BE-FH-01":
        return "KILL (forever must pin live_fp_id=BE-FH-01)"
    req = proto.get("required_classes")
    if not isinstance(req, list) or len(req) < 3:
        return "KILL (forever required_classes incomplete)"
    return _gate_fh_rows()


def _gate_forever() -> str | None:
    proto = BE0_FOREVER_PROTOCOL
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
    if int(proto.get("heldout_n", 0)) < min_n:
        return f"KILL ({label} must cite ≥{min_n} forever rows)"
    req = proto.get("required_classes")
    if not isinstance(req, list) or not need.issubset(set(req)):
        return f"KILL ({label} required_classes incomplete)"
    return None


def _gate_ba_hold() -> str | None:
    return _gate_hold_pack(
        proto=BE0_BA_HOLD_PROTOCOL,
        label="BA hold",
        min_n=15,
        need={"ops_pow", "ops_mod", "ops_max", "list_sort", "list_len"},
    )


def _gate_bb_hold() -> str | None:
    return _gate_hold_pack(
        proto=BE0_BB_HOLD_PROTOCOL,
        label="BB hold",
        min_n=15,
        need={"ops_min", "ops_xor", "ops_absdiff", "ops_and", "ops_or"},
    )


def _gate_bc_hold() -> str | None:
    return _gate_hold_pack(
        proto=BE0_BC_HOLD_PROTOCOL,
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


def _gate_bd_hold() -> str | None:
    return _gate_hold_pack(
        proto=BE0_BD_HOLD_PROTOCOL,
        label="BD hold",
        min_n=12,
        need={"semantic_reverse", "semantic_mul", "wrong_bank_neighbor"},
    )


def _gate_az_hold() -> str | None:
    proto = BE0_AZ_HOLD_PROTOCOL
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
    paths = BE0_SPEED_BASELINE.get("paths")
    if not isinstance(paths, dict) or set(paths) != BE0_MODES:
        return "KILL (speed baseline paths incomplete)"
    if not bool(BE0_SPEED_BASELINE.get("quality_regress_forbidden")):
        return "KILL (speed baseline must forbid quality regress)"
    if "FASTGAIN" not in str(BE0_SPEED_BASELINE.get("source", "")):
        return "KILL (speed baseline must cite H-FASTGAIN)"
    if not bool(BE0_CTX_BASELINE.get("l_eff_alone_insufficient")):
        return "KILL (ctx baseline must mark L_eff alone insufficient)"
    if not bool(BE0_CTX_BASELINE.get("content_bars_required")):
        return "KILL (ctx baseline must require content bars)"
    return None


def _gate_util_track() -> str | None:
    util = BE0_UTIL_TRACK
    flags = (
        "known_ask_hitl",
        "ship_surface_doc",
        "paper_archive",
        "operator_card",
        "claim_matches_live",
        "gpt_claim_forbidden",
        "modes_visible_required",
    )
    for key in flags:
        if not bool(util.get(key)):
            return f"KILL (util track must set {key})"
    checklist = util.get("checklist")
    if not isinstance(checklist, list) or len(checklist) < 4:
        return "KILL (util track checklist incomplete)"
    if "SHIPUSE" not in str(util.get("be2_gate", "")):
        return "KILL (util track must gate H-SHIPUSE)"
    return None


def _gate_gen_stance_core() -> str | None:
    stance = str(BE0_GEN_STANCE.get("stance", ""))
    allowed = BE0_GEN_STANCE.get("allowed_stances")
    if not isinstance(allowed, list):
        return "KILL (gen stance allowed_stances missing)"
    if stance not in allowed:
        return "KILL (gen stance must be M1|M2|M3|defer)"
    if stance != "defer":
        return "KILL (BE0 gen stance must be defer until real new method)"
    if str(BE0_GEN_STANCE.get("capcheck", "")) != "closed":
        return "KILL (BE0 CAPCHECK must stay closed)"
    names = (
        ("named_hyp", "H-NANOGEN15"),
        ("named_compint", "H-COMPINT"),
        ("named_shipuse", "H-SHIPUSE"),
        ("named_fast", "H-FASTBE"),
        ("named_ctx", "H-CTXBE"),
    )
    for key, want in names:
        if str(BE0_GEN_STANCE.get(key, "")) != want:
            return f"KILL (BE0 must name {want})"
    methods = BE0_GEN_STANCE.get("method_candidates")
    if not isinstance(methods, dict) or set(methods) != {"M1", "M2", "M3"}:
        return "KILL (gen stance method_candidates incomplete)"
    return None


def _gate_gen_stance_cites() -> str | None:
    cites = (
        ("nanogen15_rename_forbidden", "KILL (forbid NANOGEN15 rename)"),
        ("defer_once_stop_rule", "KILL (cite DEFER-once stop rule)"),
        ("nanogen6_hold_cited", "KILL (cite NANOGEN6 HOLD)"),
        ("nanogen7_hold_cited", "KILL (cite NANOGEN7 HOLD)"),
        ("nanogen8_defer_cited", "KILL (cite NANOGEN8 DEFER)"),
        ("nanogen9_defer_cited", "KILL (cite NANOGEN9 DEFER)"),
        ("nanogen10_defer_cited", "KILL (cite NANOGEN10 DEFER)"),
        ("nanogen11_defer_cited", "KILL (cite NANOGEN11 DEFER)"),
        ("nanogen12_defer_cited", "KILL (cite NANOGEN12 DEFER)"),
        ("nanogen13_defer_cited", "KILL (cite NANOGEN13 DEFER)"),
        ("nanogen14_defer_cited", "KILL (cite NANOGEN14 DEFER)"),
    )
    for key, msg in cites:
        if not bool(BE0_GEN_STANCE.get(key)):
            return msg
    rat = str(BE0_GEN_STANCE.get("rationale", "")).lower()
    if "nanogen" not in rat or "defer" not in rat:
        return "KILL (gen stance rationale incomplete)"
    if "compint" not in rat and "compositional" not in rat:
        return "KILL (gen stance must prefer compositional gate)"
    return None


def _gate_gen_stance() -> str | None:
    return _gate_gen_stance_core() or _gate_gen_stance_cites()


def _gate_gen_judge() -> str | None:
    judge = BE0_TRUE_GEN_JUDGE
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
        "nanogen14_defer_archived",
        "nanogen15_rename_forbidden",
    )
    for key in flags:
        if not bool(judge.get(key)):
            return f"KILL (true judge must set {key})"
    if "true_continue" not in str(judge.get("scoring", "")):
        return "KILL (true judge scoring must be true_continue only)"
    return None


def _gate_real_eval_flags() -> str | None:
    proto = BE0_REAL_EVAL_PROTOCOL
    flags = (
        ("live_ask_battery", "KILL (real-eval must require live ask battery)"),
        ("summary_only_forbidden", "KILL (real-eval must forbid summary-only)"),
        ("wall_ms_n_new_mandatory", "KILL (real-eval must require wall_ms/n_new)"),
        ("eval_eq_prod_ask", "KILL (real-eval must require eval=prod ask)"),
        ("intent_mismatch_is_false_hit", "KILL (real-eval must mark intent FP)"),
        (
            "type_coercion_mismatch_is_false_hit",
            "KILL (real-eval must mark type/coercion FP)",
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
            "ba_bb_bc_bd_pass_neq_be_forever",
            "KILL (real-eval must mark BA…BD PASS ≠ BE forever)",
        ),
        (
            "wall_ms_n_new_insufficient_for_decode_quality",
            "KILL (real-eval must mark wall_ms/n_new insufficient for DECODE)",
        ),
        ("utilization_scored", "KILL (real-eval must score utilization)"),
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
    claim = str(BE0_REAL_EVAL_PROTOCOL.get("gen_claim_rule", "")).lower()
    if "nanogen15" not in claim:
        return "KILL (real-eval gen_claim_rule incomplete)"
    if "rename" not in claim:
        return "KILL (real-eval must forbid NANOGEN15 rename)"
    labels = BE0_REAL_EVAL_PROTOCOL.get("score_labels")
    need = {"OK", "FP", "MISS", "ABSTAIN-OK"}
    if not isinstance(labels, list) or not need.issubset(set(labels)):
        return "KILL (real-eval score_labels incomplete)"
    return None


def _scan_battery_row(
    item: Mapping[str, str], ids: set[str]
) -> tuple[str | None, str, str]:
    tid = str(item.get("id", ""))
    if not tid.startswith("BE-ASK-"):
        return f"KILL (bad battery id: {tid})", "", ""
    if tid in ids:
        return f"KILL (duplicate battery id: {tid})", "", ""
    q = str(item.get("question", ""))
    if tid != "BE-ASK-06" and not q.strip():
        return f"KILL (empty battery question: {tid})", "", ""
    mode = str(item.get("expect_mode", ""))
    if mode not in BE0_MODES:
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
    if modes_seen != BE0_MODES:
        return f"KILL (ask battery modes incomplete: {sorted(modes_seen)})"
    need_kinds = {
        "near_miss",
        "be_forever_type_fp",
        "be_forever_neighbor_fp",
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
    if not need_kinds.issubset(kinds):
        return "KILL (ask battery must cover BE scoreboard kinds)"
    return None


def _gate_safe_anti_fp() -> str | None:
    if "≠" not in BE0_SAFE_NOTE and "!=" not in BE0_SAFE_NOTE:
        return "KILL (SAFE≠quality note missing)"
    if "LOOKUP" not in BE0_ANTI_FP:
        return "KILL (anti-FP charter incomplete)"
    if "eval path = prod" not in BE0_ANTI_FP.lower():
        return "KILL (anti-FP must require eval=prod ask)"
    anti = BE0_ANTI_FP.lower()
    if "str→int" not in anti and "type/coercion" not in anti and "be-forever" not in anti:
        return "KILL (anti-FP must mark BE forever type/coercion FP)"
    if "NANOGEN15" not in BE0_ANTI_FP and "nanogen15" not in anti:
        return "KILL (anti-FP must forbid NANOGEN15 rename)"
    return None


def _gate_north_ship() -> str | None:
    if "≤5M" not in BE0_NORTH_STAR:
        return "KILL (north-star charter incomplete)"
    if "defer" not in BE0_NORTH_STAR.lower():
        return "KILL (north-star must allow HOLD/defer)"
    if "gibberish-tail" not in BE0_SHIP_LOCK:
        return "KILL (ship lock must keep STRICT gibberish-tail claim)"
    if "TAC unlocked" not in BE0_SHIP_LOCK and "not TAC" not in BE0_SHIP_LOCK:
        return "KILL (ship lock must state not TAC unlocked)"
    return None


def _gate_notes() -> str | None:
    return _gate_safe_anti_fp() or _gate_north_ship()


def _gate_charters() -> str | None:
    return (
        _gate_modes()
        or _gate_cited_bd()
        or _gate_scoreboard()
        or _gate_forever()
        or _gate_ba_hold()
        or _gate_bb_hold()
        or _gate_bc_hold()
        or _gate_bd_hold()
        or _gate_az_hold()
        or _gate_baselines()
        or _gate_util_track()
        or _gate_gen_stance()
        or _gate_gen_judge()
        or _gate_real_eval()
        or _gate_notes()
    )


def decide_be0_session(
    *,
    trials_dir_ready: bool,
    anti_fp_signed: bool,
    battery: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN BE-FOREVER/BA…BD/AZ-hold/util/scoreboard/gen-defer/real-eval + trials
    WHEN applying BE0 SESSION gate
    THEN PROMOTE iff BD locks cited, stance=defer, battery covers 4 modes,
         util track frozen, trials ready, anti-FP signed.
    """
    rows = list(battery) if battery is not None else list(BE0_ASK_BATTERY)
    err = _gate_charters() or _gate_battery(rows)
    if err:
        return err
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-be/trials/ not ready)"
    return f"PROMOTE ({BE0_ID}: {BE0_THESIS})"
