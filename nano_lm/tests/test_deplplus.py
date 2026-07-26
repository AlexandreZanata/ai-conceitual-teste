"""Contract: Wave AD4 H-DEPLPLUS — DEPL one-pagers + smoke for AC+AD."""

from __future__ import annotations

from deplplus_ops import (
    AD_STACK_MARKERS,
    APP_PAGE_NAMES,
    DEPL_AD_PAGE,
    DEPLPLUS_ID,
    DEPLPLUS_N,
    MIN_PAGES,
    decide_deplplus,
    depl_ad_body,
    deplplus_stats,
    one_pager_body,
    page_sync_report,
    score_deplplus_trial,
    select_app,
)
from appplus_ops import app_by_id, claim_is_honest


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8.6 / §13.1 AD4 H-DEPLPLUS
    assert DEPLPLUS_ID == "H-DEPLPLUS"
    assert DEPLPLUS_N == 10
    assert MIN_PAGES == 4
    assert len(APP_PAGE_NAMES) == 3
    assert DEPL_AD_PAGE.endswith("depl-ad.md")
    assert "H-ROUTEPLUS" in AD_STACK_MARKERS


def test_given_app_one_pager_when_sync_then_ok() -> None:
    body = one_pager_body(app_by_id("app-howto"))
    rep = page_sync_report("docs/results/nano-lm/app-howto.md", body)
    assert rep["ok"] is True
    assert "H-DEPLPLUS" in body
    assert "npm run nano:deplplus" in body
    assert claim_is_honest(str(app_by_id("app-howto")["claim"])) is True


def test_given_depl_ad_when_sync_then_ok() -> None:
    body = depl_ad_body()
    rep = page_sync_report(DEPL_AD_PAGE, body)
    assert rep["ok"] is True
    assert "H-HARDPARA" in body and "H-COMPOSE" in body


def test_given_missing_marker_when_sync_then_not_ok() -> None:
    rep = page_sync_report("x.md", "# stub\nNot an open chat LM.\n")
    assert rep["ok"] is False
    assert len(rep["missing"]) > 0


def test_given_correct_serve_when_score_then_hit() -> None:
    selected = select_app("howto")
    score, err, notes = score_deplplus_trial(
        mode="SEMWRAP_LOOKUP",
        completion="gold",
        expected_gold="gold",
        lookup_kind="TRUE_HIT",
        selected=selected,
        item_app_id="howto",
    )
    assert score == 9.0 and err is False
    assert any("selected=app-howto" in n for n in notes)


def test_given_wrong_surface_when_score_then_error() -> None:
    selected = select_app("howto")
    score, err, notes = score_deplplus_trial(
        mode="SEMWRAP_LOOKUP",
        completion="gold",
        expected_gold="gold",
        lookup_kind="TRUE_HIT",
        selected=selected,
        item_app_id="long-doc",
    )
    assert score == 0.0 and err is True
    assert any("DEPLOY_ROUTE_MISS" in n for n in notes)


def test_given_good_stats_when_decide_then_promote() -> None:
    stats = deplplus_stats(
        [9.0] * 10,
        [False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        n_pages_ok=4,
        n_pages=4,
        claims_ok=True,
        n_fix=0,
    )
    assert decide_deplplus(stats) == "PROMOTE"


def test_given_docs_miss_when_decide_then_hold() -> None:
    stats = deplplus_stats(
        [9.0] * 10,
        [False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        n_pages_ok=2,
        n_pages=4,
        claims_ok=True,
        n_fix=0,
    )
    assert decide_deplplus(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = deplplus_stats(
        [9.0] * 9 + [0.0],
        [False] * 9 + [True],
        n_true_hit=9,
        n_false_hit=1,
        n_miss=0,
        n_pages_ok=4,
        n_pages=4,
        claims_ok=True,
        n_fix=1,
    )
    assert decide_deplplus(stats) == "KILL"
