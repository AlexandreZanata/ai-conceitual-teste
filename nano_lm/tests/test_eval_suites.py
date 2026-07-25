"""Contract: Phase E5 eval YAML suites are fixed, disjoint, and elongate."""

from __future__ import annotations

from btc_packs import BTC_PROMPTS
from chunk_ops import LONG_TARGET_TOKENS
from dom_packs import DOM_PROMPTS
from eval_suites import (
    CLAIM_PACK_PATHS,
    E5_BTC_HELDOUT,
    E5_PROG_HELDOUT,
    EVAL_SUITE_PATHS,
    FRONTIER_PROMPTS,
)
from frontier_packs import build_frontier_pack
from hold_ops import assert_disjoint, load_prompt_ids
from matrix_common import ROOT
from prog_packs import PROG_PROMPTS
from xfer_packs import OOD_PROMPTS, load_yaml_texts


class _Tok:
    def encode(self, text: str) -> list[int]:
        return text.split()


def test_given_e5_files_when_exist_then_readable() -> None:
    for path in EVAL_SUITE_PATHS:
        assert path.is_file(), f"missing {path}"
        assert len(load_yaml_texts(path)) >= 4


def test_given_e5_ids_when_load_then_mutually_disjoint() -> None:
    suites = [load_prompt_ids(p) for p in EVAL_SUITE_PATHS]
    for i, a in enumerate(suites):
        for b in suites[i + 1 :]:
            assert_disjoint(a, b)
    others = [
        ROOT / "prompts/smoke_prompts.yaml",
        ROOT / "prompts/fit_prompts.yaml",
        OOD_PROMPTS,
        DOM_PROMPTS,
        PROG_PROMPTS,
        BTC_PROMPTS,
        *CLAIM_PACK_PATHS,
    ]
    for suite_path in EVAL_SUITE_PATHS:
        sid = load_prompt_ids(suite_path)
        for other in others:
            assert_disjoint(sid, load_prompt_ids(other))


def test_given_frontier_when_build_pack_then_target_match() -> None:
    pack = build_frontier_pack(_Tok())
    assert pack["name"] == "frontier"
    assert pack["target_tokens"] == LONG_TARGET_TOKENS
    assert pack["n_prompts"] >= 4
    assert str(FRONTIER_PROMPTS) in pack["source"]


def test_given_heldout_ids_when_prefix_then_match_domains() -> None:
    prog = load_prompt_ids(E5_PROG_HELDOUT)
    btc = load_prompt_ids(E5_BTC_HELDOUT)
    frontier = load_prompt_ids(FRONTIER_PROMPTS)
    assert all(i.startswith("g") for i in prog)
    assert all(i.startswith("b") for i in btc)
    assert all(i.startswith("r") for i in frontier)
