"""Contract: Wave AC0 SESSION — freeze 10 held-out HITL asks (§8.5 · §12)."""

from __future__ import annotations

from ac_session_ops import (
    AC0_APP_IDS,
    AC0_ID,
    AC0_MIX,
    AC0_N,
    AC0_PACK,
    AC0_THESIS,
    decide_ac0_session,
    missing_pack_source_ids,
    mix_ok,
    overlaps_ab_questions,
    pack_app_counts,
    unique_trial_ids,
)


def test_given_pack_when_count_then_exactly_ten() -> None:
    # GIVEN/WHEN/THEN: pesquisa §12 AC0 — freeze held-out HITL×10
    assert len(AC0_PACK) == AC0_N == 10


def test_given_pack_when_ids_then_unique() -> None:
    assert unique_trial_ids(AC0_PACK) is True


def test_given_pack_when_mix_then_section_125() -> None:
    assert mix_ok(AC0_PACK) is True
    assert pack_app_counts(AC0_PACK) == dict(AC0_MIX)


def test_given_registry_when_pack_then_all_source_ids_known() -> None:
    from curated_sources import source_ids

    miss = missing_pack_source_ids(set(source_ids()))
    assert miss == []


def test_given_pack_when_compare_ab_then_no_verbatim_overlap() -> None:
    assert overlaps_ab_questions(AC0_PACK) == []


def test_given_copied_ab_q_when_overlap_then_listed() -> None:
    from ab_session_ops import AB0_PACK

    bad = [dict(p) for p in AC0_PACK]
    bad[0]["question"] = AB0_PACK[0]["question"]
    assert overlaps_ab_questions(bad) == ["AC-HITL-01"]


def test_given_ready_when_decide_then_promote() -> None:
    known = {p["source_id"] for p in AC0_PACK}
    out = decide_ac0_session(known_sources=known, trials_dir_ready=True)
    assert out.startswith("PROMOTE")
    assert AC0_ID in out
    assert "CTXPLUS" in AC0_THESIS or "AC1" in AC0_THESIS


def test_given_no_trials_when_decide_then_kill() -> None:
    known = {p["source_id"] for p in AC0_PACK}
    out = decide_ac0_session(known_sources=known, trials_dir_ready=False)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_pack_when_fields_then_app_and_gold() -> None:
    for item in AC0_PACK:
        assert item["app_id"] in AC0_APP_IDS
        assert item["source_id"]
        assert item["question"].strip()
        assert item["gold"].strip()
        assert item["id"].startswith("AC-HITL-")
