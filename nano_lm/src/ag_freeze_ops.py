"""Wave AG-FREEZE: lock AG outcomes; no Wave AH without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "AG_FREEZE_ID",
    "AG_THESIS",
    "AG_DECISIONS",
    "AG_PUBLIC",
    "AG_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "decide_ag_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_ag_freeze",
]

AG_FREEZE_ID = "AG-FREEZE"
AG_THESIS = (
    "Wave AG frozen: anti-FP dual-arm HOLD on gen IQ; "
    "ship claim remains AF packaged stack; no Wave AH without reopen"
)

# Formal / closeout path → required decision token (HOLD allowed).
AG_DECISIONS: dict[str, tuple[str, str]] = {
    "H-ANTIFP": (
        "docs/results/nano-lm/formal-hantifp-antifp.md",
        "PROMOTE",
    ),
    "H-CTXREAL": (
        "docs/results/nano-lm/formal-hctxreal-ctxreal.md",
        "PROMOTE",
    ),
    "H-SMARTREAL": (
        "docs/results/nano-lm/formal-hsmartreal-smartreal.md",
        "HOLD",
    ),
    "H-FASTREAL": (
        "docs/results/nano-lm/formal-hfastreal-fastreal.md",
        "PROMOTE",
    ),
    "H-APPREAL": (
        "docs/results/nano-lm/formal-happreal-appreal.md",
        "HOLD",
    ),
    "AG-HITL-10": (
        "docs/results/nano-lm/wave-ag-hitl.md",
        "HOLD",
    ),
    "AG-REPORT": (
        "docs/results/nano-lm/wave-ag-summary.md",
        "PROMOTE",
    ),
}

AG_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ag-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ag.md",
    "docs/results/nano-lm/ag-freeze.md",
)

AG_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-ANTIFP",
    "AG-HITL-10",
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
    GIVEN AG public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AG_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AG product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_ag_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AG formals + public closeout + product docs
    WHEN applying AG-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AG_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AG public docs missing COMPLETE)"
    for path in AG_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AG_FREEZE_ID}: {AG_THESIS})"


def render_ag_freeze() -> str:
    lines = [
        "# AG-FREEZE — Wave AG NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §5 AG8 · After **AG-REPORT**  ",
        "> Module: `nano_lm/src/ag_freeze_ops.py` · "
        "Runner: `npm run nano:ag:freeze`  ",
        "> Parent: [af-freeze.md](af-freeze.md) · "
        "[wave-ag-summary.md](wave-ag-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AG outcomes locked; anti-FP dual-arm "
        "discipline stays; ship claim remains **AF packaged stack**; "
        "**no Wave AH** without explicit lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-ANTIFP | **PROMOTE** | LOOKUP≠GEN harness |",
        "| H-CTXREAL | **PROMOTE** | quad-doc L_eff↑ |",
        "| H-SMARTREAL | **HOLD** | cite ok; gen<5 honest |",
        "| H-FASTREAL | **PROMOTE** | gen wall↓; ≠ LOOKUP speed IQ |",
        "| H-APPREAL | **HOLD** | dual-arm apps + DEPL-AG |",
        "| AG-HITL-10 | **HOLD** | final L=9.0 G=1.0; ship=AF |",
        "| AG-REPORT | **PROMOTE** | [summary](wave-ag-summary.md) · "
        "[paper-lab](paper-lab-wave-ag.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AH** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / open chat LM  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Rewrite dual-arm HOLD into silent “smarter LM solved”  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:ag:freeze",
        "# optional: --skip-ask",
        "npm run nano:ag:report",
        "npm run nano:af:freeze",
        "```",
        "",
        "Dual-arm smoke must keep LOOKUP + GENERATE (`wall_ms>0`) "
        "on AG0 known-ask.  ",
        "Artifact: `results/nano-lm/wave-ag/ag_freeze.json` · "
        "Contract: `nano_lm/tests/test_ag_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
