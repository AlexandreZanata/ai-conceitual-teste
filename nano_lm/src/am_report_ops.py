"""Wave AM REPORT: public closeout (dual-arm HITL + FIX + anti-FP)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "AM_ID",
    "AM_THESIS",
    "AM_EVIDENCE",
    "AM_REPORT_MARKERS",
    "AM_HITL_SCOREBOARD",
    "decide_am_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "render_wave_am_summary",
    "render_paper_lab_wave_am",
]

AM_ID = "AM-REPORT"
AM_THESIS = (
    "Wave AM next dual-arm on 12th held-out pack: GENTRUTH HOLD · "
    "CTXNEXT·SMARTNEXT·FASTNEXT·APPNEXT·AM-HITL all PROMOTE; "
    "CAPCHECK skipped; gen≥5 via GENTRUTH peak; L_eff↑ · wall↓ · "
    "apps+DEPL; ship claim remains AF packaged stack — not open chat LM"
)

# Frozen dual-arm Cursor ASK→EVAL→FIX closeout (§3 / SESSION).
AM_HITL_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AM0",
        "id": "SESSION",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "freeze 10 held-out asks ≠ AB…AL",
    },
    {
        "stage": "AM1",
        "id": "H-GENTRUTH",
        "lookup_mean": 9.0,
        "gen_mean": 4.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "HOLD",
        "note": "ablated gen 4.0; peak_only_lift; anti-FP",
    },
    {
        "stage": "AM1b",
        "id": "H-CAPCHECK",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "SKIPPED",
        "note": "size hypothesis unused; ≤5M stays",
    },
    {
        "stage": "AM2",
        "id": "H-CTXNEXT",
        "lookup_mean": 9.0,
        "gen_mean": 1.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "deca-doc L_eff 213147 > CTXFRESH",
    },
    {
        "stage": "AM3",
        "id": "H-SMARTNEXT",
        "lookup_mean": 9.0,
        "gen_mean": 9.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "deca-hop cite 10/10; false-hit 0",
    },
    {
        "stage": "AM4",
        "id": "H-FASTNEXT",
        "lookup_mean": 9.0,
        "gen_mean": 7.0,
        "errors": "0/10",
        "fix": 1,
        "decision": "PROMOTE",
        "note": "cue-jump peak-fast hot 0.17 ≪ FASTFRESH 0.2",
    },
    {
        "stage": "AM5",
        "id": "H-APPNEXT",
        "lookup_mean": 8.33,
        "gen_mean": 9.0,
        "errors": "0/SERVE",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "expose LOOKUP|GENERATE + DEPL-AM",
    },
    {
        "stage": "AM6",
        "id": "AM-HITL-10",
        "lookup_mean": 9.0,
        "gen_mean": 9.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "final dual-arm; peak product; ship=AF",
    },
    {
        "stage": "AM7",
        "id": "AM-REPORT",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "public summary + paper-lab + anti-FP",
    },
    {
        "stage": "AM8",
        "id": "AM-FREEZE",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "lock; no Wave AN invent",
    },
)

AM_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-am-session.md",
    "docs/results/nano-lm/formal-hgentruth-gentruth.md",
    "docs/results/nano-lm/formal-hctxnext-ctxnext.md",
    "docs/results/nano-lm/formal-hsmartnext-smartnext.md",
    "docs/results/nano-lm/formal-hfastnext-fastnext.md",
    "docs/results/nano-lm/formal-happnext-appnext.md",
    "docs/results/nano-lm/depl-am.md",
    "docs/results/nano-lm/appnext-known.md",
    "docs/results/nano-lm/appnext-howto.md",
    "docs/results/nano-lm/appnext-longdoc.md",
    "docs/results/nano-lm/wave-am-hitl.md",
    "docs/results/nano-lm/wave-am-summary.md",
    "docs/results/nano-lm/paper-lab-wave-am.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AM_REPORT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "FROZEN",
    "H-GENTRUTH",
    "H-CTXNEXT",
    "H-SMARTNEXT",
    "H-FASTNEXT",
    "H-APPNEXT",
    "AM-HITL-10",
    "FIX",
    "LOOKUP",
    "GENERATE",
    "anti-FP",
    "PROMOTE",
    "not open chat",
    "AF packaged stack",
)


def decide_am_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AM_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AM report evidence
    WHEN deciding AM-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AM_ID}: {AM_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AM_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AM_HITL_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking dual-arm HITL + FIX log (§3 AM7)
    THEN every model id appears and FIX + LOOKUP/GENERATE columns exist.
    """
    body = str(text)
    if "FIX count" not in body:
        return False
    if "Lookup mean" not in body or "Gen mean" not in body:
        return False
    for row in rows:
        mid = str(row["id"])
        if mid not in body:
            return False
        if mid.startswith("H-") or mid == "AM-HITL-10":
            if f"**{mid}**" not in body:
                return False
    return True


