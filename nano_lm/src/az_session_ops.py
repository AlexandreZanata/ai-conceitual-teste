"""Wave AZ0 SESSION: freeze held-out intent · over-refuse · PRODGEN · gen-defer."""

from __future__ import annotations

from typing import Mapping, Sequence

from au_session_ops import AU0_MODES, map_au_product_mode
from ay_session_ops import AY0_INTENT_FP_ROWS

__all__ = [
    "AZ0_ID",
    "AZ0_THESIS",
    "AZ0_MODES",
    "AZ0_LATENCY_PATHS",
    "AZ0_CITED_AY_LOCKS",
    "AZ0_PRODUCT_GEN_CHARTER",
    "AZ0_HELDOUT_FP_PROTOCOL",
    "AZ0_HELDOUT_FP_ROWS",
    "AZ0_OVERREFUSE_PROTOCOL",
    "AZ0_OVERREFUSE_ROWS",
    "AZ0_GEN_STANCE",
    "AZ0_TRUE_GEN_JUDGE",
    "AZ0_REAL_EVAL_PROTOCOL",
    "AZ0_ASK_BATTERY",
    "AZ0_SAFE_NOTE",
    "AZ0_ANTI_FP",
    "AZ0_NORTH_STAR",
    "AZ0_SHIP_LOCK",
    "map_az_product_mode",
    "decide_az0_session",
]

AZ0_ID = "AZ0-SESSION"
AZ0_THESIS = (
    "Wave AZ OPEN: freeze held-out intent FP (div≠add · sub≠add · "
    "wrong-slot BIP) · over-refuse gold (a.clear() LOOKUP) · "
    "H-PRODGEN metrics charter · gen stance = defer (CAPCHECK closed; "
    "not NANOGEN10=NANOGEN9+rename) · real-eval protocol; "
    "next AZ1 H-PRODGEN (not CTX/SMART/FAST clone)"
)

AZ0_MODES: frozenset[str] = AU0_MODES
AZ0_LATENCY_PATHS: tuple[str, ...] = (
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
)

AZ0_CITED_AY_LOCKS: frozenset[str] = frozenset(
    {
        "H-PRODINT",
        "H-SHIPAY",
        "H-NANOGEN9",
        "AY-REAL-EVAL",
        "AY-FREEZE",
    }
)

AZ0_SHIP_LOCK = (
    "AF packaged stack + AQ product layer + AS trust path + "
    "ablated DECODE (snippet-prefix + gibberish-tail STRICT) — "
    "not unlabeled open chat LM · not TAC unlocked"
)

AZ0_NORTH_STAR = (
    "Nano generative / mini-AGI-inspired ≤5M: ship/harden Caminho A "
    "(held-out FH 0 + no over-refuse + hold AY/AX + SHIPAZ); true "
    "continue only after a real new method beats NANOGEN6·7 HOLD · "
    "NANOGEN8·9 DEFER — else HOLD/defer; never NANOGEN10 = NANOGEN9+rename"
)

AZ0_GEN_STANCE: Mapping[str, object] = {
    "stage": "AZ0 freezes stance; AZ3 H-NANOGEN10 applies or HOLD/DEFER",
    "stance": "defer",
    "allowed_stances": ["new_method", "capcheck_hybrid", "defer"],
    "capcheck": "closed",
    "named_hyp": "H-NANOGEN10",
    "named_prod": "H-PRODGEN",
    "named_ship": "H-SHIPAZ",
    "nanogen6_hold_cited": True,
    "nanogen7_hold_cited": True,
    "nanogen8_defer_cited": True,
    "nanogen9_defer_cited": True,
    "nanogen10_rename_forbidden": True,
    "true_continue_required_for_promote": True,
    "span_fallback_neq_gen": True,
    "rationale": (
        "No real new train/data/arch method ready at AZ0; "
        "NANOGEN6·7 HOLD · NANOGEN8·9 DEFER stand; CAPCHECK stays closed; "
        "prefer product ship (held-out FH 0 + no over-refuse) + honest "
        "paper over vanity NANOGEN10 clone; AZ3 PROMOTE only under "
        "true_continue else HOLD/DEFER"
    ),
    "az3_gate": "true_continue → PROMOTE else HOLD/DEFER",
}

AZ0_SAFE_NOTE = (
    "SAFE / ADVSAFE false-hit score ≠ answer quality; "
    "SAFE = no wrong gold only (anti-FP); "
    "named-class FH 0 ≠ held-out generalization; "
    "intent-mismatch LOOKUP = false-hit; "
    "exact-gold ABSTAIN = product miss; "
    "gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE"
)

