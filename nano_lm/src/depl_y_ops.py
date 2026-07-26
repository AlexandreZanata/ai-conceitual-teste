"""DEPL-Y freeze: Wave Y+Z deploy routes (128 vs long + HITL honesty)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "DEPL_Y_ID",
    "DEPL_Y_GOALS",
    "DEPL_Y_ROUTES",
    "DEPL_Y_FORBIDDEN",
    "DEPL_Y_EVIDENCE",
    "choose_depl_y",
    "reject_forbidden",
    "decide_depl_y",
]

DEPL_Y_ID = "DEPL-Y"

# Goal → frozen use string (RECIPES / card one-liners).
DEPL_Y_ROUTES: dict[str, str] = {
    "speed_128": "H-PACK + H-QT int8 n=1",
    "code_128": "H-ABS-QPFB2 + H-BEAMKV / H-TCACHE / H-SCORERAM",
    "code_btc": "H-ABS-BPFB",
    "long_ctx": "H-ROLL / H-SUMCACHE / H-GPFB4-LONG (+ H-PFB256)",
    "hitl_known": "--wrap LOOKUP (champion-wrap-v0) H-ZWRAP",
    "story_ce": "H-ZERR (zerr-qpfb2-v0) story-safe CE only",
    "train": "H-TPACK + H-AMORT",
    "quality_in_dist": "H-QPACK (in-dist only)",
}

DEPL_Y_GOALS: tuple[str, ...] = tuple(DEPL_Y_ROUTES.keys())

DEPL_Y_FORBIDDEN: frozenset[str] = frozenset(
    {
        "STREAM",
        "KVCACHE-Q",
        "GENCACHE",
        "GPFB_K2",
        "ood_long_pack",
        "open_chat_lm",
        "zerr_as_chat",
        "naive_CTX",
        "MIXD",
    }
)

# Public formal / HITL notes that must exist for freeze PROMOTE.
DEPL_Y_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/formal-hqpfb2-qpfb2.md",
    "docs/results/nano-lm/formal-hbeamkv-beamkv.md",
    "docs/results/nano-lm/formal-htcache-tcache.md",
    "docs/results/nano-lm/formal-hscoreram-scoreram.md",
    "docs/results/nano-lm/formal-hpfb256-pfb256.md",
    "docs/results/nano-lm/formal-hroll-roll.md",
    "docs/results/nano-lm/formal-hsumcache-sumcache.md",
    "docs/results/nano-lm/formal-hgpfb4long-gpfb4long.md",
    "docs/results/nano-lm/wave-y-summary.md",
    "docs/results/nano-lm/wave-z-hitl-z4.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)


def choose_depl_y(goal: str, *, L: int | None = None) -> str:
    """
    GIVEN deploy goal (+ optional prompt length L)
    WHEN applying DEPL-Y freeze
    THEN return route string or REJECT reason.
    """
    g = str(goal)
    if g not in DEPL_Y_ROUTES:
        return "REJECT (unknown goal; use DEPL_Y_GOALS)"
    if L is not None:
        if g == "code_128" and int(L) > 128:
            return "REJECT (code_128 is L≤128; use long_ctx)"
        if g == "long_ctx" and int(L) <= 128:
            return "REJECT (long_ctx needs L>128; use code_128)"
        if g == "speed_128" and int(L) > 128:
            return "REJECT (PACK speed route forbids ood_long L)"
    return DEPL_Y_ROUTES[g]


def reject_forbidden(token: str) -> bool:
    """
    GIVEN a recipe / claim token
    WHEN checking DEPL-Y ban list
    THEN True iff token is forbidden.
    """
    t = str(token).strip()
    if t in DEPL_Y_FORBIDDEN:
        return True
    upper = t.upper().replace("-", "_")
    for ban in DEPL_Y_FORBIDDEN:
        if ban.upper().replace("-", "_") in upper:
            return True
    return False


def decide_depl_y(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = DEPL_Y_EVIDENCE,
) -> str:
    """
    GIVEN path→exists flags for freeze evidence
    WHEN deciding DEPL-Y
    THEN PROMOTE iff every required path is True; else KILL naming first miss.
    """
    missing: list[str] = []
    for path in required:
        if not bool(evidence_ok.get(path)):
            missing.append(path)
    if missing:
        return f"KILL (missing evidence: {missing[0]})"
    routes = "; ".join(f"{g}→{DEPL_Y_ROUTES[g]}" for g in DEPL_Y_GOALS)
    return f"PROMOTE ({DEPL_Y_ID} freeze: {routes})"


def route_table() -> list[dict[str, Any]]:
    """Rows for docs / JSON freeze card."""
    return [{"goal": g, "use": DEPL_Y_ROUTES[g]} for g in DEPL_Y_GOALS]
