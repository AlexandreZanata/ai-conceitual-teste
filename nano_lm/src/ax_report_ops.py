"""Wave AX REPORT: public closeout (Caminho A harden + honest NANOGEN8 DEFER)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ax_session_ops import AX0_SHIP_LOCK

__all__ = [
    "AX_ID",
    "AX_THESIS",
    "AX_EVIDENCE",
    "AX_REPORT_MARKERS",
    "AX_SCOREBOARD",
    "SHIP_CLAIM",
    "decide_ax_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "realeval_section_ok",
    "render_wave_ax_summary",
    "render_paper_lab_wave_ax",
]

AX_ID = "AX-REPORT"
SHIP_CLAIM = AX0_SHIP_LOCK
AX_THESIS = (
    "Wave AX dual track: H-PRODNAT·H-SHIPUX PROMOTE (Caminho A · "
    "hard-natural · modes+content · DECODE law); H-NANOGEN8 DEFER "
    "(gen stance defer · CAPCHECK closed · NANOGEN6·7 HOLD cited · "
    "not TAC rename); AX-REAL-EVAL PROMOTE (live battery 8/8 · gen locked); "
    "ship " + SHIP_CLAIM
)

AX_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AX0",
        "id": "SESSION",
        "metric": "packs frozen",
        "decision": "PROMOTE",
        "note": "hard-natural · PRODNAT · gen stance defer · true-eval",
    },
    {
        "stage": "AX1",
        "id": "H-PRODNAT",
        "metric": "hard-natural Caminho A bars",
        "decision": "PROMOTE",
        "note": "hard-natural 1.0/18 · FH 0 · p50/p99 · KB · DECODE law",
    },
    {
        "stage": "AX2",
        "id": "H-SHIPUX",
        "metric": "modes+content honest",
        "decision": "PROMOTE",
        "note": "LOOKUP·PEAK·DECODE·ABSTAIN · hard-natural LOOKUP · no unlabeled",
    },
    {
        "stage": "AX3",
        "id": "H-NANOGEN8",
        "metric": "gen stance defer",
        "decision": "DEFER",
        "note": "CAPCHECK closed · no real new method · NANOGEN6·7 HOLD · not rename",
    },
    {
        "stage": "AX4",
        "id": "AX-REAL-EVAL",
        "metric": "live ask battery 8/8",
        "decision": "PROMOTE",
        "note": "product pass · gen locked (AX3 DEFER) · anti-FP · prod=eval",
    },
    {
        "stage": "AX5",
        "id": "AX-REPORT",
        "metric": "summary + paper-lab",
        "decision": "PROMOTE",
        "note": "docs + anti-FP · NANOGEN6/7 HOLD cited · real-eval section",
    },
    {
        "stage": "AX6",
        "id": "AX-FREEZE",
        "metric": "lock outcomes",
        "decision": "PROMOTE",
        "note": "COMPLETE+FROZEN · no Wave AY invent",
    },
)

AX_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ax-session.md",
    "docs/results/nano-lm/formal-hprodnat-prodnat.md",
    "docs/results/nano-lm/formal-hshipux-shipux.md",
    "docs/results/nano-lm/shipux-demo.md",
    "docs/results/nano-lm/formal-hnanogen8-nanogen8.md",
    "docs/results/nano-lm/wave-ax-real-eval.md",
    "docs/results/nano-lm/wave-ax-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ax.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AX_REPORT_MARKERS: tuple[str, ...] = (
    "H-PRODNAT",
    "H-SHIPUX",
    "H-NANOGEN8",
    "H-NANOGEN6",
    "H-NANOGEN7",
    "AX-REAL-EVAL",
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
    "anti-FP",
    "PROMOTE",
    "DEFER",
    "HOLD",
    "true_continue",
    "span-fallback",
    "hard-natural",
    "snippet-prefix",
    "gibberish-tail",
    "STRICT",
    "not unlabeled open chat",
    "AF packaged stack",
    "product layer",
    "SAFE",
    "NANOGEN6",
    "NANOGEN7",
)


def decide_ax_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AX_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AX report evidence
    WHEN deciding AX-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AX_ID}: {AX_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AX_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AX_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking AX scoreboard
    THEN every stage id appears with Metric column.
    """
    body = str(text)
    if "Metric" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid.startswith("AX-"):
            if f"**{mid}**" not in body:
                return False
    return True


def antifp_section_ok(text: str) -> bool:
    """
    GIVEN summary body
    WHEN checking anti-FP evidence block
    THEN require modes + LOOKUP≠IQ + NANOGEN6/7/8 honesty.
    """
    body = str(text)
    need = (
        "anti-FP",
        "LOOKUP",
        "PEAK",
        "DECODE",
        "ABSTAIN",
        "wall_ms",
        "n_new",
        "not generative IQ",
        "H-NANOGEN8",
        "H-NANOGEN6",
        "H-NANOGEN7",
        "span-fallback",
        "true_continue",
        "hard-natural",
        "SAFE",
        "unlabeled open chat",
    )
    return all(m in body for m in need)


