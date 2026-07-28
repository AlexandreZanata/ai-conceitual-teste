"""Contract: Wave BA-FREEZE (post-report lock; no Wave BB invent)."""

from __future__ import annotations

from ba_freeze_ops import (
    BA_DECISIONS,
    BA_FREEZE_ID,
    BA_PUBLIC,
    BA_THESIS,
    decide_ba_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_ba_freeze,
)


def test_given_contract_when_constants_then_match_ba7_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8 BA7 BA-FREEZE
    assert BA_FREEZE_ID == "BA-FREEZE"
    assert "no Wave BB" in BA_THESIS
    assert "NANOGEN11" in BA_THESIS
    assert "DEFER" in BA_THESIS
    assert "REALGAIN" in BA_THESIS
    assert "NANOGEN10" in BA_THESIS or "NANOGEN6" in BA_THESIS
    assert len(BA_DECISIONS) >= 6
    assert "COMPLETE" in render_ba_freeze()
    assert "FROZEN" in render_ba_freeze()
    assert "H-REALGAIN" in BA_DECISIONS
    assert "H-NANOGEN11" in BA_DECISIONS
    assert BA_DECISIONS["H-NANOGEN11"][1] == "DEFER"
    assert BA_DECISIONS["BA-REAL-EVAL"][1] == "PROMOTE"
    assert BA_DECISIONS["BA-REPORT"][1] == "PROMOTE"
    assert BA_DECISIONS["H-FASTREAL"][1] == "PROMOTE"
    assert BA_DECISIONS["H-CTXREAL2"][1] == "PROMOTE"


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-NANOGEN11\n" for p in BA_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in BA_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_realgain_promote_when_formal_then_ok() -> None:
    path, want = BA_DECISIONS["H-REALGAIN"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_nanogen11_defer_when_formal_then_ok() -> None:
    path, want = BA_DECISIONS["H-NANOGEN11"]
    assert formal_decision_ok(path, f"# x\n**DONE** — {want}\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave BA COMPLETE. Product H-NANOGEN11 BA-REAL-EVAL held."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-NANOGEN11 only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in BA_DECISIONS.items()
    }
    public = {
        p: "COMPLETE BA-FREEZE H-NANOGEN11 BA-REAL-EVAL FROZEN"
        for p in BA_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN11 BA-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN11 BA-REAL-EVAL"
        ),
    }
    out = decide_ba_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert BA_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in BA_DECISIONS.items()
    }
    miss = BA_DECISIONS["H-CTXREAL2"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-NANOGEN11 BA-REAL-EVAL" for p in BA_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN11 BA-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN11 BA-REAL-EVAL"
        ),
    }
    out = decide_ba_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-CTXREAL2" in out or miss in out
