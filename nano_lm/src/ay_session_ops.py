"""Wave AY0 SESSION: freeze intent-adversary FP · PRODINT · gen-defer · true-eval."""

from __future__ import annotations

from typing import Mapping, Sequence

from au_session_ops import AU0_MODES, map_au_product_mode
from ax_session_ops import AX0_HARD_NATURAL_ROWS

__all__ = [
    "AY0_ID",
    "AY0_THESIS",
    "AY0_MODES",
    "AY0_LATENCY_PATHS",
    "AY0_CITED_AX_LOCKS",
    "AY0_PRODUCT_INT_CHARTER",
    "AY0_INTENT_FP_PROTOCOL",
    "AY0_INTENT_FP_ROWS",
    "AY0_GEN_STANCE",
    "AY0_TRUE_GEN_JUDGE",
    "AY0_REAL_EVAL_PROTOCOL",
    "AY0_ASK_BATTERY",
    "AY0_SAFE_NOTE",
    "AY0_ANTI_FP",
    "AY0_NORTH_STAR",
    "AY0_SHIP_LOCK",
    "map_ay_product_mode",
    "decide_ay0_session",
]

AY0_ID = "AY0-SESSION"
AY0_THESIS = (
    "Wave AY OPEN: freeze intent-adversary FP pack (mul≠add · "
    "difference-add · remove≠clear · half-known BIP) · H-PRODINT "
    "metrics charter · gen stance = defer (CAPCHECK closed; not "
    "NANOGEN9=NANOGEN8+rename) · real-eval protocol; "
    "next AY1 H-PRODINT (not CTX/SMART/FAST clone)"
)

AY0_MODES: frozenset[str] = AU0_MODES
AY0_LATENCY_PATHS: tuple[str, ...] = (
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
)

AY0_CITED_AX_LOCKS: frozenset[str] = frozenset(
    {
        "H-PRODNAT",
        "H-SHIPUX",
        "H-NANOGEN8",
        "AX-REAL-EVAL",
        "AX-FREEZE",
    }
)

AY0_SHIP_LOCK = (
    "AF packaged stack + AQ product layer + AS trust path + "
    "ablated DECODE (snippet-prefix + gibberish-tail STRICT) — "
    "not unlabeled open chat LM · not TAC unlocked"
)

AY0_NORTH_STAR = (
    "Nano generative / mini-AGI-inspired ≤5M: ship/harden Caminho A "
    "(intent FH 0 + hold hard-natural + SHIPAY); true continue only "
    "after a real new method beats NANOGEN6·7 HOLD · NANOGEN8 DEFER — "
    "else HOLD/defer; never NANOGEN9 = NANOGEN8+rename"
)

AY0_GEN_STANCE: Mapping[str, object] = {
    "stage": "AY0 freezes stance; AY3 H-NANOGEN9 applies or HOLD/DEFER",
    "stance": "defer",
    "allowed_stances": ["new_method", "capcheck_hybrid", "defer"],
    "capcheck": "closed",
    "named_hyp": "H-NANOGEN9",
    "nanogen6_hold_cited": True,
    "nanogen7_hold_cited": True,
    "nanogen8_defer_cited": True,
    "nanogen9_rename_forbidden": True,
    "true_continue_required_for_promote": True,
    "span_fallback_neq_gen": True,
    "rationale": (
        "No real new train/data/arch method ready at AY0; "
        "NANOGEN6·7 HOLD · NANOGEN8 DEFER stand; CAPCHECK stays closed; "
        "prefer product ship (intent FH 0) + honest paper over vanity "
        "NANOGEN9 clone; AY3 PROMOTE only under true_continue else "
        "HOLD/DEFER"
    ),
    "ay3_gate": "true_continue → PROMOTE else HOLD/DEFER",
}

AY0_SAFE_NOTE = (
    "SAFE / ADVSAFE false-hit score ≠ answer quality; "
    "SAFE = no wrong gold only (anti-FP); "
    "pack FH 0 ≠ live intent/adversary coverage; "
    "intent-mismatch LOOKUP = false-hit; "
    "gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE"
)

AY0_ANTI_FP = (
    "LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; "
    "never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; "
    "intent-mismatch LOOKUP = false-hit (mul/diff/remove/half-known); "
    "truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; "
    "eval path = prod ask path; pack FH 0 ≠ live intent coverage; "
    "generative bar = AY3 only under real new method; "
    "no NANOGEN9 = NANOGEN8+rename; no CTX/SMART/FAST clone; "
    "no invent Wave AZ without lab-book reopen; "
    "prefer HOLD/defer over fake PROMOTE"
)

