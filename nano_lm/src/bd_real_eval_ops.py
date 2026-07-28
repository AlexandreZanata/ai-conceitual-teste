"""Wave BD5 BD-REAL-EVAL: product+ctx+speed pass + live battery; gen iff NANOGEN14 PROMOTE."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from bd_session_ops import (
    BD0_ANTI_FP,
    BD0_ASK_BATTERY,
    BD0_MODES,
    BD0_REAL_EVAL_PROTOCOL,
    BD0_SAFE_NOTE,
    BD0_SHIP_LOCK,
    map_bd_product_mode,
)
from real_eval_ops import force_abstain_row, near_miss_should_abstain
from shipreal_ops import content_matches_mode

__all__ = [
    "BD_REAL_EVAL_ID",
    "BD_REAL_EVAL_THESIS",
    "BD_REAL_EVAL_CLAIM",
    "BD_REAL_EVAL_SAFE_NOTE",
    "BD_REAL_EVAL_ANTI_FP",
    "ASK_BATTERY",
    "REQUIRED_MODES",
    "PROTOCOL",
    "PARENT_NANOGEN14",
    "DECODE_PATH_KINDS",
    "LOOKUP_KINDS",
    "map_bd_product_mode",
    "telemetry_ok",
    "mode_matches_expect",
    "battery_row_ok",
    "battery_pass",
    "claim_is_honest",
    "gen_claim_allowed",
    "near_miss_should_abstain",
    "force_abstain_row",
    "content_matches_mode",
    "nanogen14_outcome_ok",
    "decide_bd_real_eval",
]

BD_REAL_EVAL_ID = "BD-REAL-EVAL"
BD_REAL_EVAL_THESIS = (
    "Final BD real eval: product+ctx+speed pass "
    "(SEMINT·FASTGAIN·CTXGAIN) + live ask battery (prod=eval; "
    "BD-FOREVER FP ABSTAIN; BA/BB/BC forever hold; over-refuse LOOKUP) + "
    "generative claim only if BD4 H-NANOGEN14 PROMOTE (true_continue; "
    "real M1|M2|M3; span-fallback ≠ gen; never NANOGEN13+rename)"
)
BD_REAL_EVAL_CLAIM = BD0_SHIP_LOCK
BD_REAL_EVAL_SAFE_NOTE = BD0_SAFE_NOTE
BD_REAL_EVAL_ANTI_FP = BD0_ANTI_FP
ASK_BATTERY: tuple[dict[str, str], ...] = BD0_ASK_BATTERY
REQUIRED_MODES: frozenset[str] = BD0_MODES
PROTOCOL: Mapping[str, object] = BD0_REAL_EVAL_PROTOCOL
PARENT_NANOGEN14 = "DEFER"
DECODE_PATH_KINDS = frozenset(
    {"decode_content", "decode_gibberish_bar", "decode_smoke"}
)
LOOKUP_KINDS = frozenset({"known_lookup", "overrefuse_gold"})


def telemetry_ok(row: Mapping[str, Any]) -> bool:
    """wall_ms + n_new + product_mode required (BD0 real-eval law)."""
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
    """All frozen BD0 battery rows pass anti-FP bars."""
    if len(rows) != len(ASK_BATTERY):
        return False
    ids = {str(r.get("id", "")) for r in rows}
    need = {str(p["id"]) for p in ASK_BATTERY}
    if ids != need:
        return False
    return all(battery_row_ok(r) for r in rows)


def gen_claim_allowed(claim: str) -> bool:
    """True if claim asserts NANOGEN14 / true-continue / mini-AGI unlock."""
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
        "nanogen14",
        "h-nanogen14",
        "mini-agi",
        "generative unlocked",
        "true-gen unlocked",
        "tac unlocked",
    )
    return any(m in cleaned for m in markers)


def nanogen14_outcome_ok(decision: str) -> bool:
    """BD4 may be PROMOTE / HOLD / DEFER (not MISSING / KILL)."""
    d = str(decision)
    if d == "MISSING":
        return False
    return d.startswith(("PROMOTE", "HOLD", "DEFER"))


def claim_is_honest(claim: str, *, nanogen14_decision: str) -> bool:
    """
    GIVEN ship claim + BD4 decision
    WHEN checking BD5 honesty
    THEN reject unlabeled open-chat / GPT-class;
         gen unlock only if NANOGEN14 PROMOTE.
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
    nano = str(nanogen14_decision)
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
    claim_rule = str(PROTOCOL.get("gen_claim_rule", "")).lower()
    if "nanogen14" not in claim_rule:
        return "KILL (protocol gen_claim_rule must name NANOGEN14)"
    if "true_continue" not in claim_rule and "true-continue" not in claim_rule:
        return "KILL (protocol gen_claim_rule must require true_continue)"
    return None


def decide_bd_real_eval(
    *,
    semint_decision: str,
    fastgain_decision: str,
    ctxgain_decision: str,
    nanogen14_decision: str,
    battery_ok: bool,
    claim: str,
) -> str:
    """
    GIVEN BD1–BD4 decisions + live battery + ship claim
    WHEN applying pesquisa §9 BD5 gate
    THEN PROMOTE iff product/ctx/speed pass + battery + honest claim under gen lock.
    """
    for name, dec in (
        ("semint", semint_decision),
        ("fastgain", fastgain_decision),
        ("ctxgain", ctxgain_decision),
    ):
        err = _gate_pillar(name, dec)
        if err:
            return err
    if not battery_ok:
        return "KILL (live ask battery failed anti-FP / mode bars)"
    nano = str(nanogen14_decision)
    if not nanogen14_outcome_ok(nano):
        return f"KILL (nanogen14 outcome invalid: {nano})"
    err = _gate_protocol()
    if err:
        return err
    if not claim_is_honest(claim, nanogen14_decision=nano):
        return "KILL (dishonest ship claim)"
    if not nano.startswith("PROMOTE") and gen_claim_allowed(claim):
        return "KILL (generative claim while BD4 not PROMOTE)"
    status = nano.split("(", 1)[0].strip()
    gen_note = (
        "gen unlocked under BD4 PROMOTE"
        if nano.startswith("PROMOTE")
        else f"gen locked under BD4 {status}"
    )
    return (
        f"PROMOTE ({BD_REAL_EVAL_ID}: SEMINT·FASTGAIN·CTXGAIN + "
        f"battery {len(ASK_BATTERY)}/{len(ASK_BATTERY)}; {gen_note})"
    )
