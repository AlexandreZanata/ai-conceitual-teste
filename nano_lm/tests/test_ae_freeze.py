"""Contract: Wave AE-FREEZE (post-report lock; no Wave AF invent)."""

from __future__ import annotations

from ae_freeze_ops import (
    AE_DECISIONS,
    AE_FREEZE_ID,
    AE_PUBLIC,
    AE_THESIS,
    decide_ae_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_ae_freeze,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AE7 AE-FREEZE
    assert AE_FREEZE_ID == "AE-FREEZE"
    assert "no Wave AF" in AE_THESIS
    assert len(AE_DECISIONS) >= 6
    assert "COMPLETE" in render_ae_freeze()
    assert "H-CTXMAX" in AE_DECISIONS
    assert "H-APPMAX" in AE_DECISIONS


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-CTXMAX\n" for p in AE_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AE_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_ctxmax_promote_when_formal_then_ok() -> None:
    path, want = AE_DECISIONS["H-CTXMAX"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave AE COMPLETE. Product H-CTXMAX AE-HITL-10 held-out."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-CTXMAX only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AE_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AE-FREEZE H-CTXMAX AE-HITL-10 FROZEN" for p in AE_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXMAX AE-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-CTXMAX AE-HITL-10"
        ),
    }
    out = decide_ae_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AE_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AE_DECISIONS.items()
    }
    miss = AE_DECISIONS["H-APPMAX"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-CTXMAX AE-HITL-10" for p in AE_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXMAX AE-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-CTXMAX AE-HITL-10"
        ),
    }
    out = decide_ae_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-APPMAX" in out or miss in out