AY0_TRUE_GEN_JUDGE: Mapping[str, object] = {
    "stage": "AY3 H-NANOGEN9 applies only if stance≠defer or new method; "
    "AY0 freezes judge law",
    "gold_substring_insufficient": True,
    "gibberish_tail_fails": True,
    "span_fallback_neq_gen": True,
    "telemetry_neq_content_ok": True,
    "usable_continue_required": True,
    "nanogen6_hold_archived": True,
    "nanogen7_tac_hold_archived": True,
    "nanogen8_defer_archived": True,
    "nanogen9_rename_forbidden": True,
    "scoring": "short_answer_f1_or_hitl_true_continue_only",
    "promote_bar": "true_continue else HOLD/DEFER",
}

AY0_PRODUCT_INT_CHARTER: Mapping[str, object] = {
    "stage": "AY1 H-PRODINT closes bars; AY0 freezes charter",
    "cite_ax_locks": sorted(AY0_CITED_AX_LOCKS),
    "accept_artifact": (
        "known-ask + robust SEMWRAP + labeled PEAK/RAG + apps "
        "(AX H-PRODNAT·H-SHIPUX locks hold; hard-natural closed)"
    ),
    "debts": [
        {
            "id": "intent_false_hit_zero",
            "evidence": (
                "Live FP: mul→add LOOKUP; difference-add→sum; "
                "remove→clear; BIP-39 wordlist→CS=ENT/32"
            ),
            "fix": "intent/adversary FH 0 on live probe class (not bank-stuff)",
            "bar": "intent_false_hit_max=0",
        },
        {
            "id": "hard_natural_hold",
            "evidence": "AX PRODNAT hard-natural 1.0/18 closed",
            "fix": "hold hard-natural ≥ bar; do not reopen vanity",
            "bar": "hard_natural_para_hit_min hold",
        },
        {
            "id": "false_hit_zero",
            "evidence": "AX PRODNAT FH 0 on ask path; must hold",
            "fix": "hard FH 0 on default ask path",
            "bar": "false_hit_max=0",
        },
        {
            "id": "latency_publish",
            "evidence": "PRODNAT board; republish every product stage",
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
            "evidence": "SHIPUX modes+content PROMOTE",
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
            "evidence": "NANOGEN6·7 HOLD · NANOGEN8 DEFER; no new method",
            "fix": "stance defer · CAPCHECK closed · no NANOGEN9 rename",
            "bar": "gen_stance=defer; nanogen9_rename_forbidden",
        },
    ],
    "metrics": [
        "intent_false_hit",
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
        "intent_false_hit_max": 0,
        "hard_natural_para_hit_min": 0.70,
        "false_hit_max": 0,
        "modes_required": list(AY0_LATENCY_PATHS),
        "intent_fp_min_n": 12,
        "intent_fp_classes_min": 4,
        "decode_gibberish_neq_content_ok": True,
        "default_ask_near_miss": "ABSTAIN",
        "default_ask_intent_mismatch": "ABSTAIN",
        "default_ask_ood": "ABSTAIN",
        "latency_publish": True,
        "kb_holes_publish": True,
        "eval_eq_prod_ask": True,
        "pack_fh_neq_live_intent": True,
        "bank_stuff_forbidden": True,
        "regression_hold": True,
    },
    "baselines": {
        "prodnat_hard_natural": 1.0,
        "prodnat_false_hit": 0,
        "shipux_modes_content": "PROMOTE",
        "nanogen6_true_continue": 0.0,
        "nanogen7_true_continue": 0.0,
        "nanogen8_decision": "DEFER",
        "nanogen6_decision": "HOLD",
        "nanogen7_decision": "HOLD",
        "ax_real_eval_battery": "8/8",
        "live_intent_fp_classes": [
            "predicate_swap",
            "antonym",
            "false_friend",
            "half_known",
        ],
        "ship_lock": AY0_SHIP_LOCK,
    },
    "runners": [
        "nano:z:ask",
        "nano:prodnat",
        "nano:shipux",
        "nano:nanogen8",
        "nano:advsafe",
        "nano:metrics",
        "nano:askabstain",
    ],
    "no_reopen_unless_fail": [
        "H-PRODNAT",
        "H-SHIPUX",
        "H-SEMFIX",
        "H-ADVSAFE",
    ],
    "complete_kb_claim_forbidden": True,
}

