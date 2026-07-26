"""Wave AA-FREEZE: lock AA outcomes; no Wave AB without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "AA_FREEZE_ID",
    "AA_THESIS",
    "AA_DECISIONS",
    "AA_PUBLIC",
    "AA_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "decide_aa_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
]

AA_FREEZE_ID = "AA-FREEZE"
AA_THESIS = (
    "Wave AA frozen: H-ZWRAP+H-WRAPBANK known-ask only; "
    "no Wave AB without reopen"
)

# Formal path → required decision token (must appear in body).
AA_DECISIONS: dict[str, tuple[str, str]] = {
    "H-WRAPBANK": (
        "docs/results/nano-lm/formal-hwrapbank-wrapbank.md",
        "PROMOTE",
    ),
    "H-PARA": ("docs/results/nano-lm/formal-hpara-para.md", "HOLD"),
    "H-SERVEALIGN": (
        "docs/results/nano-lm/formal-hservealign-servealign.md",
        "HOLD",
    ),
    "H-ZPREF": ("docs/results/nano-lm/formal-hzpref-zpref.md", "KILL"),
    "H-DEPL-DOC": (
        "docs/results/nano-lm/formal-hdepldoc-depl-doc.md",
        "PROMOTE",
    ),
}

AA_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-aa-summary.md",
    "docs/results/nano-lm/paper-lab-wave-aa.md",
    "docs/results/nano-lm/aa-freeze.md",
)

AA_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-ZWRAP",
    "H-WRAPBANK",
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
    GIVEN AA public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AA_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking known-ask product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
        _ = path
    return bool(texts)


def decide_aa_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AA formals + public closeout + product one-pagers
    WHEN applying AA-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AA_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AA public docs missing COMPLETE)"
    for path in AA_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing H-ZWRAP/H-WRAPBANK/COMPLETE)"
    return f"PROMOTE ({AA_FREEZE_ID}: {AA_THESIS})"
