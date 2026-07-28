"""Wave AZ2 H-SHIPAZ: ship/demo modes + content after H-PRODGEN."""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Sequence

from ax_session_ops import AX0_HARD_NATURAL_ROWS
from ay_session_ops import AY0_INTENT_FP_ROWS
from az_session_ops import (
    AZ0_ANTI_FP,
    AZ0_HELDOUT_FP_ROWS,
    AZ0_MODES,
    AZ0_OVERREFUSE_ROWS,
    AZ0_SAFE_NOTE,
    AZ0_SHIP_LOCK,
)
from prodhard_ops import NEAR_MISS_ASK, PEAK_ASK
from shipapp_ops import APP_SMOKE_PACK, APP_SURFACES, REQUIRED_MODES, SHIPAPP_PATHS
from shipay_ops import attach_shipay
from shipui2_ops import (
    arms_honest_ok,
    banner_modes_ok,
    content_matches_mode,
    core_modes_ok,
    decide_shipui2,
)
from shipui2_ops import demo_card_markdown as shipui2_demo_card
from shipreal_ops import apps_content_ok
from shipux_ops import mode_visible

__all__ = [
    "SHIPAZ_ID",
    "SHIPAZ_THESIS",
    "SHIPAZ_CLAIM",
    "SHIPAZ_SAFE_NOTE",
    "SHIPAZ_ANTI_FP",
    "SHIPAZ_PATHS",
    "SHIPAZ_CHARTER",
    "HARD_NATURAL_ASK",
    "NAMED_INTENT_ASK",
    "HELDOUT_FP_ASK",
    "OVERREFUSE_ASK",
    "REQUIRED_MODES",
    "APP_SURFACES",
    "APP_SMOKE_PACK",
    "NEAR_MISS_ASK",
    "PEAK_ASK",
    "attach_shipaz",
    "mode_visible",
    "content_matches_mode",
    "banner_modes_ok",
    "arms_honest_ok",
    "apps_content_ok",
    "core_modes_ok",
    "demo_card_markdown",
    "decide_shipaz",
]

SHIPAZ_ID = "H-SHIPAZ"
SHIPAZ_THESIS = (
    "Hold human ship/demo + ask + apps always show "
    "mode=LOOKUP|PEAK|DECODE|ABSTAIN after PRODGEN; content matches mode "
    "(DECODE usable or ABSTAIN on junk); hard-natural LOOKUP; "
    "held-out FP ABSTAIN; over-refuse clear LOOKUP; named intent ABSTAIN; "
    "no unlabeled"
)
SHIPAZ_CLAIM = AZ0_SHIP_LOCK
SHIPAZ_SAFE_NOTE = AZ0_SAFE_NOTE
SHIPAZ_ANTI_FP = AZ0_ANTI_FP
SHIPAZ_PATHS: tuple[str, ...] = SHIPAPP_PATHS
HARD_NATURAL_ASK = str(AX0_HARD_NATURAL_ROWS[0]["question"])
NAMED_INTENT_ASK = str(AY0_INTENT_FP_ROWS[0]["question"])
HELDOUT_FP_ASK = str(AZ0_HELDOUT_FP_ROWS[0]["question"])
OVERREFUSE_ASK = str(AZ0_OVERREFUSE_ROWS[0]["question"])
SHIPAZ_CHARTER: Mapping[str, object] = {
    "paths": list(SHIPAZ_PATHS),
    "required_modes": list(REQUIRED_MODES),
    "banner": "mode=LOOKUP|PEAK|DECODE|ABSTAIN",
    "smoke": "4/4",
    "content_bars": True,
    "decode_usable_or_abstain": True,
    "hard_natural_labeled": True,
    "named_intent_labeled_abstain": True,
    "heldout_fp_labeled_abstain": True,
    "overrefuse_labeled_lookup": True,
    "regression_hold": True,
    "cite_az_locks": ["H-PRODGEN", "H-PRODINT", "H-SHIPAY"],
    "rule": (
        "every human-facing answer shows product_mode and content "
        "matches the mode claim; DECODE gibberish → ABSTAIN; no unlabeled; "
        "hard-natural stays LOOKUP; held-out FP stays ABSTAIN; "
        "over-refuse clear stays LOOKUP; named intent stays ABSTAIN"
    ),
    "anti_fp": (
        "SHIPAZ mode+content honesty ≠ generative IQ; "
        "held-out mismatch LOOKUP = false-hit; "
        "exact-gold ABSTAIN = product miss; "
        "DECODE telemetry-only content_ok forbidden; "
        "PEAK stays extractive label; NANOGEN10 gate = AZ3 only (defer)"
    ),
    "stage": "AZ2 H-SHIPAZ",
}


def attach_shipaz(payload: MutableMapping[str, Any]) -> dict[str, Any]:
    """Attach mode banner; refuse junk DECODE to ABSTAIN (SHIPUI2 law)."""
    return attach_shipay(payload)


