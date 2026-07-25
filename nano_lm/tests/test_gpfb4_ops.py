"""Contract: H-ABS-GPFB4 dual-gate under GENC genome (K=4; ≠ GPFB K=2)."""

from __future__ import annotations

from gpfb4_ops import EPS_LP, MIN_UNIQUE, decide_hgpfb4


def test_given_code_up_story_ok_when_decide_then_promote() -> None:
    d = decide_hgpfb4(
        parent_story=-10.0,
        parent_code=-16.0,
        gpfb4_story=-9.9,
        gpfb4_code=-14.0,
        mean_unique=MIN_UNIQUE + 0.1,
        mean_elig=1.5,
        mean_switch=0.4,
        k=4,
        identical=False,
    )
    assert d.startswith("PROMOTE")
    assert "ABS-GPFB4" in d
    assert "ABS-GPFB k=" not in d
    assert "wall↓" not in d


def test_given_story_drop_when_decide_then_kill() -> None:
    d = decide_hgpfb4(
        parent_story=-10.0,
        parent_code=-16.0,
        gpfb4_story=-10.0 - EPS_LP - 0.2,
        gpfb4_code=-10.0,
        mean_unique=2.0,
        mean_elig=1.0,
        mean_switch=0.5,
        k=4,
        identical=False,
    )
    assert d.startswith("KILL")
    assert "story_lp" in d


def test_given_no_switch_when_decide_then_kill() -> None:
    d = decide_hgpfb4(
        parent_story=-10.0,
        parent_code=-16.0,
        gpfb4_story=-9.5,
        gpfb4_code=-10.0,
        mean_unique=2.0,
        mean_elig=0.0,
        mean_switch=0.0,
        k=4,
        identical=False,
    )
    assert d.startswith("KILL")


def test_given_code_flat_when_decide_then_kill() -> None:
    d = decide_hgpfb4(
        parent_story=-10.0,
        parent_code=-16.0,
        gpfb4_story=-9.9,
        gpfb4_code=-16.0,
        mean_unique=3.0,
        mean_elig=2.0,
        mean_switch=0.5,
        k=4,
        identical=False,
    )
    assert d.startswith("KILL")
    assert "code_lp" in d