AZ0_ANTI_FP = (
    "LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; "
    "never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; "
    "intent-mismatch LOOKUP = false-hit (div/sub/wrong-slot held-out); "
    "exact-gold ABSTAIN = miss (a.clear()); "
    "truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; "
    "eval path = prod ask path; pack/named FH 0 ≠ held-out coverage; "
    "generative bar = AZ3 only under real new method; "
    "no NANOGEN10 = NANOGEN9+rename; no CTX/SMART/FAST clone; "
    "no invent Wave BA without lab-book reopen; "
    "prefer HOLD/defer over fake PROMOTE"
)

AZ0_TRUE_GEN_JUDGE: Mapping[str, object] = {
    "stage": "AZ3 H-NANOGEN10 applies only if stance≠defer or new method; "
    "AZ0 freezes judge law",
    "gold_substring_insufficient": True,
    "gibberish_tail_fails": True,
    "span_fallback_neq_gen": True,
    "telemetry_neq_content_ok": True,
    "usable_continue_required": True,
    "nanogen6_hold_archived": True,
    "nanogen7_tac_hold_archived": True,
    "nanogen8_defer_archived": True,
    "nanogen9_defer_archived": True,
    "nanogen10_rename_forbidden": True,
    "scoring": "short_answer_f1_or_hitl_true_continue_only",
    "promote_bar": "true_continue else HOLD/DEFER",
}

AZ0_PRODUCT_GEN_CHARTER: Mapping[str, object] = {
    "stage": "AZ1 H-PRODGEN closes bars; AZ0 freezes charter",
    "cite_ay_locks": sorted(AZ0_CITED_AY_LOCKS),
    "accept_artifact": (
        "known-ask + robust SEMWRAP + labeled PEAK/RAG + apps "
        "(AY H-PRODINT·H-SHIPAY locks hold; named intent closed)"
    ),
    "debts": [
        {
            "id": "heldout_false_hit_zero",
            "evidence": (
                "Live FP: div→add LOOKUP; sub→add LOOKUP; "
                "BIP-39 12-word entropy→sibling gold 32"
            ),
            "fix": "held-out intent/wrong-slot FH 0 (not bank-stuff)",
            "bar": "heldout_false_hit_max=0",
        },
        {
            "id": "overrefuse_exact_gold",
            "evidence": "exact clear gold ABSTAIN (a.clear() over-refuse)",
            "fix": "exact / high-margin gold → LOOKUP",
            "bar": "overrefuse_miss_max=0",
        },
        {
            "id": "ay_named_intent_hold",
            "evidence": "AY PRODINT named intent FH 0/12 closed",
            "fix": "hold named mul·diff·remove·half-known; no vanity reopen",
            "bar": "named_intent_false_hit_max=0 hold",
        },
        {
            "id": "hard_natural_hold",
            "evidence": "AX PRODNAT hard-natural 1.0/18 · AY hold",
            "fix": "hold hard-natural ≥ bar",
            "bar": "hard_natural_para_hit_min hold",
        },
        {
            "id": "false_hit_zero",
            "evidence": "AY/AX FH 0 on ask path; must hold",
            "fix": "hard FH 0 on default ask path",
            "bar": "false_hit_max=0",
        },
        {
            "id": "latency_publish",
            "evidence": "PRODINT board; republish every product stage",
            "fix": "publish p50/p99 for LOOKUP·PEAK·DECODE·ABSTAIN",
            "bar": "latency_publish True",
        },
        {
            "id": "kb_holes_publish",
            "evidence": "open-world / multi-lang / tools listed",
            "fix": "coverage % + hole list every stage",
            "bar": "kb_holes_publish True",
        },
        {
            "id": "mode_ui_always",
            "evidence": "SHIPAY modes+content PROMOTE",
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
            "evidence": "NANOGEN6·7 HOLD · NANOGEN8·9 DEFER; no new method",
            "fix": "stance defer · CAPCHECK closed · no NANOGEN10 rename",
            "bar": "gen_stance=defer; nanogen10_rename_forbidden",
        },
    ],
    "metrics": [
        "heldout_false_hit",
        "overrefuse_miss",
        "named_intent_false_hit",
        "hard_natural_para_hit",
        "false_hit",
        "p50_wall_ms",
        "p99_wall_ms",
        "kb_coverage_pct",
        "kb_hole_list",
        "modes_visible",
        "decode_content_ok",
        "default_ask_abstain",
        "true_continue_ablated",
    ],
    "bars": {
        "heldout_false_hit_max": 0,
        "overrefuse_miss_max": 0,
        "named_intent_false_hit_max": 0,
        "hard_natural_para_hit_min": 0.70,
        "false_hit_max": 0,
        "modes_required": list(AZ0_LATENCY_PATHS),
        "heldout_fp_min_n": 12,
        "heldout_fp_classes_min": 3,
        "overrefuse_min_n": 3,
        "decode_gibberish_neq_content_ok": True,
        "default_ask_intent_mismatch": "ABSTAIN",
        "default_ask_near_miss": "ABSTAIN",
        "default_ask_ood": "ABSTAIN",
        "default_ask_exact_gold": "LOOKUP",
        "latency_publish": True,
        "kb_holes_publish": True,
        "eval_eq_prod_ask": True,
        "named_fh_neq_heldout": True,
        "bank_stuff_forbidden": True,
        "regression_hold": True,
    },
    "baselines": {
        "prodint_named_intent_fh": 0,
        "prodint_hard_natural": 1.0,
        "shipay_modes_content": "PROMOTE",
        "nanogen6_true_continue": 0.0,
        "nanogen7_true_continue": 0.0,
        "nanogen8_decision": "DEFER",
        "nanogen9_decision": "DEFER",
        "nanogen6_decision": "HOLD",
        "nanogen7_decision": "HOLD",
        "ay_real_eval_battery": "8/8",
        "live_audit_ok_fp_miss": "14/3/1",
        "heldout_fp_classes": ["ops_div", "ops_sub", "wrong_slot"],
        "ship_lock": AZ0_SHIP_LOCK,
    },
    "runners": [
        "nano:z:ask",
        "nano:prodint",
        "nano:shipay",
        "nano:nanogen9",
        "nano:advsafe",
        "nano:metrics",
        "nano:askabstain",
    ],
    "no_reopen_unless_fail": [
        "H-PRODINT",
        "H-SHIPAY",
        "H-PRODNAT",
        "H-SHIPUX",
        "H-SEMFIX",
        "H-ADVSAFE",
    ],
    "complete_kb_claim_forbidden": True,
}

