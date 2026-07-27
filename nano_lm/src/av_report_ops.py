"""Wave AV REPORT: public closeout (Caminho A ship + honest NANOGEN6 HOLD)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from av_session_ops import AV0_SHIP_LOCK

__all__ = [
    "AV_ID",
    "AV_THESIS",
    "AV_EVIDENCE",
    "AV_REPORT_MARKERS",
    "AV_SCOREBOARD",
    "SHIP_CLAIM",
    "decide_av_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "realeval_section_ok",
    "render_wave_av_summary",
    "render_paper_lab_wave_av",
]

AV_ID = "AV-REPORT"
SHIP_CLAIM = AV0_SHIP_LOCK
AV_THESIS = (
    "Wave AV dual track: H-PRODSHIP·H-SHIPUI2 PROMOTE (Caminho A ship · "
    "external para · DECODE content law); H-NANOGEN6 HOLD "
    "(true_continue=0 · span-fallback ≠ gen IQ); AV-REAL-EVAL PROMOTE "
    "(live battery 8/8 · gen locked); ship " + SHIP_CLAIM
)

AV_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AV0",
        "id": "SESSION",
        "metric": "packs frozen",
        "decision": "PROMOTE",
        "note": "product-ship · external-para · NANOGEN6 hyp · true-gen judge",
    },
    {
        "stage": "AV1",
        "id": "H-PRODSHIP",
        "metric": "Caminho A ship bars closed",
        "decision": "PROMOTE",
        "note": "external para · FH 0 · p50/p99 · KB · DECODE ≠ telemetry-ok",
    },
    {
        "stage": "AV2",
        "id": "H-SHIPUI2",
        "metric": "modes+content honest",
        "decision": "PROMOTE",
        "note": "LOOKUP·PEAK·DECODE·ABSTAIN · DECODE usable/ABSTAIN · no unlabeled",
    },
    {
        "stage": "AV3",
        "id": "H-NANOGEN6",
        "metric": "true_continue ablated 4.0",
        "decision": "HOLD",
        "note": "bar 5.5 unmet · span-fallback ≠ gen · refuse-or-continue honest",
    },
    {
        "stage": "AV4",
        "id": "AV-REAL-EVAL",
        "metric": "live ask battery 8/8",
        "decision": "PROMOTE",
        "note": "product pass · gen locked (AV3 HOLD) · anti-FP · prod=eval",
    },
    {
        "stage": "AV5",
        "id": "AV-REPORT",
        "metric": "summary + paper-lab",
        "decision": "PROMOTE",
        "note": "docs + anti-FP table · real-eval section",
    },
    {
        "stage": "AV6",
        "id": "AV-FREEZE",
        "metric": "lock outcomes",
        "decision": "PROMOTE",
        "note": "COMPLETE+FROZEN · no Wave AW invent",
    },
)

AV_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-av-session.md",
    "docs/results/nano-lm/formal-hprodship-prodship.md",
    "docs/results/nano-lm/formal-hshipui2-shipui2.md",
    "docs/results/nano-lm/shipui2-demo.md",
    "docs/results/nano-lm/formal-hnanogen6-nanogen6.md",
    "docs/results/nano-lm/wave-av-real-eval.md",
    "docs/results/nano-lm/wave-av-summary.md",
    "docs/results/nano-lm/paper-lab-wave-av.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AV_REPORT_MARKERS: tuple[str, ...] = (
    "H-PRODSHIP",
    "H-SHIPUI2",
    "H-NANOGEN6",
    "AV-REAL-EVAL",
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
    "anti-FP",
    "PROMOTE",
    "HOLD",
    "true_continue",
    "span-fallback",
    "snippet-prefix",
    "gibberish-tail",
    "STRICT",
    "not unlabeled open chat",
    "AF packaged stack",
    "product layer",
    "SAFE",
)


def decide_av_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AV_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AV report evidence
    WHEN deciding AV-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AV_ID}: {AV_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AV_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AV_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking AV scoreboard
    THEN every stage id appears with Metric column.
    """
    body = str(text)
    if "Metric" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid.startswith("AV-"):
            if f"**{mid}**" not in body:
                return False
    return True


