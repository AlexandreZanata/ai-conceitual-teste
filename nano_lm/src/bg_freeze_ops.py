"""Wave BG-FREEZE: lock BG outcomes; no Wave BH without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

from bg_session_ops import BG0_SHIP_LOCK

__all__ = [
    "BG_FREEZE_ID",
    "BG_THESIS",
    "BG_DECISIONS",
    "BG_PUBLIC",
    "BG_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "SHIP_CLAIM",
    "decide_bg_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_bg_freeze",
]

BG_FREEZE_ID = "BG-FREEZE"
SHIP_CLAIM = BG0_SHIP_LOCK
BG_THESIS = (
    "Wave BG frozen: H-UNARYINT·H-SHIPPUB·H-FASTBG·H-CTXBG·BG-REAL-EVAL·"
    "BG-REPORT PROMOTE; H-NANOGEN17 SKIP (gen stance skip · CAPCHECK "
    "closed · no written M1|M2|M3 plan · NANOGEN6·7 HOLD · NANOGEN8…15 "
    "DEFER · NANOGEN16 SKIP cited · not empty DEFER letter · not "
    "NANOGEN16 rename); ≤5M stays; ship claim " + SHIP_CLAIM
    + "; no Wave BH without reopen"
)

BG_DECISIONS: dict[str, tuple[str, str]] = {
    "H-UNARYINT": (
        "docs/results/nano-lm/formal-hunaryint-unaryint.md",
        "PROMOTE",
    ),
    "H-SHIPPUB": (
        "docs/results/nano-lm/formal-hshippub-shippub.md",
        "PROMOTE",
    ),
    "H-FASTBG": (
        "docs/results/nano-lm/formal-hfastbg-fastbg.md",
        "PROMOTE",
    ),
    "H-CTXBG": (
        "docs/results/nano-lm/formal-hctxbg-ctxbg.md",
        "PROMOTE",
    ),
    "H-NANOGEN17": (
        "docs/results/nano-lm/formal-hnanogen17-nanogen17.md",
        "SKIP",
    ),
    "BG-REAL-EVAL": (
        "docs/results/nano-lm/wave-bg-real-eval.md",
        "PROMOTE",
    ),
    "BG-REPORT": (
        "docs/results/nano-lm/wave-bg-summary.md",
        "PROMOTE",
    ),
}

BG_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-bg-summary.md",
    "docs/results/nano-lm/paper-lab-wave-bg.md",
    "docs/results/nano-lm/bg-freeze.md",
)

BG_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-NANOGEN17",
    "BG-REAL-EVAL",
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
    GIVEN BG public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in BG_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking BG product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_bg_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN BG formals + public closeout + product docs
    WHEN applying BG-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in BG_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (BG public docs missing COMPLETE)"
    for path in BG_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({BG_FREEZE_ID}: {BG_THESIS})"


def render_bg_freeze() -> str:
    lines = [
        "# BG-FREEZE — Wave BG NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §9 BG8 · After **BG-REPORT**  ",
        "> Module: `nano_lm/src/bg_freeze_ops.py` · "
        "Runner: `npm run nano:bg:freeze`  ",
        "> Parent: [bf-freeze.md](bf-freeze.md) · "
        "[wave-bg-summary.md](wave-bg-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave BG outcomes locked; "
        "H-UNARYINT·H-SHIPPUB·H-FASTBG·H-CTXBG PROMOTE stays; "
        "H-NANOGEN17 **SKIP** "
        "(gen stance skip · CAPCHECK closed · no written M1|M2|M3 plan · "
        "NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · NANOGEN16 SKIP cited · "
        "not empty DEFER letter · not NANOGEN16 rename) locked; "
        "BG-REAL-EVAL battery 17/17 PROMOTE locked; ≤5M hard stays; "
        f"ship claim remains **{SHIP_CLAIM}**; **no Wave BH** "
        "without explicit lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-UNARYINT | **PROMOTE** | BG-FOREVER FH 0 · BA…BF/AZ hold 0 · "
        "over-refuse 0 · live FP 0 · novel FP 0 · no bank stuffing |",
        "| H-SHIPPUB | **PROMOTE** | Track A++ util · operator deepen · "
        "paper/arXiv sync · H-SHIPUSE2 hold · BG residual ABSTAIN |",
        "| H-FASTBG | **PROMOTE** | prod p50/p99 hold · anti-FP hold · "
        "≠ BF `nano:fastbf` · ≠ BE `nano:fastbe` |",
        "| H-CTXBG | **PROMOTE** | howto·cite·long content_ok · "
        "BG/BF/BE/BD/BA/BB/BC/AZ anti-FP · L_eff alone ≠ win |",
        "| H-NANOGEN17 | **SKIP** | stance skip · CAPCHECK closed · "
        "no written M1|M2|M3 · NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · "
        "NANOGEN16 SKIP cited · not empty DEFER letter · "
        "not NANOGEN16+rename |",
        "| BG-REAL-EVAL | **PROMOTE** | live battery 17/17 · "
        "BG-FOREVER ABSTAIN · over-refuse LOOKUP · util smoke · "
        "gen locked |",
        "| BG-REPORT | **PROMOTE** | [summary](wave-bg-summary.md) · "
        "[paper-lab](paper-lab-wave-bg.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave BH** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / unlabeled open chat  ",
        "- BG-FOREVER unary/transform LOOKUP sold as success  ",
        "- Over-refuse exact gold sold as safe win  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell PEAK / bank-grounded / span-fallback as GPT-class / "
        "true-continue unlock  ",
        "- Sell SAFE mean as answer quality  ",
        "- Sell NANOGEN17 SKIP / NANOGEN16 SKIP / NANOGEN8…15 DEFER / "
        "NANOGEN6·7 HOLD as gen unlock / mini-AGI  ",
        "- NANOGEN17 = NANOGEN16+rename / truncate-to-span as gen IQ  ",
        "- Bank stuffing BG-FOREVER  ",
        "- CTX/SMART/FAST/APP letter clones without named product hole  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "- Rewrite BF/BE/BD/BC/BB/BA/AZ/AY/AX/AW/AV/AU/AT/AS/AR/AQ/AP "
        "locked outcomes  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:bg:freeze",
        "# optional: --skip-ask",
        "npm run nano:bg:report",
        "npm run nano:bf:freeze",
        "```",
        "",
        "BG forever/modes smoke must keep LOOKUP · BG-FOREVER ABSTAIN · "
        "over-refuse LOOKUP · OOD ABSTAIN · util LOOKUP honest.  ",
        "Artifact: `results/nano-lm/wave-bg/bg_freeze.json` · "
        "Contract: `nano_lm/tests/test_bg_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
