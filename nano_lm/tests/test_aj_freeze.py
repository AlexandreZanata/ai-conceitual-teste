"""Contract: Wave AJ-FREEZE (post-report lock; no Wave AK invent)."""

from __future__ import annotations

from aj_freeze_ops import (
    AJ_DECISIONS,
    AJ_FREEZE_ID,
    AJ_PUBLIC,
    AJ_THESIS,
    decide_aj_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_aj_freeze,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AJ8 AJ-FREEZE
    assert AJ_FREEZE_ID == "AJ-FREEZE"
    assert "no Wave AK" in AJ_THESIS
    assert len(AJ_DECISIONS) >= 7
    assert "COMPLETE" in render_aj_freeze()
    assert "H-CTXPEAK" in AJ_DECISIONS
    assert "H-APPPEAK" in AJ_DECISIONS
    assert "H-GENPEAK" in AJ_DECISIONS
    assert AJ_DECISIONS["H-GENPEAK"][1] == "PROMOTE"
    assert AJ_DECISIONS["AJ-HITL-10"][1] == "PROMOTE"
    assert AJ_DECISIONS["H-CTXPEAK"][1] == "PROMOTE"
    assert AJ_DECISIONS["H-FASTPEAK"][1] == "PROMOTE"


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-CTXPEAK\n" for p in AJ_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AJ_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_ctxpeak_promote_when_formal_then_ok() -> None:
    path, want = AJ_DECISIONS["H-CTXPEAK"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave AJ COMPLETE. Product H-CTXPEAK AJ-HITL-10 held-out."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-CTXPEAK only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AJ_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AJ-FREEZE H-CTXPEAK AJ-HITL-10 FROZEN" for p in AJ_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXPEAK AJ-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-CTXPEAK AJ-HITL-10"
        ),
    }
    out = decide_aj_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AJ_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AJ_DECISIONS.items()
    }
    miss = AJ_DECISIONS["H-APPPEAK"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-CTXPEAK AJ-HITL-10" for p in AJ_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXPEAK AJ-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-CTXPEAK AJ-HITL-10"
        ),
    }
    out = decide_aj_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-APPPEAK" in out or miss in out