# Held-out residual FP class (≠ AY named mul·diff·remove·half-known).
AZ0_HELDOUT_FP_ROWS: tuple[dict[str, str], ...] = (
    {
        "id": "AZ-HFP-01",
        "class": "ops_div",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named div that returns "
            "the quotient of two integers a and b."
        ),
    },
    {
        "id": "AZ-HFP-02",
        "class": "ops_div",
        "expect_mode": "ABSTAIN",
        "question": (
            "I need div(a, b) in Python — divide two ints, "
            "not add them."
        ),
    },
    {
        "id": "AZ-HFP-03",
        "class": "ops_div",
        "expect_mode": "ABSTAIN",
        "question": (
            "Show div for integers a and b returning a/b. "
            "Do not return a+b."
        ),
    },
    {
        "id": "AZ-HFP-04",
        "class": "ops_div",
        "expect_mode": "ABSTAIN",
        "question": (
            "Python helper named div: integer division of a by b, "
            "never the sum."
        ),
    },
    {
        "id": "AZ-HFP-05",
        "class": "ops_sub",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named sub that returns "
            "a minus b for two integers."
        ),
    },
    {
        "id": "AZ-HFP-06",
        "class": "ops_sub",
        "expect_mode": "ABSTAIN",
        "question": (
            "I need sub(a, b) in Python — subtract two ints, "
            "not add them."
        ),
    },
    {
        "id": "AZ-HFP-07",
        "class": "ops_sub",
        "expect_mode": "ABSTAIN",
        "question": (
            "Show sub for integers a and b returning a-b. "
            "Do not return a+b."
        ),
    },
    {
        "id": "AZ-HFP-08",
        "class": "ops_sub",
        "expect_mode": "ABSTAIN",
        "question": (
            "Python helper named sub: difference a minus b, "
            "never the sum."
        ),
    },
    {
        "id": "AZ-HFP-09",
        "class": "wrong_slot",
        "expect_mode": "ABSTAIN",
        "question": (
            "BIP-39: how many bits of entropy does a 12-word "
            "mnemonic use?"
        ),
    },
    {
        "id": "AZ-HFP-10",
        "class": "wrong_slot",
        "expect_mode": "ABSTAIN",
        "question": (
            "What entropy bit-length corresponds to a 12-word "
            "BIP-39 phrase?"
        ),
    },
    {
        "id": "AZ-HFP-11",
        "class": "wrong_slot",
        "expect_mode": "ABSTAIN",
        "question": (
            "For BIP-39 12 words, report the entropy size in bits "
            "— not the CS = ENT/32 checksum fragment."
        ),
    },
    {
        "id": "AZ-HFP-12",
        "class": "wrong_slot",
        "expect_mode": "ABSTAIN",
        "question": (
            "12-word BIP-39 entropy bits? Do not answer with "
            "checksum divisor 32 alone."
        ),
    },
)