# Live intent-FP class (≠ AX hard-natural pack · ≠ near-miss SegWit alone).
AY0_INTENT_FP_ROWS: tuple[dict[str, str], ...] = (
    {
        "id": "AY-IFP-01",
        "class": "predicate_swap",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named mul that returns "
            "the product of two integers a and b."
        ),
    },
    {
        "id": "AY-IFP-02",
        "class": "predicate_swap",
        "expect_mode": "ABSTAIN",
        "question": (
            "I need mul(a, b) in Python — multiply two ints, "
            "not add them."
        ),
    },
    {
        "id": "AY-IFP-03",
        "class": "predicate_swap",
        "expect_mode": "ABSTAIN",
        "question": (
            "Show mul for integers a and b returning a*b. "
            "Do not return a+b."
        ),
    },
    {
        "id": "AY-IFP-04",
        "class": "antonym",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a Python function named add that returns the "
            "difference of two integers a and b."
        ),
    },
    {
        "id": "AY-IFP-05",
        "class": "antonym",
        "expect_mode": "ABSTAIN",
        "question": (
            "Please draft add(a, b) whose only job is a minus b "
            "(the difference), not the sum."
        ),
    },
    {
        "id": "AY-IFP-06",
        "class": "antonym",
        "expect_mode": "ABSTAIN",
        "question": (
            "Name it add but return the difference of two ints — "
            "not a+b."
        ),
    },
    {
        "id": "AY-IFP-07",
        "class": "false_friend",
        "expect_mode": "ABSTAIN",
        "question": (
            "How do I remove a single element x from a Python list "
            "without clearing the whole list?"
        ),
    },
    {
        "id": "AY-IFP-08",
        "class": "false_friend",
        "expect_mode": "ABSTAIN",
        "question": (
            "Python: remove x from my list a — I do not want "
            "a.clear()."
        ),
    },
    {
        "id": "AY-IFP-09",
        "class": "false_friend",
        "expect_mode": "ABSTAIN",
        "question": (
            "Delete one item named x from list a; keep other "
            "elements. Not clear()."
        ),
    },
    {
        "id": "AY-IFP-10",
        "class": "half_known",
        "expect_mode": "ABSTAIN",
        "question": "What is the BIP-39 wordlist length?",
    },
    {
        "id": "AY-IFP-11",
        "class": "half_known",
        "expect_mode": "ABSTAIN",
        "question": (
            "How many words are in the BIP-39 English wordlist?"
        ),
    },
    {
        "id": "AY-IFP-12",
        "class": "half_known",
        "expect_mode": "ABSTAIN",
        "question": (
            "BIP-39: wordlist size / vocabulary length — not the "
            "checksum formula CS = ENT/32."
        ),
    },
)

AY0_INTENT_FP_PROTOCOL: Mapping[str, object] = {
    "stage": "AY1 H-PRODINT scores; AY0 freezes protocol",
    "held_out": True,
    "bank_stuff_forbidden": True,
    "neq_ax_hard_natural": True,
    "neq_near_miss_only": True,
    "intent_mismatch_is_false_hit": True,
    "source": (
        "live intent FP rewrite (mul≠add · diff≠sum · remove≠clear · "
        "half-known≠sibling gold)"
    ),
    "min_n": 12,
    "classes_min": 4,
    "required_classes": [
        "predicate_swap",
        "antonym",
        "false_friend",
        "half_known",
    ],
    "scoring": "false-hit rate on default ask path (intent mismatch → ABSTAIN)",
    "path": "nano:z:ask --wrap --semwrap",
    "pack_fh_neq_live_intent": True,
    "live_fp_id": "AY-IFP-01",
    "rows": list(AY0_INTENT_FP_ROWS),
}

