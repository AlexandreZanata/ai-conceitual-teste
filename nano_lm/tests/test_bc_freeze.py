"""Contract: Wave BC-FREEZE (post-report lock; no Wave BD invent)."""

from __future__ import annotations

from bc_freeze_ops import (
    BC_DECISIONS,
    BC_FREEZE_ID,
    BC_PUBLIC,
    BC_THESIS,
    decide_bc_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_bc_freeze,
)


def test_given_contract_when_constants_then_match_bc7_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BC7 BC-FREEZE
    assert BC_FREEZE_ID == "BC-FREEZE"
    assert "no Wave BD" in BC_THESIS
    assert "NANOGEN13" in BC_THESIS
    assert "DEFER" in BC_THESIS
    assert "OPSFAM" in BC_THESIS
    assert "NANOGEN12" in BC_THESIS or "NANOGEN6" in BC_THESIS
    assert len(BC_DECISIONS) >= 6
    assert "COMPLETE" in render_bc_freeze()
    assert "FROZEN" in render_bc_freeze()
    assert "H-OPSFAM" in BC_DECISIONS
    assert "H-NANOGEN13" in BC_DECISIONS
    assert BC_DECISIONS["H-NANOGEN13"][1] == "DEFER"
    assert BC_DECISIONS["BC-REAL-EVAL"][1] == "PROMOTE"
    assert BC_DECISIONS["BC-REPORT"][1] == "PROMOTE"
    assert BC_DECISIONS["H-FASTLIFT"][1] == "PROMOTE"
    assert BC_DECISIONS["H-CTXLIFT2"][1] == "PROMOTE"
    assert "formal-hfastlift-bc2.md" in BC_DECISIONS["H-FASTLIFT"][0]


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-NANOGEN13\n" for p in BC_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in BC_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_opsfam_promote_when_formal_then_ok() -> None:
    path, want = BC_DECISIONS["H-OPSFAM"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_nanogen13_defer_when_formal_then_ok() -> None:
    path, want = BC_DECISIONS["H-NANOGEN13"]
    assert formal_decision_ok(path, f"# x\n**DONE** — {want}\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave BC COMPLETE. Product H-NANOGEN13 BC-REAL-EVAL held."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-NANOGEN13 only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in BC_DECISIONS.items()
    }
    public = {
        p: "COMPLETE BC-FREEZE H-NANOGEN13 BC-REAL-EVAL FROZEN"
        for p in BC_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN13 BC-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN13 BC-REAL-EVAL"
        ),
    }
    out = decide_bc_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert BC_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in BC_DECISIONS.items()
    }
    miss = BC_DECISIONS["H-CTXLIFT2"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-NANOGEN13 BC-REAL-EVAL" for p in BC_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN13 BC-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN13 BC-REAL-EVAL"
        ),
    }
    out = decide_bc_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-CTXLIFT2" in out or miss in out
