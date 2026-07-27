"""Wave AQ REPORT: public closeout (product pillars + generative honesty)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "AQ_ID",
    "AQ_THESIS",
    "AQ_EVIDENCE",
    "AQ_REPORT_MARKERS",
    "AQ_SCOREBOARD",
    "SHIP_CLAIM",
    "decide_aq_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "render_wave_aq_summary",
    "render_paper_lab_wave_aq",
]

AQ_ID = "AQ-REPORT"
SHIP_CLAIM = (
    "AF packaged stack + AQ product layer — not open chat LM"
)
AQ_THESIS = (
    "Wave AQ product science on AF: PARAHIT·ADVFP·LATP·KBCOV·MODEUI·"
    "PRODUCT-HITL PROMOTE; H-NANOGEN HOLD (ablated 4.0 · peak_only_lift); "
    "generative/open-chat/mini-AGI claims locked; ship "
    + SHIP_CLAIM
)

AQ_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AQ0",
        "id": "SESSION",
        "metric": "packs frozen",
        "decision": "PROMOTE",
        "note": "para-20 · adv-20 · latency · KB · mode charter",
    },
    {
        "stage": "AQ1",
        "id": "H-PARAHIT",
        "metric": "hit_rate 0.95 · mean 8.75",
        "decision": "PROMOTE",
        "note": "false-hit 0 · SEMWRAP paraphrase",
    },
    {
        "stage": "AQ2",
        "id": "H-ADVFP",
        "metric": "false-hit 0/20",
        "decision": "PROMOTE",
        "note": "near-miss · OOD · trap SAFE",
    },
    {
        "stage": "AQ3",
        "id": "H-LATP",
        "metric": "PEAK p50 0.0223",
        "decision": "PROMOTE",
        "note": "≤ FASTBASE hot 0.0471 · triad published",
    },
    {
        "stage": "AQ4",
        "id": "H-KBCOV",
        "metric": "coverage 100% (22/22)",
        "decision": "PROMOTE",
        "note": "6 product holes · no fake complete KB",
    },
    {
        "stage": "AQ5",
        "id": "H-MODEUI",
        "metric": "3/3 modes visible",
        "decision": "PROMOTE",
        "note": "LOOKUP · PEAK · DECODE",
    },
    {
        "stage": "AQ6",
        "id": "H-NANOGEN",
        "metric": "ablated gen 4.0",
        "decision": "HOLD",
        "note": "peak_only_lift · gen claim locked",
    },
    {
        "stage": "AQ7",
        "id": "AQ-PRODUCT-HITL",
        "metric": "pillars + apps",
        "decision": "PROMOTE",
        "note": "product PROMOTE · gen locked",
    },
    {
        "stage": "AQ8",
        "id": "AQ-REPORT",
        "metric": "summary + paper-lab",
        "decision": "PROMOTE",
        "note": "docs + anti-FP table",
    },
    {
        "stage": "AQ9",
        "id": "AQ-FREEZE",
        "metric": "lock outcomes",
        "decision": "PROMOTE",
        "note": "COMPLETE+FROZEN · no Wave AR invent",
    },
)

AQ_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-aq-session.md",
    "docs/results/nano-lm/formal-hparahit-parahit.md",
    "docs/results/nano-lm/formal-hadvfp-advfp.md",
    "docs/results/nano-lm/formal-hlatp-latp.md",
    "docs/results/nano-lm/formal-hkbcov-kbcov.md",
    "docs/results/nano-lm/formal-hmodeui-modeui.md",
    "docs/results/nano-lm/modeui-demo.md",
    "docs/results/nano-lm/formal-hnanogen-nanogen.md",
    "docs/results/nano-lm/wave-aq-product-hitl.md",
    "docs/results/nano-lm/wave-aq-summary.md",
    "docs/results/nano-lm/paper-lab-wave-aq.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AQ_REPORT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-PARAHIT",
    "H-ADVFP",
    "H-LATP",
    "H-KBCOV",
    "H-MODEUI",
    "H-NANOGEN",
    "HOLD",
    "AQ-PRODUCT-HITL",
    "LOOKUP",
    "PEAK",
    "DECODE",
    "anti-FP",
    "PROMOTE",
    "not open chat",
    "AF packaged stack",
    "product layer",
    "peak_only_lift",
)


def decide_aq_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AQ_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AQ report evidence
    WHEN deciding AQ-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AQ_ID}: {AQ_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AQ_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AQ_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking product scoreboard
    THEN every stage id appears with Metric column.
    """
    body = str(text)
    if "Metric" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid.startswith("AQ-"):
            if f"**{mid}**" not in body:
                return False
    return True


