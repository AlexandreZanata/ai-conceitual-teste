"""Wave AM-FREEZE: lock AM outcomes; no Wave AN without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "AM_FREEZE_ID",
    "AM_THESIS",
    "AM_DECISIONS",
    "AM_PUBLIC",
    "AM_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "decide_am_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_am_freeze",
]

AM_FREEZE_ID = "AM-FREEZE"
AM_THESIS = (
    "Wave AM frozen: GENTRUTH HOLD · CTXNEXT·SMARTNEXT·FASTNEXT·"
    "APPNEXT·AM-HITL PROMOTE; CAPCHECK skipped; gen≥5 via GENTRUTH peak; "
    "≤5M stays; ship claim remains AF packaged stack; "
    "no Wave AN without reopen"
)

# Formal / closeout path → required decision token.
AM_DECISIONS: dict[str, tuple[str, str]] = {
    "H-GENTRUTH": (
        "docs/results/nano-lm/formal-hgentruth-gentruth.md",
        "HOLD",
    ),
    "H-CTXNEXT": (
        "docs/results/nano-lm/formal-hctxnext-ctxnext.md",
        "PROMOTE",
    ),
    "H-SMARTNEXT": (
        "docs/results/nano-lm/formal-hsmartnext-smartnext.md",
        "PROMOTE",
    ),
    "H-FASTNEXT": (
        "docs/results/nano-lm/formal-hfastnext-fastnext.md",
        "PROMOTE",
    ),
    "H-APPNEXT": (
        "docs/results/nano-lm/formal-happnext-appnext.md",
        "PROMOTE",
    ),
    "AM-HITL-10": (
        "docs/results/nano-lm/wave-am-hitl.md",
        "PROMOTE",
    ),
    "AM-REPORT": (
        "docs/results/nano-lm/wave-am-summary.md",
        "PROMOTE",
    ),
}

AM_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-am-summary.md",
    "docs/results/nano-lm/paper-lab-wave-am.md",
    "docs/results/nano-lm/am-freeze.md",
)

AM_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-CTXNEXT",
    "AM-HITL-10",
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
    GIVEN AM public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AM_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AM product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_am_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AM formals + public closeout + product docs
    WHEN applying AM-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AM_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AM public docs missing COMPLETE)"
    for path in AM_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AM_FREEZE_ID}: {AM_THESIS})"


def render_am_freeze() -> str:
    lines = [
        "# AM-FREEZE — Wave AM NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §3 AM8 · After **AM-REPORT**  ",
        "> Module: `nano_lm/src/am_freeze_ops.py` · "
        "Runner: `npm run nano:am:freeze`  ",
        "> Parent: [al-freeze.md](al-freeze.md) · "
        "[wave-am-summary.md](wave-am-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AM outcomes locked; next dual-arm "
        "PROMOTE stack stays; GENTRUTH ablated HOLD locked; "
        "gen≥5 via grounded extractive peak "
        "(not open chat); ≤5M hard stays; ship claim remains "
        "**AF packaged stack**; **no Wave AN** without explicit "
        "lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-GENTRUTH | **HOLD** | ablated gen 4.0; peak_only_lift |",
        "| H-CAPCHECK | **SKIPPED** | keep ≤5M without size reopen |",
        "| H-CTXNEXT | **PROMOTE** | deca-doc L_eff 213147 |",
        "| H-SMARTNEXT | **PROMOTE** | deca-hop cite; gen 9.0 |",
        "| H-FASTNEXT | **PROMOTE** | cue-jump peak-fast hot 0.17 |",
        "| H-APPNEXT | **PROMOTE** | dual-arm apps + DEPL-AM |",
        "| AM-HITL-10 | **PROMOTE** | final L=9.0 G=9.0; ship=AF |",
        "| AM-REPORT | **PROMOTE** | [summary](wave-am-summary.md) · "
        "[paper-lab](paper-lab-wave-am.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AN** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / open chat LM  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell CTXNEXT periods / LOOKUP hits as smarter open chat  ",
        "- Sell GENTRUTH extractive peak as open-chat IQ  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:am:freeze",
        "# optional: --skip-ask",
        "npm run nano:am:report",
        "npm run nano:al:freeze",
        "```",
        "",
        "Dual-arm smoke must keep LOOKUP + GENERATE (`wall_ms>0`) "
        "on AM0 known-ask.  ",
        "Artifact: `results/nano-lm/wave-am/am_freeze.json` · "
        "Contract: `nano_lm/tests/test_am_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
