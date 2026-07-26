"""Wave AL REPORT: public closeout (dual-arm HITL + FIX + anti-FP)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "AL_ID",
    "AL_THESIS",
    "AL_EVIDENCE",
    "AL_REPORT_MARKERS",
    "AL_HITL_SCOREBOARD",
    "decide_al_report",
    "report_markers_ok",
    "scoreboard_ok",
    "antifp_section_ok",
    "render_wave_al_summary",
    "render_paper_lab_wave_al",
]

AL_ID = "AL-REPORT"
AL_THESIS = (
    "Wave AL fresh dual-arm on 11th held-out pack: GENFRESH HOLD · "
    "CTXFRESH·SMARTFRESH·FASTFRESH·APPFRESH·AL-HITL all PROMOTE; "
    "CAPCHECK skipped; gen≥5 via GENFRESH peak; L_eff↑ · wall↓ · "
    "apps+DEPL; ship claim remains AF packaged stack — not open chat LM"
)

# Frozen dual-arm Cursor ASK→EVAL→FIX closeout (§3 / SESSION).
AL_HITL_SCOREBOARD: tuple[dict[str, Any], ...] = (
    {
        "stage": "AL0",
        "id": "SESSION",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "freeze 10 held-out asks ≠ AB…AK",
    },
    {
        "stage": "AL1",
        "id": "H-GENFRESH",
        "lookup_mean": 9.0,
        "gen_mean": 4.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "HOLD",
        "note": "ablated gen 4.0; peak_only_lift; anti-FP",
    },
    {
        "stage": "AL1b",
        "id": "H-CAPCHECK",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "SKIPPED",
        "note": "size hypothesis unused; ≤5M stays",
    },
    {
        "stage": "AL2",
        "id": "H-CTXFRESH",
        "lookup_mean": 9.0,
        "gen_mean": 1.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "nona-doc L_eff 200344 > CTXMORE",
    },
    {
        "stage": "AL3",
        "id": "H-SMARTFRESH",
        "lookup_mean": 9.0,
        "gen_mean": 9.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "nona-hop cite 10/10; false-hit 0",
    },
    {
        "stage": "AL4",
        "id": "H-FASTFRESH",
        "lookup_mean": 9.0,
        "gen_mean": 7.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "cue-first peak-fast hot ~0.2ms ≪ FASTMORE 3.8",
    },
    {
        "stage": "AL5",
        "id": "H-APPFRESH",
        "lookup_mean": 8.33,
        "gen_mean": 9.0,
        "errors": "0/SERVE",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "expose LOOKUP|GENERATE + DEPL-AL",
    },
    {
        "stage": "AL6",
        "id": "AL-HITL-10",
        "lookup_mean": 9.0,
        "gen_mean": 9.0,
        "errors": "0/10",
        "fix": 0,
        "decision": "PROMOTE",
        "note": "final dual-arm; peak product; ship=AF",
    },
    {
        "stage": "AL7",
        "id": "AL-REPORT",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "public summary + paper-lab + anti-FP",
    },
    {
        "stage": "AL8",
        "id": "AL-FREEZE",
        "lookup_mean": None,
        "gen_mean": None,
        "errors": None,
        "fix": 0,
        "decision": "PROMOTE",
        "note": "lock; no Wave AM invent",
    },
)

AL_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-al-session.md",
    "docs/results/nano-lm/formal-hgenfresh-genfresh.md",
    "docs/results/nano-lm/formal-hctxfresh-ctxfresh.md",
    "docs/results/nano-lm/formal-hsmartfresh-smartfresh.md",
    "docs/results/nano-lm/formal-hfastfresh-fastfresh.md",
    "docs/results/nano-lm/formal-happfresh-appfresh.md",
    "docs/results/nano-lm/depl-al.md",
    "docs/results/nano-lm/appfresh-known.md",
    "docs/results/nano-lm/appfresh-howto.md",
    "docs/results/nano-lm/appfresh-longdoc.md",
    "docs/results/nano-lm/wave-al-hitl.md",
    "docs/results/nano-lm/wave-al-summary.md",
    "docs/results/nano-lm/paper-lab-wave-al.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AL_REPORT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "FROZEN",
    "H-GENFRESH",
    "H-CTXFRESH",
    "H-SMARTFRESH",
    "H-FASTFRESH",
    "H-APPFRESH",
    "AL-HITL-10",
    "FIX",
    "LOOKUP",
    "GENERATE",
    "anti-FP",
    "PROMOTE",
    "not open chat",
    "AF packaged stack",
)


def decide_al_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AL_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AL report evidence
    WHEN deciding AL-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AL_ID}: {AL_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AL_REPORT_MARKERS
) -> bool:
    body = str(text)
    return all(m in body for m in markers)


def scoreboard_ok(
    text: str, *, rows: Sequence[Mapping[str, Any]] = AL_HITL_SCOREBOARD
) -> bool:
    """
    GIVEN summary body
    WHEN checking dual-arm HITL + FIX log (§3 AL7)
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
        if mid.startswith("H-") or mid == "AL-HITL-10":
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


