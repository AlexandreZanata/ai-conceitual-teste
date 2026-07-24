"""H-FLASH: SDPA/FlashAttention backend on EARLY decode path."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Mapping

import torch
import torch.nn.functional as F

from lat_ops import EPS_LP

__all__ = [
    "sdpa_attn",
    "gpt_neo_sdpa_context",
    "decide_hflash",
]


def sdpa_attn(self, query, key, value, attention_mask=None, head_mask=None):
    """
    GIVEN GPT-Neo Q/K/V (unscaled matmul semantics)
    WHEN computing attention via SDPA
    THEN return (attn_output, None); fall back if head_mask set.
    """
    eager = getattr(type(self), "_attn_eager", None)
    if head_mask is not None and eager is not None:
        return eager(self, query, key, value, attention_mask, head_mask)
    # GPT-Neo additive mask is [B,1,Q,K(+pad)]; slice to key length.
    mask = None
    if attention_mask is not None:
        mask = attention_mask[..., : key.shape[-2]]
    # Match GPT-Neo eager: no 1/sqrt(d) scale; causal already in mask/bias path.
    out = F.scaled_dot_product_attention(
        query,
        key,
        value,
        attn_mask=mask,
        dropout_p=0.0,
        is_causal=mask is None,
        scale=1.0,
    )
    return out, None


@contextmanager
def gpt_neo_sdpa_context() -> Iterator[None]:
    """
    GIVEN GPT-Neo modules
    WHEN entering context
    THEN route SelfAttention._attn through SDPA; restore on exit.
    """
    from transformers.models.gpt_neo.modeling_gpt_neo import GPTNeoSelfAttention

    if not hasattr(GPTNeoSelfAttention, "_attn_eager"):
        GPTNeoSelfAttention._attn_eager = GPTNeoSelfAttention._attn  # type: ignore[attr-defined]
    orig = GPTNeoSelfAttention._attn
    GPTNeoSelfAttention._attn = sdpa_attn
    try:
        if torch.cuda.is_available():
            with torch.nn.attention.sdpa_kernel(
                [
                    torch.nn.attention.SDPBackend.FLASH_ATTENTION,
                    torch.nn.attention.SDPBackend.EFFICIENT_ATTENTION,
                    torch.nn.attention.SDPBackend.MATH,
                ]
            ):
                yield
        else:
            yield
    finally:
        GPTNeoSelfAttention._attn = orig


def decide_hflash(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-FLASH vs H-EARLY tip
    WHEN deciding
    THEN PROMOTE iff lp ≥ EARLY−ε and wall < EARLY.
    """
    tip = stats.get("H-EARLY")
    if tip is None:
        return "needs H-EARLY control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - float(eps_lp):
        return "KILL (quality drop vs H-EARLY)"
    if not (float(s["mean_wall"]) < float(tip["mean_wall"])):
        return "KILL (no wall win vs H-EARLY)"
    return "PROMOTE (SDPA backend vs EARLY)"
