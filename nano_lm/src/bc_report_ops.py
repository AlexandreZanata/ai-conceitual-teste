"""Wave BC REPORT: public closeout (BC-FOREVER anti-FP + honest NANOGEN13 DEFER)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from bc_session_ops import BC0_SHIP_LOCK

__all__ = [
    "BC_ID",
    "BC_THESIS",
    "BC_EVIDENCE",
    "BC_REPORT_MARKERS",
    "BC_SCOREBOARD",
    "SHIP_CLAIM",
    "decide_bc_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "realeval_section_ok",
    "render_wave_bc_summary",
    "render_paper_lab_wave_bc",
]

BC_ID = "BC-REPORT"
SHIP_CLAIM = BC0_SHIP_LOCK
BC_THESIS = (
    "Wave BC dual track: H-OPSFAM·H-FASTLIFT·H-CTXLIFT2 PROMOTE "
    "(BC-FOREVER FH 0 · prod p50/p99 hold · howto·cite·long content · "
    "anti-FP); H-NANOGEN13 DEFER (gen stance defer · CAPCHECK closed · "
    "NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER cited · not NANOGEN12 rename); "
    "BC-REAL-EVAL PROMOTE (live battery 13/13 · BC-FOREVER FP ABSTAIN · "
    "BA/BB forever hold · over-refuse LOOKUP · gen locked); ship " + SHIP_CLAIM
)

BC_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "BC0",
        "id": "SESSION",
        "metric": "packs frozen",
        "decision": "PROMOTE",
        "note": (
            "BC-FOREVER · BA/BB/AZ hold · §1 scoreboard · gen stance defer · "
            "true-eval"
        ),
    },
    {
        "stage": "BC1",
        "id": "H-OPSFAM",
        "metric": "BC-FOREVER FH 0 · live FP 0",
        "decision": "PROMOTE",
        "note": (
            "family ops gate · BA/BB hold 0 · AZ hold 0 · "
            "over-refuse 0 · no bank stuffing"
        ),
    },
    {
        "stage": "BC2",
        "id": "H-FASTLIFT",
        "metric": "prod p50/p99 no FP regress",
        "decision": "PROMOTE",
        "note": (
            "prod latency hold · anti-FP hold · ≠ AH nano:fastlift · "
            "≠ BB nano:bb:fasthold"
        ),
    },
    {
        "stage": "BC3",
        "id": "H-CTXLIFT2",
        "metric": "howto·cite·long content_ok",
        "decision": "PROMOTE",
        "note": (
            "content bars · BC/BA/BB/AZ anti-FP · L_eff alone ≠ win · "
            "≠ AH nano:ctxlift · ≠ BB nano:bb:ctxhold"
        ),
    },
    {
        "stage": "BC4",
        "id": "H-NANOGEN13",
        "metric": "gen stance defer",
        "decision": "DEFER",
        "note": (
            "CAPCHECK closed · no real M1|M2|M3 · NANOGEN6·7 HOLD · "
            "NANOGEN8·9·10·11·12 DEFER · not rename"
        ),
    },
    {
        "stage": "BC5",
        "id": "BC-REAL-EVAL",
        "metric": "live ask battery 13/13",
        "decision": "PROMOTE",
        "note": (
            "product+ctx+speed pass · BC-FOREVER ABSTAIN · "
            "over-refuse LOOKUP · gen locked · prod=eval"
        ),
    },
    {
        "stage": "BC6",
        "id": "BC-REPORT",
        "metric": "summary + paper-lab",
        "decision": "PROMOTE",
        "note": (
            "docs + anti-FP · BC4 DEFER · NANOGEN6/7 HOLD · "
            "NANOGEN8·9·10·11·12 DEFER cited"
        ),
    },
    {
        "stage": "BC7",
        "id": "BC-FREEZE",
        "metric": "lock outcomes",
        "decision": "PROMOTE",
        "note": "COMPLETE+FROZEN · no Wave BD invent",
    },
)

BC_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-bc-session.md",
    "docs/results/nano-lm/formal-hopsfam-opsfam.md",
    "docs/results/nano-lm/formal-hfastlift-bc2.md",
    "docs/results/nano-lm/formal-hctxlift2-ctxlift2.md",
    "docs/results/nano-lm/formal-hnanogen13-nanogen13.md",
    "docs/results/nano-lm/wave-bc-real-eval.md",
    "docs/results/nano-lm/wave-bc-summary.md",
    "docs/results/nano-lm/paper-lab-wave-bc.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

BC_REPORT_MARKERS: tuple[str, ...] = (
    "H-OPSFAM",
    "H-FASTLIFT",
    "H-CTXLIFT2",
    "H-NANOGEN13",
    "H-NANOGEN12",
    "H-NANOGEN11",
    "H-NANOGEN10",
    "H-NANOGEN9",
    "H-NANOGEN8",
    "H-NANOGEN6",
    "H-NANOGEN7",
    "BC-REAL-EVAL",
    "BC-FOREVER",
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
    "anti-FP",
    "forever",
    "PROMOTE",
    "DEFER",
    "HOLD",
    "true_continue",
    "span-fallback",
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
    "NANOGEN10",
    "NANOGEN11",
    "NANOGEN12",
)


def decide_bc_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = BC_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for BC report evidence
    WHEN deciding BC-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({BC_ID}: {BC_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = BC_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = BC_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking BC scoreboard
    THEN every stage id appears with Metric column.
    """
    body = str(text)
    if "Metric" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid.startswith("BC-"):
            if f"**{mid}**" not in body:
                return False
    return True


