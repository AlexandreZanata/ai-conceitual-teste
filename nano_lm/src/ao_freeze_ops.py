"""Wave AO-FREEZE: lock AO outcomes; no Wave AP without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "AO_FREEZE_ID",
    "AO_THESIS",
    "AO_DECISIONS",
    "AO_PUBLIC",
    "AO_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "decide_ao_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_ao_freeze",
]

AO_FREEZE_ID = "AO-FREEZE"
AO_THESIS = (
    "Wave AO frozen: GENCORE HOLD · CTXCORE·SMARTCORE·FASTCORE·"
    "APPCORE·AO-HITL PROMOTE; CAPCHECK skipped; gen≥5 via GENCORE peak; "
    "≤5M stays; ship claim remains AF packaged stack; "
    "no Wave AP without reopen"
)

# Formal / closeout path → required decision token.
AO_DECISIONS: dict[str, tuple[str, str]] = {
    "H-GENCORE": (
        "docs/results/nano-lm/formal-hgencore-gencore.md",
        "HOLD",
    ),
    "H-CTXCORE": (
        "docs/results/nano-lm/formal-hctxcore-ctxcore.md",
        "PROMOTE",
    ),
    "H-SMARTCORE": (
        "docs/results/nano-lm/formal-hsmartcore-smartcore.md",
        "PROMOTE",
    ),
    "H-FASTCORE": (
        "docs/results/nano-lm/formal-hfastcore-fastcore.md",
        "PROMOTE",
    ),
    "H-APPCORE": (
        "docs/results/nano-lm/formal-happcore-appcore.md",
        "PROMOTE",
    ),
    "AO-HITL-10": (
        "docs/results/nano-lm/wave-ao-hitl.md",
        "PROMOTE",
    ),
    "AO-REPORT": (
        "docs/results/nano-lm/wave-ao-summary.md",
        "PROMOTE",
    ),
}

AO_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ao-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ao.md",
    "docs/results/nano-lm/ao-freeze.md",
)

AO_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-CTXCORE",
    "AO-HITL-10",
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
    GIVEN AO public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AO_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AO product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_ao_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AO formals + public closeout + product docs
    WHEN applying AO-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AO_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AO public docs missing COMPLETE)"
    for path in AO_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AO_FREEZE_ID}: {AO_THESIS})"


def render_ao_freeze() -> str:
    lines = [
        "# AO-FREEZE — Wave AO NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §3 AO8 · After **AO-REPORT**  ",
        "> Module: `nano_lm/src/ao_freeze_ops.py` · "
        "Runner: `npm run nano:ao:freeze`  ",
        "> Parent: [an-freeze.md](an-freeze.md) · "
        "[wave-ao-summary.md](wave-ao-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AO outcomes locked; core dual-arm "
        "PROMOTE stack stays; GENCORE ablated HOLD locked; "
        "gen≥5 via grounded extractive peak "
        "(not open chat); ≤5M hard stays; ship claim remains "
        "**AF packaged stack**; **no Wave AP** without explicit "
        "lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-GENCORE | **HOLD** | ablated gen 4.0; peak_only_lift |",
        "| H-CAPCHECK | **SKIPPED** | keep ≤5M without size reopen |",
        "| H-CTXCORE | **PROMOTE** | dodeca-doc L_eff 253105 |",
        "| H-SMARTCORE | **PROMOTE** | dodeca-hop cite; gen 9.0 |",
        "| H-FASTCORE | **PROMOTE** | peak-fast warm 0.06 |",
        "| H-APPCORE | **PROMOTE** | dual-arm apps + DEPL-AO |",
        "| AO-HITL-10 | **PROMOTE** | final L=9.0 G=9.0; ship=AF |",
        "| AO-REPORT | **PROMOTE** | [summary](wave-ao-summary.md) · "
        "[paper-lab](paper-lab-wave-ao.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AP** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / open chat LM  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell CTXCORE periods / LOOKUP hits as smarter open chat  ",
        "- Sell GENCORE extractive peak as open-chat IQ  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:ao:freeze",
        "# optional: --skip-ask",
        "npm run nano:ao:report",
        "npm run nano:an:freeze",
        "```",
        "",
        "Dual-arm smoke must keep LOOKUP + GENERATE (`wall_ms>0`) "
        "on AO0 known-ask.  ",
        "Artifact: `results/nano-lm/wave-ao/ao_freeze.json` · "
        "Contract: `nano_lm/tests/test_ao_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