AY0_REAL_EVAL_PROTOCOL: Mapping[str, object] = {
    "live_ask_battery": True,
    "summary_only_forbidden": True,
    "product_mode_required": True,
    "wall_ms_n_new_mandatory": True,
    "wall_ms_n_new_insufficient_for_decode_quality": True,
    "lookup_neq_iq": True,
    "peak_neq_open_chat": True,
    "safe_neq_quality": True,
    "intent_mismatch_is_false_hit": True,
    "gold_substring_neq_gen": True,
    "gibberish_tail_fails": True,
    "span_fallback_neq_gen": True,
    "pack_fh_neq_live_intent": True,
    "eval_eq_prod_ask": True,
    "answer_usability_scored": True,
    "gen_claim_rule": (
        "only if AY3 H-NANOGEN9 PROMOTE (true_continue; "
        "real new method; never NANOGEN8+rename; span-fallback ≠ gen)"
    ),
    "mini_agi_rule": "forbidden while gen stance defer or NANOGEN9 HOLD/DEFER",
    "stage": "AY4 AY-REAL-EVAL scores; AY0 freezes protocol",
}

AY0_ASK_BATTERY: tuple[dict[str, str], ...] = (
    {
        "id": "AY-ASK-01",
        "kind": "known_lookup",
        "expect_mode": "LOOKUP",
        "question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
    },
    {
        "id": "AY-ASK-02",
        "kind": "ood_abstain",
        "expect_mode": "ABSTAIN",
        "question": "Which chef won the 2019 World Cup of Baking?",
    },
    {
        "id": "AY-ASK-03",
        "kind": "near_miss",
        "expect_mode": "ABSTAIN",
        "question": (
            "BIP-39 entropy formula is CS = ENT / 32 — confirm for "
            "SegWit witness discount?"
        ),
    },
    {
        "id": "AY-ASK-04",
        "kind": "labeled_peak",
        "expect_mode": "PEAK",
        "question": (
            "From the curated Rust book intro, extract one sentence "
            "on ownership (label PEAK, not open chat)."
        ),
    },
    {
        "id": "AY-ASK-05",
        "kind": "decode_content",
        "expect_mode": "DECODE",
        "question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
    },
    {
        "id": "AY-ASK-06",
        "kind": "junk_trap",
        "expect_mode": "ABSTAIN",
        "question": ".",
    },
    {
        "id": "AY-ASK-07",
        "kind": "intent_fp",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named mul that returns "
            "the product of two integers a and b."
        ),
    },
    {
        "id": "AY-ASK-08",
        "kind": "hard_natural_hold",
        "expect_mode": "LOOKUP",
        "question": (
            "I need a Python helper that adds two numbers "
            "called a and b — name it add please"
        ),
    },
)


def map_ay_product_mode(raw_mode: str) -> str:
    """
    GIVEN raw telemetry mode string
    WHEN applying AY0 mode charter (inherits AU0 aliases)
    THEN return LOOKUP | PEAK | DECODE | ABSTAIN | UNKNOWN.
    """
    return map_au_product_mode(raw_mode)


def _gate_modes() -> str | None:
    if set(AY0_LATENCY_PATHS) != AY0_MODES:
        return "KILL (latency paths ≠ mode charter)"
    if "ABSTAIN" not in AY0_MODES:
        return "KILL (ABSTAIN missing from modes)"
    return None


def _gate_cited_ax() -> str | None:
    cited = AY0_PRODUCT_INT_CHARTER.get("cite_ax_locks")
    if not isinstance(cited, list):
        return "KILL (product-int must cite AX locks)"
    if set(cited) != AY0_CITED_AX_LOCKS:
        return "KILL (product-int AX lock citations incomplete)"
    return None


def _gate_debt_ids() -> str | None:
    debts = AY0_PRODUCT_INT_CHARTER.get("debts")
    if not isinstance(debts, list) or len(debts) < 8:
        return "KILL (product-int must list ≥8 post-AX debts)"
    ids = {str(d.get("id", "")) for d in debts if isinstance(d, dict)}
    need = {
        "intent_false_hit_zero",
        "hard_natural_hold",
        "false_hit_zero",
        "latency_publish",
        "kb_holes_publish",
        "mode_ui_always",
        "decode_content_law",
        "gen_defer_stance",
    }
    if not need.issubset(ids):
        return "KILL (product-int debt ids incomplete)"
    return None


