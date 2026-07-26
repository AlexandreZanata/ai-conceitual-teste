"""Wave AJ REPORT: public closeout (dual-arm HITL + FIX + anti-FP)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "AJ_ID",
    "AJ_THESIS",
    "AJ_EVIDENCE",
    "AJ_REPORT_MARKERS",
    "AJ_HITL_SCOREBOARD",
    "decide_aj_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "render_wave_aj_summary",
    "render_paper_lab_wave_aj",
]

AJ_ID = "AJ-REPORT"
AJ_THESIS = (
    "Wave AJ peak dual-arm on 9th held-out pack: GENPEAK·CTXPEAK·"
    "SMARTPEAK·FASTPEAK·APPPEAK·AJ-HITL all PROMOTE; CAPCHECK skipped; "
    "gen≥5 via grounded extractive peak; ship claim remains AF "
    "packaged stack — not open chat LM"
)

# Frozen dual-arm Cursor ASK→EVAL→FIX closeout (§3 / SESSION).
AJ_HITL_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AJ0",
        "id": "SESSION",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "freeze 10 held-out asks ≠ AB…AI",
    },
    {
        "stage": "AJ1",
        "id": "H-GENPEAK",
        "lookup_mean": 9.0,
        "gen_mean": 9.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "grounded+extractive peak; gen≥5",
    },
    {
        "stage": "AJ1b",
        "id": "H-CAPCHECK",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "SKIPPED",
        "note": "gen≥5 without size reopen; ≤5M stays",
    },
    {
        "stage": "AJ2",
        "id": "H-CTXPEAK",
        "lookup_mean": 9.0,
        "gen_mean": 1.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "hepta-doc L_eff 177809 > CTXPUSH",
    },
    {
        "stage": "AJ3",
        "id": "H-SMARTPEAK",
        "lookup_mean": 9.0,
        "gen_mean": 9.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "hepta-hop cite 10/10; gen 9.0 > SMARTPUSH",
    },
    {
        "stage": "AJ4",
        "id": "H-FASTPEAK",
        "lookup_mean": 9.0,
        "gen_mean": 7.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "peak-fast hot ~5.0ms < FASTPUSH 10.7",
    },
    {
        "stage": "AJ5",
        "id": "H-APPPEAK",
        "lookup_mean": 8.33,
        "gen_mean": 9.0,
        "errors": "0/SERVE",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "expose LOOKUP|GENERATE + DEPL-AJ",
    },
    {
        "stage": "AJ6",
        "id": "AJ-HITL-10",
        "lookup_mean": 9.0,
        "gen_mean": 9.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "final dual-arm; peak product; ship=AF",
    },
    {
        "stage": "AJ7",
        "id": "AJ-REPORT",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "public summary + paper-lab + anti-FP",
    },
    {
        "stage": "AJ8",
        "id": "AJ-FREEZE",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "lock; no Wave AK invent",
    },
)

AJ_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-aj-session.md",
    "docs/results/nano-lm/formal-hgenpeak-genpeak.md",
    "docs/results/nano-lm/formal-hctxpeak-ctxpeak.md",
    "docs/results/nano-lm/formal-hsmartpeak-smartpeak.md",
    "docs/results/nano-lm/formal-hfastpeak-fastpeak.md",
    "docs/results/nano-lm/formal-happpeak-apppeak.md",
    "docs/results/nano-lm/depl-aj.md",
    "docs/results/nano-lm/apppeak-known.md",
    "docs/results/nano-lm/apppeak-howto.md",
    "docs/results/nano-lm/apppeak-longdoc.md",
    "docs/results/nano-lm/wave-aj-hitl.md",
    "docs/results/nano-lm/wave-aj-summary.md",
    "docs/results/nano-lm/paper-lab-wave-aj.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AJ_REPORT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "FROZEN",
    "H-GENPEAK",
    "H-CTXPEAK",
    "H-SMARTPEAK",
    "H-FASTPEAK",
    "H-APPPEAK",
    "AJ-HITL-10",
    "FIX",
    "LOOKUP",
    "GENERATE",
    "anti-FP",
    "PROMOTE",
    "not open chat",
    "AF packaged stack",
)


def decide_aj_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AJ_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AJ report evidence
    WHEN deciding AJ-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AJ_ID}: {AJ_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AJ_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AJ_HITL_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking dual-arm HITL + FIX log (§3 AJ7)
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
        if mid.startswith("H-") or mid == "AJ-HITL-10":
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


def render_wave_aj_summary() -> str:
    lines = [
        "# Wave AJ — peak dual-arm · longer/faster/smarter/apps "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §3 · Paper-lab: "
        "[paper-lab-wave-aj.md](paper-lab-wave-aj.md) · "
        "HITL: [wave-aj-hitl.md](wave-aj-hitl.md) · "
        "Freeze: [aj-freeze.md](aj-freeze.md)  ",
        "> Parent: Wave AI **AI-FREEZE** reopen · Ship claim: "
        "**AF packaged stack** (unchanged)",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + AJ_THESIS
        + ".**",
        "",
        "## Stage scoreboard (Cursor ASK→EVAL→FIX dual-arm)",
        "",
        "| # | ID | Lookup mean | Gen mean | Errors | FIX count | Decision | Note |",
        "|---|-----|------------:|---------:|--------|----------:|----------|------|",
    ]
    for row in AJ_HITL_SCOREBOARD:
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
            "| LOOKUP labeled ≠ GENERATE | every AJ stage dual-arm log |",
            "| Generative arm `wall_ms>0` · `n_new>0` | GENPEAK · CTXPEAK · FASTPEAK · AJ-HITL-10 |",
            "| Cursor scores **completion** (not auto TRUE_HIT→9 as IQ) | GENPEAK/SMARTPEAK/APPPEAK/HITL gen 9.0 peak spans |",
            "| LOOKUP high score ≠ generative IQ | LOOKUP 9.0 with peak gen product claim |",
            "| LOOKUP scores are not generative IQ | dual-arm scoreboard + anti-FP notes |",
            "| Peak gen ≠ open-chat TinyStories IQ | extractive peak from curated context (GENPEAK doctrine) |",
            "| CTXPEAK periods ≠ smarter LM | gen 1.0 · L_eff claim only |",
            "",
            "## Honest product claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| Longer usable ctx (AJ) | **H-CTXPEAK** PROMOTE; L_eff **177809** > CTXPUSH |",
            "| Smarter gen (AJ) | **H-GENPEAK** / **H-SMARTPEAK** PROMOTE — gen **9.0** ≥ 5 (grounded peak) |",
            "| Faster generative ask | **H-FASTPEAK** PROMOTE — hot **~5.0** < FASTPUSH **10.7** |",
            "| Apps expose arms | **H-APPPEAK** PROMOTE — DEPL-AJ dual-arm · SERVE gen 9.0 |",
            "| ≤5M hard law | **H-CAPCHECK** SKIPPED — keep ≤5M |",
            "| Final dual-arm HITL | **AJ-HITL-10** LOOKUP **9.0** · GEN **9.0** · **PROMOTE** |",
            "| Ship claim | **AF packaged stack** — not open chat |",
            "| “Open chat LM ≤5M” | **False** — not open chat |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:aj:report",
            "npm run nano:aj:session",
            "npm run nano:genpeak",
            "npm run nano:ctxpeak",
            "npm run nano:smartpeak",
            "npm run nano:fastpeak",
            "npm run nano:apppeak",
            "npm run nano:aj:hitl",
            "npm run nano:aj:freeze",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave AK without "
            "lab-book reopen · claim open chat · sell CTXPEAK periods as IQ.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_aj() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AJ (peak dual-arm · longer/faster/smarter/apps)",
            "",
            "> Companion to [wave-aj-summary.md](wave-aj-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · Final HITL: "
            "[wave-aj-hitl.md](wave-aj-hitl.md) · "
            "Freeze: [aj-freeze.md](aj-freeze.md) · "
            "Parent: [ai-freeze.md](ai-freeze.md) · "
            "Ship: **AF packaged stack**",
            "",
            "## Question",
            "",
            "After AI froze push dual-arm with gen still below 5, can a "
            "**ninth** held-out 10 peak **context**, **speed**, "
            "**cite/gen**, and **apps** beyond AI without false-positive "
            "“open chat” claims — and without raising ≤5M?",
            "",
            "## Answer",
            "",
            "**Yes — as grounded peak product systems; not as open chat.** "
            "Wave AJ promotes GENPEAK, CTXPEAK, SMARTPEAK, FASTPEAK, "
            "APPPEAK, and final AJ-HITL-10 with gen≥5 via extractive peak "
            "from curated context. CAPCHECK skipped (≤5M stays). Ship "
            "claim remains the **AF packaged stack**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-GENPEAK | Grounded+peak; gen 9.0 → PROMOTE |",
            "| H-CAPCHECK | Skipped; keep ≤5M |",
            "| H-CTXPEAK | Hepta-doc L_eff 177809 > CTXPUSH → PROMOTE |",
            "| H-SMARTPEAK | Hepta-hop cite 10/10; gen 9.0 → PROMOTE |",
            "| H-FASTPEAK | Hot wall ~5.0 < FASTPUSH 10.7 → PROMOTE |",
            "| H-APPPEAK | Apps expose LOOKUP\\|GENERATE + DEPL-AJ → PROMOTE |",
            "| AJ-HITL-10 | Final L=9.0 G=9.0 → PROMOTE; ship=AF |",
            "| AJ-FREEZE | Locked; no Wave AK invent without reopen |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP mean 9.0 must never be sold as generative IQ. Peak "
            "gen **9.0** is extractive from curated context — not "
            "open-chat TinyStories. CTXPEAK gen **1.0** periods are "
            "L_eff-only. Telemetry (`mode`, `wall_ms`, `n_new`) is "
            "mandatory.",
            "",
            "## Takeaway one-liner",
            "",
            "**AJ = peak dual-arm under anti-FP; gen≥5 via grounded peak; "
            "ship stays AF packaged stack — not open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-aj-summary.md](wave-aj-summary.md) · "
            "[wave-aj-hitl.md](wave-aj-hitl.md) · "
            "[aj-freeze.md](aj-freeze.md) · "
            "[wave-ai-summary.md](wave-ai-summary.md)  ",
            "- Formals: GENPEAK · CTXPEAK · SMARTPEAK · FASTPEAK · "
            "APPPEAK  ",
            "- Deploy: [depl-aj.md](depl-aj.md) · Apps: "
            "[apppeak-known.md](apppeak-known.md) · "
            "[apppeak-howto.md](apppeak-howto.md) · "
            "[apppeak-longdoc.md](apppeak-longdoc.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
