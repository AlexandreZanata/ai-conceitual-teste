"""Contract: Wave AW-FREEZE (post-report lock; no Wave AX invent)."""

from __future__ import annotations

from aw_freeze_ops import (
    AW_DECISIONS,
    AW_FREEZE_ID,
    AW_PUBLIC,
    AW_THESIS,
    decide_aw_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_aw_freeze,
)


def test_given_contract_when_constants_then_match_aw6_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §2 AW6 AW-FREEZE
    assert AW_FREEZE_ID == "AW-FREEZE"
    assert "no Wave AX" in AW_THESIS
    assert "NANOGEN7" in AW_THESIS
    assert "HOLD" in AW_THESIS
    assert "TAC" in AW_THESIS or "span-fallback" in AW_THESIS
    assert len(AW_DECISIONS) >= 5
    assert "COMPLETE" in render_aw_freeze()
    assert "FROZEN" in render_aw_freeze()
    assert "H-PRODKEEP" in AW_DECISIONS
    assert "H-NANOGEN7" in AW_DECISIONS
    assert AW_DECISIONS["H-NANOGEN7"][1] == "HOLD"
    assert AW_DECISIONS["AW-REAL-EVAL"][1] == "PROMOTE"
    assert AW_DECISIONS["AW-REPORT"][1] == "PROMOTE"
    assert AW_DECISIONS["H-SHIPKEEP"][1] == "PROMOTE"


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-NANOGEN7\n" for p in AW_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AW_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_prodkeep_promote_when_formal_then_ok() -> None:
    path, want = AW_DECISIONS["H-PRODKEEP"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_nanogen7_hold_when_formal_then_ok() -> None:
    path, want = AW_DECISIONS["H-NANOGEN7"]
    assert formal_decision_ok(path, f"# x\n**DONE** — {want}\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave AW COMPLETE. Product H-NANOGEN7 AW-REAL-EVAL held."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-NANOGEN7 only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AW_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AW-FREEZE H-NANOGEN7 AW-REAL-EVAL FROZEN"
        for p in AW_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN7 AW-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN7 AW-REAL-EVAL"
        ),
    }
    out = decide_aw_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AW_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AW_DECISIONS.items()
    }
    miss = AW_DECISIONS["H-SHIPKEEP"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-NANOGEN7 AW-REAL-EVAL" for p in AW_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN7 AW-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN7 AW-REAL-EVAL"
        ),
    }
    out = decide_aw_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-SHIPKEEP" in out or miss in out
