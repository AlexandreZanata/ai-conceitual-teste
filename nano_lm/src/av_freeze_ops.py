"""Wave AV-FREEZE: lock AV outcomes; no Wave AW without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

from av_session_ops import AV0_SHIP_LOCK

__all__ = [
    "AV_FREEZE_ID",
    "AV_THESIS",
    "AV_DECISIONS",
    "AV_PUBLIC",
    "AV_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "SHIP_CLAIM",
    "decide_av_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_av_freeze",
]

AV_FREEZE_ID = "AV-FREEZE"
SHIP_CLAIM = AV0_SHIP_LOCK
AV_THESIS = (
    "Wave AV frozen: H-PRODSHIP·H-SHIPUI2·AV-REAL-EVAL·AV-REPORT "
    "PROMOTE; H-NANOGEN6 HOLD (true_continue unmet · span-fallback ≠ "
    "gen IQ); ≤5M stays; ship claim " + SHIP_CLAIM + "; "
    "no Wave AW without reopen"
)

AV_DECISIONS: dict[str, tuple[str, str]] = {
    "H-PRODSHIP": (
        "docs/results/nano-lm/formal-hprodship-prodship.md",
        "PROMOTE",
    ),
    "H-SHIPUI2": (
        "docs/results/nano-lm/formal-hshipui2-shipui2.md",
        "PROMOTE",
    ),
    "H-NANOGEN6": (
        "docs/results/nano-lm/formal-hnanogen6-nanogen6.md",
        "HOLD",
    ),
    "AV-REAL-EVAL": (
        "docs/results/nano-lm/wave-av-real-eval.md",
        "PROMOTE",
    ),
    "AV-REPORT": (
        "docs/results/nano-lm/wave-av-summary.md",
        "PROMOTE",
    ),
}

AV_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-av-summary.md",
    "docs/results/nano-lm/paper-lab-wave-av.md",
    "docs/results/nano-lm/av-freeze.md",
)

AV_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-NANOGEN6",
    "AV-REAL-EVAL",
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
    GIVEN AV public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AV_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AV product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_av_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AV formals + public closeout + product docs
    WHEN applying AV-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AV_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AV public docs missing COMPLETE)"
    for path in AV_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AV_FREEZE_ID}: {AV_THESIS})"


def render_av_freeze() -> str:
    lines = [
        "# AV-FREEZE — Wave AV NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §5 AV6 · After **AV-REPORT**  ",
        "> Module: `nano_lm/src/av_freeze_ops.py` · "
        "Runner: `npm run nano:av:freeze`  ",
        "> Parent: [au-freeze.md](au-freeze.md) · "
        "[wave-av-summary.md](wave-av-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AV outcomes locked; Caminho A "
        "H-PRODSHIP·H-SHIPUI2 PROMOTE stays; H-NANOGEN6 **HOLD** "
        "(true_continue unmet · span-fallback ≠ gen IQ) locked; "
        "AV-REAL-EVAL battery 8/8 PROMOTE locked; ≤5M hard stays; "
        f"ship claim remains **{SHIP_CLAIM}**; **no Wave AW** "
        "without explicit lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-PRODSHIP | **PROMOTE** | external para · FH 0 · "
        "DECODE content law · p50/p99 · KB |",
        "| H-SHIPUI2 | **PROMOTE** | modes+content LOOKUP·PEAK·DECODE·"
        "ABSTAIN · DECODE usable/ABSTAIN |",
        "| H-NANOGEN6 | **HOLD** | true_continue unmet · "
        "span-fallback ≠ gen IQ · refuse-or-continue |",
        "| AV-REAL-EVAL | **PROMOTE** | live battery 8/8 · gen locked |",
        "| AV-REPORT | **PROMOTE** | [summary](wave-av-summary.md) · "
        "[paper-lab](paper-lab-wave-av.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AW** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / unlabeled open chat  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell PEAK / bank-grounded / span-fallback as GPT-class / "
        "true-continue unlock  ",
        "- Sell SAFE mean as answer quality  ",
        "- Sell NANOGEN6 HOLD as true-continue PROMOTE / mini-AGI  ",
        "- NANOGEN6 = NANOGEN5+rename / truncate-to-span as gen IQ  ",
        "- CTX/SMART/FAST/APP letter clones without named product hole  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "- Rewrite AU/AT/AS/AR/AQ/AP locked outcomes  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:av:freeze",
        "# optional: --skip-ask",
        "npm run nano:av:report",
        "npm run nano:au:freeze",
        "```",
        "",
        "SHIPUI2 smoke must keep LOOKUP · PEAK · ABSTAIN honest "
        "(DECODE usable or ABSTAIN).  ",
        "Artifact: `results/nano-lm/wave-av/av_freeze.json` · "
        "Contract: `nano_lm/tests/test_av_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
