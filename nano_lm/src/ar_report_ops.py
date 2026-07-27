"""Wave AR REPORT: public closeout (product deepen + generative honesty)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "AR_ID",
    "AR_THESIS",
    "AR_EVIDENCE",
    "AR_REPORT_MARKERS",
    "AR_SCOREBOARD",
    "SHIP_CLAIM",
    "decide_ar_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "render_wave_ar_summary",
    "render_paper_lab_wave_ar",
]

AR_ID = "AR-REPORT"
SHIP_CLAIM = (
    "AF packaged stack + AQ product layer — not open chat LM"
)
AR_THESIS = (
    "Wave AR product deepen on AQ: ABSTAIN·SHIPDEMO PROMOTE; "
    "PARAEXT HOLD · ADVREG KILL · NANOGEN2 HOLD (ablated 4.3 · peak_only); "
    "AR-DUAL-HITL HOLD (soft deepen); generative/open-chat/mini-AGI locked; "
    "ship " + SHIP_CLAIM
)

AR_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AR0",
        "id": "SESSION",
        "metric": "packs frozen",
        "decision": "PROMOTE",
        "note": "ext-para · advreg · abstain · ship-demo · NANOGEN2 hyp",
    },
    {
        "stage": "AR1",
        "id": "H-ABSTAIN",
        "metric": "OOD abstain 1.0 · FH 0",
        "decision": "PROMOTE",
        "note": "NO_ANSWER / ABSTAIN labeled",
    },
    {
        "stage": "AR2",
        "id": "H-SHIPDEMO",
        "metric": "4/4 modes visible",
        "decision": "PROMOTE",
        "note": "LOOKUP · PEAK · DECODE · ABSTAIN",
    },
    {
        "stage": "AR3",
        "id": "H-PARAEXT",
        "metric": "hit 0.65 < 0.70",
        "decision": "HOLD",
        "note": "FH 0 · misses reported · ≠ AQ-PARA",
    },
    {
        "stage": "AR4",
        "id": "H-ADVREG",
        "metric": "false-hit 2/20",
        "decision": "KILL",
        "note": "SAFE≠quality documented · near-miss leaks",
    },
    {
        "stage": "AR5",
        "id": "H-NANOGEN2",
        "metric": "ablated gen 4.3",
        "decision": "HOLD",
        "note": "beats NANOGEN 4.0 · peak/bank compare only",
    },
    {
        "stage": "AR6",
        "id": "AR-DUAL-HITL",
        "metric": "core pass · soft deepen",
        "decision": "HOLD",
        "note": "ABSTAIN/SHIPDEMO/apps · PARAEXT/ADVREG soft · gen locked",
    },
    {
        "stage": "AR7",
        "id": "AR-REPORT",
        "metric": "summary + paper-lab",
        "decision": "PROMOTE",
        "note": "docs + anti-FP table · real-eval",
    },
    {
        "stage": "AR8",
        "id": "AR-FREEZE",
        "metric": "lock outcomes",
        "decision": "PROMOTE",
        "note": "pending runner · no Wave AS invent",
    },
)

AR_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ar-session.md",
    "docs/results/nano-lm/formal-habstain-abstain.md",
    "docs/results/nano-lm/formal-hshipdemo-shipdemo.md",
    "docs/results/nano-lm/shipdemo-demo.md",
    "docs/results/nano-lm/formal-hparaext-paraext.md",
    "docs/results/nano-lm/formal-hadvreg-advreg.md",
    "docs/results/nano-lm/formal-hnanogen2-nanogen2.md",
    "docs/results/nano-lm/wave-ar-dual-hitl.md",
    "docs/results/nano-lm/wave-ar-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ar.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AR_REPORT_MARKERS: tuple[str, ...] = (
    "H-ABSTAIN",
    "H-SHIPDEMO",
    "H-PARAEXT",
    "H-ADVREG",
    "H-NANOGEN2",
    "AR-DUAL-HITL",
    "HOLD",
    "KILL",
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
    "anti-FP",
    "PROMOTE",
    "not open chat",
    "AF packaged stack",
    "product layer",
    "peak_only",
    "SAFE",
)


def decide_ar_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AR_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AR report evidence
    WHEN deciding AR-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AR_ID}: {AR_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AR_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AR_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking AR scoreboard
    THEN every stage id appears with Metric column.
    """
    body = str(text)
    if "Metric" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid.startswith("AR-"):
            if f"**{mid}**" not in body:
                return False
    return True


