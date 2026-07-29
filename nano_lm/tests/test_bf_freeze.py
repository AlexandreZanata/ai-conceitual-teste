"""Contract: Wave BF-FREEZE (post-report lock; no Wave BG invent)."""

from __future__ import annotations

from bf_freeze_ops import (
    BF_DECISIONS,
    BF_FREEZE_ID,
    BF_PUBLIC,
    BF_THESIS,
    decide_bf_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_bf_freeze,
)


def test_given_contract_when_constants_then_match_bf8_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BF8 BF-FREEZE
    assert BF_FREEZE_ID == "BF-FREEZE"
    assert "no Wave BG" in BF_THESIS
    assert "NANOGEN16" in BF_THESIS
    assert "SKIP" in BF_THESIS
    assert "PREDINT" in BF_THESIS
    assert "SHIPUSE2" in BF_THESIS
    assert "NANOGEN15" in BF_THESIS or "NANOGEN6" in BF_THESIS
    assert len(BF_DECISIONS) >= 7
    assert "COMPLETE" in render_bf_freeze()
    assert "FROZEN" in render_bf_freeze()
    assert "H-PREDINT" in BF_DECISIONS
    assert "H-SHIPUSE2" in BF_DECISIONS
    assert "H-NANOGEN16" in BF_DECISIONS
    assert BF_DECISIONS["H-NANOGEN16"][1] == "SKIP"
    assert BF_DECISIONS["BF-REAL-EVAL"][1] == "PROMOTE"
    assert BF_DECISIONS["BF-REPORT"][1] == "PROMOTE"
    assert BF_DECISIONS["H-FASTBF"][1] == "PROMOTE"
    assert BF_DECISIONS["H-CTXBF"][1] == "PROMOTE"
    assert "formal-hfastbf-fastbf.md" in BF_DECISIONS["H-FASTBF"][0]


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-NANOGEN16\n" for p in BF_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in BF_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_predint_promote_when_formal_then_ok() -> None:
    path, want = BF_DECISIONS["H-PREDINT"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_nanogen16_skip_when_formal_then_ok() -> None:
    path, want = BF_DECISIONS["H-NANOGEN16"]
    assert formal_decision_ok(path, f"# x\n**DONE** — {want}\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave BF COMPLETE. Product H-NANOGEN16 BF-REAL-EVAL held."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-NANOGEN16 only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in BF_DECISIONS.items()
    }
    public = {
        p: "COMPLETE BF-FREEZE H-NANOGEN16 BF-REAL-EVAL FROZEN"
        for p in BF_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN16 BF-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN16 BF-REAL-EVAL"
        ),
    }
    out = decide_bf_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert BF_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in BF_DECISIONS.items()
    }
    miss = BF_DECISIONS["H-CTXBF"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-NANOGEN16 BF-REAL-EVAL" for p in BF_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN16 BF-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN16 BF-REAL-EVAL"
        ),
    }
    out = decide_bf_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-CTXBF" in out or miss in out
