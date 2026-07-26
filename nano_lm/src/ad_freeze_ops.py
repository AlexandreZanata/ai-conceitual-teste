"""Wave AD-FREEZE: lock AD outcomes; no Wave AE without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "AD_FREEZE_ID",
    "AD_THESIS",
    "AD_DECISIONS",
    "AD_PUBLIC",
    "AD_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "decide_ad_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_ad_freeze",
]

AD_FREEZE_ID = "AD-FREEZE"
AD_THESIS = (
    "Wave AD frozen: scoped packaged stack on AC/APPPLUS + "
    "HARDPARA/COMPOSE/ROUTEPLUS/DEPLPLUS; no Wave AE without reopen"
)

# Formal / closeout path → required decision token.
AD_DECISIONS: dict[str, tuple[str, str]] = {
    "H-HARDPARA": (
        "docs/results/nano-lm/formal-hhardpara-hardpara.md",
        "PROMOTE",
    ),
    "H-COMPOSE": (
        "docs/results/nano-lm/formal-hcompose-compose.md",
        "PROMOTE",
    ),
    "H-ROUTEPLUS": (
        "docs/results/nano-lm/formal-hrouteplus-routeplus.md",
        "PROMOTE",
    ),
    "H-DEPLPLUS": (
        "docs/results/nano-lm/formal-hdeplplus-deplplus.md",
        "PROMOTE",
    ),
    "AD-HITL-10": (
        "docs/results/nano-lm/wave-ad-hitl.md",
        "PROMOTE",
    ),
    "AD-REPORT": (
        "docs/results/nano-lm/wave-ad-summary.md",
        "PROMOTE",
    ),
}

AD_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ad-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ad.md",
    "docs/results/nano-lm/ad-freeze.md",
)

AD_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-HARDPARA",
    "AD-HITL-10",
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
    GIVEN AD public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AD_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AD product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_ad_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AD formals + public closeout + product one-pagers
    WHEN applying AD-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AD_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AD public docs missing COMPLETE)"
    for path in AD_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AD_FREEZE_ID}: {AD_THESIS})"


def render_ad_freeze() -> str:
    lines = [
        "# AD-FREEZE — Wave AD NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §8.6 AD7 · After **AD-REPORT**  ",
        "> Module: `nano_lm/src/ad_freeze_ops.py` · "
        "Runner: `npm run nano:ad:freeze`  ",
        "> Parent: [ac-freeze.md](ac-freeze.md) · [ab-freeze.md](ab-freeze.md) · "
        "[wave-ad-summary.md](wave-ad-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AD outcomes locked; scoped product remains "
        "**AC/APPPLUS + AD stack** (HARDPARA · COMPOSE · ROUTEPLUS · "
        "DEPLPLUS); **no Wave AE** without explicit lab-book reopen.",
        "",
        "**Status: COMPLETE** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-HARDPARA | **PROMOTE** | adversarial para; false-hit 0 |",
        "| H-COMPOSE | **PROMOTE** | multi-source usable 10/10 |",
        "| H-ROUTEPLUS | **PROMOTE** | correct route + honest OOS |",
        "| H-DEPLPLUS | **PROMOTE** | DEPL one-pagers + smoke |",
        "| AD-HITL-10 | **PROMOTE** | final mean 9.0 |",
        "| AD-REPORT | **PROMOTE** | [summary](wave-ad-summary.md) · "
        "[paper-lab](paper-lab-wave-ad.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AE** letter-pack / new H-IDs  ",
        "- Claim AD/AC stack / SERVEALIGN / ZERR = unbounded open chat LM  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF  ",
        "- Rewrite held-out HITL into silent “open chat solved”  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:ad:freeze",
        "# optional: --skip-ask",
        "npm run nano:ad:report",
        "npm run nano:ac:freeze",
        "```",
        "",
        "ASKFAST/SEMWRAP smoke must keep a scoped hit on held-out known-ask.  ",
        "Artifact: `results/nano-lm/wave-ad/ad_freeze.json` · "
        "Contract: `nano_lm/tests/test_ad_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
