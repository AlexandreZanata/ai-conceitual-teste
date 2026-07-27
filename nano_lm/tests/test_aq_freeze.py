"""Contract: Wave AQ-FREEZE (post-report lock; no Wave AR invent)."""

from __future__ import annotations

from aq_freeze_ops import (
    AQ_DECISIONS,
    AQ_FREEZE_ID,
    AQ_PUBLIC,
    AQ_THESIS,
    decide_aq_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_aq_freeze,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AQ9 AQ-FREEZE
    assert AQ_FREEZE_ID == "AQ-FREEZE"
    assert "no Wave AR" in AQ_THESIS
    assert "HOLD" in AQ_THESIS
    assert len(AQ_DECISIONS) >= 8
    assert "COMPLETE" in render_aq_freeze()
    assert "FROZEN" in render_aq_freeze()
    assert "H-PARAHIT" in AQ_DECISIONS
    assert "H-NANOGEN" in AQ_DECISIONS
    assert AQ_DECISIONS["H-NANOGEN"][1] == "HOLD"
    assert AQ_DECISIONS["AQ-PRODUCT-HITL"][1] == "PROMOTE"
    assert AQ_DECISIONS["H-MODEUI"][1] == "PROMOTE"
    assert AQ_DECISIONS["AQ-REPORT"][1] == "PROMOTE"


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-PARAHIT\n" for p in AQ_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AQ_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_parahit_promote_when_formal_then_ok() -> None:
    path, want = AQ_DECISIONS["H-PARAHIT"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave AQ COMPLETE. Product H-PARAHIT AQ-PRODUCT-HITL held."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-PARAHIT only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AQ_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AQ-FREEZE H-PARAHIT AQ-PRODUCT-HITL FROZEN"
        for p in AQ_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-PARAHIT AQ-PRODUCT-HITL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-PARAHIT AQ-PRODUCT-HITL"
        ),
    }
    out = decide_aq_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AQ_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AQ_DECISIONS.items()
    }
    miss = AQ_DECISIONS["H-MODEUI"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-PARAHIT AQ-PRODUCT-HITL" for p in AQ_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-PARAHIT AQ-PRODUCT-HITL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-PARAHIT AQ-PRODUCT-HITL"
        ),
    }
    out = decide_aq_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-MODEUI" in out or miss in out