def antifp_section_ok(text: str) -> bool:
    """
    GIVEN summary body
    WHEN checking anti-FP evidence block
    THEN require modes + LOOKUP≠IQ + NANOGEN6 honesty (span-fallback ≠ gen).
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
        "H-NANOGEN6",
        "span-fallback",
        "true_continue",
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
        and "nanogen6" in body
        and "prodship" in body
        and "shipui2" in body
        and "span-fallback" in body
    )


def render_wave_av_summary() -> str:
    lines = [
        "# Wave AV — Caminho A ship + Nano true-gen honesty "
        "(**RESEARCH_COMPLETE** · pending FREEZE)",
        "",
        "> Lab: `.local/pesquisa.md` §5 · Paper-lab: "
        "[paper-lab-wave-av.md](paper-lab-wave-av.md) · "
        "Real-eval: [wave-av-real-eval.md](wave-av-real-eval.md) · "
        "Freeze: [av-freeze.md](av-freeze.md) · "
        "[formal-havfreeze-av-freeze.md](formal-havfreeze-av-freeze.md)  ",
        "> Parent: Wave AU **AU-FREEZE** reopen · Ship claim: "
        f"**{SHIP_CLAIM}**",
        "",
        "**Status: RESEARCH_COMPLETE** (AV6 FREEZE next) · Thesis: **"
        + AV_THESIS
        + ".**",
        "",
        "## Stage scoreboard (product + generative)",
        "",
        "| # | ID | Metric | Decision | Note |",
        "|---|-----|--------|----------|------|",
    ]
    for row in AV_SCOREBOARD:
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
            "H-SHIPUI2 · AV-REAL-EVAL known_lookup · WRAP_LOOKUP |",
            "| PEAK extractive ≠ open-chat | "
            "H-SHIPUI2 PEAK · H-PRODSHIP usable span · NANOGEN6 peak compare |",
            "| DECODE arm `wall_ms>0` · `n_new>0` | "
            "H-SHIPUI2 WRAP_DECODE · NANOGEN6 ablated · AV-ASK-05/08 |",
            "| DECODE gibberish ≠ content_ok | "
            "H-PRODSHIP · H-SHIPUI2 junk→ABSTAIN · AV-ASK-08 |",
            "| ABSTAIN refuse junk / OOD / near-miss | "
            "AV-REAL-EVAL OOD·junk·SegWit/BIP-39 refuse · FH honesty |",
            "| SAFE ≠ answer quality | "
            "H-PRODSHIP cites ADVSAFE · SAFE≠quality |",
            "| True-gen HOLD honesty | "
            "**H-NANOGEN6** HOLD · true_continue=0 · "
            "span-fallback ≠ gen IQ · not unlabeled open chat |",
            "| Modes always visible + content bars | "
            "**H-SHIPUI2** LOOKUP·PEAK·DECODE·ABSTAIN |",
            "| Generative claim gated | "
            "AV-REAL-EVAL · true-continue unlock only if AV3 PROMOTE |",
            "| Telemetry keys | `mode` · `wall_ms` · `n_new` · "
            "`product_mode` |",
            "",
            "## Honest claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| Caminho A ship | **H-PRODSHIP** PROMOTE |",
            "| Mode+content ask/apps/ship | **H-SHIPUI2** PROMOTE |",
            "| North-star generative | **H-NANOGEN6** HOLD — "
            "true_continue unmet · span-fallback ≠ gen |",
            "| Final real eval | **AV-REAL-EVAL** PROMOTE — "
            "battery **8/8** · gen locked |",
            "| Ship claim | **" + SHIP_CLAIM + "** |",
            "| “Unlabeled open chat / GPT-class ≤5M” | **False** |",
            "| “True-continue unlocked” | **False** (AV3 HOLD) |",
            "",
            "## Real-eval section",
            "",
            "| Arm | What was measured | Outcome |",
            "|-----|-------------------|---------|",
            "| Product (PRODSHIP) | external para · FH · latency · KB · "
            "DECODE content | **PROMOTE** |",
            "| Product (SHIPUI2) | ask · apps · ship/demo modes+content | "
            "**PROMOTE** |",
            "| Generative (NANOGEN6) | true_continue vs span-fallback | "
            "**HOLD** (true_continue=0 · span-fallback ≠ gen IQ) |",
            "| Live ask battery | LOOKUP·PEAK·DECODE·ABSTAIN + "
            "human-para · near-miss · DECODE junk→ABSTAIN | "
            "**PASS** 8/8 |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:av:report",
            "npm run nano:av:session",
            "npm run nano:prodship",
            "npm run nano:shipui2",
            "npm run nano:nanogen6",
            "npm run nano:av:real-eval",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave AW without "
            "lab-book reopen · sell PEAK/bank-grounded as unlabeled open-chat · "
            "sell SAFE mean as IQ · sell span-fallback as true-continue · "
            "gold-substring PROMOTE · truncate-to-span as gen IQ · "
            "NANOGEN6 = NANOGEN5+rename · "
            "CTX/SMART/FAST/APP letter clones · rewrite AU/AT/AS/AR/AQ locks.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_av() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AV (Caminho A ship + Nano true-gen honesty)",
            "",
            "> Companion to [wave-av-summary.md](wave-av-summary.md). "
            "English lab note.  ",
            "> **Status: RESEARCH_COMPLETE** (pending AV-FREEZE) · "
            "Real-eval: [wave-av-real-eval.md](wave-av-real-eval.md) · "
            "Freeze: [av-freeze.md](av-freeze.md) · "
            "[formal-havfreeze-av-freeze.md](formal-havfreeze-av-freeze.md) · "
            "Parent: [au-freeze.md](au-freeze.md) · "
            f"Ship: **{SHIP_CLAIM}**",
            "",
            "## Question",
            "",
            "After AU froze Caminho A harden + STRICT ablated DECODE 5.5 "
            "(snippet-prefix + gibberish-tail), can Wave AV **ship the "
            "product under external human metrics** (PRODSHIP + SHIPUI2) "
            "**and** clear one **true-continue** generative lift "
            "(span-fallback ≠ gen IQ) under ≤5M **without** unlabeled "
            "open-chat / GPT-class / NANOGEN5-truncate clone?",
            "",
            "## Answer",
            "",
            "**Yes for Caminho A; honest HOLD for true-continue gen.** "
            "H-PRODSHIP · H-SHIPUI2 PROMOTE. **H-NANOGEN6 HOLD** "
            "(true_continue=0/10; span-fallback labeled PEAK with zero "
            "gen credit — not a 5.5 truncate-bar clone). "
            "AV-REAL-EVAL PROMOTE (live battery 8/8; gen unlock locked). "
            f"Ship claim stays AU STRICT archive: **{SHIP_CLAIM}**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-PRODSHIP | External para · FH0 · DECODE content → PROMOTE |",
            "| H-SHIPUI2 | Modes+content · DECODE usable/ABSTAIN → PROMOTE |",
            "| H-NANOGEN6 | true_continue unmet · span-fallback ≠ gen → HOLD |",
            "| AV-REAL-EVAL | Live battery 8/8 · gen locked → PROMOTE |",
            "| AV-REPORT | Summary + paper-lab + anti-FP → PROMOTE |",
            "| AV-FREEZE | Outcomes lock — no Wave AW invent |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP / SHIPUI2 must never be sold as generative IQ. PEAK and "
            "span-fallback stay product/extractive credit only. DECODE "
            "telemetry (`wall_ms`, `n_new`) is mandatory but insufficient "
            "for content_ok. SAFE≠quality. Gold-substring / gibberish-tail / "
            "truncate-to-span ≠ generative PROMOTE. **H-NANOGEN6 HOLD** "
            "keeps true-continue / mini-AGI language locked — ship remains "
            "AU STRICT ablated DECODE archive, not unlabeled open chat.",
            "",
            "## Takeaway one-liner",
            "",
            "**AV = Caminho A shipped + true-continue gen HOLDs honestly "
            "(span-fallback ≠ IQ); ship AF+AQ+AS trust + STRICT "
            "snippet-prefix DECODE — not unlabeled open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-av-summary.md](wave-av-summary.md) · "
            "[wave-av-real-eval.md](wave-av-real-eval.md) · "
            "[wave-av-session.md](wave-av-session.md) · "
            "[au-freeze.md](au-freeze.md)  ",
            "- Formals: PRODSHIP · SHIPUI2 · NANOGEN6  ",
            "- Demo: [shipui2-demo.md](shipui2-demo.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