def antifp_section_ok(text: str) -> bool:
    """
    GIVEN summary body
    WHEN checking anti-FP evidence block
    THEN require modes + LOOKUP≠IQ + BC-FOREVER + NANOGEN6–13 honesty.
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
        "H-NANOGEN13",
        "H-NANOGEN12",
        "H-NANOGEN11",
        "H-NANOGEN10",
        "H-NANOGEN9",
        "H-NANOGEN8",
        "H-NANOGEN6",
        "H-NANOGEN7",
        "BC-FOREVER",
        "span-fallback",
        "true_continue",
        "forever",
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
        and "nanogen13" in body
        and "opsfam" in body
        and "fastlift" in body
        and "ctxlift2" in body
        and "span-fallback" in body
        and "defer" in body
        and "nanogen6" in body
        and "nanogen7" in body
        and "nanogen8" in body
        and "nanogen9" in body
        and "nanogen10" in body
        and "nanogen11" in body
        and "nanogen12" in body
        and "bc-forever" in body
        and "over-refuse" in body
    )


def render_wave_bc_summary() -> str:
    lines = [
        "# Wave BC — family anti-FP + Nano gen-defer honesty "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §9 · Paper-lab: "
        "[paper-lab-wave-bc.md](paper-lab-wave-bc.md) · "
        "Real-eval: [wave-bc-real-eval.md](wave-bc-real-eval.md) · "
        "Freeze: [bc-freeze.md](bc-freeze.md) · "
        "[formal-habcfreeze-bc-freeze.md](formal-habcfreeze-bc-freeze.md)  ",
        "> Parent: Wave BB **BB-FREEZE** · Ship claim: "
        f"**{SHIP_CLAIM}**",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + BC_THESIS
        + ".**",
        "",
        "## Stage scoreboard (product + generative)",
        "",
        "| # | ID | Metric | Decision | Note |",
        "|---|-----|--------|----------|------|",
    ]
    for row in BC_SCOREBOARD:
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
            "H-OPSFAM · BC-REAL-EVAL known_lookup · WRAP_LOOKUP |",
            "| PEAK extractive ≠ open-chat | "
            "BC-REAL-EVAL PEAK · H-CTXLIFT2 usable span |",
            "| DECODE arm `wall_ms>0` · `n_new>0` | "
            "BC-ASK-05 DECODE path · junk law |",
            "| DECODE gibberish ≠ content_ok | "
            "BC-ASK-06 junk→ABSTAIN |",
            "| BC-FOREVER intent LOOKUP = false-hit | "
            "H-OPSFAM BC-FOREVER FH 0 · BC-ASK-07/12/13 ABSTAIN |",
            "| Exact-gold ABSTAIN = product miss | "
            "H-OPSFAM over-refuse 0 · BC-ASK-08 LOOKUP |",
            "| ABSTAIN refuse junk / OOD / near-miss / forever | "
            "BC-REAL-EVAL OOD·junk·near-miss·BC-FOREVER·BA hold·BB hold·"
            "AZ hold · FH 0 |",
            "| SAFE ≠ answer quality | "
            "H-OPSFAM cites SAFE≠quality |",
            "| True-gen DEFER honesty | "
            "**H-NANOGEN13** DEFER · **H-NANOGEN12** DEFER · "
            "**H-NANOGEN11** DEFER · **H-NANOGEN10** DEFER · "
            "**H-NANOGEN9** DEFER · **H-NANOGEN8** DEFER · "
            "**H-NANOGEN6** HOLD · **H-NANOGEN7** HOLD · true_continue unmet · "
            "span-fallback ≠ gen IQ · not unlabeled open chat |",
            "| Modes always visible + content bars | "
            "**H-CTXLIFT2** · **BC-REAL-EVAL** LOOKUP·PEAK·DECODE·ABSTAIN |",
            "| Speed without FP regress | "
            "**H-FASTLIFT** prod p50/p99 · anti-FP hold |",
            "| Generative claim gated | "
            "BC-REAL-EVAL · unlock only if BC4 PROMOTE |",
            "| Telemetry keys | `mode` · `wall_ms` · `n_new` · "
            "`product_mode` |",
            "",
            "## Honest claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| BC-FOREVER anti-FP scoreboard | **H-OPSFAM** PROMOTE |",
            "| Prod speed p50/p99 hold | **H-FASTLIFT** PROMOTE |",
            "| Ctx howto·cite·long content | **H-CTXLIFT2** PROMOTE |",
            "| North-star generative | **H-NANOGEN13** DEFER — "
            "stance defer · CAPCHECK closed · "
            "NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER stand · not rename |",
            "| Parent gen HOLDs / DEFER cited | **H-NANOGEN6** HOLD · "
            "**H-NANOGEN7** HOLD · **H-NANOGEN8** DEFER · "
            "**H-NANOGEN9** DEFER · **H-NANOGEN10** DEFER · "
            "**H-NANOGEN11** DEFER · **H-NANOGEN12** DEFER |",
            "| Final real eval | **BC-REAL-EVAL** PROMOTE — "
            "battery **13/13** · BC-FOREVER ABSTAIN · over-refuse LOOKUP · "
            "gen locked |",
            "| Ship claim | **" + SHIP_CLAIM + "** |",
            "| “Unlabeled open chat / GPT-class ≤5M” | **False** |",
            "| “TAC / true-continue unlocked” | **False** (BC4 DEFER) |",
            "| “Mini-AGI unlocked” | **False** (BC4 DEFER) |",
            "",
            "## Real-eval section",
            "",
            "| Arm | What was measured | Outcome |",
            "|-----|-------------------|---------|",
            "| Product (OPSFAM) | BC-FOREVER FH 0 · BA/BB/AZ hold · "
            "over-refuse 0 · live FP 0 | **PROMOTE** |",
            "| Speed (FASTLIFT) | prod p50/p99 · anti-FP hold | "
            "**PROMOTE** |",
            "| Context (CTXLIFT2) | howto·cite·long content_ok · "
            "anti-FP hold | **PROMOTE** |",
            "| Generative (NANOGEN13) | defer stance · CAPCHECK closed · "
            "cite NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER · not rename | "
            "**DEFER** |",
            "| Live ask battery | LOOKUP·PEAK·DECODE·ABSTAIN + "
            "BC-FOREVER FP · BA/BB forever · over-refuse · near-miss · "
            "DECODE junk→ABSTAIN | **PASS** 13/13 |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:bc:report",
            "npm run nano:bc:session",
            "npm run nano:opsfam",
            "npm run nano:bc:fastlift",
            "npm run nano:bc:ctxlift2",
            "npm run nano:nanogen13",
            "npm run nano:bc:real-eval",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave BD without "
            "lab-book reopen · sell PEAK/bank-grounded as unlabeled open-chat · "
            "sell SAFE mean as IQ · sell span-fallback as true-continue · "
            "gold-substring PROMOTE · truncate-to-span as gen IQ · "
            "BC-FOREVER intent LOOKUP as success · over-refuse as win · "
            "NANOGEN13 = NANOGEN12+rename · bank stuffing BC-FOREVER · "
            "CTX/SMART/FAST/APP letter clones · rewrite BB/BA/AZ/… locks.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_bc() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave BC (family anti-FP + Nano gen-defer)",
            "",
            "> Companion to [wave-bc-summary.md](wave-bc-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · "
            "Real-eval: [wave-bc-real-eval.md](wave-bc-real-eval.md) · "
            "Freeze: [bc-freeze.md](bc-freeze.md) · "
            "[formal-habcfreeze-bc-freeze.md](formal-habcfreeze-bc-freeze.md) · "
            "Parent: [bb-freeze.md](bb-freeze.md) · "
            f"Ship: **{SHIP_CLAIM}**",
            "",
            "## Question",
            "",
            "After BB froze compositional anti-FP + honest NANOGEN12 DEFER, "
            "can Wave BC **close family-level residual intent FP** "
            "(BC-FOREVER FH 0 + live ask + novel) **and** hold **context** / "
            "**speed** on the prod path **and** clear a **real new method** "
            "generative lift under ≤5M **without** unlabeled open-chat / "
            "GPT-class / NANOGEN13=NANOGEN12+rename / bank stuffing?",
            "",
            "## Answer",
            "",
            "**Yes for family anti-FP + ctx/speed hold; honest DEFER "
            "for generative.** "
            "H-OPSFAM · H-FASTLIFT · H-CTXLIFT2 PROMOTE. "
            "**H-NANOGEN13 DEFER** "
            "(BC0 stance=defer; CAPCHECK closed; no real M1|M2|M3; "
            "NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER cited; not a rename). "
            "BC-REAL-EVAL PROMOTE (live battery 13/13; BC-FOREVER FP ABSTAIN; "
            "over-refuse LOOKUP; gen unlock locked). "
            f"Ship claim stays STRICT archive: **{SHIP_CLAIM}**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-OPSFAM | BC-FOREVER FH 0 · BA/BB/AZ hold · "
            "over-refuse 0 → PROMOTE |",
            "| H-FASTLIFT | Prod p50/p99 hold · anti-FP hold → PROMOTE |",
            "| H-CTXLIFT2 | Howto·cite·long content_ok · "
            "anti-FP hold → PROMOTE |",
            "| H-NANOGEN13 | Gen stance defer · NANOGEN6·7 HOLD · "
            "NANOGEN8·9·10·11·12 DEFER cited → DEFER |",
            "| BC-REAL-EVAL | Live battery 13/13 · gen locked → PROMOTE |",
            "| BC-REPORT | Summary + paper-lab + anti-FP → PROMOTE |",
            "| BC-FREEZE | Outcomes lock — no Wave BD invent |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP / BC-FOREVER probes must never be sold as generative IQ. "
            "Family intent mismatch LOOKUP (floordiv/gcd/shift/nand→add) is a "
            "false-hit. Exact-gold ABSTAIN is a product miss. PEAK and "
            "span-fallback stay product/extractive credit only. L_eff alone "
            "≠ ctx win. Warm-cache microbench ≠ speed win. DECODE telemetry "
            "(`wall_ms`, `n_new`) is mandatory but insufficient for "
            "content_ok. SAFE≠quality. Gold-substring / gibberish-tail / "
            "truncate-to-span ≠ generative PROMOTE. "
            "**H-NANOGEN13 DEFER** plus cited **H-NANOGEN6** / **H-NANOGEN7 "
            "HOLD** and **H-NANOGEN8** / **H-NANOGEN9** / **H-NANOGEN10** / "
            "**H-NANOGEN11** / **H-NANOGEN12 DEFER** keep true-continue / "
            "mini-AGI language locked — ship remains STRICT ablated DECODE "
            "archive, not unlabeled open chat.",
            "",
            "## Takeaway one-liner",
            "",
            "**BC = family BC-FOREVER anti-FP + measurable ctx/speed "
            "hold + gen DEFERs honestly (NANOGEN6·7 HOLD · "
            "NANOGEN8·9·10·11·12 DEFER stand; not NANOGEN12 rename); ship "
            "AF+AQ+AS trust + STRICT snippet-prefix DECODE — not unlabeled "
            "open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-bc-summary.md](wave-bc-summary.md) · "
            "[wave-bc-real-eval.md](wave-bc-real-eval.md) · "
            "[wave-bc-session.md](wave-bc-session.md) · "
            "[bb-freeze.md](bb-freeze.md)  ",
            "- Formals: OPSFAM · FASTLIFT · CTXLIFT2 · NANOGEN13  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
