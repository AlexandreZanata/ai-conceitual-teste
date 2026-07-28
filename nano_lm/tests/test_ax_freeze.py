"""Contract: Wave AX-FREEZE (post-report lock; no Wave AY invent)."""

from __future__ import annotations

from ax_freeze_ops import (
    AX_DECISIONS,
    AX_FREEZE_ID,
    AX_PUBLIC,
    AX_THESIS,
    decide_ax_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_ax_freeze,
)


def test_given_contract_when_constants_then_match_ax6_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AX6 AX-FREEZE
    assert AX_FREEZE_ID == "AX-FREEZE"
    assert "no Wave AY" in AX_THESIS
    assert "NANOGEN8" in AX_THESIS
    assert "DEFER" in AX_THESIS
    assert "NANOGEN6" in AX_THESIS or "NANOGEN7" in AX_THESIS
    assert len(AX_DECISIONS) >= 5
    assert "COMPLETE" in render_ax_freeze()
    assert "FROZEN" in render_ax_freeze()
    assert "H-PRODNAT" in AX_DECISIONS
    assert "H-NANOGEN8" in AX_DECISIONS
    assert AX_DECISIONS["H-NANOGEN8"][1] == "DEFER"
    assert AX_DECISIONS["AX-REAL-EVAL"][1] == "PROMOTE"
    assert AX_DECISIONS["AX-REPORT"][1] == "PROMOTE"
    assert AX_DECISIONS["H-SHIPUX"][1] == "PROMOTE"


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-NANOGEN8\n" for p in AX_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AX_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_prodnat_promote_when_formal_then_ok() -> None:
    path, want = AX_DECISIONS["H-PRODNAT"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_nanogen8_defer_when_formal_then_ok() -> None:
    path, want = AX_DECISIONS["H-NANOGEN8"]
    assert formal_decision_ok(path, f"# x\n**DONE** — {want}\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave AX COMPLETE. Product H-NANOGEN8 AX-REAL-EVAL held."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-NANOGEN8 only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AX_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AX-FREEZE H-NANOGEN8 AX-REAL-EVAL FROZEN"
        for p in AX_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN8 AX-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN8 AX-REAL-EVAL"
        ),
    }
    out = decide_ax_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AX_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AX_DECISIONS.items()
    }
    miss = AX_DECISIONS["H-SHIPUX"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-NANOGEN8 AX-REAL-EVAL" for p in AX_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN8 AX-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN8 AX-REAL-EVAL"
        ),
    }
    out = decide_ax_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-SHIPUX" in out or miss in out