def render_wave_al_summary() -> str:
    lines = [
        "# Wave AL — fresh dual-arm · longer/faster/smarter/apps "
        "(**COMPLETE + FROZEN**)",
        "",
        "> Lab: `.local/pesquisa.md` §3 · Paper-lab: "
        "[paper-lab-wave-al.md](paper-lab-wave-al.md) · "
        "HITL: [wave-al-hitl.md](wave-al-hitl.md) · "
        "Freeze: [al-freeze.md](al-freeze.md)  ",
        "> Parent: Wave AK **AK-FREEZE** reopen · Ship claim: "
        "**AF packaged stack** (unchanged)",
        "",
        "**Status: COMPLETE + FROZEN** · Thesis: **"
        + AL_THESIS
        + ".**",
        "",
        "## Stage scoreboard (Cursor ASK→EVAL→FIX dual-arm)",
        "",
        "| # | ID | Lookup mean | Gen mean | Errors | FIX count | Decision | Note |",
        "|---|-----|------------:|---------:|--------|----------:|----------|------|",
    ]
    for row in AL_HITL_SCOREBOARD:
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
            "| LOOKUP labeled ≠ GENERATE | every AL stage dual-arm log |",
            "| Generative arm `wall_ms>0` · `n_new>0` | GENFRESH · CTXFRESH · FASTFRESH · AL-HITL-10 |",
            "| Cursor scores **completion** (not auto TRUE_HIT→9 as IQ) | SMARTFRESH/APPFRESH/HITL gen 9.0 peak spans |",
            "| LOOKUP high score ≠ generative IQ | LOOKUP 9.0 with peak gen product claim |",
            "| LOOKUP scores are not generative IQ | dual-arm scoreboard + anti-FP notes |",
            "| Peak gen ≠ open-chat TinyStories IQ | extractive peak from curated context (GENFRESH doctrine) |",
            "| CTXFRESH periods ≠ smarter LM | gen 1.0 · L_eff claim only |",
            "| Ablated gen HOLD honesty | H-GENFRESH ablated 4.0 · peak_only_lift |",
            "",
            "## Honest product claims",
            "",
            "| Claim | Truth |",
            "|-------|-------|",
            "| Longer usable ctx (AL) | **H-CTXFRESH** PROMOTE; L_eff **200344** > CTXMORE |",
            "| Smarter cite+gen (AL) | **H-SMARTFRESH** PROMOTE — gen **9.0** ≥ 5 (GENFRESH peak) |",
            "| True-gen ablation | **H-GENFRESH** HOLD — ablated gen **4.0** |",
            "| Faster generative ask | **H-FASTFRESH** PROMOTE — hot **~0.2** ≪ FASTMORE **3.8** |",
            "| Apps expose arms | **H-APPFRESH** PROMOTE — DEPL-AL dual-arm · SERVE gen 9.0 |",
            "| ≤5M hard law | **H-CAPCHECK** SKIPPED — keep ≤5M |",
            "| Final dual-arm HITL | **AL-HITL-10** LOOKUP **9.0** · GEN **9.0** · **PROMOTE** |",
            "| Ship claim | **AF packaged stack** — not open chat |",
            "| “Open chat LM ≤5M” | **False** — not open chat |",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:al:report",
            "npm run nano:al:session",
            "npm run nano:genfresh",
            "npm run nano:ctxfresh",
            "npm run nano:smartfresh",
            "npm run nano:fastfresh",
            "npm run nano:appfresh",
            "npm run nano:al:hitl",
            "npm run nano:al:freeze",
            "```",
            "",
            "## Do not reopen",
            "",
            "QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · "
            "ZPREF · claim LOOKUP = generative IQ · invent Wave AM without "
            "lab-book reopen · claim open chat · sell CTXFRESH periods as IQ · "
            "sell GENFRESH peak as open-chat IQ.",
            "",
        ]
    )
    return "\n".join(lines)


