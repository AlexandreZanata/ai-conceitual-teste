"""Wave BD-FREEZE: lock BD outcomes; no Wave BE without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

from bd_session_ops import BD0_SHIP_LOCK

__all__ = [
    "BD_FREEZE_ID",
    "BD_THESIS",
    "BD_DECISIONS",
    "BD_PUBLIC",
    "BD_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "SHIP_CLAIM",
    "decide_bd_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_bd_freeze",
]

BD_FREEZE_ID = "BD-FREEZE"
SHIP_CLAIM = BD0_SHIP_LOCK
BD_THESIS = (
    "Wave BD frozen: H-SEMINT·H-FASTGAIN·H-CTXGAIN·BD-REAL-EVAL·"
    "BD-REPORT PROMOTE; H-NANOGEN14 DEFER (gen stance defer · "
    "CAPCHECK closed · NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12·13 DEFER "
    "cited · not NANOGEN13 rename); ≤5M stays; ship claim " + SHIP_CLAIM
    + "; no Wave BE without reopen"
)

BD_DECISIONS: dict[str, tuple[str, str]] = {
    "H-SEMINT": (
        "docs/results/nano-lm/formal-hsemint-semint.md",
        "PROMOTE",
    ),
    "H-FASTGAIN": (
        "docs/results/nano-lm/formal-hfastgain-fastgain.md",
        "PROMOTE",
    ),
    "H-CTXGAIN": (
        "docs/results/nano-lm/formal-hctxgain-ctxgain.md",
        "PROMOTE",
    ),
    "H-NANOGEN14": (
        "docs/results/nano-lm/formal-hnanogen14-nanogen14.md",
        "DEFER",
    ),
    "BD-REAL-EVAL": (
        "docs/results/nano-lm/wave-bd-real-eval.md",
        "PROMOTE",
    ),
    "BD-REPORT": (
        "docs/results/nano-lm/wave-bd-summary.md",
        "PROMOTE",
    ),
}

BD_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-bd-summary.md",
    "docs/results/nano-lm/paper-lab-wave-bd.md",
    "docs/results/nano-lm/bd-freeze.md",
)

BD_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-NANOGEN14",
    "BD-REAL-EVAL",
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
    GIVEN BD public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in BD_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking BD product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_bd_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN BD formals + public closeout + product docs
    WHEN applying BD-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in BD_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (BD public docs missing COMPLETE)"
    for path in BD_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({BD_FREEZE_ID}: {BD_THESIS})"


def render_bd_freeze() -> str:
    lines = [
        "# BD-FREEZE — Wave BD NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §9 BD7 · After **BD-REPORT**  ",
        "> Module: `nano_lm/src/bd_freeze_ops.py` · "
        "Runner: `npm run nano:bd:freeze`  ",
        "> Parent: [bc-freeze.md](bc-freeze.md) · "
        "[wave-bd-summary.md](wave-bd-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave BD outcomes locked; "
        "H-SEMINT·H-FASTGAIN·H-CTXGAIN PROMOTE stays; "
        "H-NANOGEN14 **DEFER** "
        "(gen stance defer · CAPCHECK closed · NANOGEN6·7 HOLD · "
        "NANOGEN8·9·10·11·12·13 DEFER cited · not NANOGEN13 rename) locked; "
        "BD-REAL-EVAL battery 14/14 PROMOTE locked; ≤5M hard stays; "
        f"ship claim remains **{SHIP_CLAIM}**; **no Wave BE** "
        "without explicit lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-SEMINT | **PROMOTE** | BD-FOREVER FH 0 · BA/BB/BC/AZ hold 0 · "
        "over-refuse 0 · live FP 0 · no bank stuffing |",
        "| H-FASTGAIN | **PROMOTE** | prod p50/p99 hold · anti-FP hold · "
        "≠ AH `nano:fastlift` · ≠ BC `nano:bc:fastlift` |",
        "| H-CTXGAIN | **PROMOTE** | howto·cite·long content_ok · "
        "BD/BA/BB/BC/AZ anti-FP · L_eff alone ≠ win |",
        "| H-NANOGEN14 | **DEFER** | stance defer · CAPCHECK closed · "
        "NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12·13 DEFER cited · "
        "not NANOGEN13+rename |",
        "| BD-REAL-EVAL | **PROMOTE** | live battery 14/14 · "
        "BD-FOREVER ABSTAIN · over-refuse LOOKUP · gen locked |",
        "| BD-REPORT | **PROMOTE** | [summary](wave-bd-summary.md) · "
        "[paper-lab](paper-lab-wave-bd.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave BE** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / unlabeled open chat  ",
        "- BD-FOREVER semantic LOOKUP sold as success  ",
        "- Over-refuse exact gold sold as safe win  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell PEAK / bank-grounded / span-fallback as GPT-class / "
        "true-continue unlock  ",
        "- Sell SAFE mean as answer quality  ",
        "- Sell NANOGEN14 DEFER / NANOGEN8·9·10·11·12·13 DEFER / "
        "NANOGEN6·7 HOLD as gen unlock / mini-AGI  ",
        "- NANOGEN14 = NANOGEN13+rename / truncate-to-span as gen IQ  ",
        "- Bank stuffing BD-FOREVER  ",
        "- CTX/SMART/FAST/APP letter clones without named product hole  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "- Rewrite BC/BB/BA/AZ/AY/AX/AW/AV/AU/AT/AS/AR/AQ/AP locked "
        "outcomes  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:bd:freeze",
        "# optional: --skip-ask",
        "npm run nano:bd:report",
        "npm run nano:bc:freeze",
        "```",
        "",
        "BD forever/modes smoke must keep LOOKUP · BD-FOREVER ABSTAIN · "
        "over-refuse LOOKUP · OOD ABSTAIN honest.  ",
        "Artifact: `results/nano-lm/wave-bd/bd_freeze.json` · "
        "Contract: `nano_lm/tests/test_bd_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
