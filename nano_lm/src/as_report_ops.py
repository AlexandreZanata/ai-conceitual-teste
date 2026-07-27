"""Wave AS REPORT: public closeout (product trust + generative honesty)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "AS_ID",
    "AS_THESIS",
    "AS_EVIDENCE",
    "AS_REPORT_MARKERS",
    "AS_SCOREBOARD",
    "SHIP_CLAIM",
    "decide_as_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "render_wave_as_summary",
    "render_paper_lab_wave_as",
]

AS_ID = "AS-REPORT"
SHIP_CLAIM = (
    "AF packaged stack + AQ product layer — not open chat LM"
)
AS_THESIS = (
    "Wave AS product trust on Caminho A: ASKABSTAIN·SEMFIX·ADVSAFE·"
    "PARAEXT2·METRICS·SHIPUI PROMOTE; NANOGEN3 HOLD (ablated 4.3 · "
    "peak_only); AS-DUAL-HITL PROMOTE (product pass · gen locked); "
    "generative/open-chat/mini-AGI locked; ship " + SHIP_CLAIM
)

AS_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AS0",
        "id": "SESSION",
        "metric": "packs frozen",
        "decision": "PROMOTE",
        "note": "ADVSAFE · PARAEXT2 · ASKABSTAIN · SEMFIX · NANOGEN3 · metrics",
    },
    {
        "stage": "AS1",
        "id": "H-ASKABSTAIN",
        "metric": "OOD abstain on default ask · FH 0",
        "decision": "PROMOTE",
        "note": "NO_ANSWER / ABSTAIN labeled · LOOKUP kept",
    },
    {
        "stage": "AS2",
        "id": "H-SEMFIX",
        "metric": "ADVREG-01/05 class FH 0",
        "decision": "PROMOTE",
        "note": "negation / contrast / margin · known SEMWRAP kept",
    },
    {
        "stage": "AS3",
        "id": "H-ADVSAFE",
        "metric": "false-hit 0/20",
        "decision": "PROMOTE",
        "note": "SAFE≠quality · cite AR-ADVREG-01/05",
    },
    {
        "stage": "AS4",
        "id": "H-PARAEXT2",
        "metric": "hit 0.80 ≥ 0.70",
        "decision": "PROMOTE",
        "note": "FH 0 · misses listed · ≠ bank stuffing",
    },
    {
        "stage": "AS5",
        "id": "H-METRICS",
        "metric": "p50/p99 tetrad + KB holes",
        "decision": "PROMOTE",
        "note": "LOOKUP·PEAK·DECODE·ABSTAIN published",
    },
    {
        "stage": "AS6",
        "id": "H-SHIPUI",
        "metric": "4/4 modes visible",
        "decision": "PROMOTE",
        "note": "LOOKUP · PEAK · DECODE · ABSTAIN on ask+demo",
    },
    {
        "stage": "AS7",
        "id": "H-NANOGEN3",
        "metric": "ablated gen 4.3",
        "decision": "HOLD",
        "note": "bar 5.0 unmet · peak_only · not open chat",
    },
    {
        "stage": "AS8",
        "id": "AS-DUAL-HITL",
        "metric": "product pillars + apps",
        "decision": "PROMOTE",
        "note": "all core PROMOTE · PARAEXT2 PROMOTE · gen locked",
    },
    {
        "stage": "AS9",
        "id": "AS-REPORT",
        "metric": "summary + paper-lab",
        "decision": "PROMOTE",
        "note": "docs + anti-FP table · real-eval",
    },
    {
        "stage": "AS10",
        "id": "AS-FREEZE",
        "metric": "lock outcomes",
        "decision": "PROMOTE",
        "note": "COMPLETE+FROZEN · no Wave AT invent",
    },
)

AS_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-as-session.md",
    "docs/results/nano-lm/formal-haskabstain-askabstain.md",
    "docs/results/nano-lm/formal-hsemfix-semfix.md",
    "docs/results/nano-lm/formal-hadvsafe-advsafe.md",
    "docs/results/nano-lm/formal-hparaext2-paraext2.md",
    "docs/results/nano-lm/formal-hmetrics-metrics.md",
    "docs/results/nano-lm/formal-hshipui-shipui.md",
    "docs/results/nano-lm/shipui-demo.md",
    "docs/results/nano-lm/formal-hnanogen3-nanogen3.md",
    "docs/results/nano-lm/wave-as-dual-hitl.md",
    "docs/results/nano-lm/wave-as-summary.md",
    "docs/results/nano-lm/paper-lab-wave-as.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AS_REPORT_MARKERS: tuple[str, ...] = (
    "H-ASKABSTAIN",
    "H-SEMFIX",
    "H-ADVSAFE",
    "H-PARAEXT2",
    "H-METRICS",
    "H-SHIPUI",
    "H-NANOGEN3",
    "AS-DUAL-HITL",
    "HOLD",
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


def decide_as_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AS_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AS report evidence
    WHEN deciding AS-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AS_ID}: {AS_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AS_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AS_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking AS scoreboard
    THEN every stage id appears with Metric column.
    """
    body = str(text)
    if "Metric" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid.startswith("AS-"):
            if f"**{mid}**" not in body:
                return False
    return True


