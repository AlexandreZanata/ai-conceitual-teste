"""H-ANN formal helpers: anneal vs cosine KD decision."""

from __future__ import annotations

from typing import Mapping

__all__ = ["decide_hann"]


def decide_hann(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-ANN vs KD-cos
    WHEN deciding
    THEN PROMOTE only if teacher_lp > KD-cos; else KILL.
    """
    cos = stats.get("KD-cos")
    if cos is None:
        return "needs KD-cos control"
    if float(s["mean_lp"]) > float(cos["mean_lp"]) + 1e-6:
        return "PROMOTE (beats cosine KD)"
    return "KILL (cosine wins)"
