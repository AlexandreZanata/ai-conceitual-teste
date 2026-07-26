"""Contract: Wave AA-FREEZE (post-report lock; no Wave AB invent)."""

from __future__ import annotations

from aa_freeze_ops import (
    AA_DECISIONS,
    AA_FREEZE_ID,
    AA_PUBLIC,
    AA_THESIS,
    decide_aa_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
)


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-ZWRAP\nH-WRAPBANK\n" for p in AA_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AA_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_wrapbank_promote_when_formal_then_ok() -> None:
    path, want = AA_DECISIONS["H-WRAPBANK"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_zpref_promote_when_expect_kill_then_fail() -> None:
    path, want = AA_DECISIONS["H-ZPREF"]
    assert want == "KILL"
    assert formal_decision_ok(path, "**PROMOTE** only", want) is False


def test_given_product_pages_when_markers_then_ok() -> None:
    body = (
        "Wave AA COMPLETE. Known-ask HITL uses H-ZWRAP and H-WRAPBANK. "
        "Not an open chat LM."
    )
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-ZWRAP only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AA_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AA-FREEZE H-ZWRAP H-WRAPBANK FROZEN" for p in AA_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": (
            "COMPLETE H-ZWRAP H-WRAPBANK known-ask"
        ),
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-ZWRAP H-WRAPBANK known-ask"
        ),
    }
    out = decide_aa_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AA_FREEZE_ID in out
    assert "WRAPBANK" in AA_THESIS or "H-ZWRAP" in AA_THESIS


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AA_DECISIONS.items()
    }
    miss = AA_DECISIONS["H-PARA"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-ZWRAP H-WRAPBANK" for p in AA_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-ZWRAP H-WRAPBANK",
        "docs/results/nano-lm/champion-card.md": "COMPLETE H-ZWRAP H-WRAPBANK",
    }
    out = decide_aa_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-PARA" in out or miss in out
