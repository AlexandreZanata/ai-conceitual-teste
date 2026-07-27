"""Contract: Wave AN-FREEZE (post-report lock; no Wave AO invent)."""

from __future__ import annotations

from an_freeze_ops import (
    AN_DECISIONS,
    AN_FREEZE_ID,
    AN_PUBLIC,
    AN_THESIS,
    decide_an_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_an_freeze,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AN8 AN-FREEZE
    assert AN_FREEZE_ID == "AN-FREEZE"
    assert "no Wave AO" in AN_THESIS
    assert len(AN_DECISIONS) >= 7
    assert "COMPLETE" in render_an_freeze()
    assert "H-CTXEDGE" in AN_DECISIONS
    assert "H-APPEDGE" in AN_DECISIONS
    assert "H-GENEDGE" in AN_DECISIONS
    assert AN_DECISIONS["H-GENEDGE"][1] == "HOLD"
    assert AN_DECISIONS["AN-HITL-10"][1] == "PROMOTE"
    assert AN_DECISIONS["H-CTXEDGE"][1] == "PROMOTE"
    assert AN_DECISIONS["H-FASTEDGE"][1] == "PROMOTE"


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-CTXEDGE\n" for p in AN_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AN_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_ctxedge_promote_when_formal_then_ok() -> None:
    path, want = AN_DECISIONS["H-CTXEDGE"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave AN COMPLETE. Product H-CTXEDGE AN-HITL-10 held-out."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-CTXEDGE only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AN_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AN-FREEZE H-CTXEDGE AN-HITL-10 FROZEN" for p in AN_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXEDGE AN-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-CTXEDGE AN-HITL-10"
        ),
    }
    out = decide_an_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AN_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AN_DECISIONS.items()
    }
    miss = AN_DECISIONS["H-APPEDGE"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-CTXEDGE AN-HITL-10" for p in AN_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXEDGE AN-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-CTXEDGE AN-HITL-10"
        ),
    }
    out = decide_an_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-APPEDGE" in out or miss in out
