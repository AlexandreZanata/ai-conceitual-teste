"""Wave AD REPORT: public closeout (per-model HITL + FIX log)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "AD_ID",
    "AD_THESIS",
    "AD_EVIDENCE",
    "AD_REPORT_MARKERS",
    "AD_HITL_SCOREBOARD",
    "decide_ad_report",
    "report_markers_ok",
    "scoreboard_ok",
    "render_wave_ad_summary",
    "render_paper_lab_wave_ad",
]

AD_ID = "AD-REPORT"
AD_THESIS = (
    "Scoped AD packaged stack = HARDPARA+COMPOSE+ROUTEPLUS+DEPLPLUS "
    "on AC/APPPLUS spine; held-out HITL mean 9.0; not open chat LM"
)

# Frozen per-model Cursor ASK→EVAL→FIX closeout (§8.6 / §13 / SESSION).
AD_HITL_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AD0",
        "id": "SESSION",
        "mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "freeze 10 held-out asks ≠ AB ≠ AC",
    },
    {
        "stage": "AD1",
        "id": "H-HARDPARA",
        "mean": 9.0,
        "errors": 0,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "adversarial para; false-hit 0",
    },
    {
        "stage": "AD2",
        "id": "H-COMPOSE",
        "mean": 9.0,
        "errors": 0,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "usable 10/10; sources 2.0",
    },
    {
        "stage": "AD3",
        "id": "H-ROUTEPLUS",
        "mean": 9.0,
        "errors": 0,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "route 10/10; OOS 10/10",
    },
    {
        "stage": "AD4",
        "id": "H-DEPLPLUS",
        "mean": 9.0,
        "errors": 0,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "pages 4/4; DEPL honest",
    },
    {
        "stage": "AD5",
        "id": "AD-HITL-10",
        "mean": 9.0,
        "errors": 0,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "final pack gate",
    },
    {
        "stage": "AD6",
        "id": "AD-REPORT",
        "mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "public summary + paper-lab",
    },
    {
        "stage": "AD7",
        "id": "AD-FREEZE",
        "mean": None,
        "errors": None,
        "fix": 0,
        "decision": "pending",
        "note": "lock; no Wave AE invent",
    },
)

AD_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ad-session.md",
    "docs/results/nano-lm/formal-hhardpara-hardpara.md",
    "docs/results/nano-lm/formal-hcompose-compose.md",
    "docs/results/nano-lm/formal-hrouteplus-routeplus.md",
    "docs/results/nano-lm/formal-hdeplplus-deplplus.md",
    "docs/results/nano-lm/depl-ad.md",
    "docs/results/nano-lm/app-known.md",
    "docs/results/nano-lm/app-howto.md",
    "docs/results/nano-lm/app-longdoc.md",
    "docs/results/nano-lm/wave-ad-hitl.md",
    "docs/results/nano-lm/wave-ad-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ad.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AD_REPORT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-HARDPARA",
    "H-COMPOSE",
    "H-ROUTEPLUS",
    "H-DEPLPLUS",
    "AD-HITL-10",
    "FIX",
    "PROMOTE",
    "not open chat",
)


def decide_ad_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AD_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AD report evidence
    WHEN deciding AD-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AD_ID}: {AD_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AD_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AD_HITL_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking per-model HITL + FIX log (§13.6)
    THEN every model id appears and FIX count column exists.
    """
    body = str(text)
    if "FIX count" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid == "AD-HITL-10":
            if f"**{mid}**" not in body:
                return False
    return True


