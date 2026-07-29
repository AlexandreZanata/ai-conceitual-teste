"""Wave BF REPORT: public closeout (BF-FOREVER anti-FP + util + honest NANOGEN16 SKIP)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from bf_session_ops import BF0_SHIP_LOCK

__all__ = [
    "BF_ID",
    "BF_THESIS",
    "BF_EVIDENCE",
    "BF_REPORT_MARKERS",
    "BF_SCOREBOARD",
    "SHIP_CLAIM",
    "decide_bf_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "realeval_section_ok",
    "render_wave_bf_summary",
    "render_paper_lab_wave_bf",
]

BF_ID = "BF-REPORT"
SHIP_CLAIM = BF0_SHIP_LOCK
BF_THESIS = (
    "Wave BF dual track: H-PREDINT·H-SHIPUSE2·H-FASTBF·H-CTXBF PROMOTE "
    "(BF-FOREVER FH 0 · Track A+ util · prod p50/p99 hold · howto·cite·long "
    "content · anti-FP); H-NANOGEN16 SKIP (gen stance skip · CAPCHECK "
    "closed · no written M1|M2|M3 plan · NANOGEN6·7 HOLD · NANOGEN8…15 DEFER "
    "cited · not empty DEFER letter · not NANOGEN15 rename); BF-REAL-EVAL "
    "PROMOTE (live battery 16/16 · BF-FOREVER FP ABSTAIN · BA…BE forever "
    "hold · over-refuse LOOKUP · utilization smoke · gen locked); ship "
    + SHIP_CLAIM
)

BF_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "BF0",
        "id": "SESSION",
        "metric": "packs frozen",
        "decision": "PROMOTE",
        "note": (
            "BF-FOREVER · BA…BE/AZ hold · §1 scoreboard · Track A+ · "
            "gen stance SKIP · true-eval"
        ),
    },
    {
        "stage": "BF1",
        "id": "H-PREDINT",
        "metric": "BF-FOREVER FH 0 · live FP 0",
        "decision": "PROMOTE",
        "note": (
            "predicate/schema gate · BA…BE hold 0 · AZ hold 0 · "
            "over-refuse 0 · novel FP 0 · no bank stuffing"
        ),
    },
    {
        "stage": "BF2",
        "id": "H-SHIPUSE2",
        "metric": "Track A+ utilization",
        "decision": "PROMOTE",
        "note": (
            "operator deepen · paper claim sync · H-SHIPUSE hold · "
            "BF residual ABSTAIN"
        ),
    },
    {
        "stage": "BF3",
        "id": "H-FASTBF",
        "metric": "prod p50/p99 no FP regress",
        "decision": "PROMOTE",
        "note": (
            "prod latency hold · anti-FP hold · ≠ BE nano:fastbe · "
            "≠ BD nano:bd:fastgain"
        ),
    },
    {
        "stage": "BF4",
        "id": "H-CTXBF",
        "metric": "howto·cite·long content_ok",
        "decision": "PROMOTE",
        "note": (
            "content bars · BF/BE/BD/BA/BB/BC/AZ anti-FP · L_eff alone ≠ win · "
            "≠ BE nano:ctxbe"
        ),
    },
    {
        "stage": "BF5",
        "id": "H-NANOGEN16",
        "metric": "gen stance SKIP stop rule",
        "decision": "SKIP",
        "note": (
            "CAPCHECK closed · no written M1|M2|M3 · NANOGEN6·7 HOLD · "
            "NANOGEN8…15 DEFER · not empty DEFER letter · not NANOGEN15 rename"
        ),
    },
    {
        "stage": "BF6",
        "id": "BF-REAL-EVAL",
        "metric": "live ask battery 16/16",
        "decision": "PROMOTE",
        "note": (
            "product+util+ctx+speed pass · BF-FOREVER ABSTAIN · "
            "over-refuse LOOKUP · util smoke · gen locked · prod=eval"
        ),
    },
    {
        "stage": "BF7",
        "id": "BF-REPORT",
        "metric": "summary + paper-lab",
        "decision": "PROMOTE",
        "note": (
            "docs + anti-FP · util · BF5 SKIP · NANOGEN6/7 HOLD · "
            "NANOGEN8…15 DEFER · NANOGEN16 SKIP cited"
        ),
    },
    {
        "stage": "BF8",
        "id": "BF-FREEZE",
        "metric": "lock outcomes",
        "decision": "PROMOTE",
        "note": "COMPLETE+FROZEN · no Wave BG invent",
    },
)

BF_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-bf-session.md",
    "docs/results/nano-lm/formal-hpredint-predint.md",
    "docs/results/nano-lm/formal-hshipuse2-shipuse2.md",
    "docs/results/nano-lm/formal-hfastbf-fastbf.md",
    "docs/results/nano-lm/formal-hctxbf-ctxbf.md",
    "docs/results/nano-lm/formal-hnanogen16-nanogen16.md",
    "docs/results/nano-lm/wave-bf-real-eval.md",
    "docs/results/nano-lm/wave-bf-summary.md",
    "docs/results/nano-lm/paper-lab-wave-bf.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

BF_REPORT_MARKERS: tuple[str, ...] = (
    "H-PREDINT",
    "H-SHIPUSE2",
    "H-FASTBF",
    "H-CTXBF",
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
    "BF-REAL-EVAL",
    "BF-FOREVER",
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
)


def decide_bf_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = BF_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for BF report evidence
    WHEN deciding BF-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({BF_ID}: {BF_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = BF_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = BF_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking BF scoreboard
    THEN every stage id appears with Metric column.
    """
    body = str(text)
    if "Metric" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid.startswith("BF-"):
            if f"**{mid}**" not in body:
                return False
    return True


