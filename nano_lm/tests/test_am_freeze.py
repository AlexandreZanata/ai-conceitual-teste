"""Contract: Wave AM-FREEZE (post-report lock; no Wave AN invent)."""

from __future__ import annotations

from am_freeze_ops import (
    AM_DECISIONS,
    AM_FREEZE_ID,
    AM_PUBLIC,
    AM_THESIS,
    decide_am_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_am_freeze,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AM8 AM-FREEZE
    assert AM_FREEZE_ID == "AM-FREEZE"
    assert "no Wave AN" in AM_THESIS
    assert len(AM_DECISIONS) >= 7
    assert "COMPLETE" in render_am_freeze()
    assert "H-CTXNEXT" in AM_DECISIONS
    assert "H-APPNEXT" in AM_DECISIONS
    assert "H-GENTRUTH" in AM_DECISIONS
    assert AM_DECISIONS["H-GENTRUTH"][1] == "HOLD"
    assert AM_DECISIONS["AM-HITL-10"][1] == "PROMOTE"
    assert AM_DECISIONS["H-CTXNEXT"][1] == "PROMOTE"
    assert AM_DECISIONS["H-FASTNEXT"][1] == "PROMOTE"


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-CTXNEXT\n" for p in AM_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AM_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_ctxnext_promote_when_formal_then_ok() -> None:
    path, want = AM_DECISIONS["H-CTXNEXT"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave AM COMPLETE. Product H-CTXNEXT AM-HITL-10 held-out."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-CTXNEXT only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AM_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AM-FREEZE H-CTXNEXT AM-HITL-10 FROZEN" for p in AM_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXNEXT AM-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-CTXNEXT AM-HITL-10"
        ),
    }
    out = decide_am_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AM_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AM_DECISIONS.items()
    }
    miss = AM_DECISIONS["H-APPNEXT"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-CTXNEXT AM-HITL-10" for p in AM_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXNEXT AM-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-CTXNEXT AM-HITL-10"
        ),
    }
    out = decide_am_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-APPNEXT" in out or miss in out
