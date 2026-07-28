"""Contract: Wave AY-FREEZE (post-report lock; no Wave AZ invent)."""

from __future__ import annotations

from ay_freeze_ops import (
    AY_DECISIONS,
    AY_FREEZE_ID,
    AY_PUBLIC,
    AY_THESIS,
    decide_ay_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_ay_freeze,
)


def test_given_contract_when_constants_then_match_ay6_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AY6 AY-FREEZE
    assert AY_FREEZE_ID == "AY-FREEZE"
    assert "no Wave AZ" in AY_THESIS
    assert "NANOGEN9" in AY_THESIS
    assert "DEFER" in AY_THESIS
    assert "NANOGEN8" in AY_THESIS or "NANOGEN6" in AY_THESIS
    assert len(AY_DECISIONS) >= 5
    assert "COMPLETE" in render_ay_freeze()
    assert "FROZEN" in render_ay_freeze()
    assert "H-PRODINT" in AY_DECISIONS
    assert "H-NANOGEN9" in AY_DECISIONS
    assert AY_DECISIONS["H-NANOGEN9"][1] == "DEFER"
    assert AY_DECISIONS["AY-REAL-EVAL"][1] == "PROMOTE"
    assert AY_DECISIONS["AY-REPORT"][1] == "PROMOTE"
    assert AY_DECISIONS["H-SHIPAY"][1] == "PROMOTE"


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-NANOGEN9\n" for p in AY_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AY_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_prodint_promote_when_formal_then_ok() -> None:
    path, want = AY_DECISIONS["H-PRODINT"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_nanogen9_defer_when_formal_then_ok() -> None:
    path, want = AY_DECISIONS["H-NANOGEN9"]
    assert formal_decision_ok(path, f"# x\n**DONE** — {want}\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave AY COMPLETE. Product H-NANOGEN9 AY-REAL-EVAL held."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-NANOGEN9 only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AY_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AY-FREEZE H-NANOGEN9 AY-REAL-EVAL FROZEN"
        for p in AY_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN9 AY-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN9 AY-REAL-EVAL"
        ),
    }
    out = decide_ay_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AY_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AY_DECISIONS.items()
    }
    miss = AY_DECISIONS["H-SHIPAY"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-NANOGEN9 AY-REAL-EVAL" for p in AY_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN9 AY-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN9 AY-REAL-EVAL"
        ),
    }
    out = decide_ay_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-SHIPAY" in out or miss in out
