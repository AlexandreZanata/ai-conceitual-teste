"""Curated programming corpus + STAG/mix batch planners for H-MIXD."""

from __future__ import annotations

import re
from pathlib import Path

import torch

from curated_sources import by_domain
from hold_ops import assert_disjoint, load_prompt_ids
from matrix_common import ROOT
from mixd_ops import MIX_FRAC, TRAIN_DOMAIN
from prog_packs import PROG_PROMPTS
from stag_batch_plan import plan_cur_batches
from stag_ops import STAG_SEQ_LO
from top_pair import TIP_STAGES

__all__ = [
    "CURATED_ROOT",
    "MIX_FRAC",
    "PROG_PROMPTS",
    "assert_mixd_holdout",
    "load_prog_corpus_texts",
    "plan_mix_batches",
    "plan_story_batches",
    "train_source_ids",
]

CURATED_ROOT = ROOT / "data" / "curated"
_TAG = re.compile(r"<[^>]+>")


def train_source_ids(domain: str = TRAIN_DOMAIN) -> list[str]:
    """Ordered curated source ids for the train-mix domain."""
    return [str(s["id"]) for s in by_domain(domain)]


def assert_mixd_holdout() -> None:
    """
    GIVEN curated train source ids and prog eval prompt ids
    WHEN validating C2 hold-out
    THEN raise if any shared id.
    """
    assert_disjoint(train_source_ids(), load_prompt_ids(PROG_PROMPTS))


def _plain(raw: str) -> str:
    return re.sub(r"\s+", " ", _TAG.sub(" ", raw)).strip()


def load_prog_corpus_texts(
    root: Path = CURATED_ROOT, *, domain: str = TRAIN_DOMAIN
) -> list[str]:
    """
    GIVEN curated domain files on disk
    WHEN loading train-mix corpus
    THEN return non-empty plain texts (HTML stripped).
    """
    texts: list[str] = []
    for row in by_domain(domain):
        path = root / str(row["path"])
        if not path.is_file():
            raise FileNotFoundError(f"curated missing: {path}")
        plain = _plain(path.read_text(encoding="utf-8", errors="ignore"))
        if plain:
            texts.append(plain)
    if not texts:
        raise ValueError("load_prog_corpus_texts: empty corpus")
    return texts


def plan_story_batches(
    *,
    tokenizer_id: str,
    cache_dir: Path,
    steps: int,
    batch_size: int,
    seq_len: int,
    max_examples: int,
    seed: int,
) -> list[torch.Tensor]:
    """STAG curriculum TinyStories batches (story-only control)."""
    return plan_cur_batches(
        tokenizer_id=tokenizer_id,
        cache_dir=cache_dir,
        steps=steps,
        batch_size=batch_size,
        seq_len=seq_len,
        max_examples=max_examples,
        seq_lo=STAG_SEQ_LO,
        n_stages=TIP_STAGES,
        seed=seed,
    )


def _pack_prog_batches(
    texts: list[str],
    tok: object,
    *,
    seq_len: int,
    batch_size: int,
    n_batches: int,
    seed: int,
) -> list[torch.Tensor]:
    g = torch.Generator()
    g.manual_seed(int(seed))
    buf: list[int] = []
    for t in texts:
        # Chunk plain text before encode to avoid tokenizer length warnings.
        for i in range(0, len(t), 1500):
            ids = tok.encode(t[i : i + 1500], add_special_tokens=False)
            buf.extend(list(ids) + [int(tok.eos_token_id)])
    if len(buf) < seq_len:
        raise ValueError("_pack_prog_batches: corpus too short")
    out: list[torch.Tensor] = []
    while len(out) < n_batches:
        batch: list[list[int]] = []
        while len(batch) < batch_size:
            start = int(torch.randint(0, len(buf) - seq_len + 1, (1,), generator=g))
            batch.append(buf[start : start + seq_len])
        out.append(torch.tensor(batch, dtype=torch.long))
    return out


def plan_mix_batches(
    story: list[torch.Tensor],
    *,
    tokenizer_id: str,
    cache_dir: Path,
    seq_len: int,
    batch_size: int,
    seed: int,
    mix_frac: float = MIX_FRAC,
) -> list[torch.Tensor]:
    """
    GIVEN story STAG batches + curated programming corpus
    WHEN replacing mix_frac of steps with prog packs
    THEN return mixed batch list (same length as story).
    """
    if not (0.0 < float(mix_frac) < 1.0):
        raise ValueError("plan_mix_batches: mix_frac must be in (0,1)")
    from data_tiny import load_tokenizer

    tok = load_tokenizer(tokenizer_id, cache_dir)
    n = len(story)
    n_mix = max(1, int(round(n * float(mix_frac))))
    prog = _pack_prog_batches(
        load_prog_corpus_texts(),
        tok,
        seq_len=seq_len,
        batch_size=batch_size,
        n_batches=n_mix,
        seed=seed + 7,
    )
    g = torch.Generator()
    g.manual_seed(int(seed) + 13)
    idx = torch.randperm(n, generator=g)[:n_mix].tolist()
    out = [b.clone() for b in story]
    for i, j in enumerate(idx):
        out[int(j)] = prog[i % len(prog)]
    return out
