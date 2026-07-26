"""Contract: Wave AG1 H-ANTIFP — LOOKUP ≠ generative IQ (pesquisa §5)."""

from __future__ import annotations

from antifp_ops import (
    ANTIFP_ID,
    ANTIFP_THESIS,
    LOOKUP_MODES,
    antifp_stats,
    classify_arm,
    decide_antifp,
    extract_telemetry,
    gen_arm_ok,
    intelligence_promote_allowed,
    lookup_arm_ok,
    score_antifp_completion,
)


def test_given_wrap_lookup_when_classify_then_lookup() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AG1 — LOOKUP labeled distinctly
    p = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    assert classify_arm(p) == "LOOKUP"
    assert lookup_arm_ok(p) is True
    assert gen_arm_ok(p) is False


def test_given_semwrap_when_classify_then_lookup() -> None:
    p = {"mode": "SEMWRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    assert p["mode"] in LOOKUP_MODES
    assert classify_arm(p) == "LOOKUP"


def test_given_decode_when_classify_then_generate() -> None:
    p = {"mode": "QT+EARLY n=1", "wall_ms": 12.5, "n_new": 8}
    assert classify_arm(p) == "GENERATE"
    assert gen_arm_ok(p) is True
    assert lookup_arm_ok(p) is False


def test_given_wrap_decode_when_wall_then_generate() -> None:
    p = {"mode": "WRAP_DECODE", "wall_ms": 40.0, "n_new": 16}
    assert classify_arm(p) == "GENERATE"
    assert gen_arm_ok(p) is True


def test_given_lookup_mode_with_wall_when_gen_ok_then_false() -> None:
    # LOOKUP label must never count as generative arm
    p = {"mode": "WRAP_LOOKUP", "wall_ms": 5.0, "n_new": 3}
    assert classify_arm(p) == "LOOKUP"
    assert gen_arm_ok(p) is False


def test_given_iq_claim_lookup_only_when_allowed_then_false() -> None:
    assert (
        intelligence_promote_allowed(
            lookup_logged=True,
            gen_logged=False,
            claim="smarter generative IQ from LOOKUP scores",
        )
        is False
    )


def test_given_iq_claim_dual_when_allowed_then_true() -> None:
    assert (
        intelligence_promote_allowed(
            lookup_logged=True,
            gen_logged=True,
            claim="smarter model with dual-arm evidence",
        )
        is True
    )


def test_given_product_lookup_claim_when_allowed_then_true() -> None:
    assert (
        intelligence_promote_allowed(
            lookup_logged=True,
            gen_logged=False,
            claim="scoped WRAP_LOOKUP product — not open chat",
        )
        is True
    )


def test_given_lookup_gold_match_when_score_then_labeled_not_iq() -> None:
    score, err, notes = score_antifp_completion(
        arm="LOOKUP", completion="gold", gold="gold"
    )
    assert score == 9.0 and err is False
    assert any("not generative IQ" in n for n in notes)


def test_given_gen_periods_when_score_then_error() -> None:
    score, err, notes = score_antifp_completion(
        arm="GENERATE", completion="........", gold="anything"
    )
    assert score == 1.0 and err is True
    assert notes


def test_given_ready_when_decide_then_promote() -> None:
    stats = antifp_stats(
        lookup_ok=True,
        gen_ok=True,
        arms_distinct=True,
        iq_gate_rejects_lookup_only=True,
        iq_gate_allows_dual=True,
        telemetry_complete=True,
        n_lookup_trials=1,
        n_gen_trials=1,
    )
    out = decide_antifp(stats)
    assert out.startswith("PROMOTE")
    assert ANTIFP_ID in out
    assert "LOOKUP" in ANTIFP_THESIS


def test_given_no_gen_when_decide_then_kill() -> None:
    stats = antifp_stats(
        lookup_ok=True,
        gen_ok=False,
        arms_distinct=True,
        iq_gate_rejects_lookup_only=True,
        iq_gate_allows_dual=True,
        telemetry_complete=True,
        n_lookup_trials=1,
        n_gen_trials=1,
    )
    out = decide_antifp(stats)
    assert out.startswith("KILL")
    assert "gen_ok" in out


def test_given_payload_when_extract_then_telemetry() -> None:
    tel = extract_telemetry(
        {"mode": "WRAP_LOOKUP", "wall_ms": "0", "n_new": "0"}
    )
    assert tel == {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
