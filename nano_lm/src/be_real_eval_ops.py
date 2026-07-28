"""Wave BE6 BE-REAL-EVAL: product+util+ctx+speed + live battery; gen iff NANOGEN15 PROMOTE."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from be_session_ops import (
    BE0_ANTI_FP,
    BE0_ASK_BATTERY,
    BE0_MODES,
    BE0_REAL_EVAL_PROTOCOL,
    BE0_SAFE_NOTE,
    BE0_SHIP_LOCK,
    map_be_product_mode,
)
from real_eval_ops import force_abstain_row, near_miss_should_abstain
from shipreal_ops import content_matches_mode

__all__ = [
    "BE_REAL_EVAL_ID",
    "BE_REAL_EVAL_THESIS",
    "BE_REAL_EVAL_CLAIM",
    "BE_REAL_EVAL_SAFE_NOTE",
    "BE_REAL_EVAL_ANTI_FP",
    "ASK_BATTERY",
    "REQUIRED_MODES",
    "PROTOCOL",
    "PARENT_NANOGEN15",
    "DECODE_PATH_KINDS",
    "LOOKUP_KINDS",
    "map_be_product_mode",
    "telemetry_ok",
    "mode_matches_expect",
    "battery_row_ok",
    "battery_pass",
    "claim_is_honest",
    "gen_claim_allowed",
    "near_miss_should_abstain",
    "force_abstain_row",
    "content_matches_mode",
    "nanogen15_outcome_ok",
    "decide_be_real_eval",
]

BE_REAL_EVAL_ID = "BE-REAL-EVAL"
BE_REAL_EVAL_THESIS = (
    "Final BE real eval: product+util+ctx+speed pass "
    "(COMPINT·SHIPUSE·FASTBE·CTXBE) + live ask battery (prod=eval; "
    "BE-FOREVER FP ABSTAIN; BA…BD forever hold; over-refuse LOOKUP; "
    "utilization smoke) + generative claim only if BE5 H-NANOGEN15 PROMOTE "
    "(true_continue; real M1|M2|M3; span-fallback ≠ gen; never NANOGEN14+rename)"
)
BE_REAL_EVAL_CLAIM = BE0_SHIP_LOCK
BE_REAL_EVAL_SAFE_NOTE = BE0_SAFE_NOTE
BE_REAL_EVAL_ANTI_FP = BE0_ANTI_FP
ASK_BATTERY: tuple[dict[str, str], ...] = BE0_ASK_BATTERY
REQUIRED_MODES: frozenset[str] = BE0_MODES
PROTOCOL: Mapping[str, object] = BE0_REAL_EVAL_PROTOCOL
PARENT_NANOGEN15 = "DEFER"
DECODE_PATH_KINDS = frozenset(
    {"decode_content", "decode_gibberish_bar", "decode_smoke"}
)
LOOKUP_KINDS = frozenset(
    {"known_lookup", "overrefuse_gold", "utilization_smoke"}
)


def telemetry_ok(row: Mapping[str, Any]) -> bool:
    """wall_ms + n_new + product_mode required (BE0 real-eval law)."""
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
    """All frozen BE0 battery rows pass anti-FP bars."""
    if len(rows) != len(ASK_BATTERY):
        return False
    ids = {str(r.get("id", "")) for r in rows}
    need = {str(p["id"]) for p in ASK_BATTERY}
    if ids != need:
        return False
    return all(battery_row_ok(r) for r in rows)


def gen_claim_allowed(claim: str) -> bool:
    """True if claim asserts NANOGEN15 / true-continue / mini-AGI unlock."""
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
        "nanogen15",
        "h-nanogen15",
        "mini-agi",
        "generative unlocked",
        "true-gen unlocked",
        "tac unlocked",
    )
    return any(m in cleaned for m in markers)


def nanogen15_outcome_ok(decision: str) -> bool:
    """BE5 may be PROMOTE / HOLD / DEFER (not MISSING / KILL)."""
    d = str(decision)
    if d == "MISSING":
        return False
    return d.startswith(("PROMOTE", "HOLD", "DEFER"))


def claim_is_honest(claim: str, *, nanogen15_decision: str) -> bool:
    """
    GIVEN ship claim + BE5 decision
    WHEN checking BE6 honesty
    THEN reject unlabeled open-chat / GPT-class;
         gen unlock only if NANOGEN15 PROMOTE.
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
    nano = str(nanogen15_decision)
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
    if not bool(PROTOCOL.get("exact_gold_abstain_is_miss")):
        return "KILL (protocol must mark exact-gold ABSTAIN as miss)"
    if not bool(PROTOCOL.get("utilization_scored")):
        return "KILL (protocol must score utilization)"
    if not bool(PROTOCOL.get("type_coercion_mismatch_is_false_hit")):
        return "KILL (protocol must mark type/coercion FP)"
    claim_rule = str(PROTOCOL.get("gen_claim_rule", "")).lower()
    if "nanogen15" not in claim_rule:
        return "KILL (protocol gen_claim_rule must name NANOGEN15)"
    if "true_continue" not in claim_rule and "true-continue" not in claim_rule:
        return "KILL (protocol gen_claim_rule must require true_continue)"
    return None


def decide_be_real_eval(
    *,
    compint_decision: str,
    shipuse_decision: str,
    fastbe_decision: str,
    ctxbe_decision: str,
    nanogen15_decision: str,
    battery_ok: bool,
    claim: str,
) -> str:
    """
    GIVEN BE1–BE5 decisions + live battery + ship claim
    WHEN applying pesquisa §9 BE6 gate
    THEN PROMOTE iff product/util/ctx/speed pass + battery + honest claim.
    """
    for name, dec in (
        ("compint", compint_decision),
        ("shipuse", shipuse_decision),
        ("fastbe", fastbe_decision),
        ("ctxbe", ctxbe_decision),
    ):
        err = _gate_pillar(name, dec)
        if err:
            return err
    if not battery_ok:
        return "KILL (live ask battery failed anti-FP / mode bars)"
    nano = str(nanogen15_decision)
    if not nanogen15_outcome_ok(nano):
        return f"KILL (nanogen15 outcome invalid: {nano})"
    err = _gate_protocol()
    if err:
        return err
    if not claim_is_honest(claim, nanogen15_decision=nano):
        return "KILL (dishonest ship claim)"
    if not nano.startswith("PROMOTE") and gen_claim_allowed(claim):
        return "KILL (generative claim while BE5 not PROMOTE)"
    status = nano.split("(", 1)[0].strip()
    gen_note = (
        "gen unlocked under BE5 PROMOTE"
        if nano.startswith("PROMOTE")
        else f"gen locked under BE5 {status}"
    )
    return (
        f"PROMOTE ({BE_REAL_EVAL_ID}: COMPINT·SHIPUSE·FASTBE·CTXBE + "
        f"battery {len(ASK_BATTERY)}/{len(ASK_BATTERY)}; {gen_note})"
    )
