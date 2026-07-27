"""Wave AV2 H-SHIPUI2: ship/demo modes + DECODE content honesty."""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Sequence

from av_session_ops import (
    AV0_ANTI_FP,
    AV0_MODES,
    AV0_SAFE_NOTE,
    AV0_SHIP_LOCK,
)
from modeui_ops import format_modeui_line
from prodhard_ops import NEAR_MISS_ASK, PEAK_ASK, near_miss_ok
from prodship_ops import decode_content_honest, gate_junk_decode
from shipapp_ops import (
    APP_SMOKE_PACK,
    APP_SURFACES,
    REQUIRED_MODES,
    SHIPAPP_PATHS,
    apps_labeled,
    attach_shipapp,
    charter_ok,
    demo_card_markdown as shipapp_demo_card,
)
from shipreal_ops import apps_content_ok, content_matches_mode
from shipui_ops import mode_visible

__all__ = [
    "SHIPUI2_ID",
    "SHIPUI2_THESIS",
    "SHIPUI2_CLAIM",
    "SHIPUI2_SAFE_NOTE",
    "SHIPUI2_ANTI_FP",
    "SHIPUI2_PATHS",
    "SHIPUI2_CHARTER",
    "REQUIRED_MODES",
    "APP_SURFACES",
    "APP_SMOKE_PACK",
    "NEAR_MISS_ASK",
    "PEAK_ASK",
    "attach_shipui2",
    "mode_visible",
    "content_matches_mode",
    "banner_modes_ok",
    "arms_honest_ok",
    "apps_content_ok",
    "core_modes_ok",
    "demo_card_markdown",
    "decide_shipui2",
]

SHIPUI2_ID = "H-SHIPUI2"
SHIPUI2_THESIS = (
    "Human ship/demo + ask + apps always show mode=LOOKUP|PEAK|DECODE|"
    "ABSTAIN; content matches mode (DECODE usable or ABSTAIN on junk); "
    "no unlabeled"
)
SHIPUI2_CLAIM = AV0_SHIP_LOCK
SHIPUI2_SAFE_NOTE = AV0_SAFE_NOTE
SHIPUI2_ANTI_FP = AV0_ANTI_FP
SHIPUI2_PATHS: tuple[str, ...] = SHIPAPP_PATHS
SHIPUI2_CHARTER: Mapping[str, object] = {
    "paths": list(SHIPUI2_PATHS),
    "required_modes": list(REQUIRED_MODES),
    "banner": "mode=LOOKUP|PEAK|DECODE|ABSTAIN",
    "smoke": "4/4",
    "content_bars": True,
    "decode_usable_or_abstain": True,
    "rule": (
        "every human-facing answer shows product_mode and content "
        "matches the mode claim; DECODE gibberish → ABSTAIN; no unlabeled"
    ),
    "anti_fp": (
        "SHIPUI2 mode+content honesty ≠ generative IQ; "
        "DECODE telemetry-only content_ok forbidden; "
        "PEAK stays extractive label"
    ),
    "stage": "AV2 H-SHIPUI2",
}


def attach_shipui2(payload: MutableMapping[str, Any]) -> dict[str, Any]:
    """Attach mode banner; refuse junk DECODE to ABSTAIN."""
    row = attach_shipapp(payload)
    return attach_shipapp(gate_junk_decode(row))


def banner_modes_ok() -> bool:
    """
    GIVEN REQUIRED_MODES charter
    WHEN formatting modeui lines
    THEN each mode renders `mode=<MODE>` (banner 4/4).
    """
    for mode in REQUIRED_MODES:
        line = format_modeui_line(
            product_mode=mode, wall_ms=1.0, n_new=1, raw_mode=mode
        )
        if f"mode={mode}" not in line:
            return False
    return True


def arms_honest_ok(arms: Sequence[Mapping[str, Any]]) -> bool:
    """Every arm labeled and content matches claimed product_mode."""
    if len(arms) < 3:
        return False
    for row in arms:
        if not mode_visible(row):
            return False
        if not content_matches_mode(row):
            return False
    return True


def core_modes_ok(arms: Sequence[Mapping[str, Any]]) -> bool:
    """LOOKUP · PEAK · ABSTAIN must appear in live honest arms."""
    modes = {str(r.get("product_mode") or "") for r in arms}
    return {"LOOKUP", "PEAK", "ABSTAIN"} <= modes


def demo_card_markdown(
    *,
    arms: Sequence[Mapping[str, Any]],
    apps: Sequence[Mapping[str, Any]],
    decode_probe: Mapping[str, Any] | None = None,
) -> str:
    """Human demo card with arms + apps + DECODE probe honesty."""
    body = shipapp_demo_card(arms=arms, apps=apps)
    if decode_probe is None:
        return body.replace("SHIPAPP", "SHIPUI2", 1)
    pm = str(decode_probe.get("product_mode", "UNKNOWN"))
    line = str(decode_probe.get("modeui_line", ""))
    comp = str(decode_probe.get("completion", ""))[:72]
    extra = "\n".join(
        [
            "",
            "## DECODE path probe (content law)",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| product_mode | **{pm}** |",
            f"| modeui_line | `{line}` |",
            f"| completion | `{comp}` |",
            f"| honest | **{decode_content_honest(decode_probe)}** |",
            "",
            "Rule: DECODE gibberish must ABSTAIN — never telemetry-only "
            "`content_ok`.",
            "",
        ]
    )
    return body.replace("SHIPAPP", "SHIPUI2", 1) + extra


def decide_shipui2(
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
    GIVEN ship/demo arms + apps + DECODE probe + near-miss
    WHEN applying pesquisa §5 AV2 H-SHIPUI2
    THEN PROMOTE iff banner 4/4 · labeled · content honest ·
         DECODE usable/ABSTAIN · near-miss ABSTAIN; else KILL.
    """
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    src = charter if charter is not None else SHIPUI2_CHARTER
    if not charter_ok(src):
        return "KILL (SHIPUI2 charter incomplete)"
    if not bool(src.get("decode_usable_or_abstain")):
        return "KILL (SHIPUI2 must require DECODE usable-or-abstain)"
    if not banner_modes_ok():
        return "KILL (banner cannot render LOOKUP|PEAK|DECODE|ABSTAIN)"
    if not arms_honest_ok(arms):
        return "KILL (arm content/mode honesty fail)"
    if not core_modes_ok(arms):
        return "KILL (live arms missing LOOKUP·PEAK·ABSTAIN)"
    if not apps_content_ok(apps):
        return "KILL (apps content/mode honesty fail)"
    if not apps_labeled(apps):
        return "KILL (apps unlabeled)"
    for row in default_asks:
        if not mode_visible(row):
            return "KILL (default ask unlabeled)"
        if not content_matches_mode(row):
            return "KILL (default ask content mismatch)"
    if not decode_content_honest(decode_probe):
        return "KILL (DECODE probe not usable and not ABSTAIN)"
    # If DECODE still labeled, content_matches already covered via honest.
    # If junk was refused, product_mode must be ABSTAIN.
    d_mode = str(decode_probe.get("product_mode") or "")
    if d_mode not in AV0_MODES:
        return "KILL (DECODE probe unlabeled)"
    if near_miss is not None and not near_miss_ok(near_miss):
        return "KILL (near-miss on default ask not ABSTAIN)"
    return f"PROMOTE ({SHIPUI2_ID}: modes+content honest · DECODE law)"
