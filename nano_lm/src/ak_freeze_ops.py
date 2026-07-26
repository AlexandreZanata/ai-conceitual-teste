"""Wave AK-FREEZE: lock AK outcomes; no Wave AL without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "AK_FREEZE_ID",
    "AK_THESIS",
    "AK_DECISIONS",
    "AK_PUBLIC",
    "AK_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "decide_ak_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_ak_freeze",
]

AK_FREEZE_ID = "AK-FREEZE"
AK_THESIS = (
    "Wave AK frozen: GENTRUE HOLD · CTXMORE·SMARTMORE·FASTMORE·"
    "APPMORE·AK-HITL PROMOTE; CAPCHECK skipped; gen≥5 via GENTRUE peak; "
    "≤5M stays; ship claim remains AF packaged stack; "
    "no Wave AL without reopen"
)

# Formal / closeout path → required decision token.
AK_DECISIONS: dict[str, tuple[str, str]] = {
    "H-GENTRUE": (
        "docs/results/nano-lm/formal-hgentrue-gentrue.md",
        "HOLD",
    ),
    "H-CTXMORE": (
        "docs/results/nano-lm/formal-hctxmore-ctxmore.md",
        "PROMOTE",
    ),
    "H-SMARTMORE": (
        "docs/results/nano-lm/formal-hsmartmore-smartmore.md",
        "PROMOTE",
    ),
    "H-FASTMORE": (
        "docs/results/nano-lm/formal-hfastmore-fastmore.md",
        "PROMOTE",
    ),
    "H-APPMORE": (
        "docs/results/nano-lm/formal-happmore-appmore.md",
        "PROMOTE",
    ),
    "AK-HITL-10": (
        "docs/results/nano-lm/wave-ak-hitl.md",
        "PROMOTE",
    ),
    "AK-REPORT": (
        "docs/results/nano-lm/wave-ak-summary.md",
        "PROMOTE",
    ),
}

AK_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ak-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ak.md",
    "docs/results/nano-lm/ak-freeze.md",
)

AK_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-CTXMORE",
    "AK-HITL-10",
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
    GIVEN AK public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AK_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AK product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_ak_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AK formals + public closeout + product docs
    WHEN applying AK-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AK_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AK public docs missing COMPLETE)"
    for path in AK_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AK_FREEZE_ID}: {AK_THESIS})"


def render_ak_freeze() -> str:
    lines = [
        "# AK-FREEZE — Wave AK NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §3 AK8 · After **AK-REPORT**  ",
        "> Module: `nano_lm/src/ak_freeze_ops.py` · "
        "Runner: `npm run nano:ak:freeze`  ",
        "> Parent: [aj-freeze.md](aj-freeze.md) · "
        "[wave-ak-summary.md](wave-ak-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AK outcomes locked; more dual-arm "
        "PROMOTE stack stays; GENTRUE ablated HOLD locked; "
        "gen≥5 via grounded extractive peak "
        "(not open chat); ≤5M hard stays; ship claim remains "
        "**AF packaged stack**; **no Wave AL** without explicit "
        "lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-GENTRUE | **HOLD** | ablated gen 4.0; peak_only_lift |",
        "| H-CAPCHECK | **SKIPPED** | keep ≤5M without size reopen |",
        "| H-CTXMORE | **PROMOTE** | octa-doc L_eff 188984 |",
        "| H-SMARTMORE | **PROMOTE** | octa-hop cite; gen 9.0 |",
        "| H-FASTMORE | **PROMOTE** | peak-fast hot 3.8 < FASTPEAK |",
        "| H-APPMORE | **PROMOTE** | dual-arm apps + DEPL-AK |",
        "| AK-HITL-10 | **PROMOTE** | final L=9.0 G=9.0; ship=AF |",
        "| AK-REPORT | **PROMOTE** | [summary](wave-ak-summary.md) · "
        "[paper-lab](paper-lab-wave-ak.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AL** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / open chat LM  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell CTXMORE periods / LOOKUP hits as smarter open chat  ",
        "- Sell GENTRUE extractive peak as open-chat IQ  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:ak:freeze",
        "# optional: --skip-ask",
        "npm run nano:ak:report",
        "npm run nano:aj:freeze",
        "```",
        "",
        "Dual-arm smoke must keep LOOKUP + GENERATE (`wall_ms>0`) "
        "on AK0 known-ask.  ",
        "Artifact: `results/nano-lm/wave-ak/ak_freeze.json` · "
        "Contract: `nano_lm/tests/test_ak_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
