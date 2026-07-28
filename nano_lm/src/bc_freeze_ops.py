"""Wave BC-FREEZE: lock BC outcomes; no Wave BD without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

from bc_session_ops import BC0_SHIP_LOCK

__all__ = [
    "BC_FREEZE_ID",
    "BC_THESIS",
    "BC_DECISIONS",
    "BC_PUBLIC",
    "BC_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "SHIP_CLAIM",
    "decide_bc_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_bc_freeze",
]

BC_FREEZE_ID = "BC-FREEZE"
SHIP_CLAIM = BC0_SHIP_LOCK
BC_THESIS = (
    "Wave BC frozen: H-OPSFAM·H-FASTLIFT·H-CTXLIFT2·BC-REAL-EVAL·"
    "BC-REPORT PROMOTE; H-NANOGEN13 DEFER (gen stance defer · "
    "CAPCHECK closed · NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER "
    "cited · not NANOGEN12 rename); ≤5M stays; ship claim " + SHIP_CLAIM
    + "; no Wave BD without reopen"
)

BC_DECISIONS: dict[str, tuple[str, str]] = {
    "H-OPSFAM": (
        "docs/results/nano-lm/formal-hopsfam-opsfam.md",
        "PROMOTE",
    ),
    "H-FASTLIFT": (
        "docs/results/nano-lm/formal-hfastlift-bc2.md",
        "PROMOTE",
    ),
    "H-CTXLIFT2": (
        "docs/results/nano-lm/formal-hctxlift2-ctxlift2.md",
        "PROMOTE",
    ),
    "H-NANOGEN13": (
        "docs/results/nano-lm/formal-hnanogen13-nanogen13.md",
        "DEFER",
    ),
    "BC-REAL-EVAL": (
        "docs/results/nano-lm/wave-bc-real-eval.md",
        "PROMOTE",
    ),
    "BC-REPORT": (
        "docs/results/nano-lm/wave-bc-summary.md",
        "PROMOTE",
    ),
}

BC_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-bc-summary.md",
    "docs/results/nano-lm/paper-lab-wave-bc.md",
    "docs/results/nano-lm/bc-freeze.md",
)

BC_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-NANOGEN13",
    "BC-REAL-EVAL",
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
    GIVEN BC public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in BC_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking BC product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_bc_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN BC formals + public closeout + product docs
    WHEN applying BC-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in BC_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (BC public docs missing COMPLETE)"
    for path in BC_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({BC_FREEZE_ID}: {BC_THESIS})"


def render_bc_freeze() -> str:
    lines = [
        "# BC-FREEZE — Wave BC NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §9 BC7 · After **BC-REPORT**  ",
        "> Module: `nano_lm/src/bc_freeze_ops.py` · "
        "Runner: `npm run nano:bc:freeze`  ",
        "> Parent: [bb-freeze.md](bb-freeze.md) · "
        "[wave-bc-summary.md](wave-bc-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave BC outcomes locked; "
        "H-OPSFAM·H-FASTLIFT·H-CTXLIFT2 PROMOTE stays; "
        "H-NANOGEN13 **DEFER** "
        "(gen stance defer · CAPCHECK closed · NANOGEN6·7 HOLD · "
        "NANOGEN8·9·10·11·12 DEFER cited · not NANOGEN12 rename) locked; "
        "BC-REAL-EVAL battery 13/13 PROMOTE locked; ≤5M hard stays; "
        f"ship claim remains **{SHIP_CLAIM}**; **no Wave BD** "
        "without explicit lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-OPSFAM | **PROMOTE** | BC-FOREVER FH 0 · BA/BB/AZ hold 0 · "
        "over-refuse 0 · live FP 0 · no bank stuffing |",
        "| H-FASTLIFT | **PROMOTE** | prod p50/p99 hold · anti-FP hold · "
        "≠ AH `nano:fastlift` · ≠ BB `nano:bb:fasthold` |",
        "| H-CTXLIFT2 | **PROMOTE** | howto·cite·long content_ok · "
        "BC/BA/BB/AZ anti-FP · L_eff alone ≠ win |",
        "| H-NANOGEN13 | **DEFER** | stance defer · CAPCHECK closed · "
        "NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER cited · "
        "not NANOGEN12+rename |",
        "| BC-REAL-EVAL | **PROMOTE** | live battery 13/13 · "
        "BC-FOREVER ABSTAIN · over-refuse LOOKUP · gen locked |",
        "| BC-REPORT | **PROMOTE** | [summary](wave-bc-summary.md) · "
        "[paper-lab](paper-lab-wave-bc.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave BD** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / unlabeled open chat  ",
        "- BC-FOREVER intent LOOKUP sold as success  ",
        "- Over-refuse exact gold sold as safe win  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell PEAK / bank-grounded / span-fallback as GPT-class / "
        "true-continue unlock  ",
        "- Sell SAFE mean as answer quality  ",
        "- Sell NANOGEN13 DEFER / NANOGEN8·9·10·11·12 DEFER / "
        "NANOGEN6·7 HOLD as gen unlock / mini-AGI  ",
        "- NANOGEN13 = NANOGEN12+rename / truncate-to-span as gen IQ  ",
        "- Bank stuffing BC-FOREVER  ",
        "- CTX/SMART/FAST/APP letter clones without named product hole  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "- Rewrite BB/BA/AZ/AY/AX/AW/AV/AU/AT/AS/AR/AQ/AP locked outcomes  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:bc:freeze",
        "# optional: --skip-ask",
        "npm run nano:bc:report",
        "npm run nano:bb:freeze",
        "```",
        "",
        "BC forever/modes smoke must keep LOOKUP · BC-FOREVER ABSTAIN · "
        "over-refuse LOOKUP · OOD ABSTAIN honest.  ",
        "Artifact: `results/nano-lm/wave-bc/bc_freeze.json` · "
        "Contract: `nano_lm/tests/test_bc_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
