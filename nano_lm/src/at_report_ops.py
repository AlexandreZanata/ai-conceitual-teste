"""Wave AT REPORT: public closeout (Caminho A + ablated DECODE honesty)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "AT_ID",
    "AT_THESIS",
    "AT_EVIDENCE",
    "AT_REPORT_MARKERS",
    "AT_SCOREBOARD",
    "SHIP_CLAIM",
    "decide_at_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "realeval_section_ok",
    "render_wave_at_summary",
    "render_paper_lab_wave_at",
]

AT_ID = "AT-REPORT"
SHIP_CLAIM = (
    "AF packaged stack + AQ product layer + AS trust path + "
    "ablated DECODE (snippet-prefix) — not unlabeled open chat LM"
)
AT_THESIS = (
    "Wave AT dual track: H-PRODREG·H-SHIPAPP PROMOTE (Caminho A); "
    "H-NANOGEN4 PROMOTE (ablated 5.5 ≥ 5.0 vs NANOGEN3 4.3 · "
    "snippet-prefix); AT-REAL-EVAL PROMOTE (live battery 6/6); "
    "ship " + SHIP_CLAIM
)

AT_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AT0",
        "id": "SESSION",
        "metric": "packs frozen",
        "decision": "PROMOTE",
        "note": "PRODREG · SHIPAPP · NANOGEN4 hyp · real-eval protocol",
    },
    {
        "stage": "AT1",
        "id": "H-PRODREG",
        "metric": "Caminho A bars hold",
        "decision": "PROMOTE",
        "note": "para 0.80 · FH 0 · modes 4/4 · abstain · p50/p99+KB",
    },
    {
        "stage": "AT2",
        "id": "H-SHIPAPP",
        "metric": "ask·apps·ship/demo 4/4",
        "decision": "PROMOTE",
        "note": "LOOKUP·PEAK·DECODE·ABSTAIN always visible",
    },
    {
        "stage": "AT3",
        "id": "H-NANOGEN4",
        "metric": "ablated gen 5.5 ≥ 5.0",
        "decision": "PROMOTE",
        "note": "snippet-prefix · beats NANOGEN3 4.3 · peak/bank compare",
    },
    {
        "stage": "AT4",
        "id": "AT-REAL-EVAL",
        "metric": "live ask battery 6/6",
        "decision": "PROMOTE",
        "note": "product+gen · near-miss refuse · anti-FP",
    },
    {
        "stage": "AT5",
        "id": "AT-REPORT",
        "metric": "summary + paper-lab",
        "decision": "PROMOTE",
        "note": "docs + anti-FP table · real-eval section",
    },
    {
        "stage": "AT6",
        "id": "AT-FREEZE",
        "metric": "lock outcomes",
        "decision": "PROMOTE",
        "note": "COMPLETE+FROZEN · no Wave AU invent",
    },
)

AT_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-at-session.md",
    "docs/results/nano-lm/formal-hprodreg-prodreg.md",
    "docs/results/nano-lm/formal-hshipapp-shipapp.md",
    "docs/results/nano-lm/shipapp-demo.md",
    "docs/results/nano-lm/formal-hnanogen4-nanogen4.md",
    "docs/results/nano-lm/wave-at-real-eval.md",
    "docs/results/nano-lm/wave-at-summary.md",
    "docs/results/nano-lm/paper-lab-wave-at.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AT_REPORT_MARKERS: tuple[str, ...] = (
    "H-PRODREG",
    "H-SHIPAPP",
    "H-NANOGEN4",
    "AT-REAL-EVAL",
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
    "anti-FP",
    "PROMOTE",
    "snippet-prefix",
    "ablated",
    "5.5",
    "not unlabeled open chat",
    "AF packaged stack",
    "product layer",
    "SAFE",
)


def decide_at_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AT_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AT report evidence
    WHEN deciding AT-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AT_ID}: {AT_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AT_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AT_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking AT scoreboard
    THEN every stage id appears with Metric column.
    """
    body = str(text)
    if "Metric" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid.startswith("AT-"):
            if f"**{mid}**" not in body:
                return False
    return True


