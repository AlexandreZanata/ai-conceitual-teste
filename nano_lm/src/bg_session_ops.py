"""Wave BG0 SESSION: freeze BG-FOREVER · BA…BF/AZ hold · util · gen-SKIP."""

from __future__ import annotations

from typing import Mapping, Sequence

from au_session_ops import AU0_MODES, map_au_product_mode
from az_session_ops import AZ0_HELDOUT_FP_ROWS, AZ0_OVERREFUSE_ROWS
from ba_session_ops import BA0_FOREVER_ROWS
from bb_session_ops import BB0_FOREVER_ROWS
from bc_session_ops import BC0_FOREVER_ROWS
from bd_session_ops import BD0_FOREVER_ROWS
from be_session_ops import BE0_FOREVER_ROWS
from bf_session_ops import BF0_FOREVER_ROWS, BF0_SHIP_LOCK, BF0_SPEED_BASELINE

__all__ = [
    "BG0_ID",
    "BG0_THESIS",
    "BG0_MODES",
    "BG0_LATENCY_PATHS",
    "BG0_CITED_BF_LOCKS",
    "BG0_SCOREBOARD",
    "BG0_FOREVER_PROTOCOL",
    "BG0_FOREVER_ROWS",
    "BG0_BA_HOLD_PROTOCOL",
    "BG0_BB_HOLD_PROTOCOL",
    "BG0_BC_HOLD_PROTOCOL",
    "BG0_BD_HOLD_PROTOCOL",
    "BG0_BE_HOLD_PROTOCOL",
    "BG0_BF_HOLD_PROTOCOL",
    "BG0_AZ_HOLD_PROTOCOL",
    "BG0_CTX_BASELINE",
    "BG0_SPEED_BASELINE",
    "BG0_UTIL_TRACK",
    "BG0_GEN_STANCE",
    "BG0_TRUE_GEN_JUDGE",
    "BG0_REAL_EVAL_PROTOCOL",
    "BG0_ASK_BATTERY",
    "BG0_SAFE_NOTE",
    "BG0_ANTI_FP",
    "BG0_NORTH_STAR",
    "BG0_SHIP_LOCK",
    "map_bg_product_mode",
    "decide_bg0_session",
]

BG0_ID = "BG0-SESSION"
BG0_THESIS = (
    "Wave BG ACTIVE: freeze BG-FOREVER (unary/math/string-transform/"
    "aggregate residual FP: abs≠add · factorial≠add · upper≠f-string · "
    "all-truthy≠clear + paraphrases · arity/transform neighbors) · "
    "BA/BB/BC/BD/BE/BF-FOREVER hold · AZ hold · §1 anti-FP scoreboard · "
    "Track A++ utilization (paper/arXiv sync) · ctx/speed baselines from "
    "BF · gen stance = SKIP (no written M1|M2|M3 plan; not NANOGEN17 "
    "rename) · real-eval; next BG1 H-UNARYINT (not CTX/SMART/FAST clone)"
)

BG0_MODES: frozenset[str] = AU0_MODES
BG0_LATENCY_PATHS: tuple[str, ...] = (
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
)

BG0_CITED_BF_LOCKS: frozenset[str] = frozenset(
    {
        "H-PREDINT",
        "H-SHIPUSE2",
        "H-FASTBF",
        "H-CTXBF",
        "H-NANOGEN16",
        "BF-REAL-EVAL",
        "BF-FREEZE",
    }
)

BG0_SHIP_LOCK = BF0_SHIP_LOCK

BG0_NORTH_STAR = (
    "Nano generative / mini-AGI-inspired ≤5M: unary/transform anti-FP "
    "(BG-FOREVER FH 0 + BA…BF forever hold + AZ hold + novel probes) + "
    "ship/utilize/publish proven AF+AQ+AS stack + measurable context & "
    "speed + one honest generative method (M1|M2|M3) — else SKIP gen "
    "letters; never pack theater · never LOOKUP-as-IQ · never NANOGEN17 "
    "without method plan"
)

BG0_GEN_STANCE: Mapping[str, object] = {
    "stage": "BG0 freezes stance; BG5 H-NANOGEN17 SKIP without method plan",
    "stance": "skip",
    "allowed_stances": ["M1", "M2", "M3", "skip"],
    "method_candidates": {
        "M1": "teacher distill continue + anti-copy-gold loss",
        "M2": "student draft + bank/teacher rejector (hybrid)",
        "M3": "named CAPCHECK (raise params with ablations)",
    },
    "method_plan_attached": False,
    "capcheck": "closed",
    "named_hyp": "H-NANOGEN17",
    "named_unaryint": "H-UNARYINT",
    "named_shippub": "H-SHIPPUB",
    "named_fast": "H-FASTBG",
    "named_ctx": "H-CTXBG",
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
    "nanogen16_skip_cited": True,
    "nanogen17_rename_forbidden": True,
    "nanogen17_without_plan_forbidden": True,
    "skip_gen_stop_rule": True,
    "true_continue_required_for_promote": True,
    "span_fallback_neq_gen": True,
    "rationale": (
        "No written M1|M2|M3 method plan at BG0; H-NANOGEN16 already "
        "SKIP once — stop rule forbids empty NANOGEN17 letter; "
        "NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · NANOGEN16 SKIP stand; "
        "CAPCHECK stays closed; prefer unary/transform/arity gate "
        "(H-UNARYINT) + Track A++ publish/utilize (H-SHIPPUB) over "
        "vanity NANOGEN17 rename; BG5 = SKIP stage"
    ),
    "bg5_gate": "SKIP stage (no written M1|M2|M3 plan at BG0)",
}

