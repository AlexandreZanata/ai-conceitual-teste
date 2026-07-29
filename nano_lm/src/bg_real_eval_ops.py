"""Wave BG6 BG-REAL-EVAL: product+util+ctx+speed + live battery; gen iff NANOGEN17 PROMOTE."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from bg_session_ops import (
    BG0_ANTI_FP,
    BG0_ASK_BATTERY,
    BG0_MODES,
    BG0_REAL_EVAL_PROTOCOL,
    BG0_SAFE_NOTE,
    BG0_SHIP_LOCK,
    map_bg_product_mode,
)
from real_eval_ops import force_abstain_row, near_miss_should_abstain
from shipreal_ops import content_matches_mode

__all__ = [
    "BG_REAL_EVAL_ID",
    "BG_REAL_EVAL_THESIS",
    "BG_REAL_EVAL_CLAIM",
    "BG_REAL_EVAL_SAFE_NOTE",
    "BG_REAL_EVAL_ANTI_FP",
    "ASK_BATTERY",
    "REQUIRED_MODES",
    "PROTOCOL",
    "PARENT_NANOGEN17",
    "DECODE_PATH_KINDS",
    "LOOKUP_KINDS",
    "map_bg_product_mode",
    "telemetry_ok",
    "mode_matches_expect",
    "battery_row_ok",
    "battery_pass",
    "claim_is_honest",
    "gen_claim_allowed",
    "near_miss_should_abstain",
    "force_abstain_row",
    "content_matches_mode",
    "nanogen17_outcome_ok",
    "decide_bg_real_eval",
]

BG_REAL_EVAL_ID = "BG-REAL-EVAL"
BG_REAL_EVAL_THESIS = (
    "Final BG real eval: product+util+ctx+speed pass "
    "(UNARYINT·SHIPPUB·FASTBG·CTXBG) + live ask battery (prod=eval; "
    "BG-FOREVER FP ABSTAIN; BA…BF forever hold; over-refuse LOOKUP; "
    "utilization smoke) + generative claim only if BG5 H-NANOGEN17 PROMOTE "
    "(true_continue; written M1|M2|M3 plan; span-fallback ≠ gen; "
    "never NANOGEN16+rename; else SKIP gen claim)"
)
BG_REAL_EVAL_CLAIM = BG0_SHIP_LOCK
BG_REAL_EVAL_SAFE_NOTE = BG0_SAFE_NOTE
BG_REAL_EVAL_ANTI_FP = BG0_ANTI_FP
ASK_BATTERY: tuple[dict[str, str], ...] = BG0_ASK_BATTERY
REQUIRED_MODES: frozenset[str] = BG0_MODES
PROTOCOL: Mapping[str, object] = BG0_REAL_EVAL_PROTOCOL
PARENT_NANOGEN17 = "SKIP"
DECODE_PATH_KINDS = frozenset(
    {"decode_content", "decode_gibberish_bar", "decode_smoke"}
)
LOOKUP_KINDS = frozenset(
    {"known_lookup", "overrefuse_gold", "utilization_smoke"}
)


def telemetry_ok(row: Mapping[str, Any]) -> bool:
    """wall_ms + n_new + product_mode required (BG0 real-eval law)."""
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
    """All frozen BG0 battery rows pass anti-FP bars."""
    if len(rows) != len(ASK_BATTERY):
        return False
    ids = {str(r.get("id", "")) for r in rows}
    need = {str(p["id"]) for p in ASK_BATTERY}
    if ids != need:
        return False
    return all(battery_row_ok(r) for r in rows)


def gen_claim_allowed(claim: str) -> bool:
    """True if claim asserts NANOGEN17 / true-continue / mini-AGI unlock."""
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
        "nanogen17",
        "h-nanogen17",
        "mini-agi",
        "generative unlocked",
        "true-gen unlocked",
        "tac unlocked",
    )
    return any(m in cleaned for m in markers)


def nanogen17_outcome_ok(decision: str) -> bool:
    """BG5 may be PROMOTE / HOLD / SKIP / DEFER (not MISSING / KILL)."""
    d = str(decision)
    if d == "MISSING":
        return False
    return d.startswith(("PROMOTE", "HOLD", "SKIP", "DEFER"))


def claim_is_honest(claim: str, *, nanogen17_decision: str) -> bool:
    """
    GIVEN ship claim + BG5 decision
    WHEN checking BG6 honesty
    THEN reject unlabeled open-chat / GPT-class;
         gen unlock only if NANOGEN17 PROMOTE.
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
    nano = str(nanogen17_decision)
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
    if not bool(PROTOCOL.get("unary_mismatch_is_false_hit")):
        return "KILL (protocol must mark unary mismatch as false-hit)"
    if not bool(PROTOCOL.get("transform_mismatch_is_false_hit")):
        return "KILL (protocol must mark transform mismatch as false-hit)"
    if not bool(PROTOCOL.get("exact_gold_abstain_is_miss")):
        return "KILL (protocol must mark exact-gold ABSTAIN as miss)"
    if not bool(PROTOCOL.get("utilization_scored")):
        return "KILL (protocol must score utilization)"
    claim_rule = str(PROTOCOL.get("gen_claim_rule", "")).lower()
    if "nanogen17" not in claim_rule:
        return "KILL (protocol gen_claim_rule must name NANOGEN17)"
    if "true_continue" not in claim_rule and "true-continue" not in claim_rule:
        return "KILL (protocol gen_claim_rule must require true_continue)"
    return None


def decide_bg_real_eval(
    *,
    unaryint_decision: str,
    shippub_decision: str,
    fastbg_decision: str,
    ctxbg_decision: str,
    nanogen17_decision: str,
    battery_ok: bool,
    claim: str,
) -> str:
    """
    GIVEN BG1–BG5 decisions + live battery + ship claim
    WHEN applying pesquisa §9 BG6 gate
    THEN PROMOTE iff product/util/ctx/speed pass + battery + honest claim.
    """
    for name, dec in (
        ("unaryint", unaryint_decision),
        ("shippub", shippub_decision),
        ("fastbg", fastbg_decision),
        ("ctxbg", ctxbg_decision),
    ):
        err = _gate_pillar(name, dec)
        if err:
            return err
    if not battery_ok:
        return "KILL (live ask battery failed anti-FP / mode bars)"
    nano = str(nanogen17_decision)
    if not nanogen17_outcome_ok(nano):
        return f"KILL (nanogen17 outcome invalid: {nano})"
    err = _gate_protocol()
    if err:
        return err
    if not claim_is_honest(claim, nanogen17_decision=nano):
        return "KILL (dishonest ship claim)"
    if not nano.startswith("PROMOTE") and gen_claim_allowed(claim):
        return "KILL (generative claim while BG5 not PROMOTE)"
    status = nano.split("(", 1)[0].strip()
    gen_note = (
        "gen unlocked under BG5 PROMOTE"
        if nano.startswith("PROMOTE")
        else f"gen locked under BG5 {status}"
    )
    return (
        f"PROMOTE ({BG_REAL_EVAL_ID}: UNARYINT·SHIPPUB·FASTBG·CTXBG + "
        f"battery {len(ASK_BATTERY)}/{len(ASK_BATTERY)}; {gen_note})"
    )
