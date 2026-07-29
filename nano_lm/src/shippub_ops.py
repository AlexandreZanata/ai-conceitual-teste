"""Wave BG2 H-SHIPPUB: Track A++ utilization — operator + paper/arXiv sync."""

from __future__ import annotations

import re
from typing import Any, Mapping, MutableMapping, Sequence

from az_session_ops import AZ0_MODES, AZ0_OVERREFUSE_ROWS
from be_session_ops import BE0_FOREVER_ROWS, BE0_SAFE_NOTE
from bf_session_ops import BF0_FOREVER_ROWS
from bg_session_ops import (
    BG0_ANTI_FP,
    BG0_FOREVER_ROWS,
    BG0_SHIP_LOCK,
    BG0_UTIL_TRACK,
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
    "SHIPPUB_ID",
    "SHIPPUB_THESIS",
    "SHIPPUB_CLAIM",
    "SHIPPUB_SAFE_NOTE",
    "SHIPPUB_ANTI_FP",
    "SHIPPUB_CHARTER",
    "SHIPPUB_PATHS",
    "REQUIRED_MODES",
    "KNOWN_ASK",
    "NEAR_MISS_ASK",
    "PEAK_ASK",
    "BE_RESIDUAL_ASK",
    "BF_RESIDUAL_ASK",
    "BG_UNARY_ASK",
    "BG_TRANSFORM_ASK",
    "APPEND_ASK",
    "OVERREFUSE_ASK",
    "OOD_ASK",
    "attach_shippub",
    "mode_visible",
    "content_matches_mode",
    "banner_modes_ok",
    "arms_honest_ok",
    "core_modes_ok",
    "demo_card_markdown",
    "operator_card_ok",
    "paper_claim_ok",
    "paper_arxiv_ok",
    "claim_matches_live",
    "decide_shippub",
]

SHIPPUB_ID = "H-SHIPPUB"
SHIPPUB_THESIS = (
    "Track A++ utilization: hold H-SHIPUSE2 demo·operator·paper; "
    "deepen paper/arXiv sync; live BG residual (abs≠add · upper≠f-string) "
    "ABSTAIN + append LOOKUP smoke under H-UNARYINT — no GPT unlock"
)
SHIPPUB_CLAIM = BG0_SHIP_LOCK
SHIPPUB_SAFE_NOTE = BE0_SAFE_NOTE
SHIPPUB_ANTI_FP = BG0_ANTI_FP
SHIPPUB_PATHS: tuple[str, ...] = (
    "nano:z:ask --wrap --semwrap",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
    "npm run paper:build",
    "docs/arxiv.md",
)
BE_RESIDUAL_ASK = str(BE0_FOREVER_ROWS[0]["question"])
BF_RESIDUAL_ASK = str(BF0_FOREVER_ROWS[0]["question"])
BG_UNARY_ASK = str(BG0_FOREVER_ROWS[0]["question"])
BG_TRANSFORM_ASK = str(BG0_FOREVER_ROWS[2]["question"])
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
    "H-UNARYINT",
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

SHIPPUB_CHARTER: Mapping[str, object] = {
    "paths": list(SHIPPUB_PATHS),
    "required_modes": list(REQUIRED_MODES),
    "banner": "mode=LOOKUP|PEAK|DECODE|ABSTAIN",
    "smoke": "demo + BG/BF/BE residual + append + clear + OOD",
    "known_ask_hitl": True,
    "ship_surface_doc": True,
    "paper_archive": True,
    "paper_arxiv_sync": True,
    "operator_card": True,
    "claim_matches_live": True,
    "gpt_claim_forbidden": True,
    "modes_visible_required": True,
    "be_residual_abstain": True,
    "bf_residual_abstain": True,
    "bg_unary_abstain": True,
    "bg_transform_abstain": True,
    "append_labeled_lookup": True,
    "h_shipuse2_hold": True,
    "overrefuse_labeled_lookup": True,
    "cite_bg_locks": [
        "H-UNARYINT",
        "H-SHIPUSE2",
        "H-PREDINT",
        "H-COMPINT",
    ],
    "util_track": dict(BG0_UTIL_TRACK),
    "regression_hold": True,
    "rule": (
        "Track A++ deepen: hold H-SHIPUSE2; BG residual ABSTAIN; "
        "append LOOKUP; operator + paper/arXiv sync; modes always visible"
    ),
    "anti_fp": (
        "SHIPPUB utilization ≠ generative IQ; "
        "claim/doc drift = fail; GPT claim forbidden; "
        "BG residual LOOKUP = false-hit; H-SHIPUSE2 hold"
    ),
    "stage": "BG2 H-SHIPPUB",
}


