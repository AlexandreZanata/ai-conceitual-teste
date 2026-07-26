"""Wave AB5 H-REALAPP: package scoped apps (known + longdoc) with DEPL honesty."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "REALAPP_ID",
    "REALAPP_N",
    "MIN_APPS",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "REALAPP_APPS",
    "FORBIDDEN_OPEN_CHAT",
    "app_by_id",
    "claim_is_honest",
    "route_item",
    "honest_out_of_scope_text",
    "score_realapp_trial",
    "app_stats",
    "decide_app",
    "realapp_stats",
    "decide_realapp",
    "one_pager_body",
]

REALAPP_ID = "H-REALAPP"
REALAPP_N = 10
MIN_APPS = 1  # §11.1: ≥1 runnable documented app path
FORBIDDEN_OPEN_CHAT = ("open chat lm", "unbounded chat", "general chat")

# §11.6 — ship two surfaces (known + longdoc); howto remains via known wrap.
REALAPP_APPS: tuple[dict[str, Any], ...] = (
    {
        "app_id": "app-known",
        "surface": "known-ask",
        "accepts": frozenset({"known-ask", "howto"}),
        "spine": ("H-ZWRAP", "H-SEMWRAP", "H-ASKFAST"),
        "stack": "askfast",
        "claim": (
            "scoped known / near-known lab ask via SEMWRAP — "
            "not open chat LM"
        ),
        "one_pager": "docs/results/nano-lm/app-known.md",
        "npm": "npm run nano:realapp -- --app app-known",
    },
    {
        "app_id": "app-longdoc",
        "surface": "long-doc",
        "accepts": frozenset({"long-doc", "known-ask", "howto"}),
        "spine": ("H-LONGAPP", "H-SUMCACHE", "H-ROLL", "H-SEMWRAP"),
        "stack": "longapp",
        "claim": (
            "ask over curated long docs via ROLL/SUMCACHE — "
            "not STREAM / open chat"
        ),
        "one_pager": "docs/results/nano-lm/app-longdoc.md",
        "npm": "npm run nano:realapp -- --app app-longdoc",
    },
)


def app_by_id(app_id: str) -> dict[str, Any]:
    for app in REALAPP_APPS:
        if app["app_id"] == app_id:
            return dict(app)
    raise KeyError(f"unknown realapp id: {app_id}")


def claim_is_honest(claim: str) -> bool:
    """
    GIVEN a product claim string
    WHEN checking DEPL honesty
    THEN reject open-chat product language; require scoped negation.
    """
    low = str(claim).lower()
    if "not open chat" not in low and "not stream" not in low:
        if any(tok in low for tok in FORBIDDEN_OPEN_CHAT):
            return False
        if "open chat" in low and "not" not in low:
            return False
    return "scoped" in low or "curated" in low or "known" in low


def route_item(app: Mapping[str, Any], item_app_id: str) -> dict[str, Any]:
    """
    GIVEN packaged app + pack item app_id
    WHEN routing
    THEN in_scope if accepted; else honest out-of-scope (no false serve claim).
    """
    accepts = frozenset(app.get("accepts") or ())
    in_scope = str(item_app_id) in accepts
    return {
        "app_id": str(app["app_id"]),
        "item_app_id": str(item_app_id),
        "in_scope": in_scope,
        "route": "SERVE" if in_scope else "OUT_OF_SCOPE",
    }


def honest_out_of_scope_text(app_id: str, surface: str) -> str:
    return (
        f"Out of scope for {app_id} (surface={surface}). "
        "Use the matching packaged app."
    )


def score_realapp_trial(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    route: Mapping[str, Any],
    longapp_ok: bool | None = None,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN REALAPP ask result + route
    WHEN scoring HITL
    THEN FALSE_HIT→0; TRUE_HIT→9; honest out-of-scope refuse→8.
    """
    from semwrap_ops import score_semwrap_trial

    notes: list[str] = [f"route={route.get('route')}"]
    if not bool(route.get("in_scope")):
        low = str(completion).lower()
        if "out of scope" in low:
            notes.append("HONEST_OUT_OF_SCOPE")
            return 8.0, False, notes
        if lookup_kind == "FALSE_HIT":
            notes.append("OUT_OF_SCOPE_FALSE_HIT")
            return 0.0, True, notes
        notes.append("OUT_OF_SCOPE_LEAK")
        return 4.0, True, notes

    score, err, more = score_semwrap_trial(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
    )
    notes.extend(more)
    if longapp_ok is False:
        err = True
        notes.append("LONGAPP_CTX_FAIL")
    return float(score), bool(err), notes


