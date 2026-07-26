"""Wave AI-FREEZE: lock AI outcomes; no Wave AJ without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "AI_FREEZE_ID",
    "AI_THESIS",
    "AI_DECISIONS",
    "AI_PUBLIC",
    "AI_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "decide_ai_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_ai_freeze",
]

AI_FREEZE_ID = "AI-FREEZE"
AI_THESIS = (
    "Wave AI frozen: CTXPUSH+FASTPUSH PROMOTE; gen IQ HOLD; "
    "≤5M stays; ship claim remains AF packaged stack; "
    "no Wave AJ without reopen"
)

# Formal / closeout path → required decision token (HOLD allowed).
AI_DECISIONS: dict[str, tuple[str, str]] = {
    "H-GENPLUS": (
        "docs/results/nano-lm/formal-hgenplus-genplus.md",
        "HOLD",
    ),
    "H-CAPRENEG": (
        "docs/results/nano-lm/formal-hcapreneg-capreneg.md",
        "HOLD",
    ),
    "H-CTXPUSH": (
        "docs/results/nano-lm/formal-hctxpush-ctxpush.md",
        "PROMOTE",
    ),
    "H-SMARTPUSH": (
        "docs/results/nano-lm/formal-hsmartpush-smartpush.md",
        "HOLD",
    ),
    "H-FASTPUSH": (
        "docs/results/nano-lm/formal-hfastpush-fastpush.md",
        "PROMOTE",
    ),
    "H-APPPUSH": (
        "docs/results/nano-lm/formal-happpush-apppush.md",
        "HOLD",
    ),
    "AI-HITL-10": (
        "docs/results/nano-lm/wave-ai-hitl.md",
        "HOLD",
    ),
    "AI-REPORT": (
        "docs/results/nano-lm/wave-ai-summary.md",
        "PROMOTE",
    ),
}

AI_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-ai-summary.md",
    "docs/results/nano-lm/paper-lab-wave-ai.md",
    "docs/results/nano-lm/ai-freeze.md",
)

AI_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-CTXPUSH",
    "AI-HITL-10",
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
    GIVEN AI public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AI_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AI product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_ai_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AI formals + public closeout + product docs
    WHEN applying AI-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AI_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AI public docs missing COMPLETE)"
    for path in AI_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AI_FREEZE_ID}: {AI_THESIS})"


def render_ai_freeze() -> str:
    lines = [
        "# AI-FREEZE — Wave AI NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §5 AI8 · After **AI-REPORT**  ",
        "> Module: `nano_lm/src/ai_freeze_ops.py` · "
        "Runner: `npm run nano:ai:freeze`  ",
        "> Parent: [ah-freeze.md](ah-freeze.md) · "
        "[wave-ai-summary.md](wave-ai-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AI outcomes locked; ctx+speed pushes stay; "
        "gen IQ HOLDs stay honest; ≤5M hard stays; ship claim remains "
        "**AF packaged stack**; **no Wave AJ** without explicit "
        "lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-GENPLUS | **HOLD** | grounded QPFB2; gen 4.0 <5 |",
        "| H-CAPRENEG | **HOLD** | CAP-125M probe; keep ≤5M |",
        "| H-CTXPUSH | **PROMOTE** | hexa-doc L_eff 162851 |",
        "| H-SMARTPUSH | **HOLD** | hexa-hop cite; gen ties 4.0 |",
        "| H-FASTPUSH | **PROMOTE** | hot wall↓ vs FASTLIFT |",
        "| H-APPPUSH | **HOLD** | dual-arm apps + DEPL-AI |",
        "| AI-HITL-10 | **HOLD** | final L=9.0 G=4.0; ship=AF |",
        "| AI-REPORT | **PROMOTE** | [summary](wave-ai-summary.md) · "
        "[paper-lab](paper-lab-wave-ai.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AJ** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / open chat LM  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Rewrite dual-arm HOLD into silent “smarter LM solved”  ",
        "- Raise param cap without named CAPRENEG-style reopen  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:ai:freeze",
        "# optional: --skip-ask",
        "npm run nano:ai:report",
        "npm run nano:ah:freeze",
        "```",
        "",
        "Dual-arm smoke must keep LOOKUP + GENERATE (`wall_ms>0`) "
        "on AI0 known-ask.  ",
        "Artifact: `results/nano-lm/wave-ai/ai_freeze.json` · "
        "Contract: `nano_lm/tests/test_ai_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
