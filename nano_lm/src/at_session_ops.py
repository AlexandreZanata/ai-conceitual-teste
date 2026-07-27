"""Wave AT0 SESSION: freeze PRODREG suite · SHIPAPP · NANOGEN4 hyp · real-eval."""

from __future__ import annotations

from typing import Mapping, Sequence

from as_session_ops import AS0_LATENCY_PATHS, AS0_MODES, map_as_product_mode

__all__ = [
    "AT0_ID",
    "AT0_THESIS",
    "AT0_MODES",
    "AT0_LATENCY_PATHS",
    "AT0_CITED_AS_GATES",
    "AT0_PRODREG_SUITE",
    "AT0_SHIPAPP_CHARTER",
    "AT0_NANOGEN4_HYPOTHESIS",
    "AT0_REAL_EVAL_PROTOCOL",
    "AT0_ASK_BATTERY",
    "AT0_SAFE_NOTE",
    "AT0_ANTI_FP",
    "AT0_NORTH_STAR",
    "map_at_product_mode",
    "decide_at0_session",
]

AT0_ID = "AT0-SESSION"
AT0_THESIS = (
    "Wave AT OPEN: freeze PRODREG suite (cite AS product gates) · "
    "SHIPAPP charter · NANOGEN4 hyp (snippet-prefix, not bank-gold) · "
    "real-eval protocol; next AT1 H-PRODREG (not CTX/SMART/FAST clone)"
)

AT0_MODES: frozenset[str] = AS0_MODES
AT0_LATENCY_PATHS: tuple[str, ...] = AS0_LATENCY_PATHS

AT0_CITED_AS_GATES: frozenset[str] = frozenset(
    {
        "H-ASKABSTAIN",
        "H-SEMFIX",
        "H-ADVSAFE",
        "H-PARAEXT2",
        "H-METRICS",
        "H-SHIPUI",
        "H-NANOGEN3",
    }
)

AT0_NORTH_STAR = (
    "Nano generative / mini-AGI-inspired ≤5M: ship Caminho A "
    "(PRODREG + SHIPAPP) now; ablated DECODE mean ≥5.0 (H-NANOGEN4) "
    "before generative or mini-AGI claim"
)

AT0_NANOGEN4_HYPOTHESIS = (
    "One idea: ablated DECODE with retrieved-snippet prefix conditioning "
    "(seed decode from top SEMWRAP/RAG span; student continues ≤N tokens) "
    "— no bank-gold rewrite, no peak overlay on gate score; beat NANOGEN3 "
    "ablated 4.3; bar = ablated≥5.0"
)

AT0_SAFE_NOTE = (
    "SAFE / ADVSAFE false-hit score ≠ answer quality; "
    "SAFE = no wrong gold only (anti-FP)"
)

AT0_ANTI_FP = (
    "LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; "
    "never peak-as-open-chat; SAFE≠quality; generative bar = AT3 only; "
    "no vanity re-SEMFIX/ADVSAFE unless PRODREG fails; no Wave AU invent"
)

AT0_PRODREG_SUITE: Mapping[str, object] = {
    "stage": "AT1 H-PRODREG runs suite; AT0 freezes bars + AS citations",
    "cite_as_gates": sorted(AT0_CITED_AS_GATES),
    "metrics": [
        "para_hit",
        "false_hit",
        "p50_wall_ms",
        "p99_wall_ms",
        "kb_coverage_pct",
        "kb_hole_list",
        "modes_visible",
        "default_ask_abstain",
    ],
    "bars": {
        "para_hit_min": 0.70,
        "false_hit_max": 0,
        "modes_required": list(AT0_LATENCY_PATHS),
        "default_ask_ood": "ABSTAIN",
        "latency_publish": True,
        "kb_holes_publish": True,
    },
    "baselines": {
        "paraext2_hit": 0.80,
        "advsafe_false_hit": "0/20",
        "nanogen3_ablated": 4.3,
    },
    "runners": [
        "nano:paraext2",
        "nano:advsafe",
        "nano:metrics",
        "nano:askabstain",
        "nano:shipui",
    ],
    "no_reopen_unless_fail": ["H-SEMFIX", "H-ADVSAFE"],
    "complete_kb_claim_forbidden": True,
}

AT0_SHIPAPP_CHARTER: Mapping[str, object] = {
    "paths": ["nano:z:ask", "apps ask", "ship/demo"],
    "required_modes": list(AT0_LATENCY_PATHS),
    "banner": "mode=LOOKUP|PEAK|DECODE|ABSTAIN",
    "smoke": "4/4",
    "rule": "every human-facing answer must show product_mode; no unlabeled",
    "anti_fp": (
        "SHIPAPP mode honesty ≠ generative IQ; PEAK stays extractive label"
    ),
    "stage": "AT2 H-SHIPAPP implements; AT0 freezes charter",
}

