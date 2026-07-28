"""Wave AY-FREEZE: lock AY outcomes; no Wave AZ without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

from ay_session_ops import AY0_SHIP_LOCK

__all__ = [
    "AY_FREEZE_ID",
    "AY_THESIS",
    "AY_DECISIONS",
    "AY_PUBLIC",
    "AY_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "SHIP_CLAIM",
    "decide_ay_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_ay_freeze",
]

AY_FREEZE_ID = "AY-FREEZE"
SHIP_CLAIM = AY0_SHIP_LOCK
AY_THESIS = (
    "Wave AY frozen: H-PRODINT·H-SHIPAY·AY-REAL-EVAL·AY-REPORT "
    "PROMOTE; H-NANOGEN9 DEFER (gen stance defer · CAPCHECK closed · "
    "NANOGEN6·7 HOLD · NANOGEN8 DEFER cited · not NANOGEN8 rename); "
    "≤5M stays; ship claim " + SHIP_CLAIM + "; no Wave AZ without reopen"
)

AY_DECISIONS: dict[str, tuple[str, str]] = {
    "H-PRODINT": (
        "docs/results/nano-lm/formal-hprodint-prodint.md",
        "PROMOTE",
    ),
    "H-SHIPAY": (
        "docs/results/nano-lm/formal-hshipay-shipay.md",
        "PROMOTE",
    ),
    "H-NANOGEN9": (
        "docs/results/nano-lm/formal-hnanogen9-nanogen9.md",
        "DEFER",
    ),
    "AY-REAL-EVAL": (
        "docs/results/nano-lm/wave-ay-real-eval.md",
        "PROMOTE",
    ),
    "AY-REPORT": (
        "docs/results/nano-lm/wave-ay-summary.md",
        "PROMOTE",
    ),
}

AY_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ay-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ay.md",
    "docs/results/nano-lm/ay-freeze.md",
)

AY_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-NANOGEN9",
    "AY-REAL-EVAL",
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
    GIVEN AY public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AY_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AY product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_ay_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AY formals + public closeout + product docs
    WHEN applying AY-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AY_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AY public docs missing COMPLETE)"
    for path in AY_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AY_FREEZE_ID}: {AY_THESIS})"


def render_ay_freeze() -> str:
    lines = [
        "# AY-FREEZE — Wave AY NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §5 AY6 · After **AY-REPORT**  ",
        "> Module: `nano_lm/src/ay_freeze_ops.py` · "
        "Runner: `npm run nano:ay:freeze`  ",
        "> Parent: [ax-freeze.md](ax-freeze.md) · "
        "[wave-ay-summary.md](wave-ay-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AY outcomes locked; Caminho A "
        "H-PRODINT·H-SHIPAY PROMOTE stays; H-NANOGEN9 **DEFER** "
        "(gen stance defer · CAPCHECK closed · NANOGEN6·7 HOLD · "
        "NANOGEN8 DEFER cited · not NANOGEN8 rename) locked; "
        "AY-REAL-EVAL battery 8/8 PROMOTE locked; ≤5M hard stays; "
        f"ship claim remains **{SHIP_CLAIM}**; **no Wave AZ** "
        "without explicit lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-PRODINT | **PROMOTE** | intent FH 0 · hard-natural hold · "
        "DECODE content law · p50/p99 · KB |",
        "| H-SHIPAY | **PROMOTE** | modes+content LOOKUP·PEAK·DECODE·"
        "ABSTAIN · intent ABSTAIN · DECODE usable/ABSTAIN |",
        "| H-NANOGEN9 | **DEFER** | stance defer · CAPCHECK closed · "
        "NANOGEN6·7 HOLD · NANOGEN8 DEFER cited · not NANOGEN8+rename |",
        "| AY-REAL-EVAL | **PROMOTE** | live battery 8/8 · "
        "intent-FP ABSTAIN · gen locked |",
        "| AY-REPORT | **PROMOTE** | [summary](wave-ay-summary.md) · "
        "[paper-lab](paper-lab-wave-ay.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AZ** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / unlabeled open chat  ",
        "- Intent-mismatch LOOKUP sold as success  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell PEAK / bank-grounded / span-fallback as GPT-class / "
        "true-continue unlock  ",
        "- Sell SAFE mean as answer quality  ",
        "- Sell NANOGEN9 DEFER / NANOGEN8 DEFER / NANOGEN6·7 HOLD "
        "as gen unlock / mini-AGI  ",
        "- NANOGEN9 = NANOGEN8+rename / truncate-to-span as gen IQ  ",
        "- CTX/SMART/FAST/APP letter clones without named product hole  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "- Rewrite AX/AW/AV/AU/AT/AS/AR/AQ/AP locked outcomes  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:ay:freeze",
        "# optional: --skip-ask",
        "npm run nano:ay:report",
        "npm run nano:ax:freeze",
        "```",
        "",
        "SHIPAY smoke must keep LOOKUP · PEAK · ABSTAIN honest "
        "(DECODE usable or ABSTAIN).  ",
        "Artifact: `results/nano-lm/wave-ay/ay_freeze.json` · "
        "Contract: `nano_lm/tests/test_ay_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
