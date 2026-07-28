"""Wave AX0 SESSION: freeze hard-natural para · PRODNAT · gen-defer · true-eval."""

from __future__ import annotations

from typing import Mapping, Sequence

from au_session_ops import AU0_HUMAN_PARA_ROWS, AU0_MODES, map_au_product_mode
from av_session_ops import AV0_EXTERNAL_PARA_ROWS
from aw_session_ops import AW0_PRESSURE_PARA_ROWS

__all__ = [
    "AX0_ID",
    "AX0_THESIS",
    "AX0_MODES",
    "AX0_LATENCY_PATHS",
    "AX0_CITED_AW_LOCKS",
    "AX0_PRODUCT_NAT_CHARTER",
    "AX0_HARD_NATURAL_PROTOCOL",
    "AX0_HARD_NATURAL_ROWS",
    "AX0_GEN_STANCE",
    "AX0_TRUE_GEN_JUDGE",
    "AX0_REAL_EVAL_PROTOCOL",
    "AX0_ASK_BATTERY",
    "AX0_SAFE_NOTE",
    "AX0_ANTI_FP",
    "AX0_NORTH_STAR",
    "AX0_SHIP_LOCK",
    "map_ax_product_mode",
    "decide_ax0_session",
]

AX0_ID = "AX0-SESSION"
AX0_THESIS = (
    "Wave AX OPEN: freeze hard-natural para protocol (live miss class ≠ "
    "AW/AV/AU packs) · H-PRODNAT metrics charter · gen stance = defer "
    "(CAPCHECK closed; not NANOGEN8=NANOGEN7+rename) · real-eval protocol; "
    "next AX1 H-PRODNAT (not CTX/SMART/FAST clone)"
)

AX0_MODES: frozenset[str] = AU0_MODES
AX0_LATENCY_PATHS: tuple[str, ...] = (
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
)

AX0_CITED_AW_LOCKS: frozenset[str] = frozenset(
    {
        "H-PRODKEEP",
        "H-SHIPKEEP",
        "H-NANOGEN7",
        "AW-REAL-EVAL",
        "AW-FREEZE",
    }
)

AX0_SHIP_LOCK = (
    "AF packaged stack + AQ product layer + AS trust path + "
    "ablated DECODE (snippet-prefix + gibberish-tail STRICT) — "
    "not unlabeled open chat LM · not TAC unlocked"
)

AX0_NORTH_STAR = (
    "Nano generative / mini-AGI-inspired ≤5M: ship/harden Caminho A "
    "(hard natural para + PRODNAT + SHIPUX); true continue only after "
    "a real new method beats NANOGEN6·7 HOLD — else HOLD/defer; "
    "never NANOGEN8 = NANOGEN7+rename"
)

AX0_GEN_STANCE: Mapping[str, object] = {
    "stage": "AX0 freezes stance; AX3 H-NANOGEN8 applies or HOLD/DEFER",
    "stance": "defer",
    "allowed_stances": ["new_method", "capcheck_hybrid", "defer"],
    "capcheck": "closed",
    "nanogen6_hold_cited": True,
    "nanogen7_hold_cited": True,
    "nanogen8_rename_forbidden": True,
    "true_continue_required_for_promote": True,
    "span_fallback_neq_gen": True,
    "rationale": (
        "No real new train/data/arch method ready at AX0; "
        "NANOGEN6·7 HOLD (true_continue=0) stands; CAPCHECK stays closed; "
        "prefer product ship (hard natural) + honest paper over vanity "
        "NANOGEN8 clone; AX3 PROMOTE only under true_continue else HOLD/DEFER"
    ),
    "ax3_gate": "true_continue → PROMOTE else HOLD/DEFER",
}

AX0_SAFE_NOTE = (
    "SAFE / ADVSAFE false-hit score ≠ answer quality; "
    "SAFE = no wrong gold only (anti-FP); "
    "pack/pressure-para ≠ hard natural coverage; "
    "gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE"
)

