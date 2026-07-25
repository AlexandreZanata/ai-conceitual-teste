"""Build Phase E5 frontier eval pack (elongated to tip LONG_TARGET_TOKENS)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from chunk_fit import long_prompts
from chunk_ops import LONG_TARGET_TOKENS
from eval_suites import FRONTIER_PROMPTS
from xfer_packs import load_yaml_texts

__all__ = ["FRONTIER_PROMPTS", "FRONTIER_PACK", "build_frontier_pack"]

FRONTIER_PACK = "frontier"


def build_frontier_pack(
    tok: object,
    *,
    path: Path = FRONTIER_PROMPTS,
    target_tokens: int = LONG_TARGET_TOKENS,
) -> dict[str, Any]:
    """
    GIVEN frontier domain YAML + tokenizer
    WHEN elongating to tip target
    THEN return pack dict with texts / n / target_tokens.
    """
    raw = load_yaml_texts(path)
    texts = long_prompts(raw, tok, target_tokens=int(target_tokens))
    return {
        "name": FRONTIER_PACK,
        "texts": texts,
        "target_tokens": int(target_tokens),
        "n_prompts": len(texts),
        "source": str(path),
    }
