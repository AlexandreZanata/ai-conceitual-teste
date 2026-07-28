"""Wave BD REPORT: public closeout (BD-FOREVER anti-FP + honest NANOGEN14 DEFER)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from bd_session_ops import BD0_SHIP_LOCK

__all__ = [
    "BD_ID",
    "BD_THESIS",
    "BD_EVIDENCE",
    "BD_REPORT_MARKERS",
    "BD_SCOREBOARD",
    "SHIP_CLAIM",
    "decide_bd_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "realeval_section_ok",
    "render_wave_bd_summary",
    "render_paper_lab_wave_bd",
]

BD_ID = "BD-REPORT"
SHIP_CLAIM = BD0_SHIP_LOCK
BD_THESIS = (
    "Wave BD dual track: H-SEMINT·H-FASTGAIN·H-CTXGAIN PROMOTE "
    "(BD-FOREVER FH 0 · prod p50/p99 hold · howto·cite·long content · "
    "anti-FP); H-NANOGEN14 DEFER (gen stance defer · CAPCHECK closed · "
    "NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12·13 DEFER cited · not NANOGEN13 "
    "rename); BD-REAL-EVAL PROMOTE (live battery 14/14 · BD-FOREVER FP "
    "ABSTAIN · BA/BB/BC forever hold · over-refuse LOOKUP · gen locked); "
    "ship " + SHIP_CLAIM
)

BD_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "BD0",
        "id": "SESSION",
        "metric": "packs frozen",
        "decision": "PROMOTE",
        "note": (
            "BD-FOREVER · BA/BB/BC/AZ hold · §1 scoreboard · gen stance "
            "defer · true-eval"
        ),
    },
    {
        "stage": "BD1",
        "id": "H-SEMINT",
        "metric": "BD-FOREVER FH 0 · live FP 0",
        "decision": "PROMOTE",
        "note": (
            "semantic intent gate · BA/BB/BC hold 0 · AZ hold 0 · "
            "over-refuse 0 · no bank stuffing"
        ),
    },
    {
        "stage": "BD2",
        "id": "H-FASTGAIN",
        "metric": "prod p50/p99 no FP regress",
        "decision": "PROMOTE",
        "note": (
            "prod latency hold · anti-FP hold · ≠ AH nano:fastlift · "
            "≠ BC nano:bc:fastlift"
        ),
    },
    {
        "stage": "BD3",
        "id": "H-CTXGAIN",
        "metric": "howto·cite·long content_ok",
        "decision": "PROMOTE",
        "note": (
            "content bars · BD/BA/BB/BC/AZ anti-FP · L_eff alone ≠ win · "
            "≠ AH nano:ctxlift · ≠ BC nano:bc:ctxlift2"
        ),
    },
    {
        "stage": "BD4",
        "id": "H-NANOGEN14",
        "metric": "gen stance defer",
        "decision": "DEFER",
        "note": (
            "CAPCHECK closed · no real M1|M2|M3 · NANOGEN6·7 HOLD · "
            "NANOGEN8·9·10·11·12·13 DEFER · not rename"
        ),
    },
    {
        "stage": "BD5",
        "id": "BD-REAL-EVAL",
        "metric": "live ask battery 14/14",
        "decision": "PROMOTE",
        "note": (
            "product+ctx+speed pass · BD-FOREVER ABSTAIN · "
            "over-refuse LOOKUP · gen locked · prod=eval"
        ),
    },
    {
        "stage": "BD6",
        "id": "BD-REPORT",
        "metric": "summary + paper-lab",
        "decision": "PROMOTE",
        "note": (
            "docs + anti-FP · BD4 DEFER · NANOGEN6/7 HOLD · "
            "NANOGEN8·9·10·11·12·13 DEFER cited"
        ),
    },
    {
        "stage": "BD7",
        "id": "BD-FREEZE",
        "metric": "lock outcomes",
        "decision": "PROMOTE",
        "note": "COMPLETE+FROZEN · no Wave BE invent",
    },
)

BD_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-bd-session.md",
    "docs/results/nano-lm/formal-hsemint-semint.md",
    "docs/results/nano-lm/formal-hfastgain-fastgain.md",
    "docs/results/nano-lm/formal-hctxgain-ctxgain.md",
    "docs/results/nano-lm/formal-hnanogen14-nanogen14.md",
    "docs/results/nano-lm/wave-bd-real-eval.md",
    "docs/results/nano-lm/wave-bd-summary.md",
    "docs/results/nano-lm/paper-lab-wave-bd.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

BD_REPORT_MARKERS: tuple[str, ...] = (
    "H-SEMINT",
    "H-FASTGAIN",
    "H-CTXGAIN",
    "H-NANOGEN14",
    "H-NANOGEN13",
    "H-NANOGEN12",
    "H-NANOGEN11",
    "H-NANOGEN10",
    "H-NANOGEN9",
    "H-NANOGEN8",
    "H-NANOGEN6",
    "H-NANOGEN7",
    "BD-REAL-EVAL",
    "BD-FOREVER",
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
    "NANOGEN13",
)


def decide_bd_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = BD_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for BD report evidence
    WHEN deciding BD-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({BD_ID}: {BD_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = BD_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = BD_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking BD scoreboard
    THEN every stage id appears with Metric column.
    """
    body = str(text)
    if "Metric" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid.startswith("BD-"):
            if f"**{mid}**" not in body:
                return False
    return True


