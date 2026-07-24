"""Build ≤5M GPT-Neo student with local sliding-window attention."""

from __future__ import annotations

from transformers import AutoModelForCausalLM, GPTNeoConfig

from student_model import count_params
from win_ops import DEFAULT_WINDOW

__all__ = ["build_win_student", "WIN_WINDOW", "count_params"]

WIN_WINDOW = DEFAULT_WINDOW


def build_win_student(
    vocab_size: int = 50257, *, window: int = WIN_WINDOW
) -> object:
    """
    GIVEN vocab size and window
    WHEN building H-WIN student
    THEN local attention layers with window_size; params ≤5M.
    """
    cfg = GPTNeoConfig(
        vocab_size=vocab_size,
        hidden_size=64,
        num_layers=2,
        num_heads=4,
        max_position_embeddings=512,
        intermediate_size=256,
        attention_types=[[["local"], 2]],
        window_size=int(max(1, window)),
        activation_function="gelu_new",
        resid_dropout=0.0,
        embed_dropout=0.0,
        attention_dropout=0.0,
        bos_token_id=50256,
        eos_token_id=50256,
        use_cache=False,
    )
    model = AutoModelForCausalLM.from_config(cfg)
    n = count_params(model)
    if n > 5_000_000:
        raise RuntimeError(f"win student has {n} params (>5M cap)")
    return model
