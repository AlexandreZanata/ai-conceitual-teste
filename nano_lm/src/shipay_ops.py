"""Wave AY2 H-SHIPAY: ship/demo modes + content after H-PRODINT."""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Sequence

from ay_session_ops import (
    AY0_ANTI_FP,
    AY0_INTENT_FP_ROWS,
    AY0_MODES,
    AY0_SAFE_NOTE,
    AY0_SHIP_LOCK,
)
from ax_session_ops import AX0_HARD_NATURAL_ROWS
from prodhard_ops import NEAR_MISS_ASK, PEAK_ASK
from shipapp_ops import APP_SMOKE_PACK, APP_SURFACES, REQUIRED_MODES, SHIPAPP_PATHS
from shipui2_ops import (
    arms_honest_ok,
    banner_modes_ok,
    content_matches_mode,
    core_modes_ok,
    decide_shipui2,
)
from shipui2_ops import attach_shipui2
from shipui2_ops import demo_card_markdown as shipui2_demo_card
from shipreal_ops import apps_content_ok
from shipux_ops import mode_visible

__all__ = [
    "SHIPAY_ID",
    "SHIPAY_THESIS",
    "SHIPAY_CLAIM",
    "SHIPAY_SAFE_NOTE",
    "SHIPAY_ANTI_FP",
    "SHIPAY_PATHS",
    "SHIPAY_CHARTER",
    "HARD_NATURAL_ASK",
    "INTENT_FP_ASK",
    "REQUIRED_MODES",
    "APP_SURFACES",
    "APP_SMOKE_PACK",
    "NEAR_MISS_ASK",
    "PEAK_ASK",
    "attach_shipay",
    "mode_visible",
    "content_matches_mode",
    "banner_modes_ok",
    "arms_honest_ok",
    "apps_content_ok",
    "core_modes_ok",
    "demo_card_markdown",
    "decide_shipay",
]

SHIPAY_ID = "H-SHIPAY"
SHIPAY_THESIS = (
    "Hold human ship/demo + ask + apps always show "
    "mode=LOOKUP|PEAK|DECODE|ABSTAIN after PRODINT; content matches mode "
    "(DECODE usable or ABSTAIN on junk); hard-natural LOOKUP; "
    "intent-FP ABSTAIN labeled; no unlabeled"
)
SHIPAY_CLAIM = AY0_SHIP_LOCK
SHIPAY_SAFE_NOTE = AY0_SAFE_NOTE
SHIPAY_ANTI_FP = AY0_ANTI_FP
SHIPAY_PATHS: tuple[str, ...] = SHIPAPP_PATHS
HARD_NATURAL_ASK = str(AX0_HARD_NATURAL_ROWS[0]["question"])
INTENT_FP_ASK = str(AY0_INTENT_FP_ROWS[0]["question"])
SHIPAY_CHARTER: Mapping[str, object] = {
    "paths": list(SHIPAY_PATHS),
    "required_modes": list(REQUIRED_MODES),
    "banner": "mode=LOOKUP|PEAK|DECODE|ABSTAIN",
    "smoke": "4/4",
    "content_bars": True,
    "decode_usable_or_abstain": True,
    "hard_natural_labeled": True,
    "intent_fp_labeled_abstain": True,
    "regression_hold": True,
    "cite_ay_locks": ["H-PRODINT", "H-PRODNAT", "H-SHIPUX"],
    "rule": (
        "every human-facing answer shows product_mode and content "
        "matches the mode claim; DECODE gibberish → ABSTAIN; no unlabeled; "
        "hard-natural stays LOOKUP; intent-FP stays ABSTAIN after PRODINT"
    ),
    "anti_fp": (
        "SHIPAY mode+content honesty ≠ generative IQ; "
        "intent-mismatch LOOKUP = false-hit; "
        "DECODE telemetry-only content_ok forbidden; "
        "PEAK stays extractive label; NANOGEN9 gate = AY3 only (defer)"
    ),
    "stage": "AY2 H-SHIPAY",
}


def attach_shipay(payload: MutableMapping[str, Any]) -> dict[str, Any]:
    """Attach mode banner; refuse junk DECODE to ABSTAIN (SHIPUI2 law)."""
    return attach_shipui2(payload)


def demo_card_markdown(
    *,
    arms: Sequence[Mapping[str, Any]],
    apps: Sequence[Mapping[str, Any]],
    decode_probe: Mapping[str, Any] | None = None,
) -> str:
    """Human demo card renamed for SHIPAY."""
    body = shipui2_demo_card(arms=arms, apps=apps, decode_probe=decode_probe)
    return body.replace("SHIPUI2", "SHIPAY")


def _hard_natural_labeled(default_asks: Sequence[Mapping[str, Any]]) -> bool:
    for row in default_asks:
        q = str(row.get("question") or "")
        if q != HARD_NATURAL_ASK and "Python helper that adds" not in q:
            continue
        if str(row.get("product_mode") or "") != "LOOKUP":
            return False
        if not mode_visible(row):
            return False
        if not content_matches_mode(row):
            return False
        return True
    return False


def _intent_fp_labeled(default_asks: Sequence[Mapping[str, Any]]) -> bool:
    for row in default_asks:
        q = str(row.get("question") or "")
        if q != INTENT_FP_ASK and "named mul" not in q.lower():
            continue
        if str(row.get("product_mode") or "") != "ABSTAIN":
            return False
        if not mode_visible(row):
            return False
        if not content_matches_mode(row):
            return False
        return True
    return False


def decide_shipay(
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
    GIVEN ship/demo arms + apps + DECODE + hard-natural + intent-FP after PRODINT
    WHEN applying pesquisa §5 AY2 H-SHIPAY
    THEN PROMOTE iff banner 4/4 · labeled · content honest ·
         DECODE usable/ABSTAIN · hard-natural LOOKUP · intent-FP ABSTAIN ·
         near-miss ABSTAIN.
    """
    src = charter if charter is not None else SHIPAY_CHARTER
    if not bool(src.get("regression_hold", True)):
        return "KILL (SHIPAY must require regression_hold)"
    modes = set(src.get("required_modes") or [])
    if modes and modes != set(AY0_MODES):
        return "KILL (SHIPAY modes ≠ AY0 mode charter)"
    cited = set(src.get("cite_ay_locks") or [])
    if not {"H-PRODINT", "H-PRODNAT", "H-SHIPUX"} <= cited:
        return "KILL (SHIPAY must cite PRODINT·PRODNAT·SHIPUX)"
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
        if "SHIPUI2" in out:
            return out.replace("SHIPUI2", "SHIPAY")
        return out
    if bool(src.get("hard_natural_labeled", True)):
        if not _hard_natural_labeled(default_asks):
            return "KILL (hard-natural ask not labeled LOOKUP on ship path)"
    if bool(src.get("intent_fp_labeled_abstain", True)):
        if not _intent_fp_labeled(default_asks):
            return "KILL (intent-FP ask not labeled ABSTAIN on ship path)"
    return (
        f"PROMOTE ({SHIPAY_ID}: modes+content honest · "
        "DECODE law · hard-natural LOOKUP · intent-FP ABSTAIN after PRODINT)"
    )
