"""Wave AK5 H-APPMORE: apps expose LOOKUP vs GENERATE + DEPL-AK honesty."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from antifp_ops import classify_arm, extract_telemetry
from realapp_ops import (
    claim_is_honest,
    honest_out_of_scope_text,
    route_item,
)
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "APPMORE_ID",
    "APPMORE_N",
    "MIN_APPS",
    "MIN_PAGES",
    "MIN_LOOKUP_MEAN",
    "MIN_GEN_MEAN",
    "APPPUSH_GEN_MEAN",
    "APPPEAK_GEN_MEAN",
    "SERVEALIGN_MEAN",
    "DEPL_AK_PAGE",
    "AK_STACK_MARKERS",
    "FORBIDDEN_MARKERS",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "APPMORE_APPS",
    "app_by_id",
    "claim_is_honest",
    "route_item",
    "honest_out_of_scope_text",
    "arm_label_ok",
    "score_appmore_lookup",
    "score_appmore_gen",
    "one_pager_body",
    "depl_ak_body",
    "page_sync_report",
    "app_dual_stats",
    "decide_app",
    "appmore_stats",
    "decide_appmore",
]

APPMORE_ID = "H-APPMORE"
APPMORE_N = 10
MIN_APPS = 3  # known + howto + longdoc (AK0 surfaces)
MIN_PAGES = 4  # 3 apps + depl-ak
MIN_LOOKUP_MEAN = 7.0
MIN_GEN_MEAN = 5.0  # pesquisa §3 AK5 — or honest HOLD
APPPUSH_GEN_MEAN = 4.0  # parent AI5 SERVE gen (HOLD)
APPPEAK_GEN_MEAN = 9.0  # peer AJ5 peak SERVE
SERVEALIGN_MEAN = 3.4
DEPL_AK_PAGE = "docs/results/nano-lm/depl-ak.md"

AK_STACK_MARKERS: tuple[str, ...] = (
    "H-APPMORE",
    "LOOKUP",
    "GENERATE",
    "H-FASTMORE",
)

FORBIDDEN_MARKERS: tuple[str, ...] = (
    "STREAM",
    "KVCACHE-Q",
    "GENCACHE",
    "ZPREF",
)

APPMORE_APPS: tuple[dict[str, Any], ...] = (
    {
        "app_id": "app-known",
        "surface": "known-ask",
        "accepts": frozenset({"known-ask"}),
        "spine": (
            "H-SEMWRAP",
            "H-ASKFAST",
            "H-CTXMORE",
            "H-FASTMORE",
            "H-APPMORE",
        ),
        "stack": "askfast",
        "claim": (
            "scoped known-ask exposes LOOKUP vs GENERATE arms — "
            "not open chat LM"
        ),
        "one_pager": "docs/results/nano-lm/appmore-known.md",
        "npm": "npm run nano:appmore -- --app app-known",
    },
    {
        "app_id": "app-howto",
        "surface": "howto",
        "accepts": frozenset({"howto"}),
        "spine": (
            "H-SEMWRAP",
            "H-ASKFAST",
            "H-CTXMORE",
            "H-FASTMORE",
            "H-APPMORE",
        ),
        "stack": "howto",
        "claim": (
            "scoped howto exposes LOOKUP vs GENERATE arms — "
            "not open chat LM"
        ),
        "one_pager": "docs/results/nano-lm/appmore-howto.md",
        "npm": "npm run nano:appmore -- --app app-howto",
    },
    {
        "app_id": "app-longdoc",
        "surface": "long-doc",
        "accepts": frozenset({"long-doc"}),
        "spine": (
            "H-SEMWRAP",
            "H-ASKFAST",
            "H-CTXMORE",
            "H-FASTMORE",
            "H-APPMORE",
        ),
        "stack": "longdoc",
        "claim": (
            "scoped long-doc exposes LOOKUP vs GENERATE arms — "
            "not open chat LM"
        ),
        "one_pager": "docs/results/nano-lm/appmore-longdoc.md",
        "npm": "npm run nano:appmore -- --app app-longdoc",
    },
)


def app_by_id(app_id: str) -> dict[str, Any]:
    for app in APPMORE_APPS:
        if app["app_id"] == app_id:
            return dict(app)
    raise KeyError(f"unknown appmore id: {app_id}")


def arm_label_ok(payload: Mapping[str, Any], *, expect: str) -> bool:
    """
    GIVEN ask payload + expected arm
    WHEN classifying
    THEN True iff classify_arm matches expect (LOOKUP|GENERATE).
    """
    return classify_arm(payload) == str(expect)


def score_appmore_lookup(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    route: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """LOOKUP on app surface — OOS refuse ok; SERVE ≠ generative IQ."""
    from askfast_ops import score_askfast_trial
    from realapp_ops import score_realapp_trial

    if not bool(route.get("in_scope")):
        score, err, notes = score_realapp_trial(
            mode=mode,
            completion=completion,
            expected_gold=expected_gold,
            lookup_kind=lookup_kind,
            route=route,
        )
        return float(score), bool(err), list(notes) + [
            "APPMORE LOOKUP OOS — not generative IQ"
        ]
    score, err, notes = score_askfast_trial(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
    )
    tel = extract_telemetry(payload)
    notes = list(notes) + [
        f"arm=LOOKUP mode={tel['mode']} wall_ms={tel['wall_ms']} "
        f"n_new={tel['n_new']}",
        "APPMORE LOOKUP labeled — not generative IQ",
    ]
    if not arm_label_ok(payload, expect="LOOKUP"):
        return float(score), True, notes + ["LOOKUP arm mislabeled"]
    return float(score), bool(err), notes


def score_appmore_gen(
    *,
    completion: str,
    expected_gold: str,
    route: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """GENERATE on app surface — OOS refuse ok; SERVE uses GENTRUE peak."""
    from gentrue_ops import score_gentrue_gen
    from realapp_ops import score_realapp_trial

    if not bool(route.get("in_scope")):
        score, err, notes = score_realapp_trial(
            mode=str(payload.get("mode", "")),
            completion=completion,
            expected_gold=expected_gold,
            lookup_kind="MISS",
            route=route,
        )
        return float(score), bool(err), list(notes) + [
            "APPMORE GENERATE OOS refuse — honest"
        ]
    score, err, notes = score_gentrue_gen(
        completion=completion,
        expected_gold=expected_gold,
        payload=payload,
        peak_ablated=False,
    )
    notes = list(notes) + [
        "APPMORE GENERATE GENTRUE peak — Cursor scores completion",
        f"beat APPPUSH SERVE gen={APPPUSH_GEN_MEAN} / peer APPPEAK="
        f"{APPPEAK_GEN_MEAN}",
        "peak extractive — NOT open-chat IQ",
    ]
    return float(score), bool(err), notes


def one_pager_body(app: Mapping[str, Any]) -> str:
    """Public one-pager for an APPMORE packaged app (dual-arm)."""
    spine = " → ".join(str(x) for x in app.get("spine") or ())
    return "\n".join(
        [
            f"# {app['app_id']} — scoped nano app (APPMORE)",
            "",
            f"> Wave AK5 **H-APPMORE** · Spine: `{spine}`",
            f"> Claim: {app['claim']}",
            "",
            "## Job",
            "",
            f"Surface `{app['surface']}` — dual-arm LOOKUP + GENERATE on AK0.",
            "",
            "## Arms",
            "",
            "| Arm | Mode family | IQ claim |",
            "|-----|-------------|----------|",
            "| LOOKUP | WRAP_LOOKUP / SEMWRAP / ASKFAST | product retrieve — not IQ |",
            "| GENERATE | QPFB2+GROUNDED+GENTRUE_PEAK | wall_ms>0 · Cursor-scored |",
            "",
            "## Run",
            "",
            "```bash",
            str(app["npm"]),
            "npm run nano:appmore",
            "```",
            "",
            "## AK stack",
            "",
            "- H-GENTRUE · H-CTXMORE · H-SMARTMORE · H-FASTMORE · H-APPMORE",
            "",
            "## Honesty",
            "",
            "- Not an open chat LM.",
            "- LOOKUP scores ≠ generative IQ.",
            "- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF revival.",
            "",
        ]
    )


def depl_ak_body() -> str:
    """Overview one-pager for AK dual-arm packaged deploy."""
    lines = [
        "# DEPL-AK — AK packaged deploy (**H-APPMORE**)",
        "",
        "> Wave AK5 **H-APPMORE** · Inherit AJ apps + AK more spines",
        "> Claim: scoped apps expose LOOKUP vs GENERATE — not open chat LM",
        "",
        "## Routes",
        "",
        "| Surface | App | npm |",
        "|---------|-----|-----|",
    ]
    for app in APPMORE_APPS:
        lines.append(
            f"| `{app['surface']}` | `{app['app_id']}` | `{app['npm']}` |"
        )
    lines.extend(
        [
            "",
            "## Dual-arm law",
            "",
            "- LOOKUP: labeled WRAP_LOOKUP / SEMWRAP — product path only.",
            "- GENERATE: wall_ms>0 · n_new>0 · Cursor scores completion.",
            "- Never PROMOTE smarter LM from LOOKUP-only HITL.",
            "",
            "## AK stack",
            "",
            "- H-GENTRUE · H-CTXMORE · H-SMARTMORE · H-FASTMORE · H-APPMORE",
            "",
            "## Run",
            "",
            "```bash",
            "npm run nano:appmore",
            "```",
            "",
            "## Honesty",
            "",
            "- Not an open chat LM.",
            "- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF · QI · MIXD.",
            "- Ship claim remains AF packaged stack until AK6 gen bar.",
            "",
        ]
    )
    return "\n".join(lines)


def page_sync_report(path: str, text: str) -> dict[str, Any]:
    """
    GIVEN one-pager path + body
    WHEN checking DEPL-AK sync
    THEN require honesty + dual-arm markers + forbidden list.
    """
    body = str(text)
    miss: list[str] = []
    low = body.lower()
    if "not an open chat" not in low and "not open chat" not in low:
        miss.append("honest_not_open_chat")
    for m in AK_STACK_MARKERS:
        if m not in body:
            miss.append(m)
    for m in FORBIDDEN_MARKERS:
        if m not in body:
            miss.append(f"forbidden:{m}")
    if "npm run nano:appmore" not in body:
        miss.append("npm_appmore")
    return {"path": path, "ok": len(miss) == 0, "missing": miss}


def app_dual_stats(
    *,
    lookup_scores: Sequence[float],
    lookup_errors: Sequence[bool],
    gen_scores: Sequence[float],
    gen_errors: Sequence[bool],
    serve_gen_scores: Sequence[float],
    n_true_hit: int,
    n_false_hit: int,
    n_lookup_labeled: int,
    n_gen_wall_ok: int,
    n_in_scope: int,
    claim_ok: bool,
    one_pager_ok: bool,
) -> dict[str, Any]:
    """
    GIVEN one app dual-arm scores
    WHEN summarizing surface
    THEN lookup mean over pack; gen IQ mean = in-scope SERVE only.
    """
    if len(lookup_scores) != APPMORE_N or len(gen_scores) != APPMORE_N:
        raise ValueError(f"APPMORE app requires {APPMORE_N} dual-arm scores")
    if len(serve_gen_scores) != int(n_in_scope):
        raise ValueError("serve_gen_scores must match n_in_scope")
    l_mean = float(sum(lookup_scores) / float(APPMORE_N))
    g_pack = float(sum(gen_scores) / float(APPMORE_N))
    g_mean = (
        float(sum(serve_gen_scores) / float(len(serve_gen_scores)))
        if serve_gen_scores
        else 0.0
    )
    n_l_err = int(sum(1 for e in lookup_errors if e))
    n_g_err = int(sum(1 for e in gen_errors if e))
    dual_ok = (
        int(n_lookup_labeled) >= int(n_in_scope)
        and int(n_gen_wall_ok) >= int(n_in_scope)
        and int(n_in_scope) >= 1
    )
    return {
        "n_trials": APPMORE_N,
        "lookup_mean": l_mean,
        "gen_mean": g_mean,
        "gen_pack_mean": g_pack,
        "n_lookup_errors": n_l_err,
        "n_gen_errors": n_g_err,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_lookup_labeled": int(n_lookup_labeled),
        "n_gen_wall_ok": int(n_gen_wall_ok),
        "n_in_scope": int(n_in_scope),
        "claim_ok": bool(claim_ok),
        "one_pager_ok": bool(one_pager_ok),
        "dual_arm_ok": bool(dual_ok),
        "pass_lookup": l_mean >= MIN_LOOKUP_MEAN
        and n_l_err <= PASS_MAX_ERRORS
        and int(n_false_hit) == 0,
        "pass_gen": g_mean >= MIN_GEN_MEAN,
        "beats_apppush_gen": g_mean > float(APPPUSH_GEN_MEAN),
        "beats_servealign": g_mean > float(SERVEALIGN_MEAN),
    }


def decide_app(stats: Mapping[str, Any]) -> str:
    """
    GIVEN one-app dual-arm stats
    WHEN gating surface
    THEN KILL if false-hit/missing dual-arm; PROMOTE if lookup+gen≥5;
         HOLD if lookup+expose only.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("dual_arm_ok")):
        return "KILL"
    if not bool(stats.get("claim_ok")) or not bool(stats.get("one_pager_ok")):
        return "KILL"
    if bool(stats.get("pass_lookup")) and bool(stats.get("pass_gen")):
        return "PROMOTE"
    if bool(stats.get("pass_lookup")):
        return "HOLD"
    return "KILL"


