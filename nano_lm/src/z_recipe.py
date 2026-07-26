"""Wave Z recipe card: freeze champion QPFB2 stack (schema + validate)."""

from __future__ import annotations

from typing import Any, Mapping

from pfb2_ops import K2_BEAMS
from pfb_ops import PFB_TEMP
from qt_ops import QT_BITS

__all__ = [
    "RECIPE_ID",
    "FAMILY",
    "FORBIDDEN",
    "REQUIRED_KEYS",
    "champion_recipe",
    "validate_recipe",
]

RECIPE_ID = "champion-qpfb2-v0"
FAMILY = "H-ABS-QPFB2"
FORBIDDEN = ("STREAM", "KVCACHE-Q", "GENCACHE", "GPFB_K2", "MIXD")
REQUIRED_KEYS = (
    "recipe_id",
    "family",
    "seed",
    "ckpt",
    "early_gene",
    "qt_bits",
    "pfb_k",
    "pfb_temp",
    "max_new",
    "tokenizer_id",
    "forbidden",
)


def champion_recipe(*, seed: int = 0) -> dict[str, Any]:
    """
    GIVEN Wave Y+X survivors
    WHEN freezing Z0 champion
    THEN return QPFB2 card (QT int8 + EARLY + PFB K=2); never KILL stacks.
    """
    s = int(seed)
    return {
        "recipe_id": RECIPE_ID,
        "family": FAMILY,
        "seed": s,
        "ckpt": f"B2_seed{s}.pt",
        "early_gene": f"genes/HEARLY_seed{s}_train.json",
        "qt_bits": int(QT_BITS),
        "pfb_k": int(K2_BEAMS),
        "pfb_temp": float(PFB_TEMP),
        "max_new": 32,
        "tokenizer_id": "EleutherAI/gpt-neo-125M",
        "teacher_id": "roneneldan/TinyStories-33M",
        "y_cache": {
            "beamkv": True,
            "tcache": False,
            "scoreram": False,
            "roll": False,
            "sumcache": False,
            "gpfb4long": False,
        },
        "sources": {
            "ckpt_dir": "results/nano-lm/formal-hdeck-b4",
            "early_dir": "results/nano-lm/formal-hearly",
            "formal": "docs/results/nano-lm/formal-hqpfb2-qpfb2.md",
            "wave_y": "docs/results/nano-lm/wave-y-summary.md",
        },
        "forbidden": list(FORBIDDEN),
    }


def _missing_keys(recipe: Mapping[str, Any]) -> list[str]:
    return [f"missing key: {k}" for k in REQUIRED_KEYS if k not in recipe]


def _field_errors(recipe: Mapping[str, Any]) -> list[str]:
    errs: list[str] = []
    if str(recipe["recipe_id"]) != RECIPE_ID:
        errs.append(f"recipe_id must be {RECIPE_ID}")
    if str(recipe["family"]) != FAMILY:
        errs.append(f"family must be {FAMILY}")
    if int(recipe["pfb_k"]) != int(K2_BEAMS):
        errs.append(f"pfb_k must be {K2_BEAMS} (GPFB K=2 forbidden)")
    if int(recipe["qt_bits"]) != int(QT_BITS):
        errs.append(f"qt_bits must be {QT_BITS}")
    return errs


def _forbidden_errors(recipe: Mapping[str, Any]) -> list[str]:
    forb = {str(x) for x in recipe.get("forbidden", [])}
    return [f"forbidden list missing {n}" for n in FORBIDDEN if n not in forb]


def validate_recipe(recipe: Mapping[str, Any]) -> list[str]:
    """
    GIVEN a recipe dict
    WHEN validating Z0 schema
    THEN return list of error strings (empty iff ok).
    """
    missing = _missing_keys(recipe)
    if missing:
        return missing
    return _field_errors(recipe) + _forbidden_errors(recipe)