AX0_ANTI_FP = (
    "LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; "
    "never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; "
    "truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; "
    "eval path = prod ask path; pack-para ≠ hard natural coverage; "
    "generative bar = AX3 only under real new method; "
    "no NANOGEN8 = NANOGEN7+rename; no CTX/SMART/FAST clone; "
    "no invent Wave AY without lab-book reopen; "
    "prefer HOLD/defer over fake PROMOTE"
)

AX0_TRUE_GEN_JUDGE: Mapping[str, object] = {
    "stage": "AX3 H-NANOGEN8 applies only if stance≠defer or new method; "
    "AX0 freezes judge law",
    "gold_substring_insufficient": True,
    "gibberish_tail_fails": True,
    "span_fallback_neq_gen": True,
    "telemetry_neq_content_ok": True,
    "usable_continue_required": True,
    "nanogen6_hold_archived": True,
    "nanogen7_tac_hold_archived": True,
    "nanogen8_rename_forbidden": True,
    "scoring": "short_answer_f1_or_hitl_true_continue_only",
    "promote_bar": "true_continue else HOLD/DEFER",
}

AX0_PRODUCT_NAT_CHARTER: Mapping[str, object] = {
    "stage": "AX1 H-PRODNAT closes bars; AX0 freezes charter",
    "cite_aw_locks": sorted(AX0_CITED_AW_LOCKS),
    "accept_artifact": (
        "known-ask + robust SEMWRAP + labeled PEAK/RAG + apps "
        "(AW H-PRODKEEP·H-SHIPKEEP locks hold)"
    ),
    "debts": [
        {
            "id": "hard_natural_para",
            "evidence": (
                "Live miss: natural 'I need a Python helper that adds "
                "two numbers… name it add' → ABSTAIN; AW-PARA-19 miss"
            ),
            "fix": "held-out hard-natural N≥15 ≠ AW/AV/AU packs",
            "bar": "hard_natural_para_hit_min on held-out set",
        },
        {
            "id": "false_hit_zero",
            "evidence": "AW PRODKEEP FH 0 on ask path; must hold",
            "fix": "hard FH 0 on default ask path",
            "bar": "false_hit_max=0",
        },
        {
            "id": "latency_publish",
            "evidence": "PRODKEEP board; republish every product stage",
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
            "evidence": "SHIPKEEP modes+content PROMOTE",
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
            "evidence": "NANOGEN6·7 HOLD; no real new method at AX0",
            "fix": "stance defer · CAPCHECK closed · no rename",
            "bar": "gen_stance=defer; nanogen8_rename_forbidden",
        },
    ],
    "metrics": [
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
        "hard_natural_para_hit_min": 0.70,
        "false_hit_max": 0,
        "modes_required": list(AX0_LATENCY_PATHS),
        "hard_natural_min_n": 15,
        "decode_gibberish_neq_content_ok": True,
        "default_ask_near_miss": "ABSTAIN",
        "default_ask_ood": "ABSTAIN",
        "latency_publish": True,
        "kb_holes_publish": True,
        "eval_eq_prod_ask": True,
        "pressure_para_neq_hard_natural": True,
        "regression_hold": True,
    },
    "baselines": {
        "prodkeep_pressure_para": 0.95,
        "prodkeep_false_hit": 0,
        "shipkeep_modes_content": "PROMOTE",
        "nanogen6_true_continue": 0.0,
        "nanogen7_true_continue": 0.0,
        "nanogen6_decision": "HOLD",
        "nanogen7_decision": "HOLD",
        "aw_real_eval_battery": "8/8",
        "live_hard_natural_miss": (
            "I need a Python helper that adds two numbers "
            "called a and b — name it add please"
        ),
        "ship_lock": AX0_SHIP_LOCK,
    },
    "runners": [
        "nano:z:ask",
        "nano:prodkeep",
        "nano:shipkeep",
        "nano:nanogen7",
        "nano:advsafe",
        "nano:metrics",
        "nano:askabstain",
    ],
    "no_reopen_unless_fail": [
        "H-SEMFIX",
        "H-ADVSAFE",
        "H-PRODKEEP",
        "H-SHIPKEEP",
    ],
    "complete_kb_claim_forbidden": True,
}

