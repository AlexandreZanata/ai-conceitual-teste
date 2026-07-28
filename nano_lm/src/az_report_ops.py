"""Wave AZ REPORT: public closeout (held-out harden + honest NANOGEN10 DEFER)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from az_session_ops import AZ0_SHIP_LOCK

__all__ = [
    "AZ_ID",
    "AZ_THESIS",
    "AZ_EVIDENCE",
    "AZ_REPORT_MARKERS",
    "AZ_SCOREBOARD",
    "SHIP_CLAIM",
    "decide_az_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "realeval_section_ok",
    "render_wave_az_summary",
    "render_paper_lab_wave_az",
]

AZ_ID = "AZ-REPORT"
SHIP_CLAIM = AZ0_SHIP_LOCK
AZ_THESIS = (
    "Wave AZ dual track: H-PRODGEN·H-SHIPAZ PROMOTE (Caminho A · "
    "held-out FH 0 · no over-refuse · modes+content · DECODE law); "
    "H-NANOGEN10 DEFER (gen stance defer · CAPCHECK closed · "
    "NANOGEN6·7 HOLD · NANOGEN8·9 DEFER cited · not NANOGEN9 rename); "
    "AZ-REAL-EVAL PROMOTE (live battery 9/9 · held-out ABSTAIN · "
    "over-refuse LOOKUP · gen locked); ship " + SHIP_CLAIM
)

AZ_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AZ0",
        "id": "SESSION",
        "metric": "packs frozen",
        "decision": "PROMOTE",
        "note": "held-out FP · over-refuse · PRODGEN · gen stance defer · true-eval",
    },
    {
        "stage": "AZ1",
        "id": "H-PRODGEN",
        "metric": "held-out FH 0 Caminho A bars",
        "decision": "PROMOTE",
        "note": "held-out FH 0 · over-refuse 0 · AY named hold · p50/p99 · KB",
    },
    {
        "stage": "AZ2",
        "id": "H-SHIPAZ",
        "metric": "modes+content honest",
        "decision": "PROMOTE",
        "note": "LOOKUP·PEAK·DECODE·ABSTAIN · held-out ABSTAIN · over-refuse LOOKUP",
    },
    {
        "stage": "AZ3",
        "id": "H-NANOGEN10",
        "metric": "gen stance defer",
        "decision": "DEFER",
        "note": "CAPCHECK closed · no real new method · NANOGEN6·7 HOLD · NANOGEN8·9 DEFER · not rename",
    },
    {
        "stage": "AZ4",
        "id": "AZ-REAL-EVAL",
        "metric": "live ask battery 9/9",
        "decision": "PROMOTE",
        "note": "product pass · held-out ABSTAIN · over-refuse LOOKUP · gen locked · prod=eval",
    },
    {
        "stage": "AZ5",
        "id": "AZ-REPORT",
        "metric": "summary + paper-lab",
        "decision": "PROMOTE",
        "note": "docs + anti-FP · NANOGEN6/7 HOLD · NANOGEN8·9 DEFER cited",
    },
    {
        "stage": "AZ6",
        "id": "AZ-FREEZE",
        "metric": "lock outcomes",
        "decision": "PROMOTE",
        "note": "COMPLETE+FROZEN · no Wave BA invent",
    },
)

AZ_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-az-session.md",
    "docs/results/nano-lm/formal-hprodgen-prodgen.md",
    "docs/results/nano-lm/formal-hshipaz-shipaz.md",
    "docs/results/nano-lm/shipaz-demo.md",
    "docs/results/nano-lm/formal-hnanogen10-nanogen10.md",
    "docs/results/nano-lm/wave-az-real-eval.md",
    "docs/results/nano-lm/wave-az-summary.md",
    "docs/results/nano-lm/paper-lab-wave-az.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AZ_REPORT_MARKERS: tuple[str, ...] = (
    "H-PRODGEN",
    "H-SHIPAZ",
    "H-NANOGEN10",
    "H-NANOGEN9",
    "H-NANOGEN8",
    "H-NANOGEN6",
    "H-NANOGEN7",
    "AZ-REAL-EVAL",
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
    "held-out",
    "over-refuse",
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
    "NANOGEN9",
)


def decide_az_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AZ_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AZ report evidence
    WHEN deciding AZ-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AZ_ID}: {AZ_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AZ_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AZ_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking AZ scoreboard
    THEN every stage id appears with Metric column.
    """
    body = str(text)
    if "Metric" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid.startswith("AZ-"):
            if f"**{mid}**" not in body:
                return False
    return True


