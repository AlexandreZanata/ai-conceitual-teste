"""Load frozen TinyStories causal LM — prefer full CUDA + fp16 throughput."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


@dataclass(frozen=True)
class LoadedModel:
    model: object
    tokenizer: object
    device: torch.device
    dtype: torch.dtype


def resolve_device(prefer_cuda: bool = True) -> torch.device:
    if prefer_cuda and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def _tune_cuda() -> None:
    if not torch.cuda.is_available():
        return
    torch.backends.cudnn.benchmark = True
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.set_float32_matmul_precision("high")


def load_causal_lm(
    model_id: str,
    tokenizer_id: str,
    *,
    cache_dir: Path | None = None,
    prefer_cuda: bool = True,
    use_fp16: bool = True,
) -> LoadedModel:
    _tune_cuda()
    device = resolve_device(prefer_cuda)
    cache = str(cache_dir) if cache_dir else None
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_id, cache_dir=cache)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    dtype = torch.float16 if (use_fp16 and device.type == "cuda") else torch.float32
    kwargs = {"cache_dir": cache, "dtype": dtype}
    try:
        model = AutoModelForCausalLM.from_pretrained(model_id, **kwargs)
    except TypeError:
        model = AutoModelForCausalLM.from_pretrained(
            model_id, cache_dir=cache, torch_dtype=dtype
        )
    model.to(device)
    model.eval()
    if device.type == "cuda":
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
    return LoadedModel(
        model=model, tokenizer=tokenizer, device=device, dtype=dtype
    )
