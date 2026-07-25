"""Contract: H-BEAMKV dual-gate + wall↓ vs indep prefills."""

from __future__ import annotations

from beamkv_ops import EPS_LP, MIN_UNIQUE, decide_hbeamkv


def test_given_code_up_wall_down_when_decide_then_promote() -> None:
    # GIVEN QPFB2-class dual win + wall↓ vs naive WHEN decide THEN PROMOTE
    d = decide_hbeamkv(
        parent_story=-10.0,
        parent_code=-16.0,
        beamkv_story=-9.9,
        beamkv_code=-14.0,
        mean_unique=MIN_UNIQUE + 0.1,
        mean_elig=1.5,
        mean_switch=0.4,
        beamkv_wall=40.0,
        naive_wall=75.0,
        identical=False,
    )
    assert d.startswith("PROMOTE")
    assert "BEAMKV" in d
    assert "wall↓" in d
    assert "indep" in d


def test_given_wall_not_down_when_decide_then_kill() -> None:
    d = decide_hbeamkv(
        parent_story=-10.0,
        parent_code=-16.0,
        beamkv_story=-9.9,
        beamkv_code=-14.0,
        mean_unique=2.0,
        mean_elig=1.5,
        mean_switch=0.4,
        beamkv_wall=80.0,
        naive_wall=75.0,
        identical=False,
    )
    assert d.startswith("KILL")
    assert "wall" in d.lower()


def test_given_story_drop_when_decide_then_kill() -> None:
    d = decide_hbeamkv(
        parent_story=-10.0,
        parent_code=-16.0,
        beamkv_story=-10.0 - EPS_LP - 0.2,
        beamkv_code=-10.0,
        mean_unique=2.0,
        mean_elig=1.0,
        mean_switch=0.5,
        beamkv_wall=40.0,
        naive_wall=75.0,
        identical=False,
    )
    assert d.startswith("KILL")
    assert "story_lp" in d


def test_given_no_switch_when_decide_then_kill() -> None:
    d = decide_hbeamkv(
        parent_story=-10.0,
        parent_code=-16.0,
        beamkv_story=-9.5,
        beamkv_code=-10.0,
        mean_unique=2.0,
        mean_elig=0.0,
        mean_switch=0.0,
        beamkv_wall=40.0,
        naive_wall=75.0,
        identical=False,
    )
    assert d.startswith("KILL")