def _gate_debt_bar_nums(bars: Mapping[str, object]) -> str | None:
    if int(bars.get("intent_false_hit_max", 1)) != 0:
        return "KILL (intent_false_hit_max must be 0)"
    if float(bars.get("hard_natural_para_hit_min", -1)) < 0.70:
        return "KILL (hard_natural_para_hit_min must be ≥0.70)"
    if int(bars.get("false_hit_max", 1)) != 0:
        return "KILL (product-int false_hit_max must be 0)"
    if int(bars.get("intent_fp_min_n", 0)) < 12:
        return "KILL (intent_fp_min_n must be ≥12)"
    if int(bars.get("intent_fp_classes_min", 0)) < 4:
        return "KILL (intent_fp_classes_min must be ≥4)"
    return None


def _gate_debt_bar_flags(bars: Mapping[str, object]) -> str | None:
    if not bool(bars.get("decode_gibberish_neq_content_ok")):
        return "KILL (DECODE gibberish≠content_ok bar missing)"
    if str(bars.get("default_ask_intent_mismatch", "")) != "ABSTAIN":
        return "KILL (intent mismatch on default ask must be ABSTAIN)"
    if str(bars.get("default_ask_near_miss", "")) != "ABSTAIN":
        return "KILL (near_miss on default ask must be ABSTAIN)"
    if not bool(bars.get("eval_eq_prod_ask")):
        return "KILL (eval path must equal prod ask path)"
    if not bool(bars.get("pack_fh_neq_live_intent")):
        return "KILL (pack FH ≠ live intent bar missing)"
    if not bool(bars.get("bank_stuff_forbidden")):
        return "KILL (product-int must forbid bank stuffing)"
    if not bool(bars.get("regression_hold")):
        return "KILL (product-int must require regression_hold)"
    modes = bars.get("modes_required")
    if not isinstance(modes, list) or set(modes) != AY0_MODES:
        return "KILL (product-int modes_required incomplete)"
    return None


def _gate_debt_bars() -> str | None:
    bars = AY0_PRODUCT_INT_CHARTER.get("bars")
    if not isinstance(bars, dict):
        return "KILL (product-int bars missing)"
    return _gate_debt_bar_nums(bars) or _gate_debt_bar_flags(bars)


def _gate_debt_metrics() -> str | None:
    metrics = AY0_PRODUCT_INT_CHARTER.get("metrics")
    need_m = {
        "intent_false_hit",
        "hard_natural_para_hit",
        "false_hit",
        "p50_wall_ms",
        "p99_wall_ms",
        "decode_content_ok",
        "true_continue_ablated",
    }
    if not isinstance(metrics, list) or not need_m.issubset(set(metrics)):
        return "KILL (product-int metrics incomplete)"
    return None


def _gate_product_int() -> str | None:
    return _gate_debt_ids() or _gate_debt_bars() or _gate_debt_metrics()


def _ax_nat_questions() -> set[str]:
    return {str(p.get("question", "")).strip() for p in AX0_HARD_NATURAL_ROWS}


def _gate_ifp_rows() -> str | None:
    ids: set[str] = set()
    classes: set[str] = set()
    prior = _ax_nat_questions()
    for item in AY0_INTENT_FP_ROWS:
        tid = str(item.get("id", ""))
        if not tid.startswith("AY-IFP-"):
            return f"KILL (bad intent-fp id: {tid})"
        if tid in ids:
            return f"KILL (duplicate intent-fp id: {tid})"
        ids.add(tid)
        q = str(item.get("question", "")).strip()
        if not q:
            return f"KILL (empty intent-fp question: {tid})"
        if q in prior:
            return f"KILL (intent-fp reuses AX hard-natural: {tid})"
        mode = str(item.get("expect_mode", ""))
        if mode != "ABSTAIN":
            return f"KILL (intent-fp expect_mode must be ABSTAIN: {tid})"
        classes.add(str(item.get("class", "")))
    need = {"predicate_swap", "antonym", "false_friend", "half_known"}
    if not need.issubset(classes):
        return "KILL (intent-fp classes incomplete)"
    return None


def _gate_intent_fp_flags(proto: Mapping[str, object]) -> str | None:
    flags = (
        ("held_out", "KILL (intent-fp must be held-out)"),
        ("bank_stuff_forbidden", "KILL (intent-fp must forbid bank stuffing)"),
        ("neq_ax_hard_natural", "KILL (intent-fp must ≠ AX hard-natural)"),
        (
            "intent_mismatch_is_false_hit",
            "KILL (intent-fp must mark mismatch as false-hit)",
        ),
        (
            "pack_fh_neq_live_intent",
            "KILL (intent-fp must mark pack FH ≠ live intent)",
        ),
    )
    for key, msg in flags:
        if not bool(proto.get(key)):
            return msg
    return None


