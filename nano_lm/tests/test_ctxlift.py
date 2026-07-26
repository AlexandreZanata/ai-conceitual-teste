"""Contract: Wave AH2 H-CTXLIFT — penta-doc dual-arm (pesquisa §5)."""

from __future__ import annotations

from ctxlift_ops import (
    CTXREAL_MEAN_LEFF,
    CTXLIFT_ID,
    CTXLIFT_N,
    CTXLIFT_QUATERNARY,
    CTXLIFT_QUINARY,
    CTXLIFT_SECONDARY,
    CTXLIFT_TERTIARY,
    MIN_GEN_USABLE,
    MIN_LOOKUP_USABLE,
    MIN_SOURCES,
    TOP_K_SLICES_LIFT,
    ctxlift_doc_meta,
    ctxlift_stats,
    decide_ctxlift,
    quaternary_for,
    quinary_for,
    score_ctxlift_gen,
    score_ctxlift_lookup,
    secondary_for,
    tertiary_for,
)
from ctxreal_ops import TOP_K_SLICES_REAL


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AH2 H-CTXLIFT
    assert CTXLIFT_ID == "H-CTXLIFT"
    assert CTXLIFT_N == 10
    assert MIN_LOOKUP_USABLE == 7
    assert MIN_GEN_USABLE == 5
    assert MIN_SOURCES == 5
    assert TOP_K_SLICES_LIFT == 11
    assert TOP_K_SLICES_LIFT > TOP_K_SLICES_REAL
    assert CTXREAL_MEAN_LEFF == 93975.0


def test_given_ah0_sources_when_pair_then_all_mapped_distinct() -> None:
    from ah_session_ops import AH0_PACK

    for item in AH0_PACK:
        primary = item["source_id"]
        sec = secondary_for(primary)
        ter = tertiary_for(primary)
        quat = quaternary_for(primary)
        quin = quinary_for(primary)
        assert len({primary, sec, ter, quat, quin}) == 5
        assert CTXLIFT_SECONDARY[primary] == sec
        assert CTXLIFT_TERTIARY[primary] == ter
        assert CTXLIFT_QUATERNARY[primary] == quat
        assert CTXLIFT_QUINARY[primary] == quin


def test_given_penta_docs_when_meta_then_multi_source_and_deeper_k() -> None:
    primary = list(range(1500))
    secondary = list(range(2000, 3500))
    tertiary = list(range(4000, 5500))
    quaternary = list(range(6000, 7500))
    quinary = list(range(8000, 9500))
    q = [10, 20, 400, 800]
    meta = ctxlift_doc_meta(
        primary,
        secondary,
        tertiary,
        quaternary,
        quinary,
        q,
        primary_source="a",
        secondary_source="b",
        tertiary_source="c",
        quaternary_source="d",
        quinary_source="e",
    )
    assert meta["n_sources"] == 5
    assert meta["multi_source"] is True
    assert meta["k_slices"] == TOP_K_SLICES_LIFT
    assert meta["n_slices"] == TOP_K_SLICES_LIFT * 5
    assert meta["l_eff"] == 1500 * 5
    assert meta["deeper_than_ctxreal_k"] is True
    assert meta["above_ctxreal_leff"] is False  # 7500 < 93975


def test_given_lookup_true_hit_when_score_then_usable() -> None:
    meta = {
        "n_sources": 5,
        "l_eff": 120000,
        "sumcache_active": 352,
        "n_slices": 55,
        "k_slices": 11,
        "l_eff_ok": True,
        "ratio_ok": True,
        "ctx_bounded": True,
    }
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes, usable = score_ctxlift_lookup(
        mode="WRAP_LOOKUP",
        completion="gold answer",
        expected_gold="gold answer",
        lookup_kind="TRUE_HIT",
        meta=meta,
        payload=payload,
    )
    assert score >= 8.0 and err is False and usable is True
    assert any("≠ generative IQ" in n or "not generative" in n for n in notes)


def test_given_gen_periods_when_score_then_usable_if_ctx_ok() -> None:
    meta = {
        "n_sources": 5,
        "l_eff": 120000,
        "sumcache_active": 352,
        "n_slices": 55,
        "k_slices": 11,
        "l_eff_ok": True,
        "ratio_ok": True,
        "ctx_bounded": True,
    }
    payload = {"mode": "QT+EARLY n=1", "wall_ms": 20.0, "n_new": 8}
    score, err, notes, usable = score_ctxlift_gen(
        completion="........",
        expected_gold="anything",
        meta=meta,
        payload=payload,
    )
    assert score == 1.0 and err is True and usable is True
    assert notes


def test_given_ready_when_decide_then_promote() -> None:
    stats = ctxlift_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        lookup_usables=[True] * 10,
        gen_scores=[1.0] * 10,
        gen_errors=[True] * 10,
        gen_usables=[True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        mean_l_eff=120000.0,
        mean_active=352.0,
        mean_slices=55.0,
        mean_sources=5.0,
        n_fix=0,
    )
    assert stats["pass_leff_up"] is True
    assert decide_ctxlift(stats) == "PROMOTE"


def test_given_low_leff_when_decide_then_hold() -> None:
    stats = ctxlift_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        lookup_usables=[True] * 10,
        gen_scores=[1.0] * 10,
        gen_errors=[True] * 10,
        gen_usables=[True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        mean_l_eff=50000.0,
        mean_active=352.0,
        mean_slices=55.0,
        mean_sources=5.0,
        n_fix=0,
    )
    assert stats["pass_leff_up"] is False
    assert decide_ctxlift(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = ctxlift_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        lookup_usables=[True] * 10,
        gen_scores=[1.0] * 10,
        gen_errors=[True] * 10,
        gen_usables=[True] * 10,
        n_true_hit=9,
        n_false_hit=1,
        mean_l_eff=120000.0,
        mean_active=352.0,
        mean_slices=55.0,
        mean_sources=5.0,
        n_fix=0,
    )
    assert decide_ctxlift(stats) == "KILL"
