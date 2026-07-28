"""Wave BB-FREEZE: lock BB outcomes; no Wave BC without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

from bb_session_ops import BB0_SHIP_LOCK

__all__ = [
    "BB_FREEZE_ID",
    "BB_THESIS",
    "BB_DECISIONS",
    "BB_PUBLIC",
    "BB_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "SHIP_CLAIM",
    "decide_bb_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_bb_freeze",
]

BB_FREEZE_ID = "BB-FREEZE"
SHIP_CLAIM = BB0_SHIP_LOCK
BB_THESIS = (
    "Wave BB frozen: H-INTENTGEN·H-FASTHOLD·H-CTXHOLD·BB-REAL-EVAL·"
    "BB-REPORT PROMOTE; H-NANOGEN12 DEFER (gen stance defer · "
    "CAPCHECK closed · NANOGEN6·7 HOLD · NANOGEN8·9·10·11 DEFER cited · "
    "not NANOGEN11 rename); ≤5M stays; ship claim " + SHIP_CLAIM
    + "; no Wave BC without reopen"
)

BB_DECISIONS: dict[str, tuple[str, str]] = {
    "H-INTENTGEN": (
        "docs/results/nano-lm/formal-hintentgen-intentgen.md",
        "PROMOTE",
    ),
    "H-FASTHOLD": (
        "docs/results/nano-lm/formal-hfasthold-fasthold.md",
        "PROMOTE",
    ),
    "H-CTXHOLD": (
        "docs/results/nano-lm/formal-hctxhold-ctxhold.md",
        "PROMOTE",
    ),
    "H-NANOGEN12": (
        "docs/results/nano-lm/formal-hnanogen12-nanogen12.md",
        "DEFER",
    ),
    "BB-REAL-EVAL": (
        "docs/results/nano-lm/wave-bb-real-eval.md",
        "PROMOTE",
    ),
    "BB-REPORT": (
        "docs/results/nano-lm/wave-bb-summary.md",
        "PROMOTE",
    ),
}

BB_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-bb-summary.md",
    "docs/results/nano-lm/paper-lab-wave-bb.md",
    "docs/results/nano-lm/bb-freeze.md",
)

BB_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-NANOGEN12",
    "BB-REAL-EVAL",
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
    GIVEN BB public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in BB_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking BB product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_bb_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN BB formals + public closeout + product docs
    WHEN applying BB-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in BB_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (BB public docs missing COMPLETE)"
    for path in BB_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({BB_FREEZE_ID}: {BB_THESIS})"


def render_bb_freeze() -> str:
    lines = [
        "# BB-FREEZE — Wave BB NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §8 BB7 · After **BB-REPORT**  ",
        "> Module: `nano_lm/src/bb_freeze_ops.py` · "
        "Runner: `npm run nano:bb:freeze`  ",
        "> Parent: [ba-freeze.md](ba-freeze.md) · "
        "[wave-bb-summary.md](wave-bb-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave BB outcomes locked; "
        "H-INTENTGEN·H-FASTHOLD·H-CTXHOLD PROMOTE stays; "
        "H-NANOGEN12 **DEFER** "
        "(gen stance defer · CAPCHECK closed · NANOGEN6·7 HOLD · "
        "NANOGEN8·9·10·11 DEFER cited · not NANOGEN11 rename) locked; "
        "BB-REAL-EVAL battery 12/12 PROMOTE locked; ≤5M hard stays; "
        f"ship claim remains **{SHIP_CLAIM}**; **no Wave BC** "
        "without explicit lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-INTENTGEN | **PROMOTE** | BB-FOREVER FH 0 · BA hold 0 · "
        "AZ hold 0 · over-refuse 0 · live FP 0 · no bank stuffing |",
        "| H-FASTHOLD | **PROMOTE** | prod p50/p99 hold · anti-FP hold · "
        "≠ BA `nano:ba:fastreal` · ≠ AG `nano:fastreal` |",
        "| H-CTXHOLD | **PROMOTE** | howto·cite·long content_ok · "
        "BB/BA/AZ anti-FP · L_eff alone ≠ win |",
        "| H-NANOGEN12 | **DEFER** | stance defer · CAPCHECK closed · "
        "NANOGEN6·7 HOLD · NANOGEN8·9·10·11 DEFER cited · "
        "not NANOGEN11+rename |",
        "| BB-REAL-EVAL | **PROMOTE** | live battery 12/12 · "
        "BB-FOREVER ABSTAIN · over-refuse LOOKUP · gen locked |",
        "| BB-REPORT | **PROMOTE** | [summary](wave-bb-summary.md) · "
        "[paper-lab](paper-lab-wave-bb.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave BC** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / unlabeled open chat  ",
        "- BB-FOREVER intent LOOKUP sold as success  ",
        "- Over-refuse exact gold sold as safe win  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell PEAK / bank-grounded / span-fallback as GPT-class / "
        "true-continue unlock  ",
        "- Sell SAFE mean as answer quality  ",
        "- Sell NANOGEN12 DEFER / NANOGEN8·9·10·11 DEFER / NANOGEN6·7 HOLD "
        "as gen unlock / mini-AGI  ",
        "- NANOGEN12 = NANOGEN11+rename / truncate-to-span as gen IQ  ",
        "- Bank stuffing BB-FOREVER  ",
        "- CTX/SMART/FAST/APP letter clones without named product hole  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "- Rewrite BA/AZ/AY/AX/AW/AV/AU/AT/AS/AR/AQ/AP locked outcomes  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:bb:freeze",
        "# optional: --skip-ask",
        "npm run nano:bb:report",
        "npm run nano:ba:freeze",
        "```",
        "",
        "BB forever/modes smoke must keep LOOKUP · BB-FOREVER ABSTAIN · "
        "over-refuse LOOKUP · OOD ABSTAIN honest.  ",
        "Artifact: `results/nano-lm/wave-bb/bb_freeze.json` · "
        "Contract: `nano_lm/tests/test_bb_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