def demo_card_markdown(
    *,
    arms: Sequence[Mapping[str, Any]],
    apps: Sequence[Mapping[str, Any]],
    decode_probe: Mapping[str, Any] | None = None,
) -> str:
    """Human demo card renamed for SHIPAZ."""
    body = shipui2_demo_card(arms=arms, apps=apps, decode_probe=decode_probe)
    return body.replace("SHIPUI2", "SHIPAZ").replace("SHIPAY", "SHIPAZ")


def _row_matches(
    row: Mapping[str, Any],
    *,
    expect_mode: str,
    need_clear: bool = False,
) -> bool:
    if str(row.get("product_mode") or "") != expect_mode:
        return False
    if not mode_visible(row):
        return False
    if not content_matches_mode(row):
        return False
    if need_clear and "clear" not in str(row.get("completion", "")).lower():
        return False
    return True


def _find_ask(
    default_asks: Sequence[Mapping[str, Any]],
    *,
    exact: str,
    needle: str,
) -> Mapping[str, Any] | None:
    for row in default_asks:
        q = str(row.get("question") or "")
        if q == exact or needle.lower() in q.lower():
            return row
    return None


def _hard_natural_labeled(default_asks: Sequence[Mapping[str, Any]]) -> bool:
    row = _find_ask(
        default_asks, exact=HARD_NATURAL_ASK, needle="Python helper that adds"
    )
    return bool(row) and _row_matches(row, expect_mode="LOOKUP")


def _named_intent_labeled(default_asks: Sequence[Mapping[str, Any]]) -> bool:
    row = _find_ask(default_asks, exact=NAMED_INTENT_ASK, needle="named mul")
    return bool(row) and _row_matches(row, expect_mode="ABSTAIN")


def _heldout_fp_labeled(default_asks: Sequence[Mapping[str, Any]]) -> bool:
    row = _find_ask(default_asks, exact=HELDOUT_FP_ASK, needle="named div")
    return bool(row) and _row_matches(row, expect_mode="ABSTAIN")


def _overrefuse_labeled(default_asks: Sequence[Mapping[str, Any]]) -> bool:
    row = _find_ask(
        default_asks, exact=OVERREFUSE_ASK, needle="Remove all items"
    )
    return bool(row) and _row_matches(row, expect_mode="LOOKUP", need_clear=True)


def decide_shipaz(
    *,
    arms: Sequence[Mapping[str, Any]],
    default_asks: Sequence[Mapping[str, Any]],
    apps: Sequence[Mapping[str, Any]],
    decode_probe: Mapping[str, Any],
    near_miss: Mapping[str, Any] | None = None,
    charter: Mapping[str, object] | None = None,
    anti_fp_signed: bool = True,
) -> str:
    """
    GIVEN ship/demo arms + apps + DECODE + AZ product asks after PRODGEN
    WHEN applying pesquisa §5 AZ2 H-SHIPAZ
    THEN PROMOTE iff banner 4/4 · labeled · content honest ·
         DECODE usable/ABSTAIN · hard-natural LOOKUP · held-out ABSTAIN ·
         over-refuse LOOKUP · named intent ABSTAIN · near-miss ABSTAIN.
    """
    src = charter if charter is not None else SHIPAZ_CHARTER
    if not bool(src.get("regression_hold", True)):
        return "KILL (SHIPAZ must require regression_hold)"
    modes = set(src.get("required_modes") or [])
    if modes and modes != set(AZ0_MODES):
        return "KILL (SHIPAZ modes ≠ AZ0 mode charter)"
    cited = set(src.get("cite_az_locks") or [])
    if not {"H-PRODGEN", "H-PRODINT", "H-SHIPAY"} <= cited:
        return "KILL (SHIPAZ must cite PRODGEN·PRODINT·SHIPAY)"
    out = decide_shipui2(
        arms=arms,
        default_asks=default_asks,
        apps=apps,
        decode_probe=decode_probe,
        near_miss=near_miss,
        charter=src,
        anti_fp_signed=anti_fp_signed,
    )
    if not out.startswith("PROMOTE"):
        for old, new in (("SHIPUI2", "SHIPAZ"), ("SHIPAY", "SHIPAZ")):
            if old in out:
                return out.replace(old, new)
        return out
    checks = (
        (
            bool(src.get("hard_natural_labeled", True)),
            _hard_natural_labeled,
            "KILL (hard-natural ask not labeled LOOKUP on ship path)",
        ),
        (
            bool(src.get("named_intent_labeled_abstain", True)),
            _named_intent_labeled,
            "KILL (named intent ask not labeled ABSTAIN on ship path)",
        ),
        (
            bool(src.get("heldout_fp_labeled_abstain", True)),
            _heldout_fp_labeled,
            "KILL (held-out FP ask not labeled ABSTAIN on ship path)",
        ),
        (
            bool(src.get("overrefuse_labeled_lookup", True)),
            _overrefuse_labeled,
            "KILL (over-refuse clear ask not labeled LOOKUP on ship path)",
        ),
    )
    for enabled, fn, msg in checks:
        if enabled and not fn(default_asks):
            return msg
    return (
        f"PROMOTE ({SHIPAZ_ID}: modes+content honest · DECODE law · "
        "held-out ABSTAIN · over-refuse LOOKUP · named hold after PRODGEN)"
    )
