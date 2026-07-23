"""
Contract: H-DECQ snaps to codebook; must beat H-DECM and B4 to promote.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from decq_ops import (
    TEMP_LEVELS,
    TOP_P_LEVELS,
    decide_hdecq,
    mutate_gene_decq,
    quantize_gene,
    random_gene_decq,
)


def test_given_raw_when_quantize_then_levels_and_n_le_2():
    g = quantize_gene(
        {
            "temperature": 0.85,
            "top_p": 0.88,
            "n": 5,
            "k": 3,
            "block": 2,
            "horizon": 2,
            "use_mae": False,
        }
    )
    assert g["temperature"] in TEMP_LEVELS
    assert g["top_p"] in TOP_P_LEVELS
    assert 1 <= g["n"] <= 2


def test_given_random_mutate_when_decq_then_stays_on_codebook():
    rng = random.Random(0)
    g = random_gene_decq(rng)
    for _ in range(15):
        g = mutate_gene_decq(g, rng)
        assert g["temperature"] in TEMP_LEVELS
        assert g["top_p"] in TOP_P_LEVELS
        assert 1 <= g["n"] <= 2


def test_given_beats_both_when_decide_then_promote():
    stats = {
        "B4": {"mean_lp": -17.0, "mean_wall": 50.0},
        "H-DECM": {"mean_lp": -16.5, "mean_wall": 200.0},
    }
    s = {"mean_lp": -16.0, "mean_wall": 180.0}
    assert decide_hdecq(s, stats).startswith("PROMOTE")


def test_given_leq_decm_when_decide_then_kill():
    stats = {
        "B4": {"mean_lp": -17.0, "mean_wall": 50.0},
        "H-DECM": {"mean_lp": -16.0, "mean_wall": 200.0},
    }
    s = {"mean_lp": -16.0, "mean_wall": 180.0}
    assert "≤ H-DECM" in decide_hdecq(s, stats)


def test_given_leq_b4_when_decide_then_kill():
    stats = {
        "B4": {"mean_lp": -16.0, "mean_wall": 50.0},
        "H-DECM": {"mean_lp": -17.0, "mean_wall": 200.0},
    }
    s = {"mean_lp": -16.0, "mean_wall": 180.0}
    assert "≤ B4" in decide_hdecq(s, stats)
