"""Wave BF2 H-SHIPUSE2: Track A+ utilization — deepen demo + operator + paper."""

from __future__ import annotations

import re
from typing import Any, Mapping, MutableMapping, Sequence

from az_session_ops import AZ0_MODES, AZ0_OVERREFUSE_ROWS
from be_session_ops import BE0_FOREVER_ROWS, BE0_SAFE_NOTE
from bf_session_ops import BF0_ANTI_FP, BF0_FOREVER_ROWS, BF0_SHIP_LOCK, BF0_UTIL_TRACK
from prodhard_ops import KNOWN_ASK, NEAR_MISS_ASK, PEAK_ASK
from shipaz_ops import attach_shipaz
from shipui2_ops import (
    REQUIRED_MODES,
    arms_honest_ok,
    banner_modes_ok,
    content_matches_mode,
    core_modes_ok,
)
from shipui2_ops import demo_card_markdown as shipui2_demo_card
from shipux_ops import mode_visible

__all__ = [
    "SHIPUSE2_ID",
    "SHIPUSE2_THESIS",
    "SHIPUSE2_CLAIM",
    "SHIPUSE2_SAFE_NOTE",
    "SHIPUSE2_ANTI_FP",
    "SHIPUSE2_CHARTER",
    "SHIPUSE2_PATHS",
    "REQUIRED_MODES",
    "KNOWN_ASK",
    "NEAR_MISS_ASK",
    "PEAK_ASK",
    "BE_RESIDUAL_ASK",
    "BF_RESIDUAL_ASK",
    "APPEND_ASK",
    "OVERREFUSE_ASK",
    "OOD_ASK",
    "attach_shipuse2",
    "mode_visible",
    "content_matches_mode",
    "banner_modes_ok",
    "arms_honest_ok",
    "core_modes_ok",
    "demo_card_markdown",
    "operator_card_ok",
    "paper_claim_ok",
    "claim_matches_live",
    "decide_shipuse2",
]

SHIPUSE2_ID = "H-SHIPUSE2"
SHIPUSE2_THESIS = (
    "Track A+ utilization deepen: hold H-SHIPUSE demo·operator·paper; "
    "live BF residual (even≠add) ABSTAIN + append LOOKUP smoke; "
    "operator path + paper claim sync under H-PREDINT — no GPT unlock"
)
SHIPUSE2_CLAIM = BF0_SHIP_LOCK
SHIPUSE2_SAFE_NOTE = BE0_SAFE_NOTE
SHIPUSE2_ANTI_FP = BF0_ANTI_FP
SHIPUSE2_PATHS: tuple[str, ...] = (
    "nano:z:ask --wrap --semwrap",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
    "npm run paper:build",
)
BE_RESIDUAL_ASK = str(BE0_FOREVER_ROWS[0]["question"])
BF_RESIDUAL_ASK = str(BF0_FOREVER_ROWS[0]["question"])
APPEND_ASK = "How do I append x to list a in one Python method call?"
OVERREFUSE_ASK = str(AZ0_OVERREFUSE_ROWS[0]["question"])
OOD_ASK = "Who won the 2022 FIFA World Cup?"

_OPERATOR_NEEDLES: tuple[str, ...] = (
    "nano:z:ask",
    "semwrap",
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
    "H-PREDINT",
)
_CLAIM_NEEDLES: tuple[str, ...] = (
    "AF packaged",
    "STRICT",
    "not unlabeled open chat",
)
_FORBIDDEN_UNLOCK: tuple[str, ...] = (
    "true-continue unlocked",
    "TAC unlocked",
    "open chat LM unlocked",
    "GPT-class unlock",
    "mini-AGI unlock",
)

SHIPUSE2_CHARTER: Mapping[str, object] = {
    "paths": list(SHIPUSE2_PATHS),
    "required_modes": list(REQUIRED_MODES),
    "banner": "mode=LOOKUP|PEAK|DECODE|ABSTAIN",
    "smoke": "demo + BE/BF residual + append + clear + OOD",
    "known_ask_hitl": True,
    "ship_surface_doc": True,
    "paper_archive": True,
    "operator_card": True,
    "claim_matches_live": True,
    "gpt_claim_forbidden": True,
    "modes_visible_required": True,
    "be_residual_abstain": True,
    "bf_residual_abstain": True,
    "append_labeled_lookup": True,
    "h_shipuse_hold": True,
    "overrefuse_labeled_lookup": True,
    "cite_be_locks": ["H-COMPINT", "H-SHIPUSE", "H-PREDINT", "H-SHIPUSE2"],
    "util_track": dict(BF0_UTIL_TRACK),
    "regression_hold": True,
    "rule": (
        "Track A+ deepen: hold H-SHIPUSE; BF residual ABSTAIN; "
        "append LOOKUP; operator + paper sync; modes always visible"
    ),
    "anti_fp": (
        "SHIPUSE2 utilization ≠ generative IQ; "
        "claim/doc drift = fail; GPT claim forbidden; "
        "BF residual LOOKUP = false-hit; H-SHIPUSE hold"
    ),
    "stage": "BF2 H-SHIPUSE2",
}


