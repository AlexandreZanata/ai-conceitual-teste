"""Wave AX2 H-SHIPUX: ship/demo modes + content after H-PRODNAT."""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Sequence

from ax_session_ops import (
    AX0_ANTI_FP,
    AX0_HARD_NATURAL_ROWS,
    AX0_MODES,
    AX0_SAFE_NOTE,
    AX0_SHIP_LOCK,
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
    "SHIPUX_ID",
    "SHIPUX_THESIS",
    "SHIPUX_CLAIM",
    "SHIPUX_SAFE_NOTE",
    "SHIPUX_ANTI_FP",
    "SHIPUX_PATHS",
    "SHIPUX_CHARTER",
    "HARD_NATURAL_ASK",
    "REQUIRED_MODES",
    "APP_SURFACES",
    "APP_SMOKE_PACK",
    "NEAR_MISS_ASK",
    "PEAK_ASK",
    "attach_shipux",
    "mode_visible",
    "content_matches_mode",
    "banner_modes_ok",
    "arms_honest_ok",
    "apps_content_ok",
    "core_modes_ok",
    "demo_card_markdown",
    "decide_shipux",
]

SHIPUX_ID = "H-SHIPUX"
SHIPUX_THESIS = (
    "Hold human ship/demo + ask + apps always show "
    "mode=LOOKUP|PEAK|DECODE|ABSTAIN after PRODNAT; content matches mode "
    "(DECODE usable or ABSTAIN on junk); hard-natural ask labeled; no unlabeled"
)
SHIPUX_CLAIM = AX0_SHIP_LOCK
SHIPUX_SAFE_NOTE = AX0_SAFE_NOTE
SHIPUX_ANTI_FP = AX0_ANTI_FP
SHIPUX_PATHS: tuple[str, ...] = SHIPAPP_PATHS
HARD_NATURAL_ASK = str(AX0_HARD_NATURAL_ROWS[0]["question"])
SHIPUX_CHARTER: Mapping[str, object] = {
    "paths": list(SHIPUX_PATHS),
    "required_modes": list(REQUIRED_MODES),
    "banner": "mode=LOOKUP|PEAK|DECODE|ABSTAIN",
    "smoke": "4/4",
    "content_bars": True,
    "decode_usable_or_abstain": True,
    "hard_natural_labeled": True,
    "regression_hold": True,
    "cite_ax_locks": ["H-PRODNAT", "H-PRODKEEP", "H-SHIPKEEP"],
    "rule": (
        "every human-facing answer shows product_mode and content "
        "matches the mode claim; DECODE gibberish → ABSTAIN; no unlabeled; "
        "hard-natural live miss stays labeled LOOKUP after PRODNAT"
    ),
    "anti_fp": (
        "SHIPUX mode+content honesty ≠ generative IQ; "
        "DECODE telemetry-only content_ok forbidden; "
        "PEAK stays extractive label; NANOGEN8 gate = AX3 only (defer)"
    ),
    "stage": "AX2 H-SHIPUX",
}


def attach_shipux(payload: MutableMapping[str, Any]) -> dict[str, Any]:
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
    """Human demo card renamed for SHIPUX."""
    body = shipui2_demo_card(arms=arms, apps=apps, decode_probe=decode_probe)
    return body.replace("SHIPUI2", "SHIPUX")


def _hard_natural_labeled(default_asks: Sequence[Mapping[str, Any]]) -> bool:
    for row in default_asks:
        q = str(row.get("question") or "")
        if q != HARD_NATURAL_ASK and "Python helper that adds" not in q:
            continue
        mode = str(row.get("product_mode") or "")
        if mode != "LOOKUP":
            return False
        if not mode_visible(row):
            return False
        if not content_matches_mode(row):
            return False
        return True
    return False


def decide_shipux(
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
    GIVEN ship/demo arms + apps + DECODE + hard-natural after PRODNAT
    WHEN applying pesquisa §5 AX2 H-SHIPUX
    THEN PROMOTE iff banner 4/4 · labeled · content honest ·
         DECODE usable/ABSTAIN · hard-natural LOOKUP · near-miss ABSTAIN.
    """
    src = charter if charter is not None else SHIPUX_CHARTER
    if not bool(src.get("regression_hold", True)):
        return "KILL (SHIPUX must require regression_hold)"
    modes = set(src.get("required_modes") or [])
    if modes and modes != set(AX0_MODES):
        return "KILL (SHIPUX modes ≠ AX0 mode charter)"
    cited = set(src.get("cite_ax_locks") or [])
    if not {"H-PRODNAT", "H-PRODKEEP", "H-SHIPKEEP"} <= cited:
        return "KILL (SHIPUX must cite PRODNAT·PRODKEEP·SHIPKEEP)"
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
            return out.replace("SHIPUI2", "SHIPUX")
        return out
    if bool(src.get("hard_natural_labeled", True)):
        if not _hard_natural_labeled(default_asks):
            return "KILL (hard-natural ask not labeled LOOKUP on ship path)"
    return (
        f"PROMOTE ({SHIPUX_ID}: modes+content honest · "
        "DECODE law · hard-natural labeled after PRODNAT)"
    )