def _gate_intent_fp_sizes(proto: Mapping[str, object]) -> str | None:
    rows = proto.get("rows")
    min_n = int(proto.get("min_n", 12))
    if min_n < 12:
        return "KILL (intent-fp min_n must be ≥12)"
    if not isinstance(rows, list) or len(rows) < min_n:
        return f"KILL (intent-fp must have ≥{min_n} rows)"
    if len(AY0_INTENT_FP_ROWS) < min_n:
        return "KILL (AY0_INTENT_FP_ROWS below min_n)"
    if str(proto.get("live_fp_id", "")) != "AY-IFP-01":
        return "KILL (intent-fp must pin live_fp_id=AY-IFP-01)"
    req = proto.get("required_classes")
    if not isinstance(req, list) or len(req) < 4:
        return "KILL (intent-fp required_classes incomplete)"
    return _gate_ifp_rows()


def _gate_intent_fp() -> str | None:
    proto = AY0_INTENT_FP_PROTOCOL
    return _gate_intent_fp_flags(proto) or _gate_intent_fp_sizes(proto)


def _gate_gen_stance_core() -> str | None:
    stance = str(AY0_GEN_STANCE.get("stance", ""))
    allowed = AY0_GEN_STANCE.get("allowed_stances")
    if not isinstance(allowed, list):
        return "KILL (gen stance allowed_stances missing)"
    if stance not in allowed:
        return "KILL (gen stance must be new_method|capcheck_hybrid|defer)"
    if stance != "defer":
        return "KILL (AY0 gen stance must be defer until real new method)"
    if str(AY0_GEN_STANCE.get("capcheck", "")) != "closed":
        return "KILL (AY0 CAPCHECK must stay closed)"
    if str(AY0_GEN_STANCE.get("named_hyp", "")) != "H-NANOGEN9":
        return "KILL (AY0 must name AY3 hyp H-NANOGEN9)"
    return None


def _gate_gen_stance_cites() -> str | None:
    cites = (
        ("nanogen9_rename_forbidden", "KILL (gen stance must forbid NANOGEN9 rename)"),
        ("nanogen6_hold_cited", "KILL (gen stance must cite NANOGEN6 HOLD)"),
        ("nanogen7_hold_cited", "KILL (gen stance must cite NANOGEN7 HOLD)"),
        ("nanogen8_defer_cited", "KILL (gen stance must cite NANOGEN8 DEFER)"),
    )
    for key, msg in cites:
        if not bool(AY0_GEN_STANCE.get(key)):
            return msg
    rat = str(AY0_GEN_STANCE.get("rationale", "")).lower()
    if "nanogen" not in rat or "defer" not in rat:
        return "KILL (gen stance rationale incomplete)"
    return None


def _gate_gen_stance() -> str | None:
    return _gate_gen_stance_core() or _gate_gen_stance_cites()


def _gate_gen_judge() -> str | None:
    judge = AY0_TRUE_GEN_JUDGE
    flags = (
        "span_fallback_neq_gen",
        "gold_substring_insufficient",
        "gibberish_tail_fails",
        "telemetry_neq_content_ok",
        "nanogen6_hold_archived",
        "nanogen7_tac_hold_archived",
        "nanogen8_defer_archived",
        "nanogen9_rename_forbidden",
    )
    for key in flags:
        if not bool(judge.get(key)):
            return f"KILL (true judge must set {key})"
    scoring = str(judge.get("scoring", ""))
    if "true_continue" not in scoring:
        return "KILL (true judge scoring must be true_continue only)"
    return None


