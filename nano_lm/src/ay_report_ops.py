"""Wave AY REPORT: public closeout (intent harden + honest NANOGEN9 DEFER)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ay_session_ops import AY0_SHIP_LOCK

__all__ = [
    "AY_ID",
    "AY_THESIS",
    "AY_EVIDENCE",
    "AY_REPORT_MARKERS",
    "AY_SCOREBOARD",
    "SHIP_CLAIM",
    "decide_ay_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "realeval_section_ok",
    "render_wave_ay_summary",
    "render_paper_lab_wave_ay",
]

AY_ID = "AY-REPORT"
SHIP_CLAIM = AY0_SHIP_LOCK
AY_THESIS = (
    "Wave AY dual track: H-PRODINT·H-SHIPAY PROMOTE (Caminho A · "
    "intent FH 0 · hard-natural hold · modes+content · DECODE law); "
    "H-NANOGEN9 DEFER (gen stance defer · CAPCHECK closed · "
    "NANOGEN6·7 HOLD · NANOGEN8 DEFER cited · not NANOGEN8 rename); "
    "AY-REAL-EVAL PROMOTE (live battery 8/8 · intent-FP ABSTAIN · "
    "gen locked); ship " + SHIP_CLAIM
)

AY_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AY0",
        "id": "SESSION",
        "metric": "packs frozen",
        "decision": "PROMOTE",
        "note": "intent-FP · PRODINT · gen stance defer · true-eval",
    },
    {
        "stage": "AY1",
        "id": "H-PRODINT",
        "metric": "intent FH 0 Caminho A bars",
        "decision": "PROMOTE",
        "note": "intent FH 0 · hard-natural hold · p50/p99 · KB · DECODE law",
    },
    {
        "stage": "AY2",
        "id": "H-SHIPAY",
        "metric": "modes+content honest",
        "decision": "PROMOTE",
        "note": "LOOKUP·PEAK·DECODE·ABSTAIN · intent ABSTAIN · no unlabeled",
    },
    {
        "stage": "AY3",
        "id": "H-NANOGEN9",
        "metric": "gen stance defer",
        "decision": "DEFER",
        "note": "CAPCHECK closed · no real new method · NANOGEN6·7 HOLD · NANOGEN8 DEFER · not rename",
    },
    {
        "stage": "AY4",
        "id": "AY-REAL-EVAL",
        "metric": "live ask battery 8/8",
        "decision": "PROMOTE",
        "note": "product pass · intent-FP ABSTAIN · gen locked (AY3 DEFER) · prod=eval",
    },
    {
        "stage": "AY5",
        "id": "AY-REPORT",
        "metric": "summary + paper-lab",
        "decision": "PROMOTE",
        "note": "docs + anti-FP · NANOGEN6/7 HOLD · NANOGEN8 DEFER cited",
    },
    {
        "stage": "AY6",
        "id": "AY-FREEZE",
        "metric": "lock outcomes",
        "decision": "PROMOTE",
        "note": "COMPLETE+FROZEN · no Wave AZ invent",
    },
)

AY_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ay-session.md",
    "docs/results/nano-lm/formal-hprodint-prodint.md",
    "docs/results/nano-lm/formal-hshipay-shipay.md",
    "docs/results/nano-lm/shipay-demo.md",
    "docs/results/nano-lm/formal-hnanogen9-nanogen9.md",
    "docs/results/nano-lm/wave-ay-real-eval.md",
    "docs/results/nano-lm/wave-ay-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ay.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AY_REPORT_MARKERS: tuple[str, ...] = (
    "H-PRODINT",
    "H-SHIPAY",
    "H-NANOGEN9",
    "H-NANOGEN8",
    "H-NANOGEN6",
    "H-NANOGEN7",
    "AY-REAL-EVAL",
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
    "intent",
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
    "NANOGEN8",
)


def decide_ay_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AY_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AY report evidence
    WHEN deciding AY-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AY_ID}: {AY_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AY_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AY_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking AY scoreboard
    THEN every stage id appears with Metric column.
    """
    body = str(text)
    if "Metric" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid.startswith("AY-"):
            if f"**{mid}**" not in body:
                return False
    return True


