"""Contract: Wave AB0 SESSION — freeze 10 real HITL asks (§8.3 · §11)."""

from __future__ import annotations

from ab_session_ops import (
    AB0_APP_IDS,
    AB0_ID,
    AB0_MIX,
    AB0_N,
    AB0_PACK,
    AB0_THESIS,
    decide_ab0_session,
    missing_pack_source_ids,
    mix_ok,
    pack_app_counts,
    unique_trial_ids,
)


def test_given_pack_when_count_then_exactly_ten() -> None:
    # GIVEN/WHEN/THEN: pesquisa §11 AB0 — freeze HITL×10
    assert len(AB0_PACK) == AB0_N == 10


def test_given_pack_when_ids_then_unique() -> None:
    assert unique_trial_ids(AB0_PACK) is True


def test_given_pack_when_mix_then_section_115() -> None:
    assert mix_ok(AB0_PACK) is True
    assert pack_app_counts(AB0_PACK) == dict(AB0_MIX)


def test_given_registry_when_pack_then_all_source_ids_known() -> None:
    from curated_sources import source_ids

    miss = missing_pack_source_ids(set(source_ids()))
    assert miss == []


def test_given_unknown_source_when_missing_then_listed() -> None:
    assert missing_pack_source_ids({"bip-0039"}) == sorted(
        {
            p["source_id"]
            for p in AB0_PACK
            if p["source_id"] != "bip-0039"
        }
    )


def test_given_bad_mix_when_ok_then_false() -> None:
    bad = [dict(p) for p in AB0_PACK]
    bad[0]["app_id"] = "howto"
    assert mix_ok(bad) is False


def test_given_ready_when_decide_then_promote() -> None:
    known = {p["source_id"] for p in AB0_PACK}
    out = decide_ab0_session(known_sources=known, trials_dir_ready=True)
    assert out.startswith("PROMOTE")
    assert AB0_ID in out
    assert "SEMWRAP" in AB0_THESIS or "AB1" in AB0_THESIS


def test_given_no_trials_when_decide_then_kill() -> None:
    known = {p["source_id"] for p in AB0_PACK}
    out = decide_ab0_session(known_sources=known, trials_dir_ready=False)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_pack_when_fields_then_app_and_gold() -> None:
    for item in AB0_PACK:
        assert item["app_id"] in AB0_APP_IDS
        assert item["source_id"]
        assert item["question"].strip()
        assert item["gold"].strip()
        assert item["id"].startswith("AB-HITL-")
