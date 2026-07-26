"""Contract: Wave AE0 SESSION — freeze 10 held-out HITL asks (pesquisa §5)."""

from __future__ import annotations

from ae_session_ops import (
    AE0_APP_IDS,
    AE0_ID,
    AE0_MIX,
    AE0_N,
    AE0_PACK,
    AE0_THESIS,
    decide_ae0_session,
    missing_pack_source_ids,
    mix_ok,
    overlaps_prior_questions,
    pack_app_counts,
    unique_trial_ids,
)


def test_given_pack_when_count_then_exactly_ten() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AE0 — freeze held-out HITL×10
    assert len(AE0_PACK) == AE0_N == 10


def test_given_pack_when_ids_then_unique() -> None:
    assert unique_trial_ids(AE0_PACK) is True


def test_given_pack_when_mix_then_three_three_four() -> None:
    assert mix_ok(AE0_PACK) is True
    assert pack_app_counts(AE0_PACK) == dict(AE0_MIX)


def test_given_registry_when_pack_then_all_source_ids_known() -> None:
    from curated_sources import source_ids

    miss = missing_pack_source_ids(set(source_ids()))
    assert miss == []


def test_given_pack_when_compare_prior_then_no_verbatim_overlap() -> None:
    assert overlaps_prior_questions(AE0_PACK) == []


def test_given_copied_ab_q_when_overlap_then_listed() -> None:
    from ab_session_ops import AB0_PACK

    bad = [dict(p) for p in AE0_PACK]
    bad[0]["question"] = AB0_PACK[0]["question"]
    assert overlaps_prior_questions(bad) == ["AE-HITL-01"]


def test_given_copied_ac_q_when_overlap_then_listed() -> None:
    from ac_session_ops import AC0_PACK

    bad = [dict(p) for p in AE0_PACK]
    bad[1]["question"] = AC0_PACK[0]["question"]
    assert overlaps_prior_questions(bad) == ["AE-HITL-02"]


def test_given_copied_ad_q_when_overlap_then_listed() -> None:
    from ad_session_ops import AD0_PACK

    bad = [dict(p) for p in AE0_PACK]
    bad[2]["question"] = AD0_PACK[0]["question"]
    assert overlaps_prior_questions(bad) == ["AE-HITL-03"]


def test_given_ready_when_decide_then_promote() -> None:
    known = {p["source_id"] for p in AE0_PACK}
    out = decide_ae0_session(known_sources=known, trials_dir_ready=True)
    assert out.startswith("PROMOTE")
    assert AE0_ID in out
    assert "CTXMAX" in AE0_THESIS or "AE1" in AE0_THESIS


def test_given_no_trials_when_decide_then_kill() -> None:
    known = {p["source_id"] for p in AE0_PACK}
    out = decide_ae0_session(known_sources=known, trials_dir_ready=False)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_pack_when_fields_then_app_and_gold() -> None:
    for item in AE0_PACK:
        assert item["app_id"] in AE0_APP_IDS
        assert item["source_id"]
        assert item["question"].strip()
        assert item["gold"].strip()
        assert item["id"].startswith("AE-HITL-")