def appmore_stats(
    app_results: Sequence[Mapping[str, Any]],
    *,
    n_pages_ok: int,
    n_pages: int,
) -> dict[str, Any]:
    """
    GIVEN per-app dual-arm results + DEPL pages
    WHEN summarizing AK5
    THEN expose arms ∧ lookup≥7 ∧ DEPL; gen≥5 for full PROMOTE else HOLD.
    """
    n = len(app_results)
    by_id = {str(a.get("app_id")): a for a in app_results}
    n_promote = sum(1 for a in app_results if a.get("decision") == "PROMOTE")
    n_kill = sum(1 for a in app_results if a.get("decision") == "KILL")
    n_hold = sum(1 for a in app_results if a.get("decision") == "HOLD")
    l_means = [float(a.get("lookup_mean", 0.0)) for a in app_results]
    g_means = [float(a.get("gen_mean", 0.0)) for a in app_results]
    lookup_mean = float(sum(l_means) / len(l_means)) if l_means else 0.0
    gen_mean = float(sum(g_means) / len(g_means)) if g_means else 0.0
    dual_all = all(bool(a.get("dual_arm_ok")) for a in app_results)
    docs_ok = int(n_pages_ok) >= MIN_PAGES and int(n_pages) >= MIN_PAGES
    known_ok = str((by_id.get("app-known") or {}).get("decision")) in {
        "PROMOTE",
        "HOLD",
    }
    howto_ok = str((by_id.get("app-howto") or {}).get("decision")) in {
        "PROMOTE",
        "HOLD",
    }
    long_ok = str((by_id.get("app-longdoc") or {}).get("decision")) in {
        "PROMOTE",
        "HOLD",
    }
    pass_expose = dual_all and docs_ok and n >= MIN_APPS and n_kill == 0
    pass_lookup = lookup_mean >= MIN_LOOKUP_MEAN
    pass_gen = gen_mean >= MIN_GEN_MEAN
    return {
        "n_apps": n,
        "n_promote": int(n_promote),
        "n_hold": int(n_hold),
        "n_kill": int(n_kill),
        "min_apps": MIN_APPS,
        "lookup_mean_across": lookup_mean,
        "gen_mean_across": gen_mean,
        "dual_arm_all": dual_all,
        "known_ok": known_ok,
        "howto_ok": howto_ok,
        "longdoc_ok": long_ok,
        "n_pages_ok": int(n_pages_ok),
        "n_pages": int(n_pages),
        "depl_ok": docs_ok,
        "pass_expose": pass_expose,
        "pass_lookup": pass_lookup,
        "pass_gen": pass_gen,
        "pass_product": pass_expose and pass_lookup and pass_gen,
        "beats_apppush_gen": gen_mean > float(APPPUSH_GEN_MEAN),
        "min_lookup_mean": MIN_LOOKUP_MEAN,
        "min_gen_mean": MIN_GEN_MEAN,
        "apppush_gen_mean": APPPUSH_GEN_MEAN,
        "apppeak_gen_mean": APPPEAK_GEN_MEAN,
        "servealign_mean": SERVEALIGN_MEAN,
    }


def decide_appmore(stats: Mapping[str, Any]) -> str:
    """
    GIVEN APPMORE wave stats
    WHEN applying pesquisa §3 AK5 gate
    THEN PROMOTE if expose+lookup+gen≥5; HOLD if expose+lookup; else KILL.
    """
    if int(stats.get("n_kill", 0)) > 0:
        return "KILL"
    if bool(stats.get("pass_product")):
        return "PROMOTE"
    if bool(stats.get("pass_expose")) and bool(stats.get("pass_lookup")):
        return "HOLD"
    if int(stats.get("n_apps", 0)) >= MIN_APPS:
        return "HOLD"
    return "KILL"