BG0_SAFE_NOTE = (
    "SAFE / ADVSAFE false-hit score ≠ answer quality; "
    "SAFE = no wrong gold only (anti-FP); "
    "pack FH 0 ≠ forever held-out generalization; "
    "unary/math/string-transform wrong-bank LOOKUP = false-hit "
    "(abs→def add · upper→f-string · all-truthy→clear); "
    "BA…BF forever PASS with BG-FOREVER FP = PACK THEATER; "
    "exact-gold ABSTAIN = product miss; "
    "gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE"
)

BG0_ANTI_FP = (
    "LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; "
    "never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; "
    "unary/math LOOKUP = false-hit (BG-FOREVER abs/factorial→add); "
    "string-transform LOOKUP = false-hit (BG-FOREVER upper→f-string); "
    "aggregate/predicate LOOKUP = false-hit (all-truthy→clear); "
    "predicate/boolean LOOKUP = false-hit (BF-FOREVER even→add); "
    "type/coercion LOOKUP = false-hit (BE-FOREVER str→int→add); "
    "exact-gold ABSTAIN = miss (a.clear()); "
    "BA-FOREVER pow·mod·max·sort·len FH must stay 0; "
    "BB-FOREVER min·xor·absdiff·and·or FH must stay 0; "
    "BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; "
    "BD-FOREVER reverse≠f-string · mul≠add FH must stay 0; "
    "BE-FOREVER str→int / type-coercion FH must stay 0; "
    "BF-FOREVER even/bool ≠ add FH must stay 0; "
    "AZ hold div·sub·BIP FH must stay 0; "
    "BA…BF PASS with BG FP = PACK THEATER; "
    "truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; "
    "eval path = prod ask path; "
    "generative bar = BG5 only under written method plan; "
    "no NANOGEN17 without M1|M2|M3 plan; no CTX/SMART/FAST clone; "
    "no invent Wave BH without lab-book reopen; "
    "prefer unary/transform/arity gate over bank stuffing; "
    "prefer HOLD/SKIP over fake PROMOTE"
)

BG0_TRUE_GEN_JUDGE: Mapping[str, object] = {
    "stage": "BG5 H-NANOGEN17 SKIP without method plan; BG0 freezes judge",
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
    "nanogen16_skip_archived": True,
    "nanogen17_rename_forbidden": True,
    "nanogen17_without_plan_forbidden": True,
    "scoring": "short_answer_f1_or_hitl_true_continue_only",
    "promote_bar": "true_continue else SKIP (no empty DEFER letter)",
}

BG0_SPEED_BASELINE: Mapping[str, object] = {
    "source": "H-FASTBF / formal-hfastbf-fastbf.md (prod ask path)",
    "path": "nano:z:ask prod path",
    "unit": "wall_ms",
    "paths": {
        "LOOKUP": {"p50": 0.0, "p99": 0.0},
        "PEAK": {
            "p50": 0.020638000023609493,
            "p99": 0.028944830004320465,
        },
        "DECODE": {
            "p50": 10.507157999995798,
            "p99": 10.882093060029092,
        },
        "ABSTAIN": {
            "p50": 87.36960300001329,
            "p99": 110.29079292000351,
        },
    },
    "quality_regress_forbidden": True,
    "warm_cache_vanity_forbidden": True,
    "bg3_gate": (
        "speed PROMOTE only if §1 anti-FP bars hold (incl BG-FOREVER)"
    ),
    "parent_bf0_baseline_cited": True,
    "parent_bf0_paths": dict(BF0_SPEED_BASELINE["paths"]),  # type: ignore[arg-type]
}

BG0_CTX_BASELINE: Mapping[str, object] = {
    "source": "H-CTXBF / H-CTXBE / H-CTXGAIN (content-first)",
    "l_eff_alone_insufficient": True,
    "content_bars_required": True,
    "modes_visible_required": True,
    "long_cite_howto_pack": True,
    "honest_abstain_when_missing": True,
    "bg4_gate": (
        "H-CTXBG PROMOTE only if content_ok + no new intent FP "
        "(incl BG-FOREVER) + p50/p99 published + modes visible"
    ),
}

BG0_UTIL_TRACK: Mapping[str, object] = {
    "stage": "BG2 H-SHIPPUB executes; BG0 freezes Track A++ checklist",
    "known_ask_hitl": True,
    "ship_surface_doc": True,
    "paper_archive": True,
    "paper_arxiv_sync": True,
    "operator_card": True,
    "claim_matches_live": True,
    "gpt_claim_forbidden": True,
    "modes_visible_required": True,
    "h_shipuse2_hold": True,
    "checklist": [
        "demo smoke: npm run nano:z:ask -- --wrap --semwrap",
        "RECIPES + champion-card operator sync",
        "paper:build + narrative/arXiv sync = selective retriever + refuse ≤5M",
        "modes always LOOKUP|PEAK|DECODE|ABSTAIN",
        "H-SHIPUSE2 hold; deepen utilization + paper surface",
    ],
    "path": "nano:z:ask --wrap --semwrap",
    "bg2_gate": "Track A++ done before utilization PROMOTE (H-SHIPPUB)",
}

