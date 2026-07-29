"""Wave BG REPORT: public closeout (BG-FOREVER anti-FP + util + honest NANOGEN17 SKIP)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from bg_session_ops import BG0_SHIP_LOCK

__all__ = [
    "BG_ID",
    "BG_THESIS",
    "BG_EVIDENCE",
    "BG_REPORT_MARKERS",
    "BG_SCOREBOARD",
    "SHIP_CLAIM",
    "decide_bg_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "realeval_section_ok",
    "render_wave_bg_summary",
    "render_paper_lab_wave_bg",
]

BG_ID = "BG-REPORT"
SHIP_CLAIM = BG0_SHIP_LOCK
BG_THESIS = (
    "Wave BG dual track: H-UNARYINT·H-SHIPPUB·H-FASTBG·H-CTXBG PROMOTE "
    "(BG-FOREVER FH 0 · Track A++ util/paper · prod p50/p99 hold · "
    "howto·cite·long content · anti-FP); H-NANOGEN17 SKIP (gen stance skip · "
    "CAPCHECK closed · no written M1|M2|M3 plan · NANOGEN6·7 HOLD · "
    "NANOGEN8…15 DEFER · NANOGEN16 SKIP cited · not empty DEFER letter · "
    "not NANOGEN16 rename); BG-REAL-EVAL PROMOTE (live battery 17/17 · "
    "BG-FOREVER FP ABSTAIN · BA…BF forever hold · over-refuse LOOKUP · "
    "utilization smoke · gen locked); ship " + SHIP_CLAIM
)

BG_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "BG0",
        "id": "SESSION",
        "metric": "packs frozen",
        "decision": "PROMOTE",
        "note": (
            "BG-FOREVER · BA…BF/AZ hold · §1 scoreboard · Track A++ · "
            "gen stance SKIP · true-eval"
        ),
    },
    {
        "stage": "BG1",
        "id": "H-UNARYINT",
        "metric": "BG-FOREVER FH 0 · live FP 0",
        "decision": "PROMOTE",
        "note": (
            "unary/transform/arity gate · BA…BF hold 0 · AZ hold 0 · "
            "over-refuse 0 · novel FP 0 · no bank stuffing"
        ),
    },
    {
        "stage": "BG2",
        "id": "H-SHIPPUB",
        "metric": "Track A++ utilization + paper",
        "decision": "PROMOTE",
        "note": (
            "operator deepen · paper/arXiv sync · H-SHIPUSE2 hold · "
            "BG residual ABSTAIN"
        ),
    },
    {
        "stage": "BG3",
        "id": "H-FASTBG",
        "metric": "prod p50/p99 no FP regress",
        "decision": "PROMOTE",
        "note": (
            "prod latency hold · anti-FP hold · ≠ BF nano:fastbf · "
            "≠ BE nano:fastbe"
        ),
    },
    {
        "stage": "BG4",
        "id": "H-CTXBG",
        "metric": "howto·cite·long content_ok",
        "decision": "PROMOTE",
        "note": (
            "content bars · BG/BF/BE/BD/BA/BB/BC/AZ anti-FP · L_eff alone ≠ win · "
            "≠ BF nano:ctxbf"
        ),
    },
    {
        "stage": "BG5",
        "id": "H-NANOGEN17",
        "metric": "gen stance SKIP stop rule",
        "decision": "SKIP",
        "note": (
            "CAPCHECK closed · no written M1|M2|M3 · NANOGEN6·7 HOLD · "
            "NANOGEN8…15 DEFER · NANOGEN16 SKIP · not empty DEFER letter · "
            "not NANOGEN16 rename"
        ),
    },
    {
        "stage": "BG6",
        "id": "BG-REAL-EVAL",
        "metric": "live ask battery 17/17",
        "decision": "PROMOTE",
        "note": (
            "product+util+ctx+speed pass · BG-FOREVER ABSTAIN · "
            "over-refuse LOOKUP · util smoke · gen locked · prod=eval"
        ),
    },
    {
        "stage": "BG7",
        "id": "BG-REPORT",
        "metric": "summary + paper-lab",
        "decision": "PROMOTE",
        "note": (
            "docs + anti-FP · util · BG5 SKIP · NANOGEN6/7 HOLD · "
            "NANOGEN8…15 DEFER · NANOGEN16 SKIP · NANOGEN17 SKIP cited"
        ),
    },
    {
        "stage": "BG8",
        "id": "BG-FREEZE",
        "metric": "lock outcomes",
        "decision": "PROMOTE",
        "note": "COMPLETE+FROZEN · no Wave BH invent",
    },
)

BG_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-bg-session.md",
    "docs/results/nano-lm/formal-hunaryint-unaryint.md",
    "docs/results/nano-lm/formal-hshippub-shippub.md",
    "docs/results/nano-lm/formal-hfastbg-fastbg.md",
    "docs/results/nano-lm/formal-hctxbg-ctxbg.md",
    "docs/results/nano-lm/formal-hnanogen17-nanogen17.md",
    "docs/results/nano-lm/wave-bg-real-eval.md",
    "docs/results/nano-lm/wave-bg-summary.md",
    "docs/results/nano-lm/paper-lab-wave-bg.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

BG_REPORT_MARKERS: tuple[str, ...] = (
    "H-UNARYINT",
    "H-SHIPPUB",
    "H-FASTBG",
    "H-CTXBG",
    "H-NANOGEN17",
    "H-NANOGEN16",
    "H-NANOGEN15",
    "H-NANOGEN14",
    "H-NANOGEN13",
    "H-NANOGEN12",
    "H-NANOGEN11",
    "H-NANOGEN10",
    "H-NANOGEN9",
    "H-NANOGEN8",
    "H-NANOGEN6",
    "H-NANOGEN7",
    "BG-REAL-EVAL",
    "BG-FOREVER",
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
    "anti-FP",
    "forever",
    "PROMOTE",
    "SKIP",
    "DEFER",
    "HOLD",
    "true_continue",
    "span-fallback",
    "over-refuse",
    "utilization",
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
    "NANOGEN14",
    "NANOGEN15",
    "NANOGEN16",
    "NANOGEN17",
)


def decide_bg_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = BG_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for BG report evidence
    WHEN deciding BG-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({BG_ID}: {BG_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = BG_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = BG_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking BG scoreboard
    THEN every stage id appears with Metric column.
    """
    body = str(text)
    if "Metric" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid.startswith("BG-"):
            if f"**{mid}**" not in body:
                return False
    return True