def attach_shipuse2(payload: MutableMapping[str, Any]) -> dict[str, Any]:
    """Attach product_mode + modeui_line (reuse SHIPAZ law)."""
    return attach_shipaz(payload)


def demo_card_markdown(
    *,
    arms: Sequence[Mapping[str, Any]],
    probes: Sequence[Mapping[str, Any]] | None = None,
) -> str:
    """Human utilization demo card for Track A+."""
    body = shipui2_demo_card(arms=arms, apps=probes or (), decode_probe=None)
    return (
        body.replace("SHIPUI2", "SHIPUSE2")
        .replace("SHIPAY", "SHIPUSE2")
        .replace("SHIPAZ", "SHIPUSE2")
        .replace("SHIPUSE —", "SHIPUSE2 —")
    )


def operator_card_ok(*, recipes: str, card: str) -> bool:
    """
    GIVEN RECIPES + champion-card text
    WHEN checking Track A+ operator card
    THEN True iff both expose ask path + four modes + H-PREDINT.
    """
    for blob in (recipes, card):
        for needle in _OPERATOR_NEEDLES:
            if needle not in blob:
                return False
    return True


def _has_forbidden_unlock(text: str) -> bool:
    """True iff unlock language appears without an explicit negation."""
    low = text.lower()
    scrubbed = re.sub(r"do\s+\*\*not\*\*\s+claim[^\n.]*", "", low)
    scrubbed = re.sub(r"do\s+not\s+claim[^\n.]*", "", scrubbed)
    for bad in _FORBIDDEN_UNLOCK:
        scrubbed = scrubbed.replace(f"not {bad.lower()}", "")
    for bad in _FORBIDDEN_UNLOCK:
        if bad.lower() in scrubbed:
            return True
    return False


def paper_claim_ok(*, narrative: str, paper_tex: str) -> bool:
    """
    GIVEN paper narrative + sections tex
    WHEN checking claim sync
    THEN True iff ship lock needles present and unlock phrases absent.
    """
    joined = f"{narrative}\n{paper_tex}"
    low = joined.lower()
    for needle in _CLAIM_NEEDLES:
        if needle.lower() not in low:
            return False
    if _has_forbidden_unlock(joined):
        return False
    if "hold/defer" not in low and "hold" not in low:
        return False
    return "≤5m" in low or "<=5m" in low or "5m" in low


def claim_matches_live(
    *,
    claim: str,
    arms: Sequence[Mapping[str, Any]],
    probes: Sequence[Mapping[str, Any]],
) -> bool:
    """
    GIVEN ship claim + live labeled rows
    WHEN checking claim/live drift
    THEN True iff modes visible and claim forbids open chat / TAC unlock.
    """
    if "not unlabeled open chat" not in claim.lower():
        return False
    if "not tac unlocked" not in claim.lower():
        return False
    rows = list(arms) + list(probes)
    if not rows:
        return False
    for row in rows:
        if not mode_visible(row):
            return False
        if not content_matches_mode(row):
            return False
    return True


def _row_mode(row: Mapping[str, Any] | None, expect: str) -> bool:
    if row is None:
        return False
    if str(row.get("product_mode") or "") != expect:
        return False
    return mode_visible(row) and content_matches_mode(row)


def _find_q(
    rows: Sequence[Mapping[str, Any]], *, exact: str, needle: str
) -> Mapping[str, Any] | None:
    for row in rows:
        q = str(row.get("question") or "")
        if q == exact or needle.lower() in q.lower():
            return row
    return None


def _be_residual_ok(probes: Sequence[Mapping[str, Any]]) -> bool:
    row = _find_q(probes, exact=BE_RESIDUAL_ASK, needle="convert string")
    return _row_mode(row, "ABSTAIN")


def _bf_residual_ok(probes: Sequence[Mapping[str, Any]]) -> bool:
    row = _find_q(probes, exact=BF_RESIDUAL_ASK, needle="is even")
    return _row_mode(row, "ABSTAIN")


def _append_ok(probes: Sequence[Mapping[str, Any]]) -> bool:
    row = _find_q(probes, exact=APPEND_ASK, needle="append x to list")
    if not _row_mode(row, "LOOKUP"):
        return False
    assert row is not None
    return "append" in str(row.get("completion", "")).lower()


def _overrefuse_ok(probes: Sequence[Mapping[str, Any]]) -> bool:
    row = _find_q(probes, exact=OVERREFUSE_ASK, needle="Remove all items")
    if not _row_mode(row, "LOOKUP"):
        return False
    assert row is not None
    return "clear" in str(row.get("completion", "")).lower()


def _known_ok(probes: Sequence[Mapping[str, Any]]) -> bool:
    row = _find_q(probes, exact=KNOWN_ASK, needle="named add")
    if row is None:
        row = _find_q(probes, exact=KNOWN_ASK, needle="sum of two")
    return _row_mode(row, "LOOKUP")


def _ood_ok(probes: Sequence[Mapping[str, Any]]) -> bool:
    row = _find_q(probes, exact=OOD_ASK, needle="FIFA World Cup")
    return _row_mode(row, "ABSTAIN")


