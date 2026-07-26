"""Wave AC-FREEZE: lock AC outcomes; no Wave AD without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "AC_FREEZE_ID",
    "AC_THESIS",
    "AC_DECISIONS",
    "AC_PUBLIC",
    "AC_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "decide_ac_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_ac_freeze",
]

AC_FREEZE_ID = "AC-FREEZE"
AC_THESIS = (
    "Wave AC frozen: scoped packaged apps on AB spine + "
    "CTXPLUS/SMARTPLUS/FASTPLUS/APPPLUS; no Wave AD without reopen"
)

# Formal / closeout path → required decision token.
AC_DECISIONS: dict[str, tuple[str, str]] = {
    "H-CTXPLUS": (
        "docs/results/nano-lm/formal-hctxplus-ctxplus.md",
        "PROMOTE",
    ),
    "H-SMARTPLUS": (
        "docs/results/nano-lm/formal-hsmartplus-smartplus.md",
        "PROMOTE",
    ),
    "H-FASTPLUS": (
        "docs/results/nano-lm/formal-hfastplus-fastplus.md",
        "PROMOTE",
    ),
    "H-APPPLUS": (
        "docs/results/nano-lm/formal-happplus-appplus.md",
        "PROMOTE",
    ),
    "AC-HITL-10": (
        "docs/results/nano-lm/wave-ac-hitl.md",
        "PROMOTE",
    ),
    "AC-REPORT": (
        "docs/results/nano-lm/wave-ac-summary.md",
        "PROMOTE",
    ),
}

AC_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ac-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ac.md",
    "docs/results/nano-lm/ac-freeze.md",
)

AC_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-CTXPLUS",
    "H-APPPLUS",
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
    GIVEN AC public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AC_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AC product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_ac_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AC formals + public closeout + product one-pagers
    WHEN applying AC-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AC_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AC public docs missing COMPLETE)"
    for path in AC_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AC_FREEZE_ID}: {AC_THESIS})"


def render_ac_freeze() -> str:
    lines = [
        "# AC-FREEZE — Wave AC NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §8.5 AC7 · After **AC-REPORT**  ",
        "> Module: `nano_lm/src/ac_freeze_ops.py` · "
        "Runner: `npm run nano:ac:freeze`  ",
        "> Parent: [ab-freeze.md](ab-freeze.md) · [aa-freeze.md](aa-freeze.md) · "
        "[wave-ac-summary.md](wave-ac-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AC outcomes locked; scoped product remains "
        "**H-ZWRAP + H-WRAPBANK + AB stack + AC stack** (CTXPLUS · SMARTPLUS · "
        "FASTPLUS · APPPLUS / app-known · app-howto · app-longdoc); "
        "**no Wave AD** without explicit lab-book reopen.",
        "",
        "**Status: COMPLETE** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-CTXPLUS | **PROMOTE** | multi-slice L_eff≫AB |",
        "| H-SMARTPLUS | **PROMOTE** | hard paraphrase; false-hit 0 |",
        "| H-FASTPLUS | **PROMOTE** | held-out ask latency ↓ |",
        "| H-APPPLUS | **PROMOTE** | app-howto + known/longdoc |",
        "| AC-HITL-10 | **PROMOTE** | final mean 9.0 |",
        "| AC-REPORT | **PROMOTE** | [summary](wave-ac-summary.md) · "
        "[paper-lab](paper-lab-wave-ac.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AD** letter-pack / new H-IDs  ",
        "- Claim AC/AB stack / SERVEALIGN / ZERR = unbounded open chat LM  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF  ",
        "- Rewrite held-out HITL into silent “open chat solved”  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:ac:freeze",
        "# optional: --skip-ask",
        "npm run nano:ac:report",
        "npm run nano:ab:freeze",
        "```",
        "",
        "ASKFAST/SEMWRAP smoke must keep a scoped hit on known-ask.  ",
        "Artifact: `results/nano-lm/wave-ac/ac_freeze.json` · "
        "Contract: `nano_lm/tests/test_ac_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
