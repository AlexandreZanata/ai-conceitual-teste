"""H-CHUNK: chunked prefill under FLASH; wall gate vs FLASH tip."""

from __future__ import annotations

from typing import Any, Mapping

from lat_ops import EPS_LP

__all__ = [
    "DEFAULT_CHUNK",
    "LONG_TARGET_TOKENS",
    "decide_hchunk",
    "elongate_prompt",
    "EPS_LP",
]

DEFAULT_CHUNK = 32
LONG_TARGET_TOKENS = 128


def elongate_prompt(
    text: str,
    tokenizer: Any,
    *,
    target_tokens: int = LONG_TARGET_TOKENS,
) -> str:
    """
    GIVEN a short smoke prompt
    WHEN elongating by repetition
    THEN return text with ≥ target_tokens (hypothesis needs long prefill).
    """
    if int(target_tokens) < 1:
        raise ValueError("target_tokens must be >= 1")
    cur = text.strip() or "Once upon a time"
    while len(tokenizer.encode(cur)) < int(target_tokens):
        cur = f"{cur} {text.strip() or 'Once upon a time'}"
    return cur


def decide_hchunk(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-CHUNK vs H-EARLY / H-FLASH
    WHEN deciding
    THEN PROMOTE iff lp ≥ EARLY−ε and wall < FLASH; else KILL.
    """
    early = stats.get("H-EARLY")
    flash = stats.get("H-FLASH")
    if early is None:
        return "needs H-EARLY control"
    if flash is None:
        return "needs H-FLASH control"
    if float(s["mean_lp"]) < float(early["mean_lp"]) - float(eps_lp):
        return "KILL (quality drop vs H-EARLY)"
    if not (float(s["mean_wall"]) < float(flash["mean_wall"])):
        return "KILL (no wall win vs H-FLASH)"
    return "PROMOTE (chunked prefill under FLASH)"