def antifp_section_ok(text: str) -> bool:
    """
    GIVEN summary body
    WHEN checking anti-FP evidence block
    THEN require mode triad + LOOKUP≠IQ + NANOGEN HOLD honesty.
    """
    body = str(text)
    need = (
        "anti-FP",
        "LOOKUP",
        "PEAK",
        "DECODE",
        "wall_ms",
        "n_new",
        "not generative IQ",
        "H-NANOGEN",
        "HOLD",
    )
    return all(m in body for m in need)


def render_wave_aq_summary() -> str:
    lines = [
        "# Wave AQ — Product Science + Nano Generative "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §5 · Paper-lab: "
        "[paper-lab-wave-aq.md](paper-lab-wave-aq.md) · "
        "HITL: [wave-aq-product-hitl.md](wave-aq-product-hitl.md) · "
        "Freeze: [aq-freeze.md](aq-freeze.md) · "
        "[formal-haqfreeze-aq-freeze.md](formal-haqfreeze-aq-freeze.md)  ",
        "> Parent: Wave AP **AP-FREEZE** reopen · Ship claim: "
        f"**{SHIP_CLAIM}**",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + AQ_THESIS
        + ".**",
        "",
        "## Stage scoreboard (product science)",
        "",
        "| # | ID | Metric | Decision | Note |",
        "|---|-----|--------|----------|------|",
    ]
    for row in AQ_SCOREBOARD:
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
            "PARAHIT · PRODUCT-HITL · MODEUI `mode=LOOKUP` |",
            "| PEAK extractive ≠ open-chat | "
            "LATP · MODEUI PEAK · NANOGEN peak compare only |",
            "| DECODE arm `wall_ms>0` · `n_new>0` | "
            "LATP DECODE · MODEUI DECODE · NANOGEN ablated |",
            "| LOOKUP high score — not generative IQ | "
            "PARAHIT 0.95 · LOOKUP mean 9.0 with gen HOLD |",
            "| Ablated gen HOLD honesty | "
            "**H-NANOGEN** ablated **4.0** · peak_only_lift |",
            "| Modes always visible | **H-MODEUI** LOOKUP·PEAK·DECODE |",
            "| Generative claim locked while HOLD | "
            "AQ-PRODUCT-HITL · ship claim not open chat |",
            "| Telemetry keys | `mode` · `wall_ms` · `n_new` · "
            "`product_mode` |",
            "",
            "## Honest product claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| Paraphrase robustness | **H-PARAHIT** PROMOTE — "
            "hit_rate **0.95** · false-hit **0** |",
            "| Adversary safety | **H-ADVFP** PROMOTE — false-hit **0**/20 |",
            "| Latency triad published | **H-LATP** PROMOTE — "
            "PEAK p50 **0.0223** ≤ FASTBASE hot |",
            "| KB coverage honest | **H-KBCOV** PROMOTE — "
            "100% registry + **6** product holes |",
            "| Mode-visible UI | **H-MODEUI** PROMOTE — 3/3 |",
            "| North-star generative | **H-NANOGEN** HOLD — "
            "ablated **4.0** · not open chat |",
            "| Final product HITL | **AQ-PRODUCT-HITL** PROMOTE — "
            "gen claim locked |",
            "| Ship claim | **" + SHIP_CLAIM + "** |",
            "| “Open chat / mini-AGI ≤5M” | **False** — AQ6 HOLD |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:aq:freeze",
            "npm run nano:aq:report",
            "npm run nano:aq:session",
            "npm run nano:parahit",
            "npm run nano:advfp",
            "npm run nano:latp",
            "npm run nano:kbcov",
            "npm run nano:modeui",
            "npm run nano:nanogen",
            "npm run nano:aq:product-hitl",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave AR without "
            "lab-book reopen · claim open chat / mini-AGI while H-NANOGEN HOLD · "
            "sell PEAK as open-chat IQ · sell product PROMOTE as generative unlock.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_aq() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AQ (Product Science + Nano Generative)",
            "",
            "> Companion to [wave-aq-summary.md](wave-aq-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · HITL: "
            "[wave-aq-product-hitl.md](wave-aq-product-hitl.md) · "
            "Freeze: [aq-freeze.md](aq-freeze.md) · "
            "[formal-haqfreeze-aq-freeze.md](formal-haqfreeze-aq-freeze.md) · "
            "Parent: [ap-freeze.md](ap-freeze.md) · "
            f"Ship: **{SHIP_CLAIM}**",
            "",
            "## Question",
            "",
            "After AP froze the AF packaged stack, can a **product-science** "
            "wave (paraphrase · adversary · latency · KB · modes · apps) "
            "ship measurable UX gains **without** unlocking false "
            "generative / open-chat / mini-AGI claims under ≤5M?",
            "",
            "## Answer",
            "",
            "**Yes for product; no for generative.** AQ1–AQ5 and AQ7 "
            "PROMOTE the product layer. **H-NANOGEN HOLD** (ablated gen "
            "**4.0**, peak_only_lift) keeps generative ship language locked. "
            f"Ship claim: **{SHIP_CLAIM}**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-PARAHIT | hit_rate 0.95 · false-hit 0 → PROMOTE |",
            "| H-ADVFP | false-hit 0/20 · contrast reject → PROMOTE |",
            "| H-LATP | triad p50/p99 · no FASTBASE regress → PROMOTE |",
            "| H-KBCOV | 22/22 + 6 product holes → PROMOTE |",
            "| H-MODEUI | LOOKUP·PEAK·DECODE visible → PROMOTE |",
            "| H-NANOGEN | Ablated 4.0 → HOLD; peak compare only |",
            "| AQ-PRODUCT-HITL | Product pillars+apps → PROMOTE; gen locked |",
            "| AQ-REPORT | Summary + paper-lab + anti-FP → PROMOTE |",
            "| AQ-FREEZE | Outcomes locked — no Wave AR invent |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP and product HITL PROMOTE must never be sold as generative "
            "IQ. PEAK extractive walls are labeled PEAK. DECODE telemetry "
            "(`wall_ms`, `n_new`) is mandatory. **H-NANOGEN HOLD** is the "
            "honest north-star bar — peak_only_lift is comparison, not "
            "open-chat unlock.",
            "",
            "## Takeaway one-liner",
            "",
            "**AQ = product layer on AF under anti-FP; generative bar HOLD "
            "(ablated 4.0); ship stays AF packaged stack + AQ product layer "
            "— not open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-aq-summary.md](wave-aq-summary.md) · "
            "[wave-aq-product-hitl.md](wave-aq-product-hitl.md) · "
            "[wave-aq-session.md](wave-aq-session.md) · "
            "[aq-freeze.md](aq-freeze.md) · "
            "[ap-freeze.md](ap-freeze.md)  ",
            "- Formals: PARAHIT · ADVFP · LATP · KBCOV · MODEUI · NANOGEN  ",
            "- Demo: [modeui-demo.md](modeui-demo.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
