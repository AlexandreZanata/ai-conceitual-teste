"""Contract: H-ROLL dual-gate + L_eff≫W + active≤W+S."""

from __future__ import annotations

from roll_ctx import compress_token_ids, iter_roll_segments
from roll_ops import (
    EPS_LP,
    MIN_LEFF_RATIO,
    MIN_UNIQUE,
    ROLL_S,
    ROLL_TARGET,
    ROLL_W,
    decide_hroll,
)


def test_given_constants_when_read_then_leff_beats_w() -> None:
    assert ROLL_W == 128
    assert ROLL_S == 32
    assert ROLL_TARGET == 384
    assert ROLL_TARGET >= MIN_LEFF_RATIO * ROLL_W


def test_given_long_ids_when_compress_then_budget_s() -> None:
    ids = list(range(200))
    out = compress_token_ids(ids, ROLL_S)
    assert len(out) == ROLL_S
    assert out[0] == 0
    assert out[-1] == 199


def test_given_ids_when_roll_then_active_bounded() -> None:
    ids = list(range(ROLL_TARGET))
    segs = iter_roll_segments(ids, w=ROLL_W, s=ROLL_S)
    assert len(segs) == 3
    assert segs[0]["summary_len"] == 0
    assert segs[0]["active_len"] == ROLL_W
    for seg in segs:
        assert seg["active_len"] <= ROLL_W + ROLL_S
        assert seg["l_eff"] == ROLL_TARGET


def test_given_code_up_when_decide_then_promote() -> None:
    d = decide_hroll(
        parent_story=-10.0,
        parent_code=-16.0,
        roll_story=-9.9,
        roll_code=-14.0,
        mean_unique=MIN_UNIQUE + 0.1,
        mean_elig=1.0,
        mean_switch=0.4,
        l_eff=float(ROLL_TARGET),
        mean_active=float(ROLL_W + ROLL_S),
        identical=False,
    )
    assert d.startswith("PROMOTE")
    assert "ROLL" in d
    assert "L_eff=384" in d
    assert "active=160" in d


def test_given_short_leff_when_decide_then_kill() -> None:
    d = decide_hroll(
        parent_story=-10.0,
        parent_code=-16.0,
        roll_story=-9.5,
        roll_code=-10.0,
        mean_unique=2.0,
        mean_elig=1.0,
        mean_switch=0.5,
        l_eff=float(ROLL_W),
        mean_active=float(ROLL_W),
        identical=False,
    )
    assert d.startswith("KILL")
    assert "L_eff" in d


def test_given_active_too_big_when_decide_then_kill() -> None:
    d = decide_hroll(
        parent_story=-10.0,
        parent_code=-16.0,
        roll_story=-9.5,
        roll_code=-10.0,
        mean_unique=2.0,
        mean_elig=1.0,
        mean_switch=0.5,
        l_eff=float(ROLL_TARGET),
        mean_active=float(ROLL_W + ROLL_S + 10),
        identical=False,
    )
    assert d.startswith("KILL")
    assert "active" in d or "O(W)" in d


def test_given_story_drop_when_decide_then_kill() -> None:
    d = decide_hroll(
        parent_story=-10.0,
        parent_code=-16.0,
        roll_story=-10.0 - EPS_LP - 0.2,
        roll_code=-10.0,
        mean_unique=2.0,
        mean_elig=1.0,
        mean_switch=0.5,
        l_eff=float(ROLL_TARGET),
        mean_active=float(ROLL_W),
        identical=False,
    )
    assert d.startswith("KILL")
    assert "story_lp" in d
