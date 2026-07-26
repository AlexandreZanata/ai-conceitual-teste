"""Wave AF REPORT: public closeout (per-model HITL + FIX log)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "AF_ID",
    "AF_THESIS",
    "AF_EVIDENCE",
    "AF_REPORT_MARKERS",
    "AF_HITL_SCOREBOARD",
    "decide_af_report",
    "report_markers_ok",
    "scoreboard_ok",
    "render_wave_af_summary",
    "render_paper_lab_wave_af",
]

AF_ID = "AF-REPORT"
AF_THESIS = (
    "Scoped AF packaged stack = CTXULTRA+SMARTULTRA+FASTULTRA+APPULTRA "
    "on held-out AF0; final HITL mean 9.0; not open chat LM"
)

# Frozen per-model Cursor ASK→EVAL→FIX closeout (§5 / SESSION).
AF_HITL_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AF0",
        "id": "SESSION",
        "mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "freeze 10 held-out asks ≠ AB ≠ AC ≠ AD ≠ AE",
    },
    {
        "stage": "AF1",
        "id": "H-CTXULTRA",
        "mean": 9.0,
        "errors": 0,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "triple-doc L_eff↑ vs CTXMAX",
    },
    {
        "stage": "AF2",
        "id": "H-SMARTULTRA",
        "mean": 9.0,
        "errors": 0,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "triple-hop cite; false-hit 0",
    },
    {
        "stage": "AF3",
        "id": "H-FASTULTRA",
        "mean": 9.0,
        "errors": 0,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "hot e2e ≪ FASTMAX",
    },
    {
        "stage": "AF4",
        "id": "H-APPULTRA",
        "mean": 8.86,
        "errors": 0,
        "fix": 7,
        "decision": "PROMOTE",
        "note": "howto↑ + compose 5th + DEPL-AF",
    },
    {
        "stage": "AF5",
        "id": "AF-HITL-10",
        "mean": 9.0,
        "errors": 0,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "final pack gate",
    },
    {
        "stage": "AF6",
        "id": "AF-REPORT",
        "mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "public summary + paper-lab",
    },
    {
        "stage": "AF7",
        "id": "AF-FREEZE",
        "mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "lock; no Wave AG invent",
    },
)

AF_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-af-session.md",
    "docs/results/nano-lm/formal-hctxultra-ctxultra.md",
    "docs/results/nano-lm/formal-hsmartultra-smartultra.md",
    "docs/results/nano-lm/formal-hfastultra-fastultra.md",
    "docs/results/nano-lm/formal-happultra-appultra.md",
    "docs/results/nano-lm/depl-af.md",
    "docs/results/nano-lm/appultra-known.md",
    "docs/results/nano-lm/appultra-howto.md",
    "docs/results/nano-lm/appultra-longdoc.md",
    "docs/results/nano-lm/appultra-route.md",
    "docs/results/nano-lm/appultra-compose.md",
    "docs/results/nano-lm/wave-af-hitl.md",
    "docs/results/nano-lm/wave-af-summary.md",
    "docs/results/nano-lm/paper-lab-wave-af.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AF_REPORT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-CTXULTRA",
    "H-SMARTULTRA",
    "H-FASTULTRA",
    "H-APPULTRA",
    "AF-HITL-10",
    "FIX",
    "PROMOTE",
    "not open chat",
)


def decide_af_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AF_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AF report evidence
    WHEN deciding AF-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AF_ID}: {AF_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AF_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AF_HITL_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking per-model HITL + FIX log (§5 AF6)
    THEN every model id appears and FIX count column exists.
    """
    body = str(text)
    if "FIX count" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid == "AF-HITL-10":
            if f"**{mid}**" not in body:
                return False
    return True


