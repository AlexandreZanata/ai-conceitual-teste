"""Contract: H-ABS-BPFB dual-gate + wall↓ on bitcoin pack."""

from __future__ import annotations

from bpfb_ops import EPS_LP, MIN_UNIQUE, decide_hbpfb


def test_given_code_up_wall_down_when_decide_then_promote() -> None:
    d = decide_hbpfb(
        parent_story=-10.0,
        parent_code=-16.0,
        bpfb_story=-9.9,
        bpfb_code=-14.0,
        mean_unique=MIN_UNIQUE + 0.1,
        mean_elig=1.5,
        mean_switch=0.4,
        bpfb_wall=40.0,
        bpfb4_wall=75.0,
        identical=False,
    )
    assert d.startswith("PROMOTE")
    assert "ABS-BPFB" in d
    assert "wall↓" in d
    assert "ABS-BBPFB" not in d
    assert "PFB22" not in d


def test_given_wall_not_down_when_decide_then_kill() -> None:
    d = decide_hbpfb(
        parent_story=-10.0,
        parent_code=-16.0,
        bpfb_story=-9.9,
        bpfb_code=-14.0,
        mean_unique=2.0,
        mean_elig=1.5,
        mean_switch=0.4,
        bpfb_wall=80.0,
        bpfb4_wall=75.0,
        identical=False,
    )
    assert d.startswith("KILL")
    assert "wall" in d.lower()


def test_given_story_drop_when_decide_then_kill() -> None:
    d = decide_hbpfb(
        parent_story=-10.0,
        parent_code=-16.0,
        bpfb_story=-10.0 - EPS_LP - 0.2,
        bpfb_code=-10.0,
        mean_unique=2.0,
        mean_elig=1.0,
        mean_switch=0.5,
        bpfb_wall=40.0,
        bpfb4_wall=75.0,
        identical=False,
    )
    assert d.startswith("KILL")
    assert "story_lp" in d


def test_given_no_switch_when_decide_then_kill() -> None:
    d = decide_hbpfb(
        parent_story=-10.0,
        parent_code=-16.0,
        bpfb_story=-9.5,
        bpfb_code=-10.0,
        mean_unique=2.0,
        mean_elig=0.0,
        mean_switch=0.0,
        bpfb_wall=40.0,
        bpfb4_wall=75.0,
        identical=False,
    )
    assert d.startswith("KILL")
