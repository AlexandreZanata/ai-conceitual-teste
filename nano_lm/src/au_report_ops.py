"""Wave AU REPORT: public closeout (Caminho A harden + STRICT DECODE)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "AU_ID",
    "AU_THESIS",
    "AU_EVIDENCE",
    "AU_REPORT_MARKERS",
    "AU_SCOREBOARD",
    "SHIP_CLAIM",
    "decide_au_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "realeval_section_ok",
    "render_wave_au_summary",
    "render_paper_lab_wave_au",
]

AU_ID = "AU-REPORT"
SHIP_CLAIM = (
    "AF packaged stack + AQ product layer + AS trust path + "
    "ablated DECODE (snippet-prefix + gibberish-tail STRICT) — "
    "not unlabeled open chat LM"
)
AU_THESIS = (
    "Wave AU dual track: H-PRODHARD·H-SHIPREAL PROMOTE (Caminho A "
    "live-audit); H-NANOGEN5 PROMOTE (strict ablated 5.5 ≥ 5.5 vs "
    "NANOGEN4 soft 5.5 · gibberish-tail + F1/HITL); AU-REAL-EVAL "
    "PROMOTE (live battery 7/7); ship " + SHIP_CLAIM
)

AU_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AU0",
        "id": "SESSION",
        "metric": "packs frozen",
        "decision": "PROMOTE",
        "note": "product-debt · human-para · NANOGEN5 hyp · strict judge",
    },
    {
        "stage": "AU1",
        "id": "H-PRODHARD",
        "metric": "live-audit debts closed",
        "decision": "PROMOTE",
        "note": "near-miss ABSTAIN · para · PEAK usable · FH 0 · p50/p99+KB",
    },
    {
        "stage": "AU2",
        "id": "H-SHIPREAL",
        "metric": "modes+content 4/4",
        "decision": "PROMOTE",
        "note": "LOOKUP·PEAK·DECODE·ABSTAIN + content bars · no unlabeled",
    },
    {
        "stage": "AU3",
        "id": "H-NANOGEN5",
        "metric": "strict ablated 5.5 ≥ 5.5",
        "decision": "PROMOTE",
        "note": "snippet-prefix · gibberish-tail · F1/HITL · vs NANOGEN4 5.5",
    },
    {
        "stage": "AU4",
        "id": "AU-REAL-EVAL",
        "metric": "live ask battery 7/7",
        "decision": "PROMOTE",
        "note": "product+STRICT gen · human-para · near-miss · anti-FP",
    },
    {
        "stage": "AU5",
        "id": "AU-REPORT",
        "metric": "summary + paper-lab",
        "decision": "PROMOTE",
        "note": "docs + anti-FP table · real-eval section",
    },
    {
        "stage": "AU6",
        "id": "AU-FREEZE",
        "metric": "lock outcomes",
        "decision": "PROMOTE",
        "note": "COMPLETE+FROZEN · no Wave AV invent",
    },
)

AU_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-au-session.md",
    "docs/results/nano-lm/formal-hprodhard-prodhard.md",
    "docs/results/nano-lm/formal-hshipreal-shipreal.md",
    "docs/results/nano-lm/shipreal-demo.md",
    "docs/results/nano-lm/formal-hnanogen5-nanogen5.md",
    "docs/results/nano-lm/wave-au-real-eval.md",
    "docs/results/nano-lm/wave-au-summary.md",
    "docs/results/nano-lm/paper-lab-wave-au.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AU_REPORT_MARKERS: tuple[str, ...] = (
    "H-PRODHARD",
    "H-SHIPREAL",
    "H-NANOGEN5",
    "AU-REAL-EVAL",
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
    "anti-FP",
    "PROMOTE",
    "snippet-prefix",
    "gibberish-tail",
    "STRICT",
    "ablated",
    "5.5",
    "not unlabeled open chat",
    "AF packaged stack",
    "product layer",
    "SAFE",
)


def decide_au_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AU_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AU report evidence
    WHEN deciding AU-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AU_ID}: {AU_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AU_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AU_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking AU scoreboard
    THEN every stage id appears with Metric column.
    """
    body = str(text)
    if "Metric" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid.startswith("AU-"):
            if f"**{mid}**" not in body:
                return False
    return True