def antifp_section_ok(text: str) -> bool:
    """
    GIVEN summary body
    WHEN checking anti-FP evidence block
    THEN require modes + LOOKUP≠IQ + held-out + NANOGEN6/7/8/9/10 honesty.
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
        "H-NANOGEN10",
        "H-NANOGEN9",
        "H-NANOGEN8",
        "H-NANOGEN6",
        "H-NANOGEN7",
        "span-fallback",
        "true_continue",
        "held-out",
        "over-refuse",
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
        and "nanogen10" in body
        and "prodgen" in body
        and "shipaz" in body
        and "span-fallback" in body
        and "defer" in body
        and "nanogen6" in body
        and "nanogen7" in body
        and "nanogen8" in body
        and "nanogen9" in body
        and "held-out" in body
        and "over-refuse" in body
    )


def render_wave_az_summary() -> str:
    lines = [
        "# Wave AZ — held-out harden + Nano gen-defer honesty "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §5 · Paper-lab: "
        "[paper-lab-wave-az.md](paper-lab-wave-az.md) · "
        "Real-eval: [wave-az-real-eval.md](wave-az-real-eval.md) · "
        "Freeze: [az-freeze.md](az-freeze.md) · "
        "[formal-hazfreeze-az-freeze.md](formal-hazfreeze-az-freeze.md)  ",
        "> Parent: Wave AY **AY-FREEZE** · Ship claim: "
        f"**{SHIP_CLAIM}**",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + AZ_THESIS
        + ".**",
        "",
        "## Stage scoreboard (product + generative)",
        "",
        "| # | ID | Metric | Decision | Note |",
        "|---|-----|--------|----------|------|",
    ]
    for row in AZ_SCOREBOARD:
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
            "H-SHIPAZ · AZ-REAL-EVAL known_lookup · WRAP_LOOKUP |",
            "| PEAK extractive ≠ open-chat | "
            "H-SHIPAZ PEAK · H-PRODGEN usable span |",
            "| DECODE arm `wall_ms>0` · `n_new>0` | "
            "H-SHIPAZ WRAP_DECODE · AZ-ASK-05 |",
            "| DECODE gibberish ≠ content_ok | "
            "H-PRODGEN · H-SHIPAZ junk→ABSTAIN · AZ-ASK-06 |",
            "| Held-out intent LOOKUP = false-hit | "
            "H-PRODGEN held-out FH 0 · AZ-ASK-07 ABSTAIN |",
            "| Exact-gold ABSTAIN = product miss | "
            "H-PRODGEN over-refuse 0 · AZ-ASK-08 LOOKUP |",
            "| ABSTAIN refuse junk / OOD / near-miss / held-out | "
            "AZ-REAL-EVAL OOD·junk·SegWit/BIP-39·held-out refuse · FH 0 |",
            "| SAFE ≠ answer quality | "
            "H-PRODGEN cites SAFE≠quality |",
            "| True-gen DEFER honesty | "
            "**H-NANOGEN10** DEFER · **H-NANOGEN9** DEFER · "
            "**H-NANOGEN8** DEFER · **H-NANOGEN6** HOLD · "
            "**H-NANOGEN7** HOLD · true_continue unmet · "
            "span-fallback ≠ gen IQ · not unlabeled open chat |",
            "| Modes always visible + content bars | "
            "**H-SHIPAZ** LOOKUP·PEAK·DECODE·ABSTAIN |",
            "| Generative claim gated | "
            "AZ-REAL-EVAL · unlock only if AZ3 PROMOTE |",
            "| Telemetry keys | `mode` · `wall_ms` · `n_new` · "
            "`product_mode` |",
            "",
            "## Honest claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| Caminho A held-out harden | **H-PRODGEN** PROMOTE |",
            "| Mode+content ask/apps/ship | **H-SHIPAZ** PROMOTE |",
            "| North-star generative | **H-NANOGEN10** DEFER — "
            "stance defer · CAPCHECK closed · "
            "NANOGEN6·7 HOLD · NANOGEN8·9 DEFER stand · not rename |",
            "| Parent gen HOLDs / DEFER cited | **H-NANOGEN6** HOLD · "
            "**H-NANOGEN7** HOLD · **H-NANOGEN8** DEFER · "
            "**H-NANOGEN9** DEFER |",
            "| Final real eval | **AZ-REAL-EVAL** PROMOTE — "
            "battery **9/9** · held-out ABSTAIN · over-refuse LOOKUP · "
            "gen locked |",
            "| Ship claim | **" + SHIP_CLAIM + "** |",
            "| “Unlabeled open chat / GPT-class ≤5M” | **False** |",
            "| “TAC / true-continue unlocked” | **False** (AZ3 DEFER) |",
            "",
            "## Real-eval section",
            "",
            "| Arm | What was measured | Outcome |",
            "|-----|-------------------|---------|",
            "| Product (PRODGEN) | held-out FH 0 · over-refuse 0 · "
            "latency · KB · DECODE content | **PROMOTE** |",
            "| Product (SHIPAZ) | ask · apps · ship/demo modes+content · "
            "held-out ABSTAIN · over-refuse LOOKUP | **PROMOTE** |",
            "| Generative (NANOGEN10) | defer stance · CAPCHECK closed · "
            "cite NANOGEN6·7 HOLD · NANOGEN8·9 DEFER · not rename | "
            "**DEFER** |",
            "| Live ask battery | LOOKUP·PEAK·DECODE·ABSTAIN + "
            "held-out FP · over-refuse · near-miss · DECODE junk→ABSTAIN | "
            "**PASS** 9/9 |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:az:report",
            "npm run nano:az:session",
            "npm run nano:prodgen",
            "npm run nano:shipaz",
            "npm run nano:nanogen10",
            "npm run nano:az:real-eval",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave BA without "
            "lab-book reopen · sell PEAK/bank-grounded as unlabeled open-chat · "
            "sell SAFE mean as IQ · sell span-fallback as true-continue · "
            "gold-substring PROMOTE · truncate-to-span as gen IQ · "
            "held-out intent LOOKUP as success · over-refuse as win · "
            "NANOGEN10 = NANOGEN9+rename · "
            "CTX/SMART/FAST/APP letter clones · rewrite AY/AX/AW/AV/AU/AT/AS locks.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_az() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AZ (held-out harden + Nano gen-defer)",
            "",
            "> Companion to [wave-az-summary.md](wave-az-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · "
            "Real-eval: [wave-az-real-eval.md](wave-az-real-eval.md) · "
            "Freeze: [az-freeze.md](az-freeze.md) · "
            "[formal-hazfreeze-az-freeze.md](formal-hazfreeze-az-freeze.md) · "
            "Parent: [ay-freeze.md](ay-freeze.md) · "
            f"Ship: **{SHIP_CLAIM}**",
            "",
            "## Question",
            "",
            "After AY froze intent product + honest NANOGEN9 DEFER, "
            "can Wave AZ **close held-out / over-refuse product debt** "
            "(PRODGEN + SHIPAZ) **and** clear a **real new method** "
            "generative lift under ≤5M **without** unlabeled open-chat / "
            "GPT-class / NANOGEN10=NANOGEN9+rename?",
            "",
            "## Answer",
            "",
            "**Yes for Caminho A held-out harden; honest DEFER for generative.** "
            "H-PRODGEN · H-SHIPAZ PROMOTE. **H-NANOGEN10 DEFER** "
            "(AZ0 stance=defer; CAPCHECK closed; no real new method; "
            "NANOGEN6·7 HOLD · NANOGEN8·9 DEFER cited; not a rename). "
            "AZ-REAL-EVAL PROMOTE (live battery 9/9; held-out ABSTAIN; "
            "over-refuse LOOKUP; gen unlock locked). "
            f"Ship claim stays STRICT archive: **{SHIP_CLAIM}**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-PRODGEN | Held-out FH 0 · over-refuse 0 · DECODE → PROMOTE |",
            "| H-SHIPAZ | Modes+content · held-out ABSTAIN · over-refuse LOOKUP → PROMOTE |",
            "| H-NANOGEN10 | Gen stance defer · NANOGEN6·7 HOLD · NANOGEN8·9 DEFER cited → DEFER |",
            "| AZ-REAL-EVAL | Live battery 9/9 · gen locked → PROMOTE |",
            "| AZ-REPORT | Summary + paper-lab + anti-FP → PROMOTE |",
            "| AZ-FREEZE | Outcomes lock — no Wave BA invent |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP / SHIPAZ must never be sold as generative IQ. Held-out "
            "intent mismatch LOOKUP is a false-hit. Exact-gold ABSTAIN is a "
            "product miss. PEAK and span-fallback stay product/extractive "
            "credit only. Named-class FH 0 ≠ held-out coverage. DECODE "
            "telemetry (`wall_ms`, `n_new`) is mandatory but insufficient "
            "for content_ok. SAFE≠quality. Gold-substring / gibberish-tail / "
            "truncate-to-span ≠ generative PROMOTE. "
            "**H-NANOGEN10 DEFER** plus cited **H-NANOGEN6** / **H-NANOGEN7 "
            "HOLD** and **H-NANOGEN8** / **H-NANOGEN9 DEFER** keep "
            "true-continue / mini-AGI language locked — ship remains STRICT "
            "ablated DECODE archive, not unlabeled open chat.",
            "",
            "## Takeaway one-liner",
            "",
            "**AZ = Caminho A held-out harden + gen DEFERs honestly "
            "(NANOGEN6·7 HOLD · NANOGEN8·9 DEFER stand; not NANOGEN9 rename); "
            "ship AF+AQ+AS trust + STRICT snippet-prefix DECODE — "
            "not unlabeled open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-az-summary.md](wave-az-summary.md) · "
            "[wave-az-real-eval.md](wave-az-real-eval.md) · "
            "[wave-az-session.md](wave-az-session.md) · "
            "[ay-freeze.md](ay-freeze.md)  ",
            "- Formals: PRODGEN · SHIPAZ · NANOGEN10  ",
            "- Demo: [shipaz-demo.md](shipaz-demo.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
