"""Wave AW0 SESSION: freeze product-keep · pressure-para · NANOGEN7 TAC · true-eval."""

from __future__ import annotations

from typing import Mapping, Sequence

from au_session_ops import AU0_HUMAN_PARA_ROWS, AU0_MODES, map_au_product_mode
from av_session_ops import AV0_EXTERNAL_PARA_ROWS

__all__ = [
    "AW0_ID",
    "AW0_THESIS",
    "AW0_MODES",
    "AW0_LATENCY_PATHS",
    "AW0_CITED_AV_LOCKS",
    "AW0_PRODUCT_KEEP_CHARTER",
    "AW0_PRESSURE_PARA_PROTOCOL",
    "AW0_PRESSURE_PARA_ROWS",
    "AW0_NANOGEN7_HYPOTHESIS",
    "AW0_TRUE_GEN_JUDGE",
    "AW0_REAL_EVAL_PROTOCOL",
    "AW0_ASK_BATTERY",
    "AW0_SAFE_NOTE",
    "AW0_ANTI_FP",
    "AW0_NORTH_STAR",
    "AW0_SHIP_LOCK",
    "map_aw_product_mode",
    "decide_aw0_session",
]

AW0_ID = "AW0-SESSION"
AW0_THESIS = (
    "Wave AW OPEN: freeze product-keep charter · pressure-para "
    "protocol (N≥20 ≠ AV/AU) · NANOGEN7 TAC hyp (teacher-anchored "
    "novel continue; span-fallback ≠ gen IQ) · real-eval protocol; "
    "next AW1 H-PRODKEEP (not CTX/SMART/FAST clone · not NANOGEN6 rename)"
)

AW0_MODES: frozenset[str] = AU0_MODES
AW0_LATENCY_PATHS: tuple[str, ...] = (
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
)

AW0_CITED_AV_LOCKS: frozenset[str] = frozenset(
    {
        "H-PRODSHIP",
        "H-SHIPUI2",
        "H-NANOGEN6",
        "AV-REAL-EVAL",
        "AV-FREEZE",
    }
)

AW0_SHIP_LOCK = (
    "AF packaged stack + AQ product layer + AS trust path + "
    "ablated DECODE (snippet-prefix + gibberish-tail STRICT) — "
    "not unlabeled open chat LM"
)

AW0_NORTH_STAR = (
    "Nano generative / mini-AGI-inspired ≤5M: hold Caminho A "
    "(PRODKEEP + SHIPKEEP); true ablated DECODE via H-NANOGEN7 TAC "
    "(teacher-anchored novel continue) without span-fallback-as-IQ "
    "before generative or mini-AGI claim"
)

AW0_NANOGEN7_HYPOTHESIS = (
    "One idea: teacher-anchored novel continue (TAC) — DECODE may "
    "emit only tokens that are novel vs retrieved span (no contiguous "
    "span copy) AND in code-teacher top-k at that step; pure span copy "
    "→ label PEAK (zero gen credit); no novel teacher-consistent "
    "continue → ABSTAIN; wall_ms/n_new ≠ content_ok; not a NANOGEN6 "
    "refuse-or-continue rename; bar = true_continue_ablated PROMOTE "
    "else HOLD"
)

AW0_SAFE_NOTE = (
    "SAFE / ADVSAFE false-hit score ≠ answer quality; "
    "SAFE = no wrong gold only (anti-FP); "
    "gold-substring / gibberish-tail / truncate-to-span ≠ "
    "generative PROMOTE"
)

AW0_ANTI_FP = (
    "LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; "
    "never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; "
    "truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; "
    "eval path = prod ask path; generative bar = AW3 only; "
    "no vanity re-SEMFIX/ADVSAFE unless PRODKEEP fails; "
    "no Wave AX invent; no CTX/SMART/FAST clone; "
    "no NANOGEN7 = NANOGEN6+rename; TAC ≠ refuse-or-continue clone"
)

AW0_TRUE_GEN_JUDGE: Mapping[str, object] = {
    "stage": "AW3 H-NANOGEN7 applies; AW0 freezes judge law",
    "gold_substring_insufficient": True,
    "gibberish_tail_fails": True,
    "span_fallback_neq_gen": True,
    "telemetry_neq_content_ok": True,
    "usable_continue_required": True,
    "teacher_topk_gate": True,
    "novel_vs_span_required": True,
    "scoring": "short_answer_f1_or_hitl_true_continue_only",
    "nanogen6_refuse_or_continue_archived": True,
    "nanogen5_truncate_bar_archived": True,
    "archived_nanogen5_strict": 5.5,
    "promote_bar": "true_continue_ablated else HOLD",
}

