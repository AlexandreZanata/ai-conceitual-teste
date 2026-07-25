"""Build H-BTC bitcoin domain pack (elongated to tip LONG_TARGET_TOKENS)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from btc_ops import BTC_PACK
from chunk_fit import long_prompts
from chunk_ops import LONG_TARGET_TOKENS
from matrix_common import ROOT
from xfer_packs import load_yaml_texts

__all__ = ["BTC_PROMPTS", "BTC_PACK", "build_btc_pack"]

BTC_PROMPTS = ROOT / "prompts/btc_prompts.yaml"


def build_btc_pack(
    tok: object,
    *,
    path: Path = BTC_PROMPTS,
    target_tokens: int = LONG_TARGET_TOKENS,
) -> dict[str, Any]:
    """
    GIVEN bitcoin domain YAML + tokenizer
    WHEN elongating to tip target
    THEN return pack dict with texts / n / target_tokens.
    """
    raw = load_yaml_texts(path)
    texts = long_prompts(raw, tok, target_tokens=int(target_tokens))
    return {
        "name": BTC_PACK,
        "texts": texts,
        "target_tokens": int(target_tokens),
        "n_prompts": len(texts),
        "source": str(path),
    }
