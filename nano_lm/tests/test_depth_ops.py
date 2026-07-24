"""Contract: H-DEPTH shallow student + dual gate vs STAG."""

from __future__ import annotations

from depth_ops import DEPTH_LAYERS, TIP_LAYERS, decide_hdepth
from student_model import (
    build_depth_student,
    build_student,
    count_params,
    depth_student_config,
)


def test_given_depth_cfg_when_build_then_one_fewer_layer() -> None:
    # GIVEN tip layers=2 WHEN depth config THEN layers=1 and fewer params
    assert TIP_LAYERS == 2
    assert DEPTH_LAYERS == 1
    assert depth_student_config().num_layers == DEPTH_LAYERS
    tip = build_student()
    depth = build_depth_student()
    assert tip.config.num_layers == TIP_LAYERS
    assert depth.config.num_layers == DEPTH_LAYERS
    assert count_params(depth) < count_params(tip)


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_wall": 70.0}
    stats = {"H-STAG": tip}
    assert decide_hdepth(
        {"mean_lp": -16.0, "mean_wall": 60.0}, stats
    ).startswith("PROMOTE")
    assert "quality" in decide_hdepth(
        {"mean_lp": -16.2, "mean_wall": 50.0}, stats
    )
    assert "wall" in decide_hdepth(
        {"mean_lp": -15.9, "mean_wall": 70.0}, stats
    )
