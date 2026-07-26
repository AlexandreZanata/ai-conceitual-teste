"""Build hierarchical summary+tail contexts for H-SUMCACHE."""

from __future__ import annotations

from typing import Any

from roll_ctx import compress_token_ids
from sumcache_ops import (
    SUMCACHE_S_COARSE,
    SUMCACHE_S_FINE,
    SUMCACHE_TARGET,
    SUMCACHE_W,
    FULL_PREFILL_CAP,
)

__all__ = ["build_sumcache_ids", "expand_sumcache_prompts", "clip_full_ids"]


def clip_full_ids(ids: list[int], *, cap: int = FULL_PREFILL_CAP) -> list[int]:
    """Full-prefill baseline: first `cap` tokens (leave room for max_new)."""
    if cap < 1:
        raise ValueError("cap must be >= 1")
    return list(ids[:cap])


def build_sumcache_ids(
    ids: list[int],
    *,
    w: int = SUMCACHE_W,
    s_coarse: int = SUMCACHE_S_COARSE,
    s_fine: int = SUMCACHE_S_FINE,
) -> dict[str, Any]:
    """
    GIVEN full source token ids (L_eff)
    WHEN building hierarchical summary+tail
    THEN coarse‖fine‖tail with active ≤ S_coarse+S_fine+W.
    """
    l_eff = len(ids)
    if l_eff < 1:
        return {
            "l_eff": 0,
            "active_len": 0,
            "ctx_ids": [],
            "coarse_len": 0,
            "fine_len": 0,
            "tail_len": 0,
        }
    if l_eff <= w:
        return {
            "l_eff": l_eff,
            "active_len": l_eff,
            "ctx_ids": list(ids),
            "coarse_len": 0,
            "fine_len": 0,
            "tail_len": l_eff,
        }
    tail = ids[-w:]
    past = ids[:-w]
    mid = len(past) // 2
    coarse = compress_token_ids(past[:mid], s_coarse) if mid else []
    fine = compress_token_ids(past[mid:], s_fine) if past[mid:] else []
    ctx = coarse + fine + tail
    return {
        "l_eff": l_eff,
        "active_len": len(ctx),
        "ctx_ids": ctx,
        "coarse_len": len(coarse),
        "fine_len": len(fine),
        "tail_len": len(tail),
    }


def expand_sumcache_prompts(
    tokenizer: Any,
    texts: list[str],
    *,
    w: int = SUMCACHE_W,
    s_coarse: int = SUMCACHE_S_COARSE,
    s_fine: int = SUMCACHE_S_FINE,
    full_cap: int = FULL_PREFILL_CAP,
) -> tuple[list[str], list[str], list[dict[str, Any]]]:
    """
    GIVEN elongated prog texts
    WHEN expanding SUMCACHE + full-prefill arms
    THEN (sum_prompts, full_prompts, meta) aligned 1:1.
    """
    sum_prompts: list[str] = []
    full_prompts: list[str] = []
    meta: list[dict[str, Any]] = []
    for text in texts:
        ids = list(tokenizer.encode(text, add_special_tokens=False))
        built = build_sumcache_ids(
            ids, w=w, s_coarse=s_coarse, s_fine=s_fine
        )
        full_ids = clip_full_ids(ids, cap=full_cap)
        sum_prompts.append(
            tokenizer.decode(built["ctx_ids"], skip_special_tokens=True)
        )
        full_prompts.append(
            tokenizer.decode(full_ids, skip_special_tokens=True)
        )
        meta.append(
            {
                "l_eff": int(built["l_eff"]),
                "active_len": int(built["active_len"]),
                "full_len": len(full_ids),
                "coarse_len": int(built["coarse_len"]),
                "fine_len": int(built["fine_len"]),
                "tail_len": int(built["tail_len"]),
                "source_prompt": text,
            }
        )
    return sum_prompts, full_prompts, meta
