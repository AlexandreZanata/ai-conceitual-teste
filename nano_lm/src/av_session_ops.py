"""Wave AV0 SESSION: freeze product-ship · external-para · NANOGEN6 · true-eval."""

from __future__ import annotations

from typing import Mapping, Sequence

from au_session_ops import AU0_HUMAN_PARA_ROWS, AU0_MODES, map_au_product_mode

__all__ = [
    "AV0_ID",
    "AV0_THESIS",
    "AV0_MODES",
    "AV0_LATENCY_PATHS",
    "AV0_CITED_AU_LOCKS",
    "AV0_PRODUCT_SHIP_CHARTER",
    "AV0_EXTERNAL_PARA_PROTOCOL",
    "AV0_EXTERNAL_PARA_ROWS",
    "AV0_NANOGEN6_HYPOTHESIS",
    "AV0_TRUE_GEN_JUDGE",
    "AV0_REAL_EVAL_PROTOCOL",
    "AV0_ASK_BATTERY",
    "AV0_SAFE_NOTE",
    "AV0_ANTI_FP",
    "AV0_NORTH_STAR",
    "AV0_SHIP_LOCK",
    "map_av_product_mode",
    "decide_av0_session",
]

AV0_ID = "AV0-SESSION"
AV0_THESIS = (
    "Wave AV OPEN: freeze product-ship charter · external-para "
    "protocol (N≥20 ≠ AU) · NANOGEN6 hyp (true continue; "
    "span-fallback ≠ gen IQ) · real-eval protocol; next AV1 "
    "H-PRODSHIP (not CTX/SMART/FAST clone · not NANOGEN5 rename)"
)

AV0_MODES: frozenset[str] = AU0_MODES
AV0_LATENCY_PATHS: tuple[str, ...] = (
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
)

AV0_CITED_AU_LOCKS: frozenset[str] = frozenset(
    {
        "H-PRODHARD",
        "H-SHIPREAL",
        "H-NANOGEN5",
        "AU-REAL-EVAL",
        "AU-FREEZE",
    }
)

AV0_SHIP_LOCK = (
    "AF packaged stack + AQ product layer + AS trust path + "
    "ablated DECODE (snippet-prefix + gibberish-tail STRICT) — "
    "not unlabeled open chat LM"
)

AV0_NORTH_STAR = (
    "Nano generative / mini-AGI-inspired ≤5M: ship Caminho A "
    "(PRODSHIP + SHIPUI2) now; true ablated DECODE (H-NANOGEN6) "
    "without span-fallback-as-IQ before generative or mini-AGI claim"
)

AV0_NANOGEN6_HYPOTHESIS = (
    "One idea: refuse-or-continue DECODE with fallback labeling — "
    "score only novel readable continue tokens; truncate-to-retrieved-"
    "span must label PEAK/LOOKUP fallback (zero gen credit); "
    "gibberish → ABSTAIN; wall_ms/n_new ≠ content_ok; not a "
    "NANOGEN5 5.5 truncate-bar clone; bar = true_continue_ablated "
    "PROMOTE else HOLD"
)

AV0_SAFE_NOTE = (
    "SAFE / ADVSAFE false-hit score ≠ answer quality; "
    "SAFE = no wrong gold only (anti-FP); "
    "gold-substring / gibberish-tail / truncate-to-span ≠ "
    "generative PROMOTE"
)

AV0_ANTI_FP = (
    "LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; "
    "never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; "
    "truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; "
    "eval path = prod ask path; generative bar = AV3 only; "
    "no vanity re-SEMFIX/ADVSAFE unless PRODSHIP fails; "
    "no Wave AW invent; no CTX/SMART/FAST clone; "
    "no NANOGEN6 = NANOGEN5+rename"
)

AV0_TRUE_GEN_JUDGE: Mapping[str, object] = {
    "stage": "AV3 H-NANOGEN6 applies; AV0 freezes judge law",
    "gold_substring_insufficient": True,
    "gibberish_tail_fails": True,
    "span_fallback_neq_gen": True,
    "telemetry_neq_content_ok": True,
    "usable_continue_required": True,
    "scoring": "short_answer_f1_or_hitl_true_continue_only",
    "nanogen5_truncate_bar_archived": True,
    "archived_nanogen5_strict": 5.5,
    "promote_bar": "true_continue_ablated else HOLD",
}

