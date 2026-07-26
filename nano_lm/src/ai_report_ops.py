"""Wave AI REPORT: public closeout (dual-arm HITL + FIX + anti-FP)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "AI_ID",
    "AI_THESIS",
    "AI_EVIDENCE",
    "AI_REPORT_MARKERS",
    "AI_HITL_SCOREBOARD",
    "decide_ai_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "render_wave_ai_summary",
    "render_paper_lab_wave_ai",
]

AI_ID = "AI-REPORT"
AI_THESIS = (
    "Wave AI push dual-arm on 8th held-out pack: CTXPUSH+FASTPUSH "
    "PROMOTE; GENPLUS/SMARTPUSH/APPPUSH/AI-HITL HOLD on gen<5; "
    "CAPRENEG HOLD keeps ≤5M; ship claim remains AF packaged stack — "
    "not open chat LM"
)

# Frozen dual-arm Cursor ASK→EVAL→FIX closeout (§5 / SESSION).
AI_HITL_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AI0",
        "id": "SESSION",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "freeze 10 held-out asks ≠ AB…AH",
    },
    {
        "stage": "AI1",
        "id": "H-GENPLUS",
        "lookup_mean": 9.0,
        "gen_mean": 4.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "HOLD",
        "note": "grounded QPFB2; open mid 4.0 <5",
    },
    {
        "stage": "AI1b",
        "id": "H-CAPRENEG",
        "lookup_mean": 9.0,
        "gen_mean": 4.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "HOLD",
        "note": "CAP-125M probe; keep ≤5M",
    },
    {
        "stage": "AI2",
        "id": "H-CTXPUSH",
        "lookup_mean": 9.0,
        "gen_mean": 1.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "hexa-doc L_eff 162851 > CTXLIFT",
    },
    {
        "stage": "AI3",
        "id": "H-SMARTPUSH",
        "lookup_mean": 9.0,
        "gen_mean": 4.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "HOLD",
        "note": "hexa-hop cite 10/10; gen ties 4.0",
    },
    {
        "stage": "AI4",
        "id": "H-FASTPUSH",
        "lookup_mean": 9.0,
        "gen_mean": 1.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "hot wall 10.7 < FASTLIFT 11.6",
    },
    {
        "stage": "AI5",
        "id": "H-APPPUSH",
        "lookup_mean": 8.33,
        "gen_mean": 4.0,
        "errors": "0/SERVE",
        "fix": 0,
        "decision": "HOLD",
        "note": "expose LOOKUP|GENERATE + DEPL-AI",
    },
    {
        "stage": "AI6",
        "id": "AI-HITL-10",
        "lookup_mean": 9.0,
        "gen_mean": 4.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "HOLD",
        "note": "final dual-arm; ship claim=AF",
    },
    {
        "stage": "AI7",
        "id": "AI-REPORT",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "public summary + paper-lab + anti-FP",
    },
    {
        "stage": "AI8",
        "id": "AI-FREEZE",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "lock; no Wave AJ invent",
    },
)

AI_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ai-session.md",
    "docs/results/nano-lm/formal-hgenplus-genplus.md",
    "docs/results/nano-lm/formal-hcapreneg-capreneg.md",
    "docs/results/nano-lm/formal-hctxpush-ctxpush.md",
    "docs/results/nano-lm/formal-hsmartpush-smartpush.md",
    "docs/results/nano-lm/formal-hfastpush-fastpush.md",
    "docs/results/nano-lm/formal-happpush-apppush.md",
    "docs/results/nano-lm/depl-ai.md",
    "docs/results/nano-lm/apppush-known.md",
    "docs/results/nano-lm/apppush-howto.md",
    "docs/results/nano-lm/apppush-longdoc.md",
    "docs/results/nano-lm/wave-ai-hitl.md",
    "docs/results/nano-lm/wave-ai-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ai.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AI_REPORT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "FROZEN",
    "H-GENPLUS",
    "H-CTXPUSH",
    "H-SMARTPUSH",
    "H-FASTPUSH",
    "H-APPPUSH",
    "AI-HITL-10",
    "FIX",
    "LOOKUP",
    "GENERATE",
    "anti-FP",
    "HOLD",
    "not open chat",
    "AF packaged stack",
)


def decide_ai_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AI_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AI report evidence
    WHEN deciding AI-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AI_ID}: {AI_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AI_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AI_HITL_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking dual-arm HITL + FIX log (§5 AI7)
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
        if mid.startswith("H-") or mid == "AI-HITL-10":
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


def render_wave_ai_summary() -> str:
    lines = [
        "# Wave AI — push dual-arm · longer/faster/smarter/apps "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §5 · Paper-lab: "
        "[paper-lab-wave-ai.md](paper-lab-wave-ai.md) · "
        "HITL: [wave-ai-hitl.md](wave-ai-hitl.md) · "
        "Freeze: [ai-freeze.md](ai-freeze.md)  ",
        "> Parent: Wave AH **AH-FREEZE** reopen · Ship claim: "
        "**AF packaged stack** (unchanged)",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + AI_THESIS
        + ".**",
        "",
        "## Stage scoreboard (Cursor ASK→EVAL→FIX dual-arm)",
        "",
        "| # | ID | Lookup mean | Gen mean | Errors | FIX count | Decision | Note |",
        "|---|-----|------------:|---------:|--------|----------:|----------|------|",
    ]
    for row in AI_HITL_SCOREBOARD:
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
            "| LOOKUP labeled ≠ GENERATE | every AI stage dual-arm log |",
            "| Generative arm `wall_ms>0` · `n_new>0` | CTXPUSH · FASTPUSH · AI-HITL-10 |",
            "| Cursor scores **completion** (not auto TRUE_HIT→9 as IQ) | GENPLUS/SMARTPUSH/APPPUSH gen 4.0 · final gen 4.0 |",
            "| LOOKUP high score ≠ generative IQ | LOOKUP 9.0 / 8.33 with gen HOLD |",
            "| LOOKUP scores are not generative IQ | dual-arm scoreboard + HOLD gates |",
            "| No LOOKUP-only smarter-LM PROMOTE | GENPLUS · SMARTPUSH · APPPUSH · AI-HITL-10 **HOLD** |",
            "",
            "## Honest product claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| Longer usable ctx (AI) | **H-CTXPUSH** PROMOTE; L_eff **162851** > CTXLIFT |",
            "| Smarter gen (AI) | **H-GENPLUS** / **H-SMARTPUSH** HOLD — gen **4.0** < 5 |",
            "| Faster generative ask | **H-FASTPUSH** PROMOTE — hot **10.7** < FASTLIFT **11.6** |",
            "| Apps expose arms | **H-APPPUSH** HOLD — DEPL-AI dual-arm · SERVE gen 4.0 |",
            "| ≤5M hard law | **H-CAPRENEG** HOLD — keep ≤5M after CAP-125M |",
            "| Final dual-arm HITL | **AI-HITL-10** LOOKUP **9.0** · GEN **4.0** · **HOLD** |",
            "| Ship claim | **AF packaged stack** — not open chat |",
            "| “Open chat LM ≤5M” | **False** — not open chat |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:ai:report",
            "npm run nano:ai:session",
            "npm run nano:genplus",
            "npm run nano:capreneg",
            "npm run nano:ctxpush",
            "npm run nano:smartpush",
            "npm run nano:fastpush",
            "npm run nano:apppush",
            "npm run nano:ai:hitl",
            "npm run nano:ai:freeze",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave AJ without "
            "lab-book reopen · claim open chat.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_ai() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AI (push dual-arm · longer/faster/smarter/apps)",
            "",
            "> Companion to [wave-ai-summary.md](wave-ai-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · Final HITL: "
            "[wave-ai-hitl.md](wave-ai-hitl.md) · "
            "Freeze: [ai-freeze.md](ai-freeze.md) · "
            "Parent: [ah-freeze.md](ah-freeze.md) · "
            "Ship: **AF packaged stack**",
            "",
            "## Question",
            "",
            "After AH froze lift dual-arm with gen still below 5, can an "
            "**eighth** held-out 10 push **context**, **speed**, "
            "**cite/gen**, and **apps** beyond AH without false-positive "
            "“smarter LM” or open-chat claims — and without raising ≤5M?",
            "",
            "## Answer",
            "",
            "**Partially — as systems pushes; not as open chat.** Wave AI "
            "promotes CTXPUSH and FASTPUSH; HOLDs GENPLUS, SMARTPUSH, "
            "APPPUSH, CAPRENEG (≤5M stays), and final AI-HITL-10 on gen<5. "
            "Ship claim remains the **AF packaged stack**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-GENPLUS | Grounded QPFB2; gen 4.0 → HOLD |",
            "| H-CAPRENEG | CAP-125M probe; keep ≤5M → HOLD |",
            "| H-CTXPUSH | Hexa-doc L_eff 162851 > CTXLIFT → PROMOTE |",
            "| H-SMARTPUSH | Hexa-hop cite 10/10; gen 4.0 → HOLD |",
            "| H-FASTPUSH | Hot wall 10.7 < FASTLIFT 11.6 → PROMOTE |",
            "| H-APPPUSH | Apps expose LOOKUP\\|GENERATE + DEPL-AI → HOLD |",
            "| AI-HITL-10 | Final L=9.0 G=4.0 → HOLD; ship=AF |",
            "| AI-FREEZE | Locked; no Wave AJ invent without reopen |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP mean 9.0 with GENERATE mean 1.0–4.0 must **HOLD** "
            "intelligence claims. Telemetry (`mode`, `wall_ms`, `n_new`) "
            "is mandatory. Peak gen across AI stays **4.0**.",
            "",
            "## Takeaway one-liner",
            "",
            "**AI = ctx+speed push under anti-FP; gen still HOLD; ship "
            "stays AF packaged stack — not open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-ai-summary.md](wave-ai-summary.md) · "
            "[wave-ai-hitl.md](wave-ai-hitl.md) · "
            "[ai-freeze.md](ai-freeze.md) · "
            "[wave-ah-summary.md](wave-ah-summary.md)  ",
            "- Formals: GENPLUS · CAPRENEG · CTXPUSH · SMARTPUSH · "
            "FASTPUSH · APPPUSH  ",
            "- Deploy: [depl-ai.md](depl-ai.md) · Apps: "
            "[apppush-known.md](apppush-known.md) · "
            "[apppush-howto.md](apppush-howto.md) · "
            "[apppush-longdoc.md](apppush-longdoc.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
