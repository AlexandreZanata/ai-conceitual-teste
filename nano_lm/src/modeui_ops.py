"""Wave AQ5 H-MODEUI: ship/demo always shows mode=LOOKUP|PEAK|DECODE."""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Sequence

from aq_session_ops import AQ0_MODES, map_product_mode

__all__ = [
    "MODEUI_ID",
    "MODEUI_THESIS",
    "REQUIRED_MODES",
    "attach_modeui",
    "format_modeui_line",
    "mode_visible",
    "demo_card_markdown",
    "smoke_modes_ok",
    "decide_modeui",
]

MODEUI_ID = "H-MODEUI"
REQUIRED_MODES: tuple[str, ...] = ("LOOKUP", "PEAK", "DECODE")
MODEUI_THESIS = (
    "Ship/demo UI always shows mode=LOOKUP|PEAK|DECODE; "
    "smoke three modes visible; no unlabeled answer"
)


def format_modeui_line(
    *,
    product_mode: str,
    wall_ms: float,
    n_new: int,
    raw_mode: str = "",
) -> str:
    """
    GIVEN product mode + telemetry
    WHEN formatting ship/demo line
    THEN return visible mode=LOOKUP|PEAK|DECODE banner.
    """
    raw = f" · raw={raw_mode}" if raw_mode and raw_mode != product_mode else ""
    return (
        f"mode={product_mode} · wall_ms={float(wall_ms):.4f} · "
        f"n_new={int(n_new)}{raw}"
    )


def attach_modeui(payload: MutableMapping[str, Any]) -> dict[str, Any]:
    """
    GIVEN an ASK/demo payload with raw mode
    WHEN attaching MODEUI fields
    THEN set product_mode + modeui_line (never leave unlabeled).
    """
    raw = str(payload.get("mode", "") or "")
    product = map_product_mode(raw)
    payload["product_mode"] = product
    payload["modeui_line"] = format_modeui_line(
        product_mode=product,
        wall_ms=float(payload.get("wall_ms") or 0.0),
        n_new=int(payload.get("n_new") or 0),
        raw_mode=raw,
    )
    return dict(payload)


def mode_visible(payload: Mapping[str, Any]) -> bool:
    """
    GIVEN a payload
    WHEN checking UI honesty
    THEN True iff product_mode is exactly LOOKUP|PEAK|DECODE.
    """
    mode = str(payload.get("product_mode", "") or "")
    if mode not in AQ0_MODES:
        return False
    line = str(payload.get("modeui_line", "") or "")
    return f"mode={mode}" in line


def demo_card_markdown(rows: Sequence[Mapping[str, Any]]) -> str:
    """
    GIVEN LOOKUP/PEAK/DECODE smoke rows
    WHEN rendering ship/demo card
    THEN markdown table with modeui_line visible per arm.
    """
    lines = [
        "# MODEUI demo — mode always visible",
        "",
        "| Arm | product_mode | modeui_line |",
        "|-----|--------------|-------------|",
    ]
    for row in rows:
        arm = str(row.get("arm", row.get("product_mode", "?")))
        pm = str(row.get("product_mode", "UNKNOWN"))
        line = str(row.get("modeui_line", ""))
        lines.append(f"| {arm} | **{pm}** | `{line}` |")
    lines.extend(
        [
            "",
            "Rule: every answer shows exactly one of "
            "`LOOKUP` · `PEAK` · `DECODE` — never unlabeled.",
            "",
        ]
    )
    return "\n".join(lines)


def smoke_modes_ok(rows: Sequence[Mapping[str, Any]]) -> bool:
    """
    GIVEN three-arm smoke payloads
    WHEN validating MODEUI gate
    THEN True iff each required mode appears exactly once and is visible.
    """
    seen: list[str] = []
    for row in rows:
        if not mode_visible(row):
            return False
        seen.append(str(row.get("product_mode", "")))
    return sorted(seen) == sorted(REQUIRED_MODES)


def decide_modeui(*, rows: Sequence[Mapping[str, Any]]) -> str:
    """
    GIVEN smoke rows for LOOKUP · PEAK · DECODE
    WHEN applying H-MODEUI gate
    THEN PROMOTE iff three modes visible and none unlabeled.
    """
    if len(rows) != 3:
        return f"KILL (need 3 smoke arms, got {len(rows)})"
    for row in rows:
        pm = str(row.get("product_mode", ""))
        if pm not in AQ0_MODES:
            return f"KILL (unlabeled/unknown product_mode: {pm!r})"
        if not mode_visible(row):
            return f"KILL (mode not visible in UI line: {pm})"
    if not smoke_modes_ok(rows):
        modes = [str(r.get("product_mode", "")) for r in rows]
        return f"KILL (mode set incomplete: {modes})"
    return "PROMOTE"