AW0_PRODUCT_KEEP_CHARTER: Mapping[str, object] = {
    "stage": "AW1 H-PRODKEEP closes bars; AW0 freezes charter",
    "cite_av_locks": sorted(AW0_CITED_AV_LOCKS),
    "accept_artifact": (
        "known-ask + robust SEMWRAP + labeled PEAK/RAG + apps "
        "(AV H-PRODSHIP·H-SHIPUI2 locks hold)"
    ),
    "debts": [
        {
            "id": "product_regression_hold",
            "evidence": "AV Caminho A PROMOTE; must not regress under pressure",
            "fix": "hold para·FH·modes·DECODE content·latency·KB",
            "bar": "regression_hold vs AV PRODSHIP/SHIPUI2",
        },
        {
            "id": "pressure_human_para",
            "evidence": "AV external para closed; need ≠ AV/AU pressure set",
            "fix": "held-out pressure N≥20 paraphrase set ≠ AV/AU packs",
            "bar": "para_hit_min on pressure held-out set",
        },
        {
            "id": "false_hit_zero",
            "evidence": "AV FH 0 on ask path; must hold",
            "fix": "hard FH 0 on default ask path",
            "bar": "false_hit_max=0",
        },
        {
            "id": "mode_ui_always",
            "evidence": "SHIPUI2 modes+content PROMOTE",
            "fix": "always print mode=LOOKUP|PEAK|DECODE|ABSTAIN",
            "bar": "modes_visible 4/4",
        },
        {
            "id": "true_continue_unmet",
            "evidence": "H-NANOGEN6 HOLD true_continue=0",
            "fix": "NANOGEN7 TAC must be new method (not rename)",
            "bar": "tac_method_distinct; true_continue_ablated gate",
        },
        {
            "id": "span_fallback_neq_gen",
            "evidence": "AV law: span-fallback ≠ gen IQ",
            "fix": "pure span copy labeled PEAK; zero gen credit",
            "bar": "span_fallback_neq_gen True",
        },
    ],
    "metrics": [
        "para_hit",
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
        "para_hit_min": 0.70,
        "false_hit_max": 0,
        "modes_required": list(AW0_LATENCY_PATHS),
        "pressure_para_min_n": 20,
        "decode_gibberish_neq_content_ok": True,
        "default_ask_near_miss": "ABSTAIN",
        "default_ask_ood": "ABSTAIN",
        "latency_publish": True,
        "kb_holes_publish": True,
        "eval_eq_prod_ask": True,
        "regression_hold": True,
    },
    "baselines": {
        "prodship_external_para": "PROMOTE",
        "shipui2_modes_content": "PROMOTE",
        "nanogen6_true_continue": 0.0,
        "nanogen6_decision": "HOLD",
        "av_real_eval_battery": "8/8",
        "ship_lock": AW0_SHIP_LOCK,
    },
    "runners": [
        "nano:z:ask",
        "nano:prodship",
        "nano:shipui2",
        "nano:nanogen6",
        "nano:advsafe",
        "nano:metrics",
        "nano:askabstain",
    ],
    "no_reopen_unless_fail": ["H-SEMFIX", "H-ADVSAFE", "H-PRODSHIP", "H-SHIPUI2"],
    "complete_kb_claim_forbidden": True,
}

