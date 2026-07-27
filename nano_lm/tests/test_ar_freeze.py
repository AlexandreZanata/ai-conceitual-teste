"""Contract: Wave AR-FREEZE (post-report lock; no Wave AS invent)."""

from __future__ import annotations

from ar_freeze_ops import (
    AR_DECISIONS,
    AR_FREEZE_ID,
    AR_PUBLIC,
    AR_THESIS,
    decide_ar_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_ar_freeze,
)


def test_given_contract_when_constants_then_match_ar8_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AR8 AR-FREEZE
    assert AR_FREEZE_ID == "AR-FREEZE"
    assert "no Wave AS" in AR_THESIS
    assert "HOLD" in AR_THESIS
    assert "KILL" in AR_THESIS
    assert len(AR_DECISIONS) >= 7
    assert "COMPLETE" in render_ar_freeze()
    assert "FROZEN" in render_ar_freeze()
    assert "H-ABSTAIN" in AR_DECISIONS
    assert "H-NANOGEN2" in AR_DECISIONS
    assert AR_DECISIONS["H-NANOGEN2"][1] == "HOLD"
    assert AR_DECISIONS["H-ADVREG"][1] == "KILL"
    assert AR_DECISIONS["AR-DUAL-HITL"][1] == "HOLD"
    assert AR_DECISIONS["AR-REPORT"][1] == "PROMOTE"


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-ABSTAIN\n" for p in AR_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AR_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_abstain_promote_when_formal_then_ok() -> None:
    path, want = AR_DECISIONS["H-ABSTAIN"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave AR COMPLETE. Product H-ABSTAIN AR-DUAL-HITL held."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-ABSTAIN only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AR_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AR-FREEZE H-ABSTAIN AR-DUAL-HITL FROZEN"
        for p in AR_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-ABSTAIN AR-DUAL-HITL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-ABSTAIN AR-DUAL-HITL"
        ),
    }
    out = decide_ar_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AR_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AR_DECISIONS.items()
    }
    miss = AR_DECISIONS["H-SHIPDEMO"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-ABSTAIN AR-DUAL-HITL" for p in AR_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-ABSTAIN AR-DUAL-HITL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-ABSTAIN AR-DUAL-HITL"
        ),
    }
    out = decide_ar_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-SHIPDEMO" in out or miss in out
