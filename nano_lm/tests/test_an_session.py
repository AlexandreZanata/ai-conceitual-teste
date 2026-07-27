"""Contract: Wave AN0 SESSION — freeze 10 held-out HITL asks (pesquisa §3)."""

from __future__ import annotations

from an_session_ops import (
    AN0_APP_IDS,
    AN0_ID,
    AN0_MIX,
    AN0_N,
    AN0_PACK,
    AN0_THESIS,
    decide_an0_session,
    missing_pack_source_ids,
    mix_ok,
    overlaps_prior_questions,
    pack_app_counts,
    unique_trial_ids,
)


def test_given_pack_when_count_then_exactly_ten() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AN0 — freeze held-out HITL×10
    assert len(AN0_PACK) == AN0_N == 10


def test_given_pack_when_ids_then_unique() -> None:
    assert unique_trial_ids(AN0_PACK) is True


def test_given_pack_when_mix_then_three_five_two() -> None:
    assert mix_ok(AN0_PACK) is True
    assert pack_app_counts(AN0_PACK) == dict(AN0_MIX)


def test_given_registry_when_pack_then_all_source_ids_known() -> None:
    from curated_sources import source_ids

    miss = missing_pack_source_ids(set(source_ids()))
    assert miss == []


def test_given_pack_when_compare_prior_then_no_verbatim_overlap() -> None:
    assert overlaps_prior_questions(AN0_PACK) == []


def test_given_copied_ab_q_when_overlap_then_listed() -> None:
    from ab_session_ops import AB0_PACK

    bad = [dict(p) for p in AN0_PACK]
    bad[0]["question"] = AB0_PACK[0]["question"]
    assert overlaps_prior_questions(bad) == ["AN-HITL-01"]


def test_given_copied_am_q_when_overlap_then_listed() -> None:
    from am_session_ops import AM0_PACK

    bad = [dict(p) for p in AN0_PACK]
    bad[1]["question"] = AM0_PACK[0]["question"]
    assert overlaps_prior_questions(bad) == ["AN-HITL-02"]


def test_given_copied_al_q_when_overlap_then_listed() -> None:
    from al_session_ops import AL0_PACK

    bad = [dict(p) for p in AN0_PACK]
    bad[2]["question"] = AL0_PACK[0]["question"]
    assert overlaps_prior_questions(bad) == ["AN-HITL-03"]


def test_given_ready_when_decide_then_promote() -> None:
    known = {p["source_id"] for p in AN0_PACK}
    out = decide_an0_session(known_sources=known, trials_dir_ready=True)
    assert out.startswith("PROMOTE")
    assert AN0_ID in out
    assert "GENEDGE" in AN0_THESIS or "AN1" in AN0_THESIS


def test_given_no_trials_when_decide_then_kill() -> None:
    known = {p["source_id"] for p in AN0_PACK}
    out = decide_an0_session(known_sources=known, trials_dir_ready=False)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_pack_when_fields_then_app_and_gold() -> None:
    for item in AN0_PACK:
        assert item["app_id"] in AN0_APP_IDS
        assert item["source_id"]
        assert item["question"].strip()
        assert item["gold"].strip()
        assert item["id"].startswith("AN-HITL-")
