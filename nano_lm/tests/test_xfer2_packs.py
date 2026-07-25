"""Contract: H-XFER2 prompt packs deepen elongated + OOD axes."""

from __future__ import annotations

from hold_ops import assert_disjoint, load_prompt_ids
from matrix_common import ROOT
from xfer_packs import OOD_PROMPTS
from xfer2_ops import XFER2_ELONGATE_TOKENS, LONG_TARGET_TOKENS
from xfer2_packs import build_xfer2_packs


class _Tok:
    def encode(self, text: str) -> list[int]:
        return text.split()


def test_given_prompt_yamls_when_load_ids_then_disjoint() -> None:
    smoke = ROOT / "prompts/smoke_prompts.yaml"
    fit = ROOT / "prompts/fit_prompts.yaml"
    assert_disjoint(load_prompt_ids(fit), load_prompt_ids(smoke))
    assert_disjoint(load_prompt_ids(smoke), load_prompt_ids(OOD_PROMPTS))
    assert_disjoint(load_prompt_ids(fit), load_prompt_ids(OOD_PROMPTS))


def test_given_harness_when_build_xfer2_packs_then_targets_match() -> None:
    packs = build_xfer2_packs(
        _Tok(),
        harness=ROOT / "prompts/smoke_prompts.yaml",
        fit=ROOT / "prompts/fit_prompts.yaml",
    )
    assert set(packs) == {"elongated", "ood", "ood_long"}
    assert packs["elongated"]["target_tokens"] == XFER2_ELONGATE_TOKENS
    assert packs["ood"]["target_tokens"] == LONG_TARGET_TOKENS
    assert packs["ood_long"]["target_tokens"] == XFER2_ELONGATE_TOKENS
    assert packs["elongated"]["n_prompts"] >= 1
    assert packs["ood"]["n_prompts"] >= 1
    assert packs["ood_long"]["n_prompts"] == packs["ood"]["n_prompts"]