AZ0_HELDOUT_FP_PROTOCOL: Mapping[str, object] = {
    "stage": "AZ1 H-PRODGEN scores; AZ0 freezes protocol",
    "held_out": True,
    "bank_stuff_forbidden": True,
    "neq_ay_named_intent": True,
    "neq_ax_hard_natural": True,
    "intent_mismatch_is_false_hit": True,
    "wrong_slot_is_false_hit": True,
    "source": (
        "live held-out FP (div≠add · sub≠add · "
        "12-word entropy≠sibling 32)"
    ),
    "min_n": 12,
    "classes_min": 3,
    "required_classes": ["ops_div", "ops_sub", "wrong_slot"],
    "scoring": "false-hit rate on default ask path (mismatch → ABSTAIN)",
    "path": "nano:z:ask --wrap --semwrap",
    "named_fh_neq_heldout": True,
    "live_fp_id": "AZ-HFP-01",
    "rows": list(AZ0_HELDOUT_FP_ROWS),
}

AZ0_OVERREFUSE_ROWS: tuple[dict[str, str], ...] = (
    {
        "id": "AZ-ORF-01",
        "class": "exact_clear",
        "expect_mode": "LOOKUP",
        "gold": "a.clear()",
        "question": "Remove all items from list `a` — one method call.",
    },
    {
        "id": "AZ-ORF-02",
        "class": "exact_clear",
        "expect_mode": "LOOKUP",
        "gold": "a.clear()",
        "question": (
            "How do I clear every element from Python list a "
            "in one method call?"
        ),
    },
    {
        "id": "AZ-ORF-03",
        "class": "exact_clear",
        "expect_mode": "LOOKUP",
        "gold": "a.clear()",
        "question": (
            "Python: empty list a completely with a single "
            "method — a.clear()."
        ),
    },
)

AZ0_OVERREFUSE_PROTOCOL: Mapping[str, object] = {
    "stage": "AZ1 H-PRODGEN scores; AZ0 freezes protocol",
    "exact_gold_must_lookup": True,
    "overrefuse_is_miss": True,
    "bank_stuff_forbidden": True,
    "source": "live over-refuse: clear gold → ABSTAIN (product miss)",
    "min_n": 3,
    "required_classes": ["exact_clear"],
    "scoring": "miss rate when expect LOOKUP exact gold (ABSTAIN = miss)",
    "path": "nano:z:ask --wrap --semwrap",
    "live_orf_id": "AZ-ORF-01",
    "rows": list(AZ0_OVERREFUSE_ROWS),
}

AZ0_REAL_EVAL_PROTOCOL: Mapping[str, object] = {
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
    "named_fh_neq_heldout": True,
    "eval_eq_prod_ask": True,
    "answer_usability_scored": True,
    "gen_claim_rule": (
        "only if AZ3 H-NANOGEN10 PROMOTE (true_continue; "
        "real new method; never NANOGEN9+rename; span-fallback ≠ gen)"
    ),
    "mini_agi_rule": (
        "forbidden while gen stance defer or NANOGEN10 HOLD/DEFER"
    ),
    "stage": "AZ4 AZ-REAL-EVAL scores; AZ0 freezes protocol",
}

AZ0_ASK_BATTERY: tuple[dict[str, str], ...] = (
    {
        "id": "AZ-ASK-01",
        "kind": "known_lookup",
        "expect_mode": "LOOKUP",
        "question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
    },
    {
        "id": "AZ-ASK-02",
        "kind": "ood_abstain",
        "expect_mode": "ABSTAIN",
        "question": "Which chef won the 2019 World Cup of Baking?",
    },
    {
        "id": "AZ-ASK-03",
        "kind": "near_miss",
        "expect_mode": "ABSTAIN",
        "question": (
            "BIP-39 entropy formula is CS = ENT / 32 — confirm for "
            "SegWit witness discount?"
        ),
    },
    {
        "id": "AZ-ASK-04",
        "kind": "labeled_peak",
        "expect_mode": "PEAK",
        "question": (
            "From the curated Rust book intro, extract one sentence "
            "on ownership (label PEAK, not open chat)."
        ),
    },
    {
        "id": "AZ-ASK-05",
        "kind": "decode_content",
        "expect_mode": "DECODE",
        "question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
    },
    {
        "id": "AZ-ASK-06",
        "kind": "junk_trap",
        "expect_mode": "ABSTAIN",
        "question": ".",
    },
    {
        "id": "AZ-ASK-07",
        "kind": "heldout_intent_fp",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named div that returns "
            "the quotient of two integers a and b."
        ),
    },
    {
        "id": "AZ-ASK-08",
        "kind": "overrefuse_gold",
        "expect_mode": "LOOKUP",
        "question": "Remove all items from list `a` — one method call.",
    },
    {
        "id": "AZ-ASK-09",
        "kind": "ay_named_hold",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named mul that returns "
            "the product of two integers a and b."
        ),
    },
)


