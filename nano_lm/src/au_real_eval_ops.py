"""Wave AU4 AU-REAL-EVAL: product + STRICT gen + live ask battery."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from au_session_ops import (
    AU0_ASK_BATTERY,
    AU0_MODES,
    AU0_REAL_EVAL_PROTOCOL,
    map_au_product_mode,
)
from real_eval_ops import force_abstain_row, near_miss_should_abstain
from shipreal_ops import content_matches_mode

__all__ = [
    "AU_REAL_EVAL_ID",
    "AU_REAL_EVAL_THESIS",
    "AU_REAL_EVAL_CLAIM",
    "ASK_BATTERY",
    "REQUIRED_MODES",
    "PROTOCOL",
    "PARENT_NANOGEN5_STRICT",
    "map_au_product_mode",
    "telemetry_ok",
    "mode_matches_expect",
    "battery_row_ok",
    "battery_pass",
    "claim_is_honest",
    "gen_claim_allowed",
    "near_miss_should_abstain",
    "force_abstain_row",
    "content_matches_mode",
    "decide_au_real_eval",
]

AU_REAL_EVAL_ID = "AU-REAL-EVAL"
AU_REAL_EVAL_THESIS = (
    "Final real eval: Caminho A product pass (PRODHARD+SHIPREAL) + "
    "live ask battery (prod=eval) + generative claim only if AU3 "
    "H-NANOGEN5 PROMOTE (strict_ablated≥5.5)"
)
AU_REAL_EVAL_CLAIM = (
    "AF packaged stack + AQ product layer + AS trust path + "
    "ablated DECODE (snippet-prefix + gibberish-tail STRICT) — "
    "not unlabeled open chat LM"
)
ASK_BATTERY: tuple[dict[str, str], ...] = AU0_ASK_BATTERY
REQUIRED_MODES: frozenset[str] = AU0_MODES
PROTOCOL: Mapping[str, object] = AU0_REAL_EVAL_PROTOCOL
PARENT_NANOGEN5_STRICT = 5.5


def telemetry_ok(row: Mapping[str, Any]) -> bool:
    """
    GIVEN a live ask row
    WHEN checking AU0 real-eval telemetry law
    THEN wall_ms + n_new + product_mode required.
    """
    if "wall_ms" not in row or "n_new" not in row:
        return False
    mode = str(row.get("product_mode", "") or "")
    return mode in REQUIRED_MODES


def mode_matches_expect(*, product_mode: str, expect_mode: str) -> bool:
    """Exact product_mode == battery expect_mode."""
    return str(product_mode) == str(expect_mode)


def battery_row_ok(row: Mapping[str, Any]) -> bool:
    """Labeled mode matches expect + telemetry + answer usability."""
    if not telemetry_ok(row):
        return False
    if not mode_matches_expect(
        product_mode=str(row.get("product_mode", "")),
        expect_mode=str(row.get("expect_mode", "")),
    ):
        return False
    if bool(PROTOCOL.get("answer_usability_scored")):
        return bool(row.get("content_ok", content_matches_mode(row)))
    return True


def battery_pass(rows: Sequence[Mapping[str, Any]]) -> bool:
    """All frozen AU0 battery rows pass anti-FP bars."""
    if len(rows) != len(ASK_BATTERY):
        return False
    ids = {str(r.get("id", "")) for r in rows}
    need = {str(p["id"]) for p in ASK_BATTERY}
    if ids != need:
        return False
    return all(battery_row_ok(r) for r in rows)


def gen_claim_allowed(claim: str) -> bool:
    """True if claim asserts STRICT ablated DECODE / mini-AGI language."""
    low = str(claim).lower()
    markers = (
        "ablated",
        "snippet-prefix",
        "gibberish-tail",
        "strict",
        "mini-agi",
        "true-gen unlocked",
        "generative unlocked",
    )
    return any(m in low for m in markers)


def claim_is_honest(claim: str, *, nanogen5_decision: str) -> bool:
    """
    GIVEN ship claim + AU3 decision
    WHEN checking AU4 honesty
    THEN reject unlabeled open-chat / GPT-class; allow STRICT ablated iff PROMOTE.
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
    nano = str(nanogen5_decision)
    has_gen = gen_claim_allowed(claim)
    if nano.startswith("PROMOTE"):
        return open_chat_negated
    if has_gen:
        return False
    return open_chat_negated


def decide_au_real_eval(
    *,
    prodhard_decision: str,
    shipreal_decision: str,
    nanogen5_decision: str,
    battery_ok: bool,
    claim: str,
) -> str:
    """
    GIVEN AU1/AU2/AU3 decisions + live battery + ship claim
    WHEN applying pesquisa §5 AU4 gate
    THEN PROMOTE iff product pass + battery pass + honest claim under gen lock.
    """
    for name, dec in (
        ("prodhard", prodhard_decision),
        ("shipreal", shipreal_decision),
    ):
        if not str(dec).startswith("PROMOTE"):
            if str(dec).startswith("KILL"):
                return f"KILL ({name}: {dec})"
            if str(dec) == "MISSING":
                return f"KILL ({name} summary MISSING)"
            return f"KILL ({name} not PROMOTE: {dec})"
    if not battery_ok:
        return "KILL (live ask battery failed anti-FP / mode bars)"
    nano = str(nanogen5_decision)
    if nano == "MISSING":
        return "KILL (nanogen5 summary MISSING)"
    if not claim_is_honest(claim, nanogen5_decision=nano):
        return "KILL (dishonest ship claim)"
    if not nano.startswith("PROMOTE") and gen_claim_allowed(claim):
        return "KILL (generative claim while AU3 HOLD)"
    return "PROMOTE"