def _charter_ok(src: Mapping[str, object]) -> str | None:
    if not bool(src.get("regression_hold", True)):
        return "KILL (SHIPUSE2 must require regression_hold)"
    modes = set(src.get("required_modes") or [])
    if modes and modes != set(AZ0_MODES):
        return "KILL (SHIPUSE2 modes ≠ AZ0 mode charter)"
    cited = set(src.get("cite_be_locks") or [])
    need = {"H-COMPINT", "H-SHIPUSE", "H-PREDINT", "H-SHIPUSE2"}
    if not need <= cited:
        return "KILL (SHIPUSE2 must cite H-COMPINT·H-SHIPUSE·H-PREDINT·H-SHIPUSE2)"
    util = src.get("util_track") or {}
    if not isinstance(util, Mapping):
        return "KILL (SHIPUSE2 util_track missing)"
    if "SHIPUSE2" not in str(util.get("bf2_gate", "")):
        return "KILL (util track must gate H-SHIPUSE2)"
    if not bool(src.get("h_shipuse_hold", True)):
        return "KILL (SHIPUSE2 must hold H-SHIPUSE)"
    return None


def decide_shipuse2(
    *,
    arms: Sequence[Mapping[str, Any]],
    probes: Sequence[Mapping[str, Any]],
    decode_probe: Mapping[str, Any],
    near_miss: Mapping[str, Any] | None,
    recipes: str,
    card: str,
    narrative: str,
    paper_tex: str,
    paper_build_ok: bool,
    charter: Mapping[str, object] | None = None,
    anti_fp_signed: bool = True,
) -> str:
    """
    GIVEN Track A+ deepen after H-PREDINT + H-SHIPUSE hold
    WHEN applying pesquisa §9 BF2 H-SHIPUSE2
    THEN PROMOTE iff demo smoke · operator card · paper claim sync ·
         BE/BF residual ABSTAIN · append+clear LOOKUP · claim matches live.
    """
    if not anti_fp_signed:
        return "KILL (SHIPUSE2 anti-FP must be signed)"
    src = charter if charter is not None else SHIPUSE2_CHARTER
    bad = _charter_ok(src)
    if bad:
        return bad
    if not banner_modes_ok():
        return "KILL (SHIPUSE2 banner modes incomplete)"
    if not core_modes_ok(arms):
        return "KILL (SHIPUSE2 core LOOKUP·PEAK·ABSTAIN missing)"
    if not arms_honest_ok(arms):
        return "KILL (SHIPUSE2 arms unlabeled or content dishonest)"
    dec_mode = str(decode_probe.get("product_mode") or "")
    if dec_mode not in AZ0_MODES or not mode_visible(decode_probe):
        return "KILL (SHIPUSE2 DECODE probe unlabeled)"
    if not content_matches_mode(decode_probe):
        return "KILL (SHIPUSE2 DECODE probe content dishonest)"
    if near_miss is not None and not _row_mode(near_miss, "ABSTAIN"):
        return "KILL (SHIPUSE2 near-miss not ABSTAIN)"
    if bool(src.get("known_ask_hitl", True)) and not _known_ok(probes):
        return "KILL (known-ask HITL not labeled LOOKUP)"
    if bool(src.get("be_residual_abstain", True)) and not _be_residual_ok(probes):
        return "KILL (BE residual not labeled ABSTAIN on ship path)"
    if bool(src.get("bf_residual_abstain", True)) and not _bf_residual_ok(probes):
        return "KILL (BF residual not labeled ABSTAIN on ship path)"
    if bool(src.get("append_labeled_lookup", True)) and not _append_ok(probes):
        return "KILL (append gold not labeled LOOKUP)"
    if bool(src.get("overrefuse_labeled_lookup", True)) and not _overrefuse_ok(
        probes
    ):
        return "KILL (over-refuse clear not labeled LOOKUP)"
    if not _ood_ok(probes):
        return "KILL (OOD ask not labeled ABSTAIN)"
    if bool(src.get("operator_card", True)) and not operator_card_ok(
        recipes=recipes, card=card
    ):
        return "KILL (operator card missing ask path / modes / H-PREDINT)"
    if bool(src.get("paper_archive", True)):
        if not paper_claim_ok(narrative=narrative, paper_tex=paper_tex):
            return "KILL (paper claim out of sync / unlock language)"
        if not paper_build_ok:
            return "KILL (paper:build failed or PDF missing)"
    if bool(src.get("claim_matches_live", True)) and not claim_matches_live(
        claim=SHIPUSE2_CLAIM, arms=arms, probes=probes
    ):
        return "KILL (claim/live drift on modes or ship lock)"
    if bool(src.get("gpt_claim_forbidden", True)):
        blob = f"{recipes}\n{card}\n{narrative}"
        if _has_forbidden_unlock(blob):
            return "KILL (GPT / open-chat claim forbidden)"
    return (
        f"PROMOTE ({SHIPUSE2_ID}: Track A+ deepen · H-SHIPUSE hold · "
        "BF residual ABSTAIN · operator · paper sync)"
    )
