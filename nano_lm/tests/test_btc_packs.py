"""Contract: H-BTC bitcoin prompts are disjoint and elongate."""

from __future__ import annotations

from btc_packs import BTC_PROMPTS, build_btc_pack
from chunk_ops import LONG_TARGET_TOKENS
from dom_packs import DOM_PROMPTS
from hold_ops import assert_disjoint, load_prompt_ids
from matrix_common import ROOT
from prog_packs import PROG_PROMPTS
from xfer_packs import OOD_PROMPTS


class _Tok:
    def encode(self, text: str) -> list[int]:
        return text.split()


def test_given_btc_yamls_when_load_ids_then_disjoint() -> None:
    smoke = ROOT / "prompts/smoke_prompts.yaml"
    fit = ROOT / "prompts/fit_prompts.yaml"
    assert_disjoint(load_prompt_ids(fit), load_prompt_ids(smoke))
    assert_disjoint(load_prompt_ids(smoke), load_prompt_ids(BTC_PROMPTS))
    assert_disjoint(load_prompt_ids(fit), load_prompt_ids(BTC_PROMPTS))
    assert_disjoint(load_prompt_ids(OOD_PROMPTS), load_prompt_ids(BTC_PROMPTS))
    assert_disjoint(load_prompt_ids(DOM_PROMPTS), load_prompt_ids(BTC_PROMPTS))
    assert_disjoint(load_prompt_ids(PROG_PROMPTS), load_prompt_ids(BTC_PROMPTS))


def test_given_btc_when_build_pack_then_target_match() -> None:
    pack = build_btc_pack(_Tok())
    assert pack["target_tokens"] == LONG_TARGET_TOKENS
    assert pack["n_prompts"] >= 1
    assert pack["name"] == "btc"
