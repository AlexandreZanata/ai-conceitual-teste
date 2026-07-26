"""Contract: Wave AF-FREEZE (post-report lock; no Wave AG invent)."""

from __future__ import annotations

from af_freeze_ops import (
    AF_DECISIONS,
    AF_FREEZE_ID,
    AF_PUBLIC,
    AF_THESIS,
    decide_af_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_af_freeze,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AF7 AF-FREEZE
    assert AF_FREEZE_ID == "AF-FREEZE"
    assert "no Wave AG" in AF_THESIS
    assert len(AF_DECISIONS) >= 6
    assert "COMPLETE" in render_af_freeze()
    assert "H-CTXULTRA" in AF_DECISIONS
    assert "H-APPULTRA" in AF_DECISIONS


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-CTXULTRA\n" for p in AF_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AF_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_ctxultra_promote_when_formal_then_ok() -> None:
    path, want = AF_DECISIONS["H-CTXULTRA"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave AF COMPLETE. Product H-CTXULTRA AF-HITL-10 held-out."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-CTXULTRA only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AF_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AF-FREEZE H-CTXULTRA AF-HITL-10 FROZEN" for p in AF_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXULTRA AF-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-CTXULTRA AF-HITL-10"
        ),
    }
    out = decide_af_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AF_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AF_DECISIONS.items()
    }
    miss = AF_DECISIONS["H-APPULTRA"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-CTXULTRA AF-HITL-10" for p in AF_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXULTRA AF-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-CTXULTRA AF-HITL-10"
        ),
    }
    out = decide_af_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-APPULTRA" in out or miss in out