AW0_PRESSURE_PARA_ROWS: tuple[dict[str, str], ...] = (
    {
        "id": "AW-PARA-01",
        "parent": "add",
        "question": (
            "Pressure set: please author add(a,b) that returns the integer sum only."
        ),
    },
    {
        "id": "AW-PARA-02",
        "parent": "add",
        "question": (
            "Wave-AW human: tiny Python add for ints a and b → total."
        ),
    },
    {
        "id": "AW-PARA-03",
        "parent": "add",
        "question": (
            "Post-AV phrasing: implement add combining two integers into their sum."
        ),
    },
    {
        "id": "AW-PARA-04",
        "parent": "add",
        "question": (
            "New pressure: code named add; args a,b; output a+b as int."
        ),
    },
    {
        "id": "AW-PARA-05",
        "parent": "add",
        "question": (
            "Held-out AW: write add so two whole numbers come back summed."
        ),
    },
    {
        "id": "AW-PARA-06",
        "parent": "add",
        "question": (
            "External AW pack: helper add(a:int,b:int) yielding arithmetic sum."
        ),
    },
    {
        "id": "AW-PARA-07",
        "parent": "add",
        "question": (
            "Fresh pressure ask: shortest add for integer pair a,b returning sum."
        ),
    },
    {
        "id": "AW-PARA-08",
        "parent": "add",
        "question": (
            "AW rewrite: define add that totals two int operands without fluff."
        ),
    },
    {
        "id": "AW-PARA-09",
        "parent": "add",
        "question": (
            "Outside AV pack: produce add returning combined ints a and b."
        ),
    },
    {
        "id": "AW-PARA-10",
        "parent": "add",
        "question": (
            "Pressure human: I need add(a, b) as plain integer addition."
        ),
    },
    {
        "id": "AW-PARA-11",
        "parent": "add",
        "question": (
            "AW held-out: sketch add for beginners summing two integer inputs."
        ),
    },
    {
        "id": "AW-PARA-12",
        "parent": "add",
        "question": (
            "New set: function add — take ints; return their addition result."
        ),
    },
    {
        "id": "AW-PARA-13",
        "parent": "add",
        "question": (
            "Post-freeze phrasing: supply add(a,b)->int computing a plus b."
        ),
    },
    {
        "id": "AW-PARA-14",
        "parent": "add",
        "question": (
            "AW pressure: create integer adder called add with two arguments."
        ),
    },
    {
        "id": "AW-PARA-15",
        "parent": "add",
        "question": (
            "Distinct human: code add that outputs the sum of a and b only."
        ),
    },
    {
        "id": "AW-PARA-16",
        "parent": "add",
        "question": (
            "Wave AW: minimal add helper — inputs two ints; result is sum."
        ),
    },
    {
        "id": "AW-PARA-17",
        "parent": "add",
        "question": (
            "Pressure N≥20: write add returning the total of integers a,b."
        ),
    },
    {
        "id": "AW-PARA-18",
        "parent": "add",
        "question": (
            "Outside packs: implement add for int pair with return a+b."
        ),
    },
    {
        "id": "AW-PARA-19",
        "parent": "add",
        "question": (
            "AW-only wording: make add that sums two whole-number args."
        ),
    },
    {
        "id": "AW-PARA-20",
        "parent": "add",
        "question": (
            "Final pressure: brief add(a,b) Python — purpose is integer sum."
        ),
    },
)

AW0_PRESSURE_PARA_PROTOCOL: Mapping[str, object] = {
    "stage": "AW1 H-PRODKEEP scores; AW0 freezes protocol",
    "held_out": True,
    "bank_stuff_forbidden": True,
    "neq_av_pack": True,
    "neq_au_pack": True,
    "source": "human / pressure rewrite (≠ AV-PARA · ≠ AU-PARA)",
    "min_n": 20,
    "scoring": "hit rate on default ask path (SEMWRAP)",
    "path": "nano:z:ask --wrap --semwrap",
    "rows": list(AW0_PRESSURE_PARA_ROWS),
}

AW0_REAL_EVAL_PROTOCOL: Mapping[str, object] = {
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
    "eval_eq_prod_ask": True,
    "answer_usability_scored": True,
    "gen_claim_rule": (
        "only if AW3 H-NANOGEN7 PROMOTE (true_continue_ablated; "
        "TAC; span-fallback ≠ gen credit)"
    ),
    "mini_agi_rule": "forbidden while NANOGEN7 HOLD",
    "stage": "AW4 AW-REAL-EVAL scores; AW0 freezes protocol",
}

AW0_ASK_BATTERY: tuple[dict[str, str], ...] = (
    {
        "id": "AW-ASK-01",
        "kind": "known_lookup",
        "expect_mode": "LOOKUP",
        "question": (
            "Write a short Python function named add that returns the sum of two integers a and b."
        ),
    },
    {
        "id": "AW-ASK-02",
        "kind": "ood_abstain",
        "expect_mode": "ABSTAIN",
        "question": "Which chef won the 2019 World Cup of Baking?",
    },
    {
        "id": "AW-ASK-03",
        "kind": "near_miss",
        "expect_mode": "ABSTAIN",
        "question": (
            "BIP-39 entropy formula is CS = ENT / 32 — confirm for SegWit witness discount?"
        ),
    },
    {
        "id": "AW-ASK-04",
        "kind": "labeled_peak",
        "expect_mode": "PEAK",
        "question": (
            "From the curated Rust book intro, extract one sentence on ownership (label PEAK, not open chat)."
        ),
    },
    {
        "id": "AW-ASK-05",
        "kind": "decode_content",
        "expect_mode": "DECODE",
        "question": (
            "Write a short Python function named add that returns the sum of two integers a and b."
        ),
    },
    {
        "id": "AW-ASK-06",
        "kind": "junk_trap",
        "expect_mode": "ABSTAIN",
        "question": ".",
    },
    {
        "id": "AW-ASK-07",
        "kind": "human_para",
        "expect_mode": "LOOKUP",
        "question": (
            "Pressure set: please author add(a,b) that returns the integer sum only."
        ),
    },
    {
        "id": "AW-ASK-08",
        "kind": "decode_gibberish_bar",
        "expect_mode": "DECODE",
        "question": "Explain Merkle trees briefly",
    },
)


