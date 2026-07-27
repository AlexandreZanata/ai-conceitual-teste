"""Wave AW4 AW-REAL-EVAL: product keep + live battery; gen only if NANOGEN7 PROMOTE."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from aw_session_ops import (
    AW0_ASK_BATTERY,
    AW0_MODES,
    AW0_REAL_EVAL_PROTOCOL,
    AW0_SHIP_LOCK,
    map_aw_product_mode,
)
from real_eval_ops import force_abstain_row, near_miss_should_abstain
from shipreal_ops import content_matches_mode

__all__ = [
    "AW_REAL_EVAL_ID",
    "AW_REAL_EVAL_THESIS",
    "AW_REAL_EVAL_CLAIM",
    "ASK_BATTERY",
    "REQUIRED_MODES",
    "PROTOCOL",
    "PARENT_NANOGEN7",
    "DECODE_PATH_KINDS",
    "map_aw_product_mode",
    "telemetry_ok",
    "mode_matches_expect",
    "battery_row_ok",
    "battery_pass",
    "claim_is_honest",
    "gen_claim_allowed",
    "near_miss_should_abstain",
    "force_abstain_row",
    "content_matches_mode",
    "decide_aw_real_eval",
]

AW_REAL_EVAL_ID = "AW-REAL-EVAL"
AW_REAL_EVAL_THESIS = (
    "Final real eval: Caminho A product pass (PRODKEEP+SHIPKEEP) + "
    "live ask battery (prod=eval) + generative claim only if AW3 "
    "H-NANOGEN7 PROMOTE (TAC true_continue; span-fallback ≠ gen credit)"
)
AW_REAL_EVAL_CLAIM = AW0_SHIP_LOCK
ASK_BATTERY: tuple[dict[str, str], ...] = AW0_ASK_BATTERY
REQUIRED_MODES: frozenset[str] = AW0_MODES
PROTOCOL: Mapping[str, object] = AW0_REAL_EVAL_PROTOCOL
PARENT_NANOGEN7 = "HOLD"
DECODE_PATH_KINDS = frozenset(
    {"decode_content", "decode_gibberish_bar", "decode_smoke"}
)


def telemetry_ok(row: Mapping[str, Any]) -> bool:
    """wall_ms + n_new + product_mode required (AW0 real-eval law)."""
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
    """All frozen AW0 battery rows pass anti-FP bars."""
    if len(rows) != len(ASK_BATTERY):
        return False
    ids = {str(r.get("id", "")) for r in rows}
    need = {str(p["id"]) for p in ASK_BATTERY}
    if ids != need:
        return False
    return all(battery_row_ok(r) for r in rows)


def gen_claim_allowed(claim: str) -> bool:
    """True if claim asserts NANOGEN7 TAC / mini-AGI unlock."""
    low = str(claim).lower()
    markers = (
        "true-continue",
        "true continue",
        "true_continue",
        "nanogen7",
        "h-nanogen7",
        "tac ",
        " teacher-anchored",
        "mini-agi",
        "generative unlocked",
        "true-gen unlocked",
    )
    return any(m in low for m in markers)


def claim_is_honest(claim: str, *, nanogen7_decision: str) -> bool:
    """
    GIVEN ship claim + AW3 decision
    WHEN checking AW4 honesty
    THEN reject unlabeled open-chat / GPT-class;
         TAC unlock only if NANOGEN7 PROMOTE.
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
    nano = str(nanogen7_decision)
    has_gen = gen_claim_allowed(claim)
    if nano.startswith("PROMOTE"):
        return open_chat_negated
    if has_gen:
        return False
    return open_chat_negated


def decide_aw_real_eval(
    *,
    prodkeep_decision: str,
    shipkeep_decision: str,
    nanogen7_decision: str,
    battery_ok: bool,
    claim: str,
) -> str:
    """
    GIVEN AW1/AW2/AW3 decisions + live battery + ship claim
    WHEN applying pesquisa §2 AW4 gate
    THEN PROMOTE iff product pass + battery pass + honest claim under gen lock.
    """
    for name, dec in (
        ("prodkeep", prodkeep_decision),
        ("shipkeep", shipkeep_decision),
    ):
        if not str(dec).startswith("PROMOTE"):
            if str(dec).startswith("KILL"):
                return f"KILL ({name}: {dec})"
            if str(dec) == "MISSING":
                return f"KILL ({name} summary MISSING)"
            return f"KILL ({name} not PROMOTE: {dec})"
    if not battery_ok:
        return "KILL (live ask battery failed anti-FP / mode bars)"
    nano = str(nanogen7_decision)
    if nano == "MISSING":
        return "KILL (nanogen7 summary MISSING)"
    if not bool(PROTOCOL.get("span_fallback_neq_gen")):
        return "KILL (protocol must mark span-fallback ≠ gen)"
    if not bool(PROTOCOL.get("eval_eq_prod_ask")):
        return "KILL (protocol must require eval=prod ask)"
    claim_rule = str(PROTOCOL.get("gen_claim_rule", "")).lower()
    if "nanogen7" not in claim_rule or "tac" not in claim_rule:
        return "KILL (protocol gen_claim_rule must name NANOGEN7 TAC)"
    if not claim_is_honest(claim, nanogen7_decision=nano):
        return "KILL (dishonest ship claim)"
    if not nano.startswith("PROMOTE") and gen_claim_allowed(claim):
        return "KILL (generative claim while AW3 HOLD)"
    return "PROMOTE"