def _gate_real_eval_flags() -> str | None:
    proto = AY0_REAL_EVAL_PROTOCOL
    flags = (
        ("live_ask_battery", "KILL (real-eval must require live ask battery)"),
        ("summary_only_forbidden", "KILL (real-eval must forbid summary-only)"),
        ("wall_ms_n_new_mandatory", "KILL (real-eval must require wall_ms/n_new)"),
        ("eval_eq_prod_ask", "KILL (real-eval must require eval=prod ask)"),
        ("intent_mismatch_is_false_hit", "KILL (real-eval must mark intent FP)"),
        ("gold_substring_neq_gen", "KILL (real-eval must reject gold-substring as gen)"),
        ("gibberish_tail_fails", "KILL (real-eval must fail gibberish tail)"),
        ("span_fallback_neq_gen", "KILL (real-eval must reject span-fallback as gen)"),
        ("pack_fh_neq_live_intent", "KILL (real-eval must mark pack≠live intent)"),
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
    claim = str(AY0_REAL_EVAL_PROTOCOL.get("gen_claim_rule", "")).lower()
    if "nanogen9" not in claim:
        return "KILL (real-eval gen_claim_rule incomplete)"
    if "rename" not in claim:
        return "KILL (real-eval must forbid NANOGEN9 rename)"
    if "span" not in claim and "fallback" not in claim:
        return "KILL (real-eval must forbid span-fallback gen credit)"
    return None


def _scan_battery_row(
    item: Mapping[str, str], ids: set[str]
) -> tuple[str | None, str, str]:
    tid = str(item.get("id", ""))
    if not tid.startswith("AY-ASK-"):
        return f"KILL (bad battery id: {tid})", "", ""
    if tid in ids:
        return f"KILL (duplicate battery id: {tid})", "", ""
    q = str(item.get("question", ""))
    if tid != "AY-ASK-06" and not q.strip():
        return f"KILL (empty battery question: {tid})", "", ""
    mode = str(item.get("expect_mode", ""))
    if mode not in AY0_MODES:
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
    if modes_seen != AY0_MODES:
        return f"KILL (ask battery modes incomplete: {sorted(modes_seen)})"
    need_kinds = {
        "near_miss",
        "intent_fp",
        "hard_natural_hold",
        "labeled_peak",
        "junk_trap",
        "decode_content",
    }
    if not need_kinds.issubset(kinds):
        return "KILL (ask battery must cover product-int kinds)"
    return None


def _gate_safe_anti_fp() -> str | None:
    if "≠" not in AY0_SAFE_NOTE and "!=" not in AY0_SAFE_NOTE:
        return "KILL (SAFE≠quality note missing)"
    if "intent" not in AY0_SAFE_NOTE.lower():
        return "KILL (SAFE note must mention intent)"
    if "LOOKUP" not in AY0_ANTI_FP:
        return "KILL (anti-FP charter incomplete)"
    if "eval path = prod" not in AY0_ANTI_FP.lower():
        return "KILL (anti-FP must require eval=prod ask)"
    if "intent" not in AY0_ANTI_FP.lower():
        return "KILL (anti-FP must mark intent-mismatch as false-hit)"
    if "NANOGEN9" not in AY0_ANTI_FP and "nanogen9" not in AY0_ANTI_FP.lower():
        return "KILL (anti-FP must forbid NANOGEN9 rename)"
    return None


def _gate_north_ship() -> str | None:
    if "≤5M" not in AY0_NORTH_STAR:
        return "KILL (north-star charter incomplete)"
    if "defer" not in AY0_NORTH_STAR.lower():
        return "KILL (north-star must allow HOLD/defer)"
    if "gibberish-tail" not in AY0_SHIP_LOCK:
        return "KILL (ship lock must keep STRICT gibberish-tail claim)"
    if "TAC unlocked" not in AY0_SHIP_LOCK and "not TAC" not in AY0_SHIP_LOCK:
        return "KILL (ship lock must state not TAC unlocked)"
    return None


def _gate_notes() -> str | None:
    return _gate_safe_anti_fp() or _gate_north_ship()


def _gate_charters() -> str | None:
    return (
        _gate_modes()
        or _gate_cited_ax()
        or _gate_product_int()
        or _gate_intent_fp()
        or _gate_gen_stance()
        or _gate_gen_judge()
        or _gate_real_eval()
        or _gate_notes()
    )


def decide_ay0_session(
    *,
    trials_dir_ready: bool,
    anti_fp_signed: bool,
    battery: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN intent-FP/PRODINT/gen-defer/real-eval charters + trials + anti-FP
    WHEN applying AY0 SESSION gate
    THEN PROMOTE iff AX locks cited, stance=defer, battery covers 4 modes,
         trials ready, anti-FP signed.
    """
    rows = list(battery) if battery is not None else list(AY0_ASK_BATTERY)
    err = _gate_charters() or _gate_battery(rows)
    if err:
        return err
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-ay/trials/ not ready)"
    return f"PROMOTE ({AY0_ID}: {AY0_THESIS})"
