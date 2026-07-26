"""Contract: Wave AD-FREEZE (post-report lock; no Wave AE invent)."""

from __future__ import annotations

from ad_freeze_ops import (
    AD_DECISIONS,
    AD_FREEZE_ID,
    AD_PUBLIC,
    AD_THESIS,
    decide_ad_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_ad_freeze,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8.6 / §13 AD7 AD-FREEZE
    assert AD_FREEZE_ID == "AD-FREEZE"
    assert "no Wave AE" in AD_THESIS
    assert len(AD_DECISIONS) >= 6
    assert "COMPLETE" in render_ad_freeze()
    assert "H-COMPOSE" in AD_DECISIONS


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-HARDPARA\n" for p in AD_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AD_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_hardpara_promote_when_formal_then_ok() -> None:
    path, want = AD_DECISIONS["H-HARDPARA"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave AD COMPLETE. Product H-HARDPARA AD-HITL-10 held-out."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-HARDPARA only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AD_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AD-FREEZE H-HARDPARA AD-HITL-10 FROZEN" for p in AD_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-HARDPARA AD-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-HARDPARA AD-HITL-10"
        ),
    }
    out = decide_ad_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AD_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AD_DECISIONS.items()
    }
    miss = AD_DECISIONS["H-ROUTEPLUS"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-HARDPARA AD-HITL-10" for p in AD_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-HARDPARA AD-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-HARDPARA AD-HITL-10"
        ),
    }
    out = decide_ad_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-ROUTEPLUS" in out or miss in out
