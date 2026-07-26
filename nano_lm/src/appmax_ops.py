"""Wave AE4 H-APPMAX: stronger apps + optional route surface + DEPL-AE."""

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
    "APPMAX_ID",
    "APPMAX_N",
    "MIN_APPS",
    "MIN_PAGES",
    "REQUIRED_HOWTO",
    "REQUIRED_ROUTE",
    "APPPLUS_HOWTO_MEAN",
    "AE_STACK_MARKERS",
    "FORBIDDEN_MARKERS",
    "DEPL_AE_PAGE",
    "SURFACE_TO_APP",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "APPMAX_APPS",
    "app_by_id",
    "select_app",
    "claim_is_honest",
    "route_item",
    "honest_out_of_scope_text",
    "score_realapp_trial",
    "app_stats",
    "decide_app",
    "one_pager_body",
    "depl_ae_body",
    "page_sync_report",
    "appmax_stats",
    "decide_appmax",
]

APPMAX_ID = "H-APPMAX"
APPMAX_N = 10
MIN_APPS = 4  # known + longdoc + howto + route (4th)
MIN_PAGES = 5  # 4 apps + depl-ae
REQUIRED_HOWTO = "app-howto"
REQUIRED_ROUTE = "app-route"
# Evidence: docs/results/nano-lm/formal-happplus-appplus.md app-howto mean
APPPLUS_HOWTO_MEAN = 8.3
DEPL_AE_PAGE = "docs/results/nano-lm/depl-ae.md"

AE_STACK_MARKERS: tuple[str, ...] = (
    "H-CTXMAX",
    "H-SMARTMAX",
    "H-FASTMAX",
    "H-APPMAX",
)

FORBIDDEN_MARKERS: tuple[str, ...] = (
    "STREAM",
    "KVCACHE-Q",
    "GENCACHE",
    "ZPREF",
)

SURFACE_TO_APP: Mapping[str, str] = {
    "known-ask": "app-known",
    "howto": "app-howto",
    "long-doc": "app-longdoc",
}

APPMAX_APPS: tuple[dict[str, Any], ...] = (
    {
        "app_id": "app-known",
        "surface": "known-ask",
        "accepts": frozenset({"known-ask", "howto"}),
        "spine": ("H-SEMWRAP", "H-ASKFAST", "H-FASTMAX"),
        "stack": "askfast",
        "claim": (
            "scoped known / near-known held-out ask via FASTMAX — "
            "not open chat LM"
        ),
        "one_pager": "docs/results/nano-lm/app-known.md",
        "npm": "npm run nano:appmax -- --app app-known",
    },
    {
        "app_id": "app-longdoc",
        "surface": "long-doc",
        "accepts": frozenset({"long-doc", "known-ask", "howto"}),
        "spine": ("H-CTXMAX", "H-SUMCACHE", "H-ROLL", "H-SEMWRAP"),
        "stack": "ctxmax",
        "claim": (
            "ask over curated multi-doc ctx via CTXMAX — "
            "not STREAM / open chat"
        ),
        "one_pager": "docs/results/nano-lm/app-longdoc.md",
        "npm": "npm run nano:appmax -- --app app-longdoc",
    },
    {
        "app_id": "app-howto",
        "surface": "howto",
        "accepts": frozenset({"howto"}),
        "spine": ("H-SMARTMAX", "H-ASKSMART", "H-SEMWRAP", "H-FASTMAX"),
        "stack": "howto",
        "claim": (
            "stronger scoped procedural howto from curated sources — "
            "not open chat LM"
        ),
        "one_pager": "docs/results/nano-lm/app-howto.md",
        "npm": "npm run nano:appmax -- --app app-howto",
    },
    {
        "app_id": "app-route",
        "surface": "cross-app-route",
        "accepts": frozenset({"known-ask", "howto", "long-doc"}),
        "spine": ("H-ROUTEPLUS", "H-SMARTMAX", "H-FASTMAX", "H-APPMAX"),
        "stack": "route",
        "claim": (
            "scoped auto-route of AE pack to packaged app surfaces — "
            "not open chat LM"
        ),
        "one_pager": "docs/results/nano-lm/app-route.md",
        "npm": "npm run nano:appmax -- --app app-route",
    },
)


def app_by_id(app_id: str) -> dict[str, Any]:
    for app in APPMAX_APPS:
        if app["app_id"] == app_id:
            return dict(app)
    raise KeyError(f"unknown appmax id: {app_id}")


def select_app(item_app_id: str) -> dict[str, Any]:
    """
    GIVEN held-out item surface
    WHEN cross-app routing for app-route / DEPL-AE
    THEN return the canonical APPMAX packaged app (not app-route itself).
    """
    key = str(item_app_id)
    if key not in SURFACE_TO_APP:
        raise KeyError(f"no APPMAX app for surface {key}")
    return app_by_id(SURFACE_TO_APP[key])


