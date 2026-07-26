"""Contract: H-PFB256 dual-gate vs EARLY@256 + wall compare to @128."""

from __future__ import annotations

from pfb256_ops import EPS_LP, MIN_UNIQUE, PFB256_TARGET, REF128_TARGET, decide_hpfb256


def test_given_targets_when_read_then_256_and_128() -> None:
    assert PFB256_TARGET == 256
    assert REF128_TARGET == 128


def test_given_code_up_when_decide_then_promote_with_wall_note() -> None:
    d = decide_hpfb256(
        parent_story=-10.0,
        parent_code=-16.0,
        pfb256_story=-9.9,
        pfb256_code=-14.0,
        mean_unique=MIN_UNIQUE + 0.1,
        mean_elig=1.0,
        mean_switch=0.4,
        wall_256=80.0,
        wall_128=50.0,
        identical=False,
    )
    assert d.startswith("PROMOTE")
    assert "PFB256" in d
    assert "wall@256=80" in d
    assert "vs @128=50" in d


def test_given_story_drop_when_decide_then_kill() -> None:
    d = decide_hpfb256(
        parent_story=-10.0,
        parent_code=-16.0,
        pfb256_story=-10.0 - EPS_LP - 0.2,
        pfb256_code=-10.0,
        mean_unique=2.0,
        mean_elig=1.0,
        mean_switch=0.5,
        wall_256=80.0,
        wall_128=50.0,
        identical=False,
    )
    assert d.startswith("KILL")
    assert "story_lp" in d


def test_given_code_not_up_when_decide_then_kill() -> None:
    d = decide_hpfb256(
        parent_story=-10.0,
        parent_code=-14.0,
        pfb256_story=-9.5,
        pfb256_code=-14.0,
        mean_unique=2.0,
        mean_elig=1.0,
        mean_switch=0.5,
        wall_256=80.0,
        wall_128=50.0,
        identical=False,
    )
    assert d.startswith("KILL")
    assert "code_lp" in d


def test_given_no_switch_when_decide_then_kill() -> None:
    d = decide_hpfb256(
        parent_story=-10.0,
        parent_code=-16.0,
        pfb256_story=-9.5,
        pfb256_code=-10.0,
        mean_unique=2.0,
        mean_elig=0.0,
        mean_switch=0.0,
        wall_256=80.0,
        wall_128=50.0,
        identical=False,
    )
    assert d.startswith("KILL")
