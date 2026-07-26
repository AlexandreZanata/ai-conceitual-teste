"""Contract: Wave AD0 SESSION — freeze 10 held-out HITL asks (§8.6 · §13)."""

from __future__ import annotations

from ad_session_ops import (
    AD0_APP_IDS,
    AD0_ID,
    AD0_MIX,
    AD0_N,
    AD0_PACK,
    AD0_THESIS,
    decide_ad0_session,
    missing_pack_source_ids,
    mix_ok,
    overlaps_prior_questions,
    pack_app_counts,
    unique_trial_ids,
)


def test_given_pack_when_count_then_exactly_ten() -> None:
    # GIVEN/WHEN/THEN: pesquisa §13 AD0 — freeze held-out HITL×10
    assert len(AD0_PACK) == AD0_N == 10


def test_given_pack_when_ids_then_unique() -> None:
    assert unique_trial_ids(AD0_PACK) is True


def test_given_pack_when_mix_then_section_135() -> None:
    assert mix_ok(AD0_PACK) is True
    assert pack_app_counts(AD0_PACK) == dict(AD0_MIX)


def test_given_registry_when_pack_then_all_source_ids_known() -> None:
    from curated_sources import source_ids

    miss = missing_pack_source_ids(set(source_ids()))
    assert miss == []


def test_given_pack_when_compare_prior_then_no_verbatim_overlap() -> None:
    assert overlaps_prior_questions(AD0_PACK) == []


def test_given_copied_ab_q_when_overlap_then_listed() -> None:
    from ab_session_ops import AB0_PACK

    bad = [dict(p) for p in AD0_PACK]
    bad[0]["question"] = AB0_PACK[0]["question"]
    assert overlaps_prior_questions(bad) == ["AD-HITL-01"]


def test_given_copied_ac_q_when_overlap_then_listed() -> None:
    from ac_session_ops import AC0_PACK

    bad = [dict(p) for p in AD0_PACK]
    bad[1]["question"] = AC0_PACK[0]["question"]
    assert overlaps_prior_questions(bad) == ["AD-HITL-02"]


def test_given_ready_when_decide_then_promote() -> None:
    known = {p["source_id"] for p in AD0_PACK}
    out = decide_ad0_session(known_sources=known, trials_dir_ready=True)
    assert out.startswith("PROMOTE")
    assert AD0_ID in out
    assert "HARDPARA" in AD0_THESIS or "AD1" in AD0_THESIS


def test_given_no_trials_when_decide_then_kill() -> None:
    known = {p["source_id"] for p in AD0_PACK}
    out = decide_ad0_session(known_sources=known, trials_dir_ready=False)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_pack_when_fields_then_app_and_gold() -> None:
    for item in AD0_PACK:
        assert item["app_id"] in AD0_APP_IDS
        assert item["source_id"]
        assert item["question"].strip()
        assert item["gold"].strip()
        assert item["id"].startswith("AD-HITL-")
