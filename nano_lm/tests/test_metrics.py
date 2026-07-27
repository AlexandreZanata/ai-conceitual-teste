"""Contract: Wave AS5 H-METRICS — latency tetrad(+ABSTAIN) + KB refresh."""

from __future__ import annotations

from metrics_ops import (
    ABSTAIN_N,
    DECODE_N,
    FASTBASE_HOT_WALL_MS,
    LOOKUP_N,
    METRICS_ID,
    METRICS_PATHS,
    METRICS_PROTOCOL,
    METRICS_THESIS,
    PEAK_N,
    PRODUCT_HOLES,
    decide_metrics,
    kb_gate_ok,
    path_latency_stats,
    peak_regressed,
    percentile,
    protocol_ok,
    telemetry_rules_ok,
)


def test_given_contract_when_constants_then_match_as5() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AS5 — publish tetrad · holes explicit
    assert METRICS_ID == "H-METRICS"
    assert METRICS_PATHS == ("LOOKUP", "PEAK", "DECODE", "ABSTAIN")
    assert LOOKUP_N == 64 and PEAK_N == 256
    assert DECODE_N == 12 and ABSTAIN_N == 32
    assert FASTBASE_HOT_WALL_MS > 0.0
    assert protocol_ok() is True
    assert "p50_wall_ms" in METRICS_PROTOCOL["metrics"]
    assert "ABSTAIN" in METRICS_THESIS or "holes" in METRICS_THESIS
    assert len(PRODUCT_HOLES) >= 1


def test_given_walls_when_stats_then_p50_p99() -> None:
    walls = [float(i) for i in range(1, 101)]
    st = path_latency_stats(walls)
    assert st["n"] == 100
    assert st["p50_wall_ms"] == percentile(walls, 50)
    assert st["p99_wall_ms"] == percentile(walls, 99)


def test_given_lookup_modes_when_telemetry_then_ok() -> None:
    assert telemetry_rules_ok(
        path="LOOKUP",
        walls=[0.0, 0.0],
        n_news=[0, 0],
        modes=["WRAP_LOOKUP", "SEMWRAP_LOOKUP"],
        product_modes=["LOOKUP", "LOOKUP"],
    )


def test_given_abstain_modes_when_telemetry_then_ok() -> None:
    assert telemetry_rules_ok(
        path="ABSTAIN",
        walls=[10.0, 12.0],
        n_news=[64, 64],
        modes=["NO_ANSWER", "NO_ANSWER"],
        product_modes=["ABSTAIN", "ABSTAIN"],
    )


def test_given_decode_zero_wall_when_telemetry_then_false() -> None:
    assert (
        telemetry_rules_ok(
            path="DECODE",
            walls=[0.0],
            n_news=[1],
            modes=["WRAP_DECODE"],
            product_modes=["DECODE"],
        )
        is False
    )


def test_given_snap_when_kb_gate_then_ok() -> None:
    snap = {
        "coverage_pct": 100.0,
        "complete_claim_forbidden": True,
        "holes": list(PRODUCT_HOLES),
    }
    assert kb_gate_ok(snap) is True
    bad = dict(snap)
    bad["holes"] = []
    assert kb_gate_ok(bad) is False


def test_given_stats_when_publish_then_promote() -> None:
    paths = {
        name: {"p50_wall_ms": 1.0, "p99_wall_ms": 2.0}
        for name in METRICS_PATHS
    }
    paths["PEAK"] = {
        "p50_wall_ms": FASTBASE_HOT_WALL_MS * 0.5,
        "p99_wall_ms": 1.0,
    }
    tel = {name: True for name in METRICS_PATHS}
    snap = {
        "coverage_pct": 100.0,
        "complete_claim_forbidden": True,
        "holes": list(PRODUCT_HOLES),
    }
    assert (
        decide_metrics(
            paths=paths,
            telemetry_ok=tel,
            regress_noted=True,
            snap=snap,
        )
        == "PROMOTE"
    )


def test_given_broken_telemetry_when_decide_then_kill() -> None:
    paths = {
        name: {"p50_wall_ms": 1.0, "p99_wall_ms": 2.0}
        for name in METRICS_PATHS
    }
    tel = {name: True for name in METRICS_PATHS}
    tel["ABSTAIN"] = False
    snap = {
        "coverage_pct": 100.0,
        "complete_claim_forbidden": True,
        "holes": list(PRODUCT_HOLES),
    }
    out = decide_metrics(
        paths=paths, telemetry_ok=tel, regress_noted=True, snap=snap
    )
    assert out.startswith("KILL")


def test_given_peak_slow_when_regress_helper_then_true() -> None:
    assert peak_regressed(FASTBASE_HOT_WALL_MS + 1.0) is True
