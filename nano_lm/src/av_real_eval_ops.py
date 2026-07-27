"""Wave AV4 AV-REAL-EVAL: product + live battery; gen only if NANOGEN6 PROMOTE."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from av_session_ops import (
    AV0_ASK_BATTERY,
    AV0_MODES,
    AV0_REAL_EVAL_PROTOCOL,
    AV0_SHIP_LOCK,
    map_av_product_mode,
)
from real_eval_ops import force_abstain_row, near_miss_should_abstain
from shipreal_ops import content_matches_mode

__all__ = [
    "AV_REAL_EVAL_ID",
    "AV_REAL_EVAL_THESIS",
    "AV_REAL_EVAL_CLAIM",
    "ASK_BATTERY",
    "REQUIRED_MODES",
    "PROTOCOL",
    "PARENT_NANOGEN6",
    "DECODE_PATH_KINDS",
    "map_av_product_mode",
    "telemetry_ok",
    "mode_matches_expect",
    "battery_row_ok",
    "battery_pass",
    "claim_is_honest",
    "gen_claim_allowed",
    "near_miss_should_abstain",
    "force_abstain_row",
    "content_matches_mode",
    "decide_av_real_eval",
]

AV_REAL_EVAL_ID = "AV-REAL-EVAL"
AV_REAL_EVAL_THESIS = (
    "Final real eval: Caminho A product pass (PRODSHIP+SHIPUI2) + "
    "live ask battery (prod=eval) + generative claim only if AV3 "
    "H-NANOGEN6 PROMOTE (true_continue; span-fallback ≠ gen credit)"
)
# Default ship claim while NANOGEN6 HOLD — AU STRICT archive, no true-continue unlock.
AV_REAL_EVAL_CLAIM = AV0_SHIP_LOCK
ASK_BATTERY: tuple[dict[str, str], ...] = AV0_ASK_BATTERY
REQUIRED_MODES: frozenset[str] = AV0_MODES
PROTOCOL: Mapping[str, object] = AV0_REAL_EVAL_PROTOCOL
PARENT_NANOGEN6 = "HOLD"
DECODE_PATH_KINDS = frozenset(
    {"decode_content", "decode_gibberish_bar", "decode_smoke"}
)


def telemetry_ok(row: Mapping[str, Any]) -> bool:
    """
    GIVEN a live ask row
    WHEN checking AV0 real-eval telemetry law
    THEN wall_ms + n_new + product_mode required.
    """
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
    """
    Exact mode match, or DECODE-path honesty:
    usable DECODE or ABSTAIN after junk gate (≠ telemetry-only DECODE).
    """
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
    """All frozen AV0 battery rows pass anti-FP bars."""
    if len(rows) != len(ASK_BATTERY):
        return False
    ids = {str(r.get("id", "")) for r in rows}
    need = {str(p["id"]) for p in ASK_BATTERY}
    if ids != need:
        return False
    return all(battery_row_ok(r) for r in rows)


def gen_claim_allowed(claim: str) -> bool:
    """
    True if claim asserts NANOGEN6 true-continue / mini-AGI unlock.
    AU STRICT archive ship lock alone is NOT a gen unlock.
    """
    low = str(claim).lower()
    markers = (
        "true-continue",
        "true continue",
        "true_continue",
        "nanogen6",
        "h-nanogen6",
        "mini-agi",
        "generative unlocked",
        "true-gen unlocked",
    )
    return any(m in low for m in markers)


def claim_is_honest(claim: str, *, nanogen6_decision: str) -> bool:
    """
    GIVEN ship claim + AV3 decision
    WHEN checking AV4 honesty
    THEN reject unlabeled open-chat / GPT-class;
         true-continue unlock only if NANOGEN6 PROMOTE.
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
    nano = str(nanogen6_decision)
    has_gen = gen_claim_allowed(claim)
    if nano.startswith("PROMOTE"):
        return open_chat_negated
    if has_gen:
        return False
    return open_chat_negated


def decide_av_real_eval(
    *,
    prodship_decision: str,
    shipui2_decision: str,
    nanogen6_decision: str,
    battery_ok: bool,
    claim: str,
) -> str:
    """
    GIVEN AV1/AV2/AV3 decisions + live battery + ship claim
    WHEN applying pesquisa §5 AV4 gate
    THEN PROMOTE iff product pass + battery pass + honest claim under gen lock.
    """
    for name, dec in (
        ("prodship", prodship_decision),
        ("shipui2", shipui2_decision),
    ):
        if not str(dec).startswith("PROMOTE"):
            if str(dec).startswith("KILL"):
                return f"KILL ({name}: {dec})"
            if str(dec) == "MISSING":
                return f"KILL ({name} summary MISSING)"
            return f"KILL ({name} not PROMOTE: {dec})"
    if not battery_ok:
        return "KILL (live ask battery failed anti-FP / mode bars)"
    nano = str(nanogen6_decision)
    if nano == "MISSING":
        return "KILL (nanogen6 summary MISSING)"
    if not bool(PROTOCOL.get("span_fallback_neq_gen")):
        return "KILL (protocol must mark span-fallback ≠ gen)"
    if not claim_is_honest(claim, nanogen6_decision=nano):
        return "KILL (dishonest ship claim)"
    if not nano.startswith("PROMOTE") and gen_claim_allowed(claim):
        return "KILL (generative claim while AV3 HOLD)"
    return "PROMOTE"
