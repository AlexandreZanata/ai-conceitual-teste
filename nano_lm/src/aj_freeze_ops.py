"""Wave AJ-FREEZE: lock AJ outcomes; no Wave AK without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "AJ_FREEZE_ID",
    "AJ_THESIS",
    "AJ_DECISIONS",
    "AJ_PUBLIC",
    "AJ_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "decide_aj_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_aj_freeze",
]

AJ_FREEZE_ID = "AJ-FREEZE"
AJ_THESIS = (
    "Wave AJ frozen: GENPEAK·CTXPEAK·SMARTPEAK·FASTPEAK·APPPEAK·"
    "AJ-HITL PROMOTE; CAPCHECK skipped; gen≥5 via grounded peak; "
    "≤5M stays; ship claim remains AF packaged stack; "
    "no Wave AK without reopen"
)

# Formal / closeout path → required decision token.
AJ_DECISIONS: dict[str, tuple[str, str]] = {
    "H-GENPEAK": (
        "docs/results/nano-lm/formal-hgenpeak-genpeak.md",
        "PROMOTE",
    ),
    "H-CTXPEAK": (
        "docs/results/nano-lm/formal-hctxpeak-ctxpeak.md",
        "PROMOTE",
    ),
    "H-SMARTPEAK": (
        "docs/results/nano-lm/formal-hsmartpeak-smartpeak.md",
        "PROMOTE",
    ),
    "H-FASTPEAK": (
        "docs/results/nano-lm/formal-hfastpeak-fastpeak.md",
        "PROMOTE",
    ),
    "H-APPPEAK": (
        "docs/results/nano-lm/formal-happpeak-apppeak.md",
        "PROMOTE",
    ),
    "AJ-HITL-10": (
        "docs/results/nano-lm/wave-aj-hitl.md",
        "PROMOTE",
    ),
    "AJ-REPORT": (
        "docs/results/nano-lm/wave-aj-summary.md",
        "PROMOTE",
    ),
}

AJ_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-aj-summary.md",
    "docs/results/nano-lm/paper-lab-wave-aj.md",
    "docs/results/nano-lm/aj-freeze.md",
)

AJ_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-CTXPEAK",
    "AJ-HITL-10",
)


def formal_decision_ok(path: str, text: str, want: str) -> bool:
    """
    GIVEN formal body + expected decision token
    WHEN checking freeze
    THEN True iff path non-empty and want appears in text.
    """
    body = str(text)
    return bool(path) and bool(body.strip()) and want in body


def public_docs_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN AJ public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AJ_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AJ product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_aj_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AJ formals + public closeout + product docs
    WHEN applying AJ-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AJ_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AJ public docs missing COMPLETE)"
    for path in AJ_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AJ_FREEZE_ID}: {AJ_THESIS})"


def render_aj_freeze() -> str:
    lines = [
        "# AJ-FREEZE — Wave AJ NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §3 AJ8 · After **AJ-REPORT**  ",
        "> Module: `nano_lm/src/aj_freeze_ops.py` · "
        "Runner: `npm run nano:aj:freeze`  ",
        "> Parent: [ai-freeze.md](ai-freeze.md) · "
        "[wave-aj-summary.md](wave-aj-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AJ outcomes locked; peak dual-arm "
        "PROMOTE stack stays; gen≥5 via grounded extractive peak "
        "(not open chat); ≤5M hard stays; ship claim remains "
        "**AF packaged stack**; **no Wave AK** without explicit "
        "lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-GENPEAK | **PROMOTE** | grounded+peak; gen 9.0 ≥5 |",
        "| H-CAPCHECK | **SKIPPED** | keep ≤5M without size reopen |",
        "| H-CTXPEAK | **PROMOTE** | hepta-doc L_eff 177809 |",
        "| H-SMARTPEAK | **PROMOTE** | hepta-hop cite; gen 9.0 |",
        "| H-FASTPEAK | **PROMOTE** | peak-fast hot ~5.0 < FASTPUSH |",
        "| H-APPPEAK | **PROMOTE** | dual-arm apps + DEPL-AJ |",
        "| AJ-HITL-10 | **PROMOTE** | final L=9.0 G=9.0; ship=AF |",
        "| AJ-REPORT | **PROMOTE** | [summary](wave-aj-summary.md) · "
        "[paper-lab](paper-lab-wave-aj.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AK** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / open chat LM  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell CTXPEAK periods / LOOKUP hits as smarter open chat  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:aj:freeze",
        "# optional: --skip-ask",
        "npm run nano:aj:report",
        "npm run nano:ai:freeze",
        "```",
        "",
        "Dual-arm smoke must keep LOOKUP + GENERATE (`wall_ms>0`) "
        "on AJ0 known-ask.  ",
        "Artifact: `results/nano-lm/wave-aj/aj_freeze.json` · "
        "Contract: `nano_lm/tests/test_aj_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
