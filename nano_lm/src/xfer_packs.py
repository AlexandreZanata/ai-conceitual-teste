"""Build H-XFER prompt packs: held-out, elongated, and OOD."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from chunk_fit import long_prompts
from chunk_ops import LONG_TARGET_TOKENS
from matrix_common import ROOT
from xfer_ops import XFER_ELONGATE_TOKENS, XFER_PACKS

__all__ = [
    "OOD_PROMPTS",
    "load_yaml_texts",
    "write_texts_yaml",
    "build_xfer_packs",
    "XFER_PACKS",
]

OOD_PROMPTS = ROOT / "prompts/ood_prompts.yaml"


def load_yaml_texts(path: Path) -> list[str]:
    """Load ordered prompt texts from a prompts YAML."""
    with path.open(encoding="utf-8") as f:
        return [str(p["text"]) for p in yaml.safe_load(f)["prompts"]]


def write_texts_yaml(path: Path, texts: list[str], *, id_prefix: str) -> Path:
    """
    GIVEN elongated or filtered texts
    WHEN writing a temp prompts YAML for TPACK eval
    THEN emit id/text entries under prompts.
    """
    if not texts:
        raise ValueError("write_texts_yaml: empty texts")
    if not id_prefix:
        raise ValueError("write_texts_yaml: blank id_prefix")
    payload: dict[str, Any] = {
        "prompts": [
            {"id": f"{id_prefix}{i:02d}", "text": t} for i, t in enumerate(texts, 1)
        ]
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def build_xfer_packs(
    tok: object,
    *,
    harness: Path,
    fit: Path,
    ood: Path = OOD_PROMPTS,
) -> dict[str, dict[str, Any]]:
    """
    GIVEN harness / fit / ood YAML paths + tokenizer
    WHEN building transfer packs
    THEN return heldout@128, elongated@256, ood@128 text lists.
    """
    fit_raw = load_yaml_texts(fit)
    harness_raw = load_yaml_texts(harness)
    ood_raw = load_yaml_texts(ood)
    heldout = long_prompts(fit_raw, tok, target_tokens=LONG_TARGET_TOKENS)
    elongated = long_prompts(
        harness_raw + fit_raw, tok, target_tokens=XFER_ELONGATE_TOKENS
    )
    ood_long = long_prompts(ood_raw, tok, target_tokens=LONG_TARGET_TOKENS)
    return {
        "heldout": {
            "texts": heldout,
            "target_tokens": LONG_TARGET_TOKENS,
            "n_prompts": len(heldout),
        },
        "elongated": {
            "texts": elongated,
            "target_tokens": XFER_ELONGATE_TOKENS,
            "n_prompts": len(elongated),
        },
        "ood": {
            "texts": ood_long,
            "target_tokens": LONG_TARGET_TOKENS,
            "n_prompts": len(ood_long),
        },
    }
