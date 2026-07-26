"""Wave AF-FREEZE: lock AF outcomes; no Wave AG without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "AF_FREEZE_ID",
    "AF_THESIS",
    "AF_DECISIONS",
    "AF_PUBLIC",
    "AF_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "decide_af_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_af_freeze",
]

AF_FREEZE_ID = "AF-FREEZE"
AF_THESIS = (
    "Wave AF frozen: scoped packaged stack "
    "CTXULTRA+SMARTULTRA+FASTULTRA+APPULTRA; no Wave AG without reopen"
)

# Formal / closeout path → required decision token.
AF_DECISIONS: dict[str, tuple[str, str]] = {
    "H-CTXULTRA": (
        "docs/results/nano-lm/formal-hctxultra-ctxultra.md",
        "PROMOTE",
    ),
    "H-SMARTULTRA": (
        "docs/results/nano-lm/formal-hsmartultra-smartultra.md",
        "PROMOTE",
    ),
    "H-FASTULTRA": (
        "docs/results/nano-lm/formal-hfastultra-fastultra.md",
        "PROMOTE",
    ),
    "H-APPULTRA": (
        "docs/results/nano-lm/formal-happultra-appultra.md",
        "PROMOTE",
    ),
    "AF-HITL-10": (
        "docs/results/nano-lm/wave-af-hitl.md",
        "PROMOTE",
    ),
    "AF-REPORT": (
        "docs/results/nano-lm/wave-af-summary.md",
        "PROMOTE",
    ),
}

AF_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-af-summary.md",
    "docs/results/nano-lm/paper-lab-wave-af.md",
    "docs/results/nano-lm/af-freeze.md",
)

AF_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-CTXULTRA",
    "AF-HITL-10",
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
    GIVEN AF public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AF_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AF product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_af_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AF formals + public closeout + product docs
    WHEN applying AF-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AF_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AF public docs missing COMPLETE)"
    for path in AF_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AF_FREEZE_ID}: {AF_THESIS})"


def render_af_freeze() -> str:
    lines = [
        "# AF-FREEZE — Wave AF NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §5 AF7 · After **AF-REPORT**  ",
        "> Module: `nano_lm/src/af_freeze_ops.py` · "
        "Runner: `npm run nano:af:freeze`  ",
        "> Parent: [ae-freeze.md](ae-freeze.md) · "
        "[wave-af-summary.md](wave-af-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AF outcomes locked; scoped product remains "
        "**AF packaged stack** (CTXULTRA · SMARTULTRA · FASTULTRA · APPULTRA); "
        "**no Wave AG** without explicit lab-book reopen.",
        "",
        "**Status: COMPLETE** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-CTXULTRA | **PROMOTE** | triple-doc L_eff↑ vs CTXMAX |",
        "| H-SMARTULTRA | **PROMOTE** | triple-hop cite; false-hit 0 |",
        "| H-FASTULTRA | **PROMOTE** | hot e2e ≪ FASTMAX |",
        "| H-APPULTRA | **PROMOTE** | howto↑ + compose 5th + DEPL-AF |",
        "| AF-HITL-10 | **PROMOTE** | final mean 9.0 |",
        "| AF-REPORT | **PROMOTE** | [summary](wave-af-summary.md) · "
        "[paper-lab](paper-lab-wave-af.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AG** letter-pack / new H-IDs  ",
        "- Claim AF/AE stack / SERVEALIGN / ZERR = unbounded open chat LM  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Rewrite held-out HITL into silent “open chat solved”  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:af:freeze",
        "# optional: --skip-ask",
        "npm run nano:af:report",
        "npm run nano:ae:freeze",
        "```",
        "",
        "ASKFAST/SEMWRAP smoke must keep a scoped hit on held-out known-ask.  ",
        "Artifact: `results/nano-lm/wave-af/af_freeze.json` · "
        "Contract: `nano_lm/tests/test_af_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
