"""Contract: DEPL-Y freeze routes (128 vs long + HITL honesty)."""

from __future__ import annotations

from depl_y_ops import (
    DEPL_Y_EVIDENCE,
    DEPL_Y_FORBIDDEN,
    DEPL_Y_GOALS,
    DEPL_Y_ID,
    DEPL_Y_ROUTES,
    choose_depl_y,
    decide_depl_y,
    reject_forbidden,
    route_table,
)


def test_given_code_128_when_choose_then_qpfb2_caches() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8 #4 — 128→QPFB2+caches
    out = choose_depl_y("code_128")
    assert "QPFB2" in out
    assert "BEAMKV" in out


def test_given_long_when_choose_then_roll_family() -> None:
    out = choose_depl_y("long_ctx")
    assert "ROLL" in out
    assert "SUMCACHE" in out
    assert "GPFB4-LONG" in out


def test_given_hitl_when_choose_then_wrap() -> None:
    out = choose_depl_y("hitl_known")
    assert "wrap" in out.lower()
    assert "H-ZWRAP" in out


def test_given_L_mismatch_when_choose_then_reject() -> None:
    assert choose_depl_y("code_128", L=256).startswith("REJECT")
    assert choose_depl_y("long_ctx", L=128).startswith("REJECT")
    assert choose_depl_y("speed_128", L=512).startswith("REJECT")


def test_given_stream_when_forbidden_then_true() -> None:
    assert reject_forbidden("STREAM") is True
    assert reject_forbidden("H-STREAM") is True
    assert reject_forbidden("H-ABS-QPFB2") is False


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in DEPL_Y_EVIDENCE}
    out = decide_depl_y(ok)
    assert out.startswith("PROMOTE")
    assert DEPL_Y_ID in out


def test_given_missing_evidence_when_decide_then_kill() -> None:
    ok = {p: True for p in DEPL_Y_EVIDENCE}
    ok[DEPL_Y_EVIDENCE[0]] = False
    out = decide_depl_y(ok)
    assert out.startswith("KILL")
    assert DEPL_Y_EVIDENCE[0] in out


def test_given_constants_when_loaded_then_match_pesquisa() -> None:
    assert "code_128" in DEPL_Y_GOALS
    assert "long_ctx" in DEPL_Y_GOALS
    assert "STREAM" in DEPL_Y_FORBIDDEN
    assert "KVCACHE-Q" in DEPL_Y_FORBIDDEN
    assert "GENCACHE" in DEPL_Y_FORBIDDEN
    assert len(route_table()) == len(DEPL_Y_ROUTES)
