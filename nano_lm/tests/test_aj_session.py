"""Contract: Wave AJ0 SESSION — freeze 10 held-out HITL asks (pesquisa §6)."""

from __future__ import annotations

from aj_session_ops import (
    AJ0_APP_IDS,
    AJ0_ID,
    AJ0_MIX,
    AJ0_N,
    AJ0_PACK,
    AJ0_THESIS,
    decide_aj0_session,
    missing_pack_source_ids,
    mix_ok,
    overlaps_prior_questions,
    pack_app_counts,
    unique_trial_ids,
)


def test_given_pack_when_count_then_exactly_ten() -> None:
    # GIVEN/WHEN/THEN: pesquisa §6 AJ0 — freeze held-out HITL×10
    assert len(AJ0_PACK) == AJ0_N == 10


def test_given_pack_when_ids_then_unique() -> None:
    assert unique_trial_ids(AJ0_PACK) is True


def test_given_pack_when_mix_then_three_five_two() -> None:
    assert mix_ok(AJ0_PACK) is True
    assert pack_app_counts(AJ0_PACK) == dict(AJ0_MIX)


def test_given_registry_when_pack_then_all_source_ids_known() -> None:
    from curated_sources import source_ids

    miss = missing_pack_source_ids(set(source_ids()))
    assert miss == []


def test_given_pack_when_compare_prior_then_no_verbatim_overlap() -> None:
    assert overlaps_prior_questions(AJ0_PACK) == []


def test_given_copied_ab_q_when_overlap_then_listed() -> None:
    from ab_session_ops import AB0_PACK

    bad = [dict(p) for p in AJ0_PACK]
    bad[0]["question"] = AB0_PACK[0]["question"]
    assert overlaps_prior_questions(bad) == ["AJ-HITL-01"]


def test_given_copied_ai_q_when_overlap_then_listed() -> None:
    from ai_session_ops import AI0_PACK

    bad = [dict(p) for p in AJ0_PACK]
    bad[1]["question"] = AI0_PACK[0]["question"]
    assert overlaps_prior_questions(bad) == ["AJ-HITL-02"]


def test_given_copied_ah_q_when_overlap_then_listed() -> None:
    from ah_session_ops import AH0_PACK

    bad = [dict(p) for p in AJ0_PACK]
    bad[2]["question"] = AH0_PACK[0]["question"]
    assert overlaps_prior_questions(bad) == ["AJ-HITL-03"]


def test_given_ready_when_decide_then_promote() -> None:
    known = {p["source_id"] for p in AJ0_PACK}
    out = decide_aj0_session(known_sources=known, trials_dir_ready=True)
    assert out.startswith("PROMOTE")
    assert AJ0_ID in out
    assert "GENPEAK" in AJ0_THESIS or "AJ1" in AJ0_THESIS


def test_given_no_trials_when_decide_then_kill() -> None:
    known = {p["source_id"] for p in AJ0_PACK}
    out = decide_aj0_session(known_sources=known, trials_dir_ready=False)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_pack_when_fields_then_app_and_gold() -> None:
    for item in AJ0_PACK:
        assert item["app_id"] in AJ0_APP_IDS
        assert item["source_id"]
        assert item["question"].strip()
        assert item["gold"].strip()
        assert item["id"].startswith("AJ-HITL-")
