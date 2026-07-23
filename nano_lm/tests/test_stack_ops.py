"""
Contract: H-STACK dual gate vs H-EARLY and H-DECM tips.
"""

from __future__ import annotations

from early_ops import clamp_early_gene
from stack_ops import decide_hstack, early_gene_key
from stack_search import elite_early_mixture


def test_given_dual_win_when_decide_then_promote():
    stats = {
        "H-EARLY": {"mean_lp": -12.0, "mean_wall": 50.0},
        "H-DECM": {"mean_lp": -11.5, "mean_wall": 200.0},
    }
    s = {"mean_lp": -11.4, "mean_wall": 40.0}
    assert decide_hstack(s, stats) == "PROMOTE (dual win vs tips)"


def test_given_quality_short_when_decide_then_kill():
    stats = {
        "H-EARLY": {"mean_lp": -12.0, "mean_wall": 50.0},
        "H-DECM": {"mean_lp": -11.5, "mean_wall": 200.0},
    }
    s = {"mean_lp": -12.0, "mean_wall": 40.0}
    assert decide_hstack(s, stats) == "KILL (≤ max tip quality)"


def test_given_no_wall_win_when_decide_then_kill():
    stats = {
        "H-EARLY": {"mean_lp": -12.0, "mean_wall": 50.0},
        "H-DECM": {"mean_lp": -11.5, "mean_wall": 200.0},
    }
    s = {"mean_lp": -11.4, "mean_wall": 55.0}
    assert decide_hstack(s, stats) == "KILL (no dual wall win)"


def test_given_missing_tip_when_decide_then_needs_controls():
    assert decide_hstack({"mean_lp": -11.0}, {}) == "needs H-EARLY+H-DECM controls"


def test_given_scored_pop_when_elite_then_unique_top_m():
    g0 = clamp_early_gene(
        {
            "min_new": 4,
            "patience": 1,
            "conf_threshold": 0.8,
            "n": 1,
            "temperature": 0.7,
            "top_p": 0.9,
        }
    )
    g1 = dict(g0)
    g1["temperature"] = 1.0
    g1 = clamp_early_gene(g1)
    dup = dict(g0)
    mix = elite_early_mixture([g0, g1, dup], [1.0, 2.0, 0.5], m=2)
    assert len(mix) == 2
    assert early_gene_key(mix[0]) == early_gene_key(g1)
