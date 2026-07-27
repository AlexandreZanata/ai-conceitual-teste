"""Wave AS6 H-SHIPUI: ship/demo + default ask always show LOOKUP|PEAK|DECODE|ABSTAIN."""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Sequence

from as_session_ops import AS0_MODES, map_as_product_mode
from modeui_ops import format_modeui_line
from shipdemo_ops import (
    REQUIRED_MODES,
    demo_card_markdown,
    mode_visible,
    smoke_modes_ok,
)

__all__ = [
    "SHIPUI_ID",
    "SHIPUI_THESIS",
    "REQUIRED_MODES",
    "attach_shipui",
    "mode_visible",
    "default_ask_labeled",
    "demo_card_markdown",
    "smoke_modes_ok",
    "decide_shipui",
]

SHIPUI_ID = "H-SHIPUI"
SHIPUI_THESIS = (
    "After ASKABSTAIN + METRICS, ship/demo and default nano:z:ask always "
    "show mode=LOOKUP|PEAK|DECODE|ABSTAIN (4/4); no unlabeled answer"
)


def attach_shipui(payload: MutableMapping[str, Any]) -> dict[str, Any]:
    """
    GIVEN ASK/demo payload (post-finalize or PEAK)
    WHEN attaching SHIPUI fields
    THEN set product_mode + modeui_line (never leave unlabeled).
    """
    raw = str(payload.get("mode", "") or "")
    existing = str(payload.get("product_mode", "") or "")
    if existing in AS0_MODES:
        product = existing
    else:
        product = map_as_product_mode(raw)
    payload["product_mode"] = product
    payload["modeui_line"] = format_modeui_line(
        product_mode=product,
        wall_ms=float(payload.get("wall_ms") or 0.0),
        n_new=int(payload.get("n_new") or 0),
        raw_mode=raw,
    )
    return dict(payload)


def default_ask_labeled(payload: Mapping[str, Any]) -> bool:
    """
    GIVEN default nano:z:ask finalize payload
    WHEN checking UI honesty without re-attach
    THEN True iff product_mode + modeui_line already present and visible.
    """
    if "product_mode" not in payload or "modeui_line" not in payload:
        return False
    return mode_visible(payload)


def decide_shipui(
    *,
    rows: Sequence[Mapping[str, Any]],
    default_asks: Sequence[Mapping[str, Any]] | None = None,
) -> str:
    """
    GIVEN four-arm smoke (+ optional default-ask samples)
    WHEN applying pesquisa §5 AS6 gate
    THEN PROMOTE iff 4/4 modes visible and default asks labeled.
    """
    if len(rows) != 4:
        return f"KILL (need 4 smoke arms, got {len(rows)})"
    for row in rows:
        pm = str(row.get("product_mode", ""))
        if pm not in AS0_MODES:
            return f"KILL (unlabeled/unknown product_mode: {pm!r})"
        if not mode_visible(row):
            return f"KILL (mode not visible in UI line: {pm})"
    if not smoke_modes_ok(rows):
        modes = [str(r.get("product_mode", "")) for r in rows]
        return f"KILL (mode set incomplete: {modes})"
    if default_asks is not None:
        if not default_asks:
            return "KILL (default ask samples empty)"
        for ask in default_asks:
            if not default_ask_labeled(ask):
                return "KILL (default ask missing modeui_line / unlabeled)"
    return "PROMOTE"
