"""
Contract: H-DECM must beat H-LAT2 and B4; MIX_M ≥ 2.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from decm_ops import MIX_M, best_index, decide_hdecm


def test_given_mix_m_when_defined_then_at_least_two():
    assert MIX_M >= 2


def test_given_scores_when_best_index_then_argmax():
    assert best_index([0.1, 0.9, 0.2]) == 1


def test_given_beats_both_when_decide_then_promote():
    stats = {
        "B4": {"mean_lp": -17.0, "mean_wall": 50.0},
        "H-LAT2": {"mean_lp": -16.5, "mean_wall": 40.0},
    }
    s = {"mean_lp": -16.0, "mean_wall": 55.0}
    assert decide_hdecm(s, stats).startswith("PROMOTE")


def test_given_leq_lat2_when_decide_then_kill():
    stats = {
        "B4": {"mean_lp": -17.0, "mean_wall": 50.0},
        "H-LAT2": {"mean_lp": -16.0, "mean_wall": 40.0},
    }
    s = {"mean_lp": -16.0, "mean_wall": 55.0}
    assert "≤ H-LAT2" in decide_hdecm(s, stats)


def test_given_leq_b4_when_decide_then_kill():
    stats = {
        "B4": {"mean_lp": -16.0, "mean_wall": 50.0},
        "H-LAT2": {"mean_lp": -17.0, "mean_wall": 40.0},
    }
    s = {"mean_lp": -16.0, "mean_wall": 55.0}
    assert "≤ B4" in decide_hdecm(s, stats)


def test_given_dup_genes_when_elite_then_unique_capped():
    from decm_search import elite_mixture

    g = {
        "temperature": 0.8,
        "top_p": 0.9,
        "n": 2,
        "k": 2,
        "block": 1,
        "horizon": 2,
        "use_mae": False,
    }
    mix = elite_mixture([g, dict(g), dict(g)], [3.0, 2.0, 1.0], m=3)
    assert len(mix) == 1
