"""Wave AB-FREEZE: lock AB outcomes; no Wave AC without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "AB_FREEZE_ID",
    "AB_THESIS",
    "AB_DECISIONS",
    "AB_PUBLIC",
    "AB_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "decide_ab_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_ab_freeze",
]

AB_FREEZE_ID = "AB-FREEZE"
AB_THESIS = (
    "Wave AB frozen: scoped apps on H-ZWRAP+H-WRAPBANK+AB stack; "
    "no Wave AC without reopen"
)

# Formal / closeout path → required decision token.
AB_DECISIONS: dict[str, tuple[str, str]] = {
    "H-SEMWRAP": (
        "docs/results/nano-lm/formal-hsemwrap-semwrap.md",
        "PROMOTE",
    ),
    "H-ASKFAST": (
        "docs/results/nano-lm/formal-haskfast-askfast.md",
        "PROMOTE",
    ),
    "H-LONGAPP": (
        "docs/results/nano-lm/formal-hlongapp-longapp.md",
        "PROMOTE",
    ),
    "H-ASKSMART": (
        "docs/results/nano-lm/formal-hasksmart-asksmart.md",
        "PROMOTE",
    ),
    "H-REALAPP": (
        "docs/results/nano-lm/formal-hrealapp-realapp.md",
        "PROMOTE",
    ),
    "AB-HITL-10": (
        "docs/results/nano-lm/wave-ab-hitl.md",
        "PROMOTE",
    ),
    "AB-REPORT": (
        "docs/results/nano-lm/wave-ab-summary.md",
        "PROMOTE",
    ),
}

AB_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ab-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ab.md",
    "docs/results/nano-lm/ab-freeze.md",
)

AB_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-ZWRAP",
    "H-WRAPBANK",
    "H-SEMWRAP",
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
    GIVEN AB public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AB_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AB product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_ab_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AB formals + public closeout + product one-pagers
    WHEN applying AB-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AB_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AB public docs missing COMPLETE)"
    for path in AB_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AB_FREEZE_ID}: {AB_THESIS})"


def render_ab_freeze() -> str:
    lines = [
        "# AB-FREEZE — Wave AB NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §8.4 · After **AB-REPORT**  ",
        "> Module: `nano_lm/src/ab_freeze_ops.py` · Runner: `npm run nano:ab:freeze`  ",
        "> Parent: [lab-freeze.md](lab-freeze.md) · [aa-freeze.md](aa-freeze.md) · "
        "[wave-ab-summary.md](wave-ab-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AB outcomes locked; scoped product remains "
        "**H-ZWRAP + H-WRAPBANK + AB stack** (SEMWRAP · ASKFAST · LONGAPP · "
        "ASKSMART · REALAPP); **no Wave AC** without explicit lab-book reopen.",
        "",
        "**Status: COMPLETE** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-SEMWRAP | **PROMOTE** | fuzzy near-known ask |",
        "| H-ASKFAST | **PROMOTE** | fast ask path |",
        "| H-LONGAPP | **PROMOTE** | curated L_eff≫W |",
        "| H-ASKSMART | **PROMOTE** | constrained decode > SERVEALIGN |",
        "| H-REALAPP | **PROMOTE** | app-known + app-longdoc |",
        "| AB-HITL-10 | **PROMOTE** | final mean 9.0 |",
        "| AB-REPORT | **PROMOTE** | [summary](wave-ab-summary.md) · "
        "[paper-lab](paper-lab-wave-ab.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AC** letter-pack / new H-IDs  ",
        "- Claim AB stack / SERVEALIGN / ZERR = unbounded open chat LM  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF  ",
        "- Rewrite PARA HOLD / SERVEALIGN HOLD into silent “solved”  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:ab:freeze",
        "# optional: --skip-ask",
        "npm run nano:ab:report",
        "npm run nano:lab-freeze",
        "```",
        "",
        "ASKFAST/SEMWRAP smoke must keep a scoped hit on known-ask.  ",
        "Artifact: `results/nano-lm/wave-ab/ab_freeze.json` · "
        "Contract: `nano_lm/tests/test_ab_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
