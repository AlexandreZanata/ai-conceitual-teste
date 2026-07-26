"""Contract: Wave AC-FREEZE (post-report lock; no Wave AD invent)."""

from __future__ import annotations

from ac_freeze_ops import (
    AC_DECISIONS,
    AC_FREEZE_ID,
    AC_PUBLIC,
    AC_THESIS,
    decide_ac_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_ac_freeze,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8.5 AC7 AC-FREEZE
    assert AC_FREEZE_ID == "AC-FREEZE"
    assert "no Wave AD" in AC_THESIS
    assert len(AC_DECISIONS) >= 6
    assert "COMPLETE" in render_ac_freeze()


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-CTXPLUS\n" for p in AC_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AC_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_ctxplus_promote_when_formal_then_ok() -> None:
    path, want = AC_DECISIONS["H-CTXPLUS"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave AC COMPLETE. Product H-CTXPLUS H-APPPLUS held-out."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-CTXPLUS only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AC_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AC-FREEZE H-CTXPLUS H-APPPLUS FROZEN" for p in AC_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXPLUS H-APPPLUS",
        "docs/results/nano-lm/champion-card.md": "COMPLETE H-CTXPLUS H-APPPLUS",
    }
    out = decide_ac_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AC_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AC_DECISIONS.items()
    }
    miss = AC_DECISIONS["H-FASTPLUS"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-CTXPLUS H-APPPLUS" for p in AC_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXPLUS H-APPPLUS",
        "docs/results/nano-lm/champion-card.md": "COMPLETE H-CTXPLUS H-APPPLUS",
    }
    out = decide_ac_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-FASTPLUS" in out or miss in out
