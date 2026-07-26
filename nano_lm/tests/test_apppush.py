"""Contract: Wave AI5 H-APPPUSH — dual-arm apps + DEPL-AI honesty."""

from __future__ import annotations

from apppush_ops import (
    APPLIFT_GEN_MEAN,
    APPPUSH_APPS,
    APPPUSH_ID,
    APPPUSH_N,
    MIN_APPS,
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    MIN_PAGES,
    SERVEALIGN_MEAN,
    app_by_id,
    app_dual_stats,
    apppush_stats,
    claim_is_honest,
    decide_app,
    decide_apppush,
    depl_ai_body,
    one_pager_body,
    page_sync_report,
    route_item,
    score_apppush_gen,
    score_apppush_lookup,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AI5 H-APPPUSH
    assert APPPUSH_ID == "H-APPPUSH"
    assert APPPUSH_N == 10
    assert MIN_APPS == 3
    assert MIN_PAGES == 4
    assert MIN_LOOKUP_MEAN == 7.0
    assert MIN_GEN_MEAN == 5.0
    assert APPLIFT_GEN_MEAN == 1.0
    assert SERVEALIGN_MEAN == 3.4
    ids = {a["app_id"] for a in APPPUSH_APPS}
    assert ids == {"app-known", "app-howto", "app-longdoc"}


def test_given_howto_when_route_then_only_howto() -> None:
    app = app_by_id("app-howto")
    assert route_item(app, "howto")["in_scope"] is True
    assert route_item(app, "known-ask")["in_scope"] is False


def test_given_claims_when_check_then_honest() -> None:
    for app in APPPUSH_APPS:
        assert claim_is_honest(str(app["claim"])) is True


def test_given_one_pager_when_body_then_dual_arm_and_honesty() -> None:
    body = one_pager_body(app_by_id("app-howto"))
    assert "LOOKUP" in body and "GENERATE" in body
    assert "npm run nano:apppush" in body
    assert "Not an open chat LM" in body
    assert "H-APPPUSH" in body
    assert "H-FASTPUSH" in body
    report = page_sync_report(
        "docs/results/nano-lm/apppush-howto.md", body
    )
    assert report["ok"] is True, report["missing"]


def test_given_depl_ai_when_body_then_sync_ok() -> None:
    body = depl_ai_body()
    assert "DEPL-AI" in body
    assert "LOOKUP" in body and "GENERATE" in body
    report = page_sync_report("docs/results/nano-lm/depl-ai.md", body)
    assert report["ok"] is True, report["missing"]


def test_given_lookup_serve_when_score_then_not_iq() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    route = {"in_scope": True, "route": "SERVE"}
    score, err, notes = score_apppush_lookup(
        mode="WRAP_LOOKUP",
        completion="gold",
        expected_gold="gold",
        lookup_kind="TRUE_HIT",
        route=route,
        payload=payload,
    )
    assert score >= 8.0 and err is False
    assert any("not generative IQ" in n for n in notes)


def test_given_gen_serve_zero_wall_when_score_then_error() -> None:
    payload = {"mode": "ASKFAST_CACHE", "wall_ms": 0.0, "n_new": 0}
    route = {"in_scope": True, "route": "SERVE"}
    _score, err, notes = score_apppush_gen(
        completion="x",
        expected_gold="gold",
        route=route,
        payload=payload,
    )
    assert err is True
    assert any("telemetry" in n.lower() or "wall" in n.lower() for n in notes)


def test_given_expose_lookup_low_gen_when_decide_then_hold() -> None:
    stats = app_dual_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[8.0] * 7 + [4.0] * 3,
        gen_errors=[False] * 7 + [True] * 3,
        serve_gen_scores=[4.0, 4.0, 4.0],
        n_true_hit=3,
        n_false_hit=0,
        n_lookup_labeled=3,
        n_gen_wall_ok=3,
        n_in_scope=3,
        claim_ok=True,
        one_pager_ok=True,
    )
    assert stats["pass_lookup"] is True
    assert stats["pass_gen"] is False
    assert stats["beats_applift_gen"] is True
    assert decide_app(stats) == "HOLD"


def test_given_wave_expose_no_gen_when_decide_then_hold() -> None:
    apps = [
        {
            "app_id": "app-known",
            "decision": "HOLD",
            "lookup_mean": 9.0,
            "gen_mean": 4.0,
            "dual_arm_ok": True,
        },
        {
            "app_id": "app-howto",
            "decision": "HOLD",
            "lookup_mean": 9.0,
            "gen_mean": 4.0,
            "dual_arm_ok": True,
        },
        {
            "app_id": "app-longdoc",
            "decision": "HOLD",
            "lookup_mean": 9.0,
            "gen_mean": 4.0,
            "dual_arm_ok": True,
        },
    ]
    wave = apppush_stats(apps, n_pages_ok=4, n_pages=4)
    assert wave["pass_expose"] is True
    assert wave["pass_lookup"] is True
    assert wave["pass_gen"] is False
    assert wave["beats_applift_gen"] is True
    assert decide_apppush(wave) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = app_dual_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[4.0] * 10,
        gen_errors=[True] * 10,
        serve_gen_scores=[4.0] * 5,
        n_true_hit=4,
        n_false_hit=1,
        n_lookup_labeled=5,
        n_gen_wall_ok=5,
        n_in_scope=5,
        claim_ok=True,
        one_pager_ok=True,
    )
    assert decide_app(stats) == "KILL"
