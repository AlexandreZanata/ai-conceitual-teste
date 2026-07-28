"""Wave BA-FREEZE: lock BA outcomes; no Wave BB without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

from ba_session_ops import BA0_SHIP_LOCK

__all__ = [
    "BA_FREEZE_ID",
    "BA_THESIS",
    "BA_DECISIONS",
    "BA_PUBLIC",
    "BA_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "SHIP_CLAIM",
    "decide_ba_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_ba_freeze",
]

BA_FREEZE_ID = "BA-FREEZE"
SHIP_CLAIM = BA0_SHIP_LOCK
BA_THESIS = (
    "Wave BA frozen: H-REALGAIN·H-FASTREAL·H-CTXREAL2·BA-REAL-EVAL·"
    "BA-REPORT PROMOTE; H-NANOGEN11 DEFER (gen stance defer · "
    "CAPCHECK closed · NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER cited · "
    "not NANOGEN10 rename); ≤5M stays; ship claim " + SHIP_CLAIM
    + "; no Wave BB without reopen"
)

BA_DECISIONS: dict[str, tuple[str, str]] = {
    "H-REALGAIN": (
        "docs/results/nano-lm/formal-hrealgain-realgain.md",
        "PROMOTE",
    ),
    "H-FASTREAL": (
        "docs/results/nano-lm/formal-hfastreal-ba2.md",
        "PROMOTE",
    ),
    "H-CTXREAL2": (
        "docs/results/nano-lm/formal-hctxreal2-ctxreal2.md",
        "PROMOTE",
    ),
    "H-NANOGEN11": (
        "docs/results/nano-lm/formal-hnanogen11-nanogen11.md",
        "DEFER",
    ),
    "BA-REAL-EVAL": (
        "docs/results/nano-lm/wave-ba-real-eval.md",
        "PROMOTE",
    ),
    "BA-REPORT": (
        "docs/results/nano-lm/wave-ba-summary.md",
        "PROMOTE",
    ),
}

BA_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ba-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ba.md",
    "docs/results/nano-lm/ba-freeze.md",
)

BA_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-NANOGEN11",
    "BA-REAL-EVAL",
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
    GIVEN BA public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in BA_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking BA product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_ba_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN BA formals + public closeout + product docs
    WHEN applying BA-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in BA_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (BA public docs missing COMPLETE)"
    for path in BA_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({BA_FREEZE_ID}: {BA_THESIS})"


def render_ba_freeze() -> str:
    lines = [
        "# BA-FREEZE — Wave BA NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §8 BA7 · After **BA-REPORT**  ",
        "> Module: `nano_lm/src/ba_freeze_ops.py` · "
        "Runner: `npm run nano:ba:freeze`  ",
        "> Parent: [az-freeze.md](az-freeze.md) · "
        "[wave-ba-summary.md](wave-ba-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave BA outcomes locked; "
        "H-REALGAIN·H-FASTREAL·H-CTXREAL2 PROMOTE stays; "
        "H-NANOGEN11 **DEFER** "
        "(gen stance defer · CAPCHECK closed · NANOGEN6·7 HOLD · "
        "NANOGEN8·9·10 DEFER cited · not NANOGEN10 rename) locked; "
        "BA-REAL-EVAL battery 10/10 PROMOTE locked; ≤5M hard stays; "
        f"ship claim remains **{SHIP_CLAIM}**; **no Wave BB** "
        "without explicit lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-REALGAIN | **PROMOTE** | forever FH 0 · AZ hold 0 · "
        "over-refuse 0 · live FP 0 · no bank stuffing |",
        "| H-FASTREAL | **PROMOTE** | prod p50/p99 · anti-FP hold · "
        "≠ AG `nano:fastreal` archive |",
        "| H-CTXREAL2 | **PROMOTE** | howto·cite·long content_ok · "
        "anti-FP hold · L_eff alone ≠ win |",
        "| H-NANOGEN11 | **DEFER** | stance defer · CAPCHECK closed · "
        "NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER cited · not NANOGEN10+rename |",
        "| BA-REAL-EVAL | **PROMOTE** | live battery 10/10 · "
        "forever ABSTAIN · over-refuse LOOKUP · gen locked |",
        "| BA-REPORT | **PROMOTE** | [summary](wave-ba-summary.md) · "
        "[paper-lab](paper-lab-wave-ba.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave BB** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / unlabeled open chat  ",
        "- Forever intent LOOKUP sold as success  ",
        "- Over-refuse exact gold sold as safe win  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell PEAK / bank-grounded / span-fallback as GPT-class / "
        "true-continue unlock  ",
        "- Sell SAFE mean as answer quality  ",
        "- Sell NANOGEN11 DEFER / NANOGEN8·9·10 DEFER / NANOGEN6·7 HOLD "
        "as gen unlock / mini-AGI  ",
        "- NANOGEN11 = NANOGEN10+rename / truncate-to-span as gen IQ  ",
        "- Bank stuffing BA-FOREVER  ",
        "- CTX/SMART/FAST/APP letter clones without named product hole  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "- Rewrite AZ/AY/AX/AW/AV/AU/AT/AS/AR/AQ/AP locked outcomes  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:ba:freeze",
        "# optional: --skip-ask",
        "npm run nano:ba:report",
        "npm run nano:az:freeze",
        "```",
        "",
        "BA forever/modes smoke must keep LOOKUP · forever ABSTAIN · "
        "over-refuse LOOKUP · OOD ABSTAIN honest.  ",
        "Artifact: `results/nano-lm/wave-ba/ba_freeze.json` · "
        "Contract: `nano_lm/tests/test_ba_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
