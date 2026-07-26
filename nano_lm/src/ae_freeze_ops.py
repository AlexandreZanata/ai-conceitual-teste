"""Wave AE-FREEZE: lock AE outcomes; no Wave AF without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "AE_FREEZE_ID",
    "AE_THESIS",
    "AE_DECISIONS",
    "AE_PUBLIC",
    "AE_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "decide_ae_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_ae_freeze",
]

AE_FREEZE_ID = "AE-FREEZE"
AE_THESIS = (
    "Wave AE frozen: scoped packaged stack "
    "CTXMAX+SMARTMAX+FASTMAX+APPMAX; no Wave AF without reopen"
)

# Formal / closeout path → required decision token.
AE_DECISIONS: dict[str, tuple[str, str]] = {
    "H-CTXMAX": (
        "docs/results/nano-lm/formal-hctxmax-ctxmax.md",
        "PROMOTE",
    ),
    "H-SMARTMAX": (
        "docs/results/nano-lm/formal-hsmartmax-smartmax.md",
        "PROMOTE",
    ),
    "H-FASTMAX": (
        "docs/results/nano-lm/formal-hfastmax-fastmax.md",
        "PROMOTE",
    ),
    "H-APPMAX": (
        "docs/results/nano-lm/formal-happmax-appmax.md",
        "PROMOTE",
    ),
    "AE-HITL-10": (
        "docs/results/nano-lm/wave-ae-hitl.md",
        "PROMOTE",
    ),
    "AE-REPORT": (
        "docs/results/nano-lm/wave-ae-summary.md",
        "PROMOTE",
    ),
}

AE_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ae-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ae.md",
    "docs/results/nano-lm/ae-freeze.md",
)

AE_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-CTXMAX",
    "AE-HITL-10",
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
    GIVEN AE public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AE_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AE product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_ae_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AE formals + public closeout + product docs
    WHEN applying AE-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AE_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AE public docs missing COMPLETE)"
    for path in AE_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AE_FREEZE_ID}: {AE_THESIS})"


def render_ae_freeze() -> str:
    lines = [
        "# AE-FREEZE — Wave AE NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §5 AE7 · After **AE-REPORT**  ",
        "> Module: `nano_lm/src/ae_freeze_ops.py` · "
        "Runner: `npm run nano:ae:freeze`  ",
        "> Parent: [ad-freeze.md](ad-freeze.md) · "
        "[wave-ae-summary.md](wave-ae-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AE outcomes locked; scoped product remains "
        "**AE packaged stack** (CTXMAX · SMARTMAX · FASTMAX · APPMAX); "
        "**no Wave AF** without explicit lab-book reopen.",
        "",
        "**Status: COMPLETE** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-CTXMAX | **PROMOTE** | multi-doc L_eff↑ vs CTXPLUS |",
        "| H-SMARTMAX | **PROMOTE** | multi-hop cite; false-hit 0 |",
        "| H-FASTMAX | **PROMOTE** | hot e2e ≪ FASTPLUS warm |",
        "| H-APPMAX | **PROMOTE** | howto↑ + app-route + DEPL-AE |",
        "| AE-HITL-10 | **PROMOTE** | final mean 9.0 |",
        "| AE-REPORT | **PROMOTE** | [summary](wave-ae-summary.md) · "
        "[paper-lab](paper-lab-wave-ae.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AF** letter-pack / new H-IDs  ",
        "- Claim AE/AD stack / SERVEALIGN / ZERR = unbounded open chat LM  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF  ",
        "- Rewrite held-out HITL into silent “open chat solved”  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:ae:freeze",
        "# optional: --skip-ask",
        "npm run nano:ae:report",
        "npm run nano:ad:freeze",
        "```",
        "",
        "ASKFAST/SEMWRAP smoke must keep a scoped hit on held-out known-ask.  ",
        "Artifact: `results/nano-lm/wave-ae/ae_freeze.json` · "
        "Contract: `nano_lm/tests/test_ae_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
