"""Wave BE-FREEZE: lock BE outcomes; no Wave BF without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

from be_session_ops import BE0_SHIP_LOCK

__all__ = [
    "BE_FREEZE_ID",
    "BE_THESIS",
    "BE_DECISIONS",
    "BE_PUBLIC",
    "BE_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "SHIP_CLAIM",
    "decide_be_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_be_freeze",
]

BE_FREEZE_ID = "BE-FREEZE"
SHIP_CLAIM = BE0_SHIP_LOCK
BE_THESIS = (
    "Wave BE frozen: H-COMPINT·H-SHIPUSE·H-FASTBE·H-CTXBE·BE-REAL-EVAL·"
    "BE-REPORT PROMOTE; H-NANOGEN15 DEFER (gen stance defer once · "
    "CAPCHECK closed · NANOGEN6·7 HOLD · NANOGEN8…14 DEFER cited · "
    "not NANOGEN14 rename); ≤5M stays; ship claim " + SHIP_CLAIM
    + "; no Wave BF without reopen"
)

BE_DECISIONS: dict[str, tuple[str, str]] = {
    "H-COMPINT": (
        "docs/results/nano-lm/formal-hcompint-compint.md",
        "PROMOTE",
    ),
    "H-SHIPUSE": (
        "docs/results/nano-lm/formal-hshipuse-shipuse.md",
        "PROMOTE",
    ),
    "H-FASTBE": (
        "docs/results/nano-lm/formal-hfastbe-fastbe.md",
        "PROMOTE",
    ),
    "H-CTXBE": (
        "docs/results/nano-lm/formal-hctxbe-ctxbe.md",
        "PROMOTE",
    ),
    "H-NANOGEN15": (
        "docs/results/nano-lm/formal-hnanogen15-nanogen15.md",
        "DEFER",
    ),
    "BE-REAL-EVAL": (
        "docs/results/nano-lm/wave-be-real-eval.md",
        "PROMOTE",
    ),
    "BE-REPORT": (
        "docs/results/nano-lm/wave-be-summary.md",
        "PROMOTE",
    ),
}

BE_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-be-summary.md",
    "docs/results/nano-lm/paper-lab-wave-be.md",
    "docs/results/nano-lm/be-freeze.md",
)

BE_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-NANOGEN15",
    "BE-REAL-EVAL",
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
    GIVEN BE public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in BE_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking BE product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_be_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN BE formals + public closeout + product docs
    WHEN applying BE-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in BE_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (BE public docs missing COMPLETE)"
    for path in BE_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({BE_FREEZE_ID}: {BE_THESIS})"


def render_be_freeze() -> str:
    lines = [
        "# BE-FREEZE — Wave BE NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §9 BE8 · After **BE-REPORT**  ",
        "> Module: `nano_lm/src/be_freeze_ops.py` · "
        "Runner: `npm run nano:be:freeze`  ",
        "> Parent: [bd-freeze.md](bd-freeze.md) · "
        "[wave-be-summary.md](wave-be-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave BE outcomes locked; "
        "H-COMPINT·H-SHIPUSE·H-FASTBE·H-CTXBE PROMOTE stays; "
        "H-NANOGEN15 **DEFER** "
        "(gen stance defer once · CAPCHECK closed · NANOGEN6·7 HOLD · "
        "NANOGEN8…14 DEFER cited · not NANOGEN14 rename) locked; "
        "BE-REAL-EVAL battery 15/15 PROMOTE locked; ≤5M hard stays; "
        f"ship claim remains **{SHIP_CLAIM}**; **no Wave BF** "
        "without explicit lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-COMPINT | **PROMOTE** | BE-FOREVER FH 0 · BA…BD/AZ hold 0 · "
        "over-refuse 0 · live FP 0 · novel FP 0 · no bank stuffing |",
        "| H-SHIPUSE | **PROMOTE** | Track A util · demo smoke · "
        "operator card · paper claim sync · BE residual ABSTAIN |",
        "| H-FASTBE | **PROMOTE** | prod p50/p99 hold · anti-FP hold · "
        "≠ BD `nano:bd:fastgain` · ≠ AH `nano:fastlift` |",
        "| H-CTXBE | **PROMOTE** | howto·cite·long content_ok · "
        "BE/BD/BA/BB/BC/AZ anti-FP · L_eff alone ≠ win |",
        "| H-NANOGEN15 | **DEFER** | stance defer once · CAPCHECK closed · "
        "NANOGEN6·7 HOLD · NANOGEN8…14 DEFER cited · "
        "not NANOGEN14+rename |",
        "| BE-REAL-EVAL | **PROMOTE** | live battery 15/15 · "
        "BE-FOREVER ABSTAIN · over-refuse LOOKUP · util smoke · "
        "gen locked |",
        "| BE-REPORT | **PROMOTE** | [summary](wave-be-summary.md) · "
        "[paper-lab](paper-lab-wave-be.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave BF** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / unlabeled open chat  ",
        "- BE-FOREVER type/coercion LOOKUP sold as success  ",
        "- Over-refuse exact gold sold as safe win  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell PEAK / bank-grounded / span-fallback as GPT-class / "
        "true-continue unlock  ",
        "- Sell SAFE mean as answer quality  ",
        "- Sell NANOGEN15 DEFER / NANOGEN8…14 DEFER / "
        "NANOGEN6·7 HOLD as gen unlock / mini-AGI  ",
        "- NANOGEN15 = NANOGEN14+rename / truncate-to-span as gen IQ  ",
        "- Bank stuffing BE-FOREVER  ",
        "- CTX/SMART/FAST/APP letter clones without named product hole  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "- Rewrite BD/BC/BB/BA/AZ/AY/AX/AW/AV/AU/AT/AS/AR/AQ/AP locked "
        "outcomes  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:be:freeze",
        "# optional: --skip-ask",
        "npm run nano:be:report",
        "npm run nano:bd:freeze",
        "```",
        "",
        "BE forever/modes smoke must keep LOOKUP · BE-FOREVER ABSTAIN · "
        "over-refuse LOOKUP · OOD ABSTAIN · util LOOKUP honest.  ",
        "Artifact: `results/nano-lm/wave-be/be_freeze.json` · "
        "Contract: `nano_lm/tests/test_be_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
