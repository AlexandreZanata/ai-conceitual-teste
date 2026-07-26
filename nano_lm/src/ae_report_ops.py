"""Wave AE REPORT: public closeout (per-model HITL + FIX log)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "AE_ID",
    "AE_THESIS",
    "AE_EVIDENCE",
    "AE_REPORT_MARKERS",
    "AE_HITL_SCOREBOARD",
    "decide_ae_report",
    "report_markers_ok",
    "scoreboard_ok",
    "render_wave_ae_summary",
    "render_paper_lab_wave_ae",
]

AE_ID = "AE-REPORT"
AE_THESIS = (
    "Scoped AE packaged stack = CTXMAX+SMARTMAX+FASTMAX+APPMAX "
    "on held-out AE0; final HITL mean 9.0; not open chat LM"
)

# Frozen per-model Cursor ASK→EVAL→FIX closeout (§5 / SESSION).
AE_HITL_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AE0",
        "id": "SESSION",
        "mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "freeze 10 held-out asks ≠ AB ≠ AC ≠ AD",
    },
    {
        "stage": "AE1",
        "id": "H-CTXMAX",
        "mean": 9.0,
        "errors": 0,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "multi-doc L_eff↑ vs CTXPLUS",
    },
    {
        "stage": "AE2",
        "id": "H-SMARTMAX",
        "mean": 9.0,
        "errors": 0,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "multi-hop cite; false-hit 0",
    },
    {
        "stage": "AE3",
        "id": "H-FASTMAX",
        "mean": 9.0,
        "errors": 0,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "hot e2e ≪ FASTPLUS warm",
    },
    {
        "stage": "AE4",
        "id": "H-APPMAX",
        "mean": 8.725,
        "errors": 0,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "howto↑ + app-route + DEPL-AE",
    },
    {
        "stage": "AE5",
        "id": "AE-HITL-10",
        "mean": 9.0,
        "errors": 0,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "final pack gate",
    },
    {
        "stage": "AE6",
        "id": "AE-REPORT",
        "mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "public summary + paper-lab",
    },
    {
        "stage": "AE7",
        "id": "AE-FREEZE",
        "mean": None,
        "errors": None,
        "fix": 0,
        "decision": "pending",
        "note": "lock; no Wave AF invent",
    },
)

AE_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ae-session.md",
    "docs/results/nano-lm/formal-hctxmax-ctxmax.md",
    "docs/results/nano-lm/formal-hsmartmax-smartmax.md",
    "docs/results/nano-lm/formal-hfastmax-fastmax.md",
    "docs/results/nano-lm/formal-happmax-appmax.md",
    "docs/results/nano-lm/depl-ae.md",
    "docs/results/nano-lm/app-known.md",
    "docs/results/nano-lm/app-howto.md",
    "docs/results/nano-lm/app-longdoc.md",
    "docs/results/nano-lm/app-route.md",
    "docs/results/nano-lm/wave-ae-hitl.md",
    "docs/results/nano-lm/wave-ae-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ae.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AE_REPORT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-CTXMAX",
    "H-SMARTMAX",
    "H-FASTMAX",
    "H-APPMAX",
    "AE-HITL-10",
    "FIX",
    "PROMOTE",
    "not open chat",
)


def decide_ae_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AE_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AE report evidence
    WHEN deciding AE-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AE_ID}: {AE_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AE_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AE_HITL_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking per-model HITL + FIX log (§5 AE6)
    THEN every model id appears and FIX count column exists.
    """
    body = str(text)
    if "FIX count" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid == "AE-HITL-10":
            if f"**{mid}**" not in body:
                return False
    return True


def render_wave_ae_summary() -> str:
    lines = [
        "# Wave AE — more ctx · smarter · faster · real apps (**COMPLETE**)",
        "",
        "> Lab: `.local/pesquisa.md` §5 · Paper-lab: "
        "[paper-lab-wave-ae.md](paper-lab-wave-ae.md)  ",
        "> Parent: Wave AD **AD-FREEZE** reopen · Product spine: "
        "**AE packaged stack**",
        "",
        "**Status: RESEARCH COMPLETE** · Freeze pending (AE7) · Thesis: **"
        + AE_THESIS
        + ".**",
        "",
        "## Stage scoreboard (Cursor ASK→EVAL→FIX)",
        "",
        "| # | ID | Mean | Errors | FIX count | Decision | Note |",
        "|---|-----|-----:|-------:|----------:|----------|------|",
    ]
    for row in AE_HITL_SCOREBOARD:
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
            "| Longer usable ctx | **H-CTXMAX**; mean **9.0**; L_eff↑ vs CTXPLUS |",
            "| Smarter retrieve/cite | **H-SMARTMAX**; mean **9.0**; false-hit **0** |",
            "| Faster ask/TTFT | **H-FASTMAX**; hot e2e ≪ FASTPLUS warm |",
            "| Stronger apps + route | **H-APPMAX**; 4/4 apps; mean **8.725** |",
            "| Final HITL | **AE-HITL-10** mean **9.0** · errors **0**/10 |",
            "| “Open chat LM ≤5M” | **False** — not open chat |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:ae:report",
            "npm run nano:ae:session",
            "npm run nano:ctxmax",
            "npm run nano:smartmax",
            "npm run nano:fastmax",
            "npm run nano:appmax",
            "npm run nano:ae:hitl",
            "npm run nano:ae:freeze",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · invent Wave AF without lab-book reopen · claim open chat.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_ae() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AE (more ctx · smarter · faster · real apps)",
            "",
            "> Companion to [wave-ae-summary.md](wave-ae-summary.md). "
            "English lab note.  ",
            "> **Status: RESEARCH COMPLETE** · Freeze pending · Final HITL: "
            "[wave-ae-hitl.md](wave-ae-hitl.md)",
            "",
            "## Question",
            "",
            "After AD froze held-out apps + para/compose/route/DEPL, can the "
            "≤5M student push **longer usable ctx, smarter cite, faster ask, "
            "and stronger apps** on a **fourth** held-out 10 with Cursor "
            "ASK→EVAL→FIX on every stack?",
            "",
            "## Answer",
            "",
            "**Yes, as a scoped AE packaged stack — not as open chat.** "
            "Wave AE promotes CTXMAX, SMARTMAX, FASTMAX, APPMAX, and final "
            "held-out HITL mean 9.0.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-CTXMAX | Multi-doc; mean 9.0; L_eff↑ vs CTXPLUS |",
            "| H-SMARTMAX | Multi-hop cite; mean 9.0; false-hit 0 |",
            "| H-FASTMAX | Hot e2e ≪ FASTPLUS warm; mean 9.0 |",
            "| H-APPMAX | 4 apps + DEPL-AE; mean 8.725 |",
            "| AE-HITL-10 | Final pack mean 9.0 · errors 0/10 |",
            "",
            "## Takeaway one-liner",
            "",
            "**Scoped AE product = CTXMAX+SMARTMAX+FASTMAX+APPMAX on "
            "held-out; not open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-ae-summary.md](wave-ae-summary.md) · "
            "[wave-ae-hitl.md](wave-ae-hitl.md) · "
            "[wave-ad-summary.md](wave-ad-summary.md)  ",
            "- Formals: CTXMAX · SMARTMAX · FASTMAX · APPMAX  ",
            "- Deploy: [depl-ae.md](depl-ae.md) · Apps: "
            "[app-known.md](app-known.md) · "
            "[app-howto.md](app-howto.md) · "
            "[app-longdoc.md](app-longdoc.md) · "
            "[app-route.md](app-route.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