def render_wave_af_summary() -> str:
    lines = [
        "# Wave AF — more ctx · smarter · faster · real apps "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §5 · Paper-lab: "
        "[paper-lab-wave-af.md](paper-lab-wave-af.md) · "
        "Freeze: [af-freeze.md](af-freeze.md)  ",
        "> Parent: Wave AE **AE-FREEZE** reopen · Product spine: "
        "**AF packaged stack**",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + AF_THESIS
        + ".**",
        "",
        "## Stage scoreboard (Cursor ASK→EVAL→FIX)",
        "",
        "| # | ID | Mean | Errors | FIX count | Decision | Note |",
        "|---|-----|-----:|-------:|----------:|----------|------|",
    ]
    for row in AF_HITL_SCOREBOARD:
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
            "| Longer usable ctx | **H-CTXULTRA**; mean **9.0**; L_eff↑ vs CTXMAX |",
            "| Smarter retrieve/cite | **H-SMARTULTRA**; mean **9.0**; false-hit **0** |",
            "| Faster ask/TTFT | **H-FASTULTRA**; hot e2e ≪ FASTMAX |",
            "| Stronger apps + compose | **H-APPULTRA**; 5/5 apps; mean **8.86** |",
            "| Final HITL | **AF-HITL-10** mean **9.0** · errors **0**/10 |",
            "| “Open chat LM ≤5M” | **False** — not open chat |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:af:report",
            "npm run nano:af:session",
            "npm run nano:ctxultra",
            "npm run nano:smartultra",
            "npm run nano:fastultra",
            "npm run nano:appultra",
            "npm run nano:af:hitl",
            "npm run nano:af:freeze",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · invent Wave AG without lab-book reopen · claim open chat.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_af() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AF (more ctx · smarter · faster · real apps)",
            "",
            "> Companion to [wave-af-summary.md](wave-af-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · Final HITL: "
            "[wave-af-hitl.md](wave-af-hitl.md) · "
            "Freeze: [af-freeze.md](af-freeze.md) · "
            "Parent: [ae-freeze.md](ae-freeze.md)",
            "",
            "## Question",
            "",
            "After AE froze CTXMAX/SMARTMAX/FASTMAX/APPMAX, can the ≤5M "
            "student push **longer usable ctx, smarter cite, faster ask, and "
            "stronger apps** on a **fifth** held-out 10 with Cursor "
            "ASK→EVAL→FIX on every stack?",
            "",
            "## Answer",
            "",
            "**Yes, as a scoped AF packaged stack — not as open chat.** "
            "Wave AF promotes CTXULTRA, SMARTULTRA, FASTULTRA, APPULTRA, and "
            "final held-out HITL mean 9.0.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-CTXULTRA | Triple-doc; mean 9.0; L_eff↑ vs CTXMAX |",
            "| H-SMARTULTRA | Triple-hop cite; mean 9.0; false-hit 0 |",
            "| H-FASTULTRA | Hot e2e ≪ FASTMAX; mean 9.0 |",
            "| H-APPULTRA | 5 apps + DEPL-AF; mean 8.86 |",
            "| AF-HITL-10 | Final pack mean 9.0 · errors 0/10 |",
            "",
            "## Takeaway one-liner",
            "",
            "**Scoped AF product = CTXULTRA+SMARTULTRA+FASTULTRA+APPULTRA on "
            "held-out; not open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-af-summary.md](wave-af-summary.md) · "
            "[wave-af-hitl.md](wave-af-hitl.md) · "
            "[wave-ae-summary.md](wave-ae-summary.md)  ",
            "- Formals: CTXULTRA · SMARTULTRA · FASTULTRA · APPULTRA  ",
            "- Deploy: [depl-af.md](depl-af.md) · Apps: "
            "[appultra-known.md](appultra-known.md) · "
            "[appultra-howto.md](appultra-howto.md) · "
            "[appultra-longdoc.md](appultra-longdoc.md) · "
            "[appultra-route.md](appultra-route.md) · "
            "[appultra-compose.md](appultra-compose.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
