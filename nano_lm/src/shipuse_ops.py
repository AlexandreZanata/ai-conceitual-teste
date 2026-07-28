"""Wave BE2 H-SHIPUSE: Track A utilization — demo + operator + paper sync."""

from __future__ import annotations

import re
from typing import Any, Mapping, MutableMapping, Sequence

from az_session_ops import AZ0_MODES, AZ0_OVERREFUSE_ROWS
from be_session_ops import (
    BE0_ANTI_FP,
    BE0_FOREVER_ROWS,
    BE0_SAFE_NOTE,
    BE0_SHIP_LOCK,
    BE0_UTIL_TRACK,
)
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
    "SHIPUSE_ID",
    "SHIPUSE_THESIS",
    "SHIPUSE_CLAIM",
    "SHIPUSE_SAFE_NOTE",
    "SHIPUSE_ANTI_FP",
    "SHIPUSE_CHARTER",
    "SHIPUSE_PATHS",
    "REQUIRED_MODES",
    "KNOWN_ASK",
    "NEAR_MISS_ASK",
    "PEAK_ASK",
    "BE_RESIDUAL_ASK",
    "OVERREFUSE_ASK",
    "OOD_ASK",
    "attach_shipuse",
    "mode_visible",
    "content_matches_mode",
    "banner_modes_ok",
    "arms_honest_ok",
    "core_modes_ok",
    "demo_card_markdown",
    "operator_card_ok",
    "paper_claim_ok",
    "claim_matches_live",
    "decide_shipuse",
]

SHIPUSE_ID = "H-SHIPUSE"
SHIPUSE_THESIS = (
    "Track A utilization: runnable known-ask HITL demo with modes visible; "
    "operator card (RECIPES + champion-card) synced; paper claim matches "
    "live AF+AQ+AS STRICT refuse stack — no GPT / open-chat unlock"
)
SHIPUSE_CLAIM = BE0_SHIP_LOCK
SHIPUSE_SAFE_NOTE = BE0_SAFE_NOTE
SHIPUSE_ANTI_FP = BE0_ANTI_FP
SHIPUSE_PATHS: tuple[str, ...] = (
    "nano:z:ask --wrap --semwrap",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
    "npm run paper:build",
)
BE_RESIDUAL_ASK = str(BE0_FOREVER_ROWS[0]["question"])
OVERREFUSE_ASK = str(AZ0_OVERREFUSE_ROWS[0]["question"])
OOD_ASK = "Who won the 2022 FIFA World Cup?"

