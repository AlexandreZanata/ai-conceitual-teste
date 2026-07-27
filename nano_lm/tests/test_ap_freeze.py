"""Contract: Wave AP-FREEZE (post-report lock; no Wave AQ invent)."""

from __future__ import annotations

from ap_freeze_ops import (
    AP_DECISIONS,
    AP_FREEZE_ID,
    AP_PUBLIC,
    AP_THESIS,
    decide_ap_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_ap_freeze,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AP8 AP-FREEZE
    assert AP_FREEZE_ID == "AP-FREEZE"
    assert "no Wave AQ" in AP_THESIS
    assert len(AP_DECISIONS) >= 7
    assert "COMPLETE" in render_ap_freeze()
    assert "H-CTXBASE" in AP_DECISIONS
    assert "H-APPBASE" in AP_DECISIONS
    assert "H-GENBASE" in AP_DECISIONS
    assert AP_DECISIONS["H-GENBASE"][1] == "HOLD"
    assert AP_DECISIONS["AP-HITL-10"][1] == "PROMOTE"
    assert AP_DECISIONS["H-CTXBASE"][1] == "PROMOTE"
    assert AP_DECISIONS["H-FASTBASE"][1] == "PROMOTE"


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-CTXBASE\n" for p in AP_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AP_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_ctxbase_promote_when_formal_then_ok() -> None:
    path, want = AP_DECISIONS["H-CTXBASE"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave AP COMPLETE. Product H-CTXBASE AP-HITL-10 held-out."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-CTXBASE only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AP_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AP-FREEZE H-CTXBASE AP-HITL-10 FROZEN" for p in AP_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXBASE AP-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-CTXBASE AP-HITL-10"
        ),
    }
    out = decide_ap_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AP_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AP_DECISIONS.items()
    }
    miss = AP_DECISIONS["H-APPBASE"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-CTXBASE AP-HITL-10" for p in AP_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-CTXBASE AP-HITL-10",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-CTXBASE AP-HITL-10"
        ),
    }
    out = decide_ap_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-APPBASE" in out or miss in out
