"""Wave BB REPORT: public closeout (BB-FOREVER anti-FP + honest NANOGEN12 DEFER)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from bb_session_ops import BB0_SHIP_LOCK

__all__ = [
    "BB_ID",
    "BB_THESIS",
    "BB_EVIDENCE",
    "BB_REPORT_MARKERS",
    "BB_SCOREBOARD",
    "SHIP_CLAIM",
    "decide_bb_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "realeval_section_ok",
    "render_wave_bb_summary",
    "render_paper_lab_wave_bb",
]

BB_ID = "BB-REPORT"
SHIP_CLAIM = BB0_SHIP_LOCK
BB_THESIS = (
    "Wave BB dual track: H-INTENTGEN·H-FASTHOLD·H-CTXHOLD PROMOTE "
    "(BB-FOREVER FH 0 · prod p50/p99 hold · howto·cite·long content · "
    "anti-FP); H-NANOGEN12 DEFER (gen stance defer · CAPCHECK closed · "
    "NANOGEN6·7 HOLD · NANOGEN8·9·10·11 DEFER cited · not NANOGEN11 rename); "
    "BB-REAL-EVAL PROMOTE (live battery 12/12 · BB-FOREVER FP ABSTAIN · "
    "BA forever hold · over-refuse LOOKUP · gen locked); ship " + SHIP_CLAIM
)

BB_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "BB0",
        "id": "SESSION",
        "metric": "packs frozen",
        "decision": "PROMOTE",
        "note": (
            "BB-FOREVER · BA/AZ hold · §1 scoreboard · gen stance defer · "
            "true-eval"
        ),
    },
    {
        "stage": "BB1",
        "id": "H-INTENTGEN",
        "metric": "BB-FOREVER FH 0 · live FP 0",
        "decision": "PROMOTE",
        "note": (
            "compositional binop gate · BA hold 0 · AZ hold 0 · "
            "over-refuse 0 · no bank stuffing"
        ),
    },
    {
        "stage": "BB2",
        "id": "H-FASTHOLD",
        "metric": "prod p50/p99 no FP regress",
        "decision": "PROMOTE",
        "note": (
            "prod latency hold · anti-FP hold · ≠ BA nano:ba:fastreal · "
            "≠ AG nano:fastreal"
        ),
    },
    {
        "stage": "BB3",
        "id": "H-CTXHOLD",
        "metric": "howto·cite·long content_ok",
        "decision": "PROMOTE",
        "note": (
            "content bars · BB/BA/AZ anti-FP · L_eff alone ≠ win · "
            "≠ BA nano:ba:ctxreal2"
        ),
    },
    {
        "stage": "BB4",
        "id": "H-NANOGEN12",
        "metric": "gen stance defer",
        "decision": "DEFER",
        "note": (
            "CAPCHECK closed · no real M1|M2|M3 · NANOGEN6·7 HOLD · "
            "NANOGEN8·9·10·11 DEFER · not rename"
        ),
    },
    {
        "stage": "BB5",
        "id": "BB-REAL-EVAL",
        "metric": "live ask battery 12/12",
        "decision": "PROMOTE",
        "note": (
            "product+ctx+speed pass · BB-FOREVER ABSTAIN · "
            "over-refuse LOOKUP · gen locked · prod=eval"
        ),
    },
    {
        "stage": "BB6",
        "id": "BB-REPORT",
        "metric": "summary + paper-lab",
        "decision": "PROMOTE",
        "note": (
            "docs + anti-FP · BB4 DEFER · NANOGEN6/7 HOLD · "
            "NANOGEN8·9·10·11 DEFER cited"
        ),
    },
    {
        "stage": "BB7",
        "id": "BB-FREEZE",
        "metric": "lock outcomes",
        "decision": "PROMOTE",
        "note": "COMPLETE+FROZEN · no Wave BC invent",
    },
)

BB_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-bb-session.md",
    "docs/results/nano-lm/formal-hintentgen-intentgen.md",
    "docs/results/nano-lm/formal-hfasthold-fasthold.md",
    "docs/results/nano-lm/formal-hctxhold-ctxhold.md",
    "docs/results/nano-lm/formal-hnanogen12-nanogen12.md",
    "docs/results/nano-lm/wave-bb-real-eval.md",
    "docs/results/nano-lm/wave-bb-summary.md",
    "docs/results/nano-lm/paper-lab-wave-bb.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

BB_REPORT_MARKERS: tuple[str, ...] = (
    "H-INTENTGEN",
    "H-FASTHOLD",
    "H-CTXHOLD",
    "H-NANOGEN12",
    "H-NANOGEN11",
    "H-NANOGEN10",
    "H-NANOGEN9",
    "H-NANOGEN8",
    "H-NANOGEN6",
    "H-NANOGEN7",
    "BB-REAL-EVAL",
    "BB-FOREVER",
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
)


def decide_bb_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = BB_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for BB report evidence
    WHEN deciding BB-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({BB_ID}: {BB_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = BB_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = BB_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking BB scoreboard
    THEN every stage id appears with Metric column.
    """
    body = str(text)
    if "Metric" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid.startswith("BB-"):
            if f"**{mid}**" not in body:
                return False
    return True