def map_az_product_mode(raw_mode: str) -> str:
    """
    GIVEN raw telemetry mode string
    WHEN applying AZ0 mode charter (inherits AU0 aliases)
    THEN return LOOKUP | PEAK | DECODE | ABSTAIN | UNKNOWN.
    """
    return map_au_product_mode(raw_mode)


def _gate_modes() -> str | None:
    if set(AZ0_LATENCY_PATHS) != AZ0_MODES:
        return "KILL (latency paths ≠ mode charter)"
    if "ABSTAIN" not in AZ0_MODES:
        return "KILL (ABSTAIN missing from modes)"
    return None


def _gate_cited_ay() -> str | None:
    cited = AZ0_PRODUCT_GEN_CHARTER.get("cite_ay_locks")
    if not isinstance(cited, list):
        return "KILL (product-gen must cite AY locks)"
    if set(cited) != AZ0_CITED_AY_LOCKS:
        return "KILL (product-gen AY lock citations incomplete)"
    return None


def _gate_debt_ids() -> str | None:
    debts = AZ0_PRODUCT_GEN_CHARTER.get("debts")
    if not isinstance(debts, list) or len(debts) < 10:
        return "KILL (product-gen must list ≥10 post-AY debts)"
    ids = {str(d.get("id", "")) for d in debts if isinstance(d, dict)}
    need = {
        "heldout_false_hit_zero",
        "overrefuse_exact_gold",
        "ay_named_intent_hold",
        "hard_natural_hold",
        "false_hit_zero",
        "latency_publish",
        "kb_holes_publish",
        "mode_ui_always",
        "decode_content_law",
        "gen_defer_stance",
    }
    if not need.issubset(ids):
        return "KILL (product-gen debt ids incomplete)"
    return None


def _gate_debt_bar_nums(bars: Mapping[str, object]) -> str | None:
    if int(bars.get("heldout_false_hit_max", 1)) != 0:
        return "KILL (heldout_false_hit_max must be 0)"
    if int(bars.get("overrefuse_miss_max", 1)) != 0:
        return "KILL (overrefuse_miss_max must be 0)"
    if int(bars.get("named_intent_false_hit_max", 1)) != 0:
        return "KILL (named_intent_false_hit_max must be 0)"
    if float(bars.get("hard_natural_para_hit_min", -1)) < 0.70:
        return "KILL (hard_natural_para_hit_min must be ≥0.70)"
    if int(bars.get("false_hit_max", 1)) != 0:
        return "KILL (product-gen false_hit_max must be 0)"
    if int(bars.get("heldout_fp_min_n", 0)) < 12:
        return "KILL (heldout_fp_min_n must be ≥12)"
    if int(bars.get("heldout_fp_classes_min", 0)) < 3:
        return "KILL (heldout_fp_classes_min must be ≥3)"
    if int(bars.get("overrefuse_min_n", 0)) < 3:
        return "KILL (overrefuse_min_n must be ≥3)"
    return None


def _gate_debt_bar_flags(bars: Mapping[str, object]) -> str | None:
    if not bool(bars.get("decode_gibberish_neq_content_ok")):
        return "KILL (DECODE gibberish≠content_ok bar missing)"
    if str(bars.get("default_ask_intent_mismatch", "")) != "ABSTAIN":
        return "KILL (intent mismatch on default ask must be ABSTAIN)"
    if str(bars.get("default_ask_near_miss", "")) != "ABSTAIN":
        return "KILL (near_miss on default ask must be ABSTAIN)"
    if str(bars.get("default_ask_exact_gold", "")) != "LOOKUP":
        return "KILL (exact gold on default ask must be LOOKUP)"
    if not bool(bars.get("eval_eq_prod_ask")):
        return "KILL (eval path must equal prod ask path)"
    if not bool(bars.get("named_fh_neq_heldout")):
        return "KILL (named FH ≠ held-out bar missing)"
    if not bool(bars.get("bank_stuff_forbidden")):
        return "KILL (product-gen must forbid bank stuffing)"
    if not bool(bars.get("regression_hold")):
        return "KILL (product-gen must require regression_hold)"
    modes = bars.get("modes_required")
    if not isinstance(modes, list) or set(modes) != AZ0_MODES:
        return "KILL (product-gen modes_required incomplete)"
    return None


def _gate_debt_bars() -> str | None:
    bars = AZ0_PRODUCT_GEN_CHARTER.get("bars")
    if not isinstance(bars, dict):
        return "KILL (product-gen bars missing)"
    return _gate_debt_bar_nums(bars) or _gate_debt_bar_flags(bars)


