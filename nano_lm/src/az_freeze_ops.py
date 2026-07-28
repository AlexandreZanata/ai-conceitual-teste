"""Wave AZ-FREEZE: lock AZ outcomes; no Wave BA without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

from az_session_ops import AZ0_SHIP_LOCK

__all__ = [
    "AZ_FREEZE_ID",
    "AZ_THESIS",
    "AZ_DECISIONS",
    "AZ_PUBLIC",
    "AZ_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "SHIP_CLAIM",
    "decide_az_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_az_freeze",
]

AZ_FREEZE_ID = "AZ-FREEZE"
SHIP_CLAIM = AZ0_SHIP_LOCK
AZ_THESIS = (
    "Wave AZ frozen: H-PRODGEN·H-SHIPAZ·AZ-REAL-EVAL·AZ-REPORT "
    "PROMOTE; H-NANOGEN10 DEFER (gen stance defer · CAPCHECK closed · "
    "NANOGEN6·7 HOLD · NANOGEN8·9 DEFER cited · not NANOGEN9 rename); "
    "≤5M stays; ship claim " + SHIP_CLAIM + "; no Wave BA without reopen"
)

AZ_DECISIONS: dict[str, tuple[str, str]] = {
    "H-PRODGEN": (
        "docs/results/nano-lm/formal-hprodgen-prodgen.md",
        "PROMOTE",
    ),
    "H-SHIPAZ": (
        "docs/results/nano-lm/formal-hshipaz-shipaz.md",
        "PROMOTE",
    ),
    "H-NANOGEN10": (
        "docs/results/nano-lm/formal-hnanogen10-nanogen10.md",
        "DEFER",
    ),
    "AZ-REAL-EVAL": (
        "docs/results/nano-lm/wave-az-real-eval.md",
        "PROMOTE",
    ),
    "AZ-REPORT": (
        "docs/results/nano-lm/wave-az-summary.md",
        "PROMOTE",
    ),
}

AZ_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-az-summary.md",
    "docs/results/nano-lm/paper-lab-wave-az.md",
    "docs/results/nano-lm/az-freeze.md",
)

AZ_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-NANOGEN10",
    "AZ-REAL-EVAL",
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
    GIVEN AZ public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AZ_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AZ product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_az_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AZ formals + public closeout + product docs
    WHEN applying AZ-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AZ_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AZ public docs missing COMPLETE)"
    for path in AZ_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AZ_FREEZE_ID}: {AZ_THESIS})"


def render_az_freeze() -> str:
    lines = [
        "# AZ-FREEZE — Wave AZ NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §5 AZ6 · After **AZ-REPORT**  ",
        "> Module: `nano_lm/src/az_freeze_ops.py` · "
        "Runner: `npm run nano:az:freeze`  ",
        "> Parent: [ay-freeze.md](ay-freeze.md) · "
        "[wave-az-summary.md](wave-az-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AZ outcomes locked; Caminho A "
        "H-PRODGEN·H-SHIPAZ PROMOTE stays; H-NANOGEN10 **DEFER** "
        "(gen stance defer · CAPCHECK closed · NANOGEN6·7 HOLD · "
        "NANOGEN8·9 DEFER cited · not NANOGEN9 rename) locked; "
        "AZ-REAL-EVAL battery 9/9 PROMOTE locked; ≤5M hard stays; "
        f"ship claim remains **{SHIP_CLAIM}**; **no Wave BA** "
        "without explicit lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-PRODGEN | **PROMOTE** | held-out FH 0 · over-refuse 0 · "
        "AY named hold · DECODE content law · p50/p99 · KB |",
        "| H-SHIPAZ | **PROMOTE** | modes+content LOOKUP·PEAK·DECODE·"
        "ABSTAIN · held-out ABSTAIN · over-refuse LOOKUP |",
        "| H-NANOGEN10 | **DEFER** | stance defer · CAPCHECK closed · "
        "NANOGEN6·7 HOLD · NANOGEN8·9 DEFER cited · not NANOGEN9+rename |",
        "| AZ-REAL-EVAL | **PROMOTE** | live battery 9/9 · "
        "held-out ABSTAIN · over-refuse LOOKUP · gen locked |",
        "| AZ-REPORT | **PROMOTE** | [summary](wave-az-summary.md) · "
        "[paper-lab](paper-lab-wave-az.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave BA** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / unlabeled open chat  ",
        "- Held-out intent LOOKUP sold as success  ",
        "- Over-refuse exact gold sold as safe win  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell PEAK / bank-grounded / span-fallback as GPT-class / "
        "true-continue unlock  ",
        "- Sell SAFE mean as answer quality  ",
        "- Sell NANOGEN10 DEFER / NANOGEN8·9 DEFER / NANOGEN6·7 HOLD "
        "as gen unlock / mini-AGI  ",
        "- NANOGEN10 = NANOGEN9+rename / truncate-to-span as gen IQ  ",
        "- CTX/SMART/FAST/APP letter clones without named product hole  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "- Rewrite AY/AX/AW/AV/AU/AT/AS/AR/AQ/AP locked outcomes  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:az:freeze",
        "# optional: --skip-ask",
        "npm run nano:az:report",
        "npm run nano:ay:freeze",
        "```",
        "",
        "SHIPAZ smoke must keep LOOKUP · PEAK · ABSTAIN honest "
        "(DECODE usable or ABSTAIN).  ",
        "Artifact: `results/nano-lm/wave-az/az_freeze.json` · "
        "Contract: `nano_lm/tests/test_az_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
