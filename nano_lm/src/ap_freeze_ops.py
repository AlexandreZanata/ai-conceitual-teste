"""Wave AP-FREEZE: lock AP outcomes; no Wave AQ without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "AP_FREEZE_ID",
    "AP_THESIS",
    "AP_DECISIONS",
    "AP_PUBLIC",
    "AP_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "decide_ap_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_ap_freeze",
]

AP_FREEZE_ID = "AP-FREEZE"
AP_THESIS = (
    "Wave AP frozen: GENBASE HOLD · CTXBASE·SMARTBASE·FASTBASE·"
    "APPBASE·AP-HITL PROMOTE; CAPCHECK skipped; gen≥5 via GENBASE peak; "
    "≤5M stays; ship claim remains AF packaged stack; "
    "no Wave AQ without reopen"
)

# Formal / closeout path → required decision token.
AP_DECISIONS: dict[str, tuple[str, str]] = {
    "H-GENBASE": (
        "docs/results/nano-lm/formal-hgenbase-genbase.md",
        "HOLD",
    ),
    "H-CTXBASE": (
        "docs/results/nano-lm/formal-hctxbase-ctxbase.md",
        "PROMOTE",
    ),
    "H-SMARTBASE": (
        "docs/results/nano-lm/formal-hsmartbase-smartbase.md",
        "PROMOTE",
    ),
    "H-FASTBASE": (
        "docs/results/nano-lm/formal-hfastbase-fastbase.md",
        "PROMOTE",
    ),
    "H-APPBASE": (
        "docs/results/nano-lm/formal-happbase-appbase.md",
        "PROMOTE",
    ),
    "AP-HITL-10": (
        "docs/results/nano-lm/wave-ap-hitl.md",
        "PROMOTE",
    ),
    "AP-REPORT": (
        "docs/results/nano-lm/wave-ap-summary.md",
        "PROMOTE",
    ),
}

AP_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ap-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ap.md",
    "docs/results/nano-lm/ap-freeze.md",
)

AP_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-CTXBASE",
    "AP-HITL-10",
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
    GIVEN AP public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AP_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AP product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_ap_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AP formals + public closeout + product docs
    WHEN applying AP-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AP_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AP public docs missing COMPLETE)"
    for path in AP_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AP_FREEZE_ID}: {AP_THESIS})"


def render_ap_freeze() -> str:
    lines = [
        "# AP-FREEZE — Wave AP NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §3 AP8 · After **AP-REPORT**  ",
        "> Module: `nano_lm/src/ap_freeze_ops.py` · "
        "Runner: `npm run nano:ap:freeze`  ",
        "> Parent: [ao-freeze.md](ao-freeze.md) · "
        "[wave-ap-summary.md](wave-ap-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AP outcomes locked; base dual-arm "
        "PROMOTE stack stays; GENBASE ablated HOLD locked; "
        "gen≥5 via grounded extractive peak "
        "(not open chat); ≤5M hard stays; ship claim remains "
        "**AF packaged stack**; **no Wave AQ** without explicit "
        "lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-GENBASE | **HOLD** | ablated gen 4.0; peak_only_lift |",
        "| H-CAPCHECK | **SKIPPED** | keep ≤5M without size reopen |",
        "| H-CTXBASE | **PROMOTE** | trideca-doc L_eff 274198 |",
        "| H-SMARTBASE | **PROMOTE** | trideca-hop cite; gen 9.0 |",
        "| H-FASTBASE | **PROMOTE** | peak-fast warm 0.056 |",
        "| H-APPBASE | **PROMOTE** | dual-arm apps + DEPL-AP |",
        "| AP-HITL-10 | **PROMOTE** | final L=9.0 G=9.0; ship=AF |",
        "| AP-REPORT | **PROMOTE** | [summary](wave-ap-summary.md) · "
        "[paper-lab](paper-lab-wave-ap.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AQ** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / open chat LM  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell CTXBASE periods / LOOKUP hits as smarter open chat  ",
        "- Sell GENBASE extractive peak as open-chat IQ  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:ap:freeze",
        "# optional: --skip-ask",
        "npm run nano:ap:report",
        "npm run nano:ao:freeze",
        "```",
        "",
        "Dual-arm smoke must keep LOOKUP + GENERATE (`wall_ms>0`) "
        "on AP0 known-ask.  ",
        "Artifact: `results/nano-lm/wave-ap/ap_freeze.json` · "
        "Contract: `nano_lm/tests/test_ap_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