BG0_SCOREBOARD: Mapping[str, object] = {
    "stage": "BG1 H-UNARYINT closes bars; BG0 freezes §1 scoreboard",
    "cite_bf_locks": sorted(BG0_CITED_BF_LOCKS),
    "accept_artifact": (
        "AF+AQ+AS trust + STRICT ablated DECODE (BF H-PREDINT·H-SHIPUSE2·"
        "H-FASTBF·H-CTXBF); NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · "
        "NANOGEN16 SKIP; not TAC unlocked"
    ),
    "debts": [
        {
            "id": "bg_forever_false_hit_zero",
            "evidence": (
                "Live FP: abs→add · factorial→add · upper→f-string · "
                "all-truthy→clear"
            ),
            "fix": "BG-FOREVER unary/transform FH 0 via general gate",
            "bar": "bg_forever_false_hit_max=0",
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
            "id": "bf_forever_hold_zero",
            "evidence": "BF even/bool ≠ add FH 0 must hold",
            "fix": "BF-FOREVER regression hold",
            "bar": "bf_forever_false_hit_max=0",
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
            "fix": "live nano:z:ask on BG+BA…BF+AZ + ≥10 novel probes",
            "bar": "live_ask_scored True",
        },
        {
            "id": "speed_baseline_publish",
            "evidence": "BF FASTBF p50/p99 republished at BG0",
            "fix": "BG3 measures prod wall without FP regress",
            "bar": "speed_baseline_published True",
        },
        {
            "id": "ctx_baseline_publish",
            "evidence": "content bars required; L_eff alone forbidden",
            "fix": "BG4 measures usable long/cite/howto",
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
                "NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · NANOGEN16 SKIP; "
                "no method plan at BG0"
            ),
            "fix": "stance SKIP · CAPCHECK closed · no NANOGEN17 without plan",
            "bar": "gen_stance=skip; nanogen17_without_plan_forbidden",
        },
        {
            "id": "paraphrase_eval_rule",
            "evidence": "BG-FOREVER seeds + held-out paraphrases at eval",
            "fix": "never bank-stuff exact seed strings",
            "bar": "paraphrase_required True; bank_stuff_forbidden",
        },
        {
            "id": "utilization_track_a_plus_plus",
            "evidence": "Track A++: demo + recipes + paper/arXiv + H-SHIPUSE2",
            "fix": "BG2 H-SHIPPUB utilization checklist",
            "bar": "utilization_track_frozen True",
        },
    ],
    "metrics": [
        "bg_forever_false_hit",
        "ba_forever_false_hit",
        "bb_forever_false_hit",
        "bc_forever_false_hit",
        "bd_forever_false_hit",
        "be_forever_false_hit",
        "bf_forever_false_hit",
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
        "bg_forever_false_hit_max": 0,
        "ba_forever_false_hit_max": 0,
        "bb_forever_false_hit_max": 0,
        "bc_forever_false_hit_max": 0,
        "bd_forever_false_hit_max": 0,
        "be_forever_false_hit_max": 0,
        "bf_forever_false_hit_max": 0,
        "az_hold_false_hit_max": 0,
        "overrefuse_miss_max": 0,
        "bg_forever_min_n": 12,
        "bg_forever_classes_min": 4,
        "modes_required": list(BG0_LATENCY_PATHS),
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
        "ba_bb_bc_bd_be_bf_pass_neq_bg_forever": True,
        "bank_stuff_forbidden": True,
        "paraphrase_required": True,
        "unary_transform_gate_preferred": True,
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
        "bf_forever_fh": 0,
        "az_heldout_fh": 0,
        "az_overrefuse_miss": 0,
        "fastbf_latency": {
            "LOOKUP": {"p50": 0.0, "p99": 0.0},
            "PEAK": {
                "p50": 0.020638000023609493,
                "p99": 0.028944830004320465,
            },
            "DECODE": {
                "p50": 10.507157999995798,
                "p99": 10.882093060029092,
            },
            "ABSTAIN": {
                "p50": 87.36960300001329,
                "p99": 110.29079292000351,
            },
        },
        "ctxbf_content": "PROMOTE",
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
        "nanogen16_decision": "SKIP",
        "bf_real_eval_battery": "16/16",
        "live_audit_bg_forever_fp": (
            "abs→add · factorial→add · upper→f-string · all-truthy→clear"
        ),
        "forever_classes": [
            "unary_math",
            "unary_math_para",
            "string_transform",
            "string_transform_para",
            "aggregate_predicate",
            "arity_transform_neighbor",
        ],
        "ship_lock": BG0_SHIP_LOCK,
    },
    "runners": [
        "nano:z:ask",
        "nano:predint",
        "nano:shipuse2",
        "nano:fastbf",
        "nano:ctxbf",
        "nano:nanogen16",
        "nano:advsafe",
        "nano:metrics",
        "nano:askabstain",
        "nano:bf:freeze",
    ],
    "no_reopen_unless_fail": [
        "H-PREDINT",
        "H-SHIPUSE2",
        "H-FASTBF",
        "H-CTXBF",
        "H-COMPINT",
        "H-SEMINT",
        "H-OPSFAM",
        "H-INTENTGEN",
        "H-REALGAIN",
        "H-ADVSAFE",
    ],
    "complete_kb_claim_forbidden": True,
}