def _gate_debt_metrics() -> str | None:
    metrics = AZ0_PRODUCT_GEN_CHARTER.get("metrics")
    need_m = {
        "heldout_false_hit",
        "overrefuse_miss",
        "named_intent_false_hit",
        "hard_natural_para_hit",
        "false_hit",
        "p50_wall_ms",
        "p99_wall_ms",
        "decode_content_ok",
        "true_continue_ablated",
    }
    if not isinstance(metrics, list) or not need_m.issubset(set(metrics)):
        return "KILL (product-gen metrics incomplete)"
    return None


def _gate_product_gen() -> str | None:
    return _gate_debt_ids() or _gate_debt_bars() or _gate_debt_metrics()


def _ay_named_questions() -> set[str]:
    return {str(p.get("question", "")).strip() for p in AY0_INTENT_FP_ROWS}


def _gate_hfp_rows() -> str | None:
    ids: set[str] = set()
    classes: set[str] = set()
    prior = _ay_named_questions()
    for item in AZ0_HELDOUT_FP_ROWS:
        tid = str(item.get("id", ""))
        if not tid.startswith("AZ-HFP-"):
            return f"KILL (bad heldout-fp id: {tid})"
        if tid in ids:
            return f"KILL (duplicate heldout-fp id: {tid})"
        ids.add(tid)
        q = str(item.get("question", "")).strip()
        if not q:
            return f"KILL (empty heldout-fp question: {tid})"
        if q in prior:
            return f"KILL (heldout-fp reuses AY named intent: {tid})"
        mode = str(item.get("expect_mode", ""))
        if mode != "ABSTAIN":
            return f"KILL (heldout-fp expect_mode must be ABSTAIN: {tid})"
        classes.add(str(item.get("class", "")))
    need = {"ops_div", "ops_sub", "wrong_slot"}
    if not need.issubset(classes):
        return "KILL (heldout-fp classes incomplete)"
    return None


def _gate_heldout_fp_flags(proto: Mapping[str, object]) -> str | None:
    flags = (
        ("held_out", "KILL (heldout-fp must be held-out)"),
        ("bank_stuff_forbidden", "KILL (heldout-fp must forbid bank stuffing)"),
        ("neq_ay_named_intent", "KILL (heldout-fp must ≠ AY named intent)"),
        (
            "intent_mismatch_is_false_hit",
            "KILL (heldout-fp must mark mismatch as false-hit)",
        ),
        (
            "wrong_slot_is_false_hit",
            "KILL (heldout-fp must mark wrong-slot as false-hit)",
        ),
        (
            "named_fh_neq_heldout",
            "KILL (heldout-fp must mark named FH ≠ held-out)",
        ),
    )
    for key, msg in flags:
        if not bool(proto.get(key)):
            return msg
    return None


def _gate_heldout_fp_sizes(proto: Mapping[str, object]) -> str | None:
    rows = proto.get("rows")
    min_n = int(proto.get("min_n", 12))
    if min_n < 12:
        return "KILL (heldout-fp min_n must be ≥12)"
    if not isinstance(rows, list) or len(rows) < min_n:
        return f"KILL (heldout-fp must have ≥{min_n} rows)"
    if len(AZ0_HELDOUT_FP_ROWS) < min_n:
        return "KILL (AZ0_HELDOUT_FP_ROWS below min_n)"
    if str(proto.get("live_fp_id", "")) != "AZ-HFP-01":
        return "KILL (heldout-fp must pin live_fp_id=AZ-HFP-01)"
    req = proto.get("required_classes")
    if not isinstance(req, list) or len(req) < 3:
        return "KILL (heldout-fp required_classes incomplete)"
    return _gate_hfp_rows()


def _gate_heldout_fp() -> str | None:
    proto = AZ0_HELDOUT_FP_PROTOCOL
    return _gate_heldout_fp_flags(proto) or _gate_heldout_fp_sizes(proto)


def _gate_orf_rows() -> str | None:
    ids: set[str] = set()
    for item in AZ0_OVERREFUSE_ROWS:
        tid = str(item.get("id", ""))
        if not tid.startswith("AZ-ORF-"):
            return f"KILL (bad overrefuse id: {tid})"
        if tid in ids:
            return f"KILL (duplicate overrefuse id: {tid})"
        ids.add(tid)
        q = str(item.get("question", "")).strip()
        if not q:
            return f"KILL (empty overrefuse question: {tid})"
        if str(item.get("expect_mode", "")) != "LOOKUP":
            return f"KILL (overrefuse expect_mode must be LOOKUP: {tid})"
        gold = str(item.get("gold", "")).strip()
        if "clear" not in gold:
            return f"KILL (overrefuse gold must be clear: {tid})"
    return None


