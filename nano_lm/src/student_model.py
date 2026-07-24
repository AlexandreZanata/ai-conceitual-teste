"""≤5M GPT-Neo-style student config + build helpers."""

from __future__ import annotations

from transformers import AutoModelForCausalLM, GPTNeoConfig

THIN_MAX_PARAMS = 3_000_000


def student_config(vocab_size: int = 50257) -> GPTNeoConfig:
    """Tiny causal LM: hidden=64, layers=2 → typically ~3.3M params."""
    return GPTNeoConfig(
        vocab_size=vocab_size,
        hidden_size=64,
        num_layers=2,
        num_heads=4,
        max_position_embeddings=512,
        intermediate_size=256,
        attention_types=[[["global"], 2]],
        activation_function="gelu_new",
        resid_dropout=0.0,
        embed_dropout=0.0,
        attention_dropout=0.0,
        bos_token_id=50256,
        eos_token_id=50256,
        use_cache=False,
    )


def thin_student_config(vocab_size: int = 50257) -> GPTNeoConfig:
    """Thinner student: hidden=48 → typically ~2.5M params (≤3M)."""
    return GPTNeoConfig(
        vocab_size=vocab_size,
        hidden_size=48,
        num_layers=2,
        num_heads=4,
        max_position_embeddings=512,
        intermediate_size=192,
        attention_types=[[["global"], 2]],
        activation_function="gelu_new",
        resid_dropout=0.0,
        embed_dropout=0.0,
        attention_dropout=0.0,
        bos_token_id=50256,
        eos_token_id=50256,
        use_cache=False,
    )


def count_params(model: object) -> int:
    return sum(int(p.numel()) for p in model.parameters())


def build_student(vocab_size: int = 50257) -> object:
    cfg = student_config(vocab_size)
    model = AutoModelForCausalLM.from_config(cfg)
    n = count_params(model)
    if n > 5_000_000:
        raise RuntimeError(f"student has {n} params (>5M cap)")
    return model


def build_thin_student(vocab_size: int = 50257) -> object:
    """
    GIVEN vocab size
    WHEN building H-THIN student
    THEN params ≤ THIN_MAX_PARAMS.
    """
    cfg = thin_student_config(vocab_size)
    model = AutoModelForCausalLM.from_config(cfg)
    n = count_params(model)
    if n > THIN_MAX_PARAMS:
        raise RuntimeError(f"thin student has {n} params (>{THIN_MAX_PARAMS})")
    return model