def antifp_section_ok(text: str) -> bool:
    """
    GIVEN summary body
    WHEN checking anti-FP evidence block
    THEN require modes + LOOKUP≠IQ + intent + NANOGEN6/7/8/9 honesty.
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
        "H-NANOGEN9",
        "H-NANOGEN8",
        "H-NANOGEN6",
        "H-NANOGEN7",
        "span-fallback",
        "true_continue",
        "intent",
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
        and "nanogen9" in body
        and "prodint" in body
        and "shipay" in body
        and "span-fallback" in body
        and "defer" in body
        and "nanogen6" in body
        and "nanogen7" in body
        and "nanogen8" in body
        and "intent" in body
    )


def render_wave_ay_summary() -> str:
    lines = [
        "# Wave AY — intent harden + Nano gen-defer honesty "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §5 · Paper-lab: "
        "[paper-lab-wave-ay.md](paper-lab-wave-ay.md) · "
        "Real-eval: [wave-ay-real-eval.md](wave-ay-real-eval.md) · "
        "Freeze: [ay-freeze.md](ay-freeze.md) · "
        "[formal-hayfreeze-ay-freeze.md](formal-hayfreeze-ay-freeze.md)  ",
        "> Parent: Wave AX **AX-FREEZE** · Ship claim: "
        f"**{SHIP_CLAIM}**",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + AY_THESIS
        + ".**",
        "",
        "## Stage scoreboard (product + generative)",
        "",
        "| # | ID | Metric | Decision | Note |",
        "|---|-----|--------|----------|------|",
    ]
    for row in AY_SCOREBOARD:
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
            "H-SHIPAY · AY-REAL-EVAL known_lookup · WRAP_LOOKUP |",
            "| PEAK extractive ≠ open-chat | "
            "H-SHIPAY PEAK · H-PRODINT usable span |",
            "| DECODE arm `wall_ms>0` · `n_new>0` | "
            "H-SHIPAY WRAP_DECODE · AY-ASK-05 |",
            "| DECODE gibberish ≠ content_ok | "
            "H-PRODINT · H-SHIPAY junk→ABSTAIN · AY-ASK-06 |",
            "| Intent-mismatch LOOKUP = false-hit | "
            "H-PRODINT intent FH 0 · AY-ASK-07 ABSTAIN |",
            "| Hard-natural ≠ pack-para | "
            "H-PRODINT hard-natural hold · AY-ASK-08 LOOKUP |",
            "| ABSTAIN refuse junk / OOD / near-miss / intent | "
            "AY-REAL-EVAL OOD·junk·SegWit/BIP-39·intent refuse · FH 0 |",
            "| SAFE ≠ answer quality | "
            "H-PRODINT cites SAFE≠quality |",
            "| True-gen DEFER honesty | "
            "**H-NANOGEN9** DEFER · **H-NANOGEN8** DEFER · "
            "**H-NANOGEN6** HOLD · **H-NANOGEN7** HOLD · "
            "true_continue unmet · span-fallback ≠ gen IQ · "
            "not unlabeled open chat |",
            "| Modes always visible + content bars | "
            "**H-SHIPAY** LOOKUP·PEAK·DECODE·ABSTAIN |",
            "| Generative claim gated | "
            "AY-REAL-EVAL · unlock only if AY3 PROMOTE |",
            "| Telemetry keys | `mode` · `wall_ms` · `n_new` · "
            "`product_mode` |",
            "",
            "## Honest claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| Caminho A intent harden | **H-PRODINT** PROMOTE |",
            "| Mode+content ask/apps/ship | **H-SHIPAY** PROMOTE |",
            "| North-star generative | **H-NANOGEN9** DEFER — "
            "stance defer · CAPCHECK closed · "
            "NANOGEN6·7 HOLD · NANOGEN8 DEFER stand · not rename |",
            "| Parent gen HOLDs / DEFER cited | **H-NANOGEN6** HOLD · "
            "**H-NANOGEN7** HOLD · **H-NANOGEN8** DEFER |",
            "| Final real eval | **AY-REAL-EVAL** PROMOTE — "
            "battery **8/8** · intent-FP ABSTAIN · gen locked |",
            "| Ship claim | **" + SHIP_CLAIM + "** |",
            "| “Unlabeled open chat / GPT-class ≤5M” | **False** |",
            "| “TAC / true-continue unlocked” | **False** (AY3 DEFER) |",
            "",
            "## Real-eval section",
            "",
            "| Arm | What was measured | Outcome |",
            "|-----|-------------------|---------|",
            "| Product (PRODINT) | intent FH 0 · hard-natural hold · "
            "latency · KB · DECODE content | **PROMOTE** |",
            "| Product (SHIPAY) | ask · apps · ship/demo modes+content · "
            "intent ABSTAIN | **PROMOTE** |",
            "| Generative (NANOGEN9) | defer stance · CAPCHECK closed · "
            "cite NANOGEN6·7 HOLD · NANOGEN8 DEFER · not rename | "
            "**DEFER** |",
            "| Live ask battery | LOOKUP·PEAK·DECODE·ABSTAIN + "
            "intent-FP · hard-natural · near-miss · DECODE junk→ABSTAIN | "
            "**PASS** 8/8 |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:ay:report",
            "npm run nano:ay:session",
            "npm run nano:prodint",
            "npm run nano:shipay",
            "npm run nano:nanogen9",
            "npm run nano:ay:real-eval",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave AZ without "
            "lab-book reopen · sell PEAK/bank-grounded as unlabeled open-chat · "
            "sell SAFE mean as IQ · sell span-fallback as true-continue · "
            "gold-substring PROMOTE · truncate-to-span as gen IQ · "
            "intent-mismatch LOOKUP as success · "
            "NANOGEN9 = NANOGEN8+rename · "
            "CTX/SMART/FAST/APP letter clones · rewrite AX/AW/AV/AU/AT/AS/AR/AQ locks.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_ay() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AY (intent harden + Nano gen-defer)",
            "",
            "> Companion to [wave-ay-summary.md](wave-ay-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · "
            "Real-eval: [wave-ay-real-eval.md](wave-ay-real-eval.md) · "
            "Freeze: [ay-freeze.md](ay-freeze.md) · "
            "[formal-hayfreeze-ay-freeze.md](formal-hayfreeze-ay-freeze.md) · "
            "Parent: [ax-freeze.md](ax-freeze.md) · "
            f"Ship: **{SHIP_CLAIM}**",
            "",
            "## Question",
            "",
            "After AX froze hard-natural product + honest NANOGEN8 DEFER, "
            "can Wave AY **close intent/adversary product debt** "
            "(PRODINT + SHIPAY) **and** clear a **real new method** "
            "generative lift under ≤5M **without** unlabeled open-chat / "
            "GPT-class / NANOGEN9=NANOGEN8+rename?",
            "",
            "## Answer",
            "",
            "**Yes for Caminho A intent harden; honest DEFER for generative.** "
            "H-PRODINT · H-SHIPAY PROMOTE. **H-NANOGEN9 DEFER** "
            "(AY0 stance=defer; CAPCHECK closed; no real new method; "
            "NANOGEN6·7 HOLD · NANOGEN8 DEFER cited; not a rename). "
            "AY-REAL-EVAL PROMOTE (live battery 8/8; intent-FP ABSTAIN; "
            "gen unlock locked). "
            f"Ship claim stays STRICT archive: **{SHIP_CLAIM}**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-PRODINT | Intent FH 0 · hard-natural hold · DECODE → PROMOTE |",
            "| H-SHIPAY | Modes+content · intent ABSTAIN · DECODE law → PROMOTE |",
            "| H-NANOGEN9 | Gen stance defer · NANOGEN6·7 HOLD · NANOGEN8 DEFER cited → DEFER |",
            "| AY-REAL-EVAL | Live battery 8/8 · gen locked → PROMOTE |",
            "| AY-REPORT | Summary + paper-lab + anti-FP → PROMOTE |",
            "| AY-FREEZE | Outcomes lock — no Wave AZ invent |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP / SHIPAY must never be sold as generative IQ. Intent "
            "mismatch LOOKUP is a false-hit. PEAK and span-fallback stay "
            "product/extractive credit only. Hard-natural ≠ pack/pressure-para "
            "coverage. DECODE telemetry (`wall_ms`, `n_new`) is mandatory but "
            "insufficient for content_ok. SAFE≠quality. Gold-substring / "
            "gibberish-tail / truncate-to-span ≠ generative PROMOTE. "
            "**H-NANOGEN9 DEFER** plus cited **H-NANOGEN6** / **H-NANOGEN7 "
            "HOLD** and **H-NANOGEN8 DEFER** keep true-continue / mini-AGI "
            "language locked — ship remains STRICT ablated DECODE archive, "
            "not unlabeled open chat.",
            "",
            "## Takeaway one-liner",
            "",
            "**AY = Caminho A intent harden + gen DEFERs honestly "
            "(NANOGEN6·7 HOLD · NANOGEN8 DEFER stand; not NANOGEN8 rename); "
            "ship AF+AQ+AS trust + STRICT snippet-prefix DECODE — "
            "not unlabeled open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-ay-summary.md](wave-ay-summary.md) · "
            "[wave-ay-real-eval.md](wave-ay-real-eval.md) · "
            "[wave-ay-session.md](wave-ay-session.md) · "
            "[ax-freeze.md](ax-freeze.md)  ",
            "- Formals: PRODINT · SHIPAY · NANOGEN9  ",
            "- Demo: [shipay-demo.md](shipay-demo.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