# Live miss class: conversational / intent-first rewrites (≠ AW pressure pack).
AX0_HARD_NATURAL_ROWS: tuple[dict[str, str], ...] = (
    {
        "id": "AX-NAT-01",
        "parent": "add",
        "question": (
            "I need a Python helper that adds two numbers "
            "called a and b — name it add please"
        ),
    },
    {
        "id": "AX-NAT-02",
        "parent": "add",
        "question": (
            "Can you help me write something in Python that just "
            "adds a and b together? Call the function add."
        ),
    },
    {
        "id": "AX-NAT-03",
        "parent": "add",
        "question": (
            "I'm stuck — what's a tiny function named add that "
            "takes two ints and gives me their sum?"
        ),
    },
    {
        "id": "AX-NAT-04",
        "parent": "add",
        "question": (
            "For my homework I need add(a, b) returning the sum. "
            "Keep it short."
        ),
    },
    {
        "id": "AX-NAT-05",
        "parent": "add",
        "question": (
            "Someone asked me for a Python adder: two arguments, "
            "name it add, return a+b."
        ),
    },
    {
        "id": "AX-NAT-06",
        "parent": "add",
        "question": (
            "Quick favor: show me how you'd name a function add "
            "that sums two integer inputs."
        ),
    },
    {
        "id": "AX-NAT-07",
        "parent": "add",
        "question": (
            "Looking for a beginner-friendly add helper — "
            "integers in, sum out."
        ),
    },
    {
        "id": "AX-NAT-08",
        "parent": "add",
        "question": (
            "My teammate wants a one-liner style add(a,b) "
            "that returns the total of two ints."
        ),
    },
    {
        "id": "AX-NAT-09",
        "parent": "add",
        "question": (
            "How would you phrase a Python function called add "
            "whose only job is a plus b?"
        ),
    },
    {
        "id": "AX-NAT-10",
        "parent": "add",
        "question": (
            "Please draft add for me: parameters a and b, "
            "both ints, result is their sum."
        ),
    },
    {
        "id": "AX-NAT-11",
        "parent": "add",
        "question": (
            "Natural ask: I keep forgetting — function add, "
            "two numbers, return the sum in Python."
        ),
    },
    {
        "id": "AX-NAT-12",
        "parent": "add",
        "question": (
            "Could you give me an add helper people would "
            "actually type when they mean integer addition?"
        ),
    },
    {
        "id": "AX-NAT-13",
        "parent": "add",
        "question": (
            "Real-world phrasing: build add so callers pass "
            "a,b and get back a+b as an int."
        ),
    },
    {
        "id": "AX-NAT-14",
        "parent": "add",
        "question": (
            "I don't want jargon — just a function named add "
            "that adds two integers together."
        ),
    },
    {
        "id": "AX-NAT-15",
        "parent": "add",
        "question": (
            "What does a minimal Python add look like when "
            "someone says 'sum these two ints for me'?"
        ),
    },
    {
        "id": "AX-NAT-16",
        "parent": "add",
        "question": (
            "Classroom voice: write add(a, b) — it should "
            "return the sum of the two integers."
        ),
    },
    {
        "id": "AX-NAT-17",
        "parent": "add",
        "question": (
            "Chat-style: hey, need add that only does integer "
            "sum of a and b — nothing fancy."
        ),
    },
    {
        "id": "AX-NAT-18",
        "parent": "add",
        "question": (
            "Product miss class: helper for adding two numbers; "
            "please name the function add."
        ),
    },
)

AX0_HARD_NATURAL_PROTOCOL: Mapping[str, object] = {
    "stage": "AX1 H-PRODNAT scores; AX0 freezes protocol",
    "held_out": True,
    "bank_stuff_forbidden": True,
    "neq_aw_pack": True,
    "neq_av_pack": True,
    "neq_au_pack": True,
    "source": "hard natural / live miss rewrite (≠ AW-PARA · ≠ AV-PARA · ≠ AU-PARA)",
    "min_n": 15,
    "scoring": "hit rate on default ask path (SEMWRAP)",
    "path": "nano:z:ask --wrap --semwrap",
    "pressure_para_neq_hard_natural": True,
    "live_miss_id": "AX-NAT-01",
    "rows": list(AX0_HARD_NATURAL_ROWS),
}

