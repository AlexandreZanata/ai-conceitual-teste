"""Contract: Wave AU-FREEZE (post-report lock; no Wave AV invent)."""

from __future__ import annotations

from au_freeze_ops import (
    AU_DECISIONS,
    AU_FREEZE_ID,
    AU_PUBLIC,
    AU_THESIS,
    decide_au_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_au_freeze,
)


def test_given_contract_when_constants_then_match_au6_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AU6 AU-FREEZE
    assert AU_FREEZE_ID == "AU-FREEZE"
    assert "no Wave AV" in AU_THESIS
    assert "NANOGEN5" in AU_THESIS
    assert "5.5" in AU_THESIS
    assert "STRICT" in AU_THESIS or "strict" in AU_THESIS.lower()
    assert len(AU_DECISIONS) >= 5
    assert "COMPLETE" in render_au_freeze()
    assert "FROZEN" in render_au_freeze()
    assert "H-PRODHARD" in AU_DECISIONS
    assert "H-NANOGEN5" in AU_DECISIONS
    assert AU_DECISIONS["H-NANOGEN5"][1] == "PROMOTE"
    assert AU_DECISIONS["AU-REAL-EVAL"][1] == "PROMOTE"
    assert AU_DECISIONS["AU-REPORT"][1] == "PROMOTE"
    assert AU_DECISIONS["H-SHIPREAL"][1] == "PROMOTE"


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-NANOGEN5\n" for p in AU_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AU_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_prodhard_promote_when_formal_then_ok() -> None:
    path, want = AU_DECISIONS["H-PRODHARD"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave AU COMPLETE. Product H-NANOGEN5 AU-REAL-EVAL held."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-NANOGEN5 only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AU_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AU-FREEZE H-NANOGEN5 AU-REAL-EVAL FROZEN"
        for p in AU_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN5 AU-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN5 AU-REAL-EVAL"
        ),
    }
    out = decide_au_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AU_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AU_DECISIONS.items()
    }
    miss = AU_DECISIONS["H-SHIPREAL"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-NANOGEN5 AU-REAL-EVAL" for p in AU_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN5 AU-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN5 AU-REAL-EVAL"
        ),
    }
    out = decide_au_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-SHIPREAL" in out or miss in out
