"""Contract: Wave AS-FREEZE (post-report lock; no Wave AT invent)."""

from __future__ import annotations

from as_freeze_ops import (
    AS_DECISIONS,
    AS_FREEZE_ID,
    AS_PUBLIC,
    AS_THESIS,
    decide_as_freeze,
    formal_decision_ok,
    product_markers_ok,
    public_docs_ok,
    render_as_freeze,
)


def test_given_contract_when_constants_then_match_as10_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AS10 AS-FREEZE
    assert AS_FREEZE_ID == "AS-FREEZE"
    assert "no Wave AT" in AS_THESIS
    assert "HOLD" in AS_THESIS
    assert "NANOGEN3" in AS_THESIS
    assert len(AS_DECISIONS) >= 9
    assert "COMPLETE" in render_as_freeze()
    assert "FROZEN" in render_as_freeze()
    assert "H-ASKABSTAIN" in AS_DECISIONS
    assert "H-NANOGEN3" in AS_DECISIONS
    assert AS_DECISIONS["H-NANOGEN3"][1] == "HOLD"
    assert AS_DECISIONS["AS-DUAL-HITL"][1] == "PROMOTE"
    assert AS_DECISIONS["AS-REPORT"][1] == "PROMOTE"
    assert AS_DECISIONS["H-ADVSAFE"][1] == "PROMOTE"


def test_given_all_public_when_ok_then_true() -> None:
    texts = {p: "COMPLETE\nH-ASKABSTAIN\n" for p in AS_PUBLIC}
    assert public_docs_ok(texts) is True


def test_given_missing_complete_when_public_then_false() -> None:
    texts = {p: "draft" for p in AS_PUBLIC}
    assert public_docs_ok(texts) is False


def test_given_askabstain_promote_when_formal_then_ok() -> None:
    path, want = AS_DECISIONS["H-ASKABSTAIN"]
    assert formal_decision_ok(path, f"# x\n**{want}**\n", want) is True


def test_given_product_pages_when_markers_then_ok() -> None:
    body = "Wave AS COMPLETE. Product H-ASKABSTAIN AS-DUAL-HITL held."
    assert product_markers_ok({"a.md": body, "b.md": body}) is True


def test_given_thin_product_when_markers_then_fail() -> None:
    assert product_markers_ok({"a.md": "H-ASKABSTAIN only"}) is False


def test_given_good_freeze_when_decide_then_promote() -> None:
    formals = {
        path: f"Decision **{dec}** for {hid}"
        for hid, (path, dec) in AS_DECISIONS.items()
    }
    public = {
        p: "COMPLETE AS-FREEZE H-ASKABSTAIN AS-DUAL-HITL FROZEN"
        for p in AS_PUBLIC
    }
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-ASKABSTAIN AS-DUAL-HITL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-ASKABSTAIN AS-DUAL-HITL"
        ),
    }
    out = decide_as_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("PROMOTE")
    assert AS_FREEZE_ID in out


def test_given_missing_formal_when_decide_then_kill() -> None:
    formals = {
        path: f"**{dec}**" for _, (path, dec) in AS_DECISIONS.items()
    }
    miss = AS_DECISIONS["H-SHIPUI"][0]
    formals[miss] = ""
    public = {p: "COMPLETE H-ASKABSTAIN AS-DUAL-HITL" for p in AS_PUBLIC}
    product = {
        "docs/results/nano-lm/RECIPES.md": "COMPLETE H-ASKABSTAIN AS-DUAL-HITL",
        "docs/results/nano-lm/champion-card.md": (
            "COMPLETE H-ASKABSTAIN AS-DUAL-HITL"
        ),
    }
    out = decide_as_freeze(
        formal_texts=formals,
        public_texts=public,
        product_texts=product,
    )
    assert out.startswith("KILL")
    assert "H-SHIPUI" in out or miss in out