def antifp_section_ok(text: str) -> bool:
    """
    GIVEN summary body
    WHEN checking anti-FP evidence block
    THEN require modes + LOOKUP≠IQ + NANOGEN3 HOLD honesty.
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
        "H-NANOGEN3",
        "HOLD",
        "SAFE",
    )
    return all(m in body for m in need)


def render_wave_as_summary() -> str:
    lines = [
        "# Wave AS — Product Science fix + Nano Generative "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §5 · Paper-lab: "
        "[paper-lab-wave-as.md](paper-lab-wave-as.md) · "
        "HITL: [wave-as-dual-hitl.md](wave-as-dual-hitl.md) · "
        "Freeze: [as-freeze.md](as-freeze.md) · "
        "[formal-hasfreeze-as-freeze.md](formal-hasfreeze-as-freeze.md)  ",
        "> Parent: Wave AR **AR-FREEZE** reopen · Ship claim: "
        f"**{SHIP_CLAIM}**",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + AS_THESIS
        + ".**",
        "",
        "## Stage scoreboard (product trust)",
        "",
        "| # | ID | Metric | Decision | Note |",
        "|---|-----|--------|----------|------|",
    ]
    for row in AS_SCOREBOARD:
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
            "SHIPUI · DUAL-HITL apps · WRAP_LOOKUP |",
            "| PEAK extractive ≠ open-chat | "
            "SHIPUI PEAK · NANOGEN3 peak compare only |",
            "| DECODE arm `wall_ms>0` · `n_new>0` | "
            "SHIPUI DECODE · NANOGEN3 ablated |",
            "| ABSTAIN refuse junk — not IQ | "
            "**H-ASKABSTAIN** OOD on default ask · FH **0** |",
            "| SAFE ≠ answer quality | "
            "**H-ADVSAFE** SAFE≠quality · mean not sold as IQ |",
            "| Ablated gen HOLD honesty | "
            "**H-NANOGEN3** ablated **4.3** · peak_only |",
            "| Modes always visible | "
            "**H-SHIPUI** LOOKUP·PEAK·DECODE·ABSTAIN |",
            "| Generative claim locked while HOLD | "
            "AS-DUAL-HITL · ship claim not open chat |",
            "| SEMWRAP near-miss fixed | "
            "**H-SEMFIX** ADVREG-01/05 class FH **0** |",
            "| Telemetry keys | `mode` · `wall_ms` · `n_new` · "
            "`product_mode` |",
            "",
            "## Honest product claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| Refuse junk on default ask | **H-ASKABSTAIN** PROMOTE |",
            "| SEMWRAP polarity/negation | **H-SEMFIX** PROMOTE |",
            "| Adversary regression | **H-ADVSAFE** PROMOTE — "
            "FH **0**/20 · SAFE≠quality |",
            "| External paraphrase | **H-PARAEXT2** PROMOTE — "
            "hit **0.80** · FH **0** |",
            "| Latency / KB holes | **H-METRICS** PROMOTE |",
            "| Mode-visible ask+demo | **H-SHIPUI** PROMOTE — 4/4 |",
            "| North-star generative | **H-NANOGEN3** HOLD — "
            "ablated **4.3** · not open chat |",
            "| Final dual HITL | **AS-DUAL-HITL** PROMOTE — "
            "product pass · gen locked |",
            "| Ship claim | **" + SHIP_CLAIM + "** |",
            "| “Open chat / mini-AGI ≤5M” | **False** — AS7 HOLD |",
            "",
            "## Real-eval section",
            "",
            "| Arm | What was measured | Outcome |",
            "|-----|-------------------|---------|",
            "| Product trust | ASKABSTAIN · SEMFIX · ADVSAFE · "
            "PARAEXT2 · METRICS · SHIPUI · apps | **PROMOTE / PASS** |",
            "| Generative | NANOGEN3 ablated vs NANOGEN2 4.3 | "
            "**HOLD** (4.3 < 5.0 · peak_only) |",
            "| Dual HITL | composite + claim honesty | "
            "**PROMOTE** · gen claim locked |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:as:report",
            "npm run nano:as:session",
            "npm run nano:askabstain",
            "npm run nano:semfix",
            "npm run nano:advsafe",
            "npm run nano:paraext2",
            "npm run nano:metrics",
            "npm run nano:shipui",
            "npm run nano:nanogen3",
            "npm run nano:as:dual-hitl",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave AT without "
            "lab-book reopen · claim open chat / mini-AGI while H-NANOGEN3 HOLD · "
            "sell PEAK/bank-grounded as open-chat IQ · sell SAFE mean as IQ · "
            "sell product PROMOTE as generative unlock · CTX/SMART/FAST/APP "
            "letter clones without named product hole.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_as() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AS (Product Science fix + Nano Generative)",
            "",
            "> Companion to [wave-as-summary.md](wave-as-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · HITL: "
            "[wave-as-dual-hitl.md](wave-as-dual-hitl.md) · "
            "Freeze: [as-freeze.md](as-freeze.md) · "
            "[formal-hasfreeze-as-freeze.md](formal-hasfreeze-as-freeze.md) · "
            "Parent: [ar-freeze.md](ar-freeze.md) · "
            f"Ship: **{SHIP_CLAIM}**",
            "",
            "## Question",
            "",
            "After AR froze product deepen with ADVREG KILL and NANOGEN2 HOLD, "
            "can Wave AS **fix the default ask path** (abstain wired · "
            "SEMWRAP near-miss · adversary SAFE · external para · metrics · "
            "mode UI) and attempt one ablated generative lift **without** "
            "letter-clone theater or unlocking mini-AGI / open-chat under ≤5M?",
            "",
            "## Answer",
            "",
            "**Yes for product trust; no for generative unlock.** "
            "ASKABSTAIN · SEMFIX · ADVSAFE · PARAEXT2 · METRICS · SHIPUI "
            "PROMOTE. **H-NANOGEN3 HOLD** (ablated **4.3**, peak_only) keeps "
            "generative ship language locked. AS-DUAL-HITL PROMOTE documents "
            "product pass with gen locked. "
            f"Ship claim: **{SHIP_CLAIM}**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-ASKABSTAIN | Default-ask OOD abstain · FH 0 → PROMOTE |",
            "| H-SEMFIX | ADVREG-01/05 class FH 0 → PROMOTE |",
            "| H-ADVSAFE | false-hit 0/20 · SAFE≠quality → PROMOTE |",
            "| H-PARAEXT2 | hit 0.80 · FH 0 → PROMOTE |",
            "| H-METRICS | tetrad p50/p99 + KB holes → PROMOTE |",
            "| H-SHIPUI | LOOKUP·PEAK·DECODE·ABSTAIN visible → PROMOTE |",
            "| H-NANOGEN3 | Ablated 4.3 → HOLD; peak_only |",
            "| AS-DUAL-HITL | Product pass · gen locked → PROMOTE |",
            "| AS-REPORT | Summary + paper-lab + anti-FP → PROMOTE |",
            "| AS-FREEZE | Outcomes locked — no Wave AT invent |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP / SHIPUI / DUAL-HITL must never be sold as generative "
            "IQ. PEAK and bank-grounded short are compare-only. DECODE "
            "telemetry (`wall_ms`, `n_new`) is mandatory. SAFE≠quality. "
            "**H-NANOGEN3 HOLD** is the honest north-star bar — peak_only "
            "is comparison, not open-chat unlock.",
            "",
            "## Takeaway one-liner",
            "",
            "**AS = Caminho A product trust under anti-FP; generative bar "
            "HOLD (ablated 4.3); ship stays AF packaged stack + AQ product "
            "layer — not open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-as-summary.md](wave-as-summary.md) · "
            "[wave-as-dual-hitl.md](wave-as-dual-hitl.md) · "
            "[wave-as-session.md](wave-as-session.md) · "
            "[ar-freeze.md](ar-freeze.md)  ",
            "- Formals: ASKABSTAIN · SEMFIX · ADVSAFE · PARAEXT2 · "
            "METRICS · SHIPUI · NANOGEN3  ",
            "- Demo: [shipui-demo.md](shipui-demo.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
