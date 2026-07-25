"""Contract: H-TCHR formal cfg uses fit≠eval genes + prog pack."""

from __future__ import annotations

from hold_ops import assert_disjoint, load_prompt_ids
from prog_packs import PROG_PROMPTS
from run_formal_htchr import formal_cfg


def test_given_formal_cfg_when_load_then_fit_neq_eval() -> None:
    c = formal_cfg()
    assert "eval_prompts" in str(c["prompts"]) or "smoke" not in str(c["prompts"]).lower()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    assert_disjoint(load_prompt_ids(c["prompts"]), load_prompt_ids(PROG_PROMPTS))
    assert int(c["steps_kd"]) >= 120
    assert c["seeds"] == [0, 1, 2]
    assert "formal-htchr" in str(c["out"])
    assert c.get("early_dir") is not None
    assert c.get("ckpt_dir") is not None