def render_paper_lab_wave_al() -> str:
    return "\n".join(
        [
            "# Paper-lab — Wave AL (fresh dual-arm · longer/faster/smarter/apps)",
            "",
            "> Companion to [wave-al-summary.md](wave-al-summary.md). "
            "English lab note.  ",
            "> **Status: COMPLETE + FROZEN** · Final HITL: "
            "[wave-al-hitl.md](wave-al-hitl.md) · "
            "Freeze: [al-freeze.md](al-freeze.md) · "
            "Parent: [ak-freeze.md](ak-freeze.md) · "
            "Ship: **AF packaged stack**",
            "",
            "## Question",
            "",
            "After AK froze more dual-arm, can an **eleventh** held-out 10 "
            "push **fresh context**, **fresh speed**, **fresh cite/gen**, "
            "and **apps** beyond AK without false-positive “open chat” "
            "claims — and without raising ≤5M?",
            "",
            "## Answer",
            "",
            "**Yes — as grounded peak product systems; not as open chat.** "
            "Wave AL promotes CTXFRESH, SMARTFRESH, FASTFRESH, APPFRESH, and "
            "final AL-HITL-10 with gen≥5 via GENFRESH extractive peak. "
            "H-GENFRESH HOLDs on ablated true-gen (4.0). CAPCHECK skipped "
            "(≤5M stays). Ship claim remains the **AF packaged stack**.",
            "",
            "| Stage | Observation |",
            "|-------|-------------|",
            "| H-GENFRESH | Ablated gen 4.0 → HOLD; peak_only_lift labeled |",
            "| H-CAPCHECK | Skipped; keep ≤5M |",
            "| H-CTXFRESH | Nona-doc L_eff 200344 > CTXMORE → PROMOTE |",
            "| H-SMARTFRESH | Nona-hop cite 10/10; gen 9.0 → PROMOTE |",
            "| H-FASTFRESH | Hot wall ~0.2 ≪ FASTMORE 3.8 → PROMOTE |",
            "| H-APPFRESH | Apps expose LOOKUP\\|GENERATE + DEPL-AL → PROMOTE |",
            "| AL-HITL-10 | Final L=9.0 G=9.0 → PROMOTE; ship=AF |",
            "| AL-FREEZE | Locked; no Wave AM invent without reopen |",
            "",
            "## Anti-FP takeaway",
            "",
            "LOOKUP mean 9.0 must never be sold as generative IQ. Peak "
            "gen **9.0** is extractive from curated context — not "
            "open-chat TinyStories. CTXFRESH gen **1.0** periods are "
            "L_eff-only. GENFRESH ablated **4.0** remains the honest "
            "true-gen bar. Telemetry (`mode`, `wall_ms`, `n_new`) is "
            "mandatory.",
            "",
            "## Takeaway one-liner",
            "",
            "**AL = fresh dual-arm under anti-FP; gen≥5 via GENFRESH peak; "
            "ablated HOLD honest; ship stays AF packaged stack — not "
            "open chat.**",
            "",
            "## Cite",
            "",
            "- [wave-al-summary.md](wave-al-summary.md) · "
            "[wave-al-hitl.md](wave-al-hitl.md) · "
            "[al-freeze.md](al-freeze.md) · "
            "[wave-ak-summary.md](wave-ak-summary.md)  ",
            "- Formals: GENFRESH · CTXFRESH · SMARTFRESH · FASTFRESH · "
            "APPFRESH  ",
            "- Deploy: [depl-al.md](depl-al.md) · Apps: "
            "[appfresh-known.md](appfresh-known.md) · "
            "[appfresh-howto.md](appfresh-howto.md) · "
            "[appfresh-longdoc.md](appfresh-longdoc.md)  ",
            "- Recipes: [RECIPES.md](RECIPES.md) · "
            "Card: [champion-card.md](champion-card.md)",
            "",
        ]
    )