BG0_FOREVER_ROWS: tuple[dict[str, str], ...] = (
    {
        "id": "BG-FH-01",
        "class": "unary_math",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a Python function that returns the absolute value of a."
        ),
    },
    {
        "id": "BG-FH-02",
        "class": "unary_math",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a Python function named factorial that returns n!."
        ),
    },
    {
        "id": "BG-FH-03",
        "class": "string_transform",
        "expect_mode": "ABSTAIN",
        "question": "How do I uppercase string s in Python?",
    },
    {
        "id": "BG-FH-04",
        "class": "aggregate_predicate",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a Python function that returns True if all items "
            "in list a are truthy."
        ),
    },
    {
        "id": "BG-FH-05",
        "class": "unary_math_para",
        "expect_mode": "ABSTAIN",
        "question": "Python: compute abs(a) for integer a and return it.",
    },
    {
        "id": "BG-FH-06",
        "class": "unary_math_para",
        "expect_mode": "ABSTAIN",
        "question": (
            "Implement factorial(n) that returns the factorial of n."
        ),
    },
    {
        "id": "BG-FH-07",
        "class": "string_transform_para",
        "expect_mode": "ABSTAIN",
        "question": (
            "Convert string s to uppercase letters — one Python call."
        ),
    },
    {
        "id": "BG-FH-08",
        "class": "unary_math_para",
        "expect_mode": "ABSTAIN",
        "question": (
            "How do I get the absolute value of integer a in a function?"
        ),
    },
    {
        "id": "BG-FH-09",
        "class": "arity_transform_neighbor",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a Python function that returns the floor of float a."
        ),
    },
    {
        "id": "BG-FH-10",
        "class": "arity_transform_neighbor",
        "expect_mode": "ABSTAIN",
        "question": "How do I lowercase string s in Python?",
    },
    {
        "id": "BG-FH-11",
        "class": "arity_transform_neighbor",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a function that returns True if any item in list a "
            "is truthy."
        ),
    },
    {
        "id": "BG-FH-12",
        "class": "arity_transform_neighbor",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a Python function that rounds float a to nearest int."
        ),
    },
)

BG0_FOREVER_PROTOCOL: Mapping[str, object] = {
    "stage": "BG1 H-UNARYINT scores; BG0 freezes protocol",
    "held_out": True,
    "forever": True,
    "bank_stuff_forbidden": True,
    "paraphrase_required": True,
    "unary_transform_gate_preferred": True,
    "neq_ba_forever": True,
    "neq_bb_forever": True,
    "neq_bc_forever": True,
    "neq_bd_forever": True,
    "neq_be_forever": True,
    "neq_bf_forever": True,
    "neq_az_heldout": True,
    "intent_mismatch_is_false_hit": True,
    "unary_mismatch_is_false_hit": True,
    "transform_mismatch_is_false_hit": True,
    "source": (
        "live residual FP (abs≠add · factorial≠add · upper≠f-string · "
        "all-truthy≠clear + paras · arity/transform neighbors)"
    ),
    "min_n": 12,
    "classes_min": 4,
    "required_classes": [
        "unary_math",
        "unary_math_para",
        "string_transform",
        "string_transform_para",
        "aggregate_predicate",
        "arity_transform_neighbor",
    ],
    "scoring": "false-hit rate on default ask path (mismatch → ABSTAIN)",
    "path": "nano:z:ask --wrap --semwrap",
    "pack_pass_neq_forever": True,
    "ba_bb_bc_bd_be_bf_pass_neq_bg_forever": True,
    "live_fp_id": "BG-FH-01",
    "rows": list(BG0_FOREVER_ROWS),
}

BG0_BA_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BG1 must hold BA bars; BG0 freezes regression pack",
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

BG0_BB_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BG1 must hold BB bars; BG0 freezes regression pack",
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

BG0_BC_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BG1 must hold BC bars; BG0 freezes regression pack",
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

BG0_BD_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BG1 must hold BD bars; BG0 freezes regression pack",
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

BG0_BE_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BG1 must hold BE bars; BG0 freezes regression pack",
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

BG0_BF_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BG1 must hold BF bars; BG0 freezes regression pack",
    "source": "BF0_FOREVER_ROWS",
    "heldout_n": len(BF0_FOREVER_ROWS),
    "forever_false_hit_max": 0,
    "required_classes": [
        "predicate_boolean",
        "predicate_boolean_para",
        "predicate_schema_neighbor",
    ],
    "path": "nano:z:ask --wrap --semwrap",
    "regression_hold": True,
}

BG0_AZ_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BG1 must hold AZ bars; BG0 freezes regression pack",
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

