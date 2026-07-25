"""H-ABS-PFB: story-floor code BoN; empty-elig → parent (≠ CSAFE)."""

from __future__ import annotations

from lat_ops import EPS_LP

__all__ = [
    "K_BEAMS",
    "PFB_TEMP",
    "MIN_UNIQUE",
    "EPS_LP",
    "eligible_indices",
    "pick_pfb_beam",
    "unique_texts",
    "decide_hpfb",
]

K_BEAMS = 4
PFB_TEMP = 0.8
MIN_UNIQUE = 1.5


def eligible_indices(story_lps: list[float], floor: float) -> list[int]:
    """
    GIVEN beam story_lps and floor = parent_story − ε
    WHEN filtering PFB eligibility
    THEN return indices with story_lp ≥ floor.
    """
    return [i for i, s in enumerate(story_lps) if float(s) >= float(floor)]


def pick_pfb_beam(
    story_lps: list[float],
    code_lps: list[float],
    *,
    floor: float,
) -> tuple[int | None, int]:
    """
    GIVEN K story/code LPs + story floor
    WHEN committing PFB
    THEN return (beam_idx, n_elig) with max code among eligible;
    if none eligible, return (None, 0) → caller keeps parent.
    """
    if len(story_lps) != len(code_lps) or not story_lps:
        raise ValueError("story_lps and code_lps must be same non-empty length")
    elig = eligible_indices(story_lps, floor)
    if not elig:
        return None, 0
    best = max(elig, key=lambda i: float(code_lps[i]))
    return int(best), len(elig)


def unique_texts(texts: list[str]) -> int:
    """Count distinct continuation strings (diversity audit)."""
    return len({t for t in texts})


def decide_hpfb(
    *,
    parent_story: float,
    parent_code: float,
    pfb_story: float,
    pfb_code: float,
    mean_unique: float,
    mean_elig: float,
    mean_switch: float,
    k: int,
    identical: bool,
) -> str:
    """
    GIVEN parent vs PFB dual means + diversity/switch
    WHEN deciding H-ABS-PFB
    THEN KILL on identity / no-switch / low unique / story < parent−ε /
    code not ↑; else PROMOTE.
    """
    if identical or float(mean_switch) <= 0.0:
        return "KILL (identity vs parent; PFB never switched)"
    if float(mean_unique) < float(MIN_UNIQUE):
        return (
            f"KILL (unique@K {float(mean_unique):.2f} < {MIN_UNIQUE} "
            f"diversity floor)"
        )
    floor = float(parent_story) - float(EPS_LP)
    if float(pfb_story) < floor:
        return (
            f"KILL (story_lp {float(pfb_story):.4f} < parent−ε {floor:.4f})"
        )
    if not (float(pfb_code) > float(parent_code)):
        return (
            f"KILL (code_lp {float(pfb_code):.4f} ≤ parent "
            f"{float(parent_code):.4f})"
        )
    return (
        f"PROMOTE (ABS-PFB k={int(k)} unique≈{float(mean_unique):.2f} "
        f"elig≈{float(mean_elig):.2f} switch≈{float(mean_switch):.2f}; "
        f"code↑ story≥parent−ε)"
    )
