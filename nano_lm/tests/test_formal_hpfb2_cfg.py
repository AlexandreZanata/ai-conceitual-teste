"""Contract: H-ABS-PFB2 formal cfg uses fit≠eval genes + prog pack."""

from __future__ import annotations

from hold_ops import assert_disjoint, load_prompt_ids
from prog_packs import PROG_PROMPTS
from run_formal_hpfb2 import formal_cfg


def test_given_formal_cfg_when_load_then_fit_neq_eval() -> None:
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    assert_disjoint(load_prompt_ids(c["prompts"]), load_prompt_ids(PROG_PROMPTS))
    assert int(c["steps_kd"]) >= 120
    assert c["seeds"] == [0, 1, 2]
    assert "formal-hpfb2" in str(c["out"])
    assert c.get("early_dir") is not None
    assert c.get("ckpt_dir") is not None
