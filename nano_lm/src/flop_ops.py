"""H-FLOP: tokens/s + estimated decode FLOPs (uncached AR math)."""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "tokens_per_s",
    "est_decode_flops",
    "to_gflops",
    "decide_hflop",
]


def tokens_per_s(*, n_new: int, wall_ms: float) -> float:
    """
    GIVEN generated token count and wall_ms
    WHEN computing throughput
    THEN return tokens/s (0 if empty or non-positive wall).
    """
    if int(n_new) < 1 or float(wall_ms) <= 0.0:
        return 0.0
    return float(n_new) / (float(wall_ms) / 1000.0)


def est_decode_flops(
    *,
    n_params: int,
    prompt_len: int,
    n_new: int,
    token_evals: int | None = None,
) -> float:
    """
    GIVEN student params and decode lengths
    WHEN estimating matmul FLOPs (use_cache=False)
    THEN 2*N*Σ(seq_len) — exact for 1-beam AR; else token_evals×avg_len.
    """
    n = int(n_params)
    p = max(0, int(prompt_len))
    t = max(0, int(n_new))
    if n < 1 or t < 1:
        return 0.0
    if token_evals is None or int(token_evals) == t:
        # sum_{k=1..t} (p+k) = t*p + t*(t+1)/2
        tok_steps = t * p + t * (t + 1) // 2
        return 2.0 * float(n) * float(tok_steps)
    avg_len = float(p) + float(t) / 2.0
    return 2.0 * float(n) * float(token_evals) * avg_len


def to_gflops(flops: float) -> float:
    return float(flops) / 1.0e9


def decide_hflop(
    stats: Mapping[str, Mapping[str, float]],
) -> str:
    """
    GIVEN families scored with FLOP instrumentation
    WHEN deciding
    THEN PROMOTE iff every family has finite tps + gflops; else KILL.
    """
    if not stats:
        return "KILL (no rows)"
    for name, s in stats.items():
        tps = s.get("mean_tps")
        gf = s.get("mean_gflops")
        if tps is None or gf is None:
            return f"KILL (missing FLOP metrics: {name})"
        if tps != tps or gf != gf:  # NaN
            return f"KILL (NaN FLOP metrics: {name})"
    return "PROMOTE (FLOP+tps metrics live)"
