"""Contract: Wave AE4 H-APPMAX — howto↑ + route + DEPL-AE."""

from __future__ import annotations

from appmax_ops import (
    APPMAX_APPS,
    APPMAX_ID,
    APPMAX_N,
    APPPLUS_HOWTO_MEAN,
    MIN_APPS,
    MIN_PAGES,
    REQUIRED_HOWTO,
    REQUIRED_ROUTE,
    app_by_id,
    app_stats,
    appmax_stats,
    claim_is_honest,
    decide_app,
    decide_appmax,
    depl_ae_body,
    one_pager_body,
    page_sync_report,
    route_item,
    select_app,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AE4 H-APPMAX
    assert APPMAX_ID == "H-APPMAX"
    assert APPMAX_N == 10
    assert MIN_APPS == 4
    assert MIN_PAGES == 5
    assert REQUIRED_HOWTO == "app-howto"
    assert REQUIRED_ROUTE == "app-route"
    assert APPPLUS_HOWTO_MEAN == 8.3
    ids = {a["app_id"] for a in APPMAX_APPS}
    assert ids == {"app-known", "app-longdoc", "app-howto", "app-route"}


def test_given_howto_when_route_then_only_howto() -> None:
    app = app_by_id("app-howto")
    assert route_item(app, "howto")["in_scope"] is True
    assert route_item(app, "known-ask")["in_scope"] is False


def test_given_route_app_when_all_surfaces_then_in_scope() -> None:
    app = app_by_id("app-route")
    for surface in ("known-ask", "howto", "long-doc"):
        assert route_item(app, surface)["in_scope"] is True


def test_given_surface_when_select_then_canonical_app() -> None:
    assert select_app("howto")["app_id"] == "app-howto"
    assert select_app("long-doc")["app_id"] == "app-longdoc"
    assert select_app("known-ask")["app_id"] == "app-known"


def test_given_claims_when_check_then_honest() -> None:
    for app in APPMAX_APPS:
        assert claim_is_honest(str(app["claim"])) is True


def test_given_one_pager_when_body_then_ae_stack_and_honesty() -> None:
    body = one_pager_body(app_by_id("app-howto"))
    assert "npm run nano:appmax" in body
    assert "Not an open chat LM" in body
    assert "H-APPMAX" in body
    assert "H-SMARTMAX" in body
    report = page_sync_report("docs/results/nano-lm/app-howto.md", body)
    assert report["ok"] is True


def test_given_depl_ae_when_body_then_sync_ok() -> None:
    body = depl_ae_body()
    assert "DEPL-AE" in body
    assert "app-route" in body
    report = page_sync_report("docs/results/nano-lm/depl-ae.md", body)
    assert report["ok"] is True


def test_given_all_green_howto_up_when_decide_then_promote() -> None:
    stats = appmax_stats(
        [
            {"app_id": "app-known", "decision": "PROMOTE", "mean": 9.0},
            {"app_id": "app-longdoc", "decision": "PROMOTE", "mean": 9.0},
            {"app_id": "app-howto", "decision": "PROMOTE", "mean": 8.5},
            {"app_id": "app-route", "decision": "PROMOTE", "mean": 9.0},
        ],
        n_pages_ok=5,
        n_pages=5,
    )
    assert stats["howto_up"] is True
    assert stats["pass_product"] is True
    assert decide_appmax(stats) == "PROMOTE"


def test_given_howto_mean_below_appplus_when_decide_then_hold() -> None:
    stats = appmax_stats(
        [
            {"app_id": "app-known", "decision": "PROMOTE", "mean": 9.0},
            {"app_id": "app-longdoc", "decision": "PROMOTE", "mean": 9.0},
            {"app_id": "app-howto", "decision": "PROMOTE", "mean": 8.0},
            {"app_id": "app-route", "decision": "PROMOTE", "mean": 9.0},
        ],
        n_pages_ok=5,
        n_pages=5,
    )
    assert stats["howto_up"] is False
    assert decide_appmax(stats) == "HOLD"


def test_given_route_kill_when_decide_then_kill() -> None:
    stats = appmax_stats(
        [
            {"app_id": "app-known", "decision": "PROMOTE", "mean": 9.0},
            {"app_id": "app-longdoc", "decision": "PROMOTE", "mean": 9.0},
            {"app_id": "app-howto", "decision": "PROMOTE", "mean": 9.0},
            {"app_id": "app-route", "decision": "KILL", "mean": 2.0},
        ],
        n_pages_ok=5,
        n_pages=5,
    )
    assert decide_appmax(stats) == "KILL"


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
