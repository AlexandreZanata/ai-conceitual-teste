"""Wave AH REPORT: public closeout (dual-arm HITL + FIX + anti-FP)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "AH_ID",
    "AH_THESIS",
    "AH_EVIDENCE",
    "AH_REPORT_MARKERS",
    "AH_HITL_SCOREBOARD",
    "decide_ah_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "render_wave_ah_summary",
    "render_paper_lab_wave_ah",
]

AH_ID = "AH-REPORT"
AH_THESIS = (
    "Wave AH lift dual-arm on 7th held-out pack: CTXLIFT+FASTLIFT "
    "PROMOTE; GENLIFT/SMARTLIFT/APPLIFT/AH-HITL HOLD on gen<5; "
    "ship claim remains AF packaged stack — not open chat LM"
)

# Frozen dual-arm Cursor ASK→EVAL→FIX closeout (§5 / SESSION).
AH_HITL_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AH0",
        "id": "SESSION",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "freeze 10 held-out asks ≠ AB…AG",
    },
    {
        "stage": "AH1",
        "id": "H-GENLIFT",
        "lookup_mean": 9.0,
        "gen_mean": 4.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "HOLD",
        "note": "anti-period; open mid 4.0 <5",
    },
    {
        "stage": "AH2",
        "id": "H-CTXLIFT",
        "lookup_mean": 9.0,
        "gen_mean": 1.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "penta-doc L_eff↑ vs CTXREAL",
    },
    {
        "stage": "AH3",
        "id": "H-SMARTLIFT",
        "lookup_mean": 9.0,
        "gen_mean": 4.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "HOLD",
        "note": "cite 10/10; gen ties SMARTREAL 4.0",
    },
    {
        "stage": "AH4",
        "id": "H-FASTLIFT",
        "lookup_mean": 9.0,
        "gen_mean": 1.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "hot wall 11.6 < FASTREAL 16.1",
    },
    {
        "stage": "AH5",
        "id": "H-APPLIFT",
        "lookup_mean": 8.33,
        "gen_mean": 1.0,
        "errors": "0/SERVE",
        "fix": 0,
        "decision": "HOLD",
        "note": "expose LOOKUP|GENERATE + DEPL-AH",
    },
    {
        "stage": "AH6",
        "id": "AH-HITL-10",
        "lookup_mean": 9.0,
        "gen_mean": 1.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "HOLD",
        "note": "final dual-arm; ship claim=AF",
    },
    {
        "stage": "AH7",
        "id": "AH-REPORT",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "public summary + paper-lab + anti-FP",
    },
    {
        "stage": "AH8",
        "id": "AH-FREEZE",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "lock; no Wave AI invent",
    },
)

AH_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ah-session.md",
    "docs/results/nano-lm/formal-hgenlift-genlift.md",
    "docs/results/nano-lm/formal-hctxlift-ctxlift.md",
    "docs/results/nano-lm/formal-hsmartlift-smartlift.md",
    "docs/results/nano-lm/formal-hfastlift-fastlift.md",
    "docs/results/nano-lm/formal-happlift-applift.md",
    "docs/results/nano-lm/depl-ah.md",
    "docs/results/nano-lm/applift-known.md",
    "docs/results/nano-lm/applift-howto.md",
    "docs/results/nano-lm/applift-longdoc.md",
    "docs/results/nano-lm/wave-ah-hitl.md",
    "docs/results/nano-lm/wave-ah-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ah.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AH_REPORT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "FROZEN",
    "H-GENLIFT",
    "H-CTXLIFT",
    "H-SMARTLIFT",
    "H-FASTLIFT",
    "H-APPLIFT",
    "AH-HITL-10",
    "FIX",
    "LOOKUP",
    "GENERATE",
    "anti-FP",
    "HOLD",
    "not open chat",
    "AF packaged stack",
)


def decide_ah_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AH_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AH report evidence
    WHEN deciding AH-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AH_ID}: {AH_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AH_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AH_HITL_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking dual-arm HITL + FIX log (§5 AH7)
    THEN every model id appears and FIX + LOOKUP/GENERATE columns exist.
    """
    body = str(text)
    if "FIX count" not in body:
        return False
    if "Lookup mean" not in body or "Gen mean" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid == "AH-HITL-10":
            if f"**{mid}**" not in body:
                return False
    return True


def antifp_section_ok(text: str) -> bool:
    """
    GIVEN summary body
    WHEN checking anti-FP evidence block
    THEN require dual-arm law + LOOKUP≠IQ + telemetry keys named.
    """
    body = str(text)
    need = (
        "anti-FP",
        "LOOKUP",
        "GENERATE",
        "wall_ms",
        "n_new",
        "not generative IQ",
    )
    return all(m in body for m in need)