AV0_PRODUCT_SHIP_CHARTER: Mapping[str, object] = {
    "stage": "AV1 H-PRODSHIP closes bars; AV0 freezes charter",
    "cite_au_locks": sorted(AV0_CITED_AU_LOCKS),
    "accept_artifact": (
        "known-ask + robust SEMWRAP + labeled PEAK/RAG + apps"
    ),
    "debts": [
        {
            "id": "decode_content_ok",
            "evidence": "AU-ASK-05 gibberish WRAP_DECODE content_ok=true",
            "fix": "DECODE usable text or ABSTAIN (gibberish fails)",
            "bar": "usable_or_abstain; gibberish≠content_ok",
        },
        {
            "id": "external_human_para",
            "evidence": "AU para pack closed; need outside-set humans",
            "fix": "held-out external N≥20 paraphrase set ≠ AU pack",
            "bar": "para_hit_min on external held-out set",
        },
        {
            "id": "false_hit_zero",
            "evidence": "ADVSAFE FH 0; must hold on production ask",
            "fix": "hard FH 0 on default ask path",
            "bar": "false_hit_max=0",
        },
        {
            "id": "mode_ui_always",
            "evidence": "ship/demo must show mode banner",
            "fix": "always print mode=LOOKUP|PEAK|DECODE|ABSTAIN",
            "bar": "modes_visible 4/4",
        },
        {
            "id": "kb_holes_honest",
            "evidence": "open-world / multi-lang / tool-use listed",
            "fix": "coverage % + hole list every stage",
            "bar": "kb_holes_publish; no overclaim",
        },
        {
            "id": "latency_publish",
            "evidence": "PRODHARD board published",
            "fix": "republish p50/p99 every product stage",
            "bar": "latency_publish True",
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
    ],
    "bars": {
        "para_hit_min": 0.70,
        "false_hit_max": 0,
        "modes_required": list(AV0_LATENCY_PATHS),
        "external_para_min_n": 20,
        "decode_gibberish_neq_content_ok": True,
        "default_ask_near_miss": "ABSTAIN",
        "default_ask_ood": "ABSTAIN",
        "latency_publish": True,
        "kb_holes_publish": True,
        "eval_eq_prod_ask": True,
    },
    "baselines": {
        "prodhard_para_hit": 1.0,
        "advsafe_false_hit": "0/20",
        "nanogen5_strict_ablated": 5.5,
        "ship_lock": AV0_SHIP_LOCK,
    },
    "runners": [
        "nano:z:ask",
        "nano:prodhard",
        "nano:shipreal",
        "nano:advsafe",
        "nano:metrics",
        "nano:askabstain",
        "nano:shipui",
    ],
    "no_reopen_unless_fail": ["H-SEMFIX", "H-ADVSAFE"],
    "complete_kb_claim_forbidden": True,
}

# External held-out paraphrases — must not reuse AU-PARA question text.
AV0_EXTERNAL_PARA_ROWS: tuple[dict[str, str], ...] = (
    {
        "id": "AV-PARA-01",
        "parent": "add",
        "question": (
            "Outside AU pack: craft a minimal add(a, b) that sums two "
            "integers and returns the total."
        ),
    },
    {
        "id": "AV-PARA-02",
        "parent": "add",
        "question": (
            "External human: I want Python code for adding integers a "
            "and b under the name add."
        ),
    },
    {
        "id": "AV-PARA-03",
        "parent": "add",
        "question": (
            "Held-out phrasing: show me add for two whole numbers that "
            "outputs their sum."
        ),
    },
    {
        "id": "AV-PARA-04",
        "parent": "add",
        "question": (
            "New wording: implement a two-argument integer adder called "
            "add returning a+b."
        ),
    },
    {
        "id": "AV-PARA-05",
        "parent": "add",
        "question": (
            "Fresh ask: small helper add — take ints a,b; give back "
            "their addition result."
        ),
    },
    {
        "id": "AV-PARA-06",
        "parent": "add",
        "question": (
            "Non-AU rewrite: please code add(a:int,b:int)->int as the "
            "sum of the pair."
        ),
    },
    {
        "id": "AV-PARA-07",
        "parent": "add",
        "question": (
            "Different human: write add so beginners can sum two "
            "integer inputs."
        ),
    },
    {
        "id": "AV-PARA-08",
        "parent": "add",
        "question": (
            "External set: define add combining integer operands a "
            "with b into one sum."
        ),
    },
    {
        "id": "AV-PARA-09",
        "parent": "add",
        "question": (
            "Outside pack: a tiny Python add that returns the total of "
            "two ints named a and b."
        ),
    },
    {
        "id": "AV-PARA-10",
        "parent": "add",
        "question": (
            "New human phrasing: function add — inputs two integers; "
            "output is their sum."
        ),
    },
    {
        "id": "AV-PARA-11",
        "parent": "add",
        "question": (
            "Held-out: can you supply add(a, b) returning integer "
            "addition of a plus b?"
        ),
    },
    {
        "id": "AV-PARA-12",
        "parent": "add",
        "question": (
            "External: sketch an adder named add for int pair a,b "
            "with return a+b."
        ),
    },
    {
        "id": "AV-PARA-13",
        "parent": "add",
        "question": (
            "Non-AU ask: produce short code titled add that sums two "
            "integer arguments."
        ),
    },
    {
        "id": "AV-PARA-14",
        "parent": "add",
        "question": (
            "Fresh external: I need add to compute the sum for two "
            "ints without extras."
        ),
    },
    {
        "id": "AV-PARA-15",
        "parent": "add",
        "question": (
            "Outside AU: write the smallest add helper for integers a "
            "and b returning sum."
        ),
    },
    {
        "id": "AV-PARA-16",
        "parent": "add",
        "question": (
            "Human held-out: create add that accepts two ints and "
            "yields their arithmetic sum."
        ),
    },
    {
        "id": "AV-PARA-17",
        "parent": "add",
        "question": (
            "External rewrite: Python add(a, b) — purpose is summing "
            "two integers only."
        ),
    },
    {
        "id": "AV-PARA-18",
        "parent": "add",
        "question": (
            "New set: implement integer addition under function name "
            "add with args a,b."
        ),
    },
    {
        "id": "AV-PARA-19",
        "parent": "add",
        "question": (
            "Outside pack phrasing: give me add returning the combined "
            "value of ints a and b."
        ),
    },
    {
        "id": "AV-PARA-20",
        "parent": "add",
        "question": (
            "External N≥20 closer: code a brief add for two whole "
            "numbers a,b → sum."
        ),
    },
)

AV0_EXTERNAL_PARA_PROTOCOL: Mapping[str, object] = {
    "stage": "AV1 H-PRODSHIP scores; AV0 freezes protocol",
    "held_out": True,
    "bank_stuff_forbidden": True,
    "neq_au_pack": True,
    "source": "human / external rewrite (≠ AU-PARA)",
    "min_n": 20,
    "scoring": "hit rate on default ask path (SEMWRAP)",
    "path": "nano:z:ask --wrap --semwrap",
    "rows": list(AV0_EXTERNAL_PARA_ROWS),
}

AV0_REAL_EVAL_PROTOCOL: Mapping[str, object] = {
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
        "only if AV3 H-NANOGEN6 PROMOTE (true_continue_ablated; "
        "span-fallback ≠ gen credit)"
    ),
    "mini_agi_rule": "forbidden while NANOGEN6 HOLD",
    "stage": "AV4 AV-REAL-EVAL scores; AV0 freezes protocol",
}

