"""Decode-family kill/promote helpers (H-DEC / H-SPEC / quantum)."""

from __future__ import annotations

from typing import Mapping

EPS_LP = 0.05


def decide_hdec_row(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    b4 = stats.get("B4")
    if b4 is None:
        return "needs B4 control"
    if float(s["mean_lp"]) > float(b4["mean_lp"]) + 1e-6:
        return "PROMOTE (beats fixed BoN/B4)"
    return "KILL (≤ fixed BoN/B4)"


def decide_hspec_row(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    b3 = stats.get("B3")
    if b3 is None:
        return "needs B3 control"
    faster = float(s["mean_tps"]) > float(b3["mean_tps"]) + 1e-6
    ok_q = float(s["mean_lp"]) >= float(b3["mean_lp"]) - EPS_LP
    if faster and ok_q:
        return "PROMOTE (faster vs B3, quality ok)"
    if not faster:
        return "KILL (no speedup vs B3)"
    return "KILL (quality drop vs B3)"


def decide_quantum_row(
    fam: str, s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    bon = stats.get("BoN-uniform", {}).get("mean_lp")
    if bon is None:
        return "ablation"
    if fam == "BoN-uniform":
        return "ablation control"
    if float(s["mean_lp"]) > float(bon) + 1e-6:
        return "PROMOTE (vs uniform BoN)"
    return "KILL (≤ uniform BoN)"
