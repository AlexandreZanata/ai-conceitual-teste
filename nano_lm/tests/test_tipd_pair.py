"""Contract: H-TIPD CPU thread tuner leaves headroom."""

from __future__ import annotations

from tipd_ops import tip_outcome
from tipd_pair import tune_cpu_threads


def test_given_cpu_count_when_tune_then_leaves_headroom() -> None:
    import os

    cpus = int(os.cpu_count() or 4)
    use = tune_cpu_threads()
    assert 4 <= use <= cpus
    if cpus > 8:
        assert use <= cpus - 4


def test_given_explicit_n_when_tune_then_caps() -> None:
    import os

    cpus = int(os.cpu_count() or 4)
    assert tune_cpu_threads(1) == 1
    assert tune_cpu_threads(10_000) == cpus


def test_given_promote_when_tip_outcome_then_stag_prime() -> None:
    assert tip_outcome("PROMOTE (x)") == "STAG_PRIME"
    assert tip_outcome("KILL (y)") == "UTIL"
