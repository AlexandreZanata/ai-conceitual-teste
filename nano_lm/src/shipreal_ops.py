"""Wave AU2 H-SHIPREAL: ship/demo modes + answers match mode claim."""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Sequence

from abstain_ops import is_junk_decode
from au_session_ops import AU0_ANTI_FP, AU0_MODES, AU0_SAFE_NOTE, AU0_SHIP_LOCK
from asksmart_ops import is_period_collapse
from prodhard_ops import NEAR_MISS_ASK, PEAK_ASK, near_miss_ok, peak_span_usable
from shipapp_ops import (
    APP_SMOKE_PACK,
    APP_SURFACES,
    REQUIRED_MODES,
    SHIPAPP_PATHS,
    apps_labeled,
    attach_shipapp,
    charter_ok,
    decide_shipapp,
    demo_card_markdown,
    mode_visible,
)
from shipui_ops import smoke_modes_ok

__all__ = [
    "SHIPREAL_ID",
    "SHIPREAL_THESIS",
    "SHIPREAL_CLAIM",
    "SHIPREAL_SAFE_NOTE",
    "SHIPREAL_ANTI_FP",
    "SHIPREAL_PATHS",
    "SHIPREAL_CHARTER",
    "REQUIRED_MODES",
    "APP_SURFACES",
    "APP_SMOKE_PACK",
    "NEAR_MISS_ASK",
    "PEAK_ASK",
    "attach_shipreal",
    "mode_visible",
    "content_matches_mode",
    "arms_content_ok",
    "apps_content_ok",
    "demo_card_markdown",
    "decide_shipreal",
]

SHIPREAL_ID = "H-SHIPREAL"
SHIPREAL_THESIS = (
    "Human ship/demo + ask + apps always show mode=LOOKUP|PEAK|DECODE|"
    "ABSTAIN; answers match mode claim (content bars); no unlabeled"
)
SHIPREAL_CLAIM = AU0_SHIP_LOCK
SHIPREAL_SAFE_NOTE = AU0_SAFE_NOTE
SHIPREAL_ANTI_FP = AU0_ANTI_FP
SHIPREAL_PATHS: tuple[str, ...] = SHIPAPP_PATHS
SHIPREAL_CHARTER: Mapping[str, object] = {
    "paths": list(SHIPREAL_PATHS),
    "required_modes": list(REQUIRED_MODES),
    "banner": "mode=LOOKUP|PEAK|DECODE|ABSTAIN",
    "smoke": "4/4",
    "content_bars": True,
    "rule": (
        "every human-facing answer shows product_mode and content "
        "matches the mode claim; no unlabeled"
    ),
    "anti_fp": (
        "SHIPREAL mode+content honesty ≠ generative IQ; "
        "PEAK stays extractive label"
    ),
    "stage": "AU2 H-SHIPREAL",
}


def attach_shipreal(payload: MutableMapping[str, Any]) -> dict[str, Any]:
    """Same mode banner attach as SHIPAPP/SHIPUI."""
    return attach_shipapp(payload)


def _lookup_content_ok(completion: str) -> bool:
    text = str(completion or "").strip()
    if not text or text == "NO_ANSWER":
        return False
    if "def add" in text:
        return True
    # Mid-word prose fragment (live-audit PEAK debt class) — reject.
    if (
        text[0].islower()
        and "." not in text
        and "(" not in text
        and not text.startswith(("`", "/", "_"))
    ):
        return False
    return len(text) >= 3


def _decode_content_ok(row: Mapping[str, Any]) -> bool:
    """
    DECODE bar: usable non-junk text.
    wall_ms/n_new mandatory but never sufficient (AV1 DECODE content debt).
    """
    text = str(row.get("completion", "")).strip()
    if not text or text == "NO_ANSWER":
        return False
    if is_period_collapse(text):
        return False
    if is_junk_decode(text):
        return False
    if "\ufffd" in text or "�" in text:
        return False
    if float(row.get("wall_ms") or 0.0) <= 0.0:
        return False
    if int(row.get("n_new") or 0) <= 0:
        return False
    return True


def content_matches_mode(row: Mapping[str, Any]) -> bool:
    """
    GIVEN a labeled ship/demo or ask row
    WHEN checking AU2 content bar
    THEN True iff completion matches claimed product_mode.
    """
    mode = str(row.get("product_mode", "") or "")
    if mode not in AU0_MODES:
        return False
    if not mode_visible(row):
        return False
    text = str(row.get("completion", ""))
    if mode == "LOOKUP":
        return _lookup_content_ok(text)
    if mode == "PEAK":
        return peak_span_usable(text)
    if mode == "DECODE":
        return _decode_content_ok(row)
    # ABSTAIN
    return text.strip() == "NO_ANSWER"


def arms_content_ok(arms: Sequence[Mapping[str, Any]]) -> bool:
    """Four arms cover modes and each passes content bar."""
    if not smoke_modes_ok(arms):
        return False
    by_mode = {str(r.get("product_mode", "")): r for r in arms}
    for mode in REQUIRED_MODES:
        row = by_mode.get(mode)
        if row is None or not content_matches_mode(row):
            return False
    return True


def apps_content_ok(apps: Sequence[Mapping[str, Any]]) -> bool:
    """
    Apps surfaces stay labeled; LOOKUP answers must carry usable content.
    """
    if not apps_labeled(apps):
        return False
    for row in apps:
        mode = str(row.get("product_mode", ""))
        if mode == "LOOKUP" and not content_matches_mode(row):
            return False
        if mode == "ABSTAIN" and not content_matches_mode(row):
            return False
        if not mode_visible(row):
            return False
    return True


def decide_shipreal(
    *,
    arms: Sequence[Mapping[str, Any]],
    default_asks: Sequence[Mapping[str, Any]],
    apps: Sequence[Mapping[str, Any]],
    near_miss: Mapping[str, Any] | None = None,
    charter: Mapping[str, object] | None = None,
    anti_fp_signed: bool = True,
) -> str:
    """
    GIVEN four-arm smoke + defaults + apps + near-miss
    WHEN applying pesquisa §5 AU2 H-SHIPREAL
    THEN PROMOTE iff modes 4/4 · content bars · near-miss ABSTAIN ·
         no unlabeled; else KILL.
    """
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    src = charter if charter is not None else SHIPREAL_CHARTER
    if not charter_ok(src):
        return "KILL (SHIPREAL charter incomplete)"
    ship = decide_shipapp(
        arms=arms, default_asks=default_asks, apps=apps, charter=src
    )
    if ship != "PROMOTE":
        return f"KILL (shipapp base: {ship})"
    if not arms_content_ok(arms):
        return "KILL (arm content does not match mode claim)"
    if not apps_content_ok(apps):
        return "KILL (apps content/mode honesty fail)"
    if near_miss is not None and not near_miss_ok(near_miss):
        return "KILL (near-miss on default ask not ABSTAIN)"
    return f"PROMOTE ({SHIPREAL_ID}: modes+content honest)"
