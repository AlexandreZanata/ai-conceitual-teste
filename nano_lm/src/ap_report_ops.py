"""Wave AP REPORT: public closeout (dual-arm HITL + FIX + anti-FP)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "AP_ID",
    "AP_THESIS",
    "AP_EVIDENCE",
    "AP_REPORT_MARKERS",
    "AP_HITL_SCOREBOARD",
    "decide_ap_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "render_wave_ap_summary",
    "render_paper_lab_wave_ap",
]

AP_ID = "AP-REPORT"
AP_THESIS = (
    "Wave AP base dual-arm on 15th held-out pack: GENBASE HOLD · "
    "CTXBASE·SMARTBASE·FASTBASE·APPBASE·AP-HITL all PROMOTE; "
    "CAPCHECK skipped; gen≥5 via GENBASE peak; L_eff↑ · wall↓ · "
    "apps+DEPL; ship claim remains AF packaged stack — not open chat LM"
)

# Frozen dual-arm Cursor ASK→EVAL→FIX closeout (§3 / SESSION).
AP_HITL_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AP0",
        "id": "SESSION",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "freeze 10 held-out asks ≠ AB…AO",
    },
    {
        "stage": "AP1",
        "id": "H-GENBASE",
        "lookup_mean": 9.0,
        "gen_mean": 4.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "HOLD",
        "note": "ablated gen 4.0; peak_only_lift; anti-FP",
    },
    {
        "stage": "AP1b",
        "id": "H-CAPCHECK",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "SKIPPED",
        "note": "size hypothesis unused; ≤5M stays",
    },
    {
        "stage": "AP2",
        "id": "H-CTXBASE",
        "lookup_mean": 9.0,
        "gen_mean": 1.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "trideca-doc L_eff 274198 > CTXCORE",
    },
    {
        "stage": "AP3",
        "id": "H-SMARTBASE",
        "lookup_mean": 9.0,
        "gen_mean": 9.0,
        "errors": "0/10",
        "fix": 1,
        "decision": "PROMOTE",
        "note": "trideca-hop cite; FIX `..` ≠ period",
    },
    {
        "stage": "AP4",
        "id": "H-FASTBASE",
        "lookup_mean": 9.0,
        "gen_mean": 7.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "peak-fast warm 0.056 < FASTCORE 0.06",
    },
    {
        "stage": "AP5",
        "id": "H-APPBASE",
        "lookup_mean": 8.33,
        "gen_mean": 9.0,
        "errors": "0/SERVE",
        "fix": 1,
        "decision": "PROMOTE",
        "note": "expose LOOKUP|GENERATE + DEPL-AP",
    },
    {
        "stage": "AP6",
        "id": "AP-HITL-10",
        "lookup_mean": 9.0,
        "gen_mean": 9.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "final dual-arm; peak product; ship=AF",
    },
    {
        "stage": "AP7",
        "id": "AP-REPORT",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "public summary + paper-lab + anti-FP",
    },
    {
        "stage": "AP8",
        "id": "AP-FREEZE",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "lock; no Wave AQ invent",
    },
)

AP_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ap-session.md",
    "docs/results/nano-lm/formal-hgenbase-genbase.md",
    "docs/results/nano-lm/formal-hctxbase-ctxbase.md",
    "docs/results/nano-lm/formal-hsmartbase-smartbase.md",
    "docs/results/nano-lm/formal-hfastbase-fastbase.md",
    "docs/results/nano-lm/formal-happbase-appbase.md",
    "docs/results/nano-lm/depl-ap.md",
    "docs/results/nano-lm/appbase-known.md",
    "docs/results/nano-lm/appbase-howto.md",
    "docs/results/nano-lm/appbase-longdoc.md",
    "docs/results/nano-lm/wave-ap-hitl.md",
    "docs/results/nano-lm/wave-ap-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ap.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AP_REPORT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "FROZEN",
    "H-GENBASE",
    "H-CTXBASE",
    "H-SMARTBASE",
    "H-FASTBASE",
    "H-APPBASE",
    "AP-HITL-10",
    "FIX",
    "LOOKUP",
    "GENERATE",
    "anti-FP",
    "PROMOTE",
    "not open chat",
    "AF packaged stack",
)


def decide_ap_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AP_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AP report evidence
    WHEN deciding AP-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AP_ID}: {AP_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AP_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AP_HITL_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking dual-arm HITL + FIX log (§3 AP7)
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
        if mid.startswith("H-") or mid == "AP-HITL-10":
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


def render_wave_ap_summary() -> str:
    lines = [
        "# Wave AP — base dual-arm · longer/faster/smarter/apps "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §3 · Paper-lab: "
        "[paper-lab-wave-ap.md](paper-lab-wave-ap.md) · "
        "HITL: [wave-ap-hitl.md](wave-ap-hitl.md) · "
        "Freeze: [ap-freeze.md](ap-freeze.md)  ",
        "> Parent: Wave AO **AO-FREEZE** reopen · Ship claim: "
        "**AF packaged stack** (unchanged)",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + AP_THESIS
        + ".**",
        "",
        "## Stage scoreboard (Cursor ASK→EVAL→FIX dual-arm)",
        "",
        "| # | ID | Lookup mean | Gen mean | Errors | FIX count | Decision | Note |",
        "|---|-----|------------:|---------:|--------|----------:|----------|------|",
    ]
    for row in AP_HITL_SCOREBOARD:
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
            "| LOOKUP labeled ≠ GENERATE | every AP stage dual-arm log |",
            "| Generative arm `wall_ms>0` · `n_new>0` | "
            "GENBASE · CTXBASE · FASTBASE · AP-HITL-10 |",
            "| Cursor scores **completion** (not auto TRUE_HIT→9 as IQ) | "
            "SMARTBASE/APPBASE/HITL gen 9.0 peak spans |",
            "| LOOKUP high score ≠ generative IQ | "
            "LOOKUP 9.0 with peak gen product claim |",
            "| LOOKUP scores are not generative IQ | "
            "dual-arm scoreboard + anti-FP notes |",
            "| Peak gen ≠ open-chat TinyStories IQ | "
            "extractive peak from curated context (GENBASE doctrine) |",
            "| CTXBASE periods ≠ smarter LM | gen 1.0 · L_eff claim only |",
            "| Ablated gen HOLD honesty | "
            "H-GENBASE ablated 4.0 · peak_only_lift |",
            "",
            "## Honest product claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| Longer usable ctx (AP) | **H-CTXBASE** PROMOTE; "
            "L_eff **274198** > CTXCORE |",
            "| Smarter cite+gen (AP) | **H-SMARTBASE** PROMOTE — "
            "gen **9.0** ≥ 5 (GENBASE peak) |",
            "| True-gen ablation | **H-GENBASE** HOLD — ablated gen **4.0** |",
            "| Faster generative ask | **H-FASTBASE** PROMOTE — "
            "warm **0.056** < FASTCORE **0.06** |",
            "| Apps expose arms | **H-APPBASE** PROMOTE — "
            "DEPL-AP dual-arm · SERVE gen 9.0 |",
            "| ≤5M hard law | **H-CAPCHECK** SKIPPED — keep ≤5M |",
            "| Final dual-arm HITL | **AP-HITL-10** LOOKUP **9.0** · "
            "GEN **9.0** · **PROMOTE** |",
            "| Ship claim | **AF packaged stack** — not open chat |",
            "| “Open chat LM ≤5M” | **False** — not open chat |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:ap:report",
            "npm run nano:ap:session",
            "npm run nano:genbase",
            "npm run nano:ctxbase",
            "npm run nano:smartbase",
            "npm run nano:fastbase",
            "npm run nano:appbase",
            "npm run nano:ap:hitl",
            "npm run nano:ap:freeze",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave AQ without "
            "lab-book reopen · claim open chat · sell CTXBASE periods as IQ · "
            "sell GENBASE peak as open-chat IQ.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_ap() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AP (base dual-arm · longer/faster/smarter/apps)",
            "",
            "> Companion to [wave-ap-summary.md](wave-ap-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · Final HITL: "
            "[wave-ap-hitl.md](wave-ap-hitl.md) · "
            "Freeze: [ap-freeze.md](ap-freeze.md) · "
            "Parent: [ao-freeze.md](ao-freeze.md) · "
            "Ship: **AF packaged stack**",
            "",
            "## Question",
            "",
            "After AO froze core dual-arm, can a **fifteenth** held-out 10 "
            "push **base context**, **base speed**, **base cite/gen**, "
            "and **apps** beyond AO without false-positive “open chat” "
            "claims — and without raising ≤5M?",
            "",
            "## Answer",
            "",
            "**Yes — as grounded peak product systems; not as open chat.** "
            "Wave AP promotes CTXBASE, SMARTBASE, FASTBASE, APPBASE, and "
            "final AP-HITL-10 with gen≥5 via GENBASE extractive peak. "
            "H-GENBASE HOLDs on ablated true-gen (4.0). CAPCHECK skipped "
            "(≤5M stays). Ship claim remains the **AF packaged stack**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-GENBASE | Ablated gen 4.0 → HOLD; peak_only_lift labeled |",
            "| H-CAPCHECK | Skipped; keep ≤5M |",
            "| H-CTXBASE | Trideca-doc L_eff 274198 > CTXCORE → PROMOTE |",
            "| H-SMARTBASE | Trideca-hop cite; gen 9.0; FIX `..` → PROMOTE |",
            "| H-FASTBASE | Warm wall 0.056 < FASTCORE 0.06 → PROMOTE |",
            "| H-APPBASE | Apps expose LOOKUP\\|GENERATE + DEPL-AP → PROMOTE |",
            "| AP-HITL-10 | Final L=9.0 G=9.0 → PROMOTE; ship=AF |",
            "| AP-FREEZE | Locked; no Wave AQ invent without reopen |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP mean 9.0 must never be sold as generative IQ. Peak "
            "gen **9.0** is extractive from curated context — not "
            "open-chat TinyStories. CTXBASE gen **1.0** periods are "
            "L_eff-only. GENBASE ablated **4.0** remains the honest "
            "true-gen bar. Telemetry (`mode`, `wall_ms`, `n_new`) is "
            "mandatory.",
            "",
            "## Takeaway one-liner",
            "",
            "**AP = base dual-arm under anti-FP; gen≥5 via GENBASE peak; "
            "ablated HOLD honest; ship stays AF packaged stack — not "
            "open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-ap-summary.md](wave-ap-summary.md) · "
            "[wave-ap-hitl.md](wave-ap-hitl.md) · "
            "[ap-freeze.md](ap-freeze.md) · "
            "[wave-ao-summary.md](wave-ao-summary.md)  ",
            "- Formals: GENBASE · CTXBASE · SMARTBASE · FASTBASE · "
            "APPBASE  ",
            "- Deploy: [depl-ap.md](depl-ap.md) · Apps: "
            "[appbase-known.md](appbase-known.md) · "
            "[appbase-howto.md](appbase-howto.md) · "
            "[appbase-longdoc.md](appbase-longdoc.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
