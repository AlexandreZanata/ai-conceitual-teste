"""Wave AF4 H-APPULTRA: stronger apps + compose 5th + DEPL-AF."""

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
    "APPULTRA_ID",
    "APPULTRA_N",
    "MIN_APPS",
    "MIN_PAGES",
    "REQUIRED_HOWTO",
    "REQUIRED_ROUTE",
    "REQUIRED_COMPOSE",
    "APPMAX_HOWTO_MEAN",
    "APPMAX_MEAN_ACROSS",
    "AF_STACK_MARKERS",
    "FORBIDDEN_MARKERS",
    "DEPL_AF_PAGE",
    "SURFACE_TO_APP",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "APPULTRA_APPS",
    "app_by_id",
    "select_app",
    "claim_is_honest",
    "route_item",
    "honest_out_of_scope_text",
    "score_realapp_trial",
    "app_stats",
    "decide_app",
    "one_pager_body",
    "depl_af_body",
    "page_sync_report",
    "appultra_stats",
    "decide_appultra",
]

APPULTRA_ID = "H-APPULTRA"
APPULTRA_N = 10
MIN_APPS = 5  # known + longdoc + howto + route + compose
MIN_PAGES = 6  # 5 apps + depl-af
REQUIRED_HOWTO = "app-howto"
REQUIRED_ROUTE = "app-route"
REQUIRED_COMPOSE = "app-compose"
# Evidence: results/nano-lm/wave-ae/appmax_summary.json
APPMAX_HOWTO_MEAN = 8.3
APPMAX_MEAN_ACROSS = 8.725
DEPL_AF_PAGE = "docs/results/nano-lm/depl-af.md"