def antifp_section_ok(text: str) -> bool:
    """
    GIVEN summary body
    WHEN checking anti-FP evidence block
    THEN require modes + LOOKUP≠IQ + BG-FOREVER + NANOGEN6–17 honesty.
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
        "H-NANOGEN17",
        "H-NANOGEN16",
        "H-NANOGEN15",
        "H-NANOGEN14",
        "H-NANOGEN13",
        "H-NANOGEN12",
        "H-NANOGEN11",
        "H-NANOGEN10",
        "H-NANOGEN9",
        "H-NANOGEN8",
        "H-NANOGEN6",
        "H-NANOGEN7",
        "BG-FOREVER",
        "span-fallback",
        "true_continue",
        "forever",
        "over-refuse",
        "utilization",
        "SAFE",
        "unlabeled open chat",
        "SKIP",
    )
    return all(m in body for m in need)


def realeval_section_ok(text: str) -> bool:
    """Require explicit real-eval section with battery + gen lock honesty."""
    body = str(text).lower()
    return (
        "real-eval" in body
        and "battery" in body
        and "nanogen17" in body
        and "unaryint" in body
        and "shippub" in body
        and "fastbg" in body
        and "ctxbg" in body
        and "span-fallback" in body
        and "skip" in body
        and "nanogen6" in body
        and "nanogen7" in body
        and "nanogen8" in body
        and "nanogen16" in body
        and "bg-forever" in body
        and "over-refuse" in body
        and "utilization" in body
    )


def render_wave_bg_summary() -> str:
    lines = [
        "# Wave BG — unary/transform anti-FP + util + Nano gen-SKIP honesty "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §9 · Paper-lab: "
        "[paper-lab-wave-bg.md](paper-lab-wave-bg.md) · "
        "Real-eval: [wave-bg-real-eval.md](wave-bg-real-eval.md) · "
        "Freeze: [bg-freeze.md](bg-freeze.md) · "
        "[formal-habgfreeze-bg-freeze.md](formal-habgfreeze-bg-freeze.md)  ",
        "> Parent: Wave BF **BF-FREEZE** · Ship claim: "
        f"**{SHIP_CLAIM}**",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + BG_THESIS
        + ".**",
        "",
        "## Stage scoreboard (product + generative)",
        "",
        "| # | ID | Metric | Decision | Note |",
        "|---|-----|--------|----------|------|",
    ]
    for row in BG_SCOREBOARD:
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
            "H-UNARYINT · BG-REAL-EVAL known_lookup · WRAP_LOOKUP |",
            "| PEAK extractive ≠ open-chat | "
            "BG-REAL-EVAL PEAK · H-CTXBG usable span |",
            "| DECODE arm `wall_ms>0` · `n_new>0` | "
            "BG-ASK-05 DECODE path · junk law |",
            "| DECODE gibberish ≠ content_ok | "
            "BG-ASK-06 junk→ABSTAIN |",
            "| BG-FOREVER unary/transform LOOKUP = false-hit | "
            "H-UNARYINT BG-FOREVER FH 0 · BG-ASK-07/16 ABSTAIN |",
            "| Exact-gold ABSTAIN = product miss | "
            "H-UNARYINT over-refuse 0 · BG-ASK-08 LOOKUP |",
            "| ABSTAIN refuse junk / OOD / near-miss / forever | "
            "BG-REAL-EVAL OOD·junk·near-miss·BG-FOREVER·BA hold·BB hold·"
            "BC hold·BD hold·BE hold·BF hold·AZ hold · FH 0 |",
            "| Utilization smoke LOOKUP | "
            "H-SHIPPUB Track A++ · BG-ASK-17 utilization |",
            "| SAFE ≠ answer quality | "
            "H-UNARYINT cites SAFE≠quality |",
            "| True-gen SKIP / DEFER honesty | "
            "**H-NANOGEN17** SKIP · **H-NANOGEN16** SKIP · "
            "**H-NANOGEN15** DEFER · **H-NANOGEN14** DEFER · "
            "**H-NANOGEN13** DEFER · **H-NANOGEN12** DEFER · "
            "**H-NANOGEN11** DEFER · **H-NANOGEN10** DEFER · "
            "**H-NANOGEN9** DEFER · **H-NANOGEN8** DEFER · "
            "**H-NANOGEN6** HOLD · **H-NANOGEN7** HOLD · true_continue unmet · "
            "span-fallback ≠ gen IQ · not unlabeled open chat |",
            "| Modes always visible + content bars | "
            "**H-CTXBG** · **BG-REAL-EVAL** LOOKUP·PEAK·DECODE·ABSTAIN |",
            "| Speed without FP regress | "
            "**H-FASTBG** prod p50/p99 · anti-FP hold |",
            "| Generative claim gated | "
            "BG-REAL-EVAL · unlock only if BG5 PROMOTE |",
            "| Telemetry keys | `mode` · `wall_ms` · `n_new` · "
            "`product_mode` |",
            "",
            "## Honest claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| BG-FOREVER anti-FP scoreboard | **H-UNARYINT** PROMOTE |",
            "| Track A++ utilization + paper | **H-SHIPPUB** PROMOTE |",
            "| Prod speed p50/p99 hold | **H-FASTBG** PROMOTE |",
            "| Ctx howto·cite·long content | **H-CTXBG** PROMOTE |",
            "| North-star generative | **H-NANOGEN17** SKIP — "
            "stance skip · CAPCHECK closed · no written plan · "
            "NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · NANOGEN16 SKIP stand · "
            "not empty DEFER letter · not rename |",
            "| Parent gen HOLDs / DEFER / SKIP cited | **H-NANOGEN6** HOLD · "
            "**H-NANOGEN7** HOLD · **H-NANOGEN8** DEFER · "
            "**H-NANOGEN9** DEFER · **H-NANOGEN10** DEFER · "
            "**H-NANOGEN11** DEFER · **H-NANOGEN12** DEFER · "
            "**H-NANOGEN13** DEFER · **H-NANOGEN14** DEFER · "
            "**H-NANOGEN15** DEFER · **H-NANOGEN16** SKIP |",
            "| Final real eval | **BG-REAL-EVAL** PROMOTE — "
            "battery **17/17** · BG-FOREVER ABSTAIN · over-refuse LOOKUP · "
            "utilization · gen locked |",
            "| Ship claim | **" + SHIP_CLAIM + "** |",
            "| “Unlabeled open chat / GPT-class ≤5M” | **False** |",
            "| “TAC / true-continue unlocked” | **False** (BG5 SKIP) |",
            "| “Mini-AGI unlocked” | **False** (BG5 SKIP) |",
            "",
            "## Real-eval section",
            "",
            "| Arm | What was measured | Outcome |",
            "|-----|-------------------|---------|",
            "| Product (UNARYINT) | BG-FOREVER FH 0 · BA…BF/AZ hold · "
            "over-refuse 0 · live FP 0 | **PROMOTE** |",
            "| Utilization (SHIPPUB) | operator · paper/arXiv sync · "
            "H-SHIPUSE2 hold | **PROMOTE** |",
            "| Speed (FASTBG) | prod p50/p99 · anti-FP hold | "
            "**PROMOTE** |",
            "| Context (CTXBG) | howto·cite·long content_ok · "
            "anti-FP hold | **PROMOTE** |",
            "| Generative (NANOGEN17) | skip stance · CAPCHECK closed · "
            "cite NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · NANOGEN16 SKIP · "
            "not empty DEFER · not rename | **SKIP** |",
            "| Live ask battery | LOOKUP·PEAK·DECODE·ABSTAIN + "
            "BG-FOREVER FP · BA…BF forever · over-refuse · utilization · "
            "near-miss · DECODE junk→ABSTAIN | **PASS** 17/17 |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:bg:report",
            "npm run nano:bg:session",
            "npm run nano:unaryint",
            "npm run nano:shippub",
            "npm run nano:fastbg",
            "npm run nano:ctxbg",
            "npm run nano:nanogen17",
            "npm run nano:bg:real-eval",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave BH without "
            "lab-book reopen · sell PEAK/bank-grounded as unlabeled open-chat · "
            "sell SAFE mean as IQ · sell span-fallback as true-continue · "
            "gold-substring PROMOTE · truncate-to-span as gen IQ · "
            "BG-FOREVER unary/transform LOOKUP as success · over-refuse as win · "
            "NANOGEN17 = NANOGEN16+rename · empty DEFER letter · "
            "bank stuffing BG-FOREVER · CTX/SMART/FAST/APP letter clones · "
            "rewrite BF/BE/BD/BC/BB/BA/AZ locks.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_bg() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave BG (unary/transform anti-FP + util + Nano gen-SKIP)",
            "",
            "> Companion to [wave-bg-summary.md](wave-bg-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · "
            "Real-eval: [wave-bg-real-eval.md](wave-bg-real-eval.md) · "
            "Freeze: [bg-freeze.md](bg-freeze.md) · "
            "[formal-habgfreeze-bg-freeze.md](formal-habgfreeze-bg-freeze.md) · "
            "Parent: [bf-freeze.md](bf-freeze.md) · "
            f"Ship: **{SHIP_CLAIM}**",
            "",
            "## Question",
            "",
            "After BF froze predicate anti-FP + honest NANOGEN16 SKIP, "
            "can Wave BG **close unary/math/string-transform residual FP** "
            "(BG-FOREVER FH 0 + novel) **and** publish/utilize the proven "
            "stack (Track A++ / paper path) **and** hold **context** / "
            "**speed** on the prod path **and** clear a **written M1|M2|M3** "
            "generative lift under ≤5M **without** unlabeled open-chat / "
            "GPT-class / NANOGEN17=NANOGEN16+rename / empty DEFER letter / "
            "bank stuffing?",
            "",
            "## Answer",
            "",
            "**Yes for unary/transform anti-FP + util/paper deepen + "
            "ctx/speed hold; honest SKIP for generative (stop rule).** "
            "H-UNARYINT · H-SHIPPUB · H-FASTBG · H-CTXBG PROMOTE. "
            "**H-NANOGEN17 SKIP** "
            "(BG0 stance=skip; CAPCHECK closed; no written M1|M2|M3 plan; "
            "NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · NANOGEN16 SKIP cited; "
            "not empty DEFER letter; not a rename; stop rule). "
            "BG-REAL-EVAL PROMOTE (live battery 17/17; BG-FOREVER FP ABSTAIN; "
            "over-refuse LOOKUP; utilization smoke; gen unlock locked). "
            f"Ship claim stays STRICT archive: **{SHIP_CLAIM}**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-UNARYINT | BG-FOREVER FH 0 · BA…BF/AZ hold · "
            "over-refuse 0 → PROMOTE |",
            "| H-SHIPPUB | Track A++ deepen · paper sync · "
            "H-SHIPUSE2 hold → PROMOTE |",
            "| H-FASTBG | Prod p50/p99 hold · anti-FP hold → PROMOTE |",
            "| H-CTXBG | Howto·cite·long content_ok · "
            "anti-FP hold → PROMOTE |",
            "| H-NANOGEN17 | Gen stance SKIP · NANOGEN6·7 HOLD · "
            "NANOGEN8…15 DEFER · NANOGEN16 SKIP cited → SKIP |",
            "| BG-REAL-EVAL | Live battery 17/17 · gen locked → PROMOTE |",
            "| BG-REPORT | Summary + paper-lab + anti-FP · util → PROMOTE |",
            "| BG-FREEZE | Outcomes lock — no Wave BH invent |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP / BG-FOREVER probes must never be sold as generative IQ. "
            "Unary/math wrong LOOKUP (abs→add, factorial→add) and "
            "string-transform wrong LOOKUP (upper→f-string) are false-hits. "
            "Exact-gold ABSTAIN is a product miss. PEAK and "
            "span-fallback stay product/extractive credit only. L_eff alone "
            "≠ ctx win. Warm-cache microbench ≠ speed win. DECODE telemetry "
            "(`wall_ms`, `n_new`) is mandatory but insufficient for "
            "content_ok. SAFE≠quality. Utilization is ship-surface, not IQ. "
            "Gold-substring / gibberish-tail / "
            "truncate-to-span ≠ generative PROMOTE. "
            "**H-NANOGEN17 SKIP** plus cited **H-NANOGEN6** / **H-NANOGEN7 "
            "HOLD**, **H-NANOGEN8**…**H-NANOGEN15 DEFER**, and "
            "**H-NANOGEN16 SKIP** keep true-continue / mini-AGI language "
            "locked — ship remains STRICT ablated DECODE archive, not "
            "unlabeled open chat.",
            "",
            "## Takeaway one-liner",
            "",
            "**BG = unary/transform BG-FOREVER anti-FP + Track A++ "
            "utilization/paper + measurable ctx/speed hold + gen SKIP "
            "honestly (NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · NANOGEN16 SKIP · "
            "NANOGEN17 SKIP stand; not NANOGEN16 rename; not empty DEFER "
            "letter); ship AF+AQ+AS trust + STRICT snippet-prefix DECODE — "
            "not unlabeled open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-bg-summary.md](wave-bg-summary.md) · "
            "[wave-bg-real-eval.md](wave-bg-real-eval.md) · "
            "[wave-bg-session.md](wave-bg-session.md) · "
            "[bf-freeze.md](bf-freeze.md)  ",
            "- Formals: UNARYINT · SHIPPUB · FASTBG · CTXBG · NANOGEN17  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