AV0_ASK_BATTERY: tuple[dict[str, str], ...] = (
    {
        "id": "AV-ASK-01",
        "kind": "known_lookup",
        "expect_mode": "LOOKUP",
        "question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
    },
    {
        "id": "AV-ASK-02",
        "kind": "ood_abstain",
        "expect_mode": "ABSTAIN",
        "question": "Which chef won the 2019 World Cup of Baking?",
    },
    {
        "id": "AV-ASK-03",
        "kind": "near_miss",
        "expect_mode": "ABSTAIN",
        "question": (
            "BIP-39 entropy formula is CS = ENT / 32 — confirm for "
            "SegWit witness discount?"
        ),
    },
    {
        "id": "AV-ASK-04",
        "kind": "labeled_peak",
        "expect_mode": "PEAK",
        "question": (
            "From the curated Rust book intro, extract one sentence on "
            "ownership (label PEAK, not open chat)."
        ),
    },
    {
        "id": "AV-ASK-05",
        "kind": "decode_content",
        "expect_mode": "DECODE",
        "question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
    },
    {
        "id": "AV-ASK-06",
        "kind": "junk_trap",
        "expect_mode": "ABSTAIN",
        "question": ".",
    },
    {
        "id": "AV-ASK-07",
        "kind": "human_para",
        "expect_mode": "LOOKUP",
        "question": (
            "Outside AU pack: craft a minimal add(a, b) that sums two "
            "integers and returns the total."
        ),
    },
    {
        "id": "AV-ASK-08",
        "kind": "decode_gibberish_bar",
        "expect_mode": "DECODE",
        "question": "Explain Merkle trees briefly",
    },
)


