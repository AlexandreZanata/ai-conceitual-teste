"""Contract: Wave AI-FREEZE (post-report lock; no Wave AJ invent)."""

from __future__ import annotations

from ai_freeze_ops import (
    AI_DECISIONS,
    AI_FREEZE_ID,
    AI_PUBLIC,
    AI_THESIS,
    decide_ai_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_ai_freeze,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AI8 AI-FREEZE
    assert AI_FREEZE_ID == "AI-FREEZE"
    assert "no Wave AJ" in AI_THESIS
    assert len(AI_DECISIONS) >= 8
    assert "COMPLETE" in render_ai_freeze()
    assert "H-CTXPUSH" in AI_DECISIONS
    assert "H-APPPUSH" in AI_DECISIONS
    assert "H-CAPRENEG" in AI_DECISIONS
    assert AI_DECISIONS["H-GENPLUS"][1] == "HOLD"
    assert AI_DECISIONS["AI-HITL-10"][1] == "HOLD"
    assert AI_DECISIONS["H-CTXPUSH"][1] == "PROMOTE"
    assert AI_DECISIONS["H-FASTPUSH"][1] == "PROMOTE"


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-CTXPUSH\n" for p in AI_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AI_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_ctxpush_promote_when_formal_then_ok() -> None:
    path, want = AI_DECISIONS["H-CTXPUSH"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave AI COMPLETE. Product H-CTXPUSH AI-HITL-10 held-out."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-CTXPUSH only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AI_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AI-FREEZE H-CTXPUSH AI-HITL-10 FROZEN" for p in AI_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXPUSH AI-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-CTXPUSH AI-HITL-10"
        ),
    }
    out = decide_ai_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AI_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AI_DECISIONS.items()
    }
    miss = AI_DECISIONS["H-APPPUSH"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-CTXPUSH AI-HITL-10" for p in AI_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXPUSH AI-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-CTXPUSH AI-HITL-10"
        ),
    }
    out = decide_ai_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-APPPUSH" in out or miss in out
