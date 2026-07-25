"""Contract: H-XFER prompt pack builders stay disjoint and elongate."""

from __future__ import annotations

from pathlib import Path

from hold_ops import assert_disjoint, load_prompt_ids
from matrix_common import ROOT
from xfer_ops import XFER_ELONGATE_TOKENS, LONG_TARGET_TOKENS
from xfer_packs import OOD_PROMPTS, build_xfer_packs, write_texts_yaml


class _Tok:
    def encode(self, text: str) -> list[int]:
        return text.split()


def test_given_prompt_yamls_when_load_ids_then_disjoint() -> None:
    smoke = ROOT / "prompts/smoke_prompts.yaml"
    fit = ROOT / "prompts/fit_prompts.yaml"
    assert_disjoint(load_prompt_ids(fit), load_prompt_ids(smoke))
    assert_disjoint(load_prompt_ids(smoke), load_prompt_ids(OOD_PROMPTS))
    assert_disjoint(load_prompt_ids(fit), load_prompt_ids(OOD_PROMPTS))


def test_given_harness_when_build_packs_then_targets_match() -> None:
    packs = build_xfer_packs(
        _Tok(),
        harness=ROOT / "prompts/smoke_prompts.yaml",
        fit=ROOT / "prompts/fit_prompts.yaml",
    )
    assert packs["heldout"]["target_tokens"] == LONG_TARGET_TOKENS
    assert packs["elongated"]["target_tokens"] == XFER_ELONGATE_TOKENS
    assert packs["ood"]["target_tokens"] == LONG_TARGET_TOKENS
    assert packs["heldout"]["n_prompts"] >= 1
    assert packs["elongated"]["n_prompts"] >= packs["heldout"]["n_prompts"]


def test_given_texts_when_write_yaml_then_readable(tmp_path: Path) -> None:
    path = write_texts_yaml(tmp_path / "t.yaml", ["hello world"], id_prefix="t")
    ids = load_prompt_ids(path)
    assert ids == ["t01"]
