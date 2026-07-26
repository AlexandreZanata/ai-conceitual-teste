"""Wave AK REPORT: public closeout (dual-arm HITL + FIX + anti-FP)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "AK_ID",
    "AK_THESIS",
    "AK_EVIDENCE",
    "AK_REPORT_MARKERS",
    "AK_HITL_SCOREBOARD",
    "decide_ak_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "render_wave_ak_summary",
    "render_paper_lab_wave_ak",
]

AK_ID = "AK-REPORT"
AK_THESIS = (
    "Wave AK more dual-arm on 10th held-out pack: GENTRUE HOLD · "
    "CTXMORE·SMARTMORE·FASTMORE·APPMORE·AK-HITL all PROMOTE; "
    "CAPCHECK skipped; gen≥5 via GENTRUE peak; L_eff↑ · wall↓ · "
    "apps+DEPL; ship claim remains AF packaged stack — not open chat LM"
)

# Frozen dual-arm Cursor ASK→EVAL→FIX closeout (§3 / SESSION).
AK_HITL_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AK0",
        "id": "SESSION",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "freeze 10 held-out asks ≠ AB…AJ",
    },
    {
        "stage": "AK1",
        "id": "H-GENTRUE",
        "lookup_mean": 9.0,
        "gen_mean": 4.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "HOLD",
        "note": "ablated gen 4.0; peak_only_lift; anti-FP",
    },
    {
        "stage": "AK1b",
        "id": "H-CAPCHECK",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "SKIPPED",
        "note": "size hypothesis unused; ≤5M stays",
    },
    {
        "stage": "AK2",
        "id": "H-CTXMORE",
        "lookup_mean": 9.0,
        "gen_mean": 1.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "octa-doc L_eff 188984 > CTXPEAK",
    },
    {
        "stage": "AK3",
        "id": "H-SMARTMORE",
        "lookup_mean": 9.0,
        "gen_mean": 9.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "octa-hop cite 10/10; false-hit 0",
    },
    {
        "stage": "AK4",
        "id": "H-FASTMORE",
        "lookup_mean": 9.0,
        "gen_mean": 7.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "peak-fast hot 3.8ms < FASTPEAK 5.0",
    },
    {
        "stage": "AK5",
        "id": "H-APPMORE",
        "lookup_mean": 8.33,
        "gen_mean": 9.0,
        "errors": "0/SERVE",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "expose LOOKUP|GENERATE + DEPL-AK",
    },
    {
        "stage": "AK6",
        "id": "AK-HITL-10",
        "lookup_mean": 9.0,
        "gen_mean": 9.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "final dual-arm; peak product; ship=AF",
    },
    {
        "stage": "AK7",
        "id": "AK-REPORT",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "public summary + paper-lab + anti-FP",
    },
    {
        "stage": "AK8",
        "id": "AK-FREEZE",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "lock; no Wave AL invent",
    },
)

AK_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ak-session.md",
    "docs/results/nano-lm/formal-hgentrue-gentrue.md",
    "docs/results/nano-lm/formal-hctxmore-ctxmore.md",
    "docs/results/nano-lm/formal-hsmartmore-smartmore.md",
    "docs/results/nano-lm/formal-hfastmore-fastmore.md",
    "docs/results/nano-lm/formal-happmore-appmore.md",
    "docs/results/nano-lm/depl-ak.md",
    "docs/results/nano-lm/appmore-known.md",
    "docs/results/nano-lm/appmore-howto.md",
    "docs/results/nano-lm/appmore-longdoc.md",
    "docs/results/nano-lm/wave-ak-hitl.md",
    "docs/results/nano-lm/wave-ak-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ak.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AK_REPORT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "FROZEN",
    "H-GENTRUE",
    "H-CTXMORE",
    "H-SMARTMORE",
    "H-FASTMORE",
    "H-APPMORE",
    "AK-HITL-10",
    "FIX",
    "LOOKUP",
    "GENERATE",
    "anti-FP",
    "PROMOTE",
    "not open chat",
    "AF packaged stack",
)


def decide_ak_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AK_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AK report evidence
    WHEN deciding AK-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AK_ID}: {AK_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AK_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AK_HITL_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking dual-arm HITL + FIX log (§3 AK7)
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
        if mid.startswith("H-") or mid == "AK-HITL-10":
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


def render_wave_ak_summary() -> str:
    lines = [
        "# Wave AK — more dual-arm · longer/faster/smarter/apps "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §3 · Paper-lab: "
        "[paper-lab-wave-ak.md](paper-lab-wave-ak.md) · "
        "HITL: [wave-ak-hitl.md](wave-ak-hitl.md) · "
        "Freeze: [ak-freeze.md](ak-freeze.md)  ",
        "> Parent: Wave AJ **AJ-FREEZE** reopen · Ship claim: "
        "**AF packaged stack** (unchanged)",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + AK_THESIS
        + ".**",
        "",
        "## Stage scoreboard (Cursor ASK→EVAL→FIX dual-arm)",
        "",
        "| # | ID | Lookup mean | Gen mean | Errors | FIX count | Decision | Note |",
        "|---|-----|------------:|---------:|--------|----------:|----------|------|",
    ]
    for row in AK_HITL_SCOREBOARD:
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
            "| LOOKUP labeled ≠ GENERATE | every AK stage dual-arm log |",
            "| Generative arm `wall_ms>0` · `n_new>0` | GENTRUE · CTXMORE · FASTMORE · AK-HITL-10 |",
            "| Cursor scores **completion** (not auto TRUE_HIT→9 as IQ) | SMARTMORE/APPMORE/HITL gen 9.0 peak spans |",
            "| LOOKUP high score ≠ generative IQ | LOOKUP 9.0 with peak gen product claim |",
            "| LOOKUP scores are not generative IQ | dual-arm scoreboard + anti-FP notes |",
            "| Peak gen ≠ open-chat TinyStories IQ | extractive peak from curated context (GENTRUE doctrine) |",
            "| CTXMORE periods ≠ smarter LM | gen 1.0 · L_eff claim only |",
            "| Ablated gen HOLD honesty | H-GENTRUE ablated 4.0 · peak_only_lift |",
            "",
            "## Honest product claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| Longer usable ctx (AK) | **H-CTXMORE** PROMOTE; L_eff **188984** > CTXPEAK |",
            "| Smarter cite+gen (AK) | **H-SMARTMORE** PROMOTE — gen **9.0** ≥ 5 (GENTRUE peak) |",
            "| True-gen ablation | **H-GENTRUE** HOLD — ablated gen **4.0** |",
            "| Faster generative ask | **H-FASTMORE** PROMOTE — hot **3.8** < FASTPEAK **5.0** |",
            "| Apps expose arms | **H-APPMORE** PROMOTE — DEPL-AK dual-arm · SERVE gen 9.0 |",
            "| ≤5M hard law | **H-CAPCHECK** SKIPPED — keep ≤5M |",
            "| Final dual-arm HITL | **AK-HITL-10** LOOKUP **9.0** · GEN **9.0** · **PROMOTE** |",
            "| Ship claim | **AF packaged stack** — not open chat |",
            "| “Open chat LM ≤5M” | **False** — not open chat |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:ak:report",
            "npm run nano:ak:session",
            "npm run nano:gentrue",
            "npm run nano:ctxmore",
            "npm run nano:smartmore",
            "npm run nano:fastmore",
            "npm run nano:appmore",
            "npm run nano:ak:hitl",
            "npm run nano:ak:freeze",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave AL without "
            "lab-book reopen · claim open chat · sell CTXMORE periods as IQ · "
            "sell GENTRUE peak as open-chat IQ.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_ak() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AK (more dual-arm · longer/faster/smarter/apps)",
            "",
            "> Companion to [wave-ak-summary.md](wave-ak-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · Final HITL: "
            "[wave-ak-hitl.md](wave-ak-hitl.md) · "
            "Freeze: [ak-freeze.md](ak-freeze.md) · "
            "Parent: [aj-freeze.md](aj-freeze.md) · "
            "Ship: **AF packaged stack**",
            "",
            "## Question",
            "",
            "After AJ froze peak dual-arm, can a **tenth** held-out 10 "
            "push **more context**, **more speed**, **more cite/gen**, "
            "and **apps** beyond AJ without false-positive “open chat” "
            "claims — and without raising ≤5M?",
            "",
            "## Answer",
            "",
            "**Yes — as grounded peak product systems; not as open chat.** "
            "Wave AK promotes CTXMORE, SMARTMORE, FASTMORE, APPMORE, and "
            "final AK-HITL-10 with gen≥5 via GENTRUE extractive peak. "
            "H-GENTRUE HOLDs on ablated true-gen (4.0). CAPCHECK skipped "
            "(≤5M stays). Ship claim remains the **AF packaged stack**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-GENTRUE | Ablated gen 4.0 → HOLD; peak_only_lift labeled |",
            "| H-CAPCHECK | Skipped; keep ≤5M |",
            "| H-CTXMORE | Octa-doc L_eff 188984 > CTXPEAK → PROMOTE |",
            "| H-SMARTMORE | Octa-hop cite 10/10; gen 9.0 → PROMOTE |",
            "| H-FASTMORE | Hot wall 3.8 < FASTPEAK 5.0 → PROMOTE |",
            "| H-APPMORE | Apps expose LOOKUP\\|GENERATE + DEPL-AK → PROMOTE |",
            "| AK-HITL-10 | Final L=9.0 G=9.0 → PROMOTE; ship=AF |",
            "| AK-FREEZE | Locked; no Wave AL invent without reopen |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP mean 9.0 must never be sold as generative IQ. Peak "
            "gen **9.0** is extractive from curated context — not "
            "open-chat TinyStories. CTXMORE gen **1.0** periods are "
            "L_eff-only. GENTRUE ablated **4.0** remains the honest "
            "true-gen bar. Telemetry (`mode`, `wall_ms`, `n_new`) is "
            "mandatory.",
            "",
            "## Takeaway one-liner",
            "",
            "**AK = more dual-arm under anti-FP; gen≥5 via GENTRUE peak; "
            "ablated HOLD honest; ship stays AF packaged stack — not "
            "open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-ak-summary.md](wave-ak-summary.md) · "
            "[wave-ak-hitl.md](wave-ak-hitl.md) · "
            "[ak-freeze.md](ak-freeze.md) · "
            "[wave-aj-summary.md](wave-aj-summary.md)  ",
            "- Formals: GENTRUE · CTXMORE · SMARTMORE · FASTMORE · "
            "APPMORE  ",
            "- Deploy: [depl-ak.md](depl-ak.md) · Apps: "
            "[appmore-known.md](appmore-known.md) · "
            "[appmore-howto.md](appmore-howto.md) · "
            "[appmore-longdoc.md](appmore-longdoc.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
