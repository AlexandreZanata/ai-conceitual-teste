"""Contract: Wave AC4 H-APPPLUS — app-howto + known/longdoc green."""

from __future__ import annotations

from appplus_ops import (
    APPPLUS_APPS,
    APPPLUS_ID,
    APPPLUS_N,
    MIN_APPS,
    REQUIRED_HOWTO,
    app_by_id,
    app_stats,
    appplus_stats,
    claim_is_honest,
    decide_app,
    decide_appplus,
    one_pager_body,
    route_item,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8.5 / §12.1 AC4 H-APPPLUS
    assert APPPLUS_ID == "H-APPPLUS"
    assert APPPLUS_N == 10
    assert MIN_APPS == 3
    assert REQUIRED_HOWTO == "app-howto"
    ids = {a["app_id"] for a in APPPLUS_APPS}
    assert ids == {"app-known", "app-longdoc", "app-howto"}


def test_given_howto_app_when_route_then_only_howto() -> None:
    app = app_by_id("app-howto")
    assert route_item(app, "howto")["in_scope"] is True
    assert route_item(app, "known-ask")["in_scope"] is False
    assert route_item(app, "long-doc")["in_scope"] is False


def test_given_claims_when_check_then_honest() -> None:
    for app in APPPLUS_APPS:
        assert claim_is_honest(str(app["claim"])) is True


def test_given_howto_one_pager_when_body_then_run_and_honesty() -> None:
    body = one_pager_body(app_by_id("app-howto"))
    assert "npm run nano:appplus" in body
    assert "Not an open chat LM" in body
    assert "app-howto" in body
    assert "H-APPPLUS" in body


def test_given_all_promote_when_decide_then_promote() -> None:
    stats = appplus_stats(
        [
            {"app_id": "app-known", "decision": "PROMOTE", "mean": 9.0},
            {"app_id": "app-longdoc", "decision": "PROMOTE", "mean": 9.0},
            {"app_id": "app-howto", "decision": "PROMOTE", "mean": 8.5},
        ]
    )
    assert stats["pass_product"] is True
    assert decide_appplus(stats) == "PROMOTE"


def test_given_howto_hold_when_decide_then_hold() -> None:
    stats = appplus_stats(
        [
            {"app_id": "app-known", "decision": "PROMOTE", "mean": 9.0},
            {"app_id": "app-longdoc", "decision": "PROMOTE", "mean": 9.0},
            {"app_id": "app-howto", "decision": "HOLD", "mean": 8.0},
        ]
    )
    assert stats["howto_promote"] is False
    assert decide_appplus(stats) == "HOLD"


def test_given_known_kill_when_decide_then_kill() -> None:
    stats = appplus_stats(
        [
            {"app_id": "app-known", "decision": "KILL", "mean": 2.0},
            {"app_id": "app-longdoc", "decision": "PROMOTE", "mean": 9.0},
            {"app_id": "app-howto", "decision": "PROMOTE", "mean": 9.0},
        ]
    )
    assert decide_appplus(stats) == "KILL"


def test_given_app_quality_when_decide_app_then_promote() -> None:
    stats = app_stats(
        [9.0] * 3 + [8.0] * 7,
        [False] * 10,
        n_true_hit=3,
        n_false_hit=0,
        n_miss=7,
        n_in_scope=3,
        claim_ok=True,
        one_pager_ok=True,
        smoke_ok=True,
    )
    assert decide_app(stats) == "PROMOTE"
