"""Wave BE REPORT: public closeout (BE-FOREVER anti-FP + util + honest NANOGEN15 DEFER)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from be_session_ops import BE0_SHIP_LOCK

__all__ = [
    "BE_ID",
    "BE_THESIS",
    "BE_EVIDENCE",
    "BE_REPORT_MARKERS",
    "BE_SCOREBOARD",
    "SHIP_CLAIM",
    "decide_be_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "realeval_section_ok",
    "render_wave_be_summary",
    "render_paper_lab_wave_be",
]

BE_ID = "BE-REPORT"
SHIP_CLAIM = BE0_SHIP_LOCK
BE_THESIS = (
    "Wave BE dual track: H-COMPINT·H-SHIPUSE·H-FASTBE·H-CTXBE PROMOTE "
    "(BE-FOREVER FH 0 · Track A util · prod p50/p99 hold · howto·cite·long "
    "content · anti-FP); H-NANOGEN15 DEFER once (gen stance defer · CAPCHECK "
    "closed · NANOGEN6·7 HOLD · NANOGEN8…14 DEFER cited · not NANOGEN14 "
    "rename); BE-REAL-EVAL PROMOTE (live battery 15/15 · BE-FOREVER FP "
    "ABSTAIN · BA…BD forever hold · over-refuse LOOKUP · utilization smoke · "
    "gen locked); ship " + SHIP_CLAIM
)

BE_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "BE0",
        "id": "SESSION",
        "metric": "packs frozen",
        "decision": "PROMOTE",
        "note": (
            "BE-FOREVER · BA…BD/AZ hold · §1 scoreboard · Track A · "
            "gen stance defer once · true-eval"
        ),
    },
    {
        "stage": "BE1",
        "id": "H-COMPINT",
        "metric": "BE-FOREVER FH 0 · live FP 0",
        "decision": "PROMOTE",
        "note": (
            "type/schema compositional gate · BA…BD hold 0 · AZ hold 0 · "
            "over-refuse 0 · novel FP 0 · no bank stuffing"
        ),
    },
    {
        "stage": "BE2",
        "id": "H-SHIPUSE",
        "metric": "Track A utilization",
        "decision": "PROMOTE",
        "note": (
            "demo smoke · operator card · paper claim sync · "
            "BE residual ABSTAIN"
        ),
    },
    {
        "stage": "BE3",
        "id": "H-FASTBE",
        "metric": "prod p50/p99 no FP regress",
        "decision": "PROMOTE",
        "note": (
            "prod latency hold · anti-FP hold · ≠ BD nano:bd:fastgain · "
            "≠ AH nano:fastlift"
        ),
    },
    {
        "stage": "BE4",
        "id": "H-CTXBE",
        "metric": "howto·cite·long content_ok",
        "decision": "PROMOTE",
        "note": (
            "content bars · BE/BD/BA/BB/BC/AZ anti-FP · L_eff alone ≠ win · "
            "≠ BD nano:bd:ctxgain"
        ),
    },
    {
        "stage": "BE5",
        "id": "H-NANOGEN15",
        "metric": "gen stance defer once",
        "decision": "DEFER",
        "note": (
            "CAPCHECK closed · no real M1|M2|M3 · NANOGEN6·7 HOLD · "
            "NANOGEN8…14 DEFER · not NANOGEN14 rename · stop rule"
        ),
    },
    {
        "stage": "BE6",
        "id": "BE-REAL-EVAL",
        "metric": "live ask battery 15/15",
        "decision": "PROMOTE",
        "note": (
            "product+util+ctx+speed pass · BE-FOREVER ABSTAIN · "
            "over-refuse LOOKUP · util smoke · gen locked · prod=eval"
        ),
    },
    {
        "stage": "BE7",
        "id": "BE-REPORT",
        "metric": "summary + paper-lab",
        "decision": "PROMOTE",
        "note": (
            "docs + anti-FP · util · BE5 DEFER · NANOGEN6/7 HOLD · "
            "NANOGEN8…15 DEFER cited"
        ),
    },
    {
        "stage": "BE8",
        "id": "BE-FREEZE",
        "metric": "lock outcomes",
        "decision": "PROMOTE",
        "note": "COMPLETE+FROZEN · no Wave BF invent",
    },
)

BE_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-be-session.md",
    "docs/results/nano-lm/formal-hcompint-compint.md",
    "docs/results/nano-lm/formal-hshipuse-shipuse.md",
    "docs/results/nano-lm/formal-hfastbe-fastbe.md",
    "docs/results/nano-lm/formal-hctxbe-ctxbe.md",
    "docs/results/nano-lm/formal-hnanogen15-nanogen15.md",
    "docs/results/nano-lm/wave-be-real-eval.md",
    "docs/results/nano-lm/wave-be-summary.md",
    "docs/results/nano-lm/paper-lab-wave-be.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

BE_REPORT_MARKERS: tuple[str, ...] = (
    "H-COMPINT",
    "H-SHIPUSE",
    "H-FASTBE",
    "H-CTXBE",
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
    "BE-REAL-EVAL",
    "BE-FOREVER",
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
)


def decide_be_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = BE_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for BE report evidence
    WHEN deciding BE-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({BE_ID}: {BE_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = BE_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = BE_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking BE scoreboard
    THEN every stage id appears with Metric column.
    """
    body = str(text)
    if "Metric" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid.startswith("BE-"):
            if f"**{mid}**" not in body:
                return False
    return True


