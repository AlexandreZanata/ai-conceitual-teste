"""Contract: Wave AH-FREEZE (post-report lock; no Wave AI invent)."""

from __future__ import annotations

from ah_freeze_ops import (
    AH_DECISIONS,
    AH_FREEZE_ID,
    AH_PUBLIC,
    AH_THESIS,
    decide_ah_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_ah_freeze,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AH8 AH-FREEZE
    assert AH_FREEZE_ID == "AH-FREEZE"
    assert "no Wave AI" in AH_THESIS
    assert len(AH_DECISIONS) >= 7
    assert "COMPLETE" in render_ah_freeze()
    assert "H-CTXLIFT" in AH_DECISIONS
    assert "H-APPLIFT" in AH_DECISIONS
    assert AH_DECISIONS["H-GENLIFT"][1] == "HOLD"
    assert AH_DECISIONS["AH-HITL-10"][1] == "HOLD"
    assert AH_DECISIONS["H-CTXLIFT"][1] == "PROMOTE"


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-CTXLIFT\n" for p in AH_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AH_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_ctxlift_promote_when_formal_then_ok() -> None:
    path, want = AH_DECISIONS["H-CTXLIFT"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave AH COMPLETE. Product H-CTXLIFT AH-HITL-10 held-out."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-CTXLIFT only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AH_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AH-FREEZE H-CTXLIFT AH-HITL-10 FROZEN" for p in AH_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXLIFT AH-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-CTXLIFT AH-HITL-10"
        ),
    }
    out = decide_ah_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AH_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AH_DECISIONS.items()
    }
    miss = AH_DECISIONS["H-APPLIFT"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-CTXLIFT AH-HITL-10" for p in AH_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXLIFT AH-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-CTXLIFT AH-HITL-10"
        ),
    }
    out = decide_ah_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-APPLIFT" in out or miss in out
