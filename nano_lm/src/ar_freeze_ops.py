"""Wave AR-FREEZE: lock AR outcomes; no Wave AS without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "AR_FREEZE_ID",
    "AR_THESIS",
    "AR_DECISIONS",
    "AR_PUBLIC",
    "AR_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "SHIP_CLAIM",
    "decide_ar_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_ar_freeze",
]

AR_FREEZE_ID = "AR-FREEZE"
SHIP_CLAIM = (
    "AF packaged stack + AQ product layer — not open chat LM"
)
AR_THESIS = (
    "Wave AR frozen: ABSTAIN·SHIPDEMO·REPORT PROMOTE; "
    "PARAEXT HOLD · ADVREG KILL · NANOGEN2 HOLD (ablated 4.3) · "
    "DUAL-HITL HOLD; ≤5M stays; ship claim "
    + SHIP_CLAIM
    + "; no Wave AS without reopen"
)

# Formal / closeout path → required decision token.
AR_DECISIONS: dict[str, tuple[str, str]] = {
    "H-ABSTAIN": (
        "docs/results/nano-lm/formal-habstain-abstain.md",
        "PROMOTE",
    ),
    "H-SHIPDEMO": (
        "docs/results/nano-lm/formal-hshipdemo-shipdemo.md",
        "PROMOTE",
    ),
    "H-PARAEXT": (
        "docs/results/nano-lm/formal-hparaext-paraext.md",
        "HOLD",
    ),
    "H-ADVREG": (
        "docs/results/nano-lm/formal-hadvreg-advreg.md",
        "KILL",
    ),
    "H-NANOGEN2": (
        "docs/results/nano-lm/formal-hnanogen2-nanogen2.md",
        "HOLD",
    ),
    "AR-DUAL-HITL": (
        "docs/results/nano-lm/wave-ar-dual-hitl.md",
        "HOLD",
    ),
    "AR-REPORT": (
        "docs/results/nano-lm/wave-ar-summary.md",
        "PROMOTE",
    ),
}

AR_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ar-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ar.md",
    "docs/results/nano-lm/ar-freeze.md",
)

AR_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-ABSTAIN",
    "AR-DUAL-HITL",
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
    GIVEN AR public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AR_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AR product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_ar_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AR formals + public closeout + product docs
    WHEN applying AR-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AR_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AR public docs missing COMPLETE)"
    for path in AR_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AR_FREEZE_ID}: {AR_THESIS})"


def render_ar_freeze() -> str:
    lines = [
        "# AR-FREEZE — Wave AR NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §5 AR8 · After **AR-REPORT**  ",
        "> Module: `nano_lm/src/ar_freeze_ops.py` · "
        "Runner: `npm run nano:ar:freeze`  ",
        "> Parent: [aq-freeze.md](aq-freeze.md) · "
        "[wave-ar-summary.md](wave-ar-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AR outcomes locked; core product "
        "ABSTAIN·SHIPDEMO PROMOTE stays; deepen HOLD/KILL locked; "
        "H-NANOGEN2 ablated HOLD locked; ≤5M hard stays; ship claim "
        f"remains **{SHIP_CLAIM}**; **no Wave AS** without explicit "
        "lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-ABSTAIN | **PROMOTE** | OOD abstain 1.0 · FH 0 |",
        "| H-SHIPDEMO | **PROMOTE** | LOOKUP·PEAK·DECODE·ABSTAIN |",
        "| H-PARAEXT | **HOLD** | hit 0.65 < 0.70 · FH 0 |",
        "| H-ADVREG | **KILL** | false-hit 2/20 · SAFE≠quality |",
        "| H-NANOGEN2 | **HOLD** | ablated gen 4.3 · peak_only |",
        "| AR-DUAL-HITL | **HOLD** | core pass · soft deepen · gen locked |",
        "| AR-REPORT | **PROMOTE** | [summary](wave-ar-summary.md) · "
        "[paper-lab](paper-lab-wave-ar.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AS** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / open chat LM  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell PEAK / bank-grounded as open-chat / mini-AGI unlocked  ",
        "- Sell SAFE mean as answer quality  ",
        "- Sell product soft HOLD as generative unlock while "
        "H-NANOGEN2 HOLD  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:ar:freeze",
        "# optional: --skip-ask",
        "npm run nano:ar:report",
        "npm run nano:aq:freeze",
        "```",
        "",
        "Four-mode smoke must keep LOOKUP · PEAK · DECODE · ABSTAIN "
        "visible.  ",
        "Artifact: `results/nano-lm/wave-ar/ar_freeze.json` · "
        "Contract: `nano_lm/tests/test_ar_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
