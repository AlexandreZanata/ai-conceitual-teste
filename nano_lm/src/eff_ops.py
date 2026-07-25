"""H-EFF: re-measure PACK efficiency on prog/btc vs Phase B baselines."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = [
    "EPS_LP",
    "PHASE_B_SERVE",
    "domain_speed_win",
    "at_quality_floor",
    "decide_heff",
]

# Phase B formal H-SERVE means (docs/results/nano-lm/formal-h{prog,btc}-*.md).
PHASE_B_SERVE: dict[str, dict[str, float]] = {
    "prog": {
        "mean_lp": -8.1653,
        "mean_wall": 4.0,
        "mean_tps": 1956.9,
        "early_lp": -8.1626,
    },
    "btc": {
        "mean_lp": -10.9160,
        "mean_wall": 7.0,
        "mean_tps": 2359.5,
        "early_lp": -10.9223,
    },
}


def at_quality_floor(
    serve_lp: float,
    early_lp: float,
    *,
    eps_lp: float = EPS_LP,
) -> bool:
    """True when SERVE teacher_lp is within ε of EARLY (same-run floor)."""
    return float(serve_lp) >= float(early_lp) - float(eps_lp)


def domain_speed_win(
    serve: Mapping[str, float],
    baseline: Mapping[str, float],
) -> bool:
    """
    GIVEN fresh SERVE means and Phase B SERVE baseline
    WHEN checking efficiency
    THEN True iff wall↓ or tok/s↑.
    """
    wall_down = float(serve["mean_wall"]) < float(baseline["mean_wall"])
    tps_up = float(serve["mean_tps"]) > float(baseline["mean_tps"])
    return wall_down or tps_up


def decide_heff(
    domain_stats: Mapping[str, Mapping[str, Mapping[str, float]]],
    *,
    baselines: Mapping[str, Mapping[str, float]] | None = None,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN per-domain {H-EARLY,H-SERVE} means vs Phase B SERVE baselines
    WHEN deciding efficiency claim update
    THEN PROMOTE if any domain at quality floor improves wall or tok/s;
    else HOLD.
    """
    base = baselines or PHASE_B_SERVE
    wins: list[str] = []
    holds: list[str] = []
    for name, fams in domain_stats.items():
        if name not in base:
            holds.append(f"{name}=no-baseline")
            continue
        early = fams.get("H-EARLY") or {}
        serve = fams.get("H-SERVE") or {}
        if "mean_lp" not in serve or "mean_lp" not in early:
            holds.append(f"{name}=incomplete")
            continue
        if not at_quality_floor(
            float(serve["mean_lp"]), float(early["mean_lp"]), eps_lp=eps_lp
        ):
            holds.append(f"{name}=floor-fail")
            continue
        if domain_speed_win(serve, base[name]):
            wins.append(name)
        else:
            holds.append(f"{name}=no-speedup")
    if wins:
        return (
            "PROMOTE (PACK efficiency ↑ at quality floor on "
            + ",".join(wins)
            + ")"
        )
    detail = "; ".join(holds) if holds else "no domains"
    return f"HOLD (no PACK efficiency gain vs Phase B: {detail})"
