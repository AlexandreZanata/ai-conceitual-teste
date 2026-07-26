"""Wave AD4 H-DEPLPLUS: DEPL one-pagers + smoke for AC+AD stack."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from appplus_ops import APPPLUS_APPS, app_by_id
from realapp_ops import claim_is_honest, route_item, score_realapp_trial
from routeplus_ops import select_app
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "DEPLPLUS_ID",
    "DEPLPLUS_N",
    "MIN_PAGES",
    "AD_STACK_MARKERS",
    "FORBIDDEN_MARKERS",
    "APP_PAGE_NAMES",
    "DEPL_AD_PAGE",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "claim_is_honest",
    "select_app",
    "route_item",
    "score_realapp_trial",
    "app_by_id",
    "one_pager_body",
    "depl_ad_body",
    "page_sync_report",
    "score_deplplus_trial",
    "deplplus_stats",
    "decide_deplplus",
]

DEPLPLUS_ID = "H-DEPLPLUS"
DEPLPLUS_N = 10
MIN_PAGES = 4  # 3 APPPLUS apps + depl-ad overview
DEPL_AD_PAGE = "docs/results/nano-lm/depl-ad.md"
APP_PAGE_NAMES: tuple[str, ...] = (
    "docs/results/nano-lm/app-known.md",
    "docs/results/nano-lm/app-howto.md",
    "docs/results/nano-lm/app-longdoc.md",
)

AD_STACK_MARKERS: tuple[str, ...] = (
    "H-HARDPARA",
    "H-COMPOSE",
    "H-ROUTEPLUS",
    "H-APPPLUS",
    "H-DEPLPLUS",
)

FORBIDDEN_MARKERS: tuple[str, ...] = (
    "STREAM",
    "KVCACHE-Q",
    "GENCACHE",
    "ZPREF",
)


def one_pager_body(app: Mapping[str, Any]) -> str:
    """Public APPPLUS one-pager refreshed for Wave AD DEPLPLUS."""
    spine = " → ".join(str(x) for x in app.get("spine") or ())
    return "\n".join(
        [
            f"# {app['app_id']} — scoped nano app",
            "",
            f"> Wave AD4 **H-DEPLPLUS** · Parent AC4 **H-APPPLUS** · Spine: `{spine}`",
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
            "npm run nano:deplplus",
            "```",
            "",
            "## AD stack (PROMOTE)",
            "",
            "- H-HARDPARA · H-COMPOSE · H-ROUTEPLUS · H-APPPLUS · H-DEPLPLUS",
            "",
            "## Honesty",
            "",
            "- Not an open chat LM.",
            "- In-lab curated sources only.",
            "- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF revival.",
            "",
        ]
    )


def depl_ad_body() -> str:
    """Overview one-pager for AC+AD deploy routes."""
    lines = [
        "# DEPL-AD — AC+AD packaged deploy (**H-DEPLPLUS**)",
        "",
        "> Wave AD4 **H-DEPLPLUS** · Inherit APPPLUS apps + AD PROMOTE stack",
        "> Claim: scoped packaged apps on AC+AD stack — not open chat LM",
        "",
        "## Routes",
        "",
        "| Surface | App | npm |",
        "|---------|-----|-----|",
    ]
    for app in APPPLUS_APPS:
        lines.append(
            f"| `{app['surface']}` | `{app['app_id']}` | `{app['npm']}` |"
        )
    lines.extend(
        [
            "",
            "## AD stack (PROMOTE)",
            "",
            "- H-HARDPARA · H-COMPOSE · H-ROUTEPLUS · H-APPPLUS · H-DEPLPLUS",
            "",
            "## Run",
            "",
            "```bash",
            "npm run nano:deplplus",
            "npm run nano:routeplus",
            "npm run nano:appplus",
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
    WHEN checking DEPLPLUS sync
    THEN require honesty + AD stack markers + forbidden list named.
    """
    body = str(text)
    miss: list[str] = []
    low = body.lower()
    if "not an open chat" not in low and "not open chat" not in low:
        miss.append("honest_not_open_chat")
    for m in AD_STACK_MARKERS:
        if m not in body:
            miss.append(m)
    for m in FORBIDDEN_MARKERS:
        if m not in body:
            miss.append(f"forbidden:{m}")
    if "npm run nano:deplplus" not in body:
        miss.append("npm_deplplus")
    return {"path": path, "ok": len(miss) == 0, "missing": miss}


def score_deplplus_trial(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    selected: Mapping[str, Any],
    item_app_id: str,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN auto-routed SERVE on declared deploy app
    WHEN scoring AD4 HITL smoke
    THEN FALSE_HIT→0; require correct in-scope route.
    """
    notes: list[str] = [f"selected={selected.get('app_id')}"]
    route = route_item(selected, item_app_id)
    if not bool(route.get("in_scope")):
        notes.append("DEPLOY_ROUTE_MISS")
        return 0.0, True, notes
    score, err, more = score_realapp_trial(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
        route=route,
    )
    notes.extend(more)
    return float(score), bool(err), notes


def deplplus_stats(
    scores: Sequence[float],
    errors: Sequence[bool],
    *,
    n_true_hit: int,
    n_false_hit: int,
    n_miss: int,
    n_pages_ok: int,
    n_pages: int,
    claims_ok: bool,
    n_fix: int,
) -> dict[str, Any]:
    if len(scores) != DEPLPLUS_N or len(errors) != DEPLPLUS_N:
        raise ValueError(f"DEPLPLUS requires exactly {DEPLPLUS_N} trials")
    mean = float(sum(float(s) for s in scores) / float(DEPLPLUS_N))
    n_err = int(sum(1 for e in errors if e))
    return {
        "n_trials": DEPLPLUS_N,
        "mean": mean,
        "n_errors": n_err,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_miss": int(n_miss),
        "n_pages_ok": int(n_pages_ok),
        "n_pages": int(n_pages),
        "min_pages": MIN_PAGES,
        "claims_ok": bool(claims_ok),
        "n_fix": int(n_fix),
        "pass_quality": mean >= PASS_MEAN and n_err <= PASS_MAX_ERRORS,
        "pass_docs": (
            int(n_pages_ok) >= MIN_PAGES and int(n_pages) >= MIN_PAGES
        ),
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_deplplus(stats: Mapping[str, Any]) -> str:
    """
    GIVEN DEPLPLUS stats
    WHEN applying §8.6 / §13.1 AD4 gate
    THEN PROMOTE if docs ∧ smoke quality ∧ honest claims;
         KILL on false-hit / dishonest; else HOLD.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("claims_ok")):
        return "KILL"
    if not bool(stats.get("pass_quality")):
        return "KILL"
    if bool(stats.get("pass_docs")):
        return "PROMOTE"
    return "HOLD"
