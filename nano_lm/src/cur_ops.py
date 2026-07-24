"""H-CUR: length-curriculum KD helpers; decide vs B2."""

from __future__ import annotations

from typing import Mapping

__all__ = ["DEFAULT_SEQ_LO", "N_STAGES", "cur_seq_len", "decide_hcur"]

DEFAULT_SEQ_LO = 16
N_STAGES = 3


def cur_seq_len(
    step: int, steps: int, *, seq_lo: int, seq_hi: int, n_stages: int = N_STAGES
) -> int:
    """
    GIVEN step in [0, steps) and seq_lo ≤ seq_hi
    WHEN forming curriculum length
    THEN n_stages equal stages from seq_lo → seq_hi (few rebuilds).
    """
    lo = int(seq_lo)
    hi = int(seq_hi)
    n = int(n_stages)
    if lo < 1 or hi < lo:
        raise ValueError("cur_seq_len: need 1 ≤ seq_lo ≤ seq_hi")
    if n < 1:
        raise ValueError("cur_seq_len: n_stages must be >= 1")
    if n == 1 or steps <= 1:
        return hi
    t = max(0, min(int(step), int(steps) - 1))
    stage = min(n - 1, (t * n) // int(steps))
    return int(round(lo + stage * (hi - lo) / float(n - 1)))


def decide_hcur(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-CUR vs B2
    WHEN deciding
    THEN PROMOTE iff teacher_lp > B2; else KILL.
    """
    b2 = stats.get("B2")
    if b2 is None:
        return "needs B2 control"
    if float(s["mean_lp"]) > float(b2["mean_lp"]) + 1e-6:
        return "PROMOTE (beats B2)"
    return "KILL (≤ B2)"