def attach_shippub(payload: MutableMapping[str, Any]) -> dict[str, Any]:
    """Attach product_mode + modeui_line (reuse SHIPAZ law)."""
    return attach_shipaz(payload)


def demo_card_markdown(
    *,
    arms: Sequence[Mapping[str, Any]],
    probes: Sequence[Mapping[str, Any]] | None = None,
) -> str:
    """Human utilization demo card for Track A++."""
    body = shipui2_demo_card(arms=arms, apps=probes or (), decode_probe=None)
    return (
        body.replace("SHIPUI2", "SHIPPUB")
        .replace("SHIPAY", "SHIPPUB")
        .replace("SHIPAZ", "SHIPPUB")
        .replace("SHIPUSE2 —", "SHIPPUB —")
        .replace("SHIPUSE —", "SHIPPUB —")
    )


def operator_card_ok(*, recipes: str, card: str) -> bool:
    """
    GIVEN RECIPES + champion-card text
    WHEN checking Track A++ operator card
    THEN True iff both expose ask path + four modes + H-UNARYINT.
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


def paper_arxiv_ok(*, narrative: str, arxiv_md: str) -> bool:
    """
    GIVEN narrative + docs/arxiv.md
    WHEN checking Track A++ paper/arXiv sync
    THEN True iff arXiv path + selective-retriever thesis are present.
    """
    joined = f"{narrative}\n{arxiv_md}".lower()
    if "arxiv" not in joined:
        return False
    return "selective" in joined or "retriever" in joined


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


def _bg_unary_ok(probes: Sequence[Mapping[str, Any]]) -> bool:
    row = _find_q(probes, exact=BG_UNARY_ASK, needle="absolute value")
    return _row_mode(row, "ABSTAIN")


def _bg_transform_ok(probes: Sequence[Mapping[str, Any]]) -> bool:
    row = _find_q(probes, exact=BG_TRANSFORM_ASK, needle="uppercase")
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
        return "KILL (SHIPPUB must require regression_hold)"
    modes = set(src.get("required_modes") or [])
    if modes and modes != set(AZ0_MODES):
        return "KILL (SHIPPUB modes ≠ AZ0 mode charter)"
    cited = set(src.get("cite_bg_locks") or [])
    need = {"H-UNARYINT", "H-SHIPUSE2", "H-PREDINT", "H-COMPINT"}
    if not need <= cited:
        return (
            "KILL (SHIPPUB must cite "
            "H-UNARYINT·H-SHIPUSE2·H-PREDINT·H-COMPINT)"
        )
    util = src.get("util_track") or {}
    if not isinstance(util, Mapping):
        return "KILL (SHIPPUB util_track missing)"
    if "SHIPPUB" not in str(util.get("bg2_gate", "")):
        return "KILL (util track must gate H-SHIPPUB)"
    if not bool(src.get("h_shipuse2_hold", True)):
        return "KILL (SHIPPUB must hold H-SHIPUSE2)"
    if not bool(src.get("paper_arxiv_sync", True)):
        return "KILL (SHIPPUB must require paper_arxiv_sync)"
    return None


def decide_shippub(
    *,
    arms: Sequence[Mapping[str, Any]],
    probes: Sequence[Mapping[str, Any]],
    decode_probe: Mapping[str, Any],
    near_miss: Mapping[str, Any] | None,
    recipes: str,
    card: str,
    narrative: str,
    paper_tex: str,
    arxiv_md: str,
    paper_build_ok: bool,
    charter: Mapping[str, object] | None = None,
    anti_fp_signed: bool = True,
) -> str:
    """
    GIVEN Track A++ after H-UNARYINT + H-SHIPUSE2 hold
    WHEN applying pesquisa §9 BG2 H-SHIPPUB
    THEN PROMOTE iff demo smoke · operator card · paper/arXiv sync ·
         BG/BF/BE residual ABSTAIN · append+clear LOOKUP · claim matches live.
    """
    if not anti_fp_signed:
        return "KILL (SHIPPUB anti-FP must be signed)"
    src = charter if charter is not None else SHIPPUB_CHARTER
    bad = _charter_ok(src)
    if bad:
        return bad
    if not banner_modes_ok():
        return "KILL (SHIPPUB banner modes incomplete)"
    if not core_modes_ok(arms):
        return "KILL (SHIPPUB core LOOKUP·PEAK·ABSTAIN missing)"
    if not arms_honest_ok(arms):
        return "KILL (SHIPPUB arms unlabeled or content dishonest)"
    dec_mode = str(decode_probe.get("product_mode") or "")
    if dec_mode not in AZ0_MODES or not mode_visible(decode_probe):
        return "KILL (SHIPPUB DECODE probe unlabeled)"
    if not content_matches_mode(decode_probe):
        return "KILL (SHIPPUB DECODE probe content dishonest)"
    if near_miss is not None and not _row_mode(near_miss, "ABSTAIN"):
        return "KILL (SHIPPUB near-miss not ABSTAIN)"
    if bool(src.get("known_ask_hitl", True)) and not _known_ok(probes):
        return "KILL (known-ask HITL not labeled LOOKUP)"
    if bool(src.get("be_residual_abstain", True)) and not _be_residual_ok(
        probes
    ):
        return "KILL (BE residual not labeled ABSTAIN on ship path)"
    if bool(src.get("bf_residual_abstain", True)) and not _bf_residual_ok(
        probes
    ):
        return "KILL (BF residual not labeled ABSTAIN on ship path)"
    if bool(src.get("bg_unary_abstain", True)) and not _bg_unary_ok(probes):
        return "KILL (BG unary residual not labeled ABSTAIN on ship path)"
    if bool(src.get("bg_transform_abstain", True)) and not _bg_transform_ok(
        probes
    ):
        return "KILL (BG transform residual not labeled ABSTAIN on ship path)"
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
        return "KILL (operator card missing ask path / modes / H-UNARYINT)"
    if bool(src.get("paper_archive", True)):
        if not paper_claim_ok(narrative=narrative, paper_tex=paper_tex):
            return "KILL (paper claim out of sync / unlock language)"
        if not paper_build_ok:
            return "KILL (paper:build failed or PDF missing)"
    if bool(src.get("paper_arxiv_sync", True)) and not paper_arxiv_ok(
        narrative=narrative, arxiv_md=arxiv_md
    ):
        return "KILL (paper/arXiv sync missing selective-retriever path)"
    if bool(src.get("claim_matches_live", True)) and not claim_matches_live(
        claim=SHIPPUB_CLAIM, arms=arms, probes=probes
    ):
        return "KILL (claim/live drift on modes or ship lock)"
    if bool(src.get("gpt_claim_forbidden", True)):
        blob = f"{recipes}\n{card}\n{narrative}"
        if _has_forbidden_unlock(blob):
            return "KILL (GPT / open-chat claim forbidden)"
    return (
        f"PROMOTE ({SHIPPUB_ID}: Track A++ deepen · H-SHIPUSE2 hold · "
        "BG residual ABSTAIN · operator · paper/arXiv sync)"
    )
