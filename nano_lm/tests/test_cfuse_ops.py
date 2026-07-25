"""Contract: H-CFUSE protocol gate vs EARLY / CHUNK / FUSE (never tip)."""

from __future__ import annotations

from cfuse_ops import decide_hcfuse


def test_given_cfuse_when_decide_then_protocol_or_kill() -> None:
    # GIVEN controls WHEN cfuse beats min(CHUNK,FUSE) wall with quality THEN PROTOCOL
    stats = {
        "H-EARLY": {"mean_lp": -16.0, "mean_wall": 100.0},
        "H-CHUNK": {"mean_lp": -16.0, "mean_wall": 55.0},
        "H-FUSE": {"mean_lp": -16.0, "mean_wall": 60.0},
    }
    out = decide_hcfuse({"mean_lp": -16.0, "mean_wall": 50.0}, stats)
    assert out.startswith("PROTOCOL")
    assert "tip" in out
    assert "PROMOTE" not in out


def test_given_quality_drop_when_decide_then_kill() -> None:
    stats = {
        "H-EARLY": {"mean_lp": -16.0, "mean_wall": 100.0},
        "H-CHUNK": {"mean_lp": -16.0, "mean_wall": 55.0},
        "H-FUSE": {"mean_lp": -16.0, "mean_wall": 60.0},
    }
    assert "quality" in decide_hcfuse(
        {"mean_lp": -16.2, "mean_wall": 40.0}, stats
    )


def test_given_no_stack_win_when_decide_then_kill() -> None:
    stats = {
        "H-EARLY": {"mean_lp": -16.0, "mean_wall": 100.0},
        "H-CHUNK": {"mean_lp": -16.0, "mean_wall": 55.0},
        "H-FUSE": {"mean_lp": -16.0, "mean_wall": 60.0},
    }
    assert "min(CHUNK,FUSE)" in decide_hcfuse(
        {"mean_lp": -15.9, "mean_wall": 55.0}, stats
    )


def test_given_missing_control_when_decide_then_needs() -> None:
    assert decide_hcfuse({}, {}).startswith("needs H-EARLY")
    assert decide_hcfuse(
        {}, {"H-EARLY": {"mean_lp": -1.0, "mean_wall": 1.0}}
    ).startswith("needs H-CHUNK")
    assert decide_hcfuse(
        {},
        {
            "H-EARLY": {"mean_lp": -1.0, "mean_wall": 1.0},
            "H-CHUNK": {"mean_lp": -1.0, "mean_wall": 1.0},
        },
    ).startswith("needs H-FUSE")
