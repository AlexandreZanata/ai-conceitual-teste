"""Contract: H-GPFB4-LONG dual gate + ROLL mem + wall budget; never K=2."""

from __future__ import annotations

from gpfb4long_ops import (
    EPS_LP,
    K_BEAMS,
    MIN_UNIQUE,
    WALL_SLACK_MS,
    decide_hgpfb4long,
    require_k4,
)


def test_given_k2_when_require_then_kill() -> None:
    assert require_k4(2) is not None
    assert require_k4(K_BEAMS) is None


def test_given_code_up_roll_ok_when_decide_then_promote() -> None:
    d = decide_hgpfb4long(
        parent_story=-10.0,
        parent_code=-16.0,
        long_story=-9.9,
        long_code=-14.0,
        mean_unique=MIN_UNIQUE + 0.1,
        mean_elig=1.5,
        mean_switch=0.4,
        k=4,
        identical=False,
        l_eff=400.0,
        mean_active=150.0,
        wall_roll=50.0,
        wall_full=60.0,
    )
    assert d.startswith("PROMOTE")
    assert "GPFB4-LONG" in d
    assert "wall_roll≤full" in d


def test_given_k2_when_decide_then_kill() -> None:
    d = decide_hgpfb4long(
        parent_story=-10.0,
        parent_code=-16.0,
        long_story=-9.9,
        long_code=-14.0,
        mean_unique=3.0,
        mean_elig=1.5,
        mean_switch=0.4,
        k=2,
        identical=False,
        l_eff=400.0,
        mean_active=150.0,
        wall_roll=40.0,
        wall_full=60.0,
    )
    assert d.startswith("KILL")
    assert "pathology" in d or "k=2" in d


def test_given_leff_low_when_decide_then_kill() -> None:
    d = decide_hgpfb4long(
        parent_story=-10.0,
        parent_code=-16.0,
        long_story=-9.9,
        long_code=-14.0,
        mean_unique=3.0,
        mean_elig=1.5,
        mean_switch=0.4,
        k=4,
        identical=False,
        l_eff=100.0,
        mean_active=80.0,
        wall_roll=40.0,
        wall_full=60.0,
    )
    assert d.startswith("KILL")
    assert "L_eff" in d


def test_given_wall_over_when_decide_then_kill() -> None:
    d = decide_hgpfb4long(
        parent_story=-10.0,
        parent_code=-16.0,
        long_story=-9.9,
        long_code=-14.0,
        mean_unique=3.0,
        mean_elig=1.5,
        mean_switch=0.4,
        k=4,
        identical=False,
        l_eff=400.0,
        mean_active=150.0,
        wall_roll=80.0,
        wall_full=60.0,
        wall_slack_ms=WALL_SLACK_MS,
    )
    assert d.startswith("KILL")
    assert "wall" in d.lower()


def test_given_story_drop_when_decide_then_kill() -> None:
    d = decide_hgpfb4long(
        parent_story=-10.0,
        parent_code=-16.0,
        long_story=-10.0 - EPS_LP - 0.2,
        long_code=-10.0,
        mean_unique=3.0,
        mean_elig=1.0,
        mean_switch=0.5,
        k=4,
        identical=False,
        l_eff=400.0,
        mean_active=150.0,
        wall_roll=40.0,
        wall_full=60.0,
    )
    assert d.startswith("KILL")
    assert "story_lp" in d
