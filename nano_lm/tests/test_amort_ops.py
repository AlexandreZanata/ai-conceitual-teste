"""Contract: H-AMORT amortized cache e2e vs live STAG."""

from __future__ import annotations

import pytest

from amort_ops import amortized_e2e, decide_hamort


def test_given_four_runs_when_amortize_then_cache_split() -> None:
    # cache=0.64, trains=1.73 → amort = 0.16+1.73 = 1.89 < live 2.28
    assert amortized_e2e(0.64, [1.73, 1.73, 1.73, 1.73]) == pytest.approx(1.89)


def test_given_empty_trains_when_amortize_then_raises() -> None:
    with pytest.raises(ValueError, match="≥1"):
        amortized_e2e(0.1, [])


def test_given_amort_win_when_decide_then_promote() -> None:
    assert decide_hamort(
        amort_e2e=1.89,
        live_e2e=2.28,
        amort_lp=-12.5,
        live_lp=-13.3,
        n_runs=4,
    ).startswith("PROMOTE")


def test_given_e2e_no_win_when_decide_then_kill() -> None:
    out = decide_hamort(
        amort_e2e=2.40,
        live_e2e=2.28,
        amort_lp=-12.5,
        live_lp=-13.3,
        n_runs=4,
    )
    assert "amortized e2e" in out


def test_given_quality_drop_when_decide_then_kill() -> None:
    out = decide_hamort(
        amort_e2e=1.5,
        live_e2e=2.28,
        amort_lp=-13.4,
        live_lp=-13.3,
        n_runs=4,
    )
    assert "quality drop" in out


def test_given_single_run_matches_etrain_tax() -> None:
    # N=1 → cache+train (ETRAIN-shaped); may lose formally
    assert amortized_e2e(0.64, [1.73]) == pytest.approx(2.37)