def antifp_section_ok(text: str) -> bool:
    """
    GIVEN summary body
    WHEN checking anti-FP evidence block
    THEN require modes + LOOKUP≠IQ + BD-FOREVER + NANOGEN6–14 honesty.
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
        "H-NANOGEN14",
        "H-NANOGEN13",
        "H-NANOGEN12",
        "H-NANOGEN11",
        "H-NANOGEN10",
        "H-NANOGEN9",
        "H-NANOGEN8",
        "H-NANOGEN6",
        "H-NANOGEN7",
        "BD-FOREVER",
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
        and "nanogen14" in body
        and "semint" in body
        and "fastgain" in body
        and "ctxgain" in body
        and "span-fallback" in body
        and "defer" in body
        and "nanogen6" in body
        and "nanogen7" in body
        and "nanogen8" in body
        and "nanogen9" in body
        and "nanogen10" in body
        and "nanogen11" in body
        and "nanogen12" in body
        and "nanogen13" in body
        and "bd-forever" in body
        and "over-refuse" in body
    )


def render_wave_bd_summary() -> str:
    lines = [
        "# Wave BD — semantic anti-FP + Nano gen-defer honesty "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §9 · Paper-lab: "
        "[paper-lab-wave-bd.md](paper-lab-wave-bd.md) · "
        "Real-eval: [wave-bd-real-eval.md](wave-bd-real-eval.md) · "
        "Freeze: [bd-freeze.md](bd-freeze.md) · "
        "[formal-habdfreeze-bd-freeze.md](formal-habdfreeze-bd-freeze.md)  ",
        "> Parent: Wave BC **BC-FREEZE** · Ship claim: "
        f"**{SHIP_CLAIM}**",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + BD_THESIS
        + ".**",
        "",
        "## Stage scoreboard (product + generative)",
        "",
        "| # | ID | Metric | Decision | Note |",
        "|---|-----|--------|----------|------|",
    ]
    for row in BD_SCOREBOARD:
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
            "H-SEMINT · BD-REAL-EVAL known_lookup · WRAP_LOOKUP |",
            "| PEAK extractive ≠ open-chat | "
            "BD-REAL-EVAL PEAK · H-CTXGAIN usable span |",
            "| DECODE arm `wall_ms>0` · `n_new>0` | "
            "BD-ASK-05 DECODE path · junk law |",
            "| DECODE gibberish ≠ content_ok | "
            "BD-ASK-06 junk→ABSTAIN |",
            "| BD-FOREVER semantic LOOKUP = false-hit | "
            "H-SEMINT BD-FOREVER FH 0 · BD-ASK-07/13/14 ABSTAIN |",
            "| Exact-gold ABSTAIN = product miss | "
            "H-SEMINT over-refuse 0 · BD-ASK-08 LOOKUP |",
            "| ABSTAIN refuse junk / OOD / near-miss / forever | "
            "BD-REAL-EVAL OOD·junk·near-miss·BD-FOREVER·BA hold·BB hold·"
            "BC hold·AZ hold · FH 0 |",
            "| SAFE ≠ answer quality | "
            "H-SEMINT cites SAFE≠quality |",
            "| True-gen DEFER honesty | "
            "**H-NANOGEN14** DEFER · **H-NANOGEN13** DEFER · "
            "**H-NANOGEN12** DEFER · **H-NANOGEN11** DEFER · "
            "**H-NANOGEN10** DEFER · **H-NANOGEN9** DEFER · "
            "**H-NANOGEN8** DEFER · **H-NANOGEN6** HOLD · "
            "**H-NANOGEN7** HOLD · true_continue unmet · "
            "span-fallback ≠ gen IQ · not unlabeled open chat |",
            "| Modes always visible + content bars | "
            "**H-CTXGAIN** · **BD-REAL-EVAL** LOOKUP·PEAK·DECODE·ABSTAIN |",
            "| Speed without FP regress | "
            "**H-FASTGAIN** prod p50/p99 · anti-FP hold |",
            "| Generative claim gated | "
            "BD-REAL-EVAL · unlock only if BD4 PROMOTE |",
            "| Telemetry keys | `mode` · `wall_ms` · `n_new` · "
            "`product_mode` |",
            "",
            "## Honest claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| BD-FOREVER anti-FP scoreboard | **H-SEMINT** PROMOTE |",
            "| Prod speed p50/p99 hold | **H-FASTGAIN** PROMOTE |",
            "| Ctx howto·cite·long content | **H-CTXGAIN** PROMOTE |",
            "| North-star generative | **H-NANOGEN14** DEFER — "
            "stance defer · CAPCHECK closed · "
            "NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12·13 DEFER stand · "
            "not rename |",
            "| Parent gen HOLDs / DEFER cited | **H-NANOGEN6** HOLD · "
            "**H-NANOGEN7** HOLD · **H-NANOGEN8** DEFER · "
            "**H-NANOGEN9** DEFER · **H-NANOGEN10** DEFER · "
            "**H-NANOGEN11** DEFER · **H-NANOGEN12** DEFER · "
            "**H-NANOGEN13** DEFER |",
            "| Final real eval | **BD-REAL-EVAL** PROMOTE — "
            "battery **14/14** · BD-FOREVER ABSTAIN · over-refuse LOOKUP · "
            "gen locked |",
            "| Ship claim | **" + SHIP_CLAIM + "** |",
            "| “Unlabeled open chat / GPT-class ≤5M” | **False** |",
            "| “TAC / true-continue unlocked” | **False** (BD4 DEFER) |",
            "| “Mini-AGI unlocked” | **False** (BD4 DEFER) |",
            "",
            "## Real-eval section",
            "",
            "| Arm | What was measured | Outcome |",
            "|-----|-------------------|---------|",
            "| Product (SEMINT) | BD-FOREVER FH 0 · BA/BB/BC/AZ hold · "
            "over-refuse 0 · live FP 0 | **PROMOTE** |",
            "| Speed (FASTGAIN) | prod p50/p99 · anti-FP hold | "
            "**PROMOTE** |",
            "| Context (CTXGAIN) | howto·cite·long content_ok · "
            "anti-FP hold | **PROMOTE** |",
            "| Generative (NANOGEN14) | defer stance · CAPCHECK closed · "
            "cite NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12·13 DEFER · "
            "not rename | **DEFER** |",
            "| Live ask battery | LOOKUP·PEAK·DECODE·ABSTAIN + "
            "BD-FOREVER FP · BA/BB/BC forever · over-refuse · near-miss · "
            "DECODE junk→ABSTAIN | **PASS** 14/14 |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:bd:report",
            "npm run nano:bd:session",
            "npm run nano:semint",
            "npm run nano:bd:fastgain",
            "npm run nano:bd:ctxgain",
            "npm run nano:nanogen14",
            "npm run nano:bd:real-eval",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave BE without "
            "lab-book reopen · sell PEAK/bank-grounded as unlabeled open-chat · "
            "sell SAFE mean as IQ · sell span-fallback as true-continue · "
            "gold-substring PROMOTE · truncate-to-span as gen IQ · "
            "BD-FOREVER semantic LOOKUP as success · over-refuse as win · "
            "NANOGEN14 = NANOGEN13+rename · bank stuffing BD-FOREVER · "
            "CTX/SMART/FAST/APP letter clones · rewrite BC/BB/BA/AZ/… locks.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_bd() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave BD (semantic anti-FP + Nano gen-defer)",
            "",
            "> Companion to [wave-bd-summary.md](wave-bd-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · "
            "Real-eval: [wave-bd-real-eval.md](wave-bd-real-eval.md) · "
            "Freeze: [bd-freeze.md](bd-freeze.md) · "
            "[formal-habdfreeze-bd-freeze.md](formal-habdfreeze-bd-freeze.md) · "
            "Parent: [bc-freeze.md](bc-freeze.md) · "
            f"Ship: **{SHIP_CLAIM}**",
            "",
            "## Question",
            "",
            "After BC froze family anti-FP + honest NANOGEN13 DEFER, "
            "can Wave BD **close semantic / wrong-bank residual FP** "
            "(BD-FOREVER FH 0 + live ask + novel) **and** hold **context** / "
            "**speed** on the prod path **and** clear a **real new method** "
            "generative lift under ≤5M **without** unlabeled open-chat / "
            "GPT-class / NANOGEN14=NANOGEN13+rename / bank stuffing?",
            "",
            "## Answer",
            "",
            "**Yes for semantic anti-FP + ctx/speed hold; honest DEFER "
            "for generative.** "
            "H-SEMINT · H-FASTGAIN · H-CTXGAIN PROMOTE. "
            "**H-NANOGEN14 DEFER** "
            "(BD0 stance=defer; CAPCHECK closed; no real M1|M2|M3; "
            "NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12·13 DEFER cited; "
            "not a rename). "
            "BD-REAL-EVAL PROMOTE (live battery 14/14; BD-FOREVER FP ABSTAIN; "
            "over-refuse LOOKUP; gen unlock locked). "
            f"Ship claim stays STRICT archive: **{SHIP_CLAIM}**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-SEMINT | BD-FOREVER FH 0 · BA/BB/BC/AZ hold · "
            "over-refuse 0 → PROMOTE |",
            "| H-FASTGAIN | Prod p50/p99 hold · anti-FP hold → PROMOTE |",
            "| H-CTXGAIN | Howto·cite·long content_ok · "
            "anti-FP hold → PROMOTE |",
            "| H-NANOGEN14 | Gen stance defer · NANOGEN6·7 HOLD · "
            "NANOGEN8·9·10·11·12·13 DEFER cited → DEFER |",
            "| BD-REAL-EVAL | Live battery 14/14 · gen locked → PROMOTE |",
            "| BD-REPORT | Summary + paper-lab + anti-FP → PROMOTE |",
            "| BD-FREEZE | Outcomes lock — no Wave BE invent |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP / BD-FOREVER probes must never be sold as generative IQ. "
            "Semantic wrong-bank LOOKUP (reverse→f-string · mul→add) is a "
            "false-hit. Exact-gold ABSTAIN is a product miss. PEAK and "
            "span-fallback stay product/extractive credit only. L_eff alone "
            "≠ ctx win. Warm-cache microbench ≠ speed win. DECODE telemetry "
            "(`wall_ms`, `n_new`) is mandatory but insufficient for "
            "content_ok. SAFE≠quality. Gold-substring / gibberish-tail / "
            "truncate-to-span ≠ generative PROMOTE. "
            "**H-NANOGEN14 DEFER** plus cited **H-NANOGEN6** / **H-NANOGEN7 "
            "HOLD** and **H-NANOGEN8** / **H-NANOGEN9** / **H-NANOGEN10** / "
            "**H-NANOGEN11** / **H-NANOGEN12** / **H-NANOGEN13 DEFER** keep "
            "true-continue / mini-AGI language locked — ship remains STRICT "
            "ablated DECODE archive, not unlabeled open chat.",
            "",
            "## Takeaway one-liner",
            "",
            "**BD = semantic BD-FOREVER anti-FP + measurable ctx/speed "
            "hold + gen DEFERs honestly (NANOGEN6·7 HOLD · "
            "NANOGEN8·9·10·11·12·13 DEFER stand; not NANOGEN13 rename); ship "
            "AF+AQ+AS trust + STRICT snippet-prefix DECODE — not unlabeled "
            "open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-bd-summary.md](wave-bd-summary.md) · "
            "[wave-bd-real-eval.md](wave-bd-real-eval.md) · "
            "[wave-bd-session.md](wave-bd-session.md) · "
            "[bc-freeze.md](bc-freeze.md)  ",
            "- Formals: SEMINT · FASTGAIN · CTXGAIN · NANOGEN14  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
