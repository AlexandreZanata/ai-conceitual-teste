"""Contract: H-MIXD dual gate on story LP + prog PPL."""

from __future__ import annotations

from hold_ops import assert_disjoint, load_prompt_ids
from mixd_ops import EPS_LP, MIX_FRAC, decide_hmixd
from run_formal_hmixd import formal_cfg


def test_given_both_gates_when_decide_then_promote() -> None:
    out = decide_hmixd(
        mix_story_lp=-12.0,
        ctrl_story_lp=-12.0,
        mix_prog_ppl=40.0,
        ctrl_prog_ppl=50.0,
    )
    assert out.startswith("PROMOTE")
    assert str(MIX_FRAC) in out


def test_given_story_regress_when_decide_then_kill() -> None:
    out = decide_hmixd(
        mix_story_lp=-12.0 - EPS_LP - 0.01,
        ctrl_story_lp=-12.0,
        mix_prog_ppl=40.0,
        ctrl_prog_ppl=50.0,
    )
    assert out.startswith("KILL")
    assert "story" in out


def test_given_ppl_not_down_when_decide_then_kill() -> None:
    out = decide_hmixd(
        mix_story_lp=-12.0,
        ctrl_story_lp=-12.0,
        mix_prog_ppl=50.0,
        ctrl_prog_ppl=50.0,
    )
    assert out.startswith("KILL")
    assert "prog PPL" in out


def test_given_formal_cfg_when_load_then_fit_neq_eval() -> None:
    c = formal_cfg()
    assert "eval_prompts" in str(c["prompts"])
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    assert int(c["steps_kd"]) >= 120
    assert c["seeds"] == [0, 1, 2]
