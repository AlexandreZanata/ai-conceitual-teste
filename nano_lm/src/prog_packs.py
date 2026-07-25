"""Build H-PROG programming domain pack (elongated to tip LONG_TARGET_TOKENS)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from chunk_fit import long_prompts
from chunk_ops import LONG_TARGET_TOKENS
from matrix_common import ROOT
from prog_ops import PROG_PACK
from xfer_packs import load_yaml_texts

__all__ = ["PROG_PROMPTS", "PROG_PACK", "build_prog_pack"]

PROG_PROMPTS = ROOT / "prompts/prog_prompts.yaml"


def build_prog_pack(
    tok: object,
    *,
    path: Path = PROG_PROMPTS,
    target_tokens: int = LONG_TARGET_TOKENS,
) -> dict[str, Any]:
    """
    GIVEN programming domain YAML + tokenizer
    WHEN elongating to tip target
    THEN return pack dict with texts / n / target_tokens.
    """
    raw = load_yaml_texts(path)
    texts = long_prompts(raw, tok, target_tokens=int(target_tokens))
    return {
        "name": PROG_PACK,
        "texts": texts,
        "target_tokens": int(target_tokens),
        "n_prompts": len(texts),
        "source": str(path),
    }
