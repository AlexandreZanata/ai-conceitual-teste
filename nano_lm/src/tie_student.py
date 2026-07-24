"""Build ≤5M student with shared transformer block (UT-lite)."""

from __future__ import annotations

from torch.nn import ModuleList

from student_model import build_student, count_params

__all__ = ["build_tie_student", "share_transformer_blocks", "count_params"]


def share_transformer_blocks(model: object) -> object:
    """
    GIVEN a GPT-Neo student with ≥2 layers
    WHEN sharing
    THEN all blocks alias block 0 (Universal-Transformer-lite).
    """
    blocks = list(model.transformer.h)
    if len(blocks) < 2:
        return model
    shared = blocks[0]
    model.transformer.h = ModuleList([shared for _ in blocks])
    if hasattr(model, "tie_weights"):
        model.tie_weights()
    return model


def build_tie_student(vocab_size: int = 50257) -> object:
    """
    GIVEN vocab size
    WHEN building H-TIE student
    THEN standard student with shared depth weights (embeds already tied).
    """
    model = build_student(vocab_size)
    return share_transformer_blocks(model)
