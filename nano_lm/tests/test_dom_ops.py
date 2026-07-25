"""Contract: H-DOM PACK tip gate aggregate on new domain."""

from __future__ import annotations

from dom_ops import decide_hdom


def test_given_pack_promote_when_decide_then_promote() -> None:
    out = decide_hdom({"H-PACK": "PROMOTE (SERVE=min-wall + SROUTE=Pareto packs vs EARLY)"})
    assert out.startswith("PROMOTE")
    assert "howto" in out


def test_given_pack_kill_when_decide_then_kill() -> None:
    out = decide_hdom({"H-PACK": "KILL (SERVE lp change vs H-EARLY)"})
    assert out.startswith("KILL")
    assert "PACK tip gate fails" in out


def test_given_missing_when_decide_then_needs() -> None:
    assert decide_hdom({}).startswith("needs H-PACK")
