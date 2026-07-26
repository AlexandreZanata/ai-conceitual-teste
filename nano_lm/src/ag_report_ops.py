"""Wave AG REPORT: public closeout (dual-arm HITL + FIX + anti-FP)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "AG_ID",
    "AG_THESIS",
    "AG_EVIDENCE",
    "AG_REPORT_MARKERS",
    "AG_HITL_SCOREBOARD",
    "decide_ag_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "render_wave_ag_summary",
    "render_paper_lab_wave_ag",
]

AG_ID = "AG-REPORT"
AG_THESIS = (
    "Wave AG anti-FP dual-arm on 6th held-out pack: LOOKUP product ok; "
    "GENERATE below gen≥5 → documented HOLD; ship claim remains "
    "AF packaged stack — not open chat LM"
)

# Frozen dual-arm Cursor ASK→EVAL→FIX closeout (§5 / SESSION).
AG_HITL_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AG0",
        "id": "SESSION",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "freeze 10 held-out asks ≠ AB…AF",
    },
    {
        "stage": "AG1",
        "id": "H-ANTIFP",
        "lookup_mean": 9.0,
        "gen_mean": 1.0,
        "errors": "0/4",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "harness: LOOKUP≠GEN labeled",
    },
    {
        "stage": "AG2",
        "id": "H-CTXREAL",
        "lookup_mean": 9.0,
        "gen_mean": 1.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "quad-doc L_eff↑ vs CTXULTRA",
    },
    {
        "stage": "AG3",
        "id": "H-SMARTREAL",
        "lookup_mean": 9.0,
        "gen_mean": 4.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "HOLD",
        "note": "cite 10/10; gen<5 honest HOLD",
    },
    {
        "stage": "AG4",
        "id": "H-FASTREAL",
        "lookup_mean": 9.0,
        "gen_mean": 1.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "gen wall↓ vs AF raw; ≠ LOOKUP speed IQ",
    },
    {
        "stage": "AG5",
        "id": "H-APPREAL",
        "lookup_mean": 8.33,
        "gen_mean": 1.0,
        "errors": "0/SERVE",
        "fix": 0,
        "decision": "HOLD",
        "note": "expose LOOKUP|GENERATE + DEPL-AG",
    },
    {
        "stage": "AG6",
        "id": "AG-HITL-10",
        "lookup_mean": 9.0,
        "gen_mean": 1.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "HOLD",
        "note": "final dual-arm; ship claim=AF",
    },
    {
        "stage": "AG7",
        "id": "AG-REPORT",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "public summary + paper-lab + anti-FP",
    },
    {
        "stage": "AG8",
        "id": "AG-FREEZE",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "lock; no Wave AH invent",
    },
)

AG_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ag-session.md",
    "docs/results/nano-lm/formal-hantifp-antifp.md",
    "docs/results/nano-lm/formal-hctxreal-ctxreal.md",
    "docs/results/nano-lm/formal-hsmartreal-smartreal.md",
    "docs/results/nano-lm/formal-hfastreal-fastreal.md",
    "docs/results/nano-lm/formal-happreal-appreal.md",
    "docs/results/nano-lm/depl-ag.md",
    "docs/results/nano-lm/appreal-known.md",
    "docs/results/nano-lm/appreal-howto.md",
    "docs/results/nano-lm/appreal-longdoc.md",
    "docs/results/nano-lm/wave-ag-hitl.md",
    "docs/results/nano-lm/wave-ag-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ag.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AG_REPORT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "FROZEN",
    "H-ANTIFP",
    "H-CTXREAL",
    "H-SMARTREAL",
    "H-FASTREAL",
    "H-APPREAL",
    "AG-HITL-10",
    "FIX",
    "LOOKUP",
    "GENERATE",
    "anti-FP",
    "HOLD",
    "not open chat",
    "AF packaged stack",
)


def decide_ag_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AG_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AG report evidence
    WHEN deciding AG-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AG_ID}: {AG_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AG_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AG_HITL_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking dual-arm HITL + FIX log (§5 AG7)
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
        if mid.startswith("H-") or mid == "AG-HITL-10":
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


def render_wave_ag_summary() -> str:
    lines = [
        "# Wave AG — anti-FP dual-arm · real answers "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §5 · Paper-lab: "
        "[paper-lab-wave-ag.md](paper-lab-wave-ag.md) · "
        "HITL: [wave-ag-hitl.md](wave-ag-hitl.md) · "
        "Freeze: [ag-freeze.md](ag-freeze.md)  ",
        "> Parent: Wave AF **AF-FREEZE** reopen · Ship claim: "
        "**AF packaged stack** (unchanged)",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + AG_THESIS
        + ".**",
        "",
        "## Stage scoreboard (Cursor ASK→EVAL→FIX dual-arm)",
        "",
        "| # | ID | Lookup mean | Gen mean | Errors | FIX count | Decision | Note |",
        "|---|-----|------------:|---------:|--------|----------:|----------|------|",
    ]
    for row in AG_HITL_SCOREBOARD:
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
            "| LOOKUP labeled ≠ GENERATE | H-ANTIFP harness + every stage log |",
            "| Generative arm `wall_ms>0` · `n_new>0` | CTXREAL · FASTREAL · AG-HITL-10 |",
            "| Cursor scores **completion** (not auto TRUE_HIT→9 as IQ) | SMARTREAL gen 4.0 · final gen 1.0 |",
            "| LOOKUP high score ≠ generative IQ | LOOKUP 9.0 / 8.33 with gen HOLD |",
            "| LOOKUP scores are not generative IQ | dual-arm scoreboard + HOLD gates |",
            "| No LOOKUP-only smarter-LM PROMOTE | SMARTREAL · APPREAL · AG-HITL-10 **HOLD** |",
            "",
            "## Honest product claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| Longer usable ctx (AG) | **H-CTXREAL** PROMOTE; L_eff↑ vs CTXULTRA |",
            "| Smarter gen (AG) | **H-SMARTREAL** HOLD — gen **4.0** < 5 |",
            "| Faster generative ask | **H-FASTREAL** PROMOTE — wall↓; LOOKUP ≠ speed IQ |",
            "| Apps expose arms | **H-APPREAL** HOLD — DEPL-AG dual-arm |",
            "| Final dual-arm HITL | **AG-HITL-10** LOOKUP **9.0** · GEN **1.0** · **HOLD** |",
            "| Ship claim | **AF packaged stack** — not open chat |",
            "| “Open chat LM ≤5M” | **False** — not open chat |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:ag:report",
            "npm run nano:ag:session",
            "npm run nano:antifp",
            "npm run nano:ctxreal",
            "npm run nano:smartreal",
            "npm run nano:fastreal",
            "npm run nano:appreal",
            "npm run nano:ag:hitl",
            "npm run nano:ag:freeze",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave AH without "
            "lab-book reopen · claim open chat.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_ag() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AG (anti-FP dual-arm · real answers)",
            "",
            "> Companion to [wave-ag-summary.md](wave-ag-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · Final HITL: "
            "[wave-ag-hitl.md](wave-ag-hitl.md) · "
            "Freeze: [ag-freeze.md](ag-freeze.md) · "
            "Parent: [af-freeze.md](af-freeze.md) · "
            "Ship: **AF packaged stack**",
            "",
            "## Question",
            "",
            "After AF froze LOOKUP-heavy apps with `wall_ms=0` TRUE_HIT→9, "
            "can a **sixth** held-out 10 with **anti-FP dual-arm** "
            "(LOOKUP + GENERATE, Cursor-scored completions) produce a "
            "honest smarter/faster/longer/real-app advance without false "
            "positive “smarter LM” claims?",
            "",
            "## Answer",
            "",
            "**Partially — as anti-FP discipline + systems wins; not as "
            "open chat.** Wave AG promotes ANTIFP, CTXREAL, FASTREAL; "
            "HOLDs SMARTREAL, APPREAL, and final AG-HITL-10 on gen<5. "
            "Ship claim remains the **AF packaged stack**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-ANTIFP | Dual-arm harness; LOOKUP≠GEN |",
            "| H-CTXREAL | Quad-doc L_eff↑; LOOKUP 9.0 |",
            "| H-SMARTREAL | Cite 10/10; gen 4.0 → HOLD |",
            "| H-FASTREAL | Gen wall↓ vs AF raw; ≠ LOOKUP speed IQ |",
            "| H-APPREAL | Apps expose LOOKUP\\|GENERATE + DEPL-AG → HOLD |",
            "| AG-HITL-10 | Final L=9.0 G=1.0 → HOLD; ship=AF |",
            "| AG-FREEZE | Locked; no Wave AH invent without reopen |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP mean 9.0 with GENERATE mean 1.0–4.0 must **HOLD** "
            "intelligence claims. Telemetry (`mode`, `wall_ms`, `n_new`) "
            "is mandatory.",
            "",
            "## Takeaway one-liner",
            "",
            "**AG = anti-FP dual-arm truth serum; ship stays AF packaged "
            "stack — not open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-ag-summary.md](wave-ag-summary.md) · "
            "[wave-ag-hitl.md](wave-ag-hitl.md) · "
            "[ag-freeze.md](ag-freeze.md) · "
            "[wave-af-summary.md](wave-af-summary.md)  ",
            "- Formals: ANTIFP · CTXREAL · SMARTREAL · FASTREAL · APPREAL  ",
            "- Deploy: [depl-ag.md](depl-ag.md) · Apps: "
            "[appreal-known.md](appreal-known.md) · "
            "[appreal-howto.md](appreal-howto.md) · "
            "[appreal-longdoc.md](appreal-longdoc.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