def map_av_product_mode(raw_mode: str) -> str:
    """
    GIVEN raw telemetry mode string
    WHEN applying AV0 mode charter (inherits AU0/AT0/AS0 aliases)
    THEN return LOOKUP | PEAK | DECODE | ABSTAIN | UNKNOWN.
    """
    return map_au_product_mode(raw_mode)


def _gate_modes() -> str | None:
    if set(AV0_LATENCY_PATHS) != AV0_MODES:
        return "KILL (latency paths ≠ mode charter)"
    if "ABSTAIN" not in AV0_MODES:
        return "KILL (ABSTAIN missing from modes)"
    return None


def _gate_cited_au() -> str | None:
    cited = AV0_PRODUCT_SHIP_CHARTER.get("cite_au_locks")
    if not isinstance(cited, list):
        return "KILL (product-ship must cite AU locks)"
    if set(cited) != AV0_CITED_AU_LOCKS:
        return "KILL (product-ship AU lock citations incomplete)"
    return None


def _gate_debt_ids() -> str | None:
    debts = AV0_PRODUCT_SHIP_CHARTER.get("debts")
    if not isinstance(debts, list) or len(debts) < 6:
        return "KILL (product-ship must list ≥6 post-AU debts)"
    ids = {str(d.get("id", "")) for d in debts if isinstance(d, dict)}
    need = {
        "decode_content_ok",
        "external_human_para",
        "false_hit_zero",
        "mode_ui_always",
        "kb_holes_honest",
        "latency_publish",
    }
    if not need.issubset(ids):
        return "KILL (product-ship debt ids incomplete)"
    return None


def _gate_debt_bars() -> str | None:
    bars = AV0_PRODUCT_SHIP_CHARTER.get("bars")
    if not isinstance(bars, dict):
        return "KILL (product-ship bars missing)"
    if float(bars.get("para_hit_min", -1)) < 0.70:
        return "KILL (product-ship para_hit_min must be ≥0.70)"
    if int(bars.get("false_hit_max", 1)) != 0:
        return "KILL (product-ship false_hit_max must be 0)"
    if int(bars.get("external_para_min_n", 0)) < 20:
        return "KILL (product-ship external_para_min_n must be ≥20)"
    if not bool(bars.get("decode_gibberish_neq_content_ok")):
        return "KILL (DECODE gibberish≠content_ok bar missing)"
    if str(bars.get("default_ask_near_miss", "")) != "ABSTAIN":
        return "KILL (near_miss on default ask must be ABSTAIN)"
    if not bool(bars.get("eval_eq_prod_ask")):
        return "KILL (eval path must equal prod ask path)"
    modes = bars.get("modes_required")
    if not isinstance(modes, list) or set(modes) != AV0_MODES:
        return "KILL (product-ship modes_required incomplete)"
    return None