def antifp_section_ok(text: str) -> bool:
    """
    GIVEN summary body
    WHEN checking anti-FP evidence block
    THEN require modes + LOOKUP≠IQ + NANOGEN2 HOLD honesty.
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
        "H-NANOGEN2",
        "HOLD",
        "SAFE",
    )
    return all(m in body for m in need)


def render_wave_ar_summary() -> str:
    lines = [
        "# Wave AR — Product Science deepen + Nano Generative "
        "(**RESEARCH_COMPLETE · pending FREEZE**)",
        "",
        "> Lab: `.local/pesquisa.md` §5 · Paper-lab: "
        "[paper-lab-wave-ar.md](paper-lab-wave-ar.md) · "
        "HITL: [wave-ar-dual-hitl.md](wave-ar-dual-hitl.md) · "
        "Freeze: [ar-freeze.md](ar-freeze.md)  ",
        "> Parent: Wave AQ **AQ-FREEZE** reopen · Ship claim: "
        f"**{SHIP_CLAIM}**",
        "",
        "**Status: RESEARCH_COMPLETE (pending AR-FREEZE)** · Thesis: **"
        + AR_THESIS
        + ".**",
        "",
        "## Stage scoreboard (product deepen)",
        "",
        "| # | ID | Metric | Decision | Note |",
        "|---|-----|--------|----------|------|",
    ]
    for row in AR_SCOREBOARD:
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
            "SHIPDEMO · DUAL-HITL apps · WRAP_LOOKUP |",
            "| PEAK extractive ≠ open-chat | "
            "SHIPDEMO PEAK · NANOGEN2 peak compare only |",
            "| DECODE arm `wall_ms>0` · `n_new>0` | "
            "SHIPDEMO DECODE · NANOGEN2 ablated |",
            "| ABSTAIN refuse junk — not IQ | "
            "**H-ABSTAIN** OOD abstain **1.0** · FH **0** |",
            "| SAFE ≠ answer quality | "
            "**H-ADVREG** SAFE≠quality · mean not sold as IQ |",
            "| Ablated gen HOLD honesty | "
            "**H-NANOGEN2** ablated **4.3** · peak_only |",
            "| Modes always visible | "
            "**H-SHIPDEMO** LOOKUP·PEAK·DECODE·ABSTAIN |",
            "| Generative claim locked while HOLD | "
            "AR-DUAL-HITL · ship claim not open chat |",
            "| Telemetry keys | `mode` · `wall_ms` · `n_new` · "
            "`product_mode` |",
            "",
            "## Honest product claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| Refuse junk DECODE | **H-ABSTAIN** PROMOTE — "
            "OOD abstain **1.0** |",
            "| Mode-visible ship/demo | **H-SHIPDEMO** PROMOTE — 4/4 |",
            "| External paraphrase | **H-PARAEXT** HOLD — "
            "hit **0.65** < 0.70 · FH **0** |",
            "| Adversary regression | **H-ADVREG** KILL — "
            "false-hit **2**/20 · SAFE≠quality |",
            "| North-star generative | **H-NANOGEN2** HOLD — "
            "ablated **4.3** · not open chat |",
            "| Final dual HITL | **AR-DUAL-HITL** HOLD — "
            "core pass · soft deepen · gen locked |",
            "| Ship claim | **" + SHIP_CLAIM + "** |",
            "| “Open chat / mini-AGI ≤5M” | **False** — AR5 HOLD |",
            "",
            "## Real-eval section",
            "",
            "| Arm | What was measured | Outcome |",
            "|-----|-------------------|---------|",
            "| Product core | ABSTAIN · SHIPDEMO · apps LOOKUP | "
            "**PROMOTE / PASS** |",
            "| Product deepen | PARAEXT · ADVREG | "
            "**HOLD / KILL** (honest soft) |",
            "| Generative | NANOGEN2 ablated vs NANOGEN 4.0 | "
            "**HOLD** (4.3 < 5.0) |",
            "| Dual HITL | composite + claim honesty | "
            "**HOLD** · gen claim locked |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:ar:report",
            "npm run nano:ar:session",
            "npm run nano:abstain",
            "npm run nano:shipdemo",
            "npm run nano:paraext",
            "npm run nano:advreg",
            "npm run nano:nanogen2",
            "npm run nano:ar:dual-hitl",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave AS without "
            "lab-book reopen · claim open chat / mini-AGI while H-NANOGEN2 HOLD · "
            "sell PEAK/bank-grounded as open-chat IQ · sell SAFE mean as IQ · "
            "sell product soft HOLD as generative unlock.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_ar() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AR (Product deepen + Nano Generative)",
            "",
            "> Companion to [wave-ar-summary.md](wave-ar-summary.md). "
            "English lab note.  ",
            "> **Status: RESEARCH_COMPLETE (pending AR-FREEZE)** · HITL: "
            "[wave-ar-dual-hitl.md](wave-ar-dual-hitl.md) · "
            "Freeze: [ar-freeze.md](ar-freeze.md) · "
            "Parent: [aq-freeze.md](aq-freeze.md) · "
            f"Ship: **{SHIP_CLAIM}**",
            "",
            "## Question",
            "",
            "After AQ froze the product layer, can Wave AR **deepen** "
            "product honesty (abstain · ship demo · external para · "
            "adversary regression) and attempt one ablated generative lift "
            "**without** inventing letter clones or unlocking mini-AGI / "
            "open-chat claims under ≤5M?",
            "",
            "## Answer",
            "",
            "**Yes for core product honesty; no for generative unlock.** "
            "ABSTAIN and SHIPDEMO PROMOTE. PARAEXT HOLD and ADVREG KILL are "
            "honest deepen defects. **H-NANOGEN2 HOLD** (ablated **4.3**, "
            "peak_only) keeps generative ship language locked. "
            "AR-DUAL-HITL HOLD documents soft deepen without silent PROMOTE. "
            f"Ship claim: **{SHIP_CLAIM}**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-ABSTAIN | OOD abstain 1.0 · FH 0 → PROMOTE |",
            "| H-SHIPDEMO | LOOKUP·PEAK·DECODE·ABSTAIN visible → PROMOTE |",
            "| H-PARAEXT | hit 0.65 < 0.70 · FH 0 → HOLD |",
            "| H-ADVREG | false-hit 2/20 · SAFE≠quality → KILL |",
            "| H-NANOGEN2 | Ablated 4.3 → HOLD; peak/bank compare only |",
            "| AR-DUAL-HITL | Core pass · soft deepen → HOLD; gen locked |",
            "| AR-REPORT | Summary + paper-lab + anti-FP → PROMOTE |",
            "| AR-FREEZE | Pending — no Wave AS invent |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP / SHIPDEMO / DUAL-HITL must never be sold as generative "
            "IQ. PEAK and bank-grounded short are compare-only. DECODE "
            "telemetry (`wall_ms`, `n_new`) is mandatory. SAFE≠quality. "
            "**H-NANOGEN2 HOLD** is the honest north-star bar — peak_only "
            "is comparison, not open-chat unlock.",
            "",
            "## Takeaway one-liner",
            "",
            "**AR = product deepen on AQ under anti-FP; generative bar HOLD "
            "(ablated 4.3); ship stays AF packaged stack + AQ product layer "
            "— not open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-ar-summary.md](wave-ar-summary.md) · "
            "[wave-ar-dual-hitl.md](wave-ar-dual-hitl.md) · "
            "[wave-ar-session.md](wave-ar-session.md) · "
            "[aq-freeze.md](aq-freeze.md)  ",
            "- Formals: ABSTAIN · SHIPDEMO · PARAEXT · ADVREG · NANOGEN2  ",
            "- Demo: [shipdemo-demo.md](shipdemo-demo.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
