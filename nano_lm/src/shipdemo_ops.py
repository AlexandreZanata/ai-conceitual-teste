"""Wave AR2 H-SHIPDEMO: ship/demo shows LOOKUP|PEAK|DECODE|ABSTAIN."""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Sequence

from ar_session_ops import AR0_MODES, map_ar_product_mode
from modeui_ops import format_modeui_line

__all__ = [
    "SHIPDEMO_ID",
    "SHIPDEMO_THESIS",
    "REQUIRED_MODES",
    "attach_shipdemo",
    "mode_visible",
    "demo_card_markdown",
    "smoke_modes_ok",
    "decide_shipdemo",
]

SHIPDEMO_ID = "H-SHIPDEMO"
REQUIRED_MODES: tuple[str, ...] = ("LOOKUP", "PEAK", "DECODE", "ABSTAIN")
SHIPDEMO_THESIS = (
    "Ship/demo UI always shows mode=LOOKUP|PEAK|DECODE|ABSTAIN; "
    "four-arm human-visible smoke; no unlabeled answer"
)


def attach_shipdemo(payload: MutableMapping[str, Any]) -> dict[str, Any]:
    """
    GIVEN an ASK/demo payload (optionally post-abstain)
    WHEN attaching ship-demo fields
    THEN set product_mode + modeui_line (never leave unlabeled).
    """
    raw = str(payload.get("mode", "") or "")
    existing = str(payload.get("product_mode", "") or "")
    if existing in AR0_MODES:
        product = existing
    else:
        product = map_ar_product_mode(raw)
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
    THEN True iff product_mode is LOOKUP|PEAK|DECODE|ABSTAIN and line shows it.
    """
    mode = str(payload.get("product_mode", "") or "")
    if mode not in AR0_MODES:
        return False
    line = str(payload.get("modeui_line", "") or "")
    return f"mode={mode}" in line


def demo_card_markdown(rows: Sequence[Mapping[str, Any]]) -> str:
    """
    GIVEN four-arm smoke rows
    WHEN rendering ship/demo card
    THEN markdown table with modeui_line visible per arm.
    """
    lines = [
        "# SHIPDEMO — mode always visible (incl. ABSTAIN)",
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
            "`LOOKUP` · `PEAK` · `DECODE` · `ABSTAIN` — never unlabeled.",
            "",
        ]
    )
    return "\n".join(lines)


def smoke_modes_ok(rows: Sequence[Mapping[str, Any]]) -> bool:
    """
    GIVEN four-arm smoke payloads
    WHEN validating SHIPDEMO gate
    THEN True iff each required mode appears exactly once and is visible.
    """
    seen: list[str] = []
    for row in rows:
        if not mode_visible(row):
            return False
        seen.append(str(row.get("product_mode", "")))
    return sorted(seen) == sorted(REQUIRED_MODES)


def decide_shipdemo(*, rows: Sequence[Mapping[str, Any]]) -> str:
    """
    GIVEN smoke rows for LOOKUP · PEAK · DECODE · ABSTAIN
    WHEN applying H-SHIPDEMO gate
    THEN PROMOTE iff four modes visible and none unlabeled.
    """
    if len(rows) != 4:
        return f"KILL (need 4 smoke arms, got {len(rows)})"
    for row in rows:
        pm = str(row.get("product_mode", ""))
        if pm not in AR0_MODES:
            return f"KILL (unlabeled/unknown product_mode: {pm!r})"
        if not mode_visible(row):
            return f"KILL (mode not visible in UI line: {pm})"
    if not smoke_modes_ok(rows):
        modes = [str(r.get("product_mode", "")) for r in rows]
        return f"KILL (mode set incomplete: {modes})"
    return "PROMOTE"