def antifp_section_ok(text: str) -> bool:
    """
    GIVEN summary body
    WHEN checking anti-FP evidence block
    THEN require modes + LOOKUP≠IQ + BE-FOREVER + NANOGEN6–15 honesty.
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
        "BE-FOREVER",
        "span-fallback",
        "true_continue",
        "forever",
        "over-refuse",
        "utilization",
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
        and "nanogen15" in body
        and "compint" in body
        and "shipuse" in body
        and "fastbe" in body
        and "ctxbe" in body
        and "span-fallback" in body
        and "defer" in body
        and "nanogen6" in body
        and "nanogen7" in body
        and "nanogen8" in body
        and "nanogen14" in body
        and "be-forever" in body
        and "over-refuse" in body
        and "utilization" in body
    )


def render_wave_be_summary() -> str:
    lines = [
        "# Wave BE — compositional anti-FP + util + Nano gen-defer honesty "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §9 · Paper-lab: "
        "[paper-lab-wave-be.md](paper-lab-wave-be.md) · "
        "Real-eval: [wave-be-real-eval.md](wave-be-real-eval.md) · "
        "Freeze: [be-freeze.md](be-freeze.md) · "
        "[formal-habefreeze-be-freeze.md](formal-habefreeze-be-freeze.md)  ",
        "> Parent: Wave BD **BD-FREEZE** · Ship claim: "
        f"**{SHIP_CLAIM}**",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + BE_THESIS
        + ".**",
        "",
        "## Stage scoreboard (product + generative)",
        "",
        "| # | ID | Metric | Decision | Note |",
        "|---|-----|--------|----------|------|",
    ]
    for row in BE_SCOREBOARD:
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
            "H-COMPINT · BE-REAL-EVAL known_lookup · WRAP_LOOKUP |",
            "| PEAK extractive ≠ open-chat | "
            "BE-REAL-EVAL PEAK · H-CTXBE usable span |",
            "| DECODE arm `wall_ms>0` · `n_new>0` | "
            "BE-ASK-05 DECODE path · junk law |",
            "| DECODE gibberish ≠ content_ok | "
            "BE-ASK-06 junk→ABSTAIN |",
            "| BE-FOREVER type/coercion LOOKUP = false-hit | "
            "H-COMPINT BE-FOREVER FH 0 · BE-ASK-07/14 ABSTAIN |",
            "| Exact-gold ABSTAIN = product miss | "
            "H-COMPINT over-refuse 0 · BE-ASK-08 LOOKUP |",
            "| ABSTAIN refuse junk / OOD / near-miss / forever | "
            "BE-REAL-EVAL OOD·junk·near-miss·BE-FOREVER·BA hold·BB hold·"
            "BC hold·BD hold·AZ hold · FH 0 |",
            "| Utilization smoke LOOKUP | "
            "H-SHIPUSE Track A · BE-ASK-15 utilization |",
            "| SAFE ≠ answer quality | "
            "H-COMPINT cites SAFE≠quality |",
            "| True-gen DEFER honesty | "
            "**H-NANOGEN15** DEFER · **H-NANOGEN14** DEFER · "
            "**H-NANOGEN13** DEFER · **H-NANOGEN12** DEFER · "
            "**H-NANOGEN11** DEFER · **H-NANOGEN10** DEFER · "
            "**H-NANOGEN9** DEFER · **H-NANOGEN8** DEFER · "
            "**H-NANOGEN6** HOLD · **H-NANOGEN7** HOLD · "
            "true_continue unmet · span-fallback ≠ gen IQ · "
            "not unlabeled open chat |",
            "| Modes always visible + content bars | "
            "**H-CTXBE** · **BE-REAL-EVAL** LOOKUP·PEAK·DECODE·ABSTAIN |",
            "| Speed without FP regress | "
            "**H-FASTBE** prod p50/p99 · anti-FP hold |",
            "| Generative claim gated | "
            "BE-REAL-EVAL · unlock only if BE5 PROMOTE |",
            "| Telemetry keys | `mode` · `wall_ms` · `n_new` · "
            "`product_mode` |",
            "",
            "## Honest claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| BE-FOREVER anti-FP scoreboard | **H-COMPINT** PROMOTE |",
            "| Track A utilization | **H-SHIPUSE** PROMOTE |",
            "| Prod speed p50/p99 hold | **H-FASTBE** PROMOTE |",
            "| Ctx howto·cite·long content | **H-CTXBE** PROMOTE |",
            "| North-star generative | **H-NANOGEN15** DEFER — "
            "stance defer once · CAPCHECK closed · "
            "NANOGEN6·7 HOLD · NANOGEN8…14 DEFER stand · not rename |",
            "| Parent gen HOLDs / DEFER cited | **H-NANOGEN6** HOLD · "
            "**H-NANOGEN7** HOLD · **H-NANOGEN8** DEFER · "
            "**H-NANOGEN9** DEFER · **H-NANOGEN10** DEFER · "
            "**H-NANOGEN11** DEFER · **H-NANOGEN12** DEFER · "
            "**H-NANOGEN13** DEFER · **H-NANOGEN14** DEFER |",
            "| Final real eval | **BE-REAL-EVAL** PROMOTE — "
            "battery **15/15** · BE-FOREVER ABSTAIN · over-refuse LOOKUP · "
            "utilization · gen locked |",
            "| Ship claim | **" + SHIP_CLAIM + "** |",
            "| “Unlabeled open chat / GPT-class ≤5M” | **False** |",
            "| “TAC / true-continue unlocked” | **False** (BE5 DEFER) |",
            "| “Mini-AGI unlocked” | **False** (BE5 DEFER) |",
            "",
            "## Real-eval section",
            "",
            "| Arm | What was measured | Outcome |",
            "|-----|-------------------|---------|",
            "| Product (COMPINT) | BE-FOREVER FH 0 · BA…BD/AZ hold · "
            "over-refuse 0 · live FP 0 | **PROMOTE** |",
            "| Utilization (SHIPUSE) | demo · operator card · paper sync | "
            "**PROMOTE** |",
            "| Speed (FASTBE) | prod p50/p99 · anti-FP hold | "
            "**PROMOTE** |",
            "| Context (CTXBE) | howto·cite·long content_ok · "
            "anti-FP hold | **PROMOTE** |",
            "| Generative (NANOGEN15) | defer-once stance · CAPCHECK closed · "
            "cite NANOGEN6·7 HOLD · NANOGEN8…14 DEFER · "
            "not rename | **DEFER** |",
            "| Live ask battery | LOOKUP·PEAK·DECODE·ABSTAIN + "
            "BE-FOREVER FP · BA…BD forever · over-refuse · utilization · "
            "near-miss · DECODE junk→ABSTAIN | **PASS** 15/15 |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:be:report",
            "npm run nano:be:session",
            "npm run nano:compint",
            "npm run nano:shipuse",
            "npm run nano:fastbe",
            "npm run nano:ctxbe",
            "npm run nano:nanogen15",
            "npm run nano:be:real-eval",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave BF without "
            "lab-book reopen · sell PEAK/bank-grounded as unlabeled open-chat · "
            "sell SAFE mean as IQ · sell span-fallback as true-continue · "
            "gold-substring PROMOTE · truncate-to-span as gen IQ · "
            "BE-FOREVER type LOOKUP as success · over-refuse as win · "
            "NANOGEN15 = NANOGEN14+rename · bank stuffing BE-FOREVER · "
            "CTX/SMART/FAST/APP letter clones · rewrite BD/BC/BB/BA/AZ locks.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_be() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave BE (compositional anti-FP + util + Nano gen-defer)",
            "",
            "> Companion to [wave-be-summary.md](wave-be-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · "
            "Real-eval: [wave-be-real-eval.md](wave-be-real-eval.md) · "
            "Freeze: [be-freeze.md](be-freeze.md) · "
            "[formal-habefreeze-be-freeze.md](formal-habefreeze-be-freeze.md) · "
            "Parent: [bd-freeze.md](bd-freeze.md) · "
            f"Ship: **{SHIP_CLAIM}**",
            "",
            "## Question",
            "",
            "After BD froze semantic anti-FP + honest NANOGEN14 DEFER, "
            "can Wave BE **close compositional residual FP** "
            "(BE-FOREVER FH 0 + novel) **and** ship/utilize the proven stack "
            "**and** hold **context** / **speed** on the prod path **and** "
            "clear a **real new method** generative lift under ≤5M "
            "**without** unlabeled open-chat / GPT-class / "
            "NANOGEN15=NANOGEN14+rename / bank stuffing?",
            "",
            "## Answer",
            "",
            "**Yes for compositional anti-FP + util + ctx/speed hold; "
            "honest DEFER-once for generative.** "
            "H-COMPINT · H-SHIPUSE · H-FASTBE · H-CTXBE PROMOTE. "
            "**H-NANOGEN15 DEFER** "
            "(BE0 stance=defer; CAPCHECK closed; no real M1|M2|M3; "
            "NANOGEN6·7 HOLD · NANOGEN8…14 DEFER cited; not a rename; "
            "stop rule). "
            "BE-REAL-EVAL PROMOTE (live battery 15/15; BE-FOREVER FP ABSTAIN; "
            "over-refuse LOOKUP; utilization smoke; gen unlock locked). "
            f"Ship claim stays STRICT archive: **{SHIP_CLAIM}**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-COMPINT | BE-FOREVER FH 0 · BA…BD/AZ hold · "
            "over-refuse 0 → PROMOTE |",
            "| H-SHIPUSE | Track A demo · operator · paper sync → PROMOTE |",
            "| H-FASTBE | Prod p50/p99 hold · anti-FP hold → PROMOTE |",
            "| H-CTXBE | Howto·cite·long content_ok · "
            "anti-FP hold → PROMOTE |",
            "| H-NANOGEN15 | Gen stance defer once · NANOGEN6·7 HOLD · "
            "NANOGEN8…14 DEFER cited → DEFER |",
            "| BE-REAL-EVAL | Live battery 15/15 · gen locked → PROMOTE |",
            "| BE-REPORT | Summary + paper-lab + anti-FP · util → PROMOTE |",
            "| BE-FREEZE | Outcomes lock — no Wave BF invent |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP / BE-FOREVER probes must never be sold as generative IQ. "
            "Type/coercion wrong LOOKUP (str→int→add) is a false-hit. "
            "Exact-gold ABSTAIN is a product miss. PEAK and "
            "span-fallback stay product/extractive credit only. L_eff alone "
            "≠ ctx win. Warm-cache microbench ≠ speed win. DECODE telemetry "
            "(`wall_ms`, `n_new`) is mandatory but insufficient for "
            "content_ok. SAFE≠quality. Utilization is ship-surface, not IQ. "
            "Gold-substring / gibberish-tail / "
            "truncate-to-span ≠ generative PROMOTE. "
            "**H-NANOGEN15 DEFER** plus cited **H-NANOGEN6** / **H-NANOGEN7 "
            "HOLD** and **H-NANOGEN8**…**H-NANOGEN14 DEFER** keep "
            "true-continue / mini-AGI language locked — ship remains STRICT "
            "ablated DECODE archive, not unlabeled open chat.",
            "",
            "## Takeaway one-liner",
            "",
            "**BE = compositional BE-FOREVER anti-FP + Track A utilization + "
            "measurable ctx/speed hold + gen DEFER-once honestly "
            "(NANOGEN6·7 HOLD · NANOGEN8…15 DEFER stand; not NANOGEN14 rename); "
            "ship AF+AQ+AS trust + STRICT snippet-prefix DECODE — not unlabeled "
            "open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-be-summary.md](wave-be-summary.md) · "
            "[wave-be-real-eval.md](wave-be-real-eval.md) · "
            "[wave-be-session.md](wave-be-session.md) · "
            "[bd-freeze.md](bd-freeze.md)  ",
            "- Formals: COMPINT · SHIPUSE · FASTBE · CTXBE · NANOGEN15  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
