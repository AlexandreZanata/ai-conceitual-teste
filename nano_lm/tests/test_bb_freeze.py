"""Contract: Wave BB-FREEZE (post-report lock; no Wave BC invent)."""

from __future__ import annotations

from bb_freeze_ops import (
    BB_DECISIONS,
    BB_FREEZE_ID,
    BB_PUBLIC,
    BB_THESIS,
    decide_bb_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_bb_freeze,
)


def test_given_contract_when_constants_then_match_bb7_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8 BB7 BB-FREEZE
    assert BB_FREEZE_ID == "BB-FREEZE"
    assert "no Wave BC" in BB_THESIS
    assert "NANOGEN12" in BB_THESIS
    assert "DEFER" in BB_THESIS
    assert "INTENTGEN" in BB_THESIS
    assert "NANOGEN11" in BB_THESIS or "NANOGEN6" in BB_THESIS
    assert len(BB_DECISIONS) >= 6
    assert "COMPLETE" in render_bb_freeze()
    assert "FROZEN" in render_bb_freeze()
    assert "H-INTENTGEN" in BB_DECISIONS
    assert "H-NANOGEN12" in BB_DECISIONS
    assert BB_DECISIONS["H-NANOGEN12"][1] == "DEFER"
    assert BB_DECISIONS["BB-REAL-EVAL"][1] == "PROMOTE"
    assert BB_DECISIONS["BB-REPORT"][1] == "PROMOTE"
    assert BB_DECISIONS["H-FASTHOLD"][1] == "PROMOTE"
    assert BB_DECISIONS["H-CTXHOLD"][1] == "PROMOTE"


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-NANOGEN12\n" for p in BB_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in BB_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_intentgen_promote_when_formal_then_ok() -> None:
    path, want = BB_DECISIONS["H-INTENTGEN"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_nanogen12_defer_when_formal_then_ok() -> None:
    path, want = BB_DECISIONS["H-NANOGEN12"]
    assert formal_decision_ok(path, f"# x\n**DONE** — {want}\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave BB COMPLETE. Product H-NANOGEN12 BB-REAL-EVAL held."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-NANOGEN12 only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in BB_DECISIONS.items()
    }
    public = {
        p: "COMPLETE BB-FREEZE H-NANOGEN12 BB-REAL-EVAL FROZEN"
        for p in BB_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN12 BB-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN12 BB-REAL-EVAL"
        ),
    }
    out = decide_bb_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert BB_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in BB_DECISIONS.items()
    }
    miss = BB_DECISIONS["H-CTXHOLD"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-NANOGEN12 BB-REAL-EVAL" for p in BB_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN12 BB-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN12 BB-REAL-EVAL"
        ),
    }
    out = decide_bb_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-CTXHOLD" in out or miss in out