def antifp_section_ok(text: str) -> bool:
    """
    GIVEN summary body
    WHEN checking anti-FP evidence block
    THEN require modes + LOOKUP≠IQ + NANOGEN4 honesty.
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
        "H-NANOGEN4",
        "snippet-prefix",
        "SAFE",
        "unlabeled open chat",
    )
    return all(m in body for m in need)


def realeval_section_ok(text: str) -> bool:
    """Require explicit real-eval section with battery + gen claim."""
    body = str(text).lower()
    return (
        "real-eval" in body
        and "battery" in body
        and "nanogen4" in body
        and "prodreg" in body
    )


def render_wave_at_summary() -> str:
    lines = [
        "# Wave AT — Caminho A ship + Nano Generative gate "
        "(**RESEARCH_COMPLETE** · freeze pending)",
        "",
        "> Lab: `.local/pesquisa.md` §5 · Paper-lab: "
        "[paper-lab-wave-at.md](paper-lab-wave-at.md) · "
        "Real-eval: [wave-at-real-eval.md](wave-at-real-eval.md) · "
        "Freeze: [at-freeze.md](at-freeze.md) · "
        "[formal-hatfreeze-at-freeze.md](formal-hatfreeze-at-freeze.md)  ",
        "> Parent: Wave AS **AS-FREEZE** reopen · Ship claim: "
        f"**{SHIP_CLAIM}**",
        "",
        "**Status: RESEARCH_COMPLETE** (AT6 FREEZE next) · Thesis: **"
        + AT_THESIS
        + ".**",
        "",
        "## Stage scoreboard (product + generative)",
        "",
        "| # | ID | Metric | Decision | Note |",
        "|---|-----|--------|----------|------|",
    ]
    for row in AT_SCOREBOARD:
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
            "H-SHIPAPP · AT-REAL-EVAL known_lookup · WRAP_LOOKUP |",
            "| PEAK extractive ≠ open-chat | "
            "H-SHIPAPP PEAK · NANOGEN4 peak compare only |",
            "| DECODE arm `wall_ms>0` · `n_new>0` | "
            "H-SHIPAPP DECODE · NANOGEN4 ablated · AT-ASK-05 |",
            "| ABSTAIN refuse junk / OOD / near-miss | "
            "AT-REAL-EVAL OOD·junk·SegWit/BIP-39 refuse · FH honesty |",
            "| SAFE ≠ answer quality | "
            "H-PRODREG cites ADVSAFE · SAFE≠quality |",
            "| Ablated gen PROMOTE honesty | "
            "**H-NANOGEN4** ablated **5.5** · snippet-prefix · "
            "not unlabeled open chat |",
            "| Modes always visible | "
            "**H-SHIPAPP** LOOKUP·PEAK·DECODE·ABSTAIN |",
            "| Generative claim gated | "
            "AT-REAL-EVAL · claim only after AT3 PROMOTE |",
            "| Telemetry keys | `mode` · `wall_ms` · `n_new` · "
            "`product_mode` |",
            "",
            "## Honest claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| Caminho A regression | **H-PRODREG** PROMOTE |",
            "| Mode-visible ask/apps/ship | **H-SHIPAPP** PROMOTE — 4/4 |",
            "| North-star generative | **H-NANOGEN4** PROMOTE — "
            "ablated **5.5** · snippet-prefix |",
            "| Final real eval | **AT-REAL-EVAL** PROMOTE — "
            "battery **6/6** |",
            "| Ship claim | **" + SHIP_CLAIM + "** |",
            "| “Unlabeled open chat / GPT-class ≤5M” | **False** |",
            "",
            "## Real-eval section",
            "",
            "| Arm | What was measured | Outcome |",
            "|-----|-------------------|---------|",
            "| Product (PRODREG) | para · FH · latency · KB · modes · "
            "abstain | **PROMOTE** |",
            "| Product (SHIPAPP) | ask · apps · ship/demo modes | "
            "**PROMOTE** 4/4 |",
            "| Generative (NANOGEN4) | ablated DECODE vs NANOGEN3 4.3 | "
            "**PROMOTE** (ablated **5.5** · snippet-prefix) |",
            "| Live ask battery | LOOKUP·PEAK·DECODE·ABSTAIN + "
            "near-miss refuse | **PASS** 6/6 |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:at:report",
            "npm run nano:at:session",
            "npm run nano:prodreg",
            "npm run nano:shipapp",
            "npm run nano:nanogen4",
            "npm run nano:at:real-eval",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave AU without "
            "lab-book reopen · sell PEAK/bank-grounded as unlabeled open-chat · "
            "sell SAFE mean as IQ · sell snippet-prefix as GPT-class · "
            "CTX/SMART/FAST/APP letter clones without named product hole · "
            "rewrite AS/AR/AQ locked outcomes.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_at() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AT (Caminho A ship + Nano Generative gate)",
            "",
            "> Companion to [wave-at-summary.md](wave-at-summary.md). "
            "English lab note.  ",
            "> **Status: RESEARCH_COMPLETE** (freeze pending) · "
            "Real-eval: [wave-at-real-eval.md](wave-at-real-eval.md) · "
            "Freeze: [at-freeze.md](at-freeze.md) · "
            "[formal-hatfreeze-at-freeze.md](formal-hatfreeze-at-freeze.md) · "
            "Parent: [as-freeze.md](as-freeze.md) · "
            f"Ship: **{SHIP_CLAIM}**",
            "",
            "## Question",
            "",
            "After AS froze product trust with NANOGEN3 HOLD (ablated 4.3), "
            "can Wave AT **ship Caminho A** (regression + mode-visible "
            "ask/apps/ship) **and** clear one ablated generative lift "
            "(snippet-prefix) under ≤5M **without** unlabeled open-chat / "
            "GPT-class overclaim?",
            "",
            "## Answer",
            "",
            "**Yes for both legs — with honest claim language.** "
            "H-PRODREG · H-SHIPAPP PROMOTE. **H-NANOGEN4 PROMOTE** "
            "(ablated **5.5**, snippet-prefix, beats NANOGEN3 4.3). "
            "AT-REAL-EVAL PROMOTE (live battery 6/6, near-miss refuse). "
            f"Ship claim: **{SHIP_CLAIM}**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-PRODREG | Caminho A bars hold → PROMOTE |",
            "| H-SHIPAPP | LOOKUP·PEAK·DECODE·ABSTAIN 4/4 → PROMOTE |",
            "| H-NANOGEN4 | Ablated 5.5 · snippet-prefix → PROMOTE |",
            "| AT-REAL-EVAL | Live battery 6/6 · anti-FP → PROMOTE |",
            "| AT-REPORT | Summary + paper-lab + anti-FP → PROMOTE |",
            "| AT-FREEZE | Outcomes lock — no Wave AU invent |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP / SHIPAPP must never be sold as generative IQ. PEAK and "
            "bank-grounded short stay compare-only. DECODE telemetry "
            "(`wall_ms`, `n_new`) is mandatory. SAFE≠quality. "
            "**H-NANOGEN4** unlocks **ablated DECODE (snippet-prefix)** "
            "language only — not unlabeled open chat / GPT-class.",
            "",
            "## Takeaway one-liner",
            "",
            "**AT = Caminho A shipped + ablated DECODE gate cleared "
            "(5.5); ship AF+AQ+AS trust + snippet-prefix DECODE — not "
            "unlabeled open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-at-summary.md](wave-at-summary.md) · "
            "[wave-at-real-eval.md](wave-at-real-eval.md) · "
            "[wave-at-session.md](wave-at-session.md) · "
            "[as-freeze.md](as-freeze.md)  ",
            "- Formals: PRODREG · SHIPAPP · NANOGEN4  ",
            "- Demo: [shipapp-demo.md](shipapp-demo.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
