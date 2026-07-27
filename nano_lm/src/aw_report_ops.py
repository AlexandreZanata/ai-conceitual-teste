"""Wave AW REPORT: public closeout (Caminho A keep + honest NANOGEN7 HOLD)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from aw_session_ops import AW0_SHIP_LOCK

__all__ = [
    "AW_ID",
    "AW_THESIS",
    "AW_EVIDENCE",
    "AW_REPORT_MARKERS",
    "AW_SCOREBOARD",
    "SHIP_CLAIM",
    "decide_aw_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "realeval_section_ok",
    "render_wave_aw_summary",
    "render_paper_lab_wave_aw",
]

AW_ID = "AW-REPORT"
SHIP_CLAIM = AW0_SHIP_LOCK
AW_THESIS = (
    "Wave AW dual track: H-PRODKEEP·H-SHIPKEEP PROMOTE (Caminho A keep · "
    "pressure-para ≠ AV/AU · DECODE content law); H-NANOGEN7 HOLD "
    "(TAC true_continue=0 · span-fallback ≠ gen IQ); AW-REAL-EVAL PROMOTE "
    "(live battery 8/8 · gen locked); ship " + SHIP_CLAIM
)

AW_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AW0",
        "id": "SESSION",
        "metric": "packs frozen",
        "decision": "PROMOTE",
        "note": "product-keep · pressure-para · NANOGEN7 TAC hyp · true-eval",
    },
    {
        "stage": "AW1",
        "id": "H-PRODKEEP",
        "metric": "Caminho A keep bars held",
        "decision": "PROMOTE",
        "note": "pressure-para · FH 0 · p50/p99 · KB · DECODE ≠ telemetry-ok",
    },
    {
        "stage": "AW2",
        "id": "H-SHIPKEEP",
        "metric": "modes+content honest",
        "decision": "PROMOTE",
        "note": "LOOKUP·PEAK·DECODE·ABSTAIN · DECODE usable/ABSTAIN · no unlabeled",
    },
    {
        "stage": "AW3",
        "id": "H-NANOGEN7",
        "metric": "TAC true_continue ablated 4.0",
        "decision": "HOLD",
        "note": "bar unmet · teacher top-k 0 · span-fallback ≠ gen · not NANOGEN6 rename",
    },
    {
        "stage": "AW4",
        "id": "AW-REAL-EVAL",
        "metric": "live ask battery 8/8",
        "decision": "PROMOTE",
        "note": "product pass · gen locked (AW3 HOLD) · anti-FP · prod=eval",
    },
    {
        "stage": "AW5",
        "id": "AW-REPORT",
        "metric": "summary + paper-lab",
        "decision": "PROMOTE",
        "note": "docs + anti-FP table · real-eval section",
    },
    {
        "stage": "AW6",
        "id": "AW-FREEZE",
        "metric": "lock outcomes",
        "decision": "PROMOTE",
        "note": "COMPLETE+FROZEN · no Wave AX invent",
    },
)

AW_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-aw-session.md",
    "docs/results/nano-lm/formal-hprodkeep-prodkeep.md",
    "docs/results/nano-lm/formal-hshipkeep-shipkeep.md",
    "docs/results/nano-lm/shipkeep-demo.md",
    "docs/results/nano-lm/formal-hnanogen7-nanogen7.md",
    "docs/results/nano-lm/wave-aw-real-eval.md",
    "docs/results/nano-lm/wave-aw-summary.md",
    "docs/results/nano-lm/paper-lab-wave-aw.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AW_REPORT_MARKERS: tuple[str, ...] = (
    "H-PRODKEEP",
    "H-SHIPKEEP",
    "H-NANOGEN7",
    "AW-REAL-EVAL",
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
    "anti-FP",
    "PROMOTE",
    "HOLD",
    "true_continue",
    "span-fallback",
    "TAC",
    "snippet-prefix",
    "gibberish-tail",
    "STRICT",
    "not unlabeled open chat",
    "AF packaged stack",
    "product layer",
    "SAFE",
)


def decide_aw_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AW_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AW report evidence
    WHEN deciding AW-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AW_ID}: {AW_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AW_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AW_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking AW scoreboard
    THEN every stage id appears with Metric column.
    """
    body = str(text)
    if "Metric" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid.startswith("AW-"):
            if f"**{mid}**" not in body:
                return False
    return True


