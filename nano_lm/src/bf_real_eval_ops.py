"""Wave BF6 BF-REAL-EVAL: product+util+ctx+speed + live battery; gen iff NANOGEN16 PROMOTE."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from bf_session_ops import (
    BF0_ANTI_FP,
    BF0_ASK_BATTERY,
    BF0_MODES,
    BF0_REAL_EVAL_PROTOCOL,
    BF0_SAFE_NOTE,
    BF0_SHIP_LOCK,
    map_bf_product_mode,
)
from real_eval_ops import force_abstain_row, near_miss_should_abstain
from shipreal_ops import content_matches_mode

__all__ = [
    "BF_REAL_EVAL_ID",
    "BF_REAL_EVAL_THESIS",
    "BF_REAL_EVAL_CLAIM",
    "BF_REAL_EVAL_SAFE_NOTE",
    "BF_REAL_EVAL_ANTI_FP",
    "ASK_BATTERY",
    "REQUIRED_MODES",
    "PROTOCOL",
    "PARENT_NANOGEN16",
    "DECODE_PATH_KINDS",
    "LOOKUP_KINDS",
    "map_bf_product_mode",
    "telemetry_ok",
    "mode_matches_expect",
    "battery_row_ok",
    "battery_pass",
    "claim_is_honest",
    "gen_claim_allowed",
    "near_miss_should_abstain",
    "force_abstain_row",
    "content_matches_mode",
    "nanogen16_outcome_ok",
    "decide_bf_real_eval",
]

BF_REAL_EVAL_ID = "BF-REAL-EVAL"
BF_REAL_EVAL_THESIS = (
    "Final BF real eval: product+util+ctx+speed pass "
    "(PREDINT·SHIPUSE2·FASTBF·CTXBF) + live ask battery (prod=eval; "
    "BF-FOREVER FP ABSTAIN; BA…BE forever hold; over-refuse LOOKUP; "
    "utilization smoke) + generative claim only if BF5 H-NANOGEN16 PROMOTE "
    "(true_continue; written M1|M2|M3 plan; span-fallback ≠ gen; "
    "never NANOGEN15+rename; else SKIP gen claim)"
)
BF_REAL_EVAL_CLAIM = BF0_SHIP_LOCK
BF_REAL_EVAL_SAFE_NOTE = BF0_SAFE_NOTE
BF_REAL_EVAL_ANTI_FP = BF0_ANTI_FP
ASK_BATTERY: tuple[dict[str, str], ...] = BF0_ASK_BATTERY
REQUIRED_MODES: frozenset[str] = BF0_MODES
PROTOCOL: Mapping[str, object] = BF0_REAL_EVAL_PROTOCOL
PARENT_NANOGEN16 = "SKIP"
DECODE_PATH_KINDS = frozenset(
    {"decode_content", "decode_gibberish_bar", "decode_smoke"}
)
LOOKUP_KINDS = frozenset(
    {"known_lookup", "overrefuse_gold", "utilization_smoke"}
)


def telemetry_ok(row: Mapping[str, Any]) -> bool:
    """wall_ms + n_new + product_mode required (BF0 real-eval law)."""
    if "wall_ms" not in row or "n_new" not in row:
        return False
    mode = str(row.get("product_mode", "") or "")
    return mode in REQUIRED_MODES


def mode_matches_expect(
    *,
    product_mode: str,
    expect_mode: str,
    kind: str = "",
) -> bool:
    """Exact mode match, or DECODE-path honesty (usable DECODE or ABSTAIN)."""
    if str(product_mode) == str(expect_mode):
        return True
    if (
        str(expect_mode) == "DECODE"
        and str(product_mode) == "ABSTAIN"
        and str(kind) in DECODE_PATH_KINDS
    ):
        return True
    return False


def battery_row_ok(row: Mapping[str, Any]) -> bool:
    """Labeled mode matches expect (+ DECODE law) + telemetry + usability."""
    if not telemetry_ok(row):
        return False
    if not mode_matches_expect(
        product_mode=str(row.get("product_mode", "")),
        expect_mode=str(row.get("expect_mode", "")),
        kind=str(row.get("kind", "")),
    ):
        return False
    if bool(PROTOCOL.get("answer_usability_scored")):
        return bool(row.get("content_ok", content_matches_mode(row)))
    return True


def battery_pass(rows: Sequence[Mapping[str, Any]]) -> bool:
    """All frozen BF0 battery rows pass anti-FP bars."""
    if len(rows) != len(ASK_BATTERY):
        return False
    ids = {str(r.get("id", "")) for r in rows}
    need = {str(p["id"]) for p in ASK_BATTERY}
    if ids != need:
        return False
    return all(battery_row_ok(r) for r in rows)


def gen_claim_allowed(claim: str) -> bool:
    """True if claim asserts NANOGEN16 / true-continue / mini-AGI unlock."""
    low = str(claim).lower()
    cleaned = (
        low.replace("not tac unlocked", " ")
        .replace("not true-continue", " ")
        .replace("not true continue", " ")
        .replace("not true_continue", " ")
        .replace("not generative unlocked", " ")
    )
    markers = (
        "true-continue",
        "true continue",
        "true_continue",
        "nanogen16",
        "h-nanogen16",
        "mini-agi",
        "generative unlocked",
        "true-gen unlocked",
        "tac unlocked",
    )
    return any(m in cleaned for m in markers)


def nanogen16_outcome_ok(decision: str) -> bool:
    """BF5 may be PROMOTE / HOLD / SKIP / DEFER (not MISSING / KILL)."""
    d = str(decision)
    if d == "MISSING":
        return False
    return d.startswith(("PROMOTE", "HOLD", "SKIP", "DEFER"))


def claim_is_honest(claim: str, *, nanogen16_decision: str) -> bool:
    """
    GIVEN ship claim + BF5 decision
    WHEN checking BF6 honesty
    THEN reject unlabeled open-chat / GPT-class;
         gen unlock only if NANOGEN16 PROMOTE.
    """
    low = str(claim).lower()
    if "gpt-class" in low or "frontier chat" in low:
        return False
    has_base = "packaged" in low or "product layer" in low
    if not has_base:
        return False
    open_chat_negated = (
        "not unlabeled open chat" in low or "not open chat" in low
    )
    if ("open chat" in low or "open-chat" in low) and not open_chat_negated:
        return False
    nano = str(nanogen16_decision)
    has_gen = gen_claim_allowed(claim)
    if nano.startswith("PROMOTE"):
        return open_chat_negated
    if has_gen:
        return False
    return open_chat_negated


def _gate_pillar(name: str, dec: str) -> str | None:
    if str(dec).startswith("PROMOTE"):
        return None
    if str(dec).startswith("KILL"):
        return f"KILL ({name}: {dec})"
    if str(dec) == "MISSING":
        return f"KILL ({name} summary MISSING)"
    return f"KILL ({name} not PROMOTE: {dec})"


def _gate_protocol() -> str | None:
    if not bool(PROTOCOL.get("span_fallback_neq_gen")):
        return "KILL (protocol must mark span-fallback ≠ gen)"
    if not bool(PROTOCOL.get("eval_eq_prod_ask")):
        return "KILL (protocol must require eval=prod ask)"
    if not bool(PROTOCOL.get("intent_mismatch_is_false_hit")):
        return "KILL (protocol must mark intent mismatch as false-hit)"
    if not bool(PROTOCOL.get("predicate_mismatch_is_false_hit")):
        return "KILL (protocol must mark predicate mismatch as false-hit)"
    if not bool(PROTOCOL.get("exact_gold_abstain_is_miss")):
        return "KILL (protocol must mark exact-gold ABSTAIN as miss)"
    if not bool(PROTOCOL.get("utilization_scored")):
        return "KILL (protocol must score utilization)"
    if not bool(PROTOCOL.get("type_coercion_mismatch_is_false_hit")):
        return "KILL (protocol must mark type/coercion FP)"
    claim_rule = str(PROTOCOL.get("gen_claim_rule", "")).lower()
    if "nanogen16" not in claim_rule:
        return "KILL (protocol gen_claim_rule must name NANOGEN16)"
    if "true_continue" not in claim_rule and "true-continue" not in claim_rule:
        return "KILL (protocol gen_claim_rule must require true_continue)"
    return None


def decide_bf_real_eval(
    *,
    predint_decision: str,
    shipuse2_decision: str,
    fastbf_decision: str,
    ctxbf_decision: str,
    nanogen16_decision: str,
    battery_ok: bool,
    claim: str,
) -> str:
    """
    GIVEN BF1–BF5 decisions + live battery + ship claim
    WHEN applying pesquisa §9 BF6 gate
    THEN PROMOTE iff product/util/ctx/speed pass + battery + honest claim.
    """
    for name, dec in (
        ("predint", predint_decision),
        ("shipuse2", shipuse2_decision),
        ("fastbf", fastbf_decision),
        ("ctxbf", ctxbf_decision),
    ):
        err = _gate_pillar(name, dec)
        if err:
            return err
    if not battery_ok:
        return "KILL (live ask battery failed anti-FP / mode bars)"
    nano = str(nanogen16_decision)
    if not nanogen16_outcome_ok(nano):
        return f"KILL (nanogen16 outcome invalid: {nano})"
    err = _gate_protocol()
    if err:
        return err
    if not claim_is_honest(claim, nanogen16_decision=nano):
        return "KILL (dishonest ship claim)"
    if not nano.startswith("PROMOTE") and gen_claim_allowed(claim):
        return "KILL (generative claim while BF5 not PROMOTE)"
    status = nano.split("(", 1)[0].strip()
    gen_note = (
        "gen unlocked under BF5 PROMOTE"
        if nano.startswith("PROMOTE")
        else f"gen locked under BF5 {status}"
    )
    return (
        f"PROMOTE ({BF_REAL_EVAL_ID}: PREDINT·SHIPUSE2·FASTBF·CTXBF + "
        f"battery {len(ASK_BATTERY)}/{len(ASK_BATTERY)}; {gen_note})"
    )
