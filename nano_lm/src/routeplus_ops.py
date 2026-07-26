"""Wave AD3 H-ROUTEPLUS: cross-app route + honest OOS refuse."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from appplus_ops import APPPLUS_APPS, app_by_id
from realapp_ops import (
    claim_is_honest,
    honest_out_of_scope_text,
    route_item,
    score_realapp_trial,
)
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "ROUTEPLUS_ID",
    "ROUTEPLUS_N",
    "MIN_CORRECT",
    "MIN_OOS_HONEST",
    "SURFACE_TO_APP",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "claim_is_honest",
    "route_item",
    "honest_out_of_scope_text",
    "select_app",
    "oos_probe_app",
    "score_routeplus_trial",
    "routeplus_stats",
    "decide_routeplus",
]

ROUTEPLUS_ID = "H-ROUTEPLUS"
ROUTEPLUS_N = 10
MIN_CORRECT = 10  # §13.1 AD3 — correct app route
MIN_OOS_HONEST = 10  # honest OOS refuse on wrong app

SURFACE_TO_APP: Mapping[str, str] = {
    "known-ask": "app-known",
    "howto": "app-howto",
    "long-doc": "app-longdoc",
}

# When every APPPLUS app accepts a surface (howto), use a narrow probe.
_OOS_FALLBACK: dict[str, Any] = {
    "app_id": "app-probe-longdoc-only",
    "surface": "long-doc",
    "accepts": frozenset({"long-doc"}),
    "claim": "scoped long-doc probe — not open chat LM",
}


def select_app(item_app_id: str) -> dict[str, Any]:
    """
    GIVEN held-out item surface app_id
    WHEN cross-app routing
    THEN return the canonical APPPLUS packaged app.
    """
    key = str(item_app_id)
    if key not in SURFACE_TO_APP:
        raise KeyError(f"no ROUTEPLUS app for surface {key}")
    return app_by_id(SURFACE_TO_APP[key])


def oos_probe_app(item_app_id: str) -> dict[str, Any]:
    """
    GIVEN item surface
    WHEN choosing a wrong packaged app for OOS honesty
    THEN return an app that does not accept the surface.
    """
    surface = str(item_app_id)
    for app in APPPLUS_APPS:
        if surface not in frozenset(app.get("accepts") or ()):
            return dict(app)
    return dict(_OOS_FALLBACK)


def score_routeplus_trial(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    selected: Mapping[str, Any],
    item_app_id: str,
    oos_completion: str,
    oos_app: Mapping[str, Any],
) -> tuple[float, bool, list[str], bool, bool]:
    """
    GIVEN auto-selected app SERVE + wrong-app OOS probe
    WHEN scoring AD3 HITL
    THEN require correct route ∧ honest OOS; FALSE_HIT→0.
    """
    notes: list[str] = []
    expected_id = SURFACE_TO_APP.get(str(item_app_id))
    correct = str(selected.get("app_id")) == str(expected_id)
    notes.append(f"selected={selected.get('app_id')}")
    serve_route = route_item(selected, item_app_id)
    if not correct or not bool(serve_route.get("in_scope")):
        notes.append("WRONG_APP_ROUTE")
        return 0.0, True, notes, False, False

    oos_route = route_item(oos_app, item_app_id)
    if bool(oos_route.get("in_scope")):
        notes.append("OOS_PROBE_NOT_OUT")
        return 2.0, True, notes, True, False
    low = str(oos_completion).lower()
    oos_honest = "out of scope" in low
    if not oos_honest:
        notes.append("FALSE_APP_CLAIM")
        return 0.0, True, notes, True, False
    notes.append("HONEST_OOS")

    score, err, more = score_realapp_trial(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
        route=serve_route,
    )
    notes.extend(more)
    return float(score), bool(err), notes, True, True


def routeplus_stats(
    scores: Sequence[float],
    errors: Sequence[bool],
    *,
    n_true_hit: int,
    n_false_hit: int,
    n_miss: int,
    n_correct_route: int,
    n_oos_honest: int,
    n_false_claim: int,
    n_fix: int,
    claims_ok: bool,
) -> dict[str, Any]:
    if len(scores) != ROUTEPLUS_N or len(errors) != ROUTEPLUS_N:
        raise ValueError(f"ROUTEPLUS requires exactly {ROUTEPLUS_N} trials")
    mean = float(sum(float(s) for s in scores) / float(ROUTEPLUS_N))
    n_err = int(sum(1 for e in errors if e))
    return {
        "n_trials": ROUTEPLUS_N,
        "mean": mean,
        "n_errors": n_err,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_miss": int(n_miss),
        "n_correct_route": int(n_correct_route),
        "n_oos_honest": int(n_oos_honest),
        "n_false_claim": int(n_false_claim),
        "n_fix": int(n_fix),
        "claims_ok": bool(claims_ok),
        "min_correct": MIN_CORRECT,
        "min_oos_honest": MIN_OOS_HONEST,
        "pass_quality": mean >= PASS_MEAN and n_err <= PASS_MAX_ERRORS,
        "pass_route": int(n_correct_route) >= MIN_CORRECT,
        "pass_oos": int(n_oos_honest) >= MIN_OOS_HONEST,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_routeplus(stats: Mapping[str, Any]) -> str:
    """
    GIVEN ROUTEPLUS stats
    WHEN applying §8.6 / §13.1 AD3 gate
    THEN PROMOTE if quality ∧ correct route ∧ honest OOS ∧ claims;
         KILL on false-hit / false claim; else HOLD.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if int(stats.get("n_false_claim", 0)) > 0:
        return "KILL"
    if not bool(stats.get("claims_ok")):
        return "KILL"
    if (
        bool(stats.get("pass_quality"))
        and bool(stats.get("pass_route"))
        and bool(stats.get("pass_oos"))
    ):
        return "PROMOTE"
    if bool(stats.get("pass_quality")):
        return "HOLD"
    return "KILL"
