"""Contract: H-FUSE protocol gate vs EARLY / FLASH / KVSEL (never tip)."""

from __future__ import annotations

from fuse_ops import decide_hfuse


def test_given_fuse_when_decide_then_protocol_or_kill() -> None:
    # GIVEN controls WHEN fuse beats min(FLASH,KVSEL) wall with quality THEN PROTOCOL
    stats = {
        "H-EARLY": {"mean_lp": -16.0, "mean_wall": 100.0},
        "H-FLASH": {"mean_lp": -16.0, "mean_wall": 60.0},
        "H-KVSEL": {"mean_lp": -16.0, "mean_wall": 70.0},
    }
    out = decide_hfuse({"mean_lp": -16.0, "mean_wall": 50.0}, stats)
    assert out.startswith("PROTOCOL")
    assert "tip" in out
    assert "PROMOTE" not in out


def test_given_quality_drop_when_decide_then_kill() -> None:
    stats = {
        "H-EARLY": {"mean_lp": -16.0, "mean_wall": 100.0},
        "H-FLASH": {"mean_lp": -16.0, "mean_wall": 60.0},
        "H-KVSEL": {"mean_lp": -16.0, "mean_wall": 70.0},
    }
    assert "quality" in decide_hfuse(
        {"mean_lp": -16.2, "mean_wall": 40.0}, stats
    )


def test_given_no_stack_win_when_decide_then_kill() -> None:
    stats = {
        "H-EARLY": {"mean_lp": -16.0, "mean_wall": 100.0},
        "H-FLASH": {"mean_lp": -16.0, "mean_wall": 60.0},
        "H-KVSEL": {"mean_lp": -16.0, "mean_wall": 70.0},
    }
    assert "min(FLASH,KVSEL)" in decide_hfuse(
        {"mean_lp": -15.9, "mean_wall": 60.0}, stats
    )


def test_given_missing_control_when_decide_then_needs() -> None:
    assert decide_hfuse({}, {}).startswith("needs H-EARLY")
    assert decide_hfuse(
        {}, {"H-EARLY": {"mean_lp": -1.0, "mean_wall": 1.0}}
    ).startswith("needs H-FLASH")
