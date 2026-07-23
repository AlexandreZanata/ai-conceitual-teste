"""≤5M GPT-Neo-style student config + build helpers."""

from __future__ import annotations

from transformers import AutoModelForCausalLM, GPTNeoConfig


def student_config(vocab_size: int = 50257) -> GPTNeoConfig:
    """Tiny causal LM: hidden=64, layers=2 → typically ~3.5–4.5M params."""
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


def count_params(model: object) -> int:
    return sum(int(p.numel()) for p in model.parameters())


def build_student(vocab_size: int = 50257) -> object:
    cfg = student_config(vocab_size)
    model = AutoModelForCausalLM.from_config(cfg)
    n = count_params(model)
    if n > 5_000_000:
        raise RuntimeError(f"student has {n} params (>5M cap)")
    return model