BG0_REAL_EVAL_PROTOCOL: Mapping[str, object] = {
    "live_ask_battery": True,
    "summary_only_forbidden": True,
    "product_mode_required": True,
    "wall_ms_n_new_mandatory": True,
    "wall_ms_n_new_insufficient_for_decode_quality": True,
    "lookup_neq_iq": True,
    "peak_neq_open_chat": True,
    "safe_neq_quality": True,
    "intent_mismatch_is_false_hit": True,
    "unary_mismatch_is_false_hit": True,
    "transform_mismatch_is_false_hit": True,
    "exact_gold_abstain_is_miss": True,
    "gold_substring_neq_gen": True,
    "gibberish_tail_fails": True,
    "span_fallback_neq_gen": True,
    "pack_pass_neq_forever": True,
    "ba_bb_bc_bd_be_bf_pass_neq_bg_forever": True,
    "eval_eq_prod_ask": True,
    "answer_usability_scored": True,
    "utilization_scored": True,
    "novel_probes_min": 10,
    "score_labels": ["OK", "FP", "MISS", "ABSTAIN-OK"],
    "gen_claim_rule": (
        "only if BG5 H-NANOGEN17 PROMOTE (true_continue; "
        "written M1|M2|M3 plan; never NANOGEN16+rename; "
        "span-fallback ≠ gen) — else SKIP gen claim"
    ),
    "mini_agi_rule": (
        "forbidden while gen stance skip or NANOGEN17 SKIP/HOLD/DEFER"
    ),
    "stage": "BG6 BG-REAL-EVAL scores; BG0 freezes protocol",
}

BG0_ASK_BATTERY: tuple[dict[str, str], ...] = (
    {
        "id": "BG-ASK-01",
        "kind": "known_lookup",
        "expect_mode": "LOOKUP",
        "question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
    },
    {
        "id": "BG-ASK-02",
        "kind": "ood_abstain",
        "expect_mode": "ABSTAIN",
        "question": "Who won the 2022 FIFA World Cup?",
    },
    {
        "id": "BG-ASK-03",
        "kind": "near_miss",
        "expect_mode": "ABSTAIN",
        "question": (
            "BIP-39 entropy formula is CS = ENT / 32 — confirm for "
            "SegWit witness discount?"
        ),
    },
    {
        "id": "BG-ASK-04",
        "kind": "labeled_peak",
        "expect_mode": "PEAK",
        "question": (
            "From the curated Rust book intro, extract one sentence "
            "on ownership (label PEAK, not open chat)."
        ),
    },
    {
        "id": "BG-ASK-05",
        "kind": "decode_content",
        "expect_mode": "DECODE",
        "question": "Explain Merkle trees briefly",
    },
    {
        "id": "BG-ASK-06",
        "kind": "junk_trap",
        "expect_mode": "ABSTAIN",
        "question": ".",
    },
    {
        "id": "BG-ASK-07",
        "kind": "bg_forever_unary_fp",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a Python function that returns the absolute value of a."
        ),
    },
    {
        "id": "BG-ASK-08",
        "kind": "overrefuse_gold",
        "expect_mode": "LOOKUP",
        "question": "Remove all items from list `a` — one method call.",
    },
    {
        "id": "BG-ASK-09",
        "kind": "az_hold_div",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named div that returns "
            "the quotient of two integers a and b."
        ),
    },
    {
        "id": "BG-ASK-10",
        "kind": "ba_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named pow2 that returns "
            "a raised to the power of b for two integers."
        ),
    },
    {
        "id": "BG-ASK-11",
        "kind": "bb_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named min2 that returns "
            "the smaller of two integers a and b."
        ),
    },
    {
        "id": "BG-ASK-12",
        "kind": "bc_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a Python function floordiv(a, b) that returns a // b."
        ),
    },
    {
        "id": "BG-ASK-13",
        "kind": "bd_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": "How do I reverse a string in Python?",
    },
    {
        "id": "BG-ASK-14",
        "kind": "be_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": "How do I convert string s to integer in Python?",
    },
    {
        "id": "BG-ASK-15",
        "kind": "bf_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a Python function that returns True if a is even."
        ),
    },
    {
        "id": "BG-ASK-16",
        "kind": "bg_forever_transform_fp",
        "expect_mode": "ABSTAIN",
        "question": "How do I uppercase string s in Python?",
    },
    {
        "id": "BG-ASK-17",
        "kind": "utilization_smoke",
        "expect_mode": "LOOKUP",
        "question": "How do I append x to list a in one Python method call?",
    },
)


def map_bg_product_mode(raw_mode: str) -> str:
    """
    GIVEN raw telemetry mode string
    WHEN applying BG0 mode charter (inherits AU0 aliases)
    THEN return LOOKUP | PEAK | DECODE | ABSTAIN | UNKNOWN.
    """
    return map_au_product_mode(raw_mode)


def _gate_modes() -> str | None:
    if set(BG0_LATENCY_PATHS) != BG0_MODES:
        return "KILL (latency paths ≠ mode charter)"
    if "ABSTAIN" not in BG0_MODES:
        return "KILL (ABSTAIN missing from modes)"
    return None


def _gate_cited_bf() -> str | None:
    cited = BG0_SCOREBOARD.get("cite_bf_locks")
    if not isinstance(cited, list):
        return "KILL (scoreboard must cite BF locks)"
    if set(cited) != BG0_CITED_BF_LOCKS:
        return "KILL (scoreboard BF lock citations incomplete)"
    return None


def _gate_debt_ids() -> str | None:
    debts = BG0_SCOREBOARD.get("debts")
    if not isinstance(debts, list) or len(debts) < 16:
        return "KILL (scoreboard must list ≥16 post-BF debts)"
    ids = {str(d.get("id", "")) for d in debts if isinstance(d, dict)}
    need = {
        "bg_forever_false_hit_zero",
        "ba_forever_hold_zero",
        "bb_forever_hold_zero",
        "bc_forever_hold_zero",
        "bd_forever_hold_zero",
        "be_forever_hold_zero",
        "bf_forever_hold_zero",
        "az_hold_zero",
        "overrefuse_exact_gold",
        "live_ask_scoreboard",
        "speed_baseline_publish",
        "ctx_baseline_publish",
        "mode_ui_always",
        "decode_content_law",
        "gen_skip_stance",
        "paraphrase_eval_rule",
        "utilization_track_a_plus_plus",
    }
    if not need.issubset(ids):
        return "KILL (scoreboard debt ids incomplete)"
    return None


