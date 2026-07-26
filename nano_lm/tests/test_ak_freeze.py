"""Contract: Wave AK-FREEZE (post-report lock; no Wave AL invent)."""

from __future__ import annotations

from ak_freeze_ops import (
    AK_DECISIONS,
    AK_FREEZE_ID,
    AK_PUBLIC,
    AK_THESIS,
    decide_ak_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_ak_freeze,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AK8 AK-FREEZE
    assert AK_FREEZE_ID == "AK-FREEZE"
    assert "no Wave AL" in AK_THESIS
    assert len(AK_DECISIONS) >= 7
    assert "COMPLETE" in render_ak_freeze()
    assert "H-CTXMORE" in AK_DECISIONS
    assert "H-APPMORE" in AK_DECISIONS
    assert "H-GENTRUE" in AK_DECISIONS
    assert AK_DECISIONS["H-GENTRUE"][1] == "HOLD"
    assert AK_DECISIONS["AK-HITL-10"][1] == "PROMOTE"
    assert AK_DECISIONS["H-CTXMORE"][1] == "PROMOTE"
    assert AK_DECISIONS["H-FASTMORE"][1] == "PROMOTE"


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-CTXMORE\n" for p in AK_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AK_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_ctxmore_promote_when_formal_then_ok() -> None:
    path, want = AK_DECISIONS["H-CTXMORE"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave AK COMPLETE. Product H-CTXMORE AK-HITL-10 held-out."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-CTXMORE only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AK_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AK-FREEZE H-CTXMORE AK-HITL-10 FROZEN" for p in AK_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXMORE AK-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-CTXMORE AK-HITL-10"
        ),
    }
    out = decide_ak_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AK_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AK_DECISIONS.items()
    }
    miss = AK_DECISIONS["H-APPMORE"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-CTXMORE AK-HITL-10" for p in AK_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXMORE AK-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-CTXMORE AK-HITL-10"
        ),
    }
    out = decide_ak_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-APPMORE" in out or miss in out
