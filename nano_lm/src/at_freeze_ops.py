"""Wave AT-FREEZE: lock AT outcomes; no Wave AU without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "AT_FREEZE_ID",
    "AT_THESIS",
    "AT_DECISIONS",
    "AT_PUBLIC",
    "AT_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "SHIP_CLAIM",
    "decide_at_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_at_freeze",
]

AT_FREEZE_ID = "AT-FREEZE"
SHIP_CLAIM = (
    "AF packaged stack + AQ product layer + AS trust path + "
    "ablated DECODE (snippet-prefix) — not unlabeled open chat LM"
)
AT_THESIS = (
    "Wave AT frozen: H-PRODREG·H-SHIPAPP·H-NANOGEN4·AT-REAL-EVAL·"
    "AT-REPORT PROMOTE; ablated DECODE 5.5 (snippet-prefix); "
    "≤5M stays; ship claim " + SHIP_CLAIM + "; no Wave AU without reopen"
)

AT_DECISIONS: dict[str, tuple[str, str]] = {
    "H-PRODREG": (
        "docs/results/nano-lm/formal-hprodreg-prodreg.md",
        "PROMOTE",
    ),
    "H-SHIPAPP": (
        "docs/results/nano-lm/formal-hshipapp-shipapp.md",
        "PROMOTE",
    ),
    "H-NANOGEN4": (
        "docs/results/nano-lm/formal-hnanogen4-nanogen4.md",
        "PROMOTE",
    ),
    "AT-REAL-EVAL": (
        "docs/results/nano-lm/wave-at-real-eval.md",
        "PROMOTE",
    ),
    "AT-REPORT": (
        "docs/results/nano-lm/wave-at-summary.md",
        "PROMOTE",
    ),
}

AT_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-at-summary.md",
    "docs/results/nano-lm/paper-lab-wave-at.md",
    "docs/results/nano-lm/at-freeze.md",
)

AT_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-NANOGEN4",
    "AT-REAL-EVAL",
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
    GIVEN AT public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AT_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AT product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_at_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AT formals + public closeout + product docs
    WHEN applying AT-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AT_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AT public docs missing COMPLETE)"
    for path in AT_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AT_FREEZE_ID}: {AT_THESIS})"


def render_at_freeze() -> str:
    lines = [
        "# AT-FREEZE — Wave AT NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §5 AT6 · After **AT-REPORT**  ",
        "> Module: `nano_lm/src/at_freeze_ops.py` · "
        "Runner: `npm run nano:at:freeze`  ",
        "> Parent: [as-freeze.md](as-freeze.md) · "
        "[wave-at-summary.md](wave-at-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AT outcomes locked; Caminho A "
        "H-PRODREG·H-SHIPAPP PROMOTE stays; H-NANOGEN4 ablated "
        "**5.5** (snippet-prefix) PROMOTE locked; AT-REAL-EVAL "
        "battery 6/6 PROMOTE locked; ≤5M hard stays; ship claim "
        f"remains **{SHIP_CLAIM}**; **no Wave AU** without explicit "
        "lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-PRODREG | **PROMOTE** | Caminho A bars · para · FH 0 |",
        "| H-SHIPAPP | **PROMOTE** | LOOKUP·PEAK·DECODE·ABSTAIN 4/4 |",
        "| H-NANOGEN4 | **PROMOTE** | ablated gen 5.5 · snippet-prefix |",
        "| AT-REAL-EVAL | **PROMOTE** | live battery 6/6 · anti-FP |",
        "| AT-REPORT | **PROMOTE** | [summary](wave-at-summary.md) · "
        "[paper-lab](paper-lab-wave-at.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AU** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / unlabeled open chat  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell PEAK / bank-grounded as GPT-class / unlabeled open chat  ",
        "- Sell SAFE mean as answer quality  ",
        "- Sell snippet-prefix DECODE as frontier chat / GPT-class  ",
        "- CTX/SMART/FAST/APP letter clones without named product hole  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "- Rewrite AS/AR/AQ/AP locked outcomes  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:at:freeze",
        "# optional: --skip-ask",
        "npm run nano:at:report",
        "npm run nano:as:freeze",
        "```",
        "",
        "Four-mode smoke must keep LOOKUP · PEAK · DECODE · ABSTAIN "
        "visible.  ",
        "Artifact: `results/nano-lm/wave-at/at_freeze.json` · "
        "Contract: `nano_lm/tests/test_at_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
