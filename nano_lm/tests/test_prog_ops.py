"""Contract: H-PROG PACK tip gate aggregate on programming domain."""

from __future__ import annotations

from prog_ops import decide_hprog


def test_given_pack_promote_when_decide_then_promote() -> None:
    out = decide_hprog(
        {"H-PACK": "PROMOTE (SERVE=min-wall + SROUTE=Pareto packs vs EARLY)"}
    )
    assert out.startswith("PROMOTE")
    assert "prog" in out


def test_given_pack_kill_when_decide_then_kill() -> None:
    out = decide_hprog({"H-PACK": "KILL (SERVE lp change vs H-EARLY)"})
    assert out.startswith("KILL")
    assert "PACK tip gate fails" in out


def test_given_missing_when_decide_then_needs() -> None:
    assert decide_hprog({}).startswith("needs H-PACK")
