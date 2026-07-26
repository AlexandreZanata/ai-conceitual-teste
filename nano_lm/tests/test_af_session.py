"""Contract: Wave AF0 SESSION — freeze 10 held-out HITL asks (pesquisa §5)."""

from __future__ import annotations

from af_session_ops import (
    AF0_APP_IDS,
    AF0_ID,
    AF0_MIX,
    AF0_N,
    AF0_PACK,
    AF0_THESIS,
    decide_af0_session,
    missing_pack_source_ids,
    mix_ok,
    overlaps_prior_questions,
    pack_app_counts,
    unique_trial_ids,
)


def test_given_pack_when_count_then_exactly_ten() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AF0 — freeze held-out HITL×10
    assert len(AF0_PACK) == AF0_N == 10


def test_given_pack_when_ids_then_unique() -> None:
    assert unique_trial_ids(AF0_PACK) is True


def test_given_pack_when_mix_then_three_five_two() -> None:
    assert mix_ok(AF0_PACK) is True
    assert pack_app_counts(AF0_PACK) == dict(AF0_MIX)


def test_given_registry_when_pack_then_all_source_ids_known() -> None:
    from curated_sources import source_ids

    miss = missing_pack_source_ids(set(source_ids()))
    assert miss == []


def test_given_pack_when_compare_prior_then_no_verbatim_overlap() -> None:
    assert overlaps_prior_questions(AF0_PACK) == []


def test_given_copied_ab_q_when_overlap_then_listed() -> None:
    from ab_session_ops import AB0_PACK

    bad = [dict(p) for p in AF0_PACK]
    bad[0]["question"] = AB0_PACK[0]["question"]
    assert overlaps_prior_questions(bad) == ["AF-HITL-01"]


def test_given_copied_ac_q_when_overlap_then_listed() -> None:
    from ac_session_ops import AC0_PACK

    bad = [dict(p) for p in AF0_PACK]
    bad[1]["question"] = AC0_PACK[0]["question"]
    assert overlaps_prior_questions(bad) == ["AF-HITL-02"]


def test_given_copied_ad_q_when_overlap_then_listed() -> None:
    from ad_session_ops import AD0_PACK

    bad = [dict(p) for p in AF0_PACK]
    bad[2]["question"] = AD0_PACK[0]["question"]
    assert overlaps_prior_questions(bad) == ["AF-HITL-03"]


def test_given_copied_ae_q_when_overlap_then_listed() -> None:
    from ae_session_ops import AE0_PACK

    bad = [dict(p) for p in AF0_PACK]
    bad[3]["question"] = AE0_PACK[0]["question"]
    assert overlaps_prior_questions(bad) == ["AF-HITL-04"]


def test_given_ready_when_decide_then_promote() -> None:
    known = {p["source_id"] for p in AF0_PACK}
    out = decide_af0_session(known_sources=known, trials_dir_ready=True)
    assert out.startswith("PROMOTE")
    assert AF0_ID in out
    assert "CTXULTRA" in AF0_THESIS or "AF1" in AF0_THESIS


def test_given_no_trials_when_decide_then_kill() -> None:
    known = {p["source_id"] for p in AF0_PACK}
    out = decide_af0_session(known_sources=known, trials_dir_ready=False)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_pack_when_fields_then_app_and_gold() -> None:
    for item in AF0_PACK:
        assert item["app_id"] in AF0_APP_IDS
        assert item["source_id"]
        assert item["question"].strip()
        assert item["gold"].strip()
        assert item["id"].startswith("AF-HITL-")