def render_wave_ah_summary() -> str:
    lines = [
        "# Wave AH — lift dual-arm · longer/faster/apps "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §5 · Paper-lab: "
        "[paper-lab-wave-ah.md](paper-lab-wave-ah.md) · "
        "HITL: [wave-ah-hitl.md](wave-ah-hitl.md) · "
        "Freeze: [ah-freeze.md](ah-freeze.md)  ",
        "> Parent: Wave AG **AG-FREEZE** reopen · Ship claim: "
        "**AF packaged stack** (unchanged)",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + AH_THESIS
        + ".**",
        "",
        "## Stage scoreboard (Cursor ASK→EVAL→FIX dual-arm)",
        "",
        "| # | ID | Lookup mean | Gen mean | Errors | FIX count | Decision | Note |",
        "|---|-----|------------:|---------:|--------|----------:|----------|------|",
    ]
    for row in AH_HITL_SCOREBOARD:
        lm = (
            "—"
            if row["lookup_mean"] is None
            else f"{float(row['lookup_mean']):g}"
        )
        gm = (
            "—"
            if row["gen_mean"] is None
            else f"{float(row['gen_mean']):g}"
        )
        err = "—" if row["errors"] is None else str(row["errors"])
        lines.append(
            f"| {row['stage']} | **{row['id']}** | {lm} | {gm} | {err} | "
            f"**{row['fix']}** | **{row['decision']}** | {row['note']} |"
        )
    lines.extend(
        [
            "",
            "## Anti-FP evidence (mandatory)",
            "",
            "| Rule | Evidence |",
            "|------|----------|",
            "| LOOKUP labeled ≠ GENERATE | every AH stage dual-arm log |",
            "| Generative arm `wall_ms>0` · `n_new>0` | CTXLIFT · FASTLIFT · AH-HITL-10 |",
            "| Cursor scores **completion** (not auto TRUE_HIT→9 as IQ) | GENLIFT/SMARTLIFT gen 4.0 · final gen 1.0 |",
            "| LOOKUP high score ≠ generative IQ | LOOKUP 9.0 / 8.33 with gen HOLD |",
            "| LOOKUP scores are not generative IQ | dual-arm scoreboard + HOLD gates |",
            "| No LOOKUP-only smarter-LM PROMOTE | GENLIFT · SMARTLIFT · APPLIFT · AH-HITL-10 **HOLD** |",
            "",
            "## Honest product claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| Longer usable ctx (AH) | **H-CTXLIFT** PROMOTE; L_eff **111578** > CTXREAL |",
            "| Smarter gen (AH) | **H-GENLIFT** / **H-SMARTLIFT** HOLD — gen **4.0** < 5 |",
            "| Faster generative ask | **H-FASTLIFT** PROMOTE — hot **11.6** < FASTREAL **16.1** |",
            "| Apps expose arms | **H-APPLIFT** HOLD — DEPL-AH dual-arm |",
            "| Final dual-arm HITL | **AH-HITL-10** LOOKUP **9.0** · GEN **1.0** · **HOLD** |",
            "| Ship claim | **AF packaged stack** — not open chat |",
            "| “Open chat LM ≤5M” | **False** — not open chat |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:ah:report",
            "npm run nano:ah:session",
            "npm run nano:genlift",
            "npm run nano:ctxlift",
            "npm run nano:smartlift",
            "npm run nano:fastlift",
            "npm run nano:applift",
            "npm run nano:ah:hitl",
            "npm run nano:ah:freeze",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave AI without "
            "lab-book reopen · claim open chat.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_ah() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AH (lift dual-arm · longer/faster/apps)",
            "",
            "> Companion to [wave-ah-summary.md](wave-ah-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · Final HITL: "
            "[wave-ah-hitl.md](wave-ah-hitl.md) · "
            "Freeze: [ah-freeze.md](ah-freeze.md) · "
            "Parent: [ag-freeze.md](ag-freeze.md) · "
            "Ship: **AF packaged stack**",
            "",
            "## Question",
            "",
            "After AG froze anti-FP dual-arm with gen still below 5, can a "
            "**seventh** held-out 10 lift **context**, **speed**, "
            "**cite/gen**, and **apps** without false-positive “smarter LM” "
            "or open-chat claims?",
            "",
            "## Answer",
            "",
            "**Partially — as systems lifts; not as open chat.** Wave AH "
            "promotes CTXLIFT and FASTLIFT; HOLDs GENLIFT, SMARTLIFT, "
            "APPLIFT, and final AH-HITL-10 on gen<5. Ship claim remains "
            "the **AF packaged stack**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-GENLIFT | Anti-period; gen 4.0 → HOLD |",
            "| H-CTXLIFT | Penta-doc L_eff↑ vs CTXREAL → PROMOTE |",
            "| H-SMARTLIFT | Cite 10/10; gen 4.0 → HOLD |",
            "| H-FASTLIFT | Hot wall 11.6 < FASTREAL 16.1 → PROMOTE |",
            "| H-APPLIFT | Apps expose LOOKUP\\|GENERATE + DEPL-AH → HOLD |",
            "| AH-HITL-10 | Final L=9.0 G=1.0 → HOLD; ship=AF |",
            "| AH-FREEZE | Locked; no Wave AI invent without reopen |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP mean 9.0 with GENERATE mean 1.0–4.0 must **HOLD** "
            "intelligence claims. Telemetry (`mode`, `wall_ms`, `n_new`) "
            "is mandatory.",
            "",
            "## Takeaway one-liner",
            "",
            "**AH = ctx+speed lift under anti-FP; ship stays AF packaged "
            "stack — not open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-ah-summary.md](wave-ah-summary.md) · "
            "[wave-ah-hitl.md](wave-ah-hitl.md) · "
            "[ah-freeze.md](ah-freeze.md) · "
            "[wave-ag-summary.md](wave-ag-summary.md)  ",
            "- Formals: GENLIFT · CTXLIFT · SMARTLIFT · FASTLIFT · APPLIFT  ",
            "- Deploy: [depl-ah.md](depl-ah.md) · Apps: "
            "[applift-known.md](applift-known.md) · "
            "[applift-howto.md](applift-howto.md) · "
            "[applift-longdoc.md](applift-longdoc.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