def realeval_section_ok(text: str) -> bool:
    """Require explicit real-eval section with battery + gen lock honesty."""
    body = str(text).lower()
    return (
        "real-eval" in body
        and "battery" in body
        and "nanogen8" in body
        and "prodnat" in body
        and "shipux" in body
        and "span-fallback" in body
        and "defer" in body
        and "nanogen6" in body
        and "nanogen7" in body
    )


def render_wave_ax_summary() -> str:
    lines = [
        "# Wave AX — Caminho A harden + Nano gen-defer honesty "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §5 · Paper-lab: "
        "[paper-lab-wave-ax.md](paper-lab-wave-ax.md) · "
        "Real-eval: [wave-ax-real-eval.md](wave-ax-real-eval.md) · "
        "Freeze: [ax-freeze.md](ax-freeze.md) · "
        "[formal-haxfreeze-ax-freeze.md](formal-haxfreeze-ax-freeze.md)  ",
        "> Parent: Wave AW **AW-FREEZE** · Ship claim: "
        f"**{SHIP_CLAIM}**",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + AX_THESIS
        + ".**",
        "",
        "## Stage scoreboard (product + generative)",
        "",
        "| # | ID | Metric | Decision | Note |",
        "|---|-----|--------|----------|------|",
    ]
    for row in AX_SCOREBOARD:
        lines.append(
            f"| {row['stage']} | **{row['id']}** | {row['metric']} | "
            f"**{row['decision']}** | {row['note']} |"
        )
    lines.extend(
        [
            "",
            "## Anti-FP evidence (mandatory)",
            "",
            "| Rule | Evidence |",
            "|------|----------|",
            "| LOOKUP labeled — not generative IQ | "
            "H-SHIPUX · AX-REAL-EVAL known_lookup · WRAP_LOOKUP |",
            "| PEAK extractive ≠ open-chat | "
            "H-SHIPUX PEAK · H-PRODNAT usable span |",
            "| DECODE arm `wall_ms>0` · `n_new>0` | "
            "H-SHIPUX WRAP_DECODE · AX-ASK-05/08 |",
            "| DECODE gibberish ≠ content_ok | "
            "H-PRODNAT · H-SHIPUX junk→ABSTAIN · AX-ASK-08 |",
            "| Hard-natural ≠ pack-para | "
            "H-PRODNAT hard-natural 1.0/18 · AX-ASK-07 LOOKUP |",
            "| ABSTAIN refuse junk / OOD / near-miss | "
            "AX-REAL-EVAL OOD·junk·SegWit/BIP-39 refuse · FH 0 |",
            "| SAFE ≠ answer quality | "
            "H-PRODNAT cites SAFE≠quality |",
            "| True-gen DEFER honesty | "
            "**H-NANOGEN8** DEFER · **H-NANOGEN6** HOLD · "
            "**H-NANOGEN7** HOLD · true_continue unmet · "
            "span-fallback ≠ gen IQ · not unlabeled open chat |",
            "| Modes always visible + content bars | "
            "**H-SHIPUX** LOOKUP·PEAK·DECODE·ABSTAIN |",
            "| Generative claim gated | "
            "AX-REAL-EVAL · unlock only if AX3 PROMOTE |",
            "| Telemetry keys | `mode` · `wall_ms` · `n_new` · "
            "`product_mode` |",
            "",
            "## Honest claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| Caminho A harden | **H-PRODNAT** PROMOTE |",
            "| Mode+content ask/apps/ship | **H-SHIPUX** PROMOTE |",
            "| North-star generative | **H-NANOGEN8** DEFER — "
            "stance defer · CAPCHECK closed · "
            "NANOGEN6·7 HOLD stand · not TAC rename |",
            "| Parent gen HOLDs cited | **H-NANOGEN6** HOLD · "
            "**H-NANOGEN7** HOLD |",
            "| Final real eval | **AX-REAL-EVAL** PROMOTE — "
            "battery **8/8** · gen locked |",
            "| Ship claim | **" + SHIP_CLAIM + "** |",
            "| “Unlabeled open chat / GPT-class ≤5M” | **False** |",
            "| “TAC / true-continue unlocked” | **False** (AX3 DEFER) |",
            "",
            "## Real-eval section",
            "",
            "| Arm | What was measured | Outcome |",
            "|-----|-------------------|---------|",
            "| Product (PRODNAT) | hard-natural · FH · latency · KB · "
            "DECODE content | **PROMOTE** |",
            "| Product (SHIPUX) | ask · apps · ship/demo modes+content | "
            "**PROMOTE** |",
            "| Generative (NANOGEN8) | defer stance · CAPCHECK closed · "
            "cite NANOGEN6·7 HOLD · not rename | **DEFER** |",
            "| Live ask battery | LOOKUP·PEAK·DECODE·ABSTAIN + "
            "hard-natural · near-miss · DECODE junk→ABSTAIN | "
            "**PASS** 8/8 |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:ax:report",
            "npm run nano:ax:session",
            "npm run nano:prodnat",
            "npm run nano:shipux",
            "npm run nano:nanogen8",
            "npm run nano:ax:real-eval",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave AY without "
            "lab-book reopen · sell PEAK/bank-grounded as unlabeled open-chat · "
            "sell SAFE mean as IQ · sell span-fallback as true-continue · "
            "gold-substring PROMOTE · truncate-to-span as gen IQ · "
            "NANOGEN8 = NANOGEN7+rename · "
            "CTX/SMART/FAST/APP letter clones · rewrite AW/AV/AU/AT/AS/AR/AQ locks.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_ax() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AX (Caminho A harden + Nano gen-defer)",
            "",
            "> Companion to [wave-ax-summary.md](wave-ax-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · "
            "Real-eval: [wave-ax-real-eval.md](wave-ax-real-eval.md) · "
            "Freeze: [ax-freeze.md](ax-freeze.md) · "
            "[formal-haxfreeze-ax-freeze.md](formal-haxfreeze-ax-freeze.md) · "
            "Parent: [aw-freeze.md](aw-freeze.md) · "
            f"Ship: **{SHIP_CLAIM}**",
            "",
            "## Question",
            "",
            "After AW froze Caminho A keep + honest NANOGEN7 HOLD "
            "(TAC true_continue unmet), can Wave AX **close hard-natural "
            "product debt** (PRODNAT + SHIPUX) **and** clear a **real new "
            "method** generative lift under ≤5M **without** unlabeled "
            "open-chat / GPT-class / NANOGEN8=NANOGEN7+rename?",
            "",
            "## Answer",
            "",
            "**Yes for Caminho A harden; honest DEFER for generative.** "
            "H-PRODNAT · H-SHIPUX PROMOTE. **H-NANOGEN8 DEFER** "
            "(AX0 stance=defer; CAPCHECK closed; no real new method; "
            "NANOGEN6·7 HOLD cited; not a TAC rename). "
            "AX-REAL-EVAL PROMOTE (live battery 8/8; gen unlock locked). "
            f"Ship claim stays STRICT archive: **{SHIP_CLAIM}**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-PRODNAT | Hard-natural · FH0 · DECODE content → PROMOTE |",
            "| H-SHIPUX | Modes+content · DECODE usable/ABSTAIN → PROMOTE |",
            "| H-NANOGEN8 | Gen stance defer · NANOGEN6·7 HOLD cited → DEFER |",
            "| AX-REAL-EVAL | Live battery 8/8 · gen locked → PROMOTE |",
            "| AX-REPORT | Summary + paper-lab + anti-FP → PROMOTE |",
            "| AX-FREEZE | Outcomes lock — no Wave AY invent |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP / SHIPUX must never be sold as generative IQ. PEAK and "
            "span-fallback stay product/extractive credit only. Hard-natural "
            "≠ pack/pressure-para coverage. DECODE telemetry (`wall_ms`, "
            "`n_new`) is mandatory but insufficient for content_ok. "
            "SAFE≠quality. Gold-substring / gibberish-tail / "
            "truncate-to-span ≠ generative PROMOTE. **H-NANOGEN8 DEFER** "
            "plus cited **H-NANOGEN6** / **H-NANOGEN7 HOLD** keep "
            "true-continue / mini-AGI language locked — ship remains "
            "STRICT ablated DECODE archive, not unlabeled open chat.",
            "",
            "## Takeaway one-liner",
            "",
            "**AX = Caminho A hard-natural harden + gen DEFERs honestly "
            "(NANOGEN6·7 HOLD stand; not TAC rename); ship AF+AQ+AS trust + "
            "STRICT snippet-prefix DECODE — not unlabeled open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-ax-summary.md](wave-ax-summary.md) · "
            "[wave-ax-real-eval.md](wave-ax-real-eval.md) · "
            "[wave-ax-session.md](wave-ax-session.md) · "
            "[aw-freeze.md](aw-freeze.md)  ",
            "- Formals: PRODNAT · SHIPUX · NANOGEN8  ",
            "- Demo: [shipux-demo.md](shipux-demo.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
