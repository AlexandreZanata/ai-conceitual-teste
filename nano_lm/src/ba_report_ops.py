"""Wave BA REPORT: public closeout (forever anti-FP + honest NANOGEN11 DEFER)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ba_session_ops import BA0_SHIP_LOCK

__all__ = [
    "BA_ID",
    "BA_THESIS",
    "BA_EVIDENCE",
    "BA_REPORT_MARKERS",
    "BA_SCOREBOARD",
    "SHIP_CLAIM",
    "decide_ba_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "realeval_section_ok",
    "render_wave_ba_summary",
    "render_paper_lab_wave_ba",
]

BA_ID = "BA-REPORT"
SHIP_CLAIM = BA0_SHIP_LOCK
BA_THESIS = (
    "Wave BA dual track: H-REALGAIN·H-FASTREAL·H-CTXREAL2 PROMOTE "
    "(forever FH 0 · prod p50/p99 · howto·cite·long content · anti-FP); "
    "H-NANOGEN11 DEFER (gen stance defer · CAPCHECK closed · "
    "NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER cited · not NANOGEN10 rename); "
    "BA-REAL-EVAL PROMOTE (live battery 10/10 · forever FP ABSTAIN · "
    "over-refuse LOOKUP · gen locked); ship " + SHIP_CLAIM
)

BA_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "BA0",
        "id": "SESSION",
        "metric": "packs frozen",
        "decision": "PROMOTE",
        "note": "BA-FOREVER · AZ hold · §1 scoreboard · gen stance defer · true-eval",
    },
    {
        "stage": "BA1",
        "id": "H-REALGAIN",
        "metric": "forever FH 0 · live FP 0",
        "decision": "PROMOTE",
        "note": "forever FH 0 · AZ hold 0 · over-refuse 0 · live probes · no bank stuffing",
    },
    {
        "stage": "BA2",
        "id": "H-FASTREAL",
        "metric": "prod p50/p99 no FP regress",
        "decision": "PROMOTE",
        "note": "prod latency published · anti-FP hold · ≠ AG nano:fastreal archive",
    },
    {
        "stage": "BA3",
        "id": "H-CTXREAL2",
        "metric": "howto·cite·long content_ok",
        "decision": "PROMOTE",
        "note": "content bars · anti-FP hold · L_eff alone ≠ win · ≠ AG nano:ctxreal",
    },
    {
        "stage": "BA4",
        "id": "H-NANOGEN11",
        "metric": "gen stance defer",
        "decision": "DEFER",
        "note": "CAPCHECK closed · no real M1|M2|M3 · NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER · not rename",
    },
    {
        "stage": "BA5",
        "id": "BA-REAL-EVAL",
        "metric": "live ask battery 10/10",
        "decision": "PROMOTE",
        "note": "product+ctx+speed pass · forever ABSTAIN · over-refuse LOOKUP · gen locked · prod=eval",
    },
    {
        "stage": "BA6",
        "id": "BA-REPORT",
        "metric": "summary + paper-lab",
        "decision": "PROMOTE",
        "note": "docs + anti-FP · BA4 DEFER · NANOGEN6/7 HOLD · NANOGEN8·9·10 DEFER cited",
    },
    {
        "stage": "BA7",
        "id": "BA-FREEZE",
        "metric": "lock outcomes",
        "decision": "PROMOTE",
        "note": "COMPLETE+FROZEN · no Wave BB invent",
    },
)

BA_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ba-session.md",
    "docs/results/nano-lm/formal-hrealgain-realgain.md",
    "docs/results/nano-lm/formal-hfastreal-ba2.md",
    "docs/results/nano-lm/formal-hctxreal2-ctxreal2.md",
    "docs/results/nano-lm/formal-hnanogen11-nanogen11.md",
    "docs/results/nano-lm/wave-ba-real-eval.md",
    "docs/results/nano-lm/wave-ba-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ba.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

BA_REPORT_MARKERS: tuple[str, ...] = (
    "H-REALGAIN",
    "H-FASTREAL",
    "H-CTXREAL2",
    "H-NANOGEN11",
    "H-NANOGEN10",
    "H-NANOGEN9",
    "H-NANOGEN8",
    "H-NANOGEN6",
    "H-NANOGEN7",
    "BA-REAL-EVAL",
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
)


def decide_ba_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = BA_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for BA report evidence
    WHEN deciding BA-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({BA_ID}: {BA_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = BA_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = BA_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking BA scoreboard
    THEN every stage id appears with Metric column.
    """
    body = str(text)
    if "Metric" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid.startswith("BA-"):
            if f"**{mid}**" not in body:
                return False
    return True


