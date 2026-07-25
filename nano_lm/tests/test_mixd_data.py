"""Contract: H-MIXD hold-out and mix batch shape."""

from __future__ import annotations

import torch

from hold_ops import load_prompt_ids
from matrix_common import ROOT
from mixd_data import (
    assert_mixd_holdout,
    load_prog_corpus_texts,
    plan_mix_batches,
    train_source_ids,
)
from mixd_ops import MIX_FRAC
from prog_packs import PROG_PROMPTS


def test_given_mixd_when_holdout_then_disjoint() -> None:
    assert_mixd_holdout()
    train = set(train_source_ids())
    eval_ids = set(load_prompt_ids(PROG_PROMPTS))
    assert train.isdisjoint(eval_ids)
    assert len(train) >= 1


def test_given_curated_when_load_then_nonempty() -> None:
    texts = load_prog_corpus_texts()
    assert len(texts) >= 1
    assert all(len(t) > 20 for t in texts)


def test_given_fake_story_when_mix_then_same_len_and_frac() -> None:
    story = [torch.zeros(2, 32, dtype=torch.long) for _ in range(10)]
    mix = plan_mix_batches(
        story,
        tokenizer_id="EleutherAI/gpt-neo-125M",
        cache_dir=ROOT / ".cache",
        seq_len=32,
        batch_size=2,
        seed=0,
        mix_frac=MIX_FRAC,
    )
    assert len(mix) == len(story)
    n_diff = sum(1 for a, b in zip(story, mix, strict=True) if not a.equal(b))
    assert n_diff >= 1