def app_stats(
    scores: Sequence[float],
    errors: Sequence[bool],
    *,
    n_true_hit: int,
    n_false_hit: int,
    n_miss: int,
    n_in_scope: int,
    claim_ok: bool,
    one_pager_ok: bool,
    smoke_ok: bool,
) -> dict[str, Any]:
    if len(scores) != REALAPP_N or len(errors) != REALAPP_N:
        raise ValueError(f"REALAPP app requires exactly {REALAPP_N} trials")
    mean = float(sum(float(s) for s in scores) / float(REALAPP_N))
    n_err = int(sum(1 for e in errors if e))
    return {
        "n_trials": REALAPP_N,
        "mean": mean,
        "n_errors": n_err,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_miss": int(n_miss),
        "n_in_scope": int(n_in_scope),
        "claim_ok": bool(claim_ok),
        "one_pager_ok": bool(one_pager_ok),
        "smoke_ok": bool(smoke_ok),
        "pass_quality": mean >= PASS_MEAN and n_err <= PASS_MAX_ERRORS,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_app(stats: Mapping[str, Any]) -> str:
    """
    GIVEN one app surface stats
    WHEN gate
    THEN PROMOTE if quality ∧ honest claim ∧ one-pager ∧ smoke ∧ no false-hit;
         HOLD if docs/smoke miss but quality; KILL if false-hit/quality fail.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("pass_quality")):
        return "KILL"
    if not bool(stats.get("claim_ok")):
        return "KILL"
    if bool(stats.get("one_pager_ok")) and bool(stats.get("smoke_ok")):
        return "PROMOTE"
    return "HOLD"


def realapp_stats(app_results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """
    GIVEN per-app decisions
    WHEN summarizing H-REALAPP
    THEN ≥1 PROMOTE app ∧ no KILL → wave PROMOTE.
    """
    n = len(app_results)
    n_promote = sum(1 for a in app_results if a.get("decision") == "PROMOTE")
    n_kill = sum(1 for a in app_results if a.get("decision") == "KILL")
    n_hold = sum(1 for a in app_results if a.get("decision") == "HOLD")
    means = [float(a.get("mean", 0.0)) for a in app_results]
    mean = float(sum(means) / len(means)) if means else 0.0
    return {
        "n_apps": n,
        "n_promote": int(n_promote),
        "n_hold": int(n_hold),
        "n_kill": int(n_kill),
        "min_apps": MIN_APPS,
        "mean_across_apps": mean,
        "pass_product": n_promote >= MIN_APPS and n_kill == 0,
    }


def decide_realapp(stats: Mapping[str, Any]) -> str:
    if int(stats.get("n_kill", 0)) > 0:
        return "KILL"
    if bool(stats.get("pass_product")):
        return "PROMOTE"
    if int(stats.get("n_apps", 0)) >= MIN_APPS:
        return "HOLD"
    return "KILL"


def one_pager_body(app: Mapping[str, Any]) -> str:
    """Public one-pager markdown for a packaged app."""
    spine = " → ".join(str(x) for x in app.get("spine") or ())
    return "\n".join(
        [
            f"# {app['app_id']} — scoped nano app",
            "",
            f"> Wave AB5 **H-REALAPP** · Spine: `{spine}`",
            f"> Claim: {app['claim']}",
            "",
            "## Job",
            "",
            f"Surface `{app['surface']}` — runnable path for lab HITL asks.",
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
