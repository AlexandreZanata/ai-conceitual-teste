"""Contract: H-ABS-BPFB formal cfg uses fit≠eval + BTC pack."""

from __future__ import annotations

from btc_packs import BTC_PROMPTS
from hold_ops import assert_disjoint, load_prompt_ids
from prog_packs import PROG_PROMPTS
from run_formal_hbpfb import formal_cfg


def test_given_formal_cfg_when_load_then_fit_neq_eval() -> None:
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    assert_disjoint(load_prompt_ids(c["prompts"]), load_prompt_ids(BTC_PROMPTS))
    assert_disjoint(load_prompt_ids(PROG_PROMPTS), load_prompt_ids(BTC_PROMPTS))
    assert int(c["steps_kd"]) >= 120
    assert c["seeds"] == [0, 1, 2]
    assert "formal-hbpfb" in str(c["out"])
    assert c.get("early_dir") is not None
    assert c.get("ckpt_dir") is not None
