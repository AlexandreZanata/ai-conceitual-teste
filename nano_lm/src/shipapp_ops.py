"""Wave AT2 H-SHIPAPP: human ask/apps/ship-demo always show product modes."""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Sequence

from aq_product_hitl_ops import APP_SURFACES
from as_dual_hitl_ops import APP_SMOKE_PACK
from at_session_ops import AT0_MODES, AT0_SHIPAPP_CHARTER
from shipui_ops import (
    REQUIRED_MODES,
    attach_shipui,
    default_ask_labeled,
    decide_shipui,
    mode_visible,
    smoke_modes_ok,
)

__all__ = [
    "SHIPAPP_ID",
    "SHIPAPP_THESIS",
    "SHIPAPP_CLAIM",
    "SHIPAPP_CHARTER",
    "SHIPAPP_PATHS",
    "REQUIRED_MODES",
    "APP_SURFACES",
    "APP_SMOKE_PACK",
    "attach_shipapp",
    "mode_visible",
    "default_ask_labeled",
    "smoke_modes_ok",
    "charter_ok",
    "apps_labeled",
    "demo_card_markdown",
    "decide_shipapp",
]

SHIPAPP_ID = "H-SHIPAPP"
SHIPAPP_THESIS = (
    "Human-facing nano:z:ask · apps ask · ship/demo always show "
    "mode=LOOKUP|PEAK|DECODE|ABSTAIN (4/4); no unlabeled answer"
)
SHIPAPP_CLAIM = (
    "AF packaged stack + AQ product layer + AS trust path — not open chat LM"
)
SHIPAPP_CHARTER: Mapping[str, object] = AT0_SHIPAPP_CHARTER
SHIPAPP_PATHS: tuple[str, ...] = ("nano:z:ask", "apps ask", "ship/demo")


def attach_shipapp(payload: MutableMapping[str, Any]) -> dict[str, Any]:
    """Delegate SHIPUI attach — same mode banner contract."""
    return attach_shipui(payload)


def charter_ok(charter: Mapping[str, object] | None = None) -> bool:
    """
    GIVEN AT0 SHIPAPP charter
    WHEN checking paths · banner · smoke · modes
    THEN True iff human surfaces + 4 modes covered.
    """
    src = charter if charter is not None else SHIPAPP_CHARTER
    paths = src.get("paths")
    if not isinstance(paths, list):
        return False
    if set(SHIPAPP_PATHS) - set(paths):
        return False
    modes = src.get("required_modes")
    if not isinstance(modes, list) or set(modes) != AT0_MODES:
        return False
    if str(src.get("smoke", "")) != "4/4":
        return False
    banner = str(src.get("banner", ""))
    return all(token in banner for token in REQUIRED_MODES)


def apps_labeled(rows: Sequence[Mapping[str, Any]]) -> bool:
    """
    GIVEN apps-ask smoke rows (known-ask · howto · long-doc)
    WHEN checking mode honesty
    THEN True iff every surface has visible product_mode banner.
    """
    if len(rows) < len(APP_SURFACES):
        return False
    by_app = {str(r.get("app_id", "")): r for r in rows}
    for surface in APP_SURFACES:
        row = by_app.get(surface)
        if row is None:
            return False
        if not mode_visible(row):
            return False
        if str(row.get("product_mode", "")) not in AT0_MODES:
            return False
    return True


def demo_card_markdown(
    *,
    arms: Sequence[Mapping[str, Any]],
    apps: Sequence[Mapping[str, Any]],
) -> str:
    """
    GIVEN four-arm + apps rows
    WHEN rendering human ship/app demo card
    THEN markdown tables with modeui_line visible.
    """
    lines = [
        "# SHIPAPP — mode always visible (ask · apps · ship/demo)",
        "",
        "## Ship/demo arms",
        "",
        "| Arm | product_mode | modeui_line |",
        "|-----|--------------|-------------|",
    ]
    for row in arms:
        arm = str(row.get("arm", row.get("product_mode", "?")))
        pm = str(row.get("product_mode", "UNKNOWN"))
        line = str(row.get("modeui_line", ""))
        lines.append(f"| {arm} | **{pm}** | `{line}` |")
    lines.extend(
        [
            "",
            "## Apps ask",
            "",
            "| app_id | product_mode | modeui_line |",
            "|--------|--------------|-------------|",
        ]
    )
    for row in apps:
        app = str(row.get("app_id", "?"))
        pm = str(row.get("product_mode", "UNKNOWN"))
        line = str(row.get("modeui_line", ""))
        lines.append(f"| {app} | **{pm}** | `{line}` |")
    lines.extend(
        [
            "",
            "Rule: every human-facing answer shows exactly one of "
            "`LOOKUP` · `PEAK` · `DECODE` · `ABSTAIN` — never unlabeled.",
            "",
            f"Charter paths: {', '.join(SHIPAPP_PATHS)}",
            "",
        ]
    )
    return "\n".join(lines)


def decide_shipapp(
    *,
    arms: Sequence[Mapping[str, Any]],
    default_asks: Sequence[Mapping[str, Any]],
    apps: Sequence[Mapping[str, Any]],
    charter: Mapping[str, object] | None = None,
) -> str:
    """
    GIVEN four-arm smoke + default asks + apps surfaces
    WHEN applying pesquisa §5 AT2 H-SHIPAPP
    THEN PROMOTE iff charter ok · 4/4 · apps labeled · no unlabeled.
    """
    if not charter_ok(charter):
        return "KILL (SHIPAPP charter incomplete)"
    ship = decide_shipui(rows=arms, default_asks=default_asks)
    if ship != "PROMOTE":
        return f"KILL (ship/demo|ask: {ship})"
    if not apps_labeled(apps):
        return "KILL (apps ask missing mode banner / unlabeled)"
    return "PROMOTE"
