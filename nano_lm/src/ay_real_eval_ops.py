"""Wave AY4 AY-REAL-EVAL: product pass + live battery; gen only if NANOGEN9 PROMOTE."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ay_session_ops import (
    AY0_ASK_BATTERY,
    AY0_MODES,
    AY0_REAL_EVAL_PROTOCOL,
    AY0_SHIP_LOCK,
    map_ay_product_mode,
)
from real_eval_ops import force_abstain_row, near_miss_should_abstain
from shipay_ops import content_matches_mode

__all__ = [
    "AY_REAL_EVAL_ID",
    "AY_REAL_EVAL_THESIS",
    "AY_REAL_EVAL_CLAIM",
    "ASK_BATTERY",
    "REQUIRED_MODES",
    "PROTOCOL",
    "PARENT_NANOGEN9",
    "DECODE_PATH_KINDS",
    "LOOKUP_KINDS",
    "map_ay_product_mode",
    "telemetry_ok",
    "mode_matches_expect",
    "battery_row_ok",
    "battery_pass",
    "claim_is_honest",
    "gen_claim_allowed",
    "near_miss_should_abstain",
    "force_abstain_row",
    "content_matches_mode",
    "nanogen9_outcome_ok",
    "decide_ay_real_eval",
]

AY_REAL_EVAL_ID = "AY-REAL-EVAL"
AY_REAL_EVAL_THESIS = (
    "Final real eval: Caminho A product pass (PRODINT+SHIPAY) + "
    "live ask battery (prod=eval; intent-FP ABSTAIN) + generative claim "
    "only if AY3 H-NANOGEN9 PROMOTE (true_continue; real new method; "
    "span-fallback ≠ gen; never NANOGEN8+rename)"
)
AY_REAL_EVAL_CLAIM = AY0_SHIP_LOCK
ASK_BATTERY: tuple[dict[str, str], ...] = AY0_ASK_BATTERY
REQUIRED_MODES: frozenset[str] = AY0_MODES
PROTOCOL: Mapping[str, object] = AY0_REAL_EVAL_PROTOCOL
PARENT_NANOGEN9 = "DEFER"
DECODE_PATH_KINDS = frozenset(
    {"decode_content", "decode_gibberish_bar", "decode_smoke"}
)
LOOKUP_KINDS = frozenset(
    {"known_lookup", "human_para", "hard_natural", "hard_natural_hold"}
)


def telemetry_ok(row: Mapping[str, Any]) -> bool:
    """wall_ms + n_new + product_mode required (AY0 real-eval law)."""
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
    """All frozen AY0 battery rows pass anti-FP bars."""
    if len(rows) != len(ASK_BATTERY):
        return False
    ids = {str(r.get("id", "")) for r in rows}
    need = {str(p["id"]) for p in ASK_BATTERY}
    if ids != need:
        return False
    return all(battery_row_ok(r) for r in rows)


def gen_claim_allowed(claim: str) -> bool:
    """True if claim asserts NANOGEN9 / true-continue / mini-AGI unlock."""
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
        "nanogen9",
        "h-nanogen9",
        "mini-agi",
        "generative unlocked",
        "true-gen unlocked",
        "tac unlocked",
    )
    return any(m in cleaned for m in markers)


def nanogen9_outcome_ok(decision: str) -> bool:
    """AY3 may be PROMOTE / HOLD / DEFER (not MISSING / KILL)."""
    d = str(decision)
    if d == "MISSING":
        return False
    return d.startswith(("PROMOTE", "HOLD", "DEFER"))


def claim_is_honest(claim: str, *, nanogen9_decision: str) -> bool:
    """
    GIVEN ship claim + AY3 decision
    WHEN checking AY4 honesty
    THEN reject unlabeled open-chat / GPT-class;
         gen unlock only if NANOGEN9 PROMOTE.
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
    nano = str(nanogen9_decision)
    has_gen = gen_claim_allowed(claim)
    if nano.startswith("PROMOTE"):
        return open_chat_negated
    if has_gen:
        return False
    return open_chat_negated


def decide_ay_real_eval(
    *,
    prodint_decision: str,
    shipay_decision: str,
    nanogen9_decision: str,
    battery_ok: bool,
    claim: str,
) -> str:
    """
    GIVEN AY1/AY2/AY3 decisions + live battery + ship claim
    WHEN applying pesquisa §5 AY4 gate
    THEN PROMOTE iff product pass + battery pass + honest claim under gen lock.
    """
    for name, dec in (
        ("prodint", prodint_decision),
        ("shipay", shipay_decision),
    ):
        if not str(dec).startswith("PROMOTE"):
            if str(dec).startswith("KILL"):
                return f"KILL ({name}: {dec})"
            if str(dec) == "MISSING":
                return f"KILL ({name} summary MISSING)"
            return f"KILL ({name} not PROMOTE: {dec})"
    if not battery_ok:
        return "KILL (live ask battery failed anti-FP / mode bars)"
    nano = str(nanogen9_decision)
    if not nanogen9_outcome_ok(nano):
        return f"KILL (nanogen9 outcome invalid: {nano})"
    if not bool(PROTOCOL.get("span_fallback_neq_gen")):
        return "KILL (protocol must mark span-fallback ≠ gen)"
    if not bool(PROTOCOL.get("eval_eq_prod_ask")):
        return "KILL (protocol must require eval=prod ask)"
    if not bool(PROTOCOL.get("intent_mismatch_is_false_hit")):
        return "KILL (protocol must mark intent mismatch as false-hit)"
    claim_rule = str(PROTOCOL.get("gen_claim_rule", "")).lower()
    if "nanogen9" not in claim_rule:
        return "KILL (protocol gen_claim_rule must name NANOGEN9)"
    if "true_continue" not in claim_rule and "true-continue" not in claim_rule:
        return "KILL (protocol gen_claim_rule must require true_continue)"
    if not claim_is_honest(claim, nanogen9_decision=nano):
        return "KILL (dishonest ship claim)"
    if not nano.startswith("PROMOTE") and gen_claim_allowed(claim):
        return "KILL (generative claim while AY3 not PROMOTE)"
    return "PROMOTE"
