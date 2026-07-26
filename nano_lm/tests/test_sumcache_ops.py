"""Contract: H-SUMCACHE dual-gate + L_eff≥512 + wall < full-prefill."""

from __future__ import annotations

from sumcache_ctx import build_sumcache_ids, clip_full_ids
from sumcache_ops import (
    ACTIVE_CAP,
    EPS_LP,
    MIN_LEFF,
    MIN_UNIQUE,
    SUMCACHE_S_COARSE,
    SUMCACHE_S_FINE,
    SUMCACHE_TARGET,
    SUMCACHE_W,
    decide_hsumcache,
)


def test_given_constants_when_read_then_budgets_ok() -> None:
    assert SUMCACHE_TARGET >= MIN_LEFF
    assert ACTIVE_CAP == SUMCACHE_S_COARSE + SUMCACHE_S_FINE + SUMCACHE_W
    assert ACTIVE_CAP + 32 <= 512
    from sumcache_ops import FULL_PREFILL_CAP

    assert FULL_PREFILL_CAP + 32 <= 512


def test_given_long_ids_when_build_then_active_bounded() -> None:
    ids = list(range(SUMCACHE_TARGET))
    built = build_sumcache_ids(ids)
    assert built["l_eff"] == SUMCACHE_TARGET
    assert built["active_len"] <= ACTIVE_CAP
    assert built["tail_len"] == SUMCACHE_W
    from sumcache_ops import FULL_PREFILL_CAP

    assert len(clip_full_ids(ids)) == FULL_PREFILL_CAP


def test_given_code_up_wall_down_when_decide_then_promote() -> None:
    d = decide_hsumcache(
        parent_story=-10.0,
        parent_code=-16.0,
        sum_story=-9.9,
        sum_code=-14.0,
        mean_unique=MIN_UNIQUE + 0.1,
        mean_elig=1.0,
        mean_switch=0.4,
        l_eff=float(SUMCACHE_TARGET),
        mean_active=float(ACTIVE_CAP),
        wall_sum=40.0,
        wall_full=80.0,
        identical=False,
    )
    assert d.startswith("PROMOTE")
    assert "SUMCACHE" in d
    assert "wall=40" in d


def test_given_wall_within_slack_when_decide_then_promote() -> None:
    from sumcache_ops import WALL_SLACK_MS

    d = decide_hsumcache(
        parent_story=-10.0,
        parent_code=-16.0,
        sum_story=-9.5,
        sum_code=-10.0,
        mean_unique=2.0,
        mean_elig=1.0,
        mean_switch=0.5,
        l_eff=float(SUMCACHE_TARGET),
        mean_active=200.0,
        wall_sum=44.0,
        wall_full=43.0,
        identical=False,
    )
    assert d.startswith("PROMOTE")
    assert WALL_SLACK_MS >= 1.0


def test_given_short_leff_when_decide_then_kill() -> None:
    d = decide_hsumcache(
        parent_story=-10.0,
        parent_code=-16.0,
        sum_story=-9.5,
        sum_code=-10.0,
        mean_unique=2.0,
        mean_elig=1.0,
        mean_switch=0.5,
        l_eff=256.0,
        mean_active=200.0,
        wall_sum=40.0,
        wall_full=80.0,
        identical=False,
    )
    assert d.startswith("KILL")
    assert "L_eff" in d


def test_given_wall_not_down_when_decide_then_kill() -> None:
    from sumcache_ops import WALL_SLACK_MS

    d = decide_hsumcache(
        parent_story=-10.0,
        parent_code=-16.0,
        sum_story=-9.5,
        sum_code=-10.0,
        mean_unique=2.0,
        mean_elig=1.0,
        mean_switch=0.5,
        l_eff=float(SUMCACHE_TARGET),
        mean_active=200.0,
        wall_sum=90.0,
        wall_full=80.0,
        identical=False,
    )
    assert d.startswith("KILL")
    assert "wall_sum" in d or "full-prefill" in d
    assert WALL_SLACK_MS < 10.0


def test_given_story_drop_when_decide_then_kill() -> None:
    d = decide_hsumcache(
        parent_story=-10.0,
        parent_code=-16.0,
        sum_story=-10.0 - EPS_LP - 0.2,
        sum_code=-10.0,
        mean_unique=2.0,
        mean_elig=1.0,
        mean_switch=0.5,
        l_eff=float(SUMCACHE_TARGET),
        mean_active=200.0,
        wall_sum=40.0,
        wall_full=80.0,
        identical=False,
    )
    assert d.startswith("KILL")
    assert "story_lp" in d
