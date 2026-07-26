"""Contract: Wave AK0 SESSION — freeze 10 held-out HITL asks (pesquisa §3)."""

from __future__ import annotations

from ak_session_ops import (
    AK0_APP_IDS,
    AK0_ID,
    AK0_MIX,
    AK0_N,
    AK0_PACK,
    AK0_THESIS,
    decide_ak0_session,
    missing_pack_source_ids,
    mix_ok,
    overlaps_prior_questions,
    pack_app_counts,
    unique_trial_ids,
)


def test_given_pack_when_count_then_exactly_ten() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AK0 — freeze held-out HITL×10
    assert len(AK0_PACK) == AK0_N == 10


def test_given_pack_when_ids_then_unique() -> None:
    assert unique_trial_ids(AK0_PACK) is True


def test_given_pack_when_mix_then_three_five_two() -> None:
    assert mix_ok(AK0_PACK) is True
    assert pack_app_counts(AK0_PACK) == dict(AK0_MIX)


def test_given_registry_when_pack_then_all_source_ids_known() -> None:
    from curated_sources import source_ids

    miss = missing_pack_source_ids(set(source_ids()))
    assert miss == []


def test_given_pack_when_compare_prior_then_no_verbatim_overlap() -> None:
    assert overlaps_prior_questions(AK0_PACK) == []


def test_given_copied_ab_q_when_overlap_then_listed() -> None:
    from ab_session_ops import AB0_PACK

    bad = [dict(p) for p in AK0_PACK]
    bad[0]["question"] = AB0_PACK[0]["question"]
    assert overlaps_prior_questions(bad) == ["AK-HITL-01"]


def test_given_copied_aj_q_when_overlap_then_listed() -> None:
    from aj_session_ops import AJ0_PACK

    bad = [dict(p) for p in AK0_PACK]
    bad[1]["question"] = AJ0_PACK[0]["question"]
    assert overlaps_prior_questions(bad) == ["AK-HITL-02"]


def test_given_copied_ai_q_when_overlap_then_listed() -> None:
    from ai_session_ops import AI0_PACK

    bad = [dict(p) for p in AK0_PACK]
    bad[2]["question"] = AI0_PACK[0]["question"]
    assert overlaps_prior_questions(bad) == ["AK-HITL-03"]


def test_given_ready_when_decide_then_promote() -> None:
    known = {p["source_id"] for p in AK0_PACK}
    out = decide_ak0_session(known_sources=known, trials_dir_ready=True)
    assert out.startswith("PROMOTE")
    assert AK0_ID in out
    assert "GENTRUE" in AK0_THESIS or "AK1" in AK0_THESIS


def test_given_no_trials_when_decide_then_kill() -> None:
    known = {p["source_id"] for p in AK0_PACK}
    out = decide_ak0_session(known_sources=known, trials_dir_ready=False)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_pack_when_fields_then_app_and_gold() -> None:
    for item in AK0_PACK:
        assert item["app_id"] in AK0_APP_IDS
        assert item["source_id"]
        assert item["question"].strip()
        assert item["gold"].strip()
        assert item["id"].startswith("AK-HITL-")