AX0_REAL_EVAL_PROTOCOL: Mapping[str, object] = {
    "live_ask_battery": True,
    "summary_only_forbidden": True,
    "product_mode_required": True,
    "wall_ms_n_new_mandatory": True,
    "wall_ms_n_new_insufficient_for_decode_quality": True,
    "lookup_neq_iq": True,
    "peak_neq_open_chat": True,
    "safe_neq_quality": True,
    "gold_substring_neq_gen": True,
    "gibberish_tail_fails": True,
    "span_fallback_neq_gen": True,
    "pack_para_neq_hard_natural": True,
    "eval_eq_prod_ask": True,
    "answer_usability_scored": True,
    "gen_claim_rule": (
        "only if AX3 H-NANOGEN8 PROMOTE (true_continue; "
        "real new method; never NANOGEN7+rename; span-fallback ≠ gen)"
    ),
    "mini_agi_rule": "forbidden while gen stance defer or NANOGEN8 HOLD",
    "stage": "AX4 AX-REAL-EVAL scores; AX0 freezes protocol",
}

AX0_ASK_BATTERY: tuple[dict[str, str], ...] = (
    {
        "id": "AX-ASK-01",
        "kind": "known_lookup",
        "expect_mode": "LOOKUP",
        "question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
    },
    {
        "id": "AX-ASK-02",
        "kind": "ood_abstain",
        "expect_mode": "ABSTAIN",
        "question": "Which chef won the 2019 World Cup of Baking?",
    },
    {
        "id": "AX-ASK-03",
        "kind": "near_miss",
        "expect_mode": "ABSTAIN",
        "question": (
            "BIP-39 entropy formula is CS = ENT / 32 — confirm for "
            "SegWit witness discount?"
        ),
    },
    {
        "id": "AX-ASK-04",
        "kind": "labeled_peak",
        "expect_mode": "PEAK",
        "question": (
            "From the curated Rust book intro, extract one sentence "
            "on ownership (label PEAK, not open chat)."
        ),
    },
    {
        "id": "AX-ASK-05",
        "kind": "decode_content",
        "expect_mode": "DECODE",
        "question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
    },
    {
        "id": "AX-ASK-06",
        "kind": "junk_trap",
        "expect_mode": "ABSTAIN",
        "question": ".",
    },
    {
        "id": "AX-ASK-07",
        "kind": "hard_natural",
        "expect_mode": "LOOKUP",
        "question": (
            "I need a Python helper that adds two numbers "
            "called a and b — name it add please"
        ),
    },
    {
        "id": "AX-ASK-08",
        "kind": "decode_gibberish_bar",
        "expect_mode": "DECODE",
        "question": "Explain Merkle trees briefly",
    },
)


def map_ax_product_mode(raw_mode: str) -> str:
    """
    GIVEN raw telemetry mode string
    WHEN applying AX0 mode charter (inherits AU0 aliases)
    THEN return LOOKUP | PEAK | DECODE | ABSTAIN | UNKNOWN.
    """
    return map_au_product_mode(raw_mode)


def _gate_modes() -> str | None:
    if set(AX0_LATENCY_PATHS) != AX0_MODES:
        return "KILL (latency paths ≠ mode charter)"
    if "ABSTAIN" not in AX0_MODES:
        return "KILL (ABSTAIN missing from modes)"
    return None


def _gate_cited_aw() -> str | None:
    cited = AX0_PRODUCT_NAT_CHARTER.get("cite_aw_locks")
    if not isinstance(cited, list):
        return "KILL (product-nat must cite AW locks)"
    if set(cited) != AX0_CITED_AW_LOCKS:
        return "KILL (product-nat AW lock citations incomplete)"
    return None


