"""Wave AX-FREEZE: lock AX outcomes; no Wave AY without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

from ax_session_ops import AX0_SHIP_LOCK

__all__ = [
    "AX_FREEZE_ID",
    "AX_THESIS",
    "AX_DECISIONS",
    "AX_PUBLIC",
    "AX_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "SHIP_CLAIM",
    "decide_ax_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_ax_freeze",
]

AX_FREEZE_ID = "AX-FREEZE"
SHIP_CLAIM = AX0_SHIP_LOCK
AX_THESIS = (
    "Wave AX frozen: H-PRODNAT·H-SHIPUX·AX-REAL-EVAL·AX-REPORT "
    "PROMOTE; H-NANOGEN8 DEFER (gen stance defer · CAPCHECK closed · "
    "NANOGEN6·7 HOLD cited · not TAC rename); ≤5M stays; ship claim "
    + SHIP_CLAIM
    + "; no Wave AY without reopen"
)

AX_DECISIONS: dict[str, tuple[str, str]] = {
    "H-PRODNAT": (
        "docs/results/nano-lm/formal-hprodnat-prodnat.md",
        "PROMOTE",
    ),
    "H-SHIPUX": (
        "docs/results/nano-lm/formal-hshipux-shipux.md",
        "PROMOTE",
    ),
    "H-NANOGEN8": (
        "docs/results/nano-lm/formal-hnanogen8-nanogen8.md",
        "DEFER",
    ),
    "AX-REAL-EVAL": (
        "docs/results/nano-lm/wave-ax-real-eval.md",
        "PROMOTE",
    ),
    "AX-REPORT": (
        "docs/results/nano-lm/wave-ax-summary.md",
        "PROMOTE",
    ),
}

AX_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ax-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ax.md",
    "docs/results/nano-lm/ax-freeze.md",
)

AX_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-NANOGEN8",
    "AX-REAL-EVAL",
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
    GIVEN AX public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AX_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AX product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_ax_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AX formals + public closeout + product docs
    WHEN applying AX-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AX_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AX public docs missing COMPLETE)"
    for path in AX_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AX_FREEZE_ID}: {AX_THESIS})"


def render_ax_freeze() -> str:
    lines = [
        "# AX-FREEZE — Wave AX NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §5 AX6 · After **AX-REPORT**  ",
        "> Module: `nano_lm/src/ax_freeze_ops.py` · "
        "Runner: `npm run nano:ax:freeze`  ",
        "> Parent: [aw-freeze.md](aw-freeze.md) · "
        "[wave-ax-summary.md](wave-ax-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AX outcomes locked; Caminho A "
        "H-PRODNAT·H-SHIPUX PROMOTE stays; H-NANOGEN8 **DEFER** "
        "(gen stance defer · CAPCHECK closed · NANOGEN6·7 HOLD cited · "
        "not TAC rename) locked; AX-REAL-EVAL battery 8/8 PROMOTE locked; "
        "≤5M hard stays; "
        f"ship claim remains **{SHIP_CLAIM}**; **no Wave AY** "
        "without explicit lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-PRODNAT | **PROMOTE** | hard-natural · FH 0 · "
        "DECODE content law · p50/p99 · KB |",
        "| H-SHIPUX | **PROMOTE** | modes+content LOOKUP·PEAK·DECODE·"
        "ABSTAIN · DECODE usable/ABSTAIN |",
        "| H-NANOGEN8 | **DEFER** | stance defer · CAPCHECK closed · "
        "NANOGEN6·7 HOLD cited · not NANOGEN7+rename |",
        "| AX-REAL-EVAL | **PROMOTE** | live battery 8/8 · gen locked |",
        "| AX-REPORT | **PROMOTE** | [summary](wave-ax-summary.md) · "
        "[paper-lab](paper-lab-wave-ax.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AY** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / unlabeled open chat  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell PEAK / bank-grounded / span-fallback as GPT-class / "
        "true-continue unlock  ",
        "- Sell SAFE mean as answer quality  ",
        "- Sell NANOGEN8 DEFER / NANOGEN6·7 HOLD as gen unlock / mini-AGI  ",
        "- NANOGEN8 = NANOGEN7+rename / truncate-to-span as gen IQ  ",
        "- CTX/SMART/FAST/APP letter clones without named product hole  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "- Rewrite AW/AV/AU/AT/AS/AR/AQ/AP locked outcomes  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:ax:freeze",
        "# optional: --skip-ask",
        "npm run nano:ax:report",
        "npm run nano:aw:freeze",
        "```",
        "",
        "SHIPUX smoke must keep LOOKUP · PEAK · ABSTAIN honest "
        "(DECODE usable or ABSTAIN).  ",
        "Artifact: `results/nano-lm/wave-ax/ax_freeze.json` · "
        "Contract: `nano_lm/tests/test_ax_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
