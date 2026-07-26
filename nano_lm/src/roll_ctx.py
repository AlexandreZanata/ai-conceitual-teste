"""Build rolled contexts: summary‖window with active ≤ W+S."""

from __future__ import annotations

from typing import Any

from roll_ops import ROLL_S, ROLL_W

__all__ = ["compress_token_ids", "iter_roll_segments", "expand_roll_prompts"]


def compress_token_ids(ids: list[int], s: int) -> list[int]:
    """
    GIVEN past token ids and budget S
    WHEN compressing for the summary cache
    THEN return ≤S ids (even stride subsample; not RAG).
    """
    n = len(ids)
    if s <= 0 or n == 0:
        return []
    if n <= s:
        return list(ids)
    if s == 1:
        return [ids[n // 2]]
    out: list[int] = []
    for i in range(s):
        out.append(ids[int(round(i * (n - 1) / (s - 1)))])
    return out


def iter_roll_segments(
    ids: list[int],
    *,
    w: int = ROLL_W,
    s: int = ROLL_S,
) -> list[dict[str, Any]]:
    """
    GIVEN full prompt token ids
    WHEN rolling with window W and summary budget S
    THEN yield one segment dict per window (ctx_ids = summary‖window).
    """
    if w < 1:
        raise ValueError("w must be >= 1")
    l_eff = len(ids)
    if l_eff < 1:
        return []
    segs: list[dict[str, Any]] = []
    for start in range(0, l_eff, w):
        past = ids[:start]
        window = ids[start : start + w]
        summary = compress_token_ids(past, s) if past else []
        ctx_ids = summary + window
        segs.append(
            {
                "l_eff": l_eff,
                "active_len": len(ctx_ids),
                "summary_len": len(summary),
                "window_len": len(window),
                "seg_i": start // w,
                "ctx_ids": ctx_ids,
            }
        )
    return segs


def expand_roll_prompts(
    tokenizer: Any,
    texts: list[str],
    *,
    w: int = ROLL_W,
    s: int = ROLL_S,
) -> tuple[list[str], list[dict[str, Any]]]:
    """
    GIVEN elongated prog texts
    WHEN expanding to rolled segment prompts
    THEN return (ctx_strings, per-segment meta aligned 1:1).
    """
    prompts: list[str] = []
    meta: list[dict[str, Any]] = []
    for text in texts:
        ids = list(tokenizer.encode(text, add_special_tokens=False))
        for seg in iter_roll_segments(ids, w=w, s=s):
            ctx = tokenizer.decode(seg["ctx_ids"], skip_special_tokens=True)
            prompts.append(ctx)
            meta.append(
                {
                    "l_eff": int(seg["l_eff"]),
                    "active_len": int(seg["active_len"]),
                    "summary_len": int(seg["summary_len"]),
                    "window_len": int(seg["window_len"]),
                    "seg_i": int(seg["seg_i"]),
                    "source_prompt": text,
                }
            )
    return prompts, meta
