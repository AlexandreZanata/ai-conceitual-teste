"""Wave AQ-FREEZE: lock AQ outcomes; no Wave AR without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "AQ_FREEZE_ID",
    "AQ_THESIS",
    "AQ_DECISIONS",
    "AQ_PUBLIC",
    "AQ_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "SHIP_CLAIM",
    "decide_aq_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_aq_freeze",
]

AQ_FREEZE_ID = "AQ-FREEZE"
SHIP_CLAIM = (
    "AF packaged stack + AQ product layer — not open chat LM"
)
AQ_THESIS = (
    "Wave AQ frozen: PARAHIT·ADVFP·LATP·KBCOV·MODEUI·PRODUCT-HITL·"
    "REPORT PROMOTE; H-NANOGEN HOLD (ablated 4.0 · peak_only_lift); "
    "≤5M stays; ship claim "
    + SHIP_CLAIM
    + "; no Wave AR without reopen"
)

# Formal / closeout path → required decision token.
AQ_DECISIONS: dict[str, tuple[str, str]] = {
    "H-PARAHIT": (
        "docs/results/nano-lm/formal-hparahit-parahit.md",
        "PROMOTE",
    ),
    "H-ADVFP": (
        "docs/results/nano-lm/formal-hadvfp-advfp.md",
        "PROMOTE",
    ),
    "H-LATP": (
        "docs/results/nano-lm/formal-hlatp-latp.md",
        "PROMOTE",
    ),
    "H-KBCOV": (
        "docs/results/nano-lm/formal-hkbcov-kbcov.md",
        "PROMOTE",
    ),
    "H-MODEUI": (
        "docs/results/nano-lm/formal-hmodeui-modeui.md",
        "PROMOTE",
    ),
    "H-NANOGEN": (
        "docs/results/nano-lm/formal-hnanogen-nanogen.md",
        "HOLD",
    ),
    "AQ-PRODUCT-HITL": (
        "docs/results/nano-lm/wave-aq-product-hitl.md",
        "PROMOTE",
    ),
    "AQ-REPORT": (
        "docs/results/nano-lm/wave-aq-summary.md",
        "PROMOTE",
    ),
}

AQ_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-aq-summary.md",
    "docs/results/nano-lm/paper-lab-wave-aq.md",
    "docs/results/nano-lm/aq-freeze.md",
)

AQ_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-PARAHIT",
    "AQ-PRODUCT-HITL",
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
    GIVEN AQ public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AQ_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AQ product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_aq_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AQ formals + public closeout + product docs
    WHEN applying AQ-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AQ_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AQ public docs missing COMPLETE)"
    for path in AQ_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AQ_FREEZE_ID}: {AQ_THESIS})"


def render_aq_freeze() -> str:
    lines = [
        "# AQ-FREEZE — Wave AQ NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §5 AQ9 · After **AQ-REPORT**  ",
        "> Module: `nano_lm/src/aq_freeze_ops.py` · "
        "Runner: `npm run nano:aq:freeze`  ",
        "> Parent: [ap-freeze.md](ap-freeze.md) · "
        "[wave-aq-summary.md](wave-aq-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AQ outcomes locked; product pillars "
        "PROMOTE stack stays; H-NANOGEN ablated HOLD locked; "
        "≤5M hard stays; ship claim remains "
        f"**{SHIP_CLAIM}**; **no Wave AR** without explicit "
        "lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-PARAHIT | **PROMOTE** | hit_rate 0.95 · false-hit 0 |",
        "| H-ADVFP | **PROMOTE** | false-hit 0/20 · contrast reject |",
        "| H-LATP | **PROMOTE** | triad p50/p99 · no FASTBASE regress |",
        "| H-KBCOV | **PROMOTE** | 22/22 + 6 product holes |",
        "| H-MODEUI | **PROMOTE** | LOOKUP·PEAK·DECODE visible |",
        "| H-NANOGEN | **HOLD** | ablated gen 4.0 · peak_only_lift |",
        "| AQ-PRODUCT-HITL | **PROMOTE** | pillars+apps; gen claim locked |",
        "| AQ-REPORT | **PROMOTE** | [summary](wave-aq-summary.md) · "
        "[paper-lab](paper-lab-wave-aq.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AR** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / open chat LM  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell PEAK extractive as open-chat / mini-AGI unlocked  ",
        "- Sell product PROMOTE as generative unlock while H-NANOGEN HOLD  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:aq:freeze",
        "# optional: --skip-ask",
        "npm run nano:aq:report",
        "npm run nano:ap:freeze",
        "```",
        "",
        "Mode triad smoke must keep LOOKUP · PEAK · DECODE visible.  ",
        "Artifact: `results/nano-lm/wave-aq/aq_freeze.json` · "
        "Contract: `nano_lm/tests/test_aq_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
