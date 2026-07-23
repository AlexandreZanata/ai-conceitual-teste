"""
Contract: decode genes clamp into bounds; mutate stays valid.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from decode_genes import BOUNDS, clamp_gene, default_bon_gene, mutate_gene


def test_given_out_of_range_when_clamp_then_within_bounds():
    raw = {
        "temperature": 9.0,
        "top_p": 0.1,
        "n": 99,
        "k": 0,
        "block": -3,
        "horizon": 100,
        "use_mae": 1,
    }
    g = clamp_gene(raw)
    for key, (lo, hi) in BOUNDS.items():
        assert lo <= g[key] <= hi
    assert g["use_mae"] is True


def test_given_gene_when_mutate_then_clamped_and_keys_preserved():
    rng = random.Random(0)
    base = default_bon_gene()
    mut = mutate_gene(base, rng)
    assert set(mut.keys()) == set(base.keys())
    for key, (lo, hi) in BOUNDS.items():
        assert lo <= mut[key] <= hi


def test_given_default_bon_when_built_then_matches_b4_smoke_knobs():
    g = default_bon_gene()
    assert g["temperature"] == 0.8
    assert g["top_p"] == 0.9
    assert g["n"] == 4
    assert g["use_mae"] is False
