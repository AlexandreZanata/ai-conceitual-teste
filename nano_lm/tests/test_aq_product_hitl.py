"""Contract: Wave AQ7 AQ-PRODUCT-HITL — product composite (pesquisa §5)."""

from __future__ import annotations

from aq_product_hitl_ops import (
    APP_SMOKE_PACK,
    APP_SURFACES,
    HONEST_CLAIM,
    PRODUCT_HITL_ID,
    PRODUCT_HITL_THESIS,
    apps_ok,
    claim_is_honest,
    decide_aq_product_hitl,
    generative_claim_unlocked,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AQ7 — product pass · gen only if AQ6 PROMOTE
    assert PRODUCT_HITL_ID == "AQ-PRODUCT-HITL"
    assert APP_SURFACES == ("known-ask", "howto", "long-doc")
    assert len(APP_SMOKE_PACK) == 3
    assert "product" in PRODUCT_HITL_THESIS.lower()
    assert claim_is_honest(HONEST_CLAIM)


def test_given_apps_when_pack_then_one_per_surface() -> None:
    apps = {p["app_id"] for p in APP_SMOKE_PACK}
    assert apps == set(APP_SURFACES)
    for p in APP_SMOKE_PACK:
        assert p["question"].strip() and p["gold"].strip()


def test_given_honest_claim_when_check_then_ok() -> None:
    assert claim_is_honest(HONEST_CLAIM)
    assert not generative_claim_unlocked(HONEST_CLAIM)


def test_given_open_chat_claim_when_check_then_fail() -> None:
    bad = "open chat mini-AGI unlocked generative ship"
    assert not claim_is_honest(bad)
    assert generative_claim_unlocked(bad)


def test_given_apps_true_hit_when_ok_then_pass() -> None:
    trials = [
        {"app_id": "known-ask", "lookup_kind": "TRUE_HIT"},
        {"app_id": "howto", "lookup_kind": "TRUE_HIT"},
        {"app_id": "long-doc", "lookup_kind": "TRUE_HIT"},
    ]
    assert apps_ok(trials)


def test_given_apps_miss_when_ok_then_fail() -> None:
    trials = [
        {"app_id": "known-ask", "lookup_kind": "TRUE_HIT"},
        {"app_id": "howto", "lookup_kind": "MISS"},
        {"app_id": "long-doc", "lookup_kind": "TRUE_HIT"},
    ]
    assert not apps_ok(trials)


def test_given_all_promote_hold_nano_when_decide_then_promote() -> None:
    out = decide_aq_product_hitl(
        para_decision="PROMOTE",
        adv_decision="PROMOTE",
        mode_decision="PROMOTE",
        apps_pass=True,
        nanogen_decision="HOLD",
        claim=HONEST_CLAIM,
    )
    assert out == "PROMOTE"


def test_given_gen_claim_while_hold_when_decide_then_kill() -> None:
    out = decide_aq_product_hitl(
        para_decision="PROMOTE",
        adv_decision="PROMOTE",
        mode_decision="PROMOTE",
        apps_pass=True,
        nanogen_decision="HOLD",
        claim="open chat mini-AGI unlocked",
    )
    assert out.startswith("KILL")


def test_given_adv_kill_when_decide_then_kill() -> None:
    out = decide_aq_product_hitl(
        para_decision="PROMOTE",
        adv_decision="KILL (false-hit)",
        mode_decision="PROMOTE",
        apps_pass=True,
        nanogen_decision="HOLD",
        claim=HONEST_CLAIM,
    )
    assert out.startswith("KILL")


def test_given_para_hold_when_decide_then_hold() -> None:
    out = decide_aq_product_hitl(
        para_decision="HOLD",
        adv_decision="PROMOTE",
        mode_decision="PROMOTE",
        apps_pass=True,
        nanogen_decision="HOLD",
        claim=HONEST_CLAIM,
    )
    assert out.startswith("HOLD")
