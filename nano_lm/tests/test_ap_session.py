"""Contract: Wave AP0 SESSION — freeze 10 held-out HITL asks (pesquisa §3)."""

from __future__ import annotations

from ap_session_ops import (
    AP0_APP_IDS,
    AP0_ID,
    AP0_MIX,
    AP0_N,
    AP0_PACK,
    AP0_THESIS,
    decide_ap0_session,
    missing_pack_source_ids,
    mix_ok,
    overlaps_prior_questions,
    pack_app_counts,
    unique_trial_ids,
)


def test_given_pack_when_count_then_exactly_ten() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AP0 — freeze held-out HITL×10
    assert len(AP0_PACK) == AP0_N == 10


def test_given_pack_when_ids_then_unique() -> None:
    assert unique_trial_ids(AP0_PACK) is True


def test_given_pack_when_mix_then_three_five_two() -> None:
    assert mix_ok(AP0_PACK) is True
    assert pack_app_counts(AP0_PACK) == dict(AP0_MIX)


def test_given_registry_when_pack_then_all_source_ids_known() -> None:
    from curated_sources import source_ids

    miss = missing_pack_source_ids(set(source_ids()))
    assert miss == []


def test_given_pack_when_compare_prior_then_no_verbatim_overlap() -> None:
    assert overlaps_prior_questions(AP0_PACK) == []


def test_given_copied_ab_q_when_overlap_then_listed() -> None:
    from ab_session_ops import AB0_PACK

    bad = [dict(p) for p in AP0_PACK]
    bad[0]["question"] = AB0_PACK[0]["question"]
    assert overlaps_prior_questions(bad) == ["AP-HITL-01"]


def test_given_copied_ao_q_when_overlap_then_listed() -> None:
    from ao_session_ops import AO0_PACK

    bad = [dict(p) for p in AP0_PACK]
    bad[1]["question"] = AO0_PACK[0]["question"]
    assert overlaps_prior_questions(bad) == ["AP-HITL-02"]


def test_given_copied_an_q_when_overlap_then_listed() -> None:
    from an_session_ops import AN0_PACK

    bad = [dict(p) for p in AP0_PACK]
    bad[2]["question"] = AN0_PACK[0]["question"]
    assert overlaps_prior_questions(bad) == ["AP-HITL-03"]


def test_given_ready_when_decide_then_promote() -> None:
    known = {p["source_id"] for p in AP0_PACK}
    out = decide_ap0_session(known_sources=known, trials_dir_ready=True)
    assert out.startswith("PROMOTE")
    assert AP0_ID in out
    assert "GENBASE" in AP0_THESIS or "AP1" in AP0_THESIS


def test_given_no_trials_when_decide_then_kill() -> None:
    known = {p["source_id"] for p in AP0_PACK}
    out = decide_ap0_session(known_sources=known, trials_dir_ready=False)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_pack_when_fields_then_app_and_gold() -> None:
    for item in AP0_PACK:
        assert item["app_id"] in AP0_APP_IDS
        assert item["source_id"]
        assert item["question"].strip()
        assert item["gold"].strip()
        assert item["id"].startswith("AP-HITL-")