def antifp_section_ok(text: str) -> bool:
    """
    GIVEN summary body
    WHEN checking anti-FP evidence block
    THEN require modes + LOOKUP≠IQ + forever + NANOGEN6–11 honesty.
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
        "H-NANOGEN11",
        "H-NANOGEN10",
        "H-NANOGEN9",
        "H-NANOGEN8",
        "H-NANOGEN6",
        "H-NANOGEN7",
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
        and "nanogen11" in body
        and "realgain" in body
        and "fastreal" in body
        and "ctxreal2" in body
        and "span-fallback" in body
        and "defer" in body
        and "nanogen6" in body
        and "nanogen7" in body
        and "nanogen8" in body
        and "nanogen9" in body
        and "nanogen10" in body
        and "forever" in body
        and "over-refuse" in body
    )


def render_wave_ba_summary() -> str:
    lines = [
        "# Wave BA — forever anti-FP + Nano gen-defer honesty "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §8 · Paper-lab: "
        "[paper-lab-wave-ba.md](paper-lab-wave-ba.md) · "
        "Real-eval: [wave-ba-real-eval.md](wave-ba-real-eval.md) · "
        "Freeze: [ba-freeze.md](ba-freeze.md) · "
        "[formal-habfreeze-ba-freeze.md](formal-habfreeze-ba-freeze.md)  ",
        "> Parent: Wave AZ **AZ-FREEZE** · Ship claim: "
        f"**{SHIP_CLAIM}**",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + BA_THESIS
        + ".**",
        "",
        "## Stage scoreboard (product + generative)",
        "",
        "| # | ID | Metric | Decision | Note |",
        "|---|-----|--------|----------|------|",
    ]
    for row in BA_SCOREBOARD:
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
            "H-REALGAIN · BA-REAL-EVAL known_lookup · WRAP_LOOKUP |",
            "| PEAK extractive ≠ open-chat | "
            "BA-REAL-EVAL PEAK · H-CTXREAL2 usable span |",
            "| DECODE arm `wall_ms>0` · `n_new>0` | "
            "BA-ASK-05 DECODE path · junk law |",
            "| DECODE gibberish ≠ content_ok | "
            "BA-ASK-06 junk→ABSTAIN |",
            "| Forever intent LOOKUP = false-hit | "
            "H-REALGAIN forever FH 0 · BA-ASK-07/10 ABSTAIN |",
            "| Exact-gold ABSTAIN = product miss | "
            "H-REALGAIN over-refuse 0 · BA-ASK-08 LOOKUP |",
            "| ABSTAIN refuse junk / OOD / near-miss / forever | "
            "BA-REAL-EVAL OOD·junk·near-miss·forever·AZ hold · FH 0 |",
            "| SAFE ≠ answer quality | "
            "H-REALGAIN cites SAFE≠quality |",
            "| True-gen DEFER honesty | "
            "**H-NANOGEN11** DEFER · **H-NANOGEN10** DEFER · "
            "**H-NANOGEN9** DEFER · **H-NANOGEN8** DEFER · "
            "**H-NANOGEN6** HOLD · **H-NANOGEN7** HOLD · "
            "true_continue unmet · span-fallback ≠ gen IQ · "
            "not unlabeled open chat |",
            "| Modes always visible + content bars | "
            "**H-CTXREAL2** · **BA-REAL-EVAL** LOOKUP·PEAK·DECODE·ABSTAIN |",
            "| Speed without FP regress | "
            "**H-FASTREAL** prod p50/p99 · anti-FP hold |",
            "| Generative claim gated | "
            "BA-REAL-EVAL · unlock only if BA4 PROMOTE |",
            "| Telemetry keys | `mode` · `wall_ms` · `n_new` · "
            "`product_mode` |",
            "",
            "## Honest claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| Forever anti-FP scoreboard | **H-REALGAIN** PROMOTE |",
            "| Prod speed p50/p99 | **H-FASTREAL** PROMOTE |",
            "| Ctx howto·cite·long content | **H-CTXREAL2** PROMOTE |",
            "| North-star generative | **H-NANOGEN11** DEFER — "
            "stance defer · CAPCHECK closed · "
            "NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER stand · not rename |",
            "| Parent gen HOLDs / DEFER cited | **H-NANOGEN6** HOLD · "
            "**H-NANOGEN7** HOLD · **H-NANOGEN8** DEFER · "
            "**H-NANOGEN9** DEFER · **H-NANOGEN10** DEFER |",
            "| Final real eval | **BA-REAL-EVAL** PROMOTE — "
            "battery **10/10** · forever ABSTAIN · over-refuse LOOKUP · "
            "gen locked |",
            "| Ship claim | **" + SHIP_CLAIM + "** |",
            "| “Unlabeled open chat / GPT-class ≤5M” | **False** |",
            "| “TAC / true-continue unlocked” | **False** (BA4 DEFER) |",
            "| “Mini-AGI unlocked” | **False** (BA4 DEFER) |",
            "",
            "## Real-eval section",
            "",
            "| Arm | What was measured | Outcome |",
            "|-----|-------------------|---------|",
            "| Product (REALGAIN) | forever FH 0 · AZ hold · "
            "over-refuse 0 · live FP 0 | **PROMOTE** |",
            "| Speed (FASTREAL) | prod p50/p99 · anti-FP hold | "
            "**PROMOTE** |",
            "| Context (CTXREAL2) | howto·cite·long content_ok · "
            "anti-FP hold | **PROMOTE** |",
            "| Generative (NANOGEN11) | defer stance · CAPCHECK closed · "
            "cite NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER · not rename | "
            "**DEFER** |",
            "| Live ask battery | LOOKUP·PEAK·DECODE·ABSTAIN + "
            "forever FP · over-refuse · near-miss · DECODE junk→ABSTAIN | "
            "**PASS** 10/10 |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:ba:report",
            "npm run nano:ba:session",
            "npm run nano:realgain",
            "npm run nano:ba:fastreal",
            "npm run nano:ba:ctxreal2",
            "npm run nano:nanogen11",
            "npm run nano:ba:real-eval",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave BB without "
            "lab-book reopen · sell PEAK/bank-grounded as unlabeled open-chat · "
            "sell SAFE mean as IQ · sell span-fallback as true-continue · "
            "gold-substring PROMOTE · truncate-to-span as gen IQ · "
            "forever intent LOOKUP as success · over-refuse as win · "
            "NANOGEN11 = NANOGEN10+rename · bank stuffing BA-FOREVER · "
            "CTX/SMART/FAST/APP letter clones · rewrite AZ/AY/AX/… locks.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_ba() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave BA (forever anti-FP + Nano gen-defer)",
            "",
            "> Companion to [wave-ba-summary.md](wave-ba-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · "
            "Real-eval: [wave-ba-real-eval.md](wave-ba-real-eval.md) · "
            "Freeze: [ba-freeze.md](ba-freeze.md) · "
            "[formal-habfreeze-ba-freeze.md](formal-habfreeze-ba-freeze.md) · "
            "Parent: [az-freeze.md](az-freeze.md) · "
            f"Ship: **{SHIP_CLAIM}**",
            "",
            "## Question",
            "",
            "After AZ froze held-out product + honest NANOGEN10 DEFER, "
            "can Wave BA **measure real intelligence gain** "
            "(BA-FOREVER FH 0 + live ask) **and** lift **context** / "
            "**speed** on the prod path **and** clear a **real new method** "
            "generative lift under ≤5M **without** unlabeled open-chat / "
            "GPT-class / NANOGEN11=NANOGEN10+rename / bank stuffing?",
            "",
            "## Answer",
            "",
            "**Yes for forever anti-FP + ctx/speed measure; honest DEFER "
            "for generative.** "
            "H-REALGAIN · H-FASTREAL · H-CTXREAL2 PROMOTE. "
            "**H-NANOGEN11 DEFER** "
            "(BA0 stance=defer; CAPCHECK closed; no real M1|M2|M3; "
            "NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER cited; not a rename). "
            "BA-REAL-EVAL PROMOTE (live battery 10/10; forever FP ABSTAIN; "
            "over-refuse LOOKUP; gen unlock locked). "
            f"Ship claim stays STRICT archive: **{SHIP_CLAIM}**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-REALGAIN | Forever FH 0 · AZ hold · over-refuse 0 → PROMOTE |",
            "| H-FASTREAL | Prod p50/p99 · anti-FP hold → PROMOTE |",
            "| H-CTXREAL2 | Howto·cite·long content_ok · anti-FP hold → PROMOTE |",
            "| H-NANOGEN11 | Gen stance defer · NANOGEN6·7 HOLD · "
            "NANOGEN8·9·10 DEFER cited → DEFER |",
            "| BA-REAL-EVAL | Live battery 10/10 · gen locked → PROMOTE |",
            "| BA-REPORT | Summary + paper-lab + anti-FP → PROMOTE |",
            "| BA-FREEZE | Outcomes lock — no Wave BB invent |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP / forever probes must never be sold as generative IQ. "
            "Forever intent mismatch LOOKUP is a false-hit. Exact-gold "
            "ABSTAIN is a product miss. PEAK and span-fallback stay "
            "product/extractive credit only. L_eff alone ≠ ctx win. "
            "Warm-cache microbench ≠ speed win. DECODE telemetry "
            "(`wall_ms`, `n_new`) is mandatory but insufficient for "
            "content_ok. SAFE≠quality. Gold-substring / gibberish-tail / "
            "truncate-to-span ≠ generative PROMOTE. "
            "**H-NANOGEN11 DEFER** plus cited **H-NANOGEN6** / **H-NANOGEN7 "
            "HOLD** and **H-NANOGEN8** / **H-NANOGEN9** / **H-NANOGEN10 "
            "DEFER** keep true-continue / mini-AGI language locked — ship "
            "remains STRICT ablated DECODE archive, not unlabeled open chat.",
            "",
            "## Takeaway one-liner",
            "",
            "**BA = forever anti-FP + measurable ctx/speed + gen DEFERs "
            "honestly (NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER stand; "
            "not NANOGEN10 rename); ship AF+AQ+AS trust + STRICT "
            "snippet-prefix DECODE — not unlabeled open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-ba-summary.md](wave-ba-summary.md) · "
            "[wave-ba-real-eval.md](wave-ba-real-eval.md) · "
            "[wave-ba-session.md](wave-ba-session.md) · "
            "[az-freeze.md](az-freeze.md)  ",
            "- Formals: REALGAIN · FASTREAL (ba2) · CTXREAL2 · NANOGEN11  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
