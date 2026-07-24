"""Contract: H-SHORT draft stop + dual gate vs EARLY."""

from __future__ import annotations

import random
import unittest

from short_ops import (
    DRAFT_MAXS,
    STOP_CONFS,
    clamp_short_gene,
    decide_hshort,
    mutate_short_gene,
    random_short_gene,
    should_stop_after_draft,
)

TIP = {
    "n": 2,
    "temperature": 0.7,
    "top_p": 0.9,
    "min_new": 8,
    "conf_threshold": 0.85,
    "patience": 2,
}


class TestShortOps(unittest.TestCase):
    def test_stop_after_draft_high_conf(self) -> None:
        self.assertTrue(
            should_stop_after_draft(draft_done=True, max_p=0.9, stop_conf=0.7)
        )
        self.assertFalse(
            should_stop_after_draft(draft_done=True, max_p=0.5, stop_conf=0.7)
        )
        self.assertFalse(
            should_stop_after_draft(draft_done=False, max_p=0.99, stop_conf=0.7)
        )

    def test_clamp_and_mutate(self) -> None:
        g = clamp_short_gene({"draft_max": 9, "stop_conf": 0.72}, TIP)
        self.assertIn(g["draft_max"], DRAFT_MAXS)
        self.assertIn(g["stop_conf"], STOP_CONFS)
        self.assertEqual(g["n"], TIP["n"])
        rng = random.Random(0)
        m = mutate_short_gene(random_short_gene(rng, TIP), rng, TIP)
        self.assertIn(m["draft_max"], DRAFT_MAXS)

    def test_decide_promotes_on_wall_or_flop(self) -> None:
        tip = {"mean_lp": -11.83, "mean_wall": 65.0, "mean_gflops": 12.0}
        self.assertTrue(
            decide_hshort(
                {"mean_lp": -11.8, "mean_wall": 50.0, "mean_gflops": 10.0},
                {"H-EARLY": tip},
            ).startswith("PROMOTE")
        )
        self.assertTrue(
            decide_hshort(
                {"mean_lp": -12.0, "mean_wall": 50.0, "mean_gflops": 10.0},
                {"H-EARLY": tip},
            ).startswith("KILL")
        )
        self.assertTrue(
            decide_hshort(
                {"mean_lp": -11.8, "mean_wall": 70.0, "mean_gflops": 12.0},
                {"H-EARLY": tip},
            ).startswith("KILL")
        )


if __name__ == "__main__":
    unittest.main()
