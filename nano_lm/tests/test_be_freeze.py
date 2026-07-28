"""Contract: Wave BE-FREEZE (post-report lock; no Wave BF invent)."""

from __future__ import annotations

from be_freeze_ops import (
    BE_DECISIONS,
    BE_FREEZE_ID,
    BE_PUBLIC,
    BE_THESIS,
    decide_be_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_be_freeze,
)


def test_given_contract_when_constants_then_match_be8_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BE8 BE-FREEZE
    assert BE_FREEZE_ID == "BE-FREEZE"
    assert "no Wave BF" in BE_THESIS
    assert "NANOGEN15" in BE_THESIS
    assert "DEFER" in BE_THESIS
    assert "COMPINT" in BE_THESIS
    assert "SHIPUSE" in BE_THESIS
    assert "NANOGEN14" in BE_THESIS or "NANOGEN6" in BE_THESIS
    assert len(BE_DECISIONS) >= 7
    assert "COMPLETE" in render_be_freeze()
    assert "FROZEN" in render_be_freeze()
    assert "H-COMPINT" in BE_DECISIONS
    assert "H-SHIPUSE" in BE_DECISIONS
    assert "H-NANOGEN15" in BE_DECISIONS
    assert BE_DECISIONS["H-NANOGEN15"][1] == "DEFER"
    assert BE_DECISIONS["BE-REAL-EVAL"][1] == "PROMOTE"
    assert BE_DECISIONS["BE-REPORT"][1] == "PROMOTE"
    assert BE_DECISIONS["H-FASTBE"][1] == "PROMOTE"
    assert BE_DECISIONS["H-CTXBE"][1] == "PROMOTE"
    assert "formal-hfastbe-fastbe.md" in BE_DECISIONS["H-FASTBE"][0]


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-NANOGEN15\n" for p in BE_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in BE_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_compint_promote_when_formal_then_ok() -> None:
    path, want = BE_DECISIONS["H-COMPINT"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_nanogen15_defer_when_formal_then_ok() -> None:
    path, want = BE_DECISIONS["H-NANOGEN15"]
    assert formal_decision_ok(path, f"# x\n**DONE** — {want}\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave BE COMPLETE. Product H-NANOGEN15 BE-REAL-EVAL held."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-NANOGEN15 only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in BE_DECISIONS.items()
    }
    public = {
        p: "COMPLETE BE-FREEZE H-NANOGEN15 BE-REAL-EVAL FROZEN"
        for p in BE_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN15 BE-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN15 BE-REAL-EVAL"
        ),
    }
    out = decide_be_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert BE_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in BE_DECISIONS.items()
    }
    miss = BE_DECISIONS["H-CTXBE"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-NANOGEN15 BE-REAL-EVAL" for p in BE_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN15 BE-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN15 BE-REAL-EVAL"
        ),
    }
    out = decide_be_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-CTXBE" in out or miss in out
