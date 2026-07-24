"""GPT-Neo causal logits with optional last-k layer skip on high conf."""

from __future__ import annotations

from typing import Any

import torch
import torch.nn.functional as F


def n_transformer_layers(model: Any) -> int:
    return int(len(model.transformer.h))


@torch.no_grad()
def logits_layer_exit(
    model: Any,
    input_ids: torch.Tensor,
    *,
    max_skip: int,
    lay_conf: float,
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
    seq = int(input_ids.shape[1])
    pos = torch.arange(seq, device=device).unsqueeze(0)
    hidden = tr.wte(input_ids) + tr.wpe(pos)
    layers_run = 0
    for i, block in enumerate(tr.h):
        hidden = block(hidden, use_cache=False)[0]
        layers_run += 1
        if skip > 0 and layers_run >= min_layers and layers_run < n_layers:
            logits = model.lm_head(tr.ln_f(hidden))
            max_p = F.softmax(logits[:, -1].float(), dim=-1).max(dim=-1).values
            if bool((max_p >= float(lay_conf)).all()):
                return logits, layers_run
    return model.lm_head(tr.ln_f(hidden)), layers_run
