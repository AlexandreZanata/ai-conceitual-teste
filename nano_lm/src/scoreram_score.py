"""Pack score pass for H-SCORERAM using PackScoreCache."""

from __future__ import annotations

import time
from typing import Any

from load_model import LoadedModel
from scoreram_ops import PackScoreCache
from tcache_score import commit_pfb_rows_tcache, rescore_bank_stories

__all__ = ["score_pack_pass"]


def score_pack_pass(
    *,
    story_teacher: LoadedModel,
    code_teacher: LoadedModel,
    banks: list[dict[str, Any]],
    parent_code_by_key: dict[tuple[str, int], float],
    cache: PackScoreCache,
) -> tuple[list[dict[str, Any]], float]:
    """
    GIVEN banks + PackScoreCache
    WHEN scoring story then eligible-only code
    THEN return PFB rows and score wall_ms (cache updated in place).
    """
    t0 = time.perf_counter()
    banks_s, _ = rescore_bank_stories(story_teacher, banks, memo=cache.memo)
    rows, _, _ = commit_pfb_rows_tcache(
        code_teacher,
        banks_s,
        parent_code_by_key=parent_code_by_key,
        story_memo=cache.memo,
        family="H-SCORERAM",
    )
    if story_teacher.device.type == "cuda" or getattr(
        getattr(code_teacher, "device", None), "type", ""
    ) == "cuda":
        import torch

        if torch.cuda.is_available():
            torch.cuda.synchronize()
    wall_ms = (time.perf_counter() - t0) * 1000.0
    return rows, wall_ms
