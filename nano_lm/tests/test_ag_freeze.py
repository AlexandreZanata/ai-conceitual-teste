"""Contract: Wave AG-FREEZE (post-report lock; no Wave AH invent)."""

from __future__ import annotations

from ag_freeze_ops import (
    AG_DECISIONS,
    AG_FREEZE_ID,
    AG_PUBLIC,
    AG_THESIS,
    decide_ag_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_ag_freeze,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AG8 AG-FREEZE
    assert AG_FREEZE_ID == "AG-FREEZE"
    assert "no Wave AH" in AG_THESIS
    assert len(AG_DECISIONS) >= 7
    assert "COMPLETE" in render_ag_freeze()
    assert "H-ANTIFP" in AG_DECISIONS
    assert "H-APPREAL" in AG_DECISIONS
    assert AG_DECISIONS["H-SMARTREAL"][1] == "HOLD"
    assert AG_DECISIONS["AG-HITL-10"][1] == "HOLD"


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-ANTIFP\n" for p in AG_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AG_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_antifp_promote_when_formal_then_ok() -> None:
    path, want = AG_DECISIONS["H-ANTIFP"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave AG COMPLETE. Product H-ANTIFP AG-HITL-10 held-out."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-ANTIFP only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AG_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AG-FREEZE H-ANTIFP AG-HITL-10 FROZEN" for p in AG_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-ANTIFP AG-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-ANTIFP AG-HITL-10"
        ),
    }
    out = decide_ag_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AG_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AG_DECISIONS.items()
    }
    miss = AG_DECISIONS["H-APPREAL"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-ANTIFP AG-HITL-10" for p in AG_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-ANTIFP AG-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-ANTIFP AG-HITL-10"
        ),
    }
    out = decide_ag_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-APPREAL" in out or miss in out