AF_STACK_MARKERS: tuple[str, ...] = (
    "H-CTXULTRA",
    "H-SMARTULTRA",
    "H-FASTULTRA",
    "H-APPULTRA",
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

APPULTRA_APPS: tuple[dict[str, Any], ...] = (
    {
        "app_id": "app-known",
        "surface": "known-ask",
        "accepts": frozenset({"known-ask", "howto"}),
        "spine": ("H-SEMWRAP", "H-ASKFAST", "H-FASTULTRA"),
        "stack": "askfast",
        "claim": (
            "scoped known / near-known held-out ask via FASTULTRA — "
            "not open chat LM"
        ),
        "one_pager": "docs/results/nano-lm/appultra-known.md",
        "npm": "npm run nano:appultra -- --app app-known",
    },
    {
        "app_id": "app-longdoc",
        "surface": "long-doc",
        "accepts": frozenset({"long-doc", "known-ask", "howto"}),
        "spine": ("H-CTXULTRA", "H-SUMCACHE", "H-ROLL", "H-SEMWRAP"),
        "stack": "ctxultra",
        "claim": (
            "ask over curated triple-doc ctx via CTXULTRA — "
            "not STREAM / open chat"
        ),
        "one_pager": "docs/results/nano-lm/appultra-longdoc.md",
        "npm": "npm run nano:appultra -- --app app-longdoc",
    },
    {
        "app_id": "app-howto",
        "surface": "howto",
        "accepts": frozenset({"howto"}),
        "spine": ("H-SMARTULTRA", "H-ASKSMART", "H-SEMWRAP", "H-FASTULTRA"),
        "stack": "howto",
        "claim": (
            "stronger scoped procedural howto from curated sources — "
            "not open chat LM"
        ),
        "one_pager": "docs/results/nano-lm/appultra-howto.md",
        "npm": "npm run nano:appultra -- --app app-howto",
    },
    {
        "app_id": "app-route",
        "surface": "cross-app-route",
        "accepts": frozenset({"known-ask", "howto", "long-doc"}),
        "spine": ("H-ROUTEPLUS", "H-SMARTULTRA", "H-FASTULTRA", "H-APPULTRA"),
        "stack": "route",
        "claim": (
            "scoped auto-route of AF pack to packaged app surfaces — "
            "not open chat LM"
        ),
        "one_pager": "docs/results/nano-lm/appultra-route.md",
        "npm": "npm run nano:appultra -- --app app-route",
    },
    {
        "app_id": "app-compose",
        "surface": "compose-multidoc",
        "accepts": frozenset({"known-ask", "howto", "long-doc"}),
        "spine": ("H-CTXULTRA", "H-COMPOSE", "H-SEMWRAP", "H-APPULTRA"),
        "stack": "compose",
        "claim": (
            "scoped multi-doc compose on AF held-out pack via CTXULTRA — "
            "not open chat LM"
        ),
        "one_pager": "docs/results/nano-lm/appultra-compose.md",
        "npm": "npm run nano:appultra -- --app app-compose",
    },
)


def app_by_id(app_id: str) -> dict[str, Any]:
    for app in APPULTRA_APPS:
        if app["app_id"] == app_id:
            return dict(app)
    raise KeyError(f"unknown appultra id: {app_id}")


def select_app(item_app_id: str) -> dict[str, Any]:
    """
    GIVEN held-out item surface
    WHEN cross-app routing for app-route / DEPL-AF
    THEN return the canonical APPULTRA packaged app (not route/compose).
    """
    key = str(item_app_id)
    if key not in SURFACE_TO_APP:
        raise KeyError(f"no APPULTRA app for surface {key}")
    return app_by_id(SURFACE_TO_APP[key])


def one_pager_body(app: Mapping[str, Any]) -> str:
    """Public one-pager markdown for an APPULTRA packaged app."""
    spine = " → ".join(str(x) for x in app.get("spine") or ())
    return "\n".join(
        [
            f"# {app['app_id']} — scoped nano app (APPULTRA)",
            "",
            f"> Wave AF4 **H-APPULTRA** · Spine: `{spine}`",
            f"> Claim: {app['claim']}",
            "",
            "## Job",
            "",
            f"Surface `{app['surface']}` — runnable path for AF0 held-out HITL.",
            "",
            "## Run",
            "",
            "```bash",
            str(app["npm"]),
            "npm run nano:appultra",
            "```",
            "",
            "## AF stack (PROMOTE)",
            "",
            "- H-CTXULTRA · H-SMARTULTRA · H-FASTULTRA · H-APPULTRA",
            "",
            "## Honesty",
            "",
            "- Not an open chat LM.",
            "- In-lab curated sources only.",
            "- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF revival.",
            "",
        ]
    )


def depl_af_body() -> str:
    """Overview one-pager for AF packaged deploy routes."""
    lines = [
        "# DEPL-AF — AF packaged deploy (**H-APPULTRA**)",
        "",
        "> Wave AF4 **H-APPULTRA** · Inherit APPMAX + AF ULTRA stack",
        "> Claim: scoped packaged apps on AF stack — not open chat LM",
        "",
        "## Routes",
        "",
        "| Surface | App | npm |",
        "|---------|-----|-----|",
    ]
    for app in APPULTRA_APPS:
        lines.append(
            f"| `{app['surface']}` | `{app['app_id']}` | `{app['npm']}` |"
        )
    lines.extend(
        [
            "",
            "## AF stack (PROMOTE)",
            "",
            "- H-CTXULTRA · H-SMARTULTRA · H-FASTULTRA · H-APPULTRA",
            "",
            "## Run",
            "",
            "```bash",
            "npm run nano:appultra",
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
    WHEN checking DEPL-AF sync
    THEN require honesty + AF stack markers + forbidden list named.
    """
    body = str(text)
    miss: list[str] = []
    low = body.lower()
    if "not an open chat" not in low and "not open chat" not in low:
        miss.append("honest_not_open_chat")
    for m in AF_STACK_MARKERS:
        if m not in body:
            miss.append(m)
    for m in FORBIDDEN_MARKERS:
        if m not in body:
            miss.append(f"forbidden:{m}")
    if "npm run nano:appultra" not in body:
        miss.append("npm_appultra")
    return {"path": path, "ok": len(miss) == 0, "missing": miss}


def appultra_stats(
    app_results: Sequence[Mapping[str, Any]],
    *,
    n_pages_ok: int,
    n_pages: int,
) -> dict[str, Any]:
    """
    GIVEN per-app decisions + DEPL page sync
    WHEN summarizing H-APPULTRA
    THEN require howto↑ vs APPMAX + 5 apps green + mean↑ + DEPL.
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
    compose = by_id.get(REQUIRED_COMPOSE) or {}
    howto_mean = float(howto.get("mean", 0.0))
    howto_ok = str(howto.get("decision")) == "PROMOTE"
    known_ok = str(known.get("decision")) == "PROMOTE"
    long_ok = str(longdoc.get("decision")) == "PROMOTE"
    route_ok = str(route.get("decision")) == "PROMOTE"
    compose_ok = str(compose.get("decision")) == "PROMOTE"
    howto_up = howto_mean >= float(APPMAX_HOWTO_MEAN)
    mean_up = mean >= float(APPMAX_MEAN_ACROSS)
    docs_ok = int(n_pages_ok) >= MIN_PAGES and int(n_pages) >= MIN_PAGES
    return {
        "n_apps": n,
        "n_promote": int(n_promote),
        "n_hold": int(n_hold),
        "n_kill": int(n_kill),
        "min_apps": MIN_APPS,
        "mean_across_apps": mean,
        "appmax_mean_across": float(APPMAX_MEAN_ACROSS),
        "howto_promote": howto_ok,
        "howto_mean": howto_mean,
        "howto_up": howto_up,
        "mean_up": mean_up,
        "known_green": known_ok,
        "longdoc_green": long_ok,
        "route_green": route_ok,
        "compose_green": compose_ok,
        "n_pages_ok": int(n_pages_ok),
        "n_pages": int(n_pages),
        "depl_ok": docs_ok,
        "pass_product": (
            howto_ok
            and howto_up
            and mean_up
            and known_ok
            and long_ok
            and route_ok
            and compose_ok
            and docs_ok
            and n_kill == 0
            and n >= MIN_APPS
        ),
    }


def decide_appultra(stats: Mapping[str, Any]) -> str:
    """
    GIVEN APPULTRA stats
    WHEN applying §5 AF4 gate
    THEN PROMOTE if howto↑ + mean↑ + 5 apps green + DEPL;
         HOLD if no KILL but soft miss; KILL if any KILL.
    """
    if int(stats.get("n_kill", 0)) > 0:
        return "KILL"
    if bool(stats.get("pass_product")):
        return "PROMOTE"
    if int(stats.get("n_apps", 0)) >= MIN_APPS:
        return "HOLD"
    return "KILL"