def antifp_section_ok(text: str) -> bool:
    """
    GIVEN summary body
    WHEN checking anti-FP evidence block
    THEN require modes + LOOKUP≠IQ + NANOGEN7 honesty (span-fallback ≠ gen).
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
        "H-NANOGEN7",
        "span-fallback",
        "true_continue",
        "TAC",
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
        and "nanogen7" in body
        and "prodkeep" in body
        and "shipkeep" in body
        and "span-fallback" in body
        and "tac" in body
    )


def render_wave_aw_summary() -> str:
    lines = [
        "# Wave AW — Caminho A keep + Nano TAC honesty "
        "(**RESEARCH COMPLETE** — pending FREEZE)",
        "",
        "> Lab: `.local/pesquisa.md` §2 · Paper-lab: "
        "[paper-lab-wave-aw.md](paper-lab-wave-aw.md) · "
        "Real-eval: [wave-aw-real-eval.md](wave-aw-real-eval.md) · "
        "Freeze: [aw-freeze.md](aw-freeze.md) · "
        "[formal-hawfreeze-aw-freeze.md](formal-hawfreeze-aw-freeze.md)  ",
        "> Parent: Wave AV **AV-FREEZE** · Ship claim: "
        f"**{SHIP_CLAIM}**",
        "",
        "**Status: RESEARCH COMPLETE** (AW6 FREEZE next) · Thesis: **"
        + AW_THESIS
        + ".**",
        "",
        "## Stage scoreboard (product + generative)",
        "",
        "| # | ID | Metric | Decision | Note |",
        "|---|-----|--------|----------|------|",
    ]
    for row in AW_SCOREBOARD:
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
            "H-SHIPKEEP · AW-REAL-EVAL known_lookup · WRAP_LOOKUP |",
            "| PEAK extractive ≠ open-chat | "
            "H-SHIPKEEP PEAK · H-PRODKEEP usable span · NANOGEN7 peak compare |",
            "| DECODE arm `wall_ms>0` · `n_new>0` | "
            "H-SHIPKEEP WRAP_DECODE · NANOGEN7 TAC ablated · AW-ASK-05/08 |",
            "| DECODE gibberish ≠ content_ok | "
            "H-PRODKEEP · H-SHIPKEEP junk→ABSTAIN · AW-ASK-08 |",
            "| ABSTAIN refuse junk / OOD / near-miss | "
            "AW-REAL-EVAL OOD·junk·SegWit/BIP-39 refuse · FH honesty |",
            "| SAFE ≠ answer quality | "
            "H-PRODKEEP cites ADVSAFE · SAFE≠quality |",
            "| True-gen HOLD honesty | "
            "**H-NANOGEN7** HOLD · TAC true_continue=0 · "
            "span-fallback ≠ gen IQ · not unlabeled open chat |",
            "| Modes always visible + content bars | "
            "**H-SHIPKEEP** LOOKUP·PEAK·DECODE·ABSTAIN |",
            "| Generative claim gated | "
            "AW-REAL-EVAL · TAC unlock only if AW3 PROMOTE |",
            "| Telemetry keys | `mode` · `wall_ms` · `n_new` · "
            "`product_mode` |",
            "",
            "## Honest claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| Caminho A keep | **H-PRODKEEP** PROMOTE |",
            "| Mode+content ask/apps/ship | **H-SHIPKEEP** PROMOTE |",
            "| North-star generative | **H-NANOGEN7** HOLD — "
            "TAC true_continue unmet · span-fallback ≠ gen |",
            "| Final real eval | **AW-REAL-EVAL** PROMOTE — "
            "battery **8/8** · gen locked |",
            "| Ship claim | **" + SHIP_CLAIM + "** |",
            "| “Unlabeled open chat / GPT-class ≤5M” | **False** |",
            "| “TAC true-continue unlocked” | **False** (AW3 HOLD) |",
            "",
            "## Real-eval section",
            "",
            "| Arm | What was measured | Outcome |",
            "|-----|-------------------|---------|",
            "| Product (PRODKEEP) | pressure-para · FH · latency · KB · "
            "DECODE content | **PROMOTE** |",
            "| Product (SHIPKEEP) | ask · apps · ship/demo modes+content | "
            "**PROMOTE** |",
            "| Generative (NANOGEN7 TAC) | true_continue vs span-fallback · "
            "teacher top-k | **HOLD** (true_continue=0 · span-fallback ≠ gen IQ) |",
            "| Live ask battery | LOOKUP·PEAK·DECODE·ABSTAIN + "
            "human-para · near-miss · DECODE junk→ABSTAIN | "
            "**PASS** 8/8 |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:aw:report",
            "npm run nano:aw:session",
            "npm run nano:prodkeep",
            "npm run nano:shipkeep",
            "npm run nano:nanogen7",
            "npm run nano:aw:real-eval",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave AX without "
            "lab-book reopen · sell PEAK/bank-grounded as unlabeled open-chat · "
            "sell SAFE mean as IQ · sell span-fallback as true-continue · "
            "gold-substring PROMOTE · truncate-to-span as gen IQ · "
            "NANOGEN7 = NANOGEN6+rename · "
            "CTX/SMART/FAST/APP letter clones · rewrite AV/AU/AT/AS/AR/AQ locks.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_aw() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AW (Caminho A keep + Nano TAC honesty)",
            "",
            "> Companion to [wave-aw-summary.md](wave-aw-summary.md). "
            "English lab note.  ",
            "> **Status: RESEARCH COMPLETE** (pending AW6 FREEZE) · "
            "Real-eval: [wave-aw-real-eval.md](wave-aw-real-eval.md) · "
            "Freeze: [aw-freeze.md](aw-freeze.md) · "
            "[formal-hawfreeze-aw-freeze.md](formal-hawfreeze-aw-freeze.md) · "
            "Parent: [av-freeze.md](av-freeze.md) · "
            f"Ship: **{SHIP_CLAIM}**",
            "",
            "## Question",
            "",
            "After AV froze Caminho A ship + honest NANOGEN6 HOLD "
            "(true_continue unmet), can Wave AW **hold the product under "
            "pressure-para ≠ AV/AU** (PRODKEEP + SHIPKEEP) **and** clear one "
            "**TAC true-continue** generative lift (teacher-anchored novel "
            "continue; span-fallback ≠ gen IQ) under ≤5M **without** "
            "unlabeled open-chat / GPT-class / NANOGEN6-rename?",
            "",
            "## Answer",
            "",
            "**Yes for Caminho A keep; honest HOLD for TAC true-continue.** "
            "H-PRODKEEP · H-SHIPKEEP PROMOTE. **H-NANOGEN7 HOLD** "
            "(true_continue=0/10; teacher_topk=0; span-fallback labeled PEAK "
            "with zero gen credit — not a NANOGEN6 refuse-or-continue rename). "
            "AW-REAL-EVAL PROMOTE (live battery 8/8; gen unlock locked). "
            f"Ship claim stays AV STRICT archive: **{SHIP_CLAIM}**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-PRODKEEP | Pressure-para · FH0 · DECODE content → PROMOTE |",
            "| H-SHIPKEEP | Modes+content · DECODE usable/ABSTAIN → PROMOTE |",
            "| H-NANOGEN7 | TAC true_continue unmet · span-fallback ≠ gen → HOLD |",
            "| AW-REAL-EVAL | Live battery 8/8 · gen locked → PROMOTE |",
            "| AW-REPORT | Summary + paper-lab + anti-FP → PROMOTE |",
            "| AW-FREEZE | Outcomes lock — no Wave AX invent |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP / SHIPKEEP must never be sold as generative IQ. PEAK and "
            "span-fallback stay product/extractive credit only. DECODE "
            "telemetry (`wall_ms`, `n_new`) is mandatory but insufficient "
            "for content_ok. SAFE≠quality. Gold-substring / gibberish-tail / "
            "truncate-to-span ≠ generative PROMOTE. **H-NANOGEN7 HOLD** "
            "keeps TAC true-continue / mini-AGI language locked — ship remains "
            "AV STRICT ablated DECODE archive, not unlabeled open chat.",
            "",
            "## Takeaway one-liner",
            "",
            "**AW = Caminho A kept under pressure + TAC gen HOLDs honestly "
            "(span-fallback ≠ IQ); ship AF+AQ+AS trust + STRICT "
            "snippet-prefix DECODE — not unlabeled open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-aw-summary.md](wave-aw-summary.md) · "
            "[wave-aw-real-eval.md](wave-aw-real-eval.md) · "
            "[wave-aw-session.md](wave-aw-session.md) · "
            "[av-freeze.md](av-freeze.md)  ",
            "- Formals: PRODKEEP · SHIPKEEP · NANOGEN7  ",
            "- Demo: [shipkeep-demo.md](shipkeep-demo.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