def antifp_section_ok(text: str) -> bool:
    """
    GIVEN summary body
    WHEN checking anti-FP evidence block
    THEN require dual-arm law + LOOKUP≠IQ + telemetry keys named.
    """
    body = str(text)
    need = (
        "anti-FP",
        "LOOKUP",
        "GENERATE",
        "wall_ms",
        "n_new",
        "not generative IQ",
    )
    return all(m in body for m in need)


def render_wave_am_summary() -> str:
    lines = [
        "# Wave AM — next dual-arm · longer/faster/smarter/apps "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §3 · Paper-lab: "
        "[paper-lab-wave-am.md](paper-lab-wave-am.md) · "
        "HITL: [wave-am-hitl.md](wave-am-hitl.md) · "
        "Freeze: [am-freeze.md](am-freeze.md)  ",
        "> Parent: Wave AL **AL-FREEZE** reopen · Ship claim: "
        "**AF packaged stack** (unchanged)",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + AM_THESIS
        + ".**",
        "",
        "## Stage scoreboard (Cursor ASK→EVAL→FIX dual-arm)",
        "",
        "| # | ID | Lookup mean | Gen mean | Errors | FIX count | Decision | Note |",
        "|---|-----|------------:|---------:|--------|----------:|----------|------|",
    ]
    for row in AM_HITL_SCOREBOARD:
        lm = (
            "—"
            if row["lookup_mean"] is None
            else f"{float(row['lookup_mean']):g}"
        )
        gm = (
            "—"
            if row["gen_mean"] is None
            else f"{float(row['gen_mean']):g}"
        )
        err = "—" if row["errors"] is None else str(row["errors"])
        lines.append(
            f"| {row['stage']} | **{row['id']}** | {lm} | {gm} | {err} | "
            f"**{row['fix']}** | **{row['decision']}** | {row['note']} |"
        )
    lines.extend(
        [
            "",
            "## Anti-FP evidence (mandatory)",
            "",
            "| Rule | Evidence |",
            "|------|----------|",
            "| LOOKUP labeled ≠ GENERATE | every AM stage dual-arm log |",
            "| Generative arm `wall_ms>0` · `n_new>0` | GENTRUTH · CTXNEXT · FASTNEXT · AM-HITL-10 |",
            "| Cursor scores **completion** (not auto TRUE_HIT→9 as IQ) | SMARTNEXT/APPNEXT/HITL gen 9.0 peak spans |",
            "| LOOKUP high score ≠ generative IQ | LOOKUP 9.0 with peak gen product claim |",
            "| LOOKUP scores are not generative IQ | dual-arm scoreboard + anti-FP notes |",
            "| Peak gen ≠ open-chat TinyStories IQ | extractive peak from curated context (GENTRUTH doctrine) |",
            "| CTXNEXT periods ≠ smarter LM | gen 1.0 · L_eff claim only |",
            "| Ablated gen HOLD honesty | H-GENTRUTH ablated 4.0 · peak_only_lift |",
            "",
            "## Honest product claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| Longer usable ctx (AM) | **H-CTXNEXT** PROMOTE; L_eff **213147** > CTXFRESH |",
            "| Smarter cite+gen (AM) | **H-SMARTNEXT** PROMOTE — gen **9.0** ≥ 5 (GENTRUTH peak) |",
            "| True-gen ablation | **H-GENTRUTH** HOLD — ablated gen **4.0** |",
            "| Faster generative ask | **H-FASTNEXT** PROMOTE — hot **0.17** ≪ FASTFRESH **0.2** |",
            "| Apps expose arms | **H-APPNEXT** PROMOTE — DEPL-AM dual-arm · SERVE gen 9.0 |",
            "| ≤5M hard law | **H-CAPCHECK** SKIPPED — keep ≤5M |",
            "| Final dual-arm HITL | **AM-HITL-10** LOOKUP **9.0** · GEN **9.0** · **PROMOTE** |",
            "| Ship claim | **AF packaged stack** — not open chat |",
            "| “Open chat LM ≤5M” | **False** — not open chat |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:am:report",
            "npm run nano:am:session",
            "npm run nano:gentruth",
            "npm run nano:ctxnext",
            "npm run nano:smartnext",
            "npm run nano:fastnext",
            "npm run nano:appnext",
            "npm run nano:am:hitl",
            "npm run nano:am:freeze",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave AN without "
            "lab-book reopen · claim open chat · sell CTXNEXT periods as IQ · "
            "sell GENTRUTH peak as open-chat IQ.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_am() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AM (next dual-arm · longer/faster/smarter/apps)",
            "",
            "> Companion to [wave-am-summary.md](wave-am-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · Final HITL: "
            "[wave-am-hitl.md](wave-am-hitl.md) · "
            "Freeze: [am-freeze.md](am-freeze.md) · "
            "Parent: [al-freeze.md](al-freeze.md) · "
            "Ship: **AF packaged stack**",
            "",
            "## Question",
            "",
            "After AL froze fresh dual-arm, can a **twelfth** held-out 10 "
            "push **next context**, **next speed**, **next cite/gen**, "
            "and **apps** beyond AL without false-positive “open chat” "
            "claims — and without raising ≤5M?",
            "",
            "## Answer",
            "",
            "**Yes — as grounded peak product systems; not as open chat.** "
            "Wave AM promotes CTXNEXT, SMARTNEXT, FASTNEXT, APPNEXT, and "
            "final AM-HITL-10 with gen≥5 via GENTRUTH extractive peak. "
            "H-GENTRUTH HOLDs on ablated true-gen (4.0). CAPCHECK skipped "
            "(≤5M stays). Ship claim remains the **AF packaged stack**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-GENTRUTH | Ablated gen 4.0 → HOLD; peak_only_lift labeled |",
            "| H-CAPCHECK | Skipped; keep ≤5M |",
            "| H-CTXNEXT | Deca-doc L_eff 213147 > CTXFRESH → PROMOTE |",
            "| H-SMARTNEXT | Deca-hop cite 10/10; gen 9.0 → PROMOTE |",
            "| H-FASTNEXT | Hot wall 0.17 ≪ FASTFRESH 0.2 → PROMOTE |",
            "| H-APPNEXT | Apps expose LOOKUP\\|GENERATE + DEPL-AM → PROMOTE |",
            "| AM-HITL-10 | Final L=9.0 G=9.0 → PROMOTE; ship=AF |",
            "| AM-FREEZE | Locked; no Wave AN invent without reopen |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP mean 9.0 must never be sold as generative IQ. Peak "
            "gen **9.0** is extractive from curated context — not "
            "open-chat TinyStories. CTXNEXT gen **1.0** periods are "
            "L_eff-only. GENTRUTH ablated **4.0** remains the honest "
            "true-gen bar. Telemetry (`mode`, `wall_ms`, `n_new`) is "
            "mandatory.",
            "",
            "## Takeaway one-liner",
            "",
            "**AM = next dual-arm under anti-FP; gen≥5 via GENTRUTH peak; "
            "ablated HOLD honest; ship stays AF packaged stack — not "
            "open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-am-summary.md](wave-am-summary.md) · "
            "[wave-am-hitl.md](wave-am-hitl.md) · "
            "[am-freeze.md](am-freeze.md) · "
            "[wave-al-summary.md](wave-al-summary.md)  ",
            "- Formals: GENTRUTH · CTXNEXT · SMARTNEXT · FASTNEXT · "
            "APPNEXT  ",
            "- Deploy: [depl-am.md](depl-am.md) · Apps: "
            "[appnext-known.md](appnext-known.md) · "
            "[appnext-howto.md](appnext-howto.md) · "
            "[appnext-longdoc.md](appnext-longdoc.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