def one_pager_body(app: Mapping[str, Any]) -> str:
    """Public one-pager markdown for an APPMAX packaged app."""
    spine = " → ".join(str(x) for x in app.get("spine") or ())
    return "\n".join(
        [
            f"# {app['app_id']} — scoped nano app",
            "",
            f"> Wave AE4 **H-APPMAX** · Spine: `{spine}`",
            f"> Claim: {app['claim']}",
            "",
            "## Job",
            "",
            f"Surface `{app['surface']}` — runnable path for AE0 held-out HITL.",
            "",
            "## Run",
            "",
            "```bash",
            str(app["npm"]),
            "npm run nano:appmax",
            "```",
            "",
            "## AE stack (PROMOTE)",
            "",
            "- H-CTXMAX · H-SMARTMAX · H-FASTMAX · H-APPMAX",
            "",
            "## Honesty",
            "",
            "- Not an open chat LM.",
            "- In-lab curated sources only.",
            "- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF revival.",
            "",
        ]
    )


def depl_ae_body() -> str:
    """Overview one-pager for AE packaged deploy routes."""
    lines = [
        "# DEPL-AE — AE packaged deploy (**H-APPMAX**)",
        "",
        "> Wave AE4 **H-APPMAX** · Inherit APPPLUS + AE PROMOTE stack",
        "> Claim: scoped packaged apps on AE stack — not open chat LM",
        "",
        "## Routes",
        "",
        "| Surface | App | npm |",
        "|---------|-----|-----|",
    ]
    for app in APPMAX_APPS:
        lines.append(
            f"| `{app['surface']}` | `{app['app_id']}` | `{app['npm']}` |"
        )
    lines.extend(
        [
            "",
            "## AE stack (PROMOTE)",
            "",
            "- H-CTXMAX · H-SMARTMAX · H-FASTMAX · H-APPMAX",
            "",
            "## Run",
            "",
            "```bash",
            "npm run nano:appmax",
            "```",
            "",
            "## Honesty",
            "",
            "- Not an open chat LM.",
            "- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF · QI · MIXD.",
            "- Never invent serve hyps that revive KILLs.",
            "",
        ]
    )
    return "\n".join(lines)


def page_sync_report(path: str, text: str) -> dict[str, Any]:
    """
    GIVEN one-pager path + body
    WHEN checking DEPL-AE sync
    THEN require honesty + AE stack markers + forbidden list named.
    """
    body = str(text)
    miss: list[str] = []
    low = body.lower()
    if "not an open chat" not in low and "not open chat" not in low:
        miss.append("honest_not_open_chat")
    for m in AE_STACK_MARKERS:
        if m not in body:
            miss.append(m)
    for m in FORBIDDEN_MARKERS:
        if m not in body:
            miss.append(f"forbidden:{m}")
    if "npm run nano:appmax" not in body:
        miss.append("npm_appmax")
    return {"path": path, "ok": len(miss) == 0, "missing": miss}


def appmax_stats(
    app_results: Sequence[Mapping[str, Any]],
    *,
    n_pages_ok: int,
    n_pages: int,
) -> dict[str, Any]:
    """
    GIVEN per-app decisions + DEPL page sync
    WHEN summarizing H-APPMAX
    THEN require howto↑ + known/longdoc/route green + DEPL docs + no KILL.
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
    route = by_id.get(REQUIRED_ROUTE) or {}
    howto_mean = float(howto.get("mean", 0.0))
    howto_ok = str(howto.get("decision")) == "PROMOTE"
    known_ok = str(known.get("decision")) == "PROMOTE"
    long_ok = str(longdoc.get("decision")) == "PROMOTE"
    route_ok = str(route.get("decision")) == "PROMOTE"
    howto_up = howto_mean >= float(APPPLUS_HOWTO_MEAN)
    docs_ok = int(n_pages_ok) >= MIN_PAGES and int(n_pages) >= MIN_PAGES
    return {
        "n_apps": n,
        "n_promote": int(n_promote),
        "n_hold": int(n_hold),
        "n_kill": int(n_kill),
        "min_apps": MIN_APPS,
        "mean_across_apps": mean,
        "howto_promote": howto_ok,
        "howto_mean": howto_mean,
        "howto_up": howto_up,
        "known_green": known_ok,
        "longdoc_green": long_ok,
        "route_green": route_ok,
        "n_pages_ok": int(n_pages_ok),
        "n_pages": int(n_pages),
        "depl_ok": docs_ok,
        "pass_product": (
            howto_ok
            and howto_up
            and known_ok
            and long_ok
            and route_ok
            and docs_ok
            and n_kill == 0
            and n >= MIN_APPS
        ),
    }


def decide_appmax(stats: Mapping[str, Any]) -> str:
    """
    GIVEN APPMAX stats
    WHEN applying §5 AE4 gate
    THEN PROMOTE if howto↑ + 4 apps green + DEPL;
         HOLD if no KILL but soft miss; KILL if any KILL.
    """
    if int(stats.get("n_kill", 0)) > 0:
        return "KILL"
    if bool(stats.get("pass_product")):
        return "PROMOTE"
    if int(stats.get("n_apps", 0)) >= MIN_APPS:
        return "HOLD"
    return "KILL"