def _gate_debt_metrics() -> str | None:
    metrics = AV0_PRODUCT_SHIP_CHARTER.get("metrics")
    need_m = {
        "para_hit",
        "false_hit",
        "p50_wall_ms",
        "p99_wall_ms",
        "decode_content_ok",
    }
    if not isinstance(metrics, list) or not need_m.issubset(set(metrics)):
        return "KILL (product-ship metrics incomplete)"
    return None


def _gate_product_ship() -> str | None:
    return _gate_debt_ids() or _gate_debt_bars() or _gate_debt_metrics()


def _au_para_questions() -> set[str]:
    return {str(p.get("question", "")).strip() for p in AU0_HUMAN_PARA_ROWS}


def _gate_para_rows() -> str | None:
    ids: set[str] = set()
    au_q = _au_para_questions()
    for item in AV0_EXTERNAL_PARA_ROWS:
        tid = str(item.get("id", ""))
        if not tid.startswith("AV-PARA-"):
            return f"KILL (bad external-para id: {tid})"
        if tid in ids:
            return f"KILL (duplicate external-para id: {tid})"
        ids.add(tid)
        q = str(item.get("question", "")).strip()
        if not q:
            return f"KILL (empty external-para question: {tid})"
        if q in au_q:
            return f"KILL (external-para reuses AU pack: {tid})"
    return None


def _gate_external_para() -> str | None:
    proto = AV0_EXTERNAL_PARA_PROTOCOL
    if not bool(proto.get("held_out")):
        return "KILL (external-para must be held-out)"
    if not bool(proto.get("bank_stuff_forbidden")):
        return "KILL (external-para must forbid bank stuffing)"
    if not bool(proto.get("neq_au_pack")):
        return "KILL (external-para must be ≠ AU pack)"
    rows = proto.get("rows")
    min_n = int(proto.get("min_n", 20))
    if min_n < 20:
        return "KILL (external-para min_n must be ≥20)"
    if not isinstance(rows, list) or len(rows) < min_n:
        return f"KILL (external-para must have ≥{min_n} rows)"
    if len(AV0_EXTERNAL_PARA_ROWS) < min_n:
        return "KILL (AV0_EXTERNAL_PARA_ROWS below min_n)"
    return _gate_para_rows()


def _gate_nanogen6_hyp() -> str | None:
    hyp = AV0_NANOGEN6_HYPOTHESIS
    low = hyp.lower()
    if "ablated" not in low and "true_continue" not in low:
        return "KILL (NANOGEN6 hyp must state true continue / ablated)"
    if "truncate" not in low and "span-fallback" not in low and "span" not in low:
        return "KILL (NANOGEN6 hyp must reject span-fallback as gen)"
    if "fallback" not in low and "peak/lookup" not in low:
        return "KILL (NANOGEN6 hyp must label PEAK/LOOKUP fallback)"
    if "nanogen5" not in low and "5.5" not in hyp:
        return "KILL (NANOGEN6 hyp must reject NANOGEN5 truncate clone)"
    if "clone" not in low and "rename" not in low:
        return "KILL (NANOGEN6 hyp must forbid truncate-bar clone)"
    if "f1" not in low and "hitl" not in low and "true_continue" not in low:
        return "KILL (NANOGEN6 hyp must use true-continue scoring)"
    if "bank-grounded short" in low:
        return "KILL (NANOGEN6 must not reuse bank-grounded short)"
    return None