def antifp_section_ok(text: str) -> bool:
    """
    GIVEN summary body
    WHEN checking anti-FP evidence block
    THEN require modes + LOOKUP≠IQ + BB-FOREVER + NANOGEN6–12 honesty.
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
        "H-NANOGEN12",
        "H-NANOGEN11",
        "H-NANOGEN10",
        "H-NANOGEN9",
        "H-NANOGEN8",
        "H-NANOGEN6",
        "H-NANOGEN7",
        "BB-FOREVER",
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
        and "nanogen12" in body
        and "intentgen" in body
        and "fasthold" in body
        and "ctxhold" in body
        and "span-fallback" in body
        and "defer" in body
        and "nanogen6" in body
        and "nanogen7" in body
        and "nanogen8" in body
        and "nanogen9" in body
        and "nanogen10" in body
        and "nanogen11" in body
        and "bb-forever" in body
        and "over-refuse" in body
    )


def render_wave_bb_summary() -> str:
    lines = [
        "# Wave BB — compositional anti-FP + Nano gen-defer honesty "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §8 · Paper-lab: "
        "[paper-lab-wave-bb.md](paper-lab-wave-bb.md) · "
        "Real-eval: [wave-bb-real-eval.md](wave-bb-real-eval.md) · "
        "Freeze: [bb-freeze.md](bb-freeze.md) · "
        "[formal-habbfreeze-bb-freeze.md](formal-habbfreeze-bb-freeze.md)  ",
        "> Parent: Wave BA **BA-FREEZE** · Ship claim: "
        f"**{SHIP_CLAIM}**",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + BB_THESIS
        + ".**",
        "",
        "## Stage scoreboard (product + generative)",
        "",
        "| # | ID | Metric | Decision | Note |",
        "|---|-----|--------|----------|------|",
    ]
    for row in BB_SCOREBOARD:
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
            "H-INTENTGEN · BB-REAL-EVAL known_lookup · WRAP_LOOKUP |",
            "| PEAK extractive ≠ open-chat | "
            "BB-REAL-EVAL PEAK · H-CTXHOLD usable span |",
            "| DECODE arm `wall_ms>0` · `n_new>0` | "
            "BB-ASK-05 DECODE path · junk law |",
            "| DECODE gibberish ≠ content_ok | "
            "BB-ASK-06 junk→ABSTAIN |",
            "| BB-FOREVER intent LOOKUP = false-hit | "
            "H-INTENTGEN BB-FOREVER FH 0 · BB-ASK-07/11/12 ABSTAIN |",
            "| Exact-gold ABSTAIN = product miss | "
            "H-INTENTGEN over-refuse 0 · BB-ASK-08 LOOKUP |",
            "| ABSTAIN refuse junk / OOD / near-miss / forever | "
            "BB-REAL-EVAL OOD·junk·near-miss·BB-FOREVER·BA hold·AZ hold · "
            "FH 0 |",
            "| SAFE ≠ answer quality | "
            "H-INTENTGEN cites SAFE≠quality |",
            "| True-gen DEFER honesty | "
            "**H-NANOGEN12** DEFER · **H-NANOGEN11** DEFER · "
            "**H-NANOGEN10** DEFER · **H-NANOGEN9** DEFER · "
            "**H-NANOGEN8** DEFER · **H-NANOGEN6** HOLD · "
            "**H-NANOGEN7** HOLD · true_continue unmet · "
            "span-fallback ≠ gen IQ · not unlabeled open chat |",
            "| Modes always visible + content bars | "
            "**H-CTXHOLD** · **BB-REAL-EVAL** LOOKUP·PEAK·DECODE·ABSTAIN |",
            "| Speed without FP regress | "
            "**H-FASTHOLD** prod p50/p99 · anti-FP hold |",
            "| Generative claim gated | "
            "BB-REAL-EVAL · unlock only if BB4 PROMOTE |",
            "| Telemetry keys | `mode` · `wall_ms` · `n_new` · "
            "`product_mode` |",
            "",
            "## Honest claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| BB-FOREVER anti-FP scoreboard | **H-INTENTGEN** PROMOTE |",
            "| Prod speed p50/p99 hold | **H-FASTHOLD** PROMOTE |",
            "| Ctx howto·cite·long content | **H-CTXHOLD** PROMOTE |",
            "| North-star generative | **H-NANOGEN12** DEFER — "
            "stance defer · CAPCHECK closed · "
            "NANOGEN6·7 HOLD · NANOGEN8·9·10·11 DEFER stand · not rename |",
            "| Parent gen HOLDs / DEFER cited | **H-NANOGEN6** HOLD · "
            "**H-NANOGEN7** HOLD · **H-NANOGEN8** DEFER · "
            "**H-NANOGEN9** DEFER · **H-NANOGEN10** DEFER · "
            "**H-NANOGEN11** DEFER |",
            "| Final real eval | **BB-REAL-EVAL** PROMOTE — "
            "battery **12/12** · BB-FOREVER ABSTAIN · over-refuse LOOKUP · "
            "gen locked |",
            "| Ship claim | **" + SHIP_CLAIM + "** |",
            "| “Unlabeled open chat / GPT-class ≤5M” | **False** |",
            "| “TAC / true-continue unlocked” | **False** (BB4 DEFER) |",
            "| “Mini-AGI unlocked” | **False** (BB4 DEFER) |",
            "",
            "## Real-eval section",
            "",
            "| Arm | What was measured | Outcome |",
            "|-----|-------------------|---------|",
            "| Product (INTENTGEN) | BB-FOREVER FH 0 · BA/AZ hold · "
            "over-refuse 0 · live FP 0 | **PROMOTE** |",
            "| Speed (FASTHOLD) | prod p50/p99 · anti-FP hold | "
            "**PROMOTE** |",
            "| Context (CTXHOLD) | howto·cite·long content_ok · "
            "anti-FP hold | **PROMOTE** |",
            "| Generative (NANOGEN12) | defer stance · CAPCHECK closed · "
            "cite NANOGEN6·7 HOLD · NANOGEN8·9·10·11 DEFER · not rename | "
            "**DEFER** |",
            "| Live ask battery | LOOKUP·PEAK·DECODE·ABSTAIN + "
            "BB-FOREVER FP · BA forever · over-refuse · near-miss · "
            "DECODE junk→ABSTAIN | **PASS** 12/12 |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:bb:report",
            "npm run nano:bb:session",
            "npm run nano:intentgen",
            "npm run nano:bb:fasthold",
            "npm run nano:bb:ctxhold",
            "npm run nano:nanogen12",
            "npm run nano:bb:real-eval",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave BC without "
            "lab-book reopen · sell PEAK/bank-grounded as unlabeled open-chat · "
            "sell SAFE mean as IQ · sell span-fallback as true-continue · "
            "gold-substring PROMOTE · truncate-to-span as gen IQ · "
            "BB-FOREVER intent LOOKUP as success · over-refuse as win · "
            "NANOGEN12 = NANOGEN11+rename · bank stuffing BB-FOREVER · "
            "CTX/SMART/FAST/APP letter clones · rewrite BA/AZ/AY/… locks.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_bb() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave BB (compositional anti-FP + Nano gen-defer)",
            "",
            "> Companion to [wave-bb-summary.md](wave-bb-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · "
            "Real-eval: [wave-bb-real-eval.md](wave-bb-real-eval.md) · "
            "Freeze: [bb-freeze.md](bb-freeze.md) · "
            "[formal-habbfreeze-bb-freeze.md](formal-habbfreeze-bb-freeze.md) · "
            "Parent: [ba-freeze.md](ba-freeze.md) · "
            f"Ship: **{SHIP_CLAIM}**",
            "",
            "## Question",
            "",
            "After BA froze forever anti-FP + honest NANOGEN11 DEFER, "
            "can Wave BB **close compositional intent FP** "
            "(BB-FOREVER FH 0 + live ask) **and** hold **context** / "
            "**speed** on the prod path **and** clear a **real new method** "
            "generative lift under ≤5M **without** unlabeled open-chat / "
            "GPT-class / NANOGEN12=NANOGEN11+rename / bank stuffing?",
            "",
            "## Answer",
            "",
            "**Yes for compositional anti-FP + ctx/speed hold; honest DEFER "
            "for generative.** "
            "H-INTENTGEN · H-FASTHOLD · H-CTXHOLD PROMOTE. "
            "**H-NANOGEN12 DEFER** "
            "(BB0 stance=defer; CAPCHECK closed; no real M1|M2|M3; "
            "NANOGEN6·7 HOLD · NANOGEN8·9·10·11 DEFER cited; not a rename). "
            "BB-REAL-EVAL PROMOTE (live battery 12/12; BB-FOREVER FP ABSTAIN; "
            "over-refuse LOOKUP; gen unlock locked). "
            f"Ship claim stays STRICT archive: **{SHIP_CLAIM}**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-INTENTGEN | BB-FOREVER FH 0 · BA/AZ hold · "
            "over-refuse 0 → PROMOTE |",
            "| H-FASTHOLD | Prod p50/p99 hold · anti-FP hold → PROMOTE |",
            "| H-CTXHOLD | Howto·cite·long content_ok · "
            "anti-FP hold → PROMOTE |",
            "| H-NANOGEN12 | Gen stance defer · NANOGEN6·7 HOLD · "
            "NANOGEN8·9·10·11 DEFER cited → DEFER |",
            "| BB-REAL-EVAL | Live battery 12/12 · gen locked → PROMOTE |",
            "| BB-REPORT | Summary + paper-lab + anti-FP → PROMOTE |",
            "| BB-FREEZE | Outcomes lock — no Wave BC invent |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP / BB-FOREVER probes must never be sold as generative IQ. "
            "Compositional intent mismatch LOOKUP (min/xor/absdiff→add) is a "
            "false-hit. Exact-gold ABSTAIN is a product miss. PEAK and "
            "span-fallback stay product/extractive credit only. L_eff alone "
            "≠ ctx win. Warm-cache microbench ≠ speed win. DECODE telemetry "
            "(`wall_ms`, `n_new`) is mandatory but insufficient for "
            "content_ok. SAFE≠quality. Gold-substring / gibberish-tail / "
            "truncate-to-span ≠ generative PROMOTE. "
            "**H-NANOGEN12 DEFER** plus cited **H-NANOGEN6** / **H-NANOGEN7 "
            "HOLD** and **H-NANOGEN8** / **H-NANOGEN9** / **H-NANOGEN10** / "
            "**H-NANOGEN11 DEFER** keep true-continue / mini-AGI language "
            "locked — ship remains STRICT ablated DECODE archive, not "
            "unlabeled open chat.",
            "",
            "## Takeaway one-liner",
            "",
            "**BB = compositional BB-FOREVER anti-FP + measurable ctx/speed "
            "hold + gen DEFERs honestly (NANOGEN6·7 HOLD · "
            "NANOGEN8·9·10·11 DEFER stand; not NANOGEN11 rename); ship "
            "AF+AQ+AS trust + STRICT snippet-prefix DECODE — not unlabeled "
            "open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-bb-summary.md](wave-bb-summary.md) · "
            "[wave-bb-real-eval.md](wave-bb-real-eval.md) · "
            "[wave-bb-session.md](wave-bb-session.md) · "
            "[ba-freeze.md](ba-freeze.md)  ",
            "- Formals: INTENTGEN · FASTHOLD · CTXHOLD · NANOGEN12  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
