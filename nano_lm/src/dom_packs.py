"""Build H-DOM howto domain pack (elongated to tip LONG_TARGET_TOKENS)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from chunk_fit import long_prompts
from chunk_ops import LONG_TARGET_TOKENS
from matrix_common import ROOT
from xfer_packs import load_yaml_texts
from dom_ops import DOM_PACK

__all__ = ["DOM_PROMPTS", "DOM_PACK", "build_dom_pack"]

DOM_PROMPTS = ROOT / "prompts/dom_prompts.yaml"


def build_dom_pack(
    tok: object,
    *,
    path: Path = DOM_PROMPTS,
    target_tokens: int = LONG_TARGET_TOKENS,
) -> dict[str, Any]:
    """
    GIVEN howto domain YAML + tokenizer
    WHEN elongating to tip target
    THEN return pack dict with texts / n / target_tokens.
    """
    raw = load_yaml_texts(path)
    texts = long_prompts(raw, tok, target_tokens=int(target_tokens))
    return {
        "name": DOM_PACK,
        "texts": texts,
        "target_tokens": int(target_tokens),
        "n_prompts": len(texts),
        "source": str(path),
    }