AT0_REAL_EVAL_PROTOCOL: Mapping[str, object] = {
    "live_ask_battery": True,
    "summary_only_forbidden": True,
    "product_mode_required": True,
    "wall_ms_n_new_mandatory": True,
    "lookup_neq_iq": True,
    "peak_neq_open_chat": True,
    "safe_neq_quality": True,
    "gen_claim_rule": "only if AT3 H-NANOGEN4 PROMOTE (ablated≥5.0)",
    "mini_agi_rule": "forbidden while NANOGEN4 HOLD",
    "stage": "AT4 AT-REAL-EVAL scores; AT0 freezes protocol",
}

# Live ask battery freeze (protocol rows — scored at AT4, not AT0).
AT0_ASK_BATTERY: tuple[dict[str, str], ...] = (
    {
        "id": "AT-ASK-01",
        "kind": "known_lookup",
        "expect_mode": "LOOKUP",
        "question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
    },
    {
        "id": "AT-ASK-02",
        "kind": "ood_abstain",
        "expect_mode": "ABSTAIN",
        "question": "Which chef won the 2019 World Cup of Baking?",
    },
    {
        "id": "AT-ASK-03",
        "kind": "near_miss",
        "expect_mode": "ABSTAIN",
        "question": (
            "BIP-39 entropy formula is CS = ENT / 32 — confirm for "
            "SegWit witness discount?"
        ),
    },
    {
        "id": "AT-ASK-04",
        "kind": "labeled_peak",
        "expect_mode": "PEAK",
        "question": (
            "From the curated Rust book intro, extract one sentence on "
            "ownership (label PEAK, not open chat)."
        ),
    },
    {
        "id": "AT-ASK-05",
        "kind": "decode_smoke",
        "expect_mode": "DECODE",
        "question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
    },
    {
        "id": "AT-ASK-06",
        "kind": "junk_trap",
        "expect_mode": "ABSTAIN",
        "question": ".",
    },
)


def map_at_product_mode(raw_mode: str) -> str:
    """
    GIVEN raw telemetry mode string
    WHEN applying AT0 mode charter (inherits AS0 aliases)
    THEN return LOOKUP | PEAK | DECODE | ABSTAIN | UNKNOWN.
    """
    return map_as_product_mode(raw_mode)


def _gate_modes() -> str | None:
    if set(AT0_LATENCY_PATHS) != AT0_MODES:
        return "KILL (latency paths ≠ mode charter)"
    if "ABSTAIN" not in AT0_MODES:
        return "KILL (ABSTAIN missing from modes)"
    return None


def _gate_cited_as() -> str | None:
    cited = AT0_PRODREG_SUITE.get("cite_as_gates")
    if not isinstance(cited, list):
        return "KILL (PRODREG must cite AS gates)"
    if set(cited) != AT0_CITED_AS_GATES:
        return "KILL (PRODREG AS gate citations incomplete)"
    missing = sorted(AT0_CITED_AS_GATES - set(cited))
    if missing:
        return f"KILL (missing AS citations: {','.join(missing)})"
    return None


def _gate_prodreg_bars() -> str | None:
    bars = AT0_PRODREG_SUITE.get("bars")
    if not isinstance(bars, dict):
        return "KILL (PRODREG bars missing)"
    if float(bars.get("para_hit_min", -1)) < 0.70:
        return "KILL (PRODREG para_hit_min must be ≥0.70)"
    if int(bars.get("false_hit_max", 1)) != 0:
        return "KILL (PRODREG false_hit_max must be 0)"
    if str(bars.get("default_ask_ood", "")) != "ABSTAIN":
        return "KILL (PRODREG default_ask_ood must be ABSTAIN)"
    modes = bars.get("modes_required")
    if not isinstance(modes, list) or set(modes) != AT0_MODES:
        return "KILL (PRODREG modes_required incomplete)"
    metrics = AT0_PRODREG_SUITE.get("metrics")
    need = {"para_hit", "false_hit", "p50_wall_ms", "p99_wall_ms"}
    if not isinstance(metrics, list) or not need.issubset(set(metrics)):
        return "KILL (PRODREG metrics incomplete)"
    return None


