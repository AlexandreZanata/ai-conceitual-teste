"""GPT-Neo causal logits with optional last-k layer skip on high conf."""

from __future__ import annotations

from typing import Any

import torch
import torch.nn.functional as F


def n_transformer_layers(model: Any) -> int:
    return int(len(model.transformer.h))


def _attn_4d(mask: torch.Tensor, *, dtype: torch.dtype) -> torch.Tensor:
    """Convert 2D 0/1 attention_mask to additive 4D mask for GPT-Neo blocks."""
    attn = mask[:, None, None, :].to(dtype=dtype)
    return (1.0 - attn) * torch.finfo(dtype).min


@torch.no_grad()
def logits_layer_exit(
    model: Any,
    input_ids: torch.Tensor,
    *,
    max_skip: int,
    lay_conf: float,
    attention_mask: torch.Tensor | None = None,
    position_ids: torch.Tensor | None = None,
) -> tuple[torch.Tensor, int]:
    """
    GIVEN causal LM ids and layer-exit knobs
    WHEN forwarding
    THEN return (logits, layers_run); may skip last max_skip blocks if conf high.
    """
    tr = model.transformer
    n_layers = len(tr.h)
    skip = int(max(0, min(int(max_skip), n_layers - 1)))
    min_layers = n_layers - skip
    device = input_ids.device
    bsz, seq = int(input_ids.shape[0]), int(input_ids.shape[1])
    if position_ids is None:
        position_ids = torch.arange(seq, device=device).unsqueeze(0).expand(bsz, -1)
    hidden = tr.wte(input_ids) + tr.wpe(position_ids)
    attn = None
    if attention_mask is not None:
        attn = _attn_4d(attention_mask, dtype=hidden.dtype)
    layers_run = 0
    for _i, block in enumerate(tr.h):
        hidden = block(hidden, attention_mask=attn, use_cache=False)[0]
        layers_run += 1
        if skip > 0 and layers_run >= min_layers and layers_run < n_layers:
            logits = model.lm_head(tr.ln_f(hidden))
            max_p = F.softmax(logits[:, -1].float(), dim=-1).max(dim=-1).values
            if bool((max_p >= float(lay_conf)).all()):
                return logits, layers_run
    return model.lm_head(tr.ln_f(hidden)), layers_run