def _gate_debt_bar_nums(bars: Mapping[str, object]) -> str | None:
    checks = (
        ("bg_forever_false_hit_max", 0, "bg_forever_false_hit_max must be 0"),
        ("ba_forever_false_hit_max", 0, "ba_forever_false_hit_max must be 0"),
        ("bb_forever_false_hit_max", 0, "bb_forever_false_hit_max must be 0"),
        ("bc_forever_false_hit_max", 0, "bc_forever_false_hit_max must be 0"),
        ("bd_forever_false_hit_max", 0, "bd_forever_false_hit_max must be 0"),
        ("be_forever_false_hit_max", 0, "be_forever_false_hit_max must be 0"),
        ("bf_forever_false_hit_max", 0, "bf_forever_false_hit_max must be 0"),
        ("az_hold_false_hit_max", 0, "az_hold_false_hit_max must be 0"),
        ("overrefuse_miss_max", 0, "overrefuse_miss_max must be 0"),
    )
    for key, want, msg in checks:
        if int(bars.get(key, 1 if want == 0 else -1)) != want:
            return f"KILL ({msg})"
    if int(bars.get("bg_forever_min_n", 0)) < 12:
        return "KILL (bg_forever_min_n must be ≥12)"
    if int(bars.get("bg_forever_classes_min", 0)) < 4:
        return "KILL (bg_forever_classes_min must be ≥4)"
    if int(bars.get("novel_probes_min", 0)) < 10:
        return "KILL (novel_probes_min must be ≥10)"
    return None


