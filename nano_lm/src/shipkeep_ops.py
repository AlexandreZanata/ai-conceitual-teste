"""Wave AW2 H-SHIPKEEP: hold ship/demo modes + DECODE content under AW keep."""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Sequence

from aw_session_ops import (
    AW0_ANTI_FP,
    AW0_MODES,
    AW0_SAFE_NOTE,
    AW0_SHIP_LOCK,
)
from prodhard_ops import NEAR_MISS_ASK, PEAK_ASK
from shipapp_ops import APP_SMOKE_PACK, APP_SURFACES, REQUIRED_MODES, SHIPAPP_PATHS
from shipui2_ops import (
    arms_honest_ok,
    banner_modes_ok,
    content_matches_mode,
    core_modes_ok,
    decide_shipui2,
    demo_card_markdown as shipui2_demo_card,
)
from shipui2_ops import attach_shipui2
from shipreal_ops import apps_content_ok

__all__ = [
    "SHIPKEEP_ID",
    "SHIPKEEP_THESIS",
    "SHIPKEEP_CLAIM",
    "SHIPKEEP_SAFE_NOTE",
    "SHIPKEEP_ANTI_FP",
    "SHIPKEEP_PATHS",
    "SHIPKEEP_CHARTER",
    "REQUIRED_MODES",
    "APP_SURFACES",
    "APP_SMOKE_PACK",
    "NEAR_MISS_ASK",
    "PEAK_ASK",
    "attach_shipkeep",
    "mode_visible",
    "content_matches_mode",
    "banner_modes_ok",
    "arms_honest_ok",
    "apps_content_ok",
    "core_modes_ok",
    "demo_card_markdown",
    "decide_shipkeep",
]

SHIPKEEP_ID = "H-SHIPKEEP"
SHIPKEEP_THESIS = (
    "Hold human ship/demo + ask + apps always show "
    "mode=LOOKUP|PEAK|DECODE|ABSTAIN after PRODKEEP; content matches mode "
    "(DECODE usable or ABSTAIN on junk); no unlabeled"
)
SHIPKEEP_CLAIM = AW0_SHIP_LOCK
SHIPKEEP_SAFE_NOTE = AW0_SAFE_NOTE
SHIPKEEP_ANTI_FP = AW0_ANTI_FP
SHIPKEEP_PATHS: tuple[str, ...] = SHIPAPP_PATHS
SHIPKEEP_CHARTER: Mapping[str, object] = {
    "paths": list(SHIPKEEP_PATHS),
    "required_modes": list(REQUIRED_MODES),
    "banner": "mode=LOOKUP|PEAK|DECODE|ABSTAIN",
    "smoke": "4/4",
    "content_bars": True,
    "decode_usable_or_abstain": True,
    "regression_hold": True,
    "cite_av_locks": ["H-PRODSHIP", "H-SHIPUI2"],
    "rule": (
        "every human-facing answer shows product_mode and content "
        "matches the mode claim; DECODE gibberish → ABSTAIN; no unlabeled; "
        "hold after AW1 H-PRODKEEP"
    ),
    "anti_fp": (
        "SHIPKEEP mode+content honesty ≠ generative IQ; "
        "DECODE telemetry-only content_ok forbidden; "
        "PEAK stays extractive label; NANOGEN7 gate = AW3 only"
    ),
    "stage": "AW2 H-SHIPKEEP",
}


def attach_shipkeep(payload: MutableMapping[str, Any]) -> dict[str, Any]:
    """Attach mode banner; refuse junk DECODE to ABSTAIN (SHIPUI2 law)."""
    return attach_shipui2(payload)


def mode_visible(row: Mapping[str, Any]) -> bool:
    from shipui_ops import mode_visible as _mv

    return _mv(row)


def demo_card_markdown(
    *,
    arms: Sequence[Mapping[str, Any]],
    apps: Sequence[Mapping[str, Any]],
    decode_probe: Mapping[str, Any] | None = None,
) -> str:
    """Human demo card renamed for SHIPKEEP."""
    body = shipui2_demo_card(arms=arms, apps=apps, decode_probe=decode_probe)
    return body.replace("SHIPUI2", "SHIPKEEP")


def decide_shipkeep(
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
    GIVEN ship/demo arms + apps + DECODE probe + near-miss after PRODKEEP
    WHEN applying pesquisa §2 AW2 H-SHIPKEEP
    THEN PROMOTE iff banner 4/4 · labeled · content honest ·
         DECODE usable/ABSTAIN · near-miss ABSTAIN · regression_hold; else KILL.
    """
    src = charter if charter is not None else SHIPKEEP_CHARTER
    if not bool(src.get("regression_hold", True)):
        return "KILL (SHIPKEEP must require regression_hold)"
    modes = set(src.get("required_modes") or [])
    if modes and modes != set(AW0_MODES):
        return "KILL (SHIPKEEP modes ≠ AW0 mode charter)"
    out = decide_shipui2(
        arms=arms,
        default_asks=default_asks,
        apps=apps,
        decode_probe=decode_probe,
        near_miss=near_miss,
        charter=src,
        anti_fp_signed=anti_fp_signed,
    )
    if out.startswith("PROMOTE"):
        return (
            f"PROMOTE ({SHIPKEEP_ID}: modes+content honest · "
            "DECODE law · keep after PRODKEEP)"
        )
    if "SHIPUI2" in out:
        return out.replace("SHIPUI2", "SHIPKEEP")
    return out