def _gate_debt_ids() -> str | None:
    debts = AX0_PRODUCT_NAT_CHARTER.get("debts")
    if not isinstance(debts, list) or len(debts) < 7:
        return "KILL (product-nat must list ≥7 post-AW debts)"
    ids = {str(d.get("id", "")) for d in debts if isinstance(d, dict)}
    need = {
        "hard_natural_para",
        "false_hit_zero",
        "latency_publish",
        "kb_holes_publish",
        "mode_ui_always",
        "decode_content_law",
        "gen_defer_stance",
    }
    if not need.issubset(ids):
        return "KILL (product-nat debt ids incomplete)"
    return None


def _gate_debt_bar_nums(bars: Mapping[str, object]) -> str | None:
    if float(bars.get("hard_natural_para_hit_min", -1)) < 0.70:
        return "KILL (hard_natural_para_hit_min must be ≥0.70)"
    if int(bars.get("false_hit_max", 1)) != 0:
        return "KILL (product-nat false_hit_max must be 0)"
    if int(bars.get("hard_natural_min_n", 0)) < 15:
        return "KILL (hard_natural_min_n must be ≥15)"
    return None


def _gate_debt_bar_flags(bars: Mapping[str, object]) -> str | None:
    if not bool(bars.get("decode_gibberish_neq_content_ok")):
        return "KILL (DECODE gibberish≠content_ok bar missing)"
    if str(bars.get("default_ask_near_miss", "")) != "ABSTAIN":
        return "KILL (near_miss on default ask must be ABSTAIN)"
    if not bool(bars.get("eval_eq_prod_ask")):
        return "KILL (eval path must equal prod ask path)"
    if not bool(bars.get("pressure_para_neq_hard_natural")):
        return "KILL (pressure-para ≠ hard-natural bar missing)"
    if not bool(bars.get("regression_hold")):
        return "KILL (product-nat must require regression_hold)"
    modes = bars.get("modes_required")
    if not isinstance(modes, list) or set(modes) != AX0_MODES:
        return "KILL (product-nat modes_required incomplete)"
    return None


def _gate_debt_bars() -> str | None:
    bars = AX0_PRODUCT_NAT_CHARTER.get("bars")
    if not isinstance(bars, dict):
        return "KILL (product-nat bars missing)"
    return _gate_debt_bar_nums(bars) or _gate_debt_bar_flags(bars)


def _gate_debt_metrics() -> str | None:
    metrics = AX0_PRODUCT_NAT_CHARTER.get("metrics")
    need_m = {
        "hard_natural_para_hit",
        "false_hit",
        "p50_wall_ms",
        "p99_wall_ms",
        "decode_content_ok",
        "true_continue_ablated",
    }
    if not isinstance(metrics, list) or not need_m.issubset(set(metrics)):
        return "KILL (product-nat metrics incomplete)"
    return None


def _gate_product_nat() -> str | None:
    return _gate_debt_ids() or _gate_debt_bars() or _gate_debt_metrics()


def _prior_para_questions() -> set[str]:
    au = {str(p.get("question", "")).strip() for p in AU0_HUMAN_PARA_ROWS}
    av = {str(p.get("question", "")).strip() for p in AV0_EXTERNAL_PARA_ROWS}
    aw = {str(p.get("question", "")).strip() for p in AW0_PRESSURE_PARA_ROWS}
    return au | av | aw


def _gate_nat_rows() -> str | None:
    ids: set[str] = set()
    prior = _prior_para_questions()
    for item in AX0_HARD_NATURAL_ROWS:
        tid = str(item.get("id", ""))
        if not tid.startswith("AX-NAT-"):
            return f"KILL (bad hard-natural id: {tid})"
        if tid in ids:
            return f"KILL (duplicate hard-natural id: {tid})"
        ids.add(tid)
        q = str(item.get("question", "")).strip()
        if not q:
            return f"KILL (empty hard-natural question: {tid})"
        if q in prior:
            return f"KILL (hard-natural reuses AW/AV/AU pack: {tid})"
    return None


