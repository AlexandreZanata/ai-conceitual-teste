"""Contract: Wave AB-FREEZE (post-report lock; no Wave AC invent)."""

from __future__ import annotations

from ab_freeze_ops import (
    AB_DECISIONS,
    AB_FREEZE_ID,
    AB_PUBLIC,
    AB_THESIS,
    decide_ab_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_ab_freeze,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8.4 AB-FREEZE (AA-FREEZE analog)
    assert AB_FREEZE_ID == "AB-FREEZE"
    assert "no Wave AC" in AB_THESIS
    assert len(AB_DECISIONS) >= 6
    assert "COMPLETE" in render_ab_freeze()


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-ZWRAP\n" for p in AB_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AB_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_semwrap_promote_when_formal_then_ok() -> None:
    path, want = AB_DECISIONS["H-SEMWRAP"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = (
        "Wave AB COMPLETE. Product H-ZWRAP H-WRAPBANK H-SEMWRAP. "
        "Not an open chat LM."
    )
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-ZWRAP only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AB_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AB-FREEZE H-ZWRAP H-WRAPBANK FROZEN" for p in AB_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": (
            "COMPLETE H-ZWRAP H-WRAPBANK H-SEMWRAP"
        ),
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-ZWRAP H-WRAPBANK H-SEMWRAP"
        ),
    }
    out = decide_ab_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AB_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AB_DECISIONS.items()
    }
    miss = AB_DECISIONS["H-ASKFAST"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-ZWRAP H-WRAPBANK" for p in AB_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-ZWRAP H-WRAPBANK H-SEMWRAP",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-ZWRAP H-WRAPBANK H-SEMWRAP"
        ),
    }
    out = decide_ab_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-ASKFAST" in out or miss in out
