"""Contract: Wave BD-FREEZE (post-report lock; no Wave BE invent)."""

from __future__ import annotations

from bd_freeze_ops import (
    BD_DECISIONS,
    BD_FREEZE_ID,
    BD_PUBLIC,
    BD_THESIS,
    decide_bd_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_bd_freeze,
)


def test_given_contract_when_constants_then_match_bd7_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BD7 BD-FREEZE
    assert BD_FREEZE_ID == "BD-FREEZE"
    assert "no Wave BE" in BD_THESIS
    assert "NANOGEN14" in BD_THESIS
    assert "DEFER" in BD_THESIS
    assert "SEMINT" in BD_THESIS
    assert "NANOGEN13" in BD_THESIS or "NANOGEN6" in BD_THESIS
    assert len(BD_DECISIONS) >= 6
    assert "COMPLETE" in render_bd_freeze()
    assert "FROZEN" in render_bd_freeze()
    assert "H-SEMINT" in BD_DECISIONS
    assert "H-NANOGEN14" in BD_DECISIONS
    assert BD_DECISIONS["H-NANOGEN14"][1] == "DEFER"
    assert BD_DECISIONS["BD-REAL-EVAL"][1] == "PROMOTE"
    assert BD_DECISIONS["BD-REPORT"][1] == "PROMOTE"
    assert BD_DECISIONS["H-FASTGAIN"][1] == "PROMOTE"
    assert BD_DECISIONS["H-CTXGAIN"][1] == "PROMOTE"
    assert "formal-hfastgain-fastgain.md" in BD_DECISIONS["H-FASTGAIN"][0]


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-NANOGEN14\n" for p in BD_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in BD_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_semint_promote_when_formal_then_ok() -> None:
    path, want = BD_DECISIONS["H-SEMINT"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_nanogen14_defer_when_formal_then_ok() -> None:
    path, want = BD_DECISIONS["H-NANOGEN14"]
    assert formal_decision_ok(path, f"# x\n**DONE** — {want}\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave BD COMPLETE. Product H-NANOGEN14 BD-REAL-EVAL held."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-NANOGEN14 only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in BD_DECISIONS.items()
    }
    public = {
        p: "COMPLETE BD-FREEZE H-NANOGEN14 BD-REAL-EVAL FROZEN"
        for p in BD_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN14 BD-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN14 BD-REAL-EVAL"
        ),
    }
    out = decide_bd_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert BD_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in BD_DECISIONS.items()
    }
    miss = BD_DECISIONS["H-CTXGAIN"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-NANOGEN14 BD-REAL-EVAL" for p in BD_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN14 BD-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN14 BD-REAL-EVAL"
        ),
    }
    out = decide_bd_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-CTXGAIN" in out or miss in out
