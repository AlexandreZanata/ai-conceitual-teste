"""Wave AW-FREEZE: lock AW outcomes; no Wave AX without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

from aw_session_ops import AW0_SHIP_LOCK

__all__ = [
    "AW_FREEZE_ID",
    "AW_THESIS",
    "AW_DECISIONS",
    "AW_PUBLIC",
    "AW_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "SHIP_CLAIM",
    "decide_aw_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_aw_freeze",
]

AW_FREEZE_ID = "AW-FREEZE"
SHIP_CLAIM = AW0_SHIP_LOCK
AW_THESIS = (
    "Wave AW frozen: H-PRODKEEP·H-SHIPKEEP·AW-REAL-EVAL·AW-REPORT "
    "PROMOTE; H-NANOGEN7 HOLD (TAC true_continue unmet · span-fallback ≠ "
    "gen IQ); ≤5M stays; ship claim " + SHIP_CLAIM + "; "
    "no Wave AX without reopen"
)

AW_DECISIONS: dict[str, tuple[str, str]] = {
    "H-PRODKEEP": (
        "docs/results/nano-lm/formal-hprodkeep-prodkeep.md",
        "PROMOTE",
    ),
    "H-SHIPKEEP": (
        "docs/results/nano-lm/formal-hshipkeep-shipkeep.md",
        "PROMOTE",
    ),
    "H-NANOGEN7": (
        "docs/results/nano-lm/formal-hnanogen7-nanogen7.md",
        "HOLD",
    ),
    "AW-REAL-EVAL": (
        "docs/results/nano-lm/wave-aw-real-eval.md",
        "PROMOTE",
    ),
    "AW-REPORT": (
        "docs/results/nano-lm/wave-aw-summary.md",
        "PROMOTE",
    ),
}

AW_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-aw-summary.md",
    "docs/results/nano-lm/paper-lab-wave-aw.md",
    "docs/results/nano-lm/aw-freeze.md",
)

AW_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-NANOGEN7",
    "AW-REAL-EVAL",
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
    GIVEN AW public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AW_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AW product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_aw_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AW formals + public closeout + product docs
    WHEN applying AW-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AW_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AW public docs missing COMPLETE)"
    for path in AW_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AW_FREEZE_ID}: {AW_THESIS})"


def render_aw_freeze() -> str:
    lines = [
        "# AW-FREEZE — Wave AW NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §2 AW6 · After **AW-REPORT**  ",
        "> Module: `nano_lm/src/aw_freeze_ops.py` · "
        "Runner: `npm run nano:aw:freeze`  ",
        "> Parent: [av-freeze.md](av-freeze.md) · "
        "[wave-aw-summary.md](wave-aw-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AW outcomes locked; Caminho A "
        "H-PRODKEEP·H-SHIPKEEP PROMOTE stays; H-NANOGEN7 **HOLD** "
        "(TAC true_continue unmet · span-fallback ≠ gen IQ) locked; "
        "AW-REAL-EVAL battery 8/8 PROMOTE locked; ≤5M hard stays; "
        f"ship claim remains **{SHIP_CLAIM}**; **no Wave AX** "
        "without explicit lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-PRODKEEP | **PROMOTE** | pressure-para · FH 0 · "
        "DECODE content law · p50/p99 · KB |",
        "| H-SHIPKEEP | **PROMOTE** | modes+content LOOKUP·PEAK·DECODE·"
        "ABSTAIN · DECODE usable/ABSTAIN |",
        "| H-NANOGEN7 | **HOLD** | TAC true_continue unmet · "
        "span-fallback ≠ gen IQ · not NANOGEN6 rename |",
        "| AW-REAL-EVAL | **PROMOTE** | live battery 8/8 · gen locked |",
        "| AW-REPORT | **PROMOTE** | [summary](wave-aw-summary.md) · "
        "[paper-lab](paper-lab-wave-aw.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AX** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / unlabeled open chat  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell PEAK / bank-grounded / span-fallback as GPT-class / "
        "TAC true-continue unlock  ",
        "- Sell SAFE mean as answer quality  ",
        "- Sell NANOGEN7 HOLD as TAC true-continue PROMOTE / mini-AGI  ",
        "- NANOGEN7 = NANOGEN6+rename / truncate-to-span as gen IQ  ",
        "- CTX/SMART/FAST/APP letter clones without named product hole  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "- Rewrite AV/AU/AT/AS/AR/AQ/AP locked outcomes  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:aw:freeze",
        "# optional: --skip-ask",
        "npm run nano:aw:report",
        "npm run nano:av:freeze",
        "```",
        "",
        "SHIPKEEP smoke must keep LOOKUP · PEAK · ABSTAIN honest "
        "(DECODE usable or ABSTAIN).  ",
        "Artifact: `results/nano-lm/wave-aw/aw_freeze.json` · "
        "Contract: `nano_lm/tests/test_aw_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
