"""Contract: Wave AD3 H-ROUTEPLUS — cross-app route + honest OOS refuse."""

from __future__ import annotations

from routeplus_ops import (
    MIN_CORRECT,
    MIN_OOS_HONEST,
    ROUTEPLUS_ID,
    ROUTEPLUS_N,
    SURFACE_TO_APP,
    claim_is_honest,
    decide_routeplus,
    honest_out_of_scope_text,
    oos_probe_app,
    routeplus_stats,
    score_routeplus_trial,
    select_app,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8.6 / §13.1 AD3 H-ROUTEPLUS
    assert ROUTEPLUS_ID == "H-ROUTEPLUS"
    assert ROUTEPLUS_N == 10
    assert MIN_CORRECT == 10
    assert MIN_OOS_HONEST == 10
    assert set(SURFACE_TO_APP) == {"known-ask", "howto", "long-doc"}


def test_given_surfaces_when_select_then_canonical_apps() -> None:
    assert select_app("known-ask")["app_id"] == "app-known"
    assert select_app("howto")["app_id"] == "app-howto"
    assert select_app("long-doc")["app_id"] == "app-longdoc"


def test_given_item_when_oos_probe_then_rejects_surface() -> None:
    for surface in ("known-ask", "howto", "long-doc"):
        probe = oos_probe_app(surface)
        assert surface not in frozenset(probe["accepts"])
        assert claim_is_honest(str(probe["claim"])) is True


def test_given_correct_serve_and_oos_when_score_then_ok() -> None:
    selected = select_app("known-ask")
    probe = oos_probe_app("known-ask")
    oos = honest_out_of_scope_text(str(probe["app_id"]), str(probe["surface"]))
    score, err, notes, correct, oos_ok = score_routeplus_trial(
        mode="SEMWRAP_LOOKUP",
        completion="gold answer",
        expected_gold="gold answer",
        lookup_kind="TRUE_HIT",
        selected=selected,
        item_app_id="known-ask",
        oos_completion=oos,
        oos_app=probe,
    )
    assert score == 9.0 and err is False
    assert correct is True and oos_ok is True
    assert any("HONEST_OOS" in n for n in notes)


def test_given_wrong_selected_when_score_then_error() -> None:
    wrong = select_app("howto")
    probe = oos_probe_app("known-ask")
    oos = honest_out_of_scope_text(str(probe["app_id"]), str(probe["surface"]))
    score, err, _notes, correct, oos_ok = score_routeplus_trial(
        mode="SEMWRAP_LOOKUP",
        completion="gold",
        expected_gold="gold",
        lookup_kind="TRUE_HIT",
        selected=wrong,
        item_app_id="known-ask",
        oos_completion=oos,
        oos_app=probe,
    )
    assert score == 0.0 and err is True
    assert correct is False and oos_ok is False


def test_given_oos_leak_when_score_then_false_claim() -> None:
    selected = select_app("long-doc")
    probe = oos_probe_app("long-doc")
    score, err, notes, correct, oos_ok = score_routeplus_trial(
        mode="SEMWRAP_LOOKUP",
        completion="gold",
        expected_gold="gold",
        lookup_kind="TRUE_HIT",
        selected=selected,
        item_app_id="long-doc",
        oos_completion="Sure, here is the answer anyway.",
        oos_app=probe,
    )
    assert score == 0.0 and err is True
    assert correct is True and oos_ok is False
    assert any("FALSE_APP_CLAIM" in n for n in notes)


def test_given_good_stats_when_decide_then_promote() -> None:
    stats = routeplus_stats(
        [9.0] * 10,
        [False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        n_correct_route=10,
        n_oos_honest=10,
        n_false_claim=0,
        n_fix=0,
        claims_ok=True,
    )
    assert decide_routeplus(stats) == "PROMOTE"


def test_given_false_claim_when_decide_then_kill() -> None:
    stats = routeplus_stats(
        [9.0] * 9 + [0.0],
        [False] * 9 + [True],
        n_true_hit=9,
        n_false_hit=0,
        n_miss=0,
        n_correct_route=10,
        n_oos_honest=9,
        n_false_claim=1,
        n_fix=1,
        claims_ok=True,
    )
    assert decide_routeplus(stats) == "KILL"


def test_given_route_miss_when_decide_then_hold() -> None:
    stats = routeplus_stats(
        [9.0] * 10,
        [False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        n_correct_route=9,
        n_oos_honest=10,
        n_false_claim=0,
        n_fix=0,
        claims_ok=True,
    )
    assert stats["pass_route"] is False
    assert decide_routeplus(stats) == "HOLD"
