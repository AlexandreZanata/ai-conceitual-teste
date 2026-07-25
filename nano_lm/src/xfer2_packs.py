"""Build H-XFER2 packs: elongated harness, OOD, and elongated OOD."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from chunk_fit import long_prompts
from chunk_ops import LONG_TARGET_TOKENS
from xfer_packs import OOD_PROMPTS, load_yaml_texts
from xfer2_ops import XFER2_ELONGATE_TOKENS, XFER2_PACKS

__all__ = [
    "OOD_PROMPTS",
    "build_xfer2_packs",
    "XFER2_PACKS",
]


def build_xfer2_packs(
    tok: object,
    *,
    harness: Path,
    fit: Path,
    ood: Path = OOD_PROMPTS,
) -> dict[str, dict[str, Any]]:
    """
    GIVEN harness / fit / ood YAML paths + tokenizer
    WHEN building PACK-only transfer deepen packs
    THEN return elongated@256, ood@128, ood_long@256 text lists.
    """
    fit_raw = load_yaml_texts(fit)
    harness_raw = load_yaml_texts(harness)
    ood_raw = load_yaml_texts(ood)
    elongated = long_prompts(
        harness_raw + fit_raw, tok, target_tokens=XFER2_ELONGATE_TOKENS
    )
    ood_std = long_prompts(ood_raw, tok, target_tokens=LONG_TARGET_TOKENS)
    ood_long = long_prompts(ood_raw, tok, target_tokens=XFER2_ELONGATE_TOKENS)
    return {
        "elongated": {
            "texts": elongated,
            "target_tokens": XFER2_ELONGATE_TOKENS,
            "n_prompts": len(elongated),
        },
        "ood": {
            "texts": ood_std,
            "target_tokens": LONG_TARGET_TOKENS,
            "n_prompts": len(ood_std),
        },
        "ood_long": {
            "texts": ood_long,
            "target_tokens": XFER2_ELONGATE_TOKENS,
            "n_prompts": len(ood_long),
        },
    }
