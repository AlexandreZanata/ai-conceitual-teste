"""Wave AN-FREEZE: lock AN outcomes; no Wave AO without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "AN_FREEZE_ID",
    "AN_THESIS",
    "AN_DECISIONS",
    "AN_PUBLIC",
    "AN_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "decide_an_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_an_freeze",
]

AN_FREEZE_ID = "AN-FREEZE"
AN_THESIS = (
    "Wave AN frozen: GENEDGE HOLD · CTXEDGE·SMARTEDGE·FASTEDGE·"
    "APPEDGE·AN-HITL PROMOTE; CAPCHECK skipped; gen≥5 via GENEDGE peak; "
    "≤5M stays; ship claim remains AF packaged stack; "
    "no Wave AO without reopen"
)

# Formal / closeout path → required decision token.
AN_DECISIONS: dict[str, tuple[str, str]] = {
    "H-GENEDGE": (
        "docs/results/nano-lm/formal-hgenedge-genedge.md",
        "HOLD",
    ),
    "H-CTXEDGE": (
        "docs/results/nano-lm/formal-hctxedge-ctxedge.md",
        "PROMOTE",
    ),
    "H-SMARTEDGE": (
        "docs/results/nano-lm/formal-hsmartedge-smartedge.md",
        "PROMOTE",
    ),
    "H-FASTEDGE": (
        "docs/results/nano-lm/formal-hfastedge-fastedge.md",
        "PROMOTE",
    ),
    "H-APPEDGE": (
        "docs/results/nano-lm/formal-happedge-appedge.md",
        "PROMOTE",
    ),
    "AN-HITL-10": (
        "docs/results/nano-lm/wave-an-hitl.md",
        "PROMOTE",
    ),
    "AN-REPORT": (
        "docs/results/nano-lm/wave-an-summary.md",
        "PROMOTE",
    ),
}

AN_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-an-summary.md",
    "docs/results/nano-lm/paper-lab-wave-an.md",
    "docs/results/nano-lm/an-freeze.md",
)

AN_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-CTXEDGE",
    "AN-HITL-10",
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
    GIVEN AN public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AN_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AN product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_an_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AN formals + public closeout + product docs
    WHEN applying AN-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AN_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AN public docs missing COMPLETE)"
    for path in AN_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AN_FREEZE_ID}: {AN_THESIS})"


def render_an_freeze() -> str:
    lines = [
        "# AN-FREEZE — Wave AN NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §3 AN8 · After **AN-REPORT**  ",
        "> Module: `nano_lm/src/an_freeze_ops.py` · "
        "Runner: `npm run nano:an:freeze`  ",
        "> Parent: [am-freeze.md](am-freeze.md) · "
        "[wave-an-summary.md](wave-an-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AN outcomes locked; edge dual-arm "
        "PROMOTE stack stays; GENEDGE ablated HOLD locked; "
        "gen≥5 via grounded extractive peak "
        "(not open chat); ≤5M hard stays; ship claim remains "
        "**AF packaged stack**; **no Wave AO** without explicit "
        "lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-GENEDGE | **HOLD** | ablated gen 4.0; peak_only_lift |",
        "| H-CAPCHECK | **SKIPPED** | keep ≤5M without size reopen |",
        "| H-CTXEDGE | **PROMOTE** | undeca-doc L_eff 242448 |",
        "| H-SMARTEDGE | **PROMOTE** | undeca-hop cite; gen 9.0 |",
        "| H-FASTEDGE | **PROMOTE** | peak-fast hot 0.05 |",
        "| H-APPEDGE | **PROMOTE** | dual-arm apps + DEPL-AN |",
        "| AN-HITL-10 | **PROMOTE** | final L=9.0 G=9.0; ship=AF |",
        "| AN-REPORT | **PROMOTE** | [summary](wave-an-summary.md) · "
        "[paper-lab](paper-lab-wave-an.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AO** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / open chat LM  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell CTXEDGE periods / LOOKUP hits as smarter open chat  ",
        "- Sell GENEDGE extractive peak as open-chat IQ  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:an:freeze",
        "# optional: --skip-ask",
        "npm run nano:an:report",
        "npm run nano:am:freeze",
        "```",
        "",
        "Dual-arm smoke must keep LOOKUP + GENERATE (`wall_ms>0`) "
        "on AN0 known-ask.  ",
        "Artifact: `results/nano-lm/wave-an/an_freeze.json` · "
        "Contract: `nano_lm/tests/test_an_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
