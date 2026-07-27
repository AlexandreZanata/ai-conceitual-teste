"""Contract: Wave AV-FREEZE (post-report lock; no Wave AW invent)."""

from __future__ import annotations

from av_freeze_ops import (
    AV_DECISIONS,
    AV_FREEZE_ID,
    AV_PUBLIC,
    AV_THESIS,
    decide_av_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_av_freeze,
)


def test_given_contract_when_constants_then_match_av6_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AV6 AV-FREEZE
    assert AV_FREEZE_ID == "AV-FREEZE"
    assert "no Wave AW" in AV_THESIS
    assert "NANOGEN6" in AV_THESIS
    assert "HOLD" in AV_THESIS
    assert "span-fallback" in AV_THESIS or "span" in AV_THESIS
    assert len(AV_DECISIONS) >= 5
    assert "COMPLETE" in render_av_freeze()
    assert "FROZEN" in render_av_freeze()
    assert "H-PRODSHIP" in AV_DECISIONS
    assert "H-NANOGEN6" in AV_DECISIONS
    assert AV_DECISIONS["H-NANOGEN6"][1] == "HOLD"
    assert AV_DECISIONS["AV-REAL-EVAL"][1] == "PROMOTE"
    assert AV_DECISIONS["AV-REPORT"][1] == "PROMOTE"
    assert AV_DECISIONS["H-SHIPUI2"][1] == "PROMOTE"


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-NANOGEN6\n" for p in AV_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AV_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_prodship_promote_when_formal_then_ok() -> None:
    path, want = AV_DECISIONS["H-PRODSHIP"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_nanogen6_hold_when_formal_then_ok() -> None:
    path, want = AV_DECISIONS["H-NANOGEN6"]
    assert formal_decision_ok(path, f"# x\n**DONE** — {want}\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave AV COMPLETE. Product H-NANOGEN6 AV-REAL-EVAL held."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-NANOGEN6 only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AV_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AV-FREEZE H-NANOGEN6 AV-REAL-EVAL FROZEN"
        for p in AV_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN6 AV-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN6 AV-REAL-EVAL"
        ),
    }
    out = decide_av_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AV_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AV_DECISIONS.items()
    }
    miss = AV_DECISIONS["H-SHIPUI2"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-NANOGEN6 AV-REAL-EVAL" for p in AV_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-NANOGEN6 AV-REAL-EVAL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-NANOGEN6 AV-REAL-EVAL"
        ),
    }
    out = decide_av_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-SHIPUI2" in out or miss in out
