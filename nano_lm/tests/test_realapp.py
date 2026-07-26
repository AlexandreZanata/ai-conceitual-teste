"""Contract: Wave AB5 H-REALAPP — ≥1 packaged app; ASK×10; DEPL honesty."""

from __future__ import annotations

from realapp_ops import (
    MIN_APPS,
    REALAPP_APPS,
    REALAPP_ID,
    REALAPP_N,
    app_by_id,
    app_stats,
    claim_is_honest,
    decide_app,
    decide_realapp,
    one_pager_body,
    realapp_stats,
    route_item,
    score_realapp_trial,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8.3 AB5 H-REALAPP
    assert REALAPP_ID == "H-REALAPP"
    assert REALAPP_N == 10
    assert MIN_APPS == 1
    assert len(REALAPP_APPS) >= MIN_APPS
    assert {a["app_id"] for a in REALAPP_APPS} >= {"app-known", "app-longdoc"}


def test_given_honest_claim_when_check_then_ok() -> None:
    app = app_by_id("app-known")
    assert claim_is_honest(str(app["claim"])) is True
    assert claim_is_honest(str(app_by_id("app-longdoc")["claim"])) is True


def test_given_open_chat_claim_when_check_then_reject() -> None:
    assert claim_is_honest("ship as open chat LM") is False


def test_given_known_app_when_route_howto_then_in_scope() -> None:
    app = app_by_id("app-known")
    r = route_item(app, "howto")
    assert r["in_scope"] is True and r["route"] == "SERVE"


def test_given_known_app_when_route_longdoc_then_out() -> None:
    app = app_by_id("app-known")
    r = route_item(app, "long-doc")
    assert r["in_scope"] is False and r["route"] == "OUT_OF_SCOPE"


def test_given_true_hit_when_score_then_shippable() -> None:
    score, err, notes = score_realapp_trial(
        mode="ASKFAST_CACHE",
        completion="BIP 9",
        expected_gold="BIP 9",
        lookup_kind="TRUE_HIT",
        route={"in_scope": True, "route": "SERVE"},
    )
    assert score == 9.0 and err is False
    assert any("route=SERVE" in n for n in notes)


def test_given_out_of_scope_refuse_when_score_then_honest() -> None:
    score, err, notes = score_realapp_trial(
        mode="REALAPP_OUT_OF_SCOPE",
        completion="Out of scope for app-known (surface=known-ask).",
        expected_gold="BIP 9",
        lookup_kind="MISS",
        route={"in_scope": False, "route": "OUT_OF_SCOPE"},
    )
    assert score == 8.0 and err is False
    assert any("HONEST_OUT_OF_SCOPE" in n for n in notes)


def test_given_false_hit_when_score_then_error() -> None:
    score, err, _notes = score_realapp_trial(
        mode="SEMWRAP_LOOKUP",
        completion="wrong",
        expected_gold="gold",
        lookup_kind="FALSE_HIT",
        route={"in_scope": True, "route": "SERVE"},
    )
    assert score == 0.0 and err is True


def test_given_app_quality_when_decide_then_promote() -> None:
    stats = app_stats(
        [9.0] * 10,
        [False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        n_in_scope=7,
        claim_ok=True,
        one_pager_ok=True,
        smoke_ok=True,
    )
    assert decide_app(stats) == "PROMOTE"


def test_given_missing_one_pager_when_decide_then_hold() -> None:
    stats = app_stats(
        [9.0] * 10,
        [False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        n_in_scope=7,
        claim_ok=True,
        one_pager_ok=False,
        smoke_ok=True,
    )
    assert decide_app(stats) == "HOLD"


def test_given_false_hit_when_decide_app_then_kill() -> None:
    stats = app_stats(
        [9.0] * 9 + [0.0],
        [False] * 9 + [True],
        n_true_hit=9,
        n_false_hit=1,
        n_miss=0,
        n_in_scope=10,
        claim_ok=True,
        one_pager_ok=True,
        smoke_ok=True,
    )
    assert decide_app(stats) == "KILL"


def test_given_two_promote_apps_when_decide_wave_then_promote() -> None:
    stats = realapp_stats(
        [
            {"decision": "PROMOTE", "mean": 9.0},
            {"decision": "PROMOTE", "mean": 8.5},
        ]
    )
    assert stats["pass_product"] is True
    assert decide_realapp(stats) == "PROMOTE"


def test_given_one_kill_when_decide_wave_then_kill() -> None:
    stats = realapp_stats(
        [
            {"decision": "PROMOTE", "mean": 9.0},
            {"decision": "KILL", "mean": 2.0},
        ]
    )
    assert decide_realapp(stats) == "KILL"


def test_given_app_when_one_pager_then_has_run_and_honesty() -> None:
    body = one_pager_body(app_by_id("app-known"))
    assert "npm run nano:realapp" in body
    assert "Not an open chat LM" in body
    assert "app-known" in body