_OPERATOR_NEEDLES: tuple[str, ...] = (
    "nano:z:ask",
    "semwrap",
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
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

SHIPUSE_CHARTER: Mapping[str, object] = {
    "paths": list(SHIPUSE_PATHS),
    "required_modes": list(REQUIRED_MODES),
    "banner": "mode=LOOKUP|PEAK|DECODE|ABSTAIN",
    "smoke": "demo + BE residual + clear + OOD",
    "known_ask_hitl": True,
    "ship_surface_doc": True,
    "paper_archive": True,
    "operator_card": True,
    "claim_matches_live": True,
    "gpt_claim_forbidden": True,
    "modes_visible_required": True,
    "be_residual_abstain": True,
    "overrefuse_labeled_lookup": True,
    "cite_be_locks": ["H-COMPINT", "H-SHIPUSE"],
    "util_track": dict(BE0_UTIL_TRACK),
    "regression_hold": True,
    "rule": (
        "demo smoke + operator card + paper claim sync; "
        "claim = selective retriever + refuse ≤5M; modes always visible"
    ),
    "anti_fp": (
        "SHIPUSE utilization ≠ generative IQ; "
        "claim/doc drift = fail; GPT claim forbidden; "
        "BE residual LOOKUP = false-hit"
    ),
    "stage": "BE2 H-SHIPUSE",
}


def attach_shipuse(payload: MutableMapping[str, Any]) -> dict[str, Any]:
    """Attach product_mode + modeui_line (reuse SHIPAZ law)."""
    return attach_shipaz(payload)


def demo_card_markdown(
    *,
    arms: Sequence[Mapping[str, Any]],
    probes: Sequence[Mapping[str, Any]] | None = None,
) -> str:
    """Human utilization demo card for Track A."""
    body = shipui2_demo_card(arms=arms, apps=probes or (), decode_probe=None)
    return (
        body.replace("SHIPUI2", "SHIPUSE")
        .replace("SHIPAY", "SHIPUSE")
        .replace("SHIPAZ", "SHIPUSE")
    )


def operator_card_ok(*, recipes: str, card: str) -> bool:
    """
    GIVEN RECIPES + champion-card text
    WHEN checking Track A operator card
    THEN True iff both expose ask path + four modes.
    """
    for blob in (recipes, card):
        low = blob
        for needle in _OPERATOR_NEEDLES:
            if needle not in low:
                return False
    return True


def _has_forbidden_unlock(text: str) -> bool:
    """True iff unlock language appears without an explicit negation."""
    low = text.lower()
    scrubbed = re.sub(r"do\s+\*\*not\*\*\s+claim[^\n.]*", "", low)
    scrubbed = re.sub(r"do\s+not\s+claim[^\n.]*", "", scrubbed)
    for bad in _FORBIDDEN_UNLOCK:
        b = bad.lower()
        scrubbed = scrubbed.replace(f"not {b}", "")
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
        return "KILL (SHIPUSE must require regression_hold)"
    modes = set(src.get("required_modes") or [])
    if modes and modes != set(AZ0_MODES):
        return "KILL (SHIPUSE modes ≠ AZ0 mode charter)"
    cited = set(src.get("cite_be_locks") or [])
    if not {"H-COMPINT", "H-SHIPUSE"} <= cited:
        return "KILL (SHIPUSE must cite H-COMPINT·H-SHIPUSE)"
    util = src.get("util_track") or {}
    if not isinstance(util, Mapping):
        return "KILL (SHIPUSE util_track missing)"
    if "SHIPUSE" not in str(util.get("be2_gate", "")):
        return "KILL (util track must gate H-SHIPUSE)"
    return None


def decide_shipuse(
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
    GIVEN Track A demo + operator docs + paper texts after H-COMPINT
    WHEN applying pesquisa §9 BE2 H-SHIPUSE
    THEN PROMOTE iff demo smoke · operator card · paper claim sync ·
         BE residual ABSTAIN · clear LOOKUP · claim matches live.
    """
    if not anti_fp_signed:
        return "KILL (SHIPUSE anti-FP must be signed)"
    src = charter if charter is not None else SHIPUSE_CHARTER
    bad = _charter_ok(src)
    if bad:
        return bad
    if not banner_modes_ok():
        return "KILL (SHIPUSE banner modes incomplete)"
    if not core_modes_ok(arms):
        return "KILL (SHIPUSE core LOOKUP·PEAK·ABSTAIN missing)"
    if not arms_honest_ok(arms):
        return "KILL (SHIPUSE arms unlabeled or content dishonest)"
    dec_mode = str(decode_probe.get("product_mode") or "")
    if dec_mode not in AZ0_MODES or not mode_visible(decode_probe):
        return "KILL (SHIPUSE DECODE probe unlabeled)"
    if not content_matches_mode(decode_probe):
        return "KILL (SHIPUSE DECODE probe content dishonest)"
    if near_miss is not None and not _row_mode(near_miss, "ABSTAIN"):
        return "KILL (SHIPUSE near-miss not ABSTAIN)"
    if bool(src.get("known_ask_hitl", True)) and not _known_ok(probes):
        return "KILL (known-ask HITL not labeled LOOKUP)"
    if bool(src.get("be_residual_abstain", True)) and not _be_residual_ok(probes):
        return "KILL (BE residual not labeled ABSTAIN on ship path)"
    if bool(src.get("overrefuse_labeled_lookup", True)) and not _overrefuse_ok(
        probes
    ):
        return "KILL (over-refuse clear not labeled LOOKUP)"
    if not _ood_ok(probes):
        return "KILL (OOD ask not labeled ABSTAIN)"
    if bool(src.get("operator_card", True)) and not operator_card_ok(
        recipes=recipes, card=card
    ):
        return "KILL (operator card missing ask path / modes)"
    if bool(src.get("paper_archive", True)):
        if not paper_claim_ok(narrative=narrative, paper_tex=paper_tex):
            return "KILL (paper claim out of sync / unlock language)"
        if not paper_build_ok:
            return "KILL (paper:build failed or PDF missing)"
    if bool(src.get("claim_matches_live", True)) and not claim_matches_live(
        claim=SHIPUSE_CLAIM, arms=arms, probes=probes
    ):
        return "KILL (claim/live drift on modes or ship lock)"
    if bool(src.get("gpt_claim_forbidden", True)):
        blob = f"{recipes}\n{card}\n{narrative}"
        if _has_forbidden_unlock(blob):
            return "KILL (GPT / open-chat claim forbidden)"
    return (
        f"PROMOTE ({SHIPUSE_ID}: demo smoke · operator card · "
        "paper claim sync · BE residual ABSTAIN · Track A done)"
    )
