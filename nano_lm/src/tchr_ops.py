"""H-TCHR: wire frozen tiny code teacher; dual story + code_teacher_lp."""

from __future__ import annotations

import math
from typing import Any, Mapping

__all__ = [
    "CODE_TEACHER_ID",
    "CODE_TEACHER_LICENSE",
    "CODE_TEACHER_PARAMS",
    "STORY_TEACHER_ID",
    "STORY_REGRESS_FLOOR",
    "code_teacher_meta",
    "decide_htchr",
    "lp_finite",
]

CODE_TEACHER_ID = "bigcode/tiny_starcoder_py"
CODE_TEACHER_PARAMS = 164_000_000
CODE_TEACHER_LICENSE = "BigCode OpenRAIL-M v1"
STORY_TEACHER_ID = "roneneldan/TinyStories-33M"
# Prog@128 EARLY formal ≈ −8.2; floor catches collapse, not tip noise.
STORY_REGRESS_FLOOR = -12.0


def code_teacher_meta() -> dict[str, Any]:
    """Frozen catalog row for every H-TCHR report."""
    return {
        "hf_id": CODE_TEACHER_ID,
        "tokenizer_id": CODE_TEACHER_ID,
        "params": CODE_TEACHER_PARAMS,
        "license": CODE_TEACHER_LICENSE,
        "role": "code_teacher",
    }


def lp_finite(lp: float) -> bool:
    """True when length-normalized mean log-prob is a usable real."""
    return bool(math.isfinite(lp)) and float(lp) > -100.0


def decide_htchr(
    *,
    code_teacher: Mapping[str, Any],
    mean_story_lp: float,
    mean_code_lp: float,
    n_rows: int,
    story_floor: float = STORY_REGRESS_FLOOR,
) -> str:
    """
    GIVEN code-teacher meta + dual mean lps on prog@128
    WHEN deciding H-TCHR wire readiness
    THEN PROMOTE iff meta matches catalog, n≥1, both lps finite,
         and story_lp ≥ floor (no silent story regression); else KILL.
    """
    if int(n_rows) < 1:
        return "KILL (no scored rows)"
    if str(code_teacher.get("hf_id")) != CODE_TEACHER_ID:
        return "KILL (code teacher hf_id mismatch)"
    if int(code_teacher.get("params", 0)) != CODE_TEACHER_PARAMS:
        return "KILL (code teacher params mismatch)"
    if not str(code_teacher.get("license", "")).strip():
        return "KILL (code teacher license missing)"
    if not lp_finite(float(mean_code_lp)):
        return "KILL (code_teacher_lp not stable/finite)"
    if not lp_finite(float(mean_story_lp)):
        return "KILL (story teacher_lp not finite)"
    if float(mean_story_lp) < float(story_floor):
        return (
            f"KILL (story teacher_lp {mean_story_lp:.4f} < floor {story_floor})"
        )
    return (
        "PROMOTE (code teacher wired; code_teacher_lp stable on prog@128; "
        "story floor held)"
    )
