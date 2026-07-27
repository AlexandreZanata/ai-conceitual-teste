"""Wave AU0 SESSION: freeze product-debt · human-para · NANOGEN5 · strict eval."""

from __future__ import annotations

from typing import Mapping, Sequence

from at_session_ops import AT0_MODES, map_at_product_mode

__all__ = [
    "AU0_ID",
    "AU0_THESIS",
    "AU0_MODES",
    "AU0_LATENCY_PATHS",
    "AU0_CITED_AT_LOCKS",
    "AU0_PRODUCT_DEBT_SUITE",
    "AU0_HUMAN_PARA_PROTOCOL",
    "AU0_HUMAN_PARA_ROWS",
    "AU0_NANOGEN5_HYPOTHESIS",
    "AU0_STRICT_GEN_JUDGE",
    "AU0_REAL_EVAL_PROTOCOL",
    "AU0_ASK_BATTERY",
    "AU0_SAFE_NOTE",
    "AU0_ANTI_FP",
    "AU0_NORTH_STAR",
    "AU0_SHIP_LOCK",
    "map_au_product_mode",
    "decide_au0_session",
]

AU0_ID = "AU0-SESSION"
AU0_THESIS = (
    "Wave AU OPEN: freeze product-debt suite (live-audit) · human-para "
    "protocol · NANOGEN5 hyp (strict judge, not gold-substring) · "
    "real-eval protocol; next AU1 H-PRODHARD (not CTX/SMART/FAST clone)"
)

AU0_MODES: frozenset[str] = AT0_MODES
AU0_LATENCY_PATHS: tuple[str, ...] = (
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
)

AU0_CITED_AT_LOCKS: frozenset[str] = frozenset(
    {
        "H-PRODREG",
        "H-SHIPAPP",
        "H-NANOGEN4",
        "AT-REAL-EVAL",
        "AT-FREEZE",
    }
)

AU0_SHIP_LOCK = (
    "AF packaged stack + AQ product layer + AS trust path + "
    "ablated DECODE (snippet-prefix) — not unlabeled open chat LM"
)

AU0_NORTH_STAR = (
    "Nano generative / mini-AGI-inspired ≤5M: harden Caminho A under "
    "live human metrics now (PRODHARD + SHIPREAL); strict ablated "
    "DECODE (H-NANOGEN5) before generative or mini-AGI claim"
)

AU0_NANOGEN5_HYPOTHESIS = (
    "One idea: ablated DECODE with snippet-prefix + gibberish-tail gate "
    "(truncate/refuse when continuation leaves retrieved-span "
    "readability) scored by short-answer F1/HITL — gold-substring alone "
    "insufficient; beat archived NANOGEN4 ablated 5.5 under STRICT "
    "judge; bar = strict_ablated≥5.5 else HOLD"
)

AU0_SAFE_NOTE = (
    "SAFE / ADVSAFE false-hit score ≠ answer quality; "
    "SAFE = no wrong gold only (anti-FP); "
    "gold-substring ≠ generative PROMOTE"
)

AU0_ANTI_FP = (
    "LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; "
    "never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; "
    "no gibberish-tail PROMOTE; eval path = prod ask path; "
    "generative bar = AU3 only; no vanity re-SEMFIX/ADVSAFE unless "
    "PRODHARD fails; no Wave AV invent; no CTX/SMART/FAST clone"
)

AU0_STRICT_GEN_JUDGE: Mapping[str, object] = {
    "stage": "AU3 H-NANOGEN5 applies; AU0 freezes judge law",
    "gold_substring_insufficient": True,
    "gibberish_tail_fails": True,
    "usable_span_required": True,
    "scoring": "short_answer_f1_or_hitl",
    "archived_nanogen4_bar": 5.5,
    "promote_bar": "strict_ablated≥5.5",
    "nanogen4_judge_archived": True,
}