def _gate_nanogen6_judge() -> str | None:
    judge = AV0_TRUE_GEN_JUDGE
    if not bool(judge.get("span_fallback_neq_gen")):
        return "KILL (true judge must mark span-fallback ≠ gen)"
    if not bool(judge.get("gold_substring_insufficient")):
        return "KILL (true judge must mark gold-substring insufficient)"
    if not bool(judge.get("gibberish_tail_fails")):
        return "KILL (true judge must fail gibberish tail)"
    if not bool(judge.get("telemetry_neq_content_ok")):
        return "KILL (true judge must mark telemetry ≠ content_ok)"
    if not bool(judge.get("nanogen5_truncate_bar_archived")):
        return "KILL (true judge must archive NANOGEN5 truncate bar)"
    scoring = str(judge.get("scoring", ""))
    if "true_continue" not in scoring:
        return "KILL (true judge scoring must be true_continue only)"
    return None


def _gate_nanogen6() -> str | None:
    return _gate_nanogen6_hyp() or _gate_nanogen6_judge()


def _gate_real_eval_flags() -> str | None:
    proto = AV0_REAL_EVAL_PROTOCOL
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
    claim = str(AV0_REAL_EVAL_PROTOCOL.get("gen_claim_rule", "")).lower()
    if "nanogen6" not in claim:
        return "KILL (real-eval gen_claim_rule incomplete)"
    if "span" not in claim and "fallback" not in claim:
        return "KILL (real-eval must forbid span-fallback gen credit)"
    return None


def _scan_battery_row(
    item: Mapping[str, str], ids: set[str]
) -> tuple[str | None, str, str]:
    tid = str(item.get("id", ""))
    if not tid.startswith("AV-ASK-"):
        return f"KILL (bad battery id: {tid})", "", ""
    if tid in ids:
        return f"KILL (duplicate battery id: {tid})", "", ""
    q = str(item.get("question", ""))
    if tid != "AV-ASK-06" and not q.strip():
        return f"KILL (empty battery question: {tid})", "", ""
    mode = str(item.get("expect_mode", ""))
    if mode not in AV0_MODES:
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
    if modes_seen != AV0_MODES:
        return f"KILL (ask battery modes incomplete: {sorted(modes_seen)})"
    need_kinds = {
        "near_miss",
        "human_para",
        "labeled_peak",
        "junk_trap",
        "decode_content",
    }
    if not need_kinds.issubset(kinds):
        return "KILL (ask battery must cover product-ship kinds)"
    return None


def _gate_notes() -> str | None:
    if "≠" not in AV0_SAFE_NOTE and "!=" not in AV0_SAFE_NOTE:
        return "KILL (SAFE≠quality note missing)"
    if "LOOKUP" not in AV0_ANTI_FP:
        return "KILL (anti-FP charter incomplete)"
    if "eval path = prod" not in AV0_ANTI_FP.lower():
        return "KILL (anti-FP must require eval=prod ask)"
    if "truncate-to-span" not in AV0_ANTI_FP.lower():
        return "KILL (anti-FP must forbid truncate-to-span as gen)"
    if "≤5M" not in AV0_NORTH_STAR:
        return "KILL (north-star charter incomplete)"
    if "NANOGEN6" not in AV0_NORTH_STAR and "H-NANOGEN6" not in AV0_NORTH_STAR:
        return "KILL (north-star must name H-NANOGEN6)"
    if "gibberish-tail" not in AV0_SHIP_LOCK:
        return "KILL (ship lock must keep AU STRICT gibberish-tail claim)"
    return None


def _gate_charters() -> str | None:
    return (
        _gate_modes()
        or _gate_cited_au()
        or _gate_product_ship()
        or _gate_external_para()
        or _gate_nanogen6()
        or _gate_real_eval()
        or _gate_notes()
    )


def decide_av0_session(
    *,
    trials_dir_ready: bool,
    anti_fp_signed: bool,
    battery: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN product-ship/external-para/NANOGEN6/real-eval charters + trials + anti-FP
    WHEN applying AV0 SESSION gate
    THEN PROMOTE iff AU locks cited, charters valid, battery covers 4 modes,
         trials ready, anti-FP signed.
    """
    rows = list(battery) if battery is not None else list(AV0_ASK_BATTERY)
    err = _gate_charters() or _gate_battery(rows)
    if err:
        return err
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-av/trials/ not ready)"
    return f"PROMOTE ({AV0_ID}: {AV0_THESIS})"
