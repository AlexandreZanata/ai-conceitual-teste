"""Contract: H-ABS-QPFB reuses PFB gate labeled for QT parent."""

from __future__ import annotations

from qpfb_ops import EPS_LP, MIN_UNIQUE, decide_hqpfb, pick_pfb_beam


def test_given_none_eligible_when_pick_then_parent_sentinel() -> None:
    pick, n = pick_pfb_beam(
        [-12.0, -11.0],
        [-1.0, -2.0],
        floor=-10.0,
    )
    assert pick is None and n == 0


def test_given_code_up_story_ok_when_decide_then_promote() -> None:
    d = decide_hqpfb(
        parent_story=-10.0,
        parent_code=-16.0,
        qpfb_story=-9.9,
        qpfb_code=-14.0,
        mean_unique=MIN_UNIQUE + 0.5,
        mean_elig=2.0,
        mean_switch=0.4,
        k=4,
        identical=False,
    )
    assert d.startswith("PROMOTE")
    assert "ABS-QPFB" in d
    assert "QQPFB" not in d


def test_given_story_drop_when_decide_then_kill() -> None:
    d = decide_hqpfb(
        parent_story=-10.0,
        parent_code=-16.0,
        qpfb_story=-10.0 - EPS_LP - 0.2,
        qpfb_code=-10.0,
        mean_unique=3.0,
        mean_elig=2.0,
        mean_switch=0.5,
        k=4,
        identical=False,
    )
    assert d.startswith("KILL")
    assert "story_lp" in d


def test_given_no_switch_when_decide_then_kill() -> None:
    d = decide_hqpfb(
        parent_story=-10.0,
        parent_code=-16.0,
        qpfb_story=-9.5,
        qpfb_code=-10.0,
        mean_unique=4.0,
        mean_elig=0.0,
        mean_switch=0.0,
        k=4,
        identical=False,
    )
    assert d.startswith("KILL")
