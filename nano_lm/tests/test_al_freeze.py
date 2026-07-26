"""Contract: Wave AL-FREEZE (post-report lock; no Wave AM invent)."""

from __future__ import annotations

from al_freeze_ops import (
    AL_DECISIONS,
    AL_FREEZE_ID,
    AL_PUBLIC,
    AL_THESIS,
    decide_al_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_al_freeze,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AL8 AL-FREEZE
    assert AL_FREEZE_ID == "AL-FREEZE"
    assert "no Wave AM" in AL_THESIS
    assert len(AL_DECISIONS) >= 7
    assert "COMPLETE" in render_al_freeze()
    assert "H-CTXFRESH" in AL_DECISIONS
    assert "H-APPFRESH" in AL_DECISIONS
    assert "H-GENFRESH" in AL_DECISIONS
    assert AL_DECISIONS["H-GENFRESH"][1] == "HOLD"
    assert AL_DECISIONS["AL-HITL-10"][1] == "PROMOTE"
    assert AL_DECISIONS["H-CTXFRESH"][1] == "PROMOTE"
    assert AL_DECISIONS["H-FASTFRESH"][1] == "PROMOTE"


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-CTXFRESH\n" for p in AL_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AL_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_ctxfresh_promote_when_formal_then_ok() -> None:
    path, want = AL_DECISIONS["H-CTXFRESH"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave AL COMPLETE. Product H-CTXFRESH AL-HITL-10 held-out."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-CTXFRESH only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AL_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AL-FREEZE H-CTXFRESH AL-HITL-10 FROZEN" for p in AL_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXFRESH AL-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-CTXFRESH AL-HITL-10"
        ),
    }
    out = decide_al_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AL_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AL_DECISIONS.items()
    }
    miss = AL_DECISIONS["H-APPFRESH"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-CTXFRESH AL-HITL-10" for p in AL_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXFRESH AL-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-CTXFRESH AL-HITL-10"
        ),
    }
    out = decide_al_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-APPFRESH" in out or miss in out