def map_aw_product_mode(raw_mode: str) -> str:
    """
    GIVEN raw telemetry mode string
    WHEN applying AW0 mode charter (inherits AU0/AV0 aliases)
    THEN return LOOKUP | PEAK | DECODE | ABSTAIN | UNKNOWN.
    """
    return map_au_product_mode(raw_mode)


def _gate_modes() -> str | None:
    if set(AW0_LATENCY_PATHS) != AW0_MODES:
        return "KILL (latency paths ≠ mode charter)"
    if "ABSTAIN" not in AW0_MODES:
        return "KILL (ABSTAIN missing from modes)"
    return None


def _gate_cited_av() -> str | None:
    cited = AW0_PRODUCT_KEEP_CHARTER.get("cite_av_locks")
    if not isinstance(cited, list):
        return "KILL (product-keep must cite AV locks)"
    if set(cited) != AW0_CITED_AV_LOCKS:
        return "KILL (product-keep AV lock citations incomplete)"
    return None


def _gate_debt_ids() -> str | None:
    debts = AW0_PRODUCT_KEEP_CHARTER.get("debts")
    if not isinstance(debts, list) or len(debts) < 6:
        return "KILL (product-keep must list ≥6 post-AV debts)"
    ids = {str(d.get("id", "")) for d in debts if isinstance(d, dict)}
    need = {
        "product_regression_hold",
        "pressure_human_para",
        "false_hit_zero",
        "mode_ui_always",
        "true_continue_unmet",
        "span_fallback_neq_gen",
    }
    if not need.issubset(ids):
        return "KILL (product-keep debt ids incomplete)"
    return None


def _gate_debt_bars() -> str | None:
    bars = AW0_PRODUCT_KEEP_CHARTER.get("bars")
    if not isinstance(bars, dict):
        return "KILL (product-keep bars missing)"
    if float(bars.get("para_hit_min", -1)) < 0.70:
        return "KILL (product-keep para_hit_min must be ≥0.70)"
    if int(bars.get("false_hit_max", 1)) != 0:
        return "KILL (product-keep false_hit_max must be 0)"
    if int(bars.get("pressure_para_min_n", 0)) < 20:
        return "KILL (product-keep pressure_para_min_n must be ≥20)"
    if not bool(bars.get("decode_gibberish_neq_content_ok")):
        return "KILL (DECODE gibberish≠content_ok bar missing)"
    if str(bars.get("default_ask_near_miss", "")) != "ABSTAIN":
        return "KILL (near_miss on default ask must be ABSTAIN)"
    if not bool(bars.get("eval_eq_prod_ask")):
        return "KILL (eval path must equal prod ask path)"
    if not bool(bars.get("regression_hold")):
        return "KILL (product-keep must require regression_hold)"
    modes = bars.get("modes_required")
    if not isinstance(modes, list) or set(modes) != AW0_MODES:
        return "KILL (product-keep modes_required incomplete)"
    return None


def _gate_debt_metrics() -> str | None:
    metrics = AW0_PRODUCT_KEEP_CHARTER.get("metrics")
    need_m = {
        "para_hit",
        "false_hit",
        "p50_wall_ms",
        "p99_wall_ms",
        "decode_content_ok",
        "true_continue_ablated",
    }
    if not isinstance(metrics, list) or not need_m.issubset(set(metrics)):
        return "KILL (product-keep metrics incomplete)"
    return None


def _gate_product_keep() -> str | None:
    return _gate_debt_ids() or _gate_debt_bars() or _gate_debt_metrics()


