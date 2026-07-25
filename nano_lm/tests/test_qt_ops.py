"""Contract: H-QT dual-gate (lp ≥ parent−ε; wall↓ or mem↓)."""

from __future__ import annotations

from qt_ops import EPS_LP, decide_hqt


def _m(story: float, wall: float, nbytes: float) -> dict[str, float]:
    return {
        "mean_story_lp": story,
        "mean_wall_ms": wall,
        "weight_bytes": nbytes,
    }


def test_given_lp_ok_mem_down_when_decide_then_promote() -> None:
    out = decide_hqt(
        parent=_m(-10.0, 20.0, 1_000_000),
        qt=_m(-10.02, 21.0, 800_000),
        n_rows=4,
    )
    assert out.startswith("PROMOTE")
    assert "mem↓" in out


def test_given_lp_ok_wall_down_when_decide_then_promote() -> None:
    out = decide_hqt(
        parent=_m(-10.0, 20.0, 1_000_000),
        qt=_m(-10.0, 15.0, 1_000_000),
        n_rows=4,
    )
    assert out.startswith("PROMOTE")
    assert "wall↓" in out


def test_given_lp_drop_when_decide_then_kill() -> None:
    out = decide_hqt(
        parent=_m(-10.0, 20.0, 1_000_000),
        qt=_m(-10.0 - EPS_LP - 0.1, 10.0, 500_000),
        n_rows=4,
    )
    assert out.startswith("KILL")
    assert "lp" in out


def test_given_no_efficiency_when_decide_then_kill() -> None:
    out = decide_hqt(
        parent=_m(-10.0, 20.0, 1_000_000),
        qt=_m(-9.9, 25.0, 1_100_000),
        n_rows=4,
    )
    assert out.startswith("KILL")
    assert "wall" in out.lower() or "weight" in out.lower()


def test_given_no_rows_when_decide_then_kill() -> None:
    out = decide_hqt(
        parent=_m(-10.0, 20.0, 1_000_000),
        qt=_m(-10.0, 15.0, 800_000),
        n_rows=0,
    )
    assert out.startswith("KILL")
