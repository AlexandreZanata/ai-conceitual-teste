"""Wave AU-FREEZE: lock AU outcomes; no Wave AV without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "AU_FREEZE_ID",
    "AU_THESIS",
    "AU_DECISIONS",
    "AU_PUBLIC",
    "AU_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "SHIP_CLAIM",
    "decide_au_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_au_freeze",
]

AU_FREEZE_ID = "AU-FREEZE"
SHIP_CLAIM = (
    "AF packaged stack + AQ product layer + AS trust path + "
    "ablated DECODE (snippet-prefix + gibberish-tail STRICT) — "
    "not unlabeled open chat LM"
)
AU_THESIS = (
    "Wave AU frozen: H-PRODHARD·H-SHIPREAL·H-NANOGEN5·AU-REAL-EVAL·"
    "AU-REPORT PROMOTE; STRICT ablated DECODE 5.5 (snippet-prefix + "
    "gibberish-tail); ≤5M stays; ship claim " + SHIP_CLAIM + "; "
    "no Wave AV without reopen"
)

AU_DECISIONS: dict[str, tuple[str, str]] = {
    "H-PRODHARD": (
        "docs/results/nano-lm/formal-hprodhard-prodhard.md",
        "PROMOTE",
    ),
    "H-SHIPREAL": (
        "docs/results/nano-lm/formal-hshipreal-shipreal.md",
        "PROMOTE",
    ),
    "H-NANOGEN5": (
        "docs/results/nano-lm/formal-hnanogen5-nanogen5.md",
        "PROMOTE",
    ),
    "AU-REAL-EVAL": (
        "docs/results/nano-lm/wave-au-real-eval.md",
        "PROMOTE",
    ),
    "AU-REPORT": (
        "docs/results/nano-lm/wave-au-summary.md",
        "PROMOTE",
    ),
}

AU_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-au-summary.md",
    "docs/results/nano-lm/paper-lab-wave-au.md",
    "docs/results/nano-lm/au-freeze.md",
)

AU_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-NANOGEN5",
    "AU-REAL-EVAL",
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
    GIVEN AU public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AU_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AU product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_au_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AU formals + public closeout + product docs
    WHEN applying AU-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AU_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AU public docs missing COMPLETE)"
    for path in AU_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AU_FREEZE_ID}: {AU_THESIS})"


def render_au_freeze() -> str:
    lines = [
        "# AU-FREEZE — Wave AU NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §5 AU6 · After **AU-REPORT**  ",
        "> Module: `nano_lm/src/au_freeze_ops.py` · "
        "Runner: `npm run nano:au:freeze`  ",
        "> Parent: [at-freeze.md](at-freeze.md) · "
        "[wave-au-summary.md](wave-au-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AU outcomes locked; Caminho A "
        "H-PRODHARD·H-SHIPREAL PROMOTE stays; H-NANOGEN5 STRICT "
        "ablated **5.5** (snippet-prefix + gibberish-tail) PROMOTE "
        "locked; AU-REAL-EVAL battery 7/7 PROMOTE locked; ≤5M hard "
        f"stays; ship claim remains **{SHIP_CLAIM}**; **no Wave AV** "
        "without explicit lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-PRODHARD | **PROMOTE** | live-audit · near-miss ABSTAIN · "
        "para · PEAK usable · FH 0 |",
        "| H-SHIPREAL | **PROMOTE** | modes+content LOOKUP·PEAK·DECODE·"
        "ABSTAIN 4/4 |",
        "| H-NANOGEN5 | **PROMOTE** | strict ablated 5.5 · "
        "snippet-prefix · gibberish-tail |",
        "| AU-REAL-EVAL | **PROMOTE** | live battery 7/7 · anti-FP |",
        "| AU-REPORT | **PROMOTE** | [summary](wave-au-summary.md) · "
        "[paper-lab](paper-lab-wave-au.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AV** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / unlabeled open chat  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell PEAK / bank-grounded as GPT-class / unlabeled open chat  ",
        "- Sell SAFE mean as answer quality  ",
        "- Sell STRICT ablated / gold-substring / gibberish-tail as "
        "frontier chat / GPT-class  ",
        "- CTX/SMART/FAST/APP letter clones without named product hole  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "- Rewrite AT/AS/AR/AQ/AP locked outcomes  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:au:freeze",
        "# optional: --skip-ask",
        "npm run nano:au:report",
        "npm run nano:at:freeze",
        "```",
        "",
        "Four-mode smoke must keep LOOKUP · PEAK · DECODE · ABSTAIN "
        "visible (SHIPREAL content bars).  ",
        "Artifact: `results/nano-lm/wave-au/au_freeze.json` · "
        "Contract: `nano_lm/tests/test_au_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
