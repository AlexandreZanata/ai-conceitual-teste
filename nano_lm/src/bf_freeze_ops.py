"""Wave BF-FREEZE: lock BF outcomes; no Wave BG without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

from bf_session_ops import BF0_SHIP_LOCK

__all__ = [
    "BF_FREEZE_ID",
    "BF_THESIS",
    "BF_DECISIONS",
    "BF_PUBLIC",
    "BF_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "SHIP_CLAIM",
    "decide_bf_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_bf_freeze",
]

BF_FREEZE_ID = "BF-FREEZE"
SHIP_CLAIM = BF0_SHIP_LOCK
BF_THESIS = (
    "Wave BF frozen: H-PREDINT·H-SHIPUSE2·H-FASTBF·H-CTXBF·BF-REAL-EVAL·"
    "BF-REPORT PROMOTE; H-NANOGEN16 SKIP (gen stance skip · CAPCHECK "
    "closed · no written M1|M2|M3 plan · NANOGEN6·7 HOLD · NANOGEN8…15 "
    "DEFER cited · not empty DEFER letter · not NANOGEN15 rename); "
    "≤5M stays; ship claim " + SHIP_CLAIM
    + "; no Wave BG without reopen"
)

BF_DECISIONS: dict[str, tuple[str, str]] = {
    "H-PREDINT": (
        "docs/results/nano-lm/formal-hpredint-predint.md",
        "PROMOTE",
    ),
    "H-SHIPUSE2": (
        "docs/results/nano-lm/formal-hshipuse2-shipuse2.md",
        "PROMOTE",
    ),
    "H-FASTBF": (
        "docs/results/nano-lm/formal-hfastbf-fastbf.md",
        "PROMOTE",
    ),
    "H-CTXBF": (
        "docs/results/nano-lm/formal-hctxbf-ctxbf.md",
        "PROMOTE",
    ),
    "H-NANOGEN16": (
        "docs/results/nano-lm/formal-hnanogen16-nanogen16.md",
        "SKIP",
    ),
    "BF-REAL-EVAL": (
        "docs/results/nano-lm/wave-bf-real-eval.md",
        "PROMOTE",
    ),
    "BF-REPORT": (
        "docs/results/nano-lm/wave-bf-summary.md",
        "PROMOTE",
    ),
}

BF_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-bf-summary.md",
    "docs/results/nano-lm/paper-lab-wave-bf.md",
    "docs/results/nano-lm/bf-freeze.md",
)

BF_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-NANOGEN16",
    "BF-REAL-EVAL",
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
    GIVEN BF public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in BF_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking BF product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_bf_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN BF formals + public closeout + product docs
    WHEN applying BF-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in BF_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (BF public docs missing COMPLETE)"
    for path in BF_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({BF_FREEZE_ID}: {BF_THESIS})"


def render_bf_freeze() -> str:
    lines = [
        "# BF-FREEZE — Wave BF NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §9 BF8 · After **BF-REPORT**  ",
        "> Module: `nano_lm/src/bf_freeze_ops.py` · "
        "Runner: `npm run nano:bf:freeze`  ",
        "> Parent: [be-freeze.md](be-freeze.md) · "
        "[wave-bf-summary.md](wave-bf-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave BF outcomes locked; "
        "H-PREDINT·H-SHIPUSE2·H-FASTBF·H-CTXBF PROMOTE stays; "
        "H-NANOGEN16 **SKIP** "
        "(gen stance skip · CAPCHECK closed · no written M1|M2|M3 plan · "
        "NANOGEN6·7 HOLD · NANOGEN8…15 DEFER cited · not empty DEFER "
        "letter · not NANOGEN15 rename) locked; "
        "BF-REAL-EVAL battery 16/16 PROMOTE locked; ≤5M hard stays; "
        f"ship claim remains **{SHIP_CLAIM}**; **no Wave BG** "
        "without explicit lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-PREDINT | **PROMOTE** | BF-FOREVER FH 0 · BA…BE/AZ hold 0 · "
        "over-refuse 0 · live FP 0 · novel FP 0 · no bank stuffing |",
        "| H-SHIPUSE2 | **PROMOTE** | Track A+ util · operator deepen · "
        "paper claim sync · H-SHIPUSE hold · BF residual ABSTAIN |",
        "| H-FASTBF | **PROMOTE** | prod p50/p99 hold · anti-FP hold · "
        "≠ BE `nano:fastbe` · ≠ BD `nano:bd:fastgain` |",
        "| H-CTXBF | **PROMOTE** | howto·cite·long content_ok · "
        "BF/BE/BD/BA/BB/BC/AZ anti-FP · L_eff alone ≠ win |",
        "| H-NANOGEN16 | **SKIP** | stance skip · CAPCHECK closed · "
        "no written M1|M2|M3 · NANOGEN6·7 HOLD · NANOGEN8…15 DEFER "
        "cited · not empty DEFER letter · not NANOGEN15+rename |",
        "| BF-REAL-EVAL | **PROMOTE** | live battery 16/16 · "
        "BF-FOREVER ABSTAIN · over-refuse LOOKUP · util smoke · "
        "gen locked |",
        "| BF-REPORT | **PROMOTE** | [summary](wave-bf-summary.md) · "
        "[paper-lab](paper-lab-wave-bf.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave BG** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / unlabeled open chat  ",
        "- BF-FOREVER predicate LOOKUP sold as success  ",
        "- Over-refuse exact gold sold as safe win  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell PEAK / bank-grounded / span-fallback as GPT-class / "
        "true-continue unlock  ",
        "- Sell SAFE mean as answer quality  ",
        "- Sell NANOGEN16 SKIP / NANOGEN8…15 DEFER / "
        "NANOGEN6·7 HOLD as gen unlock / mini-AGI  ",
        "- NANOGEN16 = NANOGEN15+rename / truncate-to-span as gen IQ  ",
        "- Bank stuffing BF-FOREVER  ",
        "- CTX/SMART/FAST/APP letter clones without named product hole  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "- Rewrite BE/BD/BC/BB/BA/AZ/AY/AX/AW/AV/AU/AT/AS/AR/AQ/AP locked "
        "outcomes  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:bf:freeze",
        "# optional: --skip-ask",
        "npm run nano:bf:report",
        "npm run nano:be:freeze",
        "```",
        "",
        "BF forever/modes smoke must keep LOOKUP · BF-FOREVER ABSTAIN · "
        "over-refuse LOOKUP · OOD ABSTAIN · util LOOKUP honest.  ",
        "Artifact: `results/nano-lm/wave-bf/bf_freeze.json` · "
        "Contract: `nano_lm/tests/test_bf_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