def _prior_para_questions() -> set[str]:
    au = {str(p.get("question", "")).strip() for p in AU0_HUMAN_PARA_ROWS}
    av = {str(p.get("question", "")).strip() for p in AV0_EXTERNAL_PARA_ROWS}
    return au | av


def _gate_para_rows() -> str | None:
    ids: set[str] = set()
    prior = _prior_para_questions()
    for item in AW0_PRESSURE_PARA_ROWS:
        tid = str(item.get("id", ""))
        if not tid.startswith("AW-PARA-"):
            return f"KILL (bad pressure-para id: {tid})"
        if tid in ids:
            return f"KILL (duplicate pressure-para id: {tid})"
        ids.add(tid)
        q = str(item.get("question", "")).strip()
        if not q:
            return f"KILL (empty pressure-para question: {tid})"
        if q in prior:
            return f"KILL (pressure-para reuses AV/AU pack: {tid})"
    return None


def _gate_pressure_para() -> str | None:
    proto = AW0_PRESSURE_PARA_PROTOCOL
    if not bool(proto.get("held_out")):
        return "KILL (pressure-para must be held-out)"
    if not bool(proto.get("bank_stuff_forbidden")):
        return "KILL (pressure-para must forbid bank stuffing)"
    if not bool(proto.get("neq_av_pack")):
        return "KILL (pressure-para must be ≠ AV pack)"
    if not bool(proto.get("neq_au_pack")):
        return "KILL (pressure-para must be ≠ AU pack)"
    rows = proto.get("rows")
    min_n = int(proto.get("min_n", 20))
    if min_n < 20:
        return "KILL (pressure-para min_n must be ≥20)"
    if not isinstance(rows, list) or len(rows) < min_n:
        return f"KILL (pressure-para must have ≥{min_n} rows)"
    if len(AW0_PRESSURE_PARA_ROWS) < min_n:
        return "KILL (AW0_PRESSURE_PARA_ROWS below min_n)"
    return _gate_para_rows()


def _gate_nanogen7_hyp() -> str | None:
    hyp = AW0_NANOGEN7_HYPOTHESIS
    low = hyp.lower()
    if "tac" not in low and "teacher" not in low:
        return "KILL (NANOGEN7 hyp must state TAC / teacher-anchored)"
    if "true_continue" not in low and "ablated" not in low:
        return "KILL (NANOGEN7 hyp must state true continue / ablated)"
    if "novel" not in low:
        return "KILL (NANOGEN7 hyp must require novel vs span)"
    if "span" not in low and "truncate" not in low:
        return "KILL (NANOGEN7 hyp must reject span-fallback as gen)"
    if "peak" not in low and "fallback" not in low:
        return "KILL (NANOGEN7 hyp must label PEAK fallback)"
    if "nanogen6" not in low:
        return "KILL (NANOGEN7 hyp must reject NANOGEN6 rename)"
    if "rename" not in low and "refuse-or-continue" not in low:
        return "KILL (NANOGEN7 hyp must forbid NANOGEN6 refuse-or-continue rename)"
    if "teacher" not in low and "top-k" not in low and "topk" not in low:
        return "KILL (NANOGEN7 hyp must use teacher top-k gate)"
    if "bank-grounded short" in low:
        return "KILL (NANOGEN7 must not reuse bank-grounded short)"
    return None


def _gate_nanogen7_judge() -> str | None:
    judge = AW0_TRUE_GEN_JUDGE
    if not bool(judge.get("span_fallback_neq_gen")):
        return "KILL (true judge must mark span-fallback ≠ gen)"
    if not bool(judge.get("gold_substring_insufficient")):
        return "KILL (true judge must mark gold-substring insufficient)"
    if not bool(judge.get("gibberish_tail_fails")):
        return "KILL (true judge must fail gibberish tail)"
    if not bool(judge.get("telemetry_neq_content_ok")):
        return "KILL (true judge must mark telemetry ≠ content_ok)"
    if not bool(judge.get("teacher_topk_gate")):
        return "KILL (true judge must require teacher top-k gate)"
    if not bool(judge.get("novel_vs_span_required")):
        return "KILL (true judge must require novel vs span)"
    if not bool(judge.get("nanogen6_refuse_or_continue_archived")):
        return "KILL (true judge must archive NANOGEN6 refuse-or-continue)"
    scoring = str(judge.get("scoring", ""))
    if "true_continue" not in scoring:
        return "KILL (true judge scoring must be true_continue only)"
    return None


