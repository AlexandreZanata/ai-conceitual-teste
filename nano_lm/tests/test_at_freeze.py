"""Contract: Wave AT-FREEZE (post-report lock; no Wave AU invent)."""

from __future__ import annotations

from at_freeze_ops import (
    AT_DECISIONS,
    AT_FREEZE_ID,
    AT_PUBLIC,
    AT_THESIS,
    decide_at_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_at_freeze,
)


def test_given_contract_when_constants_then_match_at6_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AT6 AT-FREEZE
    assert AT_FREEZE_ID == "AT-FREEZE"
    assert "no Wave AU" in AT_THESIS
    assert "NANOGEN4" in AT_THESIS
    assert "5.5" in AT_THESIS
    assert len(AT_DECISIONS) >= 5
    assert "COMPLETE" in render_at_freeze()
    assert "FROZEN" in render_at_freeze()
    assert "H-PRODREG" in AT_DECISIONS
    assert "H-NANOGEN4" in AT_DECISIONS
    assert AT_DECISIONS["H-NANOGEN4"][1] == "PROMOTE"
    assert AT_DECISIONS["AT-REAL-EVAL"][1] == "PROMOTE"
    assert AT_DECISIONS["AT-REPORT"][1] == "PROMOTE"


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-NANOGEN4\n" for p in AT_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AT_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_prodreg_promote_when_formal_then_ok() -> None:
    path, want = AT_DECISIONS["H-PRODREG"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave AT COMPLETE. Product H-NANOGEN4 AT-REAL-EVAL held."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-NANOGEN4 only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AT_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AT-FREEZE H-NANOGEN4 AT-REAL-EVAL FROZEN"
        for p in AT_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN4 AT-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN4 AT-REAL-EVAL"
        ),
    }
    out = decide_at_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AT_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AT_DECISIONS.items()
    }
    miss = AT_DECISIONS["H-SHIPAPP"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-NANOGEN4 AT-REAL-EVAL" for p in AT_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN4 AT-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN4 AT-REAL-EVAL"
        ),
    }
    out = decide_at_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-SHIPAPP" in out or miss in out
