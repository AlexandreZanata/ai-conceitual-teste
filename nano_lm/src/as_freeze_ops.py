"""Wave AS-FREEZE: lock AS outcomes; no Wave AT without lab-book reopen."""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "AS_FREEZE_ID",
    "AS_THESIS",
    "AS_DECISIONS",
    "AS_PUBLIC",
    "AS_PRODUCT_DOCS",
    "PRODUCT_MARKERS",
    "SHIP_CLAIM",
    "decide_as_freeze",
    "formal_decision_ok",
    "public_docs_ok",
    "product_markers_ok",
    "render_as_freeze",
]

AS_FREEZE_ID = "AS-FREEZE"
SHIP_CLAIM = (
    "AF packaged stack + AQ product layer — not open chat LM"
)
AS_THESIS = (
    "Wave AS frozen: ASKABSTAIN·SEMFIX·ADVSAFE·PARAEXT2·METRICS·SHIPUI·"
    "DUAL-HITL·REPORT PROMOTE; NANOGEN3 HOLD (ablated 4.3 · peak_only); "
    "≤5M stays; ship claim " + SHIP_CLAIM + "; no Wave AT without reopen"
)

# Formal / closeout path → required decision token.
AS_DECISIONS: dict[str, tuple[str, str]] = {
    "H-ASKABSTAIN": (
        "docs/results/nano-lm/formal-haskabstain-askabstain.md",
        "PROMOTE",
    ),
    "H-SEMFIX": (
        "docs/results/nano-lm/formal-hsemfix-semfix.md",
        "PROMOTE",
    ),
    "H-ADVSAFE": (
        "docs/results/nano-lm/formal-hadvsafe-advsafe.md",
        "PROMOTE",
    ),
    "H-PARAEXT2": (
        "docs/results/nano-lm/formal-hparaext2-paraext2.md",
        "PROMOTE",
    ),
    "H-METRICS": (
        "docs/results/nano-lm/formal-hmetrics-metrics.md",
        "PROMOTE",
    ),
    "H-SHIPUI": (
        "docs/results/nano-lm/formal-hshipui-shipui.md",
        "PROMOTE",
    ),
    "H-NANOGEN3": (
        "docs/results/nano-lm/formal-hnanogen3-nanogen3.md",
        "HOLD",
    ),
    "AS-DUAL-HITL": (
        "docs/results/nano-lm/wave-as-dual-hitl.md",
        "PROMOTE",
    ),
    "AS-REPORT": (
        "docs/results/nano-lm/wave-as-summary.md",
        "PROMOTE",
    ),
}

AS_PUBLIC: tuple[str, ...] = (
    "docs/results/nano-lm/wave-as-summary.md",
    "docs/results/nano-lm/paper-lab-wave-as.md",
    "docs/results/nano-lm/as-freeze.md",
)

AS_PRODUCT_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

PRODUCT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-ASKABSTAIN",
    "AS-DUAL-HITL",
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
    GIVEN AS public closeout bodies
    WHEN checking freeze
    THEN True iff each required doc has COMPLETE.
    """
    for path in AS_PUBLIC:
        if "COMPLETE" not in str(texts.get(path, "")):
            return False
    return True


def product_markers_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN RECIPES/card bodies
    WHEN checking AS product freeze
    THEN True iff every product doc contains all PRODUCT_MARKERS.
    """
    for _path, body in texts.items():
        text = str(body)
        if not all(m in text for m in PRODUCT_MARKERS):
            return False
    return bool(texts)