def _gate_overrefuse() -> str | None:
    proto = AZ0_OVERREFUSE_PROTOCOL
    if not bool(proto.get("exact_gold_must_lookup")):
        return "KILL (overrefuse must require exact gold LOOKUP)"
    if not bool(proto.get("overrefuse_is_miss")):
        return "KILL (overrefuse must mark ABSTAIN as miss)"
    if not bool(proto.get("bank_stuff_forbidden")):
        return "KILL (overrefuse must forbid bank stuffing)"
    min_n = int(proto.get("min_n", 3))
    if min_n < 3:
        return "KILL (overrefuse min_n must be ≥3)"
    rows = proto.get("rows")
    if not isinstance(rows, list) or len(rows) < min_n:
        return f"KILL (overrefuse must have ≥{min_n} rows)"
    if len(AZ0_OVERREFUSE_ROWS) < min_n:
        return "KILL (AZ0_OVERREFUSE_ROWS below min_n)"
    if str(proto.get("live_orf_id", "")) != "AZ-ORF-01":
        return "KILL (overrefuse must pin live_orf_id=AZ-ORF-01)"
    return _gate_orf_rows()


def _gate_gen_stance_core() -> str | None:
    stance = str(AZ0_GEN_STANCE.get("stance", ""))
    allowed = AZ0_GEN_STANCE.get("allowed_stances")
    if not isinstance(allowed, list):
        return "KILL (gen stance allowed_stances missing)"
    if stance not in allowed:
        return "KILL (gen stance must be new_method|capcheck_hybrid|defer)"
    if stance != "defer":
        return "KILL (AZ0 gen stance must be defer until real new method)"
    if str(AZ0_GEN_STANCE.get("capcheck", "")) != "closed":
        return "KILL (AZ0 CAPCHECK must stay closed)"
    if str(AZ0_GEN_STANCE.get("named_hyp", "")) != "H-NANOGEN10":
        return "KILL (AZ0 must name AZ3 hyp H-NANOGEN10)"
    if str(AZ0_GEN_STANCE.get("named_prod", "")) != "H-PRODGEN":
        return "KILL (AZ0 must name AZ1 hyp H-PRODGEN)"
    if str(AZ0_GEN_STANCE.get("named_ship", "")) != "H-SHIPAZ":
        return "KILL (AZ0 must name AZ2 hyp H-SHIPAZ)"
    return None


def _gate_gen_stance_cites() -> str | None:
    cites = (
        (
            "nanogen10_rename_forbidden",
            "KILL (gen stance must forbid NANOGEN10 rename)",
        ),
        ("nanogen6_hold_cited", "KILL (gen stance must cite NANOGEN6 HOLD)"),
        ("nanogen7_hold_cited", "KILL (gen stance must cite NANOGEN7 HOLD)"),
        ("nanogen8_defer_cited", "KILL (gen stance must cite NANOGEN8 DEFER)"),
        ("nanogen9_defer_cited", "KILL (gen stance must cite NANOGEN9 DEFER)"),
    )
    for key, msg in cites:
        if not bool(AZ0_GEN_STANCE.get(key)):
            return msg
    rat = str(AZ0_GEN_STANCE.get("rationale", "")).lower()
    if "nanogen" not in rat or "defer" not in rat:
        return "KILL (gen stance rationale incomplete)"
    return None


def _gate_gen_stance() -> str | None:
    return _gate_gen_stance_core() or _gate_gen_stance_cites()


def _gate_gen_judge() -> str | None:
    judge = AZ0_TRUE_GEN_JUDGE
    flags = (
        "span_fallback_neq_gen",
        "gold_substring_insufficient",
        "gibberish_tail_fails",
        "telemetry_neq_content_ok",
        "nanogen6_hold_archived",
        "nanogen7_tac_hold_archived",
        "nanogen8_defer_archived",
        "nanogen9_defer_archived",
        "nanogen10_rename_forbidden",
    )
    for key in flags:
        if not bool(judge.get(key)):
            return f"KILL (true judge must set {key})"
    scoring = str(judge.get("scoring", ""))
    if "true_continue" not in scoring:
        return "KILL (true judge scoring must be true_continue only)"
    return None


