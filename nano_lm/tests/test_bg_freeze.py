"""Contract: Wave BG-FREEZE (post-report lock; no Wave BH invent)."""

from __future__ import annotations

from bg_freeze_ops import (
    BG_DECISIONS,
    BG_FREEZE_ID,
    BG_PUBLIC,
    BG_THESIS,
    decide_bg_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_bg_freeze,
)


def test_given_contract_when_constants_then_match_bg8_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BG8 BG-FREEZE
    assert BG_FREEZE_ID == "BG-FREEZE"
    assert "no Wave BH" in BG_THESIS
    assert "NANOGEN17" in BG_THESIS
    assert "SKIP" in BG_THESIS
    assert "UNARYINT" in BG_THESIS
    assert "SHIPPUB" in BG_THESIS
    assert "NANOGEN16" in BG_THESIS or "NANOGEN6" in BG_THESIS
    assert len(BG_DECISIONS) >= 7
    assert "COMPLETE" in render_bg_freeze()
    assert "FROZEN" in render_bg_freeze()
    assert "H-UNARYINT" in BG_DECISIONS
    assert "H-SHIPPUB" in BG_DECISIONS
    assert "H-NANOGEN17" in BG_DECISIONS
    assert BG_DECISIONS["H-NANOGEN17"][1] == "SKIP"
    assert BG_DECISIONS["BG-REAL-EVAL"][1] == "PROMOTE"
    assert BG_DECISIONS["BG-REPORT"][1] == "PROMOTE"
    assert BG_DECISIONS["H-FASTBG"][1] == "PROMOTE"
    assert BG_DECISIONS["H-CTXBG"][1] == "PROMOTE"
    assert "formal-hfastbg-fastbg.md" in BG_DECISIONS["H-FASTBG"][0]


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-NANOGEN17\n" for p in BG_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in BG_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_unaryint_promote_when_formal_then_ok() -> None:
    path, want = BG_DECISIONS["H-UNARYINT"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_nanogen17_skip_when_formal_then_ok() -> None:
    path, want = BG_DECISIONS["H-NANOGEN17"]
    assert formal_decision_ok(path, f"# x\n**DONE** — {want}\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave BG COMPLETE. Product H-NANOGEN17 BG-REAL-EVAL held."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-NANOGEN17 only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in BG_DECISIONS.items()
    }
    public = {
        p: "COMPLETE BG-FREEZE H-NANOGEN17 BG-REAL-EVAL FROZEN"
        for p in BG_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN17 BG-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN17 BG-REAL-EVAL"
        ),
    }
    out = decide_bg_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert BG_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in BG_DECISIONS.items()
    }
    miss = BG_DECISIONS["H-CTXBG"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-NANOGEN17 BG-REAL-EVAL" for p in BG_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN17 BG-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN17 BG-REAL-EVAL"
        ),
    }
    out = decide_bg_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-CTXBG" in out or miss in out
