"""Wave AC4 H-APPPLUS: ship app-howto + keep known/longdoc green."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from realapp_ops import (
    PASS_MAX_ERRORS,
    PASS_MEAN,
    app_stats,
    claim_is_honest,
    decide_app,
    honest_out_of_scope_text,
    route_item,
    score_realapp_trial,
)

__all__ = [
    "APPPLUS_ID",
    "APPPLUS_N",
    "MIN_APPS",
    "REQUIRED_HOWTO",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "APPPLUS_APPS",
    "app_by_id",
    "claim_is_honest",
    "route_item",
    "honest_out_of_scope_text",
    "score_realapp_trial",
    "app_stats",
    "decide_app",
    "one_pager_body",
    "appplus_stats",
    "decide_appplus",
]

APPPLUS_ID = "H-APPPLUS"
APPPLUS_N = 10
MIN_APPS = 3  # known + longdoc + howto
REQUIRED_HOWTO = "app-howto"

APPPLUS_APPS: tuple[dict[str, Any], ...] = (
    {
        "app_id": "app-known",
        "surface": "known-ask",
        "accepts": frozenset({"known-ask", "howto"}),
        "spine": ("H-ZWRAP", "H-SEMWRAP", "H-ASKFAST", "H-FASTPLUS"),
        "stack": "askfast",
        "claim": (
            "scoped known / near-known held-out ask via SEMWRAP — "
            "not open chat LM"
        ),
        "one_pager": "docs/results/nano-lm/app-known.md",
        "npm": "npm run nano:appplus -- --app app-known",
    },
    {
        "app_id": "app-longdoc",
        "surface": "long-doc",
        "accepts": frozenset({"long-doc", "known-ask", "howto"}),
        "spine": ("H-CTXPLUS", "H-LONGAPP", "H-SUMCACHE", "H-ROLL", "H-SEMWRAP"),
        "stack": "longapp",
        "claim": (
            "ask over curated long docs via CTXPLUS/ROLL/SUMCACHE — "
            "not STREAM / open chat"
        ),
        "one_pager": "docs/results/nano-lm/app-longdoc.md",
        "npm": "npm run nano:appplus -- --app app-longdoc",
    },
    {
        "app_id": "app-howto",
        "surface": "howto",
        "accepts": frozenset({"howto"}),
        "spine": ("H-ASKSMART", "H-SEMWRAP", "H-ASKFAST"),
        "stack": "howto",
        "claim": (
            "scoped procedural howto from curated sources — "
            "not open chat LM"
        ),
        "one_pager": "docs/results/nano-lm/app-howto.md",
        "npm": "npm run nano:appplus -- --app app-howto",
    },
)


def app_by_id(app_id: str) -> dict[str, Any]:
    for app in APPPLUS_APPS:
        if app["app_id"] == app_id:
            return dict(app)
    raise KeyError(f"unknown appplus id: {app_id}")


def one_pager_body(app: Mapping[str, Any]) -> str:
    """Public one-pager markdown for an APPPLUS packaged app."""
    spine = " → ".join(str(x) for x in app.get("spine") or ())
    return "\n".join(
        [
            f"# {app['app_id']} — scoped nano app",
            "",
            f"> Wave AC4 **H-APPPLUS** · Spine: `{spine}`",
            f"> Claim: {app['claim']}",
            "",
            "## Job",
            "",
            f"Surface `{app['surface']}` — runnable path for held-out HITL asks.",
            "",
            "## Run",
            "",
            "```bash",
            str(app["npm"]),
            "```",
            "",
            "## Honesty",
            "",
            "- Not an open chat LM.",
            "- In-lab curated sources only.",
            "- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF revival.",
            "",
        ]
    )


def appplus_stats(app_results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """
    GIVEN per-app decisions
    WHEN summarizing H-APPPLUS
    THEN require app-howto PROMOTE + known/longdoc green + no KILL.
    """
    n = len(app_results)
    by_id = {str(a.get("app_id")): a for a in app_results}
    n_promote = sum(1 for a in app_results if a.get("decision") == "PROMOTE")
    n_kill = sum(1 for a in app_results if a.get("decision") == "KILL")
    n_hold = sum(1 for a in app_results if a.get("decision") == "HOLD")
    means = [float(a.get("mean", 0.0)) for a in app_results]
    mean = float(sum(means) / len(means)) if means else 0.0
    howto = by_id.get(REQUIRED_HOWTO) or {}
    known = by_id.get("app-known") or {}
    longdoc = by_id.get("app-longdoc") or {}
    howto_ok = str(howto.get("decision")) == "PROMOTE"
    known_ok = str(known.get("decision")) == "PROMOTE"
    long_ok = str(longdoc.get("decision")) == "PROMOTE"
    return {
        "n_apps": n,
        "n_promote": int(n_promote),
        "n_hold": int(n_hold),
        "n_kill": int(n_kill),
        "min_apps": MIN_APPS,
        "mean_across_apps": mean,
        "howto_promote": howto_ok,
        "known_green": known_ok,
        "longdoc_green": long_ok,
        "pass_product": (
            howto_ok
            and known_ok
            and long_ok
            and n_kill == 0
            and n >= MIN_APPS
        ),
    }


def decide_appplus(stats: Mapping[str, Any]) -> str:
    """
    GIVEN APPPLUS stats
    WHEN applying §8.5 / §12.1 AC4 gate
    THEN PROMOTE if howto+known+longdoc green;
         HOLD if no KILL but soft miss; KILL if any KILL.
    """
    if int(stats.get("n_kill", 0)) > 0:
        return "KILL"
    if bool(stats.get("pass_product")):
        return "PROMOTE"
    if int(stats.get("n_apps", 0)) >= MIN_APPS:
        return "HOLD"
    return "KILL"