AU0_PRODUCT_DEBT_SUITE: Mapping[str, object] = {
    "stage": "AU1 H-PRODHARD closes debts; AU0 freezes suite",
    "cite_at_locks": sorted(AU0_CITED_AT_LOCKS),
    "debts": [
        {
            "id": "near_miss_default_ask",
            "evidence": "BIP-39+SegWit via nano:z:ask --wrap --semwrap",
            "fix": "refuse on production ask path (not eval-only)",
            "bar": "ABSTAIN on near_miss; FH=0",
        },
        {
            "id": "human_para_heldout",
            "evidence": "human rewrite of add → ABSTAIN (SEMWRAP miss)",
            "fix": "held-out human para set + SEMWRAP robustness",
            "bar": "para_hit_min on held-out human set",
        },
        {
            "id": "peak_usable_span",
            "evidence": "AT-ASK-04 completion gibberish span",
            "fix": "PEAK returns usable labeled span (or ABSTAIN)",
            "bar": "readable_span_or_abstain",
        },
        {
            "id": "answer_usability",
            "evidence": "AT battery 6/6 checked product_mode only",
            "fix": "score answer usability where mode claims content",
            "bar": "mode_and_usable_when_claimed",
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
        "default_ask_abstain",
        "peak_usable",
        "answer_usability",
    ],
    "bars": {
        "para_hit_min": 0.70,
        "false_hit_max": 0,
        "modes_required": list(AU0_LATENCY_PATHS),
        "default_ask_near_miss": "ABSTAIN",
        "default_ask_ood": "ABSTAIN",
        "peak_usable_or_abstain": True,
        "latency_publish": True,
        "kb_holes_publish": True,
        "eval_eq_prod_ask": True,
    },
    "baselines": {
        "paraext2_hit": 0.80,
        "advsafe_false_hit": "0/20",
        "nanogen4_ablated": 5.5,
        "ship_lock": AU0_SHIP_LOCK,
    },
    "runners": [
        "nano:z:ask",
        "nano:paraext2",
        "nano:advsafe",
        "nano:metrics",
        "nano:askabstain",
        "nano:shipui",
        "nano:prodreg",
    ],
    "no_reopen_unless_fail": ["H-SEMFIX", "H-ADVSAFE"],
    "complete_kb_claim_forbidden": True,
}

AU0_HUMAN_PARA_ROWS: tuple[dict[str, str], ...] = (
    {
        "id": "AU-PARA-01",
        "parent": "add",
        "question": (
            "Please write a tiny helper called add that takes two ints "
            "a and b and returns their sum."
        ),
    },
    {
        "id": "AU-PARA-02",
        "parent": "add",
        "question": (
            "I need a short Python function named add — inputs a, b "
            "integers; output a+b."
        ),
    },
    {
        "id": "AU-PARA-03",
        "parent": "add",
        "question": (
            "Could you sketch def add(a, b) returning the sum of two "
            "integers?"
        ),
    },
    {
        "id": "AU-PARA-04",
        "parent": "add",
        "question": (
            "Human rewrite: make an add function for two integer args "
            "that returns a plus b."
        ),
    },
    {
        "id": "AU-PARA-05",
        "parent": "add",
        "question": (
            "In plain words: a small Python adder named add for ints "
            "a and b."
        ),
    },
    {
        "id": "AU-PARA-06",
        "parent": "add",
        "question": (
            "External phrasing: implement add(a: int, b: int) -> int "
            "as a+b."
        ),
    },
    {
        "id": "AU-PARA-07",
        "parent": "add",
        "question": (
            "Rewrite for a beginner: function add that adds two whole "
            "numbers a and b."
        ),
    },
    {
        "id": "AU-PARA-08",
        "parent": "add",
        "question": (
            "Held-out ask: short code for add combining integer pair "
            "a with b."
        ),
    },
)

AU0_HUMAN_PARA_PROTOCOL: Mapping[str, object] = {
    "stage": "AU1 H-PRODHARD scores; AU0 freezes protocol",
    "held_out": True,
    "bank_stuff_forbidden": True,
    "source": "human / external rewrite",
    "min_n": 8,
    "scoring": "hit rate on default ask path (SEMWRAP)",
    "path": "nano:z:ask --wrap --semwrap",
    "rows": list(AU0_HUMAN_PARA_ROWS),
}

AU0_REAL_EVAL_PROTOCOL: Mapping[str, object] = {
    "live_ask_battery": True,
    "summary_only_forbidden": True,
    "product_mode_required": True,
    "wall_ms_n_new_mandatory": True,
    "lookup_neq_iq": True,
    "peak_neq_open_chat": True,
    "safe_neq_quality": True,
    "gold_substring_neq_gen": True,
    "gibberish_tail_fails": True,
    "eval_eq_prod_ask": True,
    "answer_usability_scored": True,
    "gen_claim_rule": (
        "only if AU3 H-NANOGEN5 PROMOTE (strict_ablated≥5.5)"
    ),
    "mini_agi_rule": "forbidden while NANOGEN5 HOLD",
    "stage": "AU4 AU-REAL-EVAL scores; AU0 freezes protocol",
}

# Live ask battery freeze (protocol rows — scored at AU4, not AU0).
AU0_ASK_BATTERY: tuple[dict[str, str], ...] = (
    {
        "id": "AU-ASK-01",
        "kind": "known_lookup",
        "expect_mode": "LOOKUP",
        "question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
    },
    {
        "id": "AU-ASK-02",
        "kind": "ood_abstain",
        "expect_mode": "ABSTAIN",
        "question": "Which chef won the 2019 World Cup of Baking?",
    },
    {
        "id": "AU-ASK-03",
        "kind": "near_miss",
        "expect_mode": "ABSTAIN",
        "question": (
            "BIP-39 entropy formula is CS = ENT / 32 — confirm for "
            "SegWit witness discount?"
        ),
    },
    {
        "id": "AU-ASK-04",
        "kind": "labeled_peak",
        "expect_mode": "PEAK",
        "question": (
            "From the curated Rust book intro, extract one sentence on "
            "ownership (label PEAK, not open chat)."
        ),
    },
    {
        "id": "AU-ASK-05",
        "kind": "decode_smoke",
        "expect_mode": "DECODE",
        "question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
    },
    {
        "id": "AU-ASK-06",
        "kind": "junk_trap",
        "expect_mode": "ABSTAIN",
        "question": ".",
    },
    {
        "id": "AU-ASK-07",
        "kind": "human_para",
        "expect_mode": "LOOKUP",
        "question": (
            "Please write a tiny helper called add that takes two ints "
            "a and b and returns their sum."
        ),
    },
)


def map_au_product_mode(raw_mode: str) -> str:
    """
    GIVEN raw telemetry mode string
    WHEN applying AU0 mode charter (inherits AT0/AS0 aliases)
    THEN return LOOKUP | PEAK | DECODE | ABSTAIN | UNKNOWN.
    """
    return map_at_product_mode(raw_mode)


def _gate_modes() -> str | None:
    if set(AU0_LATENCY_PATHS) != AU0_MODES:
        return "KILL (latency paths ≠ mode charter)"
    if "ABSTAIN" not in AU0_MODES:
        return "KILL (ABSTAIN missing from modes)"
    return None


def _gate_cited_at() -> str | None:
    cited = AU0_PRODUCT_DEBT_SUITE.get("cite_at_locks")
    if not isinstance(cited, list):
        return "KILL (product-debt must cite AT locks)"
    if set(cited) != AU0_CITED_AT_LOCKS:
        return "KILL (product-debt AT lock citations incomplete)"
    return None


def _gate_debt_ids() -> str | None:
    debts = AU0_PRODUCT_DEBT_SUITE.get("debts")
    if not isinstance(debts, list) or len(debts) < 4:
        return "KILL (product-debt must list ≥4 live-audit debts)"
    ids = {str(d.get("id", "")) for d in debts if isinstance(d, dict)}
    need = {
        "near_miss_default_ask",
        "human_para_heldout",
        "peak_usable_span",
        "answer_usability",
    }
    if not need.issubset(ids):
        return "KILL (product-debt live-audit ids incomplete)"
    return None


def _gate_debt_bars() -> str | None:
    bars = AU0_PRODUCT_DEBT_SUITE.get("bars")
    if not isinstance(bars, dict):
        return "KILL (product-debt bars missing)"
    if float(bars.get("para_hit_min", -1)) < 0.70:
        return "KILL (product-debt para_hit_min must be ≥0.70)"
    if int(bars.get("false_hit_max", 1)) != 0:
        return "KILL (product-debt false_hit_max must be 0)"
    if str(bars.get("default_ask_near_miss", "")) != "ABSTAIN":
        return "KILL (near_miss on default ask must be ABSTAIN)"
    if not bool(bars.get("eval_eq_prod_ask")):
        return "KILL (eval path must equal prod ask path)"
    if not bool(bars.get("peak_usable_or_abstain")):
        return "KILL (PEAK usable-or-abstain bar missing)"
    modes = bars.get("modes_required")
    if not isinstance(modes, list) or set(modes) != AU0_MODES:
        return "KILL (product-debt modes_required incomplete)"
    return None


def _gate_debt_metrics() -> str | None:
    metrics = AU0_PRODUCT_DEBT_SUITE.get("metrics")
    need_m = {
        "para_hit",
        "false_hit",
        "p50_wall_ms",
        "p99_wall_ms",
        "peak_usable",
    }
    if not isinstance(metrics, list) or not need_m.issubset(set(metrics)):
        return "KILL (product-debt metrics incomplete)"
    return None


def _gate_product_debt() -> str | None:
    return _gate_debt_ids() or _gate_debt_bars() or _gate_debt_metrics()


def _gate_para_rows() -> str | None:
    ids: set[str] = set()
    for item in AU0_HUMAN_PARA_ROWS:
        tid = str(item.get("id", ""))
        if not tid.startswith("AU-PARA-"):
            return f"KILL (bad human-para id: {tid})"
        if tid in ids:
            return f"KILL (duplicate human-para id: {tid})"
        ids.add(tid)
        if not str(item.get("question", "")).strip():
            return f"KILL (empty human-para question: {tid})"
    return None


def _gate_human_para() -> str | None:
    proto = AU0_HUMAN_PARA_PROTOCOL
    if not bool(proto.get("held_out")):
        return "KILL (human-para must be held-out)"
    if not bool(proto.get("bank_stuff_forbidden")):
        return "KILL (human-para must forbid bank stuffing)"
    rows = proto.get("rows")
    min_n = int(proto.get("min_n", 8))
    if not isinstance(rows, list) or len(rows) < min_n:
        return f"KILL (human-para must have ≥{min_n} rows)"
    if len(AU0_HUMAN_PARA_ROWS) < min_n:
        return "KILL (AU0_HUMAN_PARA_ROWS below min_n)"
    return _gate_para_rows()


def _gate_nanogen5_hyp() -> str | None:
    hyp = AU0_NANOGEN5_HYPOTHESIS
    low = hyp.lower()
    if "ablated" not in low:
        return "KILL (NANOGEN5 hyp must mention ablated)"
    if "5.5" not in hyp:
        return "KILL (NANOGEN5 hyp must cite NANOGEN4 5.5)"
    if "strict" not in low:
        return "KILL (NANOGEN5 hyp must state STRICT judge)"
    if "gold-substring" not in low and "gold substring" not in low:
        return "KILL (NANOGEN5 hyp must reject gold-substring alone)"
    if "gibberish" not in low:
        return "KILL (NANOGEN5 hyp must gate gibberish tail)"
    if "f1" not in low and "hitl" not in low:
        return "KILL (NANOGEN5 hyp must use F1/HITL scoring)"
    if "bank-grounded short" in low:
        return "KILL (NANOGEN5 must not reuse NANOGEN3 bank-grounded short)"
    return None


def _gate_nanogen5_judge() -> str | None:
    judge = AU0_STRICT_GEN_JUDGE
    if not bool(judge.get("gold_substring_insufficient")):
        return "KILL (strict judge must mark gold-substring insufficient)"
    if not bool(judge.get("gibberish_tail_fails")):
        return "KILL (strict judge must fail gibberish tail)"
    if str(judge.get("scoring", "")) != "short_answer_f1_or_hitl":
        return "KILL (strict judge scoring must be F1/HITL)"
    return None


def _gate_nanogen5() -> str | None:
    return _gate_nanogen5_hyp() or _gate_nanogen5_judge()


def _gate_real_eval_flags() -> str | None:
    proto = AU0_REAL_EVAL_PROTOCOL
    flags = (
        ("live_ask_battery", "KILL (real-eval must require live ask battery)"),
        ("summary_only_forbidden", "KILL (real-eval must forbid summary-only)"),
        ("wall_ms_n_new_mandatory", "KILL (real-eval must require wall_ms/n_new)"),
        ("eval_eq_prod_ask", "KILL (real-eval must require eval=prod ask)"),
        ("gold_substring_neq_gen", "KILL (real-eval must reject gold-substring as gen)"),
        ("gibberish_tail_fails", "KILL (real-eval must fail gibberish tail)"),
    )
    for key, msg in flags:
        if not bool(proto.get(key)):
            return msg
    return None


def _gate_real_eval() -> str | None:
    err = _gate_real_eval_flags()
    if err:
        return err
    claim = str(AU0_REAL_EVAL_PROTOCOL.get("gen_claim_rule", "")).lower()
    if "nanogen5" not in claim or "5.5" not in claim:
        return "KILL (real-eval gen_claim_rule incomplete)"
    return None


def _scan_battery_row(
    item: Mapping[str, str], ids: set[str]
) -> tuple[str | None, str, str]:
    tid = str(item.get("id", ""))
    if not tid.startswith("AU-ASK-"):
        return f"KILL (bad battery id: {tid})", "", ""
    if tid in ids:
        return f"KILL (duplicate battery id: {tid})", "", ""
    q = str(item.get("question", ""))
    if tid != "AU-ASK-06" and not q.strip():
        return f"KILL (empty battery question: {tid})", "", ""
    mode = str(item.get("expect_mode", ""))
    if mode not in AU0_MODES:
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
    if modes_seen != AU0_MODES:
        return f"KILL (ask battery modes incomplete: {sorted(modes_seen)})"
    need_kinds = {"near_miss", "human_para", "labeled_peak", "junk_trap"}
    if not need_kinds.issubset(kinds):
        return "KILL (ask battery must cover live-audit kinds)"
    return None


def _gate_notes() -> str | None:
    if "≠" not in AU0_SAFE_NOTE and "!=" not in AU0_SAFE_NOTE:
        return "KILL (SAFE≠quality note missing)"
    if "LOOKUP" not in AU0_ANTI_FP:
        return "KILL (anti-FP charter incomplete)"
    if "eval path = prod" not in AU0_ANTI_FP.lower():
        return "KILL (anti-FP must require eval=prod ask)"
    if "≤5M" not in AU0_NORTH_STAR:
        return "KILL (north-star charter incomplete)"
    if "NANOGEN5" not in AU0_NORTH_STAR and "H-NANOGEN5" not in AU0_NORTH_STAR:
        return "KILL (north-star must name H-NANOGEN5)"
    if "snippet-prefix" not in AU0_SHIP_LOCK:
        return "KILL (ship lock must keep AT snippet-prefix claim)"
    return None


def _gate_charters() -> str | None:
    return (
        _gate_modes()
        or _gate_cited_at()
        or _gate_product_debt()
        or _gate_human_para()
        or _gate_nanogen5()
        or _gate_real_eval()
        or _gate_notes()
    )


def decide_au0_session(
    *,
    trials_dir_ready: bool,
    anti_fp_signed: bool,
    battery: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN product-debt/human-para/NANOGEN5/real-eval charters + trials + anti-FP
    WHEN applying AU0 SESSION gate
    THEN PROMOTE iff AT locks cited, charters valid, battery covers 4 modes,
         trials ready, anti-FP signed.
    """
    rows = list(battery) if battery is not None else list(AU0_ASK_BATTERY)
    err = _gate_charters() or _gate_battery(rows)
    if err:
        return err
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-au/trials/ not ready)"
    return f"PROMOTE ({AU0_ID}: {AU0_THESIS})"
