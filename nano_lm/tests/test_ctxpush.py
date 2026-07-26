"""Contract: Wave AI2 H-CTXPUSH — hexa-doc dual-arm (pesquisa §5)."""

from __future__ import annotations

from ctxlift_ops import TOP_K_SLICES_LIFT
from ctxpush_ops import (
    CTXLIFT_MEAN_LEFF,
    CTXPUSH_ID,
    CTXPUSH_N,
    CTXPUSH_QUATERNARY,
    CTXPUSH_QUINARY,
    CTXPUSH_SECONDARY,
    CTXPUSH_SENARY,
    CTXPUSH_TERTIARY,
    MIN_GEN_USABLE,
    MIN_LOOKUP_USABLE,
    MIN_SOURCES,
    TOP_K_SLICES_PUSH,
    ctxpush_doc_meta,
    ctxpush_stats,
    decide_ctxpush,
    quaternary_for,
    quinary_for,
    score_ctxpush_gen,
    score_ctxpush_lookup,
    secondary_for,
    senary_for,
    tertiary_for,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AI2 H-CTXPUSH
    assert CTXPUSH_ID == "H-CTXPUSH"
    assert CTXPUSH_N == 10
    assert MIN_LOOKUP_USABLE == 7
    assert MIN_GEN_USABLE == 5
    assert MIN_SOURCES == 6
    assert TOP_K_SLICES_PUSH == 13
    assert TOP_K_SLICES_PUSH > TOP_K_SLICES_LIFT
    assert CTXLIFT_MEAN_LEFF == 111578.4


def test_given_ai0_sources_when_pair_then_all_mapped_distinct() -> None:
    from ai_session_ops import AI0_PACK

    for item in AI0_PACK:
        primary = item["source_id"]
        sec = secondary_for(primary)
        ter = tertiary_for(primary)
        quat = quaternary_for(primary)
        quin = quinary_for(primary)
        sen = senary_for(primary)
        assert len({primary, sec, ter, quat, quin, sen}) == 6
        assert CTXPUSH_SECONDARY[primary] == sec
        assert CTXPUSH_TERTIARY[primary] == ter
        assert CTXPUSH_QUATERNARY[primary] == quat
        assert CTXPUSH_QUINARY[primary] == quin
        assert CTXPUSH_SENARY[primary] == sen


def test_given_hexa_docs_when_meta_then_multi_source_and_deeper_k() -> None:
    # Long enough that ROLL can emit full K=13 slices per doc.
    primary = list(range(5000))
    secondary = list(range(6000, 11000))
    tertiary = list(range(12000, 17000))
    quaternary = list(range(18000, 23000))
    quinary = list(range(24000, 29000))
    senary = list(range(30000, 35000))
    q = [10, 20, 400, 800]
    meta = ctxpush_doc_meta(
        primary,
        secondary,
        tertiary,
        quaternary,
        quinary,
        senary,
        q,
        primary_source="a",
        secondary_source="b",
        tertiary_source="c",
        quaternary_source="d",
        quinary_source="e",
        senary_source="f",
    )
    assert meta["n_sources"] == 6
    assert meta["multi_source"] is True
    assert meta["k_slices"] == TOP_K_SLICES_PUSH
    assert meta["n_slices"] == TOP_K_SLICES_PUSH * 6
    assert meta["l_eff"] == 5000 * 6
    assert meta["deeper_than_ctxlift_k"] is True
    assert meta["above_ctxlift_leff"] is False  # 30000 < 111578


def test_given_lookup_true_hit_when_score_then_usable() -> None:
    meta = {
        "n_sources": 6,
        "l_eff": 140000,
        "sumcache_active": 352,
        "n_slices": 78,
        "k_slices": 13,
        "l_eff_ok": True,
        "ratio_ok": True,
        "ctx_bounded": True,
    }
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes, usable = score_ctxpush_lookup(
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
        "n_sources": 6,
        "l_eff": 140000,
        "sumcache_active": 352,
        "n_slices": 78,
        "k_slices": 13,
        "l_eff_ok": True,
        "ratio_ok": True,
        "ctx_bounded": True,
    }
    payload = {"mode": "QT+EARLY n=1", "wall_ms": 20.0, "n_new": 8}
    score, err, notes, usable = score_ctxpush_gen(
        completion="........",
        expected_gold="anything",
        meta=meta,
        payload=payload,
    )
    assert score == 1.0 and err is True and usable is True
    assert notes


def test_given_ready_when_decide_then_promote() -> None:
    stats = ctxpush_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        lookup_usables=[True] * 10,
        gen_scores=[1.0] * 10,
        gen_errors=[True] * 10,
        gen_usables=[True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        mean_l_eff=140000.0,
        mean_active=352.0,
        mean_slices=78.0,
        mean_sources=6.0,
        n_fix=0,
    )
    assert stats["pass_leff_up"] is True
    assert decide_ctxpush(stats) == "PROMOTE"


def test_given_low_leff_when_decide_then_hold() -> None:
    stats = ctxpush_stats(
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
        mean_slices=78.0,
        mean_sources=6.0,
        n_fix=0,
    )
    assert stats["pass_leff_up"] is False
    assert decide_ctxpush(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = ctxpush_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        lookup_usables=[True] * 10,
        gen_scores=[1.0] * 10,
        gen_errors=[True] * 10,
        gen_usables=[True] * 10,
        n_true_hit=9,
        n_false_hit=1,
        mean_l_eff=140000.0,
        mean_active=352.0,
        mean_slices=78.0,
        mean_sources=6.0,
        n_fix=0,
    )
    assert decide_ctxpush(stats) == "KILL"
