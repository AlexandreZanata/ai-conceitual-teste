"""Contract: Wave AS8 AS-DUAL-HITL — product + gen gate."""

from __future__ import annotations

from as_dual_hitl_ops import (
    APP_SMOKE_PACK,
    APP_SURFACES,
    DUAL_HITL_ID,
    DUAL_HITL_THESIS,
    HONEST_CLAIM,
    apps_ok,
    claim_is_honest,
    decide_as_dual_hitl,
    generative_claim_unlocked,
)


def test_given_contract_when_constants_then_match_as8_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AS8 — product pass · gen only if AS7 PROMOTE
    assert DUAL_HITL_ID == "AS-DUAL-HITL"
    assert APP_SURFACES == ("known-ask", "howto", "long-doc")
    assert len(APP_SMOKE_PACK) == 3
    assert "dual" in DUAL_HITL_THESIS.lower() or "product" in DUAL_HITL_THESIS.lower()
    assert claim_is_honest(HONEST_CLAIM)
    assert not generative_claim_unlocked(HONEST_CLAIM)


def test_given_apps_when_pack_then_as_ids() -> None:
    for p in APP_SMOKE_PACK:
        assert str(p["id"]).startswith("AS-APP-")
        assert p["question"].strip() and p["gold"].strip()


def test_given_apps_true_hit_when_ok_then_pass() -> None:
    trials = [
        {"app_id": "known-ask", "lookup_kind": "TRUE_HIT"},
        {"app_id": "howto", "lookup_kind": "TRUE_HIT"},
        {"app_id": "long-doc", "lookup_kind": "TRUE_HIT"},
    ]
    assert apps_ok(trials)


def test_given_all_promote_hold_nano_when_decide_then_promote() -> None:
    out = decide_as_dual_hitl(
        askabstain_decision="PROMOTE",
        shipui_decision="PROMOTE",
        advsafe_decision="PROMOTE",
        metrics_decision="PROMOTE",
        paraext2_decision="PROMOTE",
        apps_pass=True,
        nanogen3_decision="HOLD",
        claim=HONEST_CLAIM,
    )
    assert out == "PROMOTE"


def test_given_soft_para_when_decide_then_hold() -> None:
    out = decide_as_dual_hitl(
        askabstain_decision="PROMOTE",
        shipui_decision="PROMOTE",
        advsafe_decision="PROMOTE",
        metrics_decision="PROMOTE",
        paraext2_decision="HOLD",
        apps_pass=True,
        nanogen3_decision="HOLD",
        claim=HONEST_CLAIM,
    )
    assert out.startswith("HOLD")
    assert "paraext2" in out


def test_given_gen_claim_while_hold_when_decide_then_kill() -> None:
    out = decide_as_dual_hitl(
        askabstain_decision="PROMOTE",
        shipui_decision="PROMOTE",
        advsafe_decision="PROMOTE",
        metrics_decision="PROMOTE",
        paraext2_decision="PROMOTE",
        apps_pass=True,
        nanogen3_decision="HOLD",
        claim="open chat mini-AGI unlocked",
    )
    assert out.startswith("KILL")


def test_given_advsafe_kill_when_decide_then_kill() -> None:
    out = decide_as_dual_hitl(
        askabstain_decision="PROMOTE",
        shipui_decision="PROMOTE",
        advsafe_decision="KILL",
        metrics_decision="PROMOTE",
        paraext2_decision="PROMOTE",
        apps_pass=True,
        nanogen3_decision="HOLD",
        claim=HONEST_CLAIM,
    )
    assert out.startswith("KILL") and "advsafe" in out
