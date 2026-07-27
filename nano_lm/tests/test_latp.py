"""Contract: Wave AQ3 H-LATP — latency triad p50/p99 (pesquisa §5)."""

from __future__ import annotations

from latp_ops import (
    DECODE_N,
    FASTBASE_HOT_WALL_MS,
    LATP_ID,
    LATP_PATHS,
    LATP_THESIS,
    LOOKUP_N,
    PEAK_N,
    decide_latp,
    path_latency_stats,
    peak_regressed,
    percentile,
    telemetry_rules_ok,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AQ3 — publish p50/p99 · no silent regress
    assert LATP_ID == "H-LATP"
    assert LATP_PATHS == ("LOOKUP", "PEAK", "DECODE")
    assert LOOKUP_N == 64 and PEAK_N == 256 and DECODE_N == 12
    assert FASTBASE_HOT_WALL_MS > 0.0
    assert "p50" in LATP_THESIS or "FASTBASE" in LATP_THESIS


def test_given_values_when_percentile_then_interpolates() -> None:
    xs = [1.0, 2.0, 3.0, 4.0]
    assert percentile(xs, 0) == 1.0
    assert percentile(xs, 100) == 4.0
    assert percentile(xs, 50) == 2.5


def test_given_walls_when_stats_then_p50_p99() -> None:
    walls = [float(i) for i in range(1, 101)]
    st = path_latency_stats(walls)
    assert st["n"] == 100
    assert st["p50_wall_ms"] == 50.5
    assert float(st["p99_wall_ms"]) >= 99.0


def test_given_lookup_when_telemetry_then_ok_at_zero() -> None:
    assert telemetry_rules_ok(
        path="LOOKUP",
        walls=[0.0, 0.0],
        n_news=[0, 0],
        modes=["WRAP_LOOKUP", "SEMWRAP_LOOKUP"],
    )


def test_given_peak_when_wall_zero_then_fail() -> None:
    assert not telemetry_rules_ok(
        path="PEAK",
        walls=[0.0, 0.1],
        n_news=[1, 1],
        modes=["PEAK_FAST+GENBASE", "PEAK_FAST+GENBASE"],
    )


def test_given_decode_when_n_new_zero_then_fail() -> None:
    assert not telemetry_rules_ok(
        path="DECODE",
        walls=[10.0, 12.0],
        n_news=[0, 8],
        modes=["QT+EARLY n=1", "QT+EARLY n=1"],
    )


def test_given_peak_when_faster_then_no_regress() -> None:
    assert peak_regressed(0.04) is False
    assert peak_regressed(0.10) is True


def test_given_published_when_decide_then_promote() -> None:
    paths = {
        "LOOKUP": {"p50_wall_ms": 0.0, "p99_wall_ms": 0.0},
        "PEAK": {"p50_wall_ms": 0.04, "p99_wall_ms": 0.06},
        "DECODE": {"p50_wall_ms": 150.0, "p99_wall_ms": 200.0},
    }
    tel = {"LOOKUP": True, "PEAK": True, "DECODE": True}
    assert decide_latp(paths=paths, telemetry_ok=tel, regress_noted=True) == (
        "PROMOTE"
    )


def test_given_regress_without_note_when_decide_then_kill() -> None:
    paths = {
        "LOOKUP": {"p50_wall_ms": 0.0, "p99_wall_ms": 0.0},
        "PEAK": {"p50_wall_ms": 0.20, "p99_wall_ms": 0.30},
        "DECODE": {"p50_wall_ms": 150.0, "p99_wall_ms": 200.0},
    }
    tel = {"LOOKUP": True, "PEAK": True, "DECODE": True}
    out = decide_latp(paths=paths, telemetry_ok=tel, regress_noted=False)
    assert out.startswith("KILL")
