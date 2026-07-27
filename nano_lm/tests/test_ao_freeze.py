"""Contract: Wave AO-FREEZE (post-report lock; no Wave AP invent)."""

from __future__ import annotations

from ao_freeze_ops import (
    AO_DECISIONS,
    AO_FREEZE_ID,
    AO_PUBLIC,
    AO_THESIS,
    decide_ao_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_ao_freeze,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AO8 AO-FREEZE
    assert AO_FREEZE_ID == "AO-FREEZE"
    assert "no Wave AP" in AO_THESIS
    assert len(AO_DECISIONS) >= 7
    assert "COMPLETE" in render_ao_freeze()
    assert "H-CTXCORE" in AO_DECISIONS
    assert "H-APPCORE" in AO_DECISIONS
    assert "H-GENCORE" in AO_DECISIONS
    assert AO_DECISIONS["H-GENCORE"][1] == "HOLD"
    assert AO_DECISIONS["AO-HITL-10"][1] == "PROMOTE"
    assert AO_DECISIONS["H-CTXCORE"][1] == "PROMOTE"
    assert AO_DECISIONS["H-FASTCORE"][1] == "PROMOTE"


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-CTXCORE\n" for p in AO_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AO_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_ctxcore_promote_when_formal_then_ok() -> None:
    path, want = AO_DECISIONS["H-CTXCORE"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave AO COMPLETE. Product H-CTXCORE AO-HITL-10 held-out."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-CTXCORE only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AO_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AO-FREEZE H-CTXCORE AO-HITL-10 FROZEN" for p in AO_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXCORE AO-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-CTXCORE AO-HITL-10"
        ),
    }
    out = decide_ao_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AO_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AO_DECISIONS.items()
    }
    miss = AO_DECISIONS["H-APPCORE"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-CTXCORE AO-HITL-10" for p in AO_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXCORE AO-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-CTXCORE AO-HITL-10"
        ),
    }
    out = decide_ao_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-APPCORE" in out or miss in out