def _gate_hard_natural() -> str | None:
    proto = AX0_HARD_NATURAL_PROTOCOL
    if not bool(proto.get("held_out")):
        return "KILL (hard-natural must be held-out)"
    if not bool(proto.get("bank_stuff_forbidden")):
        return "KILL (hard-natural must forbid bank stuffing)"
    for key in ("neq_aw_pack", "neq_av_pack", "neq_au_pack"):
        if not bool(proto.get(key)):
            return f"KILL (hard-natural must set {key})"
    if not bool(proto.get("pressure_para_neq_hard_natural")):
        return "KILL (hard-natural must ≠ pressure-para coverage claim)"
    rows = proto.get("rows")
    min_n = int(proto.get("min_n", 15))
    if min_n < 15:
        return "KILL (hard-natural min_n must be ≥15)"
    if not isinstance(rows, list) or len(rows) < min_n:
        return f"KILL (hard-natural must have ≥{min_n} rows)"
    if len(AX0_HARD_NATURAL_ROWS) < min_n:
        return "KILL (AX0_HARD_NATURAL_ROWS below min_n)"
    live = str(proto.get("live_miss_id", ""))
    if live != "AX-NAT-01":
        return "KILL (hard-natural must pin live_miss_id=AX-NAT-01)"
    return _gate_nat_rows()


def _gate_gen_stance() -> str | None:
    stance = str(AX0_GEN_STANCE.get("stance", ""))
    allowed = AX0_GEN_STANCE.get("allowed_stances")
    if not isinstance(allowed, list):
        return "KILL (gen stance allowed_stances missing)"
    if stance not in allowed:
        return "KILL (gen stance must be new_method|capcheck_hybrid|defer)"
    if stance != "defer":
        return "KILL (AX0 gen stance must be defer until real new method)"
    if str(AX0_GEN_STANCE.get("capcheck", "")) != "closed":
        return "KILL (AX0 CAPCHECK must stay closed)"
    if not bool(AX0_GEN_STANCE.get("nanogen8_rename_forbidden")):
        return "KILL (gen stance must forbid NANOGEN8 rename)"
    if not bool(AX0_GEN_STANCE.get("nanogen6_hold_cited")):
        return "KILL (gen stance must cite NANOGEN6 HOLD)"
    if not bool(AX0_GEN_STANCE.get("nanogen7_hold_cited")):
        return "KILL (gen stance must cite NANOGEN7 HOLD)"
    rat = str(AX0_GEN_STANCE.get("rationale", "")).lower()
    if "nanogen" not in rat or "defer" not in rat:
        return "KILL (gen stance rationale incomplete)"
    return None


def _gate_gen_judge() -> str | None:
    judge = AX0_TRUE_GEN_JUDGE
    flags = (
        "span_fallback_neq_gen",
        "gold_substring_insufficient",
        "gibberish_tail_fails",
        "telemetry_neq_content_ok",
        "nanogen6_hold_archived",
        "nanogen7_tac_hold_archived",
        "nanogen8_rename_forbidden",
    )
    for key in flags:
        if not bool(judge.get(key)):
            return f"KILL (true judge must set {key})"
    scoring = str(judge.get("scoring", ""))
    if "true_continue" not in scoring:
        return "KILL (true judge scoring must be true_continue only)"
    return None


