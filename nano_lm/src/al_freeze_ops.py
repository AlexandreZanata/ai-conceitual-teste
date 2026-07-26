"""Wave AL-FREEZE: lock AL outcomes; no Wave AM without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "AL_FREEZE_ID",
    "AL_THESIS",
    "AL_DECISIONS",
    "AL_PUBLIC",
    "AL_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "decide_al_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_al_freeze",
]

AL_FREEZE_ID = "AL-FREEZE"
AL_THESIS = (
    "Wave AL frozen: GENFRESH HOLD · CTXFRESH·SMARTFRESH·FASTFRESH·"
    "APPFRESH·AL-HITL PROMOTE; CAPCHECK skipped; gen≥5 via GENFRESH peak; "
    "≤5M stays; ship claim remains AF packaged stack; "
    "no Wave AM without reopen"
)

# Formal / closeout path → required decision token.
AL_DECISIONS: dict[str, tuple[str, str]] = {
    "H-GENFRESH": (
        "docs/results/nano-lm/formal-hgenfresh-genfresh.md",
        "HOLD",
    ),
    "H-CTXFRESH": (
        "docs/results/nano-lm/formal-hctxfresh-ctxfresh.md",
        "PROMOTE",
    ),
    "H-SMARTFRESH": (
        "docs/results/nano-lm/formal-hsmartfresh-smartfresh.md",
        "PROMOTE",
    ),
    "H-FASTFRESH": (
        "docs/results/nano-lm/formal-hfastfresh-fastfresh.md",
        "PROMOTE",
    ),
    "H-APPFRESH": (
        "docs/results/nano-lm/formal-happfresh-appfresh.md",
        "PROMOTE",
    ),
    "AL-HITL-10": (
        "docs/results/nano-lm/wave-al-hitl.md",
        "PROMOTE",
    ),
    "AL-REPORT": (
        "docs/results/nano-lm/wave-al-summary.md",
        "PROMOTE",
    ),
}

AL_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-al-summary.md",
    "docs/results/nano-lm/paper-lab-wave-al.md",
    "docs/results/nano-lm/al-freeze.md",
)

AL_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-CTXFRESH",
    "AL-HITL-10",
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
    GIVEN AL public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AL_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AL product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_al_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AL formals + public closeout + product docs
    WHEN applying AL-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AL_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AL public docs missing COMPLETE)"
    for path in AL_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AL_FREEZE_ID}: {AL_THESIS})"


def render_al_freeze() -> str:
    lines = [
        "# AL-FREEZE — Wave AL NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §3 AL8 · After **AL-REPORT**  ",
        "> Module: `nano_lm/src/al_freeze_ops.py` · "
        "Runner: `npm run nano:al:freeze`  ",
        "> Parent: [ak-freeze.md](ak-freeze.md) · "
        "[wave-al-summary.md](wave-al-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AL outcomes locked; fresh dual-arm "
        "PROMOTE stack stays; GENFRESH ablated HOLD locked; "
        "gen≥5 via grounded extractive peak "
        "(not open chat); ≤5M hard stays; ship claim remains "
        "**AF packaged stack**; **no Wave AM** without explicit "
        "lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-GENFRESH | **HOLD** | ablated gen 4.0; peak_only_lift |",
        "| H-CAPCHECK | **SKIPPED** | keep ≤5M without size reopen |",
        "| H-CTXFRESH | **PROMOTE** | nona-doc L_eff 200344 |",
        "| H-SMARTFRESH | **PROMOTE** | nona-hop cite; gen 9.0 |",
        "| H-FASTFRESH | **PROMOTE** | cue-first peak-fast hot ~0.2 |",
        "| H-APPFRESH | **PROMOTE** | dual-arm apps + DEPL-AL |",
        "| AL-HITL-10 | **PROMOTE** | final L=9.0 G=9.0; ship=AF |",
        "| AL-REPORT | **PROMOTE** | [summary](wave-al-summary.md) · "
        "[paper-lab](paper-lab-wave-al.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AM** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / open chat LM  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell CTXFRESH periods / LOOKUP hits as smarter open chat  ",
        "- Sell GENFRESH extractive peak as open-chat IQ  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:al:freeze",
        "# optional: --skip-ask",
        "npm run nano:al:report",
        "npm run nano:ak:freeze",
        "```",
        "",
        "Dual-arm smoke must keep LOOKUP + GENERATE (`wall_ms>0`) "
        "on AL0 known-ask.  ",
        "Artifact: `results/nano-lm/wave-al/al_freeze.json` · "
        "Contract: `nano_lm/tests/test_al_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