def _gate_nanogen7() -> str | None:
    return _gate_nanogen7_hyp() or _gate_nanogen7_judge()


def _gate_real_eval_flags() -> str | None:
    proto = AW0_REAL_EVAL_PROTOCOL
    flags = (
        ("live_ask_battery", "KILL (real-eval must require live ask battery)"),
        ("summary_only_forbidden", "KILL (real-eval must forbid summary-only)"),
        ("wall_ms_n_new_mandatory", "KILL (real-eval must require wall_ms/n_new)"),
        ("eval_eq_prod_ask", "KILL (real-eval must require eval=prod ask)"),
        ("gold_substring_neq_gen", "KILL (real-eval must reject gold-substring as gen)"),
        ("gibberish_tail_fails", "KILL (real-eval must fail gibberish tail)"),
        ("span_fallback_neq_gen", "KILL (real-eval must reject span-fallback as gen)"),
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
    claim = str(AW0_REAL_EVAL_PROTOCOL.get("gen_claim_rule", "")).lower()
    if "nanogen7" not in claim:
        return "KILL (real-eval gen_claim_rule incomplete)"
    if "span" not in claim and "fallback" not in claim:
        return "KILL (real-eval must forbid span-fallback gen credit)"
    if "tac" not in claim:
        return "KILL (real-eval gen_claim_rule must name TAC)"
    return None


def _scan_battery_row(
    item: Mapping[str, str], ids: set[str]
) -> tuple[str | None, str, str]:
    tid = str(item.get("id", ""))
    if not tid.startswith("AW-ASK-"):
        return f"KILL (bad battery id: {tid})", "", ""
    if tid in ids:
        return f"KILL (duplicate battery id: {tid})", "", ""
    q = str(item.get("question", ""))
    if tid != "AW-ASK-06" and not q.strip():
        return f"KILL (empty battery question: {tid})", "", ""
    mode = str(item.get("expect_mode", ""))
    if mode not in AW0_MODES:
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
    if modes_seen != AW0_MODES:
        return f"KILL (ask battery modes incomplete: {sorted(modes_seen)})"
    need_kinds = {
        "near_miss",
        "human_para",
        "labeled_peak",
        "junk_trap",
        "decode_content",
    }
    if not need_kinds.issubset(kinds):
        return "KILL (ask battery must cover product-keep kinds)"
    return None


def _gate_notes() -> str | None:
    if "≠" not in AW0_SAFE_NOTE and "!=" not in AW0_SAFE_NOTE:
        return "KILL (SAFE≠quality note missing)"
    if "LOOKUP" not in AW0_ANTI_FP:
        return "KILL (anti-FP charter incomplete)"
    if "eval path = prod" not in AW0_ANTI_FP.lower():
        return "KILL (anti-FP must require eval=prod ask)"
    if "truncate-to-span" not in AW0_ANTI_FP.lower():
        return "KILL (anti-FP must forbid truncate-to-span as gen)"
    if "≤5M" not in AW0_NORTH_STAR:
        return "KILL (north-star charter incomplete)"
    if "NANOGEN7" not in AW0_NORTH_STAR and "H-NANOGEN7" not in AW0_NORTH_STAR:
        return "KILL (north-star must name H-NANOGEN7)"
    if "TAC" not in AW0_NORTH_STAR and "teacher" not in AW0_NORTH_STAR.lower():
        return "KILL (north-star must name TAC / teacher-anchored)"
    if "gibberish-tail" not in AW0_SHIP_LOCK:
        return "KILL (ship lock must keep AU STRICT gibberish-tail claim)"
    return None


def _gate_charters() -> str | None:
    return (
        _gate_modes()
        or _gate_cited_av()
        or _gate_product_keep()
        or _gate_pressure_para()
        or _gate_nanogen7()
        or _gate_real_eval()
        or _gate_notes()
    )


def decide_aw0_session(
    *,
    trials_dir_ready: bool,
    anti_fp_signed: bool,
    battery: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN product-keep/pressure-para/NANOGEN7/real-eval charters + trials + anti-FP
    WHEN applying AW0 SESSION gate
    THEN PROMOTE iff AV locks cited, charters valid, battery covers 4 modes,
         trials ready, anti-FP signed.
    """
    rows = list(battery) if battery is not None else list(AW0_ASK_BATTERY)
    err = _gate_charters() or _gate_battery(rows)
    if err:
        return err
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-aw/trials/ not ready)"
    return f"PROMOTE ({AW0_ID}: {AW0_THESIS})"