def antifp_section_ok(text: str) -> bool:
    """
    GIVEN summary body
    WHEN checking anti-FP evidence block
    THEN require modes + LOOKUP≠IQ + BF-FOREVER + NANOGEN6–16 honesty.
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
        "BF-FOREVER",
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
        and "nanogen16" in body
        and "predint" in body
        and "shipuse2" in body
        and "fastbf" in body
        and "ctxbf" in body
        and "span-fallback" in body
        and "skip" in body
        and "nanogen6" in body
        and "nanogen7" in body
        and "nanogen8" in body
        and "nanogen15" in body
        and "bf-forever" in body
        and "over-refuse" in body
        and "utilization" in body
    )


def render_wave_bf_summary() -> str:
    lines = [
        "# Wave BF — predicate anti-FP + util + Nano gen-SKIP honesty "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §9 · Paper-lab: "
        "[paper-lab-wave-bf.md](paper-lab-wave-bf.md) · "
        "Real-eval: [wave-bf-real-eval.md](wave-bf-real-eval.md) · "
        "Freeze: [bf-freeze.md](bf-freeze.md) · "
        "[formal-habffreeze-bf-freeze.md](formal-habffreeze-bf-freeze.md)  ",
        "> Parent: Wave BE **BE-FREEZE** · Ship claim: "
        f"**{SHIP_CLAIM}**",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + BF_THESIS
        + ".**",
        "",
        "## Stage scoreboard (product + generative)",
        "",
        "| # | ID | Metric | Decision | Note |",
        "|---|-----|--------|----------|------|",
    ]
    for row in BF_SCOREBOARD:
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
            "H-PREDINT · BF-REAL-EVAL known_lookup · WRAP_LOOKUP |",
            "| PEAK extractive ≠ open-chat | "
            "BF-REAL-EVAL PEAK · H-CTXBF usable span |",
            "| DECODE arm `wall_ms>0` · `n_new>0` | "
            "BF-ASK-05 DECODE path · junk law |",
            "| DECODE gibberish ≠ content_ok | "
            "BF-ASK-06 junk→ABSTAIN |",
            "| BF-FOREVER predicate LOOKUP = false-hit | "
            "H-PREDINT BF-FOREVER FH 0 · BF-ASK-07/15 ABSTAIN |",
            "| Exact-gold ABSTAIN = product miss | "
            "H-PREDINT over-refuse 0 · BF-ASK-08 LOOKUP |",
            "| ABSTAIN refuse junk / OOD / near-miss / forever | "
            "BF-REAL-EVAL OOD·junk·near-miss·BF-FOREVER·BA hold·BB hold·"
            "BC hold·BD hold·BE hold·AZ hold · FH 0 |",
            "| Utilization smoke LOOKUP | "
            "H-SHIPUSE2 Track A+ · BF-ASK-16 utilization |",
            "| SAFE ≠ answer quality | "
            "H-PREDINT cites SAFE≠quality |",
            "| True-gen SKIP / DEFER honesty | "
            "**H-NANOGEN16** SKIP · **H-NANOGEN15** DEFER · "
            "**H-NANOGEN14** DEFER · **H-NANOGEN13** DEFER · "
            "**H-NANOGEN12** DEFER · **H-NANOGEN11** DEFER · "
            "**H-NANOGEN10** DEFER · **H-NANOGEN9** DEFER · "
            "**H-NANOGEN8** DEFER · **H-NANOGEN6** HOLD · "
            "**H-NANOGEN7** HOLD · true_continue unmet · "
            "span-fallback ≠ gen IQ · not unlabeled open chat |",
            "| Modes always visible + content bars | "
            "**H-CTXBF** · **BF-REAL-EVAL** LOOKUP·PEAK·DECODE·ABSTAIN |",
            "| Speed without FP regress | "
            "**H-FASTBF** prod p50/p99 · anti-FP hold |",
            "| Generative claim gated | "
            "BF-REAL-EVAL · unlock only if BF5 PROMOTE |",
            "| Telemetry keys | `mode` · `wall_ms` · `n_new` · "
            "`product_mode` |",
            "",
            "## Honest claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| BF-FOREVER anti-FP scoreboard | **H-PREDINT** PROMOTE |",
            "| Track A+ utilization | **H-SHIPUSE2** PROMOTE |",
            "| Prod speed p50/p99 hold | **H-FASTBF** PROMOTE |",
            "| Ctx howto·cite·long content | **H-CTXBF** PROMOTE |",
            "| North-star generative | **H-NANOGEN16** SKIP — "
            "stance skip · CAPCHECK closed · no written plan · "
            "NANOGEN6·7 HOLD · NANOGEN8…15 DEFER stand · "
            "not empty DEFER letter · not rename |",
            "| Parent gen HOLDs / DEFER cited | **H-NANOGEN6** HOLD · "
            "**H-NANOGEN7** HOLD · **H-NANOGEN8** DEFER · "
            "**H-NANOGEN9** DEFER · **H-NANOGEN10** DEFER · "
            "**H-NANOGEN11** DEFER · **H-NANOGEN12** DEFER · "
            "**H-NANOGEN13** DEFER · **H-NANOGEN14** DEFER · "
            "**H-NANOGEN15** DEFER |",
            "| Final real eval | **BF-REAL-EVAL** PROMOTE — "
            "battery **16/16** · BF-FOREVER ABSTAIN · over-refuse LOOKUP · "
            "utilization · gen locked |",
            "| Ship claim | **" + SHIP_CLAIM + "** |",
            "| “Unlabeled open chat / GPT-class ≤5M” | **False** |",
            "| “TAC / true-continue unlocked” | **False** (BF5 SKIP) |",
            "| “Mini-AGI unlocked” | **False** (BF5 SKIP) |",
            "",
            "## Real-eval section",
            "",
            "| Arm | What was measured | Outcome |",
            "|-----|-------------------|---------|",
            "| Product (PREDINT) | BF-FOREVER FH 0 · BA…BE/AZ hold · "
            "over-refuse 0 · live FP 0 | **PROMOTE** |",
            "| Utilization (SHIPUSE2) | operator · paper sync · "
            "H-SHIPUSE hold | **PROMOTE** |",
            "| Speed (FASTBF) | prod p50/p99 · anti-FP hold | "
            "**PROMOTE** |",
            "| Context (CTXBF) | howto·cite·long content_ok · "
            "anti-FP hold | **PROMOTE** |",
            "| Generative (NANOGEN16) | skip stance · CAPCHECK closed · "
            "cite NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · "
            "not empty DEFER · not rename | **SKIP** |",
            "| Live ask battery | LOOKUP·PEAK·DECODE·ABSTAIN + "
            "BF-FOREVER FP · BA…BE forever · over-refuse · utilization · "
            "near-miss · DECODE junk→ABSTAIN | **PASS** 16/16 |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:bf:report",
            "npm run nano:bf:session",
            "npm run nano:predint",
            "npm run nano:shipuse2",
            "npm run nano:fastbf",
            "npm run nano:ctxbf",
            "npm run nano:nanogen16",
            "npm run nano:bf:real-eval",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave BG without "
            "lab-book reopen · sell PEAK/bank-grounded as unlabeled open-chat · "
            "sell SAFE mean as IQ · sell span-fallback as true-continue · "
            "gold-substring PROMOTE · truncate-to-span as gen IQ · "
            "BF-FOREVER predicate LOOKUP as success · over-refuse as win · "
            "NANOGEN16 = NANOGEN15+rename · empty DEFER letter · "
            "bank stuffing BF-FOREVER · CTX/SMART/FAST/APP letter clones · "
            "rewrite BE/BD/BC/BB/BA/AZ locks.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_bf() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave BF (predicate anti-FP + util + Nano gen-SKIP)",
            "",
            "> Companion to [wave-bf-summary.md](wave-bf-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · "
            "Real-eval: [wave-bf-real-eval.md](wave-bf-real-eval.md) · "
            "Freeze: [bf-freeze.md](bf-freeze.md) · "
            "[formal-habffreeze-bf-freeze.md](formal-habffreeze-bf-freeze.md) · "
            "Parent: [be-freeze.md](be-freeze.md) · "
            f"Ship: **{SHIP_CLAIM}**",
            "",
            "## Question",
            "",
            "After BE froze compositional anti-FP + honest NANOGEN15 DEFER, "
            "can Wave BF **close predicate/boolean residual FP** "
            "(BF-FOREVER FH 0 + novel) **and** deepen ship/utilize the proven "
            "stack **and** hold **context** / **speed** on the prod path "
            "**and** clear a **written M1|M2|M3** generative lift under ≤5M "
            "**without** unlabeled open-chat / GPT-class / "
            "NANOGEN16=NANOGEN15+rename / empty DEFER letter / bank stuffing?",
            "",
            "## Answer",
            "",
            "**Yes for predicate anti-FP + util deepen + ctx/speed hold; "
            "honest SKIP for generative (stop rule).** "
            "H-PREDINT · H-SHIPUSE2 · H-FASTBF · H-CTXBF PROMOTE. "
            "**H-NANOGEN16 SKIP** "
            "(BF0 stance=skip; CAPCHECK closed; no written M1|M2|M3 plan; "
            "NANOGEN6·7 HOLD · NANOGEN8…15 DEFER cited; not empty DEFER "
            "letter; not a rename; stop rule). "
            "BF-REAL-EVAL PROMOTE (live battery 16/16; BF-FOREVER FP ABSTAIN; "
            "over-refuse LOOKUP; utilization smoke; gen unlock locked). "
            f"Ship claim stays STRICT archive: **{SHIP_CLAIM}**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-PREDINT | BF-FOREVER FH 0 · BA…BE/AZ hold · "
            "over-refuse 0 → PROMOTE |",
            "| H-SHIPUSE2 | Track A+ deepen · H-SHIPUSE hold → PROMOTE |",
            "| H-FASTBF | Prod p50/p99 hold · anti-FP hold → PROMOTE |",
            "| H-CTXBF | Howto·cite·long content_ok · "
            "anti-FP hold → PROMOTE |",
            "| H-NANOGEN16 | Gen stance SKIP · NANOGEN6·7 HOLD · "
            "NANOGEN8…15 DEFER cited → SKIP |",
            "| BF-REAL-EVAL | Live battery 16/16 · gen locked → PROMOTE |",
            "| BF-REPORT | Summary + paper-lab + anti-FP · util → PROMOTE |",
            "| BF-FREEZE | Outcomes lock — no Wave BG invent |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP / BF-FOREVER probes must never be sold as generative IQ. "
            "Predicate/boolean wrong LOOKUP (even→add) is a false-hit. "
            "Exact-gold ABSTAIN is a product miss. PEAK and "
            "span-fallback stay product/extractive credit only. L_eff alone "
            "≠ ctx win. Warm-cache microbench ≠ speed win. DECODE telemetry "
            "(`wall_ms`, `n_new`) is mandatory but insufficient for "
            "content_ok. SAFE≠quality. Utilization is ship-surface, not IQ. "
            "Gold-substring / gibberish-tail / "
            "truncate-to-span ≠ generative PROMOTE. "
            "**H-NANOGEN16 SKIP** plus cited **H-NANOGEN6** / **H-NANOGEN7 "
            "HOLD** and **H-NANOGEN8**…**H-NANOGEN15 DEFER** keep "
            "true-continue / mini-AGI language locked — ship remains STRICT "
            "ablated DECODE archive, not unlabeled open chat.",
            "",
            "## Takeaway one-liner",
            "",
            "**BF = predicate BF-FOREVER anti-FP + Track A+ utilization + "
            "measurable ctx/speed hold + gen SKIP honestly "
            "(NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · NANOGEN16 SKIP stand; "
            "not NANOGEN15 rename; not empty DEFER letter); "
            "ship AF+AQ+AS trust + STRICT snippet-prefix DECODE — not unlabeled "
            "open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-bf-summary.md](wave-bf-summary.md) · "
            "[wave-bf-real-eval.md](wave-bf-real-eval.md) · "
            "[wave-bf-session.md](wave-bf-session.md) · "
            "[be-freeze.md](be-freeze.md)  ",
            "- Formals: PREDINT · SHIPUSE2 · FASTBF · CTXBF · NANOGEN16  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
