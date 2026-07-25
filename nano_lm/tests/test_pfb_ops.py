"""Contract: H-ABS-PFB parent-fallback story-floor + dual-teacher gate."""

from __future__ import annotations

from pfb_ops import (
    EPS_LP,
    MIN_UNIQUE,
    decide_hpfb,
    eligible_indices,
    pick_pfb_beam,
    unique_texts,
)


def test_given_floor_when_eligible_then_only_above() -> None:
    assert eligible_indices([-10.0, -9.0, -11.0], -10.0) == [0, 1]


def test_given_eligibles_when_pick_then_max_code_among_them() -> None:
    pick, n = pick_pfb_beam(
        [-10.0, -9.5, -12.0],
        [-5.0, -4.0, -1.0],
        floor=-10.05,
    )
    assert n == 2
    assert pick == 1


def test_given_none_eligible_when_pick_then_parent_sentinel() -> None:
    # GIVEN all below floor
    # WHEN committing PFB
    # THEN None → caller keeps parent (≠ CSAFE max-story)
    pick, n = pick_pfb_beam(
        [-12.0, -11.0, -13.0],
        [-1.0, -2.0, -0.5],
        floor=-10.0,
    )
    assert n == 0
    assert pick is None


def test_given_distinct_when_unique_then_count() -> None:
    assert unique_texts(["a", "b", "a"]) == 2


def test_given_code_up_story_ok_when_decide_then_promote() -> None:
    d = decide_hpfb(
        parent_story=-10.0,
        parent_code=-16.0,
        pfb_story=-10.0 + 0.01,
        pfb_code=-14.0,
        mean_unique=MIN_UNIQUE + 0.1,
        mean_elig=2.0,
        mean_switch=0.5,
        k=4,
        identical=False,
    )
    assert d.startswith("PROMOTE")


def test_given_story_drop_when_decide_then_kill() -> None:
    d = decide_hpfb(
        parent_story=-10.0,
        parent_code=-16.0,
        pfb_story=-10.0 - EPS_LP - 0.1,
        pfb_code=-10.0,
        mean_unique=3.0,
        mean_elig=2.0,
        mean_switch=0.5,
        k=4,
        identical=False,
    )
    assert d.startswith("KILL")
    assert "story_lp" in d


def test_given_no_switch_when_decide_then_kill() -> None:
    d = decide_hpfb(
        parent_story=-10.0,
        parent_code=-16.0,
        pfb_story=-9.9,
        pfb_code=-10.0,
        mean_unique=4.0,
        mean_elig=0.0,
        mean_switch=0.0,
        k=4,
        identical=False,
    )
    assert d.startswith("KILL")
    assert "switch" in d.lower() or "identity" in d


def test_given_code_flat_when_decide_then_kill() -> None:
    d = decide_hpfb(
        parent_story=-10.0,
        parent_code=-16.0,
        pfb_story=-9.9,
        pfb_code=-16.0,
        mean_unique=3.0,
        mean_elig=2.0,
        mean_switch=0.5,
        k=4,
        identical=False,
    )
    assert d.startswith("KILL")
    assert "code_lp" in d
