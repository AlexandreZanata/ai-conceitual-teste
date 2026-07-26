"""Contract: Wave AF4 H-APPULTRA — howto↑ + compose 5th + DEPL-AF."""

from __future__ import annotations

from appultra_ops import (
    APPMAX_HOWTO_MEAN,
    APPMAX_MEAN_ACROSS,
    APPULTRA_APPS,
    APPULTRA_ID,
    APPULTRA_N,
    MIN_APPS,
    MIN_PAGES,
    REQUIRED_COMPOSE,
    REQUIRED_HOWTO,
    REQUIRED_ROUTE,
    app_by_id,
    app_stats,
    appultra_stats,
    claim_is_honest,
    decide_app,
    decide_appultra,
    depl_af_body,
    one_pager_body,
    page_sync_report,
    route_item,
    select_app,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AF4 H-APPULTRA
    assert APPULTRA_ID == "H-APPULTRA"
    assert APPULTRA_N == 10
    assert MIN_APPS == 5
    assert MIN_PAGES == 6
    assert REQUIRED_HOWTO == "app-howto"
    assert REQUIRED_ROUTE == "app-route"
    assert REQUIRED_COMPOSE == "app-compose"
    assert APPMAX_HOWTO_MEAN == 8.3
    assert APPMAX_MEAN_ACROSS == 8.725
    ids = {a["app_id"] for a in APPULTRA_APPS}
    assert ids == {
        "app-known",
        "app-longdoc",
        "app-howto",
        "app-route",
        "app-compose",
    }


def test_given_howto_when_route_then_only_howto() -> None:
    app = app_by_id("app-howto")
    assert route_item(app, "howto")["in_scope"] is True
    assert route_item(app, "known-ask")["in_scope"] is False


def test_given_compose_when_all_surfaces_then_in_scope() -> None:
    app = app_by_id("app-compose")
    for surface in ("known-ask", "howto", "long-doc"):
        assert route_item(app, surface)["in_scope"] is True


def test_given_route_app_when_all_surfaces_then_in_scope() -> None:
    app = app_by_id("app-route")
    for surface in ("known-ask", "howto", "long-doc"):
        assert route_item(app, surface)["in_scope"] is True


def test_given_surface_when_select_then_canonical_app() -> None:
    assert select_app("howto")["app_id"] == "app-howto"
    assert select_app("long-doc")["app_id"] == "app-longdoc"
    assert select_app("known-ask")["app_id"] == "app-known"


def test_given_claims_when_check_then_honest() -> None:
    for app in APPULTRA_APPS:
        assert claim_is_honest(str(app["claim"])) is True


def test_given_one_pager_when_body_then_af_stack_and_honesty() -> None:
    body = one_pager_body(app_by_id("app-howto"))
    assert "npm run nano:appultra" in body
    assert "Not an open chat LM" in body
    assert "H-APPULTRA" in body
    assert "H-SMARTULTRA" in body
    assert "H-CTXULTRA" in body
    report = page_sync_report(
        "docs/results/nano-lm/appultra-howto.md", body
    )
    assert report["ok"] is True


def test_given_depl_af_when_body_then_sync_ok() -> None:
    body = depl_af_body()
    assert "DEPL-AF" in body
    assert "app-compose" in body
    assert "app-route" in body
    report = page_sync_report("docs/results/nano-lm/depl-af.md", body)
    assert report["ok"] is True


def test_given_all_green_howto_mean_up_when_decide_then_promote() -> None:
    stats = appultra_stats(
        [
            {"app_id": "app-known", "decision": "PROMOTE", "mean": 9.0},
            {"app_id": "app-longdoc", "decision": "PROMOTE", "mean": 9.0},
            {"app_id": "app-howto", "decision": "PROMOTE", "mean": 8.5},
            {"app_id": "app-route", "decision": "PROMOTE", "mean": 9.0},
            {"app_id": "app-compose", "decision": "PROMOTE", "mean": 9.0},
        ],
        n_pages_ok=6,
        n_pages=6,
    )
    assert stats["howto_up"] is True
    assert stats["mean_up"] is True
    assert stats["compose_green"] is True
    assert stats["pass_product"] is True
    assert decide_appultra(stats) == "PROMOTE"


def test_given_howto_mean_below_appmax_when_decide_then_hold() -> None:
    stats = appultra_stats(
        [
            {"app_id": "app-known", "decision": "PROMOTE", "mean": 9.0},
            {"app_id": "app-longdoc", "decision": "PROMOTE", "mean": 9.0},
            {"app_id": "app-howto", "decision": "PROMOTE", "mean": 8.0},
            {"app_id": "app-route", "decision": "PROMOTE", "mean": 9.0},
            {"app_id": "app-compose", "decision": "PROMOTE", "mean": 9.0},
        ],
        n_pages_ok=6,
        n_pages=6,
    )
    assert stats["howto_up"] is False
    assert decide_appultra(stats) == "HOLD"


def test_given_compose_kill_when_decide_then_kill() -> None:
    stats = appultra_stats(
        [
            {"app_id": "app-known", "decision": "PROMOTE", "mean": 9.0},
            {"app_id": "app-longdoc", "decision": "PROMOTE", "mean": 9.0},
            {"app_id": "app-howto", "decision": "PROMOTE", "mean": 9.0},
            {"app_id": "app-route", "decision": "PROMOTE", "mean": 9.0},
            {"app_id": "app-compose", "decision": "KILL", "mean": 2.0},
        ],
        n_pages_ok=6,
        n_pages=6,
    )
    assert decide_appultra(stats) == "KILL"


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
