"""Wave AB REPORT: public closeout (per-model HITL + FIX log)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "AB_ID",
    "AB_THESIS",
    "AB_EVIDENCE",
    "AB_REPORT_MARKERS",
    "AB_HITL_SCOREBOARD",
    "decide_ab_report",
    "report_markers_ok",
    "scoreboard_ok",
    "render_wave_ab_summary",
    "render_paper_lab_wave_ab",
]

AB_ID = "AB-REPORT"
AB_THESIS = (
    "Scoped AB apps = SEMWRAP+ASKFAST+LONGAPP+ASKSMART+REALAPP on "
    "H-ZWRAP+H-WRAPBANK; final HITL mean 9.0; not open chat LM"
)

# Frozen per-model Cursor ASK→EVAL→FIX closeout (§11.8 / SESSION).
AB_HITL_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AB0",
        "id": "SESSION",
        "mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "freeze 10 real asks",
    },
    {
        "stage": "AB1",
        "id": "H-SEMWRAP",
        "mean": 9.0,
        "errors": 0,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "fuzzy near-known",
    },
    {
        "stage": "AB2",
        "id": "H-ASKFAST",
        "mean": 9.0,
        "errors": 0,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "wall↓100%",
    },
    {
        "stage": "AB3",
        "id": "H-LONGAPP",
        "mean": 9.0,
        "errors": 0,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "L_eff≫W curated",
    },
    {
        "stage": "AB4",
        "id": "H-ASKSMART",
        "mean": 8.7,
        "errors": 1,
        "fix": 10,
        "decision": "PROMOTE",
        "note": ">SERVEALIGN 3.4",
    },
    {
        "stage": "AB5",
        "id": "H-REALAPP",
        "mean": 8.85,
        "errors": 0,
        "fix": 3,
        "decision": "PROMOTE",
        "note": "app-known + app-longdoc",
    },
    {
        "stage": "AB6",
        "id": "AB-HITL-10",
        "mean": 9.0,
        "errors": 0,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "final pack gate",
    },
    {
        "stage": "AB7",
        "id": "AB-REPORT",
        "mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "public summary + paper-lab",
    },
)

AB_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ab-session.md",
    "docs/results/nano-lm/formal-hsemwrap-semwrap.md",
    "docs/results/nano-lm/formal-haskfast-askfast.md",
    "docs/results/nano-lm/formal-hlongapp-longapp.md",
    "docs/results/nano-lm/formal-hasksmart-asksmart.md",
    "docs/results/nano-lm/formal-hrealapp-realapp.md",
    "docs/results/nano-lm/app-known.md",
    "docs/results/nano-lm/app-longdoc.md",
    "docs/results/nano-lm/wave-ab-hitl.md",
    "docs/results/nano-lm/wave-ab-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ab.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AB_REPORT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-SEMWRAP",
    "H-ASKFAST",
    "H-LONGAPP",
    "H-ASKSMART",
    "H-REALAPP",
    "AB-HITL-10",
    "FIX",
    "PROMOTE",
    "H-ZWRAP",
    "H-WRAPBANK",
    "not open chat",
)


def decide_ab_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AB_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AB report evidence
    WHEN deciding AB-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AB_ID}: {AB_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AB_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AB_HITL_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking per-model HITL + FIX log (§11.8)
    THEN every model id appears and FIX count column exists.
    """
    body = str(text)
    if "FIX count" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid == "AB-HITL-10":
            if f"**{mid}**" not in body:
                return False
    return True


def render_wave_ab_summary() -> str:
    lines = [
        "# Wave AB — real apps · longer ctx · smarter · faster (**COMPLETE**)",
        "",
        "> Lab: `.local/pesquisa.md` §8.3 · §11 · Paper-lab: [paper-lab-wave-ab.md](paper-lab-wave-ab.md)  ",
        "> Parent: Wave AA **AA-FREEZE** reopen · Product spine: **H-ZWRAP + H-WRAPBANK** (+ AB stack)",
        "",
        "**Status: COMPLETE** · Thesis: **" + AB_THESIS + ".**",
        "",
        "## Stage scoreboard (Cursor ASK→EVAL→FIX)",
        "",
        "| # | ID | Mean | Errors | FIX count | Decision | Note |",
        "|---|-----|-----:|-------:|----------:|----------|------|",
    ]
    for row in AB_HITL_SCOREBOARD:
        mean = "—" if row["mean"] is None else f"{float(row['mean']):g}"
        err = "—" if row["errors"] is None else str(row["errors"])
        lines.append(
            f"| {row['stage']} | **{row['id']}** | {mean} | {err} | "
            f"**{row['fix']}** | **{row['decision']}** | {row['note']} |"
        )
    lines.extend(
        [
            "",
            "## Honest product claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| Known / near-known ask | **H-SEMWRAP** + **H-ASKFAST** on wrap bank |",
            "| Long curated docs | **H-LONGAPP** (ROLL/SUMCACHE); not STREAM |",
            "| Constrained decode | **H-ASKSMART** beats SERVEALIGN 3.4 after FIX |",
            "| Packaged apps | **H-REALAPP** `app-known` + `app-longdoc` |",
            "| Final HITL | **AB-HITL-10** mean **9.0** · errors **0**/10 |",
            "| “Open chat LM ≤5M” | **False** — not open chat |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:ab:report",
            "npm run nano:ab:session",
            "npm run nano:semwrap",
            "npm run nano:askfast",
            "npm run nano:longapp",
            "npm run nano:asksmart",
            "npm run nano:realapp",
            "npm run nano:ab:hitl",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · ZERR/SERVEALIGN-as-chat · invent Wave AC without lab-book reopen.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_ab() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AB (real apps · ctx · smart · fast)",
            "",
            "> Companion to [wave-ab-summary.md](wave-ab-summary.md). English lab note.  ",
            "> **Status: COMPLETE** · Final HITL: [wave-ab-hitl.md](wave-ab-hitl.md)",
            "",
            "## Question",
            "",
            "After AA proved known-ask wrap works and open chat does not, can the ≤5M "
            "student ship **scoped real apps** that are faster, handle longer curated "
            "docs, and answer more intelligently — with Cursor proving every stack via "
            "ASK→EVAL→FIX×10?",
            "",
            "## Answer",
            "",
            "**Yes, as scoped packaged apps — not as open chat.** Wave AB promotes "
            "SEMWRAP, ASKFAST, LONGAPP, ASKSMART, REALAPP, and final HITL mean 9.0.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-SEMWRAP | Fuzzy bank recall; mean 9.0; 0 false-hit |",
            "| H-ASKFAST | Ask wall↓100% with quality held |",
            "| H-LONGAPP | L_eff≫W on curated docs; 10/10 usable |",
            "| H-ASKSMART | Mean 8.7 > SERVEALIGN 3.4 after constrained FIX |",
            "| H-REALAPP | app-known + app-longdoc one-pagers; DEPL honest |",
            "| AB-HITL-10 | Final pack mean 9.0 · errors 0/10 |",
            "",
            "## Takeaway one-liner",
            "",
            "**Scoped AB product = H-ZWRAP + H-WRAPBANK + AB stack; not open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-ab-summary.md](wave-ab-summary.md) · [wave-ab-hitl.md](wave-ab-hitl.md) · "
            "[wave-aa-summary.md](wave-aa-summary.md)  ",
            "- Formals: SEMWRAP · ASKFAST · LONGAPP · ASKSMART · REALAPP  ",
            "- Apps: [app-known.md](app-known.md) · [app-longdoc.md](app-longdoc.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