def render_wave_ad_summary() -> str:
    lines = [
        "# Wave AD — robust held-out · hard para · compose · route · deploy "
        "(**COMPLETE**)",
        "",
        "> Lab: `.local/pesquisa.md` §8.6 · §13 · Paper-lab: "
        "[paper-lab-wave-ad.md](paper-lab-wave-ad.md)  ",
        "> Parent: Wave AC **AC-FREEZE** reopen · Product spine: "
        "**AC/APPPLUS + AD stack**",
        "",
        "**Status: COMPLETE** · Thesis: **" + AD_THESIS + ".**",
        "",
        "## Stage scoreboard (Cursor ASK→EVAL→FIX)",
        "",
        "| # | ID | Mean | Errors | FIX count | Decision | Note |",
        "|---|-----|-----:|-------:|----------:|----------|------|",
    ]
    for row in AD_HITL_SCOREBOARD:
        mean = "—" if row["mean"] is None else f"{float(row['mean']):g}"
        err = "—" if row["errors"] is None else str(row["errors"])
        lines.append(
            f"| {row['stage']} | **{row['id']}** | {mean} | {err} | "
            f"**{row['fix']}** | **{row['decision']}** | {row['note']} |"
        )
    lines.extend(
        [
            "",
            "## Honest product claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| Harder para | **H-HARDPARA**; mean **9.0**; false-hit **0** |",
            "| Multi-source compose | **H-COMPOSE**; usable **10**/10; "
            "sources **2.0** |",
            "| Cross-app route + OOS | **H-ROUTEPLUS**; route/OOS **10**/10 |",
            "| Deploy docs + smoke | **H-DEPLPLUS**; pages **4**/4 |",
            "| Final HITL | **AD-HITL-10** mean **9.0** · errors **0**/10 |",
            "| “Open chat LM ≤5M” | **False** — not open chat |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:ad:report",
            "npm run nano:ad:session",
            "npm run nano:hardpara",
            "npm run nano:compose",
            "npm run nano:routeplus",
            "npm run nano:deplplus",
            "npm run nano:ad:hitl",
            "npm run nano:ad:freeze",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · ZERR/SERVEALIGN/AB/AC-as-open-chat · invent Wave AE "
            "without lab-book reopen.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_ad() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AD (robust held-out · para · compose · "
            "route · deploy)",
            "",
            "> Companion to [wave-ad-summary.md](wave-ad-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE** · Final HITL: "
            "[wave-ad-hitl.md](wave-ad-hitl.md)",
            "",
            "## Question",
            "",
            "After AC shipped held-out packaged apps, can the ≤5M student "
            "prove **harder paraphrase, multi-source compose, cross-app "
            "route + honest OOS, and deploy honesty** on a **third** "
            "held-out 10 with Cursor ASK→EVAL→FIX on every stack?",
            "",
            "## Answer",
            "",
            "**Yes, as a scoped AD packaged stack — not as open chat.** "
            "Wave AD promotes HARDPARA, COMPOSE, ROUTEPLUS, DEPLPLUS, and "
            "final held-out HITL mean 9.0.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-HARDPARA | Adversarial para; mean 9.0; false-hit 0 |",
            "| H-COMPOSE | Dual-source; usable 10/10; sources 2.0 |",
            "| H-ROUTEPLUS | Correct route 10/10; honest OOS 10/10 |",
            "| H-DEPLPLUS | One-pagers 4/4; smoke mean 9.0 |",
            "| AD-HITL-10 | Final pack mean 9.0 · errors 0/10 |",
            "",
            "## Takeaway one-liner",
            "",
            "**Scoped AD product = AC/APPPLUS + HARDPARA/COMPOSE/ROUTEPLUS/"
            "DEPLPLUS on held-out; not open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-ad-summary.md](wave-ad-summary.md) · "
            "[wave-ad-hitl.md](wave-ad-hitl.md) · "
            "[wave-ac-summary.md](wave-ac-summary.md)  ",
            "- Formals: HARDPARA · COMPOSE · ROUTEPLUS · DEPLPLUS  ",
            "- Deploy: [depl-ad.md](depl-ad.md) · Apps: "
            "[app-known.md](app-known.md) · "
            "[app-howto.md](app-howto.md) · "
            "[app-longdoc.md](app-longdoc.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
