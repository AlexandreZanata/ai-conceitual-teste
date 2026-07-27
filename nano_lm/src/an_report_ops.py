"""Wave AN REPORT: public closeout (dual-arm HITL + FIX + anti-FP)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "AN_ID",
    "AN_THESIS",
    "AN_EVIDENCE",
    "AN_REPORT_MARKERS",
    "AN_HITL_SCOREBOARD",
    "decide_an_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "render_wave_an_summary",
    "render_paper_lab_wave_an",
]

AN_ID = "AN-REPORT"
AN_THESIS = (
    "Wave AN edge dual-arm on 13th held-out pack: GENEDGE HOLD · "
    "CTXEDGE·SMARTEDGE·FASTEDGE·APPEDGE·AN-HITL all PROMOTE; "
    "CAPCHECK skipped; gen≥5 via GENEDGE peak; L_eff↑ · wall↓ · "
    "apps+DEPL; ship claim remains AF packaged stack — not open chat LM"
)

# Frozen dual-arm Cursor ASK→EVAL→FIX closeout (§3 / SESSION).
AN_HITL_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AN0",
        "id": "SESSION",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "freeze 10 held-out asks ≠ AB…AM",
    },
    {
        "stage": "AN1",
        "id": "H-GENEDGE",
        "lookup_mean": 9.0,
        "gen_mean": 4.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "HOLD",
        "note": "ablated gen 4.0; peak_only_lift; anti-FP",
    },
    {
        "stage": "AN1b",
        "id": "H-CAPCHECK",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "SKIPPED",
        "note": "size hypothesis unused; ≤5M stays",
    },
    {
        "stage": "AN2",
        "id": "H-CTXEDGE",
        "lookup_mean": 9.0,
        "gen_mean": 1.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "undeca-doc L_eff 242448 > CTXNEXT",
    },
    {
        "stage": "AN3",
        "id": "H-SMARTEDGE",
        "lookup_mean": 9.0,
        "gen_mean": 9.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "undeca-hop cite 10/10; false-hit 0",
    },
    {
        "stage": "AN4",
        "id": "H-FASTEDGE",
        "lookup_mean": 9.0,
        "gen_mean": 7.0,
        "errors": "0/10",
        "fix": 1,
        "decision": "PROMOTE",
        "note": "peak-fast hot 0.05 ≪ FASTNEXT 0.17",
    },
    {
        "stage": "AN5",
        "id": "H-APPEDGE",
        "lookup_mean": 8.33,
        "gen_mean": 9.0,
        "errors": "0/SERVE",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "expose LOOKUP|GENERATE + DEPL-AN",
    },
    {
        "stage": "AN6",
        "id": "AN-HITL-10",
        "lookup_mean": 9.0,
        "gen_mean": 9.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "final dual-arm; peak product; ship=AF",
    },
    {
        "stage": "AN7",
        "id": "AN-REPORT",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "public summary + paper-lab + anti-FP",
    },
    {
        "stage": "AN8",
        "id": "AN-FREEZE",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "lock; no Wave AO invent",
    },
)

AN_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-an-session.md",
    "docs/results/nano-lm/formal-hgenedge-genedge.md",
    "docs/results/nano-lm/formal-hctxedge-ctxedge.md",
    "docs/results/nano-lm/formal-hsmartedge-smartedge.md",
    "docs/results/nano-lm/formal-hfastedge-fastedge.md",
    "docs/results/nano-lm/formal-happedge-appedge.md",
    "docs/results/nano-lm/depl-an.md",
    "docs/results/nano-lm/appedge-known.md",
    "docs/results/nano-lm/appedge-howto.md",
    "docs/results/nano-lm/appedge-longdoc.md",
    "docs/results/nano-lm/wave-an-hitl.md",
    "docs/results/nano-lm/wave-an-summary.md",
    "docs/results/nano-lm/paper-lab-wave-an.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AN_REPORT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "FROZEN",
    "H-GENEDGE",
    "H-CTXEDGE",
    "H-SMARTEDGE",
    "H-FASTEDGE",
    "H-APPEDGE",
    "AN-HITL-10",
    "FIX",
    "LOOKUP",
    "GENERATE",
    "anti-FP",
    "PROMOTE",
    "not open chat",
    "AF packaged stack",
)


def decide_an_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AN_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AN report evidence
    WHEN deciding AN-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AN_ID}: {AN_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AN_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AN_HITL_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking dual-arm HITL + FIX log (§3 AN7)
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
        if mid.startswith("H-") or mid == "AN-HITL-10":
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


def render_wave_an_summary() -> str:
    lines = [
        "# Wave AN — edge dual-arm · longer/faster/smarter/apps "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §3 · Paper-lab: "
        "[paper-lab-wave-an.md](paper-lab-wave-an.md) · "
        "HITL: [wave-an-hitl.md](wave-an-hitl.md) · "
        "Freeze: [an-freeze.md](an-freeze.md)  ",
        "> Parent: Wave AM **AM-FREEZE** reopen · Ship claim: "
        "**AF packaged stack** (unchanged)",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + AN_THESIS
        + ".**",
        "",
        "## Stage scoreboard (Cursor ASK→EVAL→FIX dual-arm)",
        "",
        "| # | ID | Lookup mean | Gen mean | Errors | FIX count | Decision | Note |",
        "|---|-----|------------:|---------:|--------|----------:|----------|------|",
    ]
    for row in AN_HITL_SCOREBOARD:
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
            "| LOOKUP labeled ≠ GENERATE | every AN stage dual-arm log |",
            "| Generative arm `wall_ms>0` · `n_new>0` | GENEDGE · CTXEDGE · FASTEDGE · AN-HITL-10 |",
            "| Cursor scores **completion** (not auto TRUE_HIT→9 as IQ) | SMARTEDGE/APPEDGE/HITL gen 9.0 peak spans |",
            "| LOOKUP high score ≠ generative IQ | LOOKUP 9.0 with peak gen product claim |",
            "| LOOKUP scores are not generative IQ | dual-arm scoreboard + anti-FP notes |",
            "| Peak gen ≠ open-chat TinyStories IQ | extractive peak from curated context (GENEDGE doctrine) |",
            "| CTXEDGE periods ≠ smarter LM | gen 1.0 · L_eff claim only |",
            "| Ablated gen HOLD honesty | H-GENEDGE ablated 4.0 · peak_only_lift |",
            "",
            "## Honest product claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| Longer usable ctx (AN) | **H-CTXEDGE** PROMOTE; L_eff **242448** > CTXNEXT |",
            "| Smarter cite+gen (AN) | **H-SMARTEDGE** PROMOTE — gen **9.0** ≥ 5 (GENEDGE peak) |",
            "| True-gen ablation | **H-GENEDGE** HOLD — ablated gen **4.0** |",
            "| Faster generative ask | **H-FASTEDGE** PROMOTE — hot **0.05** ≪ FASTNEXT **0.17** |",
            "| Apps expose arms | **H-APPEDGE** PROMOTE — DEPL-AN dual-arm · SERVE gen 9.0 |",
            "| ≤5M hard law | **H-CAPCHECK** SKIPPED — keep ≤5M |",
            "| Final dual-arm HITL | **AN-HITL-10** LOOKUP **9.0** · GEN **9.0** · **PROMOTE** |",
            "| Ship claim | **AF packaged stack** — not open chat |",
            "| “Open chat LM ≤5M” | **False** — not open chat |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:an:report",
            "npm run nano:an:session",
            "npm run nano:genedge",
            "npm run nano:ctxedge",
            "npm run nano:smartedge",
            "npm run nano:fastedge",
            "npm run nano:appedge",
            "npm run nano:an:hitl",
            "npm run nano:an:freeze",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave AO without "
            "lab-book reopen · claim open chat · sell CTXEDGE periods as IQ · "
            "sell GENEDGE peak as open-chat IQ.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_an() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AN (edge dual-arm · longer/faster/smarter/apps)",
            "",
            "> Companion to [wave-an-summary.md](wave-an-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · Final HITL: "
            "[wave-an-hitl.md](wave-an-hitl.md) · "
            "Freeze: [an-freeze.md](an-freeze.md) · "
            "Parent: [am-freeze.md](am-freeze.md) · "
            "Ship: **AF packaged stack**",
            "",
            "## Question",
            "",
            "After AM froze next dual-arm, can a **thirteenth** held-out 10 "
            "push **edge context**, **edge speed**, **edge cite/gen**, "
            "and **apps** beyond AM without false-positive “open chat” "
            "claims — and without raising ≤5M?",
            "",
            "## Answer",
            "",
            "**Yes — as grounded peak product systems; not as open chat.** "
            "Wave AN promotes CTXEDGE, SMARTEDGE, FASTEDGE, APPEDGE, and "
            "final AN-HITL-10 with gen≥5 via GENEDGE extractive peak. "
            "H-GENEDGE HOLDs on ablated true-gen (4.0). CAPCHECK skipped "
            "(≤5M stays). Ship claim remains the **AF packaged stack**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-GENEDGE | Ablated gen 4.0 → HOLD; peak_only_lift labeled |",
            "| H-CAPCHECK | Skipped; keep ≤5M |",
            "| H-CTXEDGE | Undeca-doc L_eff 242448 > CTXNEXT → PROMOTE |",
            "| H-SMARTEDGE | Undeca-hop cite 10/10; gen 9.0 → PROMOTE |",
            "| H-FASTEDGE | Hot wall 0.05 ≪ FASTNEXT 0.17 → PROMOTE |",
            "| H-APPEDGE | Apps expose LOOKUP\\|GENERATE + DEPL-AN → PROMOTE |",
            "| AN-HITL-10 | Final L=9.0 G=9.0 → PROMOTE; ship=AF |",
            "| AN-FREEZE | Locked; no Wave AO invent without reopen |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP mean 9.0 must never be sold as generative IQ. Peak "
            "gen **9.0** is extractive from curated context — not "
            "open-chat TinyStories. CTXEDGE gen **1.0** periods are "
            "L_eff-only. GENEDGE ablated **4.0** remains the honest "
            "true-gen bar. Telemetry (`mode`, `wall_ms`, `n_new`) is "
            "mandatory.",
            "",
            "## Takeaway one-liner",
            "",
            "**AN = edge dual-arm under anti-FP; gen≥5 via GENEDGE peak; "
            "ablated HOLD honest; ship stays AF packaged stack — not "
            "open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-an-summary.md](wave-an-summary.md) · "
            "[wave-an-hitl.md](wave-an-hitl.md) · "
            "[an-freeze.md](an-freeze.md) · "
            "[wave-am-summary.md](wave-am-summary.md)  ",
            "- Formals: GENEDGE · CTXEDGE · SMARTEDGE · FASTEDGE · "
            "APPEDGE  ",
            "- Deploy: [depl-an.md](depl-an.md) · Apps: "
            "[appedge-known.md](appedge-known.md) · "
            "[appedge-howto.md](appedge-howto.md) · "
            "[appedge-longdoc.md](appedge-longdoc.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
