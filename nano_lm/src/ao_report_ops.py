"""Wave AO REPORT: public closeout (dual-arm HITL + FIX + anti-FP)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "AO_ID",
    "AO_THESIS",
    "AO_EVIDENCE",
    "AO_REPORT_MARKERS",
    "AO_HITL_SCOREBOARD",
    "decide_ao_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "render_wave_ao_summary",
    "render_paper_lab_wave_ao",
]

AO_ID = "AO-REPORT"
AO_THESIS = (
    "Wave AO core dual-arm on 14th held-out pack: GENCORE HOLD · "
    "CTXCORE·SMARTCORE·FASTCORE·APPCORE·AO-HITL all PROMOTE; "
    "CAPCHECK skipped; gen≥5 via GENCORE peak; L_eff↑ · wall↓ · "
    "apps+DEPL; ship claim remains AF packaged stack — not open chat LM"
)

# Frozen dual-arm Cursor ASK→EVAL→FIX closeout (§3 / SESSION).
AO_HITL_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AO0",
        "id": "SESSION",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "freeze 10 held-out asks ≠ AB…AN",
    },
    {
        "stage": "AO1",
        "id": "H-GENCORE",
        "lookup_mean": 9.0,
        "gen_mean": 4.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "HOLD",
        "note": "ablated gen 4.0; peak_only_lift; anti-FP",
    },
    {
        "stage": "AO1b",
        "id": "H-CAPCHECK",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "SKIPPED",
        "note": "size hypothesis unused; ≤5M stays",
    },
    {
        "stage": "AO2",
        "id": "H-CTXCORE",
        "lookup_mean": 9.0,
        "gen_mean": 1.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "dodeca-doc L_eff 253105 > CTXEDGE",
    },
    {
        "stage": "AO3",
        "id": "H-SMARTCORE",
        "lookup_mean": 9.0,
        "gen_mean": 9.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "dodeca-hop cite 10/10; false-hit 0",
    },
    {
        "stage": "AO4",
        "id": "H-FASTCORE",
        "lookup_mean": 9.0,
        "gen_mean": 7.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "peak-fast warm 0.06 < FASTEDGE 0.10",
    },
    {
        "stage": "AO5",
        "id": "H-APPCORE",
        "lookup_mean": 8.33,
        "gen_mean": 9.0,
        "errors": "0/SERVE",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "expose LOOKUP|GENERATE + DEPL-AO",
    },
    {
        "stage": "AO6",
        "id": "AO-HITL-10",
        "lookup_mean": 9.0,
        "gen_mean": 9.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "final dual-arm; peak product; ship=AF",
    },
    {
        "stage": "AO7",
        "id": "AO-REPORT",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "public summary + paper-lab + anti-FP",
    },
    {
        "stage": "AO8",
        "id": "AO-FREEZE",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "lock; no Wave AP invent",
    },
)

AO_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ao-session.md",
    "docs/results/nano-lm/formal-hgencore-gencore.md",
    "docs/results/nano-lm/formal-hctxcore-ctxcore.md",
    "docs/results/nano-lm/formal-hsmartcore-smartcore.md",
    "docs/results/nano-lm/formal-hfastcore-fastcore.md",
    "docs/results/nano-lm/formal-happcore-appcore.md",
    "docs/results/nano-lm/depl-ao.md",
    "docs/results/nano-lm/appcore-known.md",
    "docs/results/nano-lm/appcore-howto.md",
    "docs/results/nano-lm/appcore-longdoc.md",
    "docs/results/nano-lm/wave-ao-hitl.md",
    "docs/results/nano-lm/wave-ao-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ao.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AO_REPORT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "FROZEN",
    "H-GENCORE",
    "H-CTXCORE",
    "H-SMARTCORE",
    "H-FASTCORE",
    "H-APPCORE",
    "AO-HITL-10",
    "FIX",
    "LOOKUP",
    "GENERATE",
    "anti-FP",
    "PROMOTE",
    "not open chat",
    "AF packaged stack",
)


def decide_ao_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AO_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AO report evidence
    WHEN deciding AO-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AO_ID}: {AO_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AO_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AO_HITL_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking dual-arm HITL + FIX log (§3 AO7)
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
        if mid.startswith("H-") or mid == "AO-HITL-10":
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


def render_wave_ao_summary() -> str:
    lines = [
        "# Wave AO — core dual-arm · longer/faster/smarter/apps "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §3 · Paper-lab: "
        "[paper-lab-wave-ao.md](paper-lab-wave-ao.md) · "
        "HITL: [wave-ao-hitl.md](wave-ao-hitl.md) · "
        "Freeze: [ao-freeze.md](ao-freeze.md)  ",
        "> Parent: Wave AN **AN-FREEZE** reopen · Ship claim: "
        "**AF packaged stack** (unchanged)",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + AO_THESIS
        + ".**",
        "",
        "## Stage scoreboard (Cursor ASK→EVAL→FIX dual-arm)",
        "",
        "| # | ID | Lookup mean | Gen mean | Errors | FIX count | Decision | Note |",
        "|---|-----|------------:|---------:|--------|----------:|----------|------|",
    ]
    for row in AO_HITL_SCOREBOARD:
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
            "| LOOKUP labeled ≠ GENERATE | every AO stage dual-arm log |",
            "| Generative arm `wall_ms>0` · `n_new>0` | "
            "GENCORE · CTXCORE · FASTCORE · AO-HITL-10 |",
            "| Cursor scores **completion** (not auto TRUE_HIT→9 as IQ) | "
            "SMARTCORE/APPCORE/HITL gen 9.0 peak spans |",
            "| LOOKUP high score ≠ generative IQ | "
            "LOOKUP 9.0 with peak gen product claim |",
            "| LOOKUP scores are not generative IQ | "
            "dual-arm scoreboard + anti-FP notes |",
            "| Peak gen ≠ open-chat TinyStories IQ | "
            "extractive peak from curated context (GENCORE doctrine) |",
            "| CTXCORE periods ≠ smarter LM | gen 1.0 · L_eff claim only |",
            "| Ablated gen HOLD honesty | "
            "H-GENCORE ablated 4.0 · peak_only_lift |",
            "",
            "## Honest product claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| Longer usable ctx (AO) | **H-CTXCORE** PROMOTE; "
            "L_eff **253105** > CTXEDGE |",
            "| Smarter cite+gen (AO) | **H-SMARTCORE** PROMOTE — "
            "gen **9.0** ≥ 5 (GENCORE peak) |",
            "| True-gen ablation | **H-GENCORE** HOLD — ablated gen **4.0** |",
            "| Faster generative ask | **H-FASTCORE** PROMOTE — "
            "warm **0.06** < FASTEDGE **0.10** |",
            "| Apps expose arms | **H-APPCORE** PROMOTE — "
            "DEPL-AO dual-arm · SERVE gen 9.0 |",
            "| ≤5M hard law | **H-CAPCHECK** SKIPPED — keep ≤5M |",
            "| Final dual-arm HITL | **AO-HITL-10** LOOKUP **9.0** · "
            "GEN **9.0** · **PROMOTE** |",
            "| Ship claim | **AF packaged stack** — not open chat |",
            "| “Open chat LM ≤5M” | **False** — not open chat |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:ao:report",
            "npm run nano:ao:session",
            "npm run nano:gencore",
            "npm run nano:ctxcore",
            "npm run nano:smartcore",
            "npm run nano:fastcore",
            "npm run nano:appcore",
            "npm run nano:ao:hitl",
            "npm run nano:ao:freeze",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave AP without "
            "lab-book reopen · claim open chat · sell CTXCORE periods as IQ · "
            "sell GENCORE peak as open-chat IQ.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_ao() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AO (core dual-arm · longer/faster/smarter/apps)",
            "",
            "> Companion to [wave-ao-summary.md](wave-ao-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · Final HITL: "
            "[wave-ao-hitl.md](wave-ao-hitl.md) · "
            "Freeze: [ao-freeze.md](ao-freeze.md) · "
            "Parent: [an-freeze.md](an-freeze.md) · "
            "Ship: **AF packaged stack**",
            "",
            "## Question",
            "",
            "After AN froze edge dual-arm, can a **fourteenth** held-out 10 "
            "push **core context**, **core speed**, **core cite/gen**, "
            "and **apps** beyond AN without false-positive “open chat” "
            "claims — and without raising ≤5M?",
            "",
            "## Answer",
            "",
            "**Yes — as grounded peak product systems; not as open chat.** "
            "Wave AO promotes CTXCORE, SMARTCORE, FASTCORE, APPCORE, and "
            "final AO-HITL-10 with gen≥5 via GENCORE extractive peak. "
            "H-GENCORE HOLDs on ablated true-gen (4.0). CAPCHECK skipped "
            "(≤5M stays). Ship claim remains the **AF packaged stack**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-GENCORE | Ablated gen 4.0 → HOLD; peak_only_lift labeled |",
            "| H-CAPCHECK | Skipped; keep ≤5M |",
            "| H-CTXCORE | Dodeca-doc L_eff 253105 > CTXEDGE → PROMOTE |",
            "| H-SMARTCORE | Dodeca-hop cite 10/10; gen 9.0 → PROMOTE |",
            "| H-FASTCORE | Warm wall 0.06 < FASTEDGE 0.10 → PROMOTE |",
            "| H-APPCORE | Apps expose LOOKUP\\|GENERATE + DEPL-AO → PROMOTE |",
            "| AO-HITL-10 | Final L=9.0 G=9.0 → PROMOTE; ship=AF |",
            "| AO-FREEZE | Locked; no Wave AP invent without reopen |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP mean 9.0 must never be sold as generative IQ. Peak "
            "gen **9.0** is extractive from curated context — not "
            "open-chat TinyStories. CTXCORE gen **1.0** periods are "
            "L_eff-only. GENCORE ablated **4.0** remains the honest "
            "true-gen bar. Telemetry (`mode`, `wall_ms`, `n_new`) is "
            "mandatory.",
            "",
            "## Takeaway one-liner",
            "",
            "**AO = core dual-arm under anti-FP; gen≥5 via GENCORE peak; "
            "ablated HOLD honest; ship stays AF packaged stack — not "
            "open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-ao-summary.md](wave-ao-summary.md) · "
            "[wave-ao-hitl.md](wave-ao-hitl.md) · "
            "[ao-freeze.md](ao-freeze.md) · "
            "[wave-an-summary.md](wave-an-summary.md)  ",
            "- Formals: GENCORE · CTXCORE · SMARTCORE · FASTCORE · "
            "APPCORE  ",
            "- Deploy: [depl-ao.md](depl-ao.md) · Apps: "
            "[appcore-known.md](appcore-known.md) · "
            "[appcore-howto.md](appcore-howto.md) · "
            "[appcore-longdoc.md](appcore-longdoc.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