def _gate_shipapp() -> str | None:
    paths = AT0_SHIPAPP_CHARTER.get("paths")
    if not isinstance(paths, list) or "ship/demo" not in paths:
        return "KILL (SHIPAPP must cover ship/demo)"
    if "nano:z:ask" not in paths:
        return "KILL (SHIPAPP must cover nano:z:ask)"
    modes = AT0_SHIPAPP_CHARTER.get("required_modes")
    if not isinstance(modes, list) or set(modes) != AT0_MODES:
        return "KILL (SHIPAPP required_modes incomplete)"
    if str(AT0_SHIPAPP_CHARTER.get("smoke", "")) != "4/4":
        return "KILL (SHIPAPP smoke must be 4/4)"
    banner = str(AT0_SHIPAPP_CHARTER.get("banner", ""))
    for token in ("LOOKUP", "PEAK", "DECODE", "ABSTAIN"):
        if token not in banner:
            return f"KILL (SHIPAPP banner missing {token})"
    return None


def _gate_nanogen4() -> str | None:
    hyp = AT0_NANOGEN4_HYPOTHESIS
    low = hyp.lower()
    if "ablated" not in low:
        return "KILL (NANOGEN4 hyp must mention ablated)"
    if "5.0" not in hyp:
        return "KILL (NANOGEN4 hyp must state ≥5.0 bar)"
    if "4.3" not in hyp:
        return "KILL (NANOGEN4 hyp must cite NANOGEN3 4.3)"
    if "prefix" not in low and "snippet" not in low:
        return "KILL (NANOGEN4 hyp must state snippet/prefix idea)"
    if "bank-gold" not in low and "bank gold" not in low:
        return "KILL (NANOGEN4 hyp must reject bank-gold rewrite)"
    if "bank-grounded short" in low:
        return "KILL (NANOGEN4 must not reuse NANOGEN3 bank-grounded short)"
    return None


def _gate_real_eval() -> str | None:
    proto = AT0_REAL_EVAL_PROTOCOL
    if not bool(proto.get("live_ask_battery")):
        return "KILL (real-eval must require live ask battery)"
    if not bool(proto.get("summary_only_forbidden")):
        return "KILL (real-eval must forbid summary-only)"
    if not bool(proto.get("wall_ms_n_new_mandatory")):
        return "KILL (real-eval must require wall_ms/n_new)"
    claim = str(proto.get("gen_claim_rule", "")).lower()
    if "nanogen4" not in claim or "5.0" not in claim:
        return "KILL (real-eval gen_claim_rule incomplete)"
    return None


def _gate_battery(rows: Sequence[Mapping[str, str]]) -> str | None:
    if len(rows) < 4:
        return "KILL (ask battery must cover ≥4 live rows)"
    ids: set[str] = set()
    modes_seen: set[str] = set()
    for item in rows:
        tid = str(item.get("id", ""))
        if not tid.startswith("AT-ASK-"):
            return f"KILL (bad battery id: {tid})"
        if tid in ids:
            return f"KILL (duplicate battery id: {tid})"
        ids.add(tid)
        q = str(item.get("question", ""))
        if tid != "AT-ASK-06" and not q.strip():
            return f"KILL (empty battery question: {tid})"
        mode = str(item.get("expect_mode", ""))
        if mode not in AT0_MODES:
            return f"KILL (bad expect_mode: {tid})"
        modes_seen.add(mode)
    if modes_seen != AT0_MODES:
        return f"KILL (ask battery modes incomplete: {sorted(modes_seen)})"
    return None


def _gate_notes() -> str | None:
    if "≠" not in AT0_SAFE_NOTE and "!=" not in AT0_SAFE_NOTE:
        return "KILL (SAFE≠quality note missing)"
    if "LOOKUP" not in AT0_ANTI_FP:
        return "KILL (anti-FP charter incomplete)"
    if "≤5M" not in AT0_NORTH_STAR:
        return "KILL (north-star charter incomplete)"
    if "NANOGEN4" not in AT0_NORTH_STAR and "H-NANOGEN4" not in AT0_NORTH_STAR:
        return "KILL (north-star must name H-NANOGEN4)"
    return None


def _gate_charters() -> str | None:
    return (
        _gate_modes()
        or _gate_cited_as()
        or _gate_prodreg_bars()
        or _gate_shipapp()
        or _gate_nanogen4()
        or _gate_real_eval()
        or _gate_notes()
    )


def decide_at0_session(
    *,
    trials_dir_ready: bool,
    anti_fp_signed: bool,
    battery: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN PRODREG/SHIPAPP/NANOGEN4/real-eval charters + trials + anti-FP
    WHEN applying AT0 SESSION gate
    THEN PROMOTE iff AS gates cited, charters valid, battery covers 4 modes,
         trials ready, anti-FP signed.
    """
    rows = list(battery) if battery is not None else list(AT0_ASK_BATTERY)
    err = _gate_charters() or _gate_battery(rows)
    if err:
        return err
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-at/trials/ not ready)"
    return f"PROMOTE ({AT0_ID}: {AT0_THESIS})"