def _gate_real_eval_flags() -> str | None:
    proto = AZ0_REAL_EVAL_PROTOCOL
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
        ("gold_substring_neq_gen", "KILL (real-eval must reject gold-substring as gen)"),
        ("gibberish_tail_fails", "KILL (real-eval must fail gibberish tail)"),
        ("span_fallback_neq_gen", "KILL (real-eval must reject span-fallback as gen)"),
        ("named_fh_neq_heldout", "KILL (real-eval must mark named≠held-out)"),
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
    claim = str(AZ0_REAL_EVAL_PROTOCOL.get("gen_claim_rule", "")).lower()
    if "nanogen10" not in claim:
        return "KILL (real-eval gen_claim_rule incomplete)"
    if "rename" not in claim:
        return "KILL (real-eval must forbid NANOGEN10 rename)"
    if "span" not in claim and "fallback" not in claim:
        return "KILL (real-eval must forbid span-fallback gen credit)"
    return None


def _scan_battery_row(
    item: Mapping[str, str], ids: set[str]
) -> tuple[str | None, str, str]:
    tid = str(item.get("id", ""))
    if not tid.startswith("AZ-ASK-"):
        return f"KILL (bad battery id: {tid})", "", ""
    if tid in ids:
        return f"KILL (duplicate battery id: {tid})", "", ""
    q = str(item.get("question", ""))
    if tid != "AZ-ASK-06" and not q.strip():
        return f"KILL (empty battery question: {tid})", "", ""
    mode = str(item.get("expect_mode", ""))
    if mode not in AZ0_MODES:
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
    if modes_seen != AZ0_MODES:
        return f"KILL (ask battery modes incomplete: {sorted(modes_seen)})"
    need_kinds = {
        "near_miss",
        "heldout_intent_fp",
        "overrefuse_gold",
        "ay_named_hold",
        "labeled_peak",
        "junk_trap",
        "decode_content",
    }
    if not need_kinds.issubset(kinds):
        return "KILL (ask battery must cover product-gen kinds)"
    return None


def _gate_safe_anti_fp() -> str | None:
    if "≠" not in AZ0_SAFE_NOTE and "!=" not in AZ0_SAFE_NOTE:
        return "KILL (SAFE≠quality note missing)"
    if "held-out" not in AZ0_SAFE_NOTE.lower() and "heldout" not in AZ0_SAFE_NOTE.lower():
        if "named-class" not in AZ0_SAFE_NOTE.lower():
            return "KILL (SAFE note must mention held-out/named-class)"
    if "LOOKUP" not in AZ0_ANTI_FP:
        return "KILL (anti-FP charter incomplete)"
    if "eval path = prod" not in AZ0_ANTI_FP.lower():
        return "KILL (anti-FP must require eval=prod ask)"
    if "div" not in AZ0_ANTI_FP.lower() and "held-out" not in AZ0_ANTI_FP.lower():
        return "KILL (anti-FP must mark held-out intent FP)"
    if "NANOGEN10" not in AZ0_ANTI_FP and "nanogen10" not in AZ0_ANTI_FP.lower():
        return "KILL (anti-FP must forbid NANOGEN10 rename)"
    if "over-refuse" not in AZ0_ANTI_FP.lower() and "a.clear" not in AZ0_ANTI_FP.lower():
        if "exact-gold" not in AZ0_ANTI_FP.lower():
            return "KILL (anti-FP must mark exact-gold over-refuse)"
    return None


def _gate_north_ship() -> str | None:
    if "≤5M" not in AZ0_NORTH_STAR:
        return "KILL (north-star charter incomplete)"
    if "defer" not in AZ0_NORTH_STAR.lower():
        return "KILL (north-star must allow HOLD/defer)"
    if "gibberish-tail" not in AZ0_SHIP_LOCK:
        return "KILL (ship lock must keep STRICT gibberish-tail claim)"
    if "TAC unlocked" not in AZ0_SHIP_LOCK and "not TAC" not in AZ0_SHIP_LOCK:
        return "KILL (ship lock must state not TAC unlocked)"
    return None


def _gate_notes() -> str | None:
    return _gate_safe_anti_fp() or _gate_north_ship()


def _gate_charters() -> str | None:
    return (
        _gate_modes()
        or _gate_cited_ay()
        or _gate_product_gen()
        or _gate_heldout_fp()
        or _gate_overrefuse()
        or _gate_gen_stance()
        or _gate_gen_judge()
        or _gate_real_eval()
        or _gate_notes()
    )


def decide_az0_session(
    *,
    trials_dir_ready: bool,
    anti_fp_signed: bool,
    battery: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN held-out/over-refuse/PRODGEN/gen-defer/real-eval charters + trials
    WHEN applying AZ0 SESSION gate
    THEN PROMOTE iff AY locks cited, stance=defer, battery covers 4 modes,
         trials ready, anti-FP signed.
    """
    rows = list(battery) if battery is not None else list(AZ0_ASK_BATTERY)
    err = _gate_charters() or _gate_battery(rows)
    if err:
        return err
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-az/trials/ not ready)"
    return f"PROMOTE ({AZ0_ID}: {AZ0_THESIS})"
