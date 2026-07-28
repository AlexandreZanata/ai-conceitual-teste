"""Wave AX4 AX-REAL-EVAL: product pass + live battery; gen only if NANOGEN8 PROMOTE."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ax_session_ops import (
    AX0_ASK_BATTERY,
    AX0_MODES,
    AX0_REAL_EVAL_PROTOCOL,
    AX0_SHIP_LOCK,
    map_ax_product_mode,
)
from real_eval_ops import force_abstain_row, near_miss_should_abstain
from shipux_ops import content_matches_mode

__all__ = [
    "AX_REAL_EVAL_ID",
    "AX_REAL_EVAL_THESIS",
    "AX_REAL_EVAL_CLAIM",
    "ASK_BATTERY",
    "REQUIRED_MODES",
    "PROTOCOL",
    "PARENT_NANOGEN8",
    "DECODE_PATH_KINDS",
    "LOOKUP_KINDS",
    "map_ax_product_mode",
    "telemetry_ok",
    "mode_matches_expect",
    "battery_row_ok",
    "battery_pass",
    "claim_is_honest",
    "gen_claim_allowed",
    "near_miss_should_abstain",
    "force_abstain_row",
    "content_matches_mode",
    "nanogen8_outcome_ok",
    "decide_ax_real_eval",
]

AX_REAL_EVAL_ID = "AX-REAL-EVAL"
AX_REAL_EVAL_THESIS = (
    "Final real eval: Caminho A product pass (PRODNAT+SHIPUX) + "
    "live ask battery (prod=eval) + generative claim only if AX3 "
    "H-NANOGEN8 PROMOTE (true_continue; real new method; "
    "span-fallback ≠ gen; never NANOGEN7+rename)"
)
AX_REAL_EVAL_CLAIM = AX0_SHIP_LOCK
ASK_BATTERY: tuple[dict[str, str], ...] = AX0_ASK_BATTERY
REQUIRED_MODES: frozenset[str] = AX0_MODES
PROTOCOL: Mapping[str, object] = AX0_REAL_EVAL_PROTOCOL
PARENT_NANOGEN8 = "DEFER"
DECODE_PATH_KINDS = frozenset(
    {"decode_content", "decode_gibberish_bar", "decode_smoke"}
)
LOOKUP_KINDS = frozenset({"known_lookup", "human_para", "hard_natural"})


def telemetry_ok(row: Mapping[str, Any]) -> bool:
    """wall_ms + n_new + product_mode required (AX0 real-eval law)."""
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
    """All frozen AX0 battery rows pass anti-FP bars."""
    if len(rows) != len(ASK_BATTERY):
        return False
    ids = {str(r.get("id", "")) for r in rows}
    need = {str(p["id"]) for p in ASK_BATTERY}
    if ids != need:
        return False
    return all(battery_row_ok(r) for r in rows)


def gen_claim_allowed(claim: str) -> bool:
    """True if claim asserts NANOGEN8 / true-continue / mini-AGI unlock."""
    low = str(claim).lower()
    # Honesty negations are not unlock claims.
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
        "nanogen8",
        "h-nanogen8",
        "mini-agi",
        "generative unlocked",
        "true-gen unlocked",
        "tac unlocked",
    )
    return any(m in cleaned for m in markers)


def nanogen8_outcome_ok(decision: str) -> bool:
    """AX3 may be PROMOTE / HOLD / DEFER (not MISSING / KILL)."""
    d = str(decision)
    if d == "MISSING":
        return False
    return d.startswith(("PROMOTE", "HOLD", "DEFER"))


def claim_is_honest(claim: str, *, nanogen8_decision: str) -> bool:
    """
    GIVEN ship claim + AX3 decision
    WHEN checking AX4 honesty
    THEN reject unlabeled open-chat / GPT-class;
         gen unlock only if NANOGEN8 PROMOTE.
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
    nano = str(nanogen8_decision)
    has_gen = gen_claim_allowed(claim)
    if nano.startswith("PROMOTE"):
        return open_chat_negated
    if has_gen:
        return False
    return open_chat_negated


def decide_ax_real_eval(
    *,
    prodnat_decision: str,
    shipux_decision: str,
    nanogen8_decision: str,
    battery_ok: bool,
    claim: str,
) -> str:
    """
    GIVEN AX1/AX2/AX3 decisions + live battery + ship claim
    WHEN applying pesquisa §5 AX4 gate
    THEN PROMOTE iff product pass + battery pass + honest claim under gen lock.
    """
    for name, dec in (
        ("prodnat", prodnat_decision),
        ("shipux", shipux_decision),
    ):
        if not str(dec).startswith("PROMOTE"):
            if str(dec).startswith("KILL"):
                return f"KILL ({name}: {dec})"
            if str(dec) == "MISSING":
                return f"KILL ({name} summary MISSING)"
            return f"KILL ({name} not PROMOTE: {dec})"
    if not battery_ok:
        return "KILL (live ask battery failed anti-FP / mode bars)"
    nano = str(nanogen8_decision)
    if not nanogen8_outcome_ok(nano):
        return f"KILL (nanogen8 outcome invalid: {nano})"
    if not bool(PROTOCOL.get("span_fallback_neq_gen")):
        return "KILL (protocol must mark span-fallback ≠ gen)"
    if not bool(PROTOCOL.get("eval_eq_prod_ask")):
        return "KILL (protocol must require eval=prod ask)"
    claim_rule = str(PROTOCOL.get("gen_claim_rule", "")).lower()
    if "nanogen8" not in claim_rule:
        return "KILL (protocol gen_claim_rule must name NANOGEN8)"
    if "true_continue" not in claim_rule and "true-continue" not in claim_rule:
        return "KILL (protocol gen_claim_rule must require true_continue)"
    if not claim_is_honest(claim, nanogen8_decision=nano):
        return "KILL (dishonest ship claim)"
    if not nano.startswith("PROMOTE") and gen_claim_allowed(claim):
        return "KILL (generative claim while AX3 not PROMOTE)"
    return "PROMOTE"