def _gate_debt_bar_flags(bars: Mapping[str, object]) -> str | None:
    flags = (
        ("decode_gibberish_neq_content_ok", "KILL (DECODE gibberish≠content_ok)"),
        ("eval_eq_prod_ask", "KILL (eval path must equal prod ask path)"),
        ("pack_pass_neq_forever", "KILL (pack PASS ≠ forever bar missing)"),
        (
            "ba_bb_bc_bd_be_bf_pass_neq_bg_forever",
            "KILL (BA…BF PASS ≠ BG forever bar missing)",
        ),
        ("bank_stuff_forbidden", "KILL (scoreboard must forbid bank stuffing)"),
        ("paraphrase_required", "KILL (scoreboard must require paraphrases)"),
        (
            "unary_transform_gate_preferred",
            "KILL (scoreboard must prefer unary/transform gate)",
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
    if not isinstance(modes, list) or set(modes) != BG0_MODES:
        return "KILL (scoreboard modes_required incomplete)"
    return None


def _gate_debt_bars() -> str | None:
    bars = BG0_SCOREBOARD.get("bars")
    if not isinstance(bars, dict):
        return "KILL (scoreboard bars missing)"
    return _gate_debt_bar_nums(bars) or _gate_debt_bar_flags(bars)


def _gate_debt_metrics() -> str | None:
    metrics = BG0_SCOREBOARD.get("metrics")
    need_m = {
        "bg_forever_false_hit",
        "ba_forever_false_hit",
        "bb_forever_false_hit",
        "bc_forever_false_hit",
        "bd_forever_false_hit",
        "be_forever_false_hit",
        "bf_forever_false_hit",
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
        + list(BF0_FOREVER_ROWS)
        + list(AZ0_HELDOUT_FP_ROWS)
        + list(AZ0_OVERREFUSE_ROWS)
    )
    return {str(p.get("question", "")).strip() for p in rows}


def _gate_fh_rows() -> str | None:
    ids: set[str] = set()
    classes: set[str] = set()
    prior = _prior_questions()
    for item in BG0_FOREVER_ROWS:
        tid = str(item.get("id", ""))
        if not tid.startswith("BG-FH-"):
            return f"KILL (bad forever id: {tid})"
        if tid in ids:
            return f"KILL (duplicate forever id: {tid})"
        ids.add(tid)
        q = str(item.get("question", "")).strip()
        if not q:
            return f"KILL (empty forever question: {tid})"
        if q in prior:
            return f"KILL (forever reuses BA…BF/AZ held-out: {tid})"
        if str(item.get("expect_mode", "")) != "ABSTAIN":
            return f"KILL (forever expect_mode must be ABSTAIN: {tid})"
        classes.add(str(item.get("class", "")))
    need = {
        "unary_math",
        "unary_math_para",
        "string_transform",
        "string_transform_para",
        "aggregate_predicate",
        "arity_transform_neighbor",
    }
    if not need.issubset(classes):
        return "KILL (forever classes incomplete)"
    live = str(BG0_FOREVER_ROWS[0].get("question", "")).lower()
    if "absolute" not in live and "abs" not in live:
        return "KILL (BG-FH-01 must be live abs≠add residual)"
    return None


def _gate_forever_flags(proto: Mapping[str, object]) -> str | None:
    flags = (
        ("held_out", "KILL (forever must be held-out)"),
        ("forever", "KILL (forever flag missing)"),
        ("bank_stuff_forbidden", "KILL (forever must forbid bank stuffing)"),
        ("paraphrase_required", "KILL (forever must require paraphrases)"),
        (
            "unary_transform_gate_preferred",
            "KILL (forever must prefer unary/transform gate)",
        ),
        ("neq_ba_forever", "KILL (forever must ≠ BA-FOREVER)"),
        ("neq_bb_forever", "KILL (forever must ≠ BB-FOREVER)"),
        ("neq_bc_forever", "KILL (forever must ≠ BC-FOREVER)"),
        ("neq_bd_forever", "KILL (forever must ≠ BD-FOREVER)"),
        ("neq_be_forever", "KILL (forever must ≠ BE-FOREVER)"),
        ("neq_bf_forever", "KILL (forever must ≠ BF-FOREVER)"),
        ("neq_az_heldout", "KILL (forever must ≠ AZ held-out)"),
        (
            "intent_mismatch_is_false_hit",
            "KILL (forever must mark mismatch as false-hit)",
        ),
        (
            "unary_mismatch_is_false_hit",
            "KILL (forever must mark unary mismatch as false-hit)",
        ),
        (
            "transform_mismatch_is_false_hit",
            "KILL (forever must mark transform mismatch as false-hit)",
        ),
        (
            "pack_pass_neq_forever",
            "KILL (forever must mark pack PASS ≠ forever)",
        ),
        (
            "ba_bb_bc_bd_be_bf_pass_neq_bg_forever",
            "KILL (forever must mark BA…BF PASS ≠ BG forever)",
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
    if len(BG0_FOREVER_ROWS) < min_n:
        return "KILL (BG0_FOREVER_ROWS below min_n)"
    if str(proto.get("live_fp_id", "")) != "BG-FH-01":
        return "KILL (forever must pin live_fp_id=BG-FH-01)"
    req = proto.get("required_classes")
    if not isinstance(req, list) or len(req) < 4:
        return "KILL (forever required_classes incomplete)"
    return _gate_fh_rows()


def _gate_forever() -> str | None:
    return _gate_forever_flags(BG0_FOREVER_PROTOCOL) or _gate_forever_sizes(
        BG0_FOREVER_PROTOCOL
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
            BG0_BA_HOLD_PROTOCOL,
            "BA hold",
            15,
            {"ops_pow", "ops_mod", "ops_max", "list_sort", "list_len"},
        ),
        (
            BG0_BB_HOLD_PROTOCOL,
            "BB hold",
            15,
            {"ops_min", "ops_xor", "ops_absdiff", "ops_and", "ops_or"},
        ),
        (
            BG0_BC_HOLD_PROTOCOL,
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
            BG0_BD_HOLD_PROTOCOL,
            "BD hold",
            12,
            {"semantic_reverse", "semantic_mul", "wrong_bank_neighbor"},
        ),
        (
            BG0_BE_HOLD_PROTOCOL,
            "BE hold",
            12,
            {
                "type_coercion",
                "type_coercion_para",
                "type_schema_neighbor",
            },
        ),
        (
            BG0_BF_HOLD_PROTOCOL,
            "BF hold",
            12,
            {
                "predicate_boolean",
                "predicate_boolean_para",
                "predicate_schema_neighbor",
            },
        ),
    )
    for proto, label, min_n, need in packs:
        err = _gate_hold_pack(
            proto=proto, label=label, min_n=min_n, need=need
        )
        if err:
            return err
    az = BG0_AZ_HOLD_PROTOCOL
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
    paths = BG0_SPEED_BASELINE.get("paths")
    if not isinstance(paths, dict) or set(paths) != BG0_MODES:
        return "KILL (speed baseline paths incomplete)"
    if not bool(BG0_SPEED_BASELINE.get("quality_regress_forbidden")):
        return "KILL (speed must forbid quality regress)"
    if "FASTBF" not in str(BG0_SPEED_BASELINE.get("source", "")):
        return "KILL (speed baseline must cite H-FASTBF)"
    if not bool(BG0_CTX_BASELINE.get("l_eff_alone_insufficient")):
        return "KILL (ctx must forbid L_eff alone)"
    if not bool(BG0_CTX_BASELINE.get("content_bars_required")):
        return "KILL (ctx must require content bars)"
    if "CTXBG" not in str(BG0_CTX_BASELINE.get("bg4_gate", "")):
        return "KILL (ctx gate must name H-CTXBG)"
    return None


def _gate_util() -> str | None:
    if not bool(BG0_UTIL_TRACK.get("gpt_claim_forbidden")):
        return "KILL (util must forbid GPT claim)"
    if not bool(BG0_UTIL_TRACK.get("known_ask_hitl")):
        return "KILL (util must require known-ask HITL)"
    if not bool(BG0_UTIL_TRACK.get("paper_arxiv_sync")):
        return "KILL (util must require paper/arXiv sync)"
    checklist = BG0_UTIL_TRACK.get("checklist")
    if not isinstance(checklist, list) or len(checklist) < 4:
        return "KILL (util checklist incomplete)"
    if "SHIPPUB" not in str(BG0_UTIL_TRACK.get("bg2_gate", "")):
        return "KILL (util gate must name H-SHIPPUB)"
    return None


def _gate_gen_stance() -> str | None:
    if str(BG0_GEN_STANCE.get("stance", "")) != "skip":
        return "KILL (gen stance must be skip at BG0)"
    allowed = BG0_GEN_STANCE.get("allowed_stances")
    if not isinstance(allowed, list) or set(allowed) != {
        "M1",
        "M2",
        "M3",
        "skip",
    }:
        return "KILL (allowed_stances must be M1|M2|M3|skip)"
    if bool(BG0_GEN_STANCE.get("method_plan_attached")):
        return "KILL (no method plan attached at BG0 — stance must stay skip)"
    if str(BG0_GEN_STANCE.get("capcheck", "")) != "closed":
        return "KILL (CAPCHECK must stay closed)"
    if str(BG0_GEN_STANCE.get("named_hyp", "")) != "H-NANOGEN17":
        return "KILL (named_hyp must be H-NANOGEN17)"
    if str(BG0_GEN_STANCE.get("named_unaryint", "")) != "H-UNARYINT":
        return "KILL (named_unaryint must be H-UNARYINT)"
    if not bool(BG0_GEN_STANCE.get("nanogen17_without_plan_forbidden")):
        return "KILL (NANOGEN17 without plan must be forbidden)"
    if not bool(BG0_GEN_STANCE.get("skip_gen_stop_rule")):
        return "KILL (skip gen stop rule required)"
    methods = BG0_GEN_STANCE.get("method_candidates")
    if not isinstance(methods, dict) or set(methods) != {"M1", "M2", "M3"}:
        return "KILL (method_candidates must name M1|M2|M3)"
    return None


def _gate_gen_judge() -> str | None:
    judge = BG0_TRUE_GEN_JUDGE
    if not bool(judge.get("span_fallback_neq_gen")):
        return "KILL (span-fallback ≠ gen required)"
    if not bool(judge.get("nanogen17_without_plan_forbidden")):
        return "KILL (judge must forbid NANOGEN17 without plan)"
    if "true_continue" not in str(judge.get("scoring", "")):
        return "KILL (judge scoring must cite true_continue)"
    return None


def _gate_real_eval() -> str | None:
    proto = BG0_REAL_EVAL_PROTOCOL
    flags = (
        "live_ask_battery",
        "summary_only_forbidden",
        "wall_ms_n_new_mandatory",
        "eval_eq_prod_ask",
        "intent_mismatch_is_false_hit",
        "unary_mismatch_is_false_hit",
        "transform_mismatch_is_false_hit",
        "exact_gold_abstain_is_miss",
        "gold_substring_neq_gen",
        "gibberish_tail_fails",
        "span_fallback_neq_gen",
        "pack_pass_neq_forever",
        "ba_bb_bc_bd_be_bf_pass_neq_bg_forever",
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
    if "nanogen17" not in claim or "skip" not in claim:
        return "KILL (gen_claim_rule must gate NANOGEN17 / SKIP)"
    return None


def _gate_notes() -> str | None:
    if "≠" not in BG0_SAFE_NOTE:
        return "KILL (SAFE note must contrast ≠)"
    if "LOOKUP" not in BG0_ANTI_FP:
        return "KILL (anti-FP must mention LOOKUP)"
    if "eval path = prod" not in BG0_ANTI_FP.lower():
        return "KILL (anti-FP must require eval=prod)"
    if "NANOGEN17" not in BG0_ANTI_FP and "nanogen17" not in BG0_ANTI_FP.lower():
        return "KILL (anti-FP must cite NANOGEN17)"
    if "≤5M" not in BG0_NORTH_STAR:
        return "KILL (north star must cite ≤5M)"
    if "skip" not in BG0_NORTH_STAR.lower():
        return "KILL (north star must cite SKIP)"
    if "gibberish-tail" not in BG0_SHIP_LOCK:
        return "KILL (ship lock must cite gibberish-tail)"
    if "TAC" not in BG0_SHIP_LOCK:
        return "KILL (ship lock must cite TAC)"
    return None


def _gate_battery(rows: Sequence[Mapping[str, str]]) -> str | None:
    if len(rows) < 4:
        return "KILL (ask battery too small)"
    modes = {str(p.get("expect_mode", "")) for p in rows}
    if modes != BG0_MODES:
        return "KILL (ask battery must cover all product modes)"
    kinds = {str(p.get("kind", "")) for p in rows}
    need = {
        "near_miss",
        "bg_forever_unary_fp",
        "bg_forever_transform_fp",
        "bf_forever_hold",
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
    if not all(i.startswith("BG-ASK-") for i in ids):
        return "KILL (ask battery ids must start with BG-ASK-)"
    return None


def _gate_charters() -> str | None:
    return (
        _gate_modes()
        or _gate_cited_bf()
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


def decide_bg0_session(
    *,
    trials_dir_ready: bool,
    anti_fp_signed: bool,
    battery: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN BG-FOREVER/BA…BF/AZ-hold/util/scoreboard/gen-SKIP/real-eval + trials
    WHEN applying BG0 SESSION gate
    THEN PROMOTE iff BF locks cited, stance=skip, battery covers 4 modes,
         util track frozen, trials ready, anti-FP signed.
    """
    rows = list(battery) if battery is not None else list(BG0_ASK_BATTERY)
    err = _gate_charters() or _gate_battery(rows)
    if err:
        return err
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-bg/trials/ not ready)"
    return f"PROMOTE ({BG0_ID}: {BG0_THESIS})"
