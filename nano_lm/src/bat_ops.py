"""H-BAT: batched multi-prompt decode; throughput gate vs serial EARLY."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["decide_hbat", "left_pad_batch"]


def left_pad_batch(
    sequences: list[list[int]], *, pad_id: int
) -> tuple[list[list[int]], list[list[int]], list[int]]:
    """
    GIVEN variable-length token id lists
    WHEN left-padding to a common length
    THEN return (padded_ids, attention_masks, prompt_lens).
    """
    if not sequences:
        raise ValueError("left_pad_batch: empty sequences")
    lens = [len(s) for s in sequences]
    max_len = max(lens)
    ids: list[list[int]] = []
    masks: list[list[int]] = []
    for seq, n in zip(sequences, lens):
        pad = max_len - n
        ids.append([int(pad_id)] * pad + list(seq))
        masks.append([0] * pad + [1] * n)
    return ids, masks, lens


def decide_hbat(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-BAT vs serial H-EARLY
    WHEN deciding
    THEN PROMOTE iff |Δlp| ≤ ε and tok/s > serial; else KILL.
    """
    tip = stats.get("H-EARLY")
    if tip is None:
        return "needs H-EARLY control"
    if abs(float(s["mean_lp"]) - float(tip["mean_lp"])) > float(eps_lp):
        return "KILL (lp change vs serial EARLY)"
    if float(s["mean_tps"]) <= float(tip["mean_tps"]):
        return "KILL (no tok/s win vs serial EARLY)"
    return "PROMOTE (batched throughput vs serial EARLY)"
