"""Wave AH-FREEZE: lock AH outcomes; no Wave AI without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "AH_FREEZE_ID",
    "AH_THESIS",
    "AH_DECISIONS",
    "AH_PUBLIC",
    "AH_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "decide_ah_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_ah_freeze",
]

AH_FREEZE_ID = "AH-FREEZE"
AH_THESIS = (
    "Wave AH frozen: CTXLIFT+FASTLIFT PROMOTE; gen IQ HOLD; "
    "ship claim remains AF packaged stack; no Wave AI without reopen"
)

# Formal / closeout path → required decision token (HOLD allowed).
AH_DECISIONS: dict[str, tuple[str, str]] = {
    "H-GENLIFT": (
        "docs/results/nano-lm/formal-hgenlift-genlift.md",
        "HOLD",
    ),
    "H-CTXLIFT": (
        "docs/results/nano-lm/formal-hctxlift-ctxlift.md",
        "PROMOTE",
    ),
    "H-SMARTLIFT": (
        "docs/results/nano-lm/formal-hsmartlift-smartlift.md",
        "HOLD",
    ),
    "H-FASTLIFT": (
        "docs/results/nano-lm/formal-hfastlift-fastlift.md",
        "PROMOTE",
    ),
    "H-APPLIFT": (
        "docs/results/nano-lm/formal-happlift-applift.md",
        "HOLD",
    ),
    "AH-HITL-10": (
        "docs/results/nano-lm/wave-ah-hitl.md",
        "HOLD",
    ),
    "AH-REPORT": (
        "docs/results/nano-lm/wave-ah-summary.md",
        "PROMOTE",
    ),
}

AH_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ah-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ah.md",
    "docs/results/nano-lm/ah-freeze.md",
)

AH_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-CTXLIFT",
    "AH-HITL-10",
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
    GIVEN AH public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AH_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AH product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_ah_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AH formals + public closeout + product docs
    WHEN applying AH-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AH_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AH public docs missing COMPLETE)"
    for path in AH_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AH_FREEZE_ID}: {AH_THESIS})"


def render_ah_freeze() -> str:
    lines = [
        "# AH-FREEZE — Wave AH NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §5 AH8 · After **AH-REPORT**  ",
        "> Module: `nano_lm/src/ah_freeze_ops.py` · "
        "Runner: `npm run nano:ah:freeze`  ",
        "> Parent: [ag-freeze.md](ag-freeze.md) · "
        "[wave-ah-summary.md](wave-ah-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AH outcomes locked; ctx+speed lifts stay; "
        "gen IQ HOLDs stay honest; ship claim remains **AF packaged stack**; "
        "**no Wave AI** without explicit lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-GENLIFT | **HOLD** | anti-period; gen 4.0 <5 |",
        "| H-CTXLIFT | **PROMOTE** | penta-doc L_eff↑ |",
        "| H-SMARTLIFT | **HOLD** | cite ok; gen ties SMARTREAL 4.0 |",
        "| H-FASTLIFT | **PROMOTE** | hot wall↓ vs FASTREAL |",
        "| H-APPLIFT | **HOLD** | dual-arm apps + DEPL-AH |",
        "| AH-HITL-10 | **HOLD** | final L=9.0 G=1.0; ship=AF |",
        "| AH-REPORT | **PROMOTE** | [summary](wave-ah-summary.md) · "
        "[paper-lab](paper-lab-wave-ah.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AI** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / open chat LM  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Rewrite dual-arm HOLD into silent “smarter LM solved”  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:ah:freeze",
        "# optional: --skip-ask",
        "npm run nano:ah:report",
        "npm run nano:ag:freeze",
        "```",
        "",
        "Dual-arm smoke must keep LOOKUP + GENERATE (`wall_ms>0`) "
        "on AH0 known-ask.  ",
        "Artifact: `results/nano-lm/wave-ah/ah_freeze.json` · "
        "Contract: `nano_lm/tests/test_ah_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