def decide_as_freeze(
    *,
    formal_texts: Mapping[str, str],
    public_texts: Mapping[str, str],
    product_texts: Mapping[str, str],
) -> str:
    """
    GIVEN AS formals + public closeout + product docs
    WHEN applying AS-FREEZE
    THEN PROMOTE iff decisions + COMPLETE + product markers hold.
    """
    for hid, (path, want) in AS_DECISIONS.items():
        body = str(formal_texts.get(path, ""))
        if not formal_decision_ok(path, body, want):
            return f"KILL (formal {hid} missing {want})"
    if not public_docs_ok(public_texts):
        return "KILL (AS public docs missing COMPLETE)"
    for path in AS_PRODUCT_DOCS:
        if path not in product_texts:
            return f"KILL (missing product doc: {path})"
    if not product_markers_ok(product_texts):
        return "KILL (product pages missing freeze markers)"
    return f"PROMOTE ({AS_FREEZE_ID}: {AS_THESIS})"


def render_as_freeze() -> str:
    lines = [
        "# AS-FREEZE — Wave AS NO-REOPEN (**DONE** — PROMOTE)",
        "",
        "> Lab: `.local/pesquisa.md` §5 AS10 · After **AS-REPORT**  ",
        "> Module: `nano_lm/src/as_freeze_ops.py` · "
        "Runner: `npm run nano:as:freeze`  ",
        "> Parent: [ar-freeze.md](ar-freeze.md) · "
        "[wave-as-summary.md](wave-as-summary.md)",
        "",
        "## Decision",
        "",
        "**PROMOTE** — Wave AS outcomes locked; product trust "
        "ASKABSTAIN·SEMFIX·ADVSAFE·PARAEXT2·METRICS·SHIPUI PROMOTE stays; "
        "H-NANOGEN3 ablated HOLD locked; AS-DUAL-HITL product PROMOTE with "
        "gen locked; ≤5M hard stays; ship claim remains "
        f"**{SHIP_CLAIM}**; **no Wave AT** without explicit "
        "lab-book reopen.",
        "",
        "**Status: COMPLETE + FROZEN** (freeze gate).",
        "",
        "## Locked outcomes",
        "",
        "| ID | Decision | Must stay |",
        "|----|----------|-----------|",
        "| H-ASKABSTAIN | **PROMOTE** | default-ask OOD abstain · FH 0 |",
        "| H-SEMFIX | **PROMOTE** | ADVREG-01/05 class FH 0 |",
        "| H-ADVSAFE | **PROMOTE** | false-hit 0/20 · SAFE≠quality |",
        "| H-PARAEXT2 | **PROMOTE** | hit 0.80 · FH 0 |",
        "| H-METRICS | **PROMOTE** | tetrad p50/p99 + KB holes |",
        "| H-SHIPUI | **PROMOTE** | LOOKUP·PEAK·DECODE·ABSTAIN |",
        "| H-NANOGEN3 | **HOLD** | ablated gen 4.3 · peak_only |",
        "| AS-DUAL-HITL | **PROMOTE** | product pass · gen locked |",
        "| AS-REPORT | **PROMOTE** | [summary](wave-as-summary.md) · "
        "[paper-lab](paper-lab-wave-as.md) |",
        "",
        "## Forbidden without reopen",
        "",
        "- Invent **Wave AT** letter-pack / new H-IDs  ",
        "- Claim LOOKUP scores = generative IQ / open chat LM  ",
        "- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · "
        "naive CTX · ZPREF · KVCACHE-Q  ",
        "- Sell PEAK / bank-grounded as open-chat / mini-AGI unlocked  ",
        "- Sell SAFE mean as answer quality  ",
        "- Sell product PROMOTE as generative unlock while "
        "H-NANOGEN3 HOLD  ",
        "- CTX/SMART/FAST/APP letter clones without named product hole  ",
        "- Raise param cap without named CAPCHECK-style reopen  ",
        "",
        "## Validate",
        "",
        "```bash",
        "npm run nano:as:freeze",
        "# optional: --skip-ask",
        "npm run nano:as:report",
        "npm run nano:ar:freeze",
        "```",
        "",
        "Four-mode smoke must keep LOOKUP · PEAK · DECODE · ABSTAIN "
        "visible.  ",
        "Artifact: `results/nano-lm/wave-as/as_freeze.json` · "
        "Contract: `nano_lm/tests/test_as_freeze.py`.",
        "",
    ]
    return "\n".join(lines)