def antifp_section_ok(text: str) -> bool:
    """
    GIVEN summary body
    WHEN checking anti-FP evidence block
    THEN require modes + LOOKUP≠IQ + NANOGEN5 honesty.
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
        "H-NANOGEN5",
        "snippet-prefix",
        "gibberish-tail",
        "SAFE",
        "unlabeled open chat",
    )
    return all(m in body for m in need)


def realeval_section_ok(text: str) -> bool:
    """Require explicit real-eval section with battery + STRICT gen claim."""
    body = str(text).lower()
    return (
        "real-eval" in body
        and "battery" in body
        and "nanogen5" in body
        and "prodhard" in body
        and "shipreal" in body
    )


def render_wave_au_summary() -> str:
    lines = [
        "# Wave AU — Caminho A harden + Nano STRICT generative gate "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §5 · Paper-lab: "
        "[paper-lab-wave-au.md](paper-lab-wave-au.md) · "
        "Real-eval: [wave-au-real-eval.md](wave-au-real-eval.md) · "
        "Freeze: [au-freeze.md](au-freeze.md) · "
        "[formal-haufreeze-au-freeze.md](formal-haufreeze-au-freeze.md)  ",
        "> Parent: Wave AT **AT-FREEZE** reopen · Ship claim: "
        f"**{SHIP_CLAIM}**",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + AU_THESIS
        + ".**",
        "",
        "## Stage scoreboard (product + generative)",
        "",
        "| # | ID | Metric | Decision | Note |",
        "|---|-----|--------|----------|------|",
    ]
    for row in AU_SCOREBOARD:
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
            "H-SHIPREAL · AU-REAL-EVAL known_lookup · WRAP_LOOKUP |",
            "| PEAK extractive ≠ open-chat | "
            "H-SHIPREAL PEAK · H-PRODHARD usable span · NANOGEN5 peak compare |",
            "| DECODE arm `wall_ms>0` · `n_new>0` | "
            "H-SHIPREAL WRAP_DECODE · NANOGEN5 ablated · AU-ASK-05 |",
            "| ABSTAIN refuse junk / OOD / near-miss | "
            "AU-REAL-EVAL OOD·junk·SegWit/BIP-39 refuse · FH honesty |",
            "| SAFE ≠ answer quality | "
            "H-PRODHARD cites ADVSAFE · SAFE≠quality |",
            "| STRICT ablated gen PROMOTE honesty | "
            "**H-NANOGEN5** strict **5.5** · snippet-prefix · "
            "gibberish-tail · not unlabeled open chat |",
            "| Modes always visible + content bars | "
            "**H-SHIPREAL** LOOKUP·PEAK·DECODE·ABSTAIN |",
            "| Generative claim gated | "
            "AU-REAL-EVAL · claim only after AU3 STRICT PROMOTE |",
            "| Telemetry keys | `mode` · `wall_ms` · `n_new` · "
            "`product_mode` |",
            "",
            "## Honest claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| Caminho A live-audit | **H-PRODHARD** PROMOTE |",
            "| Mode+content ask/apps/ship | **H-SHIPREAL** PROMOTE — 4/4 |",
            "| North-star generative | **H-NANOGEN5** PROMOTE — "
            "strict ablated **5.5** · gibberish-tail |",
            "| Final real eval | **AU-REAL-EVAL** PROMOTE — "
            "battery **7/7** |",
            "| Ship claim | **" + SHIP_CLAIM + "** |",
            "| “Unlabeled open chat / GPT-class ≤5M” | **False** |",
            "",
            "## Real-eval section",
            "",
            "| Arm | What was measured | Outcome |",
            "|-----|-------------------|---------|",
            "| Product (PRODHARD) | near-miss · para · PEAK usable · "
            "FH · latency · KB | **PROMOTE** |",
            "| Product (SHIPREAL) | ask · apps · ship/demo modes+content | "
            "**PROMOTE** 4/4 |",
            "| Generative (NANOGEN5) | STRICT ablated vs NANOGEN4 soft 5.5 | "
            "**PROMOTE** (strict **5.5** · gibberish-tail + F1/HITL) |",
            "| Live ask battery | LOOKUP·PEAK·DECODE·ABSTAIN + "
            "human-para · near-miss | **PASS** 7/7 |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:au:report",
            "npm run nano:au:session",
            "npm run nano:prodhard",
            "npm run nano:shipreal",
            "npm run nano:nanogen5",
            "npm run nano:au:real-eval",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave AV without "
            "lab-book reopen · sell PEAK/bank-grounded as unlabeled open-chat · "
            "sell SAFE mean as IQ · sell STRICT ablated as GPT-class · "
            "gold-substring PROMOTE · gibberish-tail pass · "
            "CTX/SMART/FAST/APP letter clones without named product hole · "
            "rewrite AT/AS/AR/AQ locked outcomes.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_au() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AU (Caminho A harden + Nano STRICT gen)",
            "",
            "> Companion to [wave-au-summary.md](wave-au-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · "
            "Real-eval: [wave-au-real-eval.md](wave-au-real-eval.md) · "
            "Freeze: [au-freeze.md](au-freeze.md) · "
            "[formal-haufreeze-au-freeze.md](formal-haufreeze-au-freeze.md) · "
            "Parent: [at-freeze.md](at-freeze.md) · "
            f"Ship: **{SHIP_CLAIM}**",
            "",
            "## Question",
            "",
            "After AT froze Caminho A + soft ablated DECODE 5.5 "
            "(snippet-prefix), can Wave AU **harden product under live "
            "human metrics** (PRODHARD + SHIPREAL) **and** clear one "
            "STRICT generative lift (gibberish-tail + F1/HITL) under ≤5M "
            "**without** unlabeled open-chat / GPT-class overclaim?",
            "",
            "## Answer",
            "",
            "**Yes for both legs — with stricter claim language.** "
            "H-PRODHARD · H-SHIPREAL PROMOTE. **H-NANOGEN5 PROMOTE** "
            "(strict ablated **5.5**, snippet-prefix + gibberish-tail, "
            "meets NANOGEN4 soft 5.5 under STRICT judge). "
            "AU-REAL-EVAL PROMOTE (live battery 7/7, near-miss refuse, "
            "human-para). "
            f"Ship claim: **{SHIP_CLAIM}**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-PRODHARD | Live-audit debts closed → PROMOTE |",
            "| H-SHIPREAL | Modes+content 4/4 → PROMOTE |",
            "| H-NANOGEN5 | Strict ablated 5.5 · gibberish-tail → PROMOTE |",
            "| AU-REAL-EVAL | Live battery 7/7 · anti-FP → PROMOTE |",
            "| AU-REPORT | Summary + paper-lab + anti-FP → PROMOTE |",
            "| AU-FREEZE | Outcomes lock — no Wave AV invent |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP / SHIPREAL must never be sold as generative IQ. PEAK and "
            "bank-grounded short stay compare-only. DECODE telemetry "
            "(`wall_ms`, `n_new`) is mandatory. SAFE≠quality. "
            "Gold-substring alone ≠ generative PROMOTE; gibberish-tail fails. "
            "**H-NANOGEN5** unlocks **STRICT ablated DECODE "
            "(snippet-prefix + gibberish-tail)** language only — not "
            "unlabeled open chat / GPT-class.",
            "",
            "## Takeaway one-liner",
            "",
            "**AU = Caminho A hardened + STRICT ablated DECODE gate "
            "cleared (5.5); ship AF+AQ+AS trust + STRICT snippet-prefix "
            "DECODE — not unlabeled open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-au-summary.md](wave-au-summary.md) · "
            "[wave-au-real-eval.md](wave-au-real-eval.md) · "
            "[wave-au-session.md](wave-au-session.md) · "
            "[at-freeze.md](at-freeze.md)  ",
            "- Formals: PRODHARD · SHIPREAL · NANOGEN5  ",
            "- Demo: [shipreal-demo.md](shipreal-demo.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