def _gate_real_eval_flags() -> str | None:
    proto = AX0_REAL_EVAL_PROTOCOL
    flags = (
        ("live_ask_battery", "KILL (real-eval must require live ask battery)"),
        ("summary_only_forbidden", "KILL (real-eval must forbid summary-only)"),
        ("wall_ms_n_new_mandatory", "KILL (real-eval must require wall_ms/n_new)"),
        ("eval_eq_prod_ask", "KILL (real-eval must require eval=prod ask)"),
        ("gold_substring_neq_gen", "KILL (real-eval must reject gold-substring as gen)"),
        ("gibberish_tail_fails", "KILL (real-eval must fail gibberish tail)"),
        ("span_fallback_neq_gen", "KILL (real-eval must reject span-fallback as gen)"),
        ("pack_para_neq_hard_natural", "KILL (real-eval must mark pack≠hard-natural)"),
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
    claim = str(AX0_REAL_EVAL_PROTOCOL.get("gen_claim_rule", "")).lower()
    if "nanogen8" not in claim:
        return "KILL (real-eval gen_claim_rule incomplete)"
    if "rename" not in claim:
        return "KILL (real-eval must forbid NANOGEN8 rename)"
    if "span" not in claim and "fallback" not in claim:
        return "KILL (real-eval must forbid span-fallback gen credit)"
    return None


def _scan_battery_row(
    item: Mapping[str, str], ids: set[str]
) -> tuple[str | None, str, str]:
    tid = str(item.get("id", ""))
    if not tid.startswith("AX-ASK-"):
        return f"KILL (bad battery id: {tid})", "", ""
    if tid in ids:
        return f"KILL (duplicate battery id: {tid})", "", ""
    q = str(item.get("question", ""))
    if tid != "AX-ASK-06" and not q.strip():
        return f"KILL (empty battery question: {tid})", "", ""
    mode = str(item.get("expect_mode", ""))
    if mode not in AX0_MODES:
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
    if modes_seen != AX0_MODES:
        return f"KILL (ask battery modes incomplete: {sorted(modes_seen)})"
    need_kinds = {
        "near_miss",
        "hard_natural",
        "labeled_peak",
        "junk_trap",
        "decode_content",
    }
    if not need_kinds.issubset(kinds):
        return "KILL (ask battery must cover product-nat kinds)"
    return None


def _gate_safe_anti_fp() -> str | None:
    if "≠" not in AX0_SAFE_NOTE and "!=" not in AX0_SAFE_NOTE:
        return "KILL (SAFE≠quality note missing)"
    if "hard natural" not in AX0_SAFE_NOTE.lower():
        return "KILL (SAFE note must mention hard natural)"
    if "LOOKUP" not in AX0_ANTI_FP:
        return "KILL (anti-FP charter incomplete)"
    if "eval path = prod" not in AX0_ANTI_FP.lower():
        return "KILL (anti-FP must require eval=prod ask)"
    if "hard natural" not in AX0_ANTI_FP.lower():
        return "KILL (anti-FP must mark pack≠hard natural)"
    if "NANOGEN8" not in AX0_ANTI_FP and "nanogen8" not in AX0_ANTI_FP.lower():
        return "KILL (anti-FP must forbid NANOGEN8 rename)"
    return None


def _gate_north_ship() -> str | None:
    if "≤5M" not in AX0_NORTH_STAR:
        return "KILL (north-star charter incomplete)"
    if "defer" not in AX0_NORTH_STAR.lower():
        return "KILL (north-star must allow HOLD/defer)"
    if "gibberish-tail" not in AX0_SHIP_LOCK:
        return "KILL (ship lock must keep STRICT gibberish-tail claim)"
    if "TAC unlocked" not in AX0_SHIP_LOCK and "not TAC" not in AX0_SHIP_LOCK:
        return "KILL (ship lock must state not TAC unlocked)"
    return None


def _gate_notes() -> str | None:
    return _gate_safe_anti_fp() or _gate_north_ship()


def _gate_charters() -> str | None:
    return (
        _gate_modes()
        or _gate_cited_aw()
        or _gate_product_nat()
        or _gate_hard_natural()
        or _gate_gen_stance()
        or _gate_gen_judge()
        or _gate_real_eval()
        or _gate_notes()
    )


def decide_ax0_session(
    *,
    trials_dir_ready: bool,
    anti_fp_signed: bool,
    battery: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN hard-natural/PRODNAT/gen-defer/real-eval charters + trials + anti-FP
    WHEN applying AX0 SESSION gate
    THEN PROMOTE iff AW locks cited, stance=defer, battery covers 4 modes,
         trials ready, anti-FP signed.
    """
    rows = list(battery) if battery is not None else list(AX0_ASK_BATTERY)
    err = _gate_charters() or _gate_battery(rows)
    if err:
        return err
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-ax/trials/ not ready)"
    return f"PROMOTE ({AX0_ID}: {AX0_THESIS})"
