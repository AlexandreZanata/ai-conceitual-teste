"""Contract: H-PROG PACK tip gate aggregate on programming domain."""

from __future__ import annotations

from hold_ops import assert_disjoint, load_prompt_ids
from prog_ops import decide_hprog
from run_formal_hprog import formal_cfg


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


def test_given_formal_cfg_when_load_then_fit_neq_eval() -> None:
    c = formal_cfg()
    assert "eval_prompts" in str(c["prompts"])
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    assert int(c["steps_kd"]) >= 120
    assert c["seeds"] == [0, 1, 2]
