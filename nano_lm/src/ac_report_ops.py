"""Wave AC REPORT: public closeout (per-model HITL + FIX log)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "AC_ID",
    "AC_THESIS",
    "AC_EVIDENCE",
    "AC_REPORT_MARKERS",
    "AC_HITL_SCOREBOARD",
    "decide_ac_report",
    "report_markers_ok",
    "scoreboard_ok",
    "render_wave_ac_summary",
    "render_paper_lab_wave_ac",
]

AC_ID = "AC-REPORT"
AC_THESIS = (
    "Scoped AC packaged apps = CTXPLUS+SMARTPLUS+FASTPLUS+APPPLUS "
    "(app-known+app-howto+app-longdoc) on AB spine; held-out HITL mean 9.0; "
    "not open chat LM"
)

# Frozen per-model Cursor ASK→EVAL→FIX closeout (§8.5 / §12 / SESSION).
AC_HITL_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AC0",
        "id": "SESSION",
        "mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "freeze 10 held-out asks",
    },
    {
        "stage": "AC1",
        "id": "H-CTXPLUS",
        "mean": 9.0,
        "errors": 0,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "L_eff 20523>AB",
    },
    {
        "stage": "AC2",
        "id": "H-SMARTPLUS",
        "mean": 9.0,
        "errors": 0,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "hard paraphrase; false-hit 0",
    },
    {
        "stage": "AC3",
        "id": "H-FASTPLUS",
        "mean": 9.0,
        "errors": 0,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "e2e≪AB; wall_drop 100%",
    },
    {
        "stage": "AC4",
        "id": "H-APPPLUS",
        "mean": 8.6,
        "errors": 0,
        "fix": 11,
        "decision": "PROMOTE",
        "note": "app-howto + known/longdoc",
    },
    {
        "stage": "AC5",
        "id": "AC-HITL-10",
        "mean": 9.0,
        "errors": 0,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "final pack gate",
    },
    {
        "stage": "AC6",
        "id": "AC-REPORT",
        "mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "public summary + paper-lab",
    },
    {
        "stage": "AC7",
        "id": "AC-FREEZE",
        "mean": None,
        "errors": None,
        "fix": 0,
        "decision": "NEXT",
        "note": "lock; no Wave AD invent",
    },
)

AC_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ac-session.md",
    "docs/results/nano-lm/formal-hctxplus-ctxplus.md",
    "docs/results/nano-lm/formal-hsmartplus-smartplus.md",
    "docs/results/nano-lm/formal-hfastplus-fastplus.md",
    "docs/results/nano-lm/formal-happplus-appplus.md",
    "docs/results/nano-lm/app-known.md",
    "docs/results/nano-lm/app-longdoc.md",
    "docs/results/nano-lm/app-howto.md",
    "docs/results/nano-lm/wave-ac-hitl.md",
    "docs/results/nano-lm/wave-ac-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ac.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AC_REPORT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-CTXPLUS",
    "H-SMARTPLUS",
    "H-FASTPLUS",
    "H-APPPLUS",
    "AC-HITL-10",
    "FIX",
    "PROMOTE",
    "app-howto",
    "not open chat",
)


def decide_ac_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AC_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AC report evidence
    WHEN deciding AC-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AC_ID}: {AC_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AC_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AC_HITL_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking per-model HITL + FIX log (§12.6)
    THEN every model id appears and FIX count column exists.
    """
    body = str(text)
    if "FIX count" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid == "AC-HITL-10":
            if f"**{mid}**" not in body:
                return False
    return True


def render_wave_ac_summary() -> str:
    lines = [
        "# Wave AC — held-out · deeper ctx · smarter · faster · apps (**COMPLETE**)",
        "",
        "> Lab: `.local/pesquisa.md` §8.5 · §12 · Paper-lab: "
        "[paper-lab-wave-ac.md](paper-lab-wave-ac.md)  ",
        "> Parent: Wave AB **AB-FREEZE** reopen · Product spine: "
        "**H-ZWRAP + H-WRAPBANK** (+ AB + AC stack)",
        "",
        "**Status: COMPLETE** · Thesis: **" + AC_THESIS + ".**",
        "",
        "## Stage scoreboard (Cursor ASK→EVAL→FIX)",
        "",
        "| # | ID | Mean | Errors | FIX count | Decision | Note |",
        "|---|-----|-----:|-------:|----------:|----------|------|",
    ]
    for row in AC_HITL_SCOREBOARD:
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
            "| Longer curated ctx | **H-CTXPLUS** multi-slice; L_eff≫AB LONGAPP |",
            "| Harder smart retrieve | **H-SMARTPLUS**; false-hit **0** |",
            "| Faster held-out ask | **H-FASTPLUS** on ASKFAST+cache |",
            "| Packaged apps | **H-APPPLUS** `app-known` + `app-howto` + "
            "`app-longdoc` |",
            "| Final HITL | **AC-HITL-10** mean **9.0** · errors **0**/10 |",
            "| “Open chat LM ≤5M” | **False** — not open chat |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:ac:report",
            "npm run nano:ac:session",
            "npm run nano:ctxplus",
            "npm run nano:smartplus",
            "npm run nano:fastplus",
            "npm run nano:appplus",
            "npm run nano:ac:hitl",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · ZERR/SERVEALIGN/AB-as-open-chat · invent Wave AD without "
            "lab-book reopen.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_ac() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AC (held-out · ctx · smart · fast · apps)",
            "",
            "> Companion to [wave-ac-summary.md](wave-ac-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE** · Final HITL: [wave-ac-hitl.md](wave-ac-hitl.md)",
            "",
            "## Question",
            "",
            "After AB shipped scoped apps on its frozen Q set, can the ≤5M "
            "student push **deeper context, smarter routing, faster ask, and "
            "app-howto** — proved on a **new held-out** 10 with Cursor "
            "ASK→EVAL→FIX on every stack?",
            "",
            "## Answer",
            "",
            "**Yes, as scoped packaged apps — not as open chat.** Wave AC "
            "promotes CTXPLUS, SMARTPLUS, FASTPLUS, APPPLUS, and final "
            "held-out HITL mean 9.0.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-CTXPLUS | L_eff 20523>AB; usable 10/10 |",
            "| H-SMARTPLUS | Hard paraphrase; mean 9.0; false-hit 0 |",
            "| H-FASTPLUS | e2e≪AB ASKFAST; wall_drop 100% |",
            "| H-APPPLUS | app-howto + known/longdoc; mean 8.6 across apps |",
            "| AC-HITL-10 | Final pack mean 9.0 · errors 0/10 |",
            "",
            "## Takeaway one-liner",
            "",
            "**Scoped AC product = AB spine + CTXPLUS/SMARTPLUS/FASTPLUS/"
            "APPPLUS on held-out; not open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-ac-summary.md](wave-ac-summary.md) · "
            "[wave-ac-hitl.md](wave-ac-hitl.md) · "
            "[wave-ab-summary.md](wave-ab-summary.md)  ",
            "- Formals: CTXPLUS · SMARTPLUS · FASTPLUS · APPPLUS  ",
            "- Apps: [app-known.md](app-known.md) · "
            "[app-howto.md](app-howto.md) · "
            "[app-longdoc.md](app-longdoc.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
