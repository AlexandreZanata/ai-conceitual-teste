"""Weight-only int4 Linear via torch._weight_int4pack_mm (CUDA)."""

from __future__ import annotations

import torch
import torch.nn as nn

from q4_ops import DEFAULT_GROUP, DEFAULT_TILES

__all__ = [
    "Int4Linear",
    "quantize_student_int4",
    "count_int4_linears",
    "weight_bytes",
]


def _group_qparams(
    w: torch.Tensor, *, groupsize: int
) -> tuple[torch.Tensor, torch.Tensor]:
    to_q = w.reshape(-1, groupsize)
    mx = to_q.amax(dim=1, keepdim=True)
    mn = to_q.amin(dim=1, keepdim=True)
    scales = (mx - mn).clamp(min=1e-6) / 15.0
    zeros = mn + scales * 8.0
    return scales.reshape(w.shape[0], -1), zeros.reshape(w.shape[0], -1)


def _pack_saz(scales: torch.Tensor, zeros: torch.Tensor) -> torch.Tensor:
    return (
        torch.cat(
            [scales.unsqueeze(-1), zeros.unsqueeze(-1)],
            dim=2,
        )
        .transpose(0, 1)
        .contiguous()
    )


def _quantize_weight(
    weight: torch.Tensor, *, groupsize: int, tiles: int
) -> tuple[torch.Tensor, torch.Tensor]:
    """Return (int4pack, scales_and_zeros) for CUDA mm."""
    w = weight.detach().to(torch.bfloat16)
    scales, zeros = _group_qparams(w.float(), groupsize=groupsize)
    scales = scales.to(torch.bfloat16)
    zeros = zeros.to(torch.bfloat16)
    to_q = w.float().reshape(-1, groupsize)
    s = scales.reshape(-1, 1).float()
    z = zeros.reshape(-1, 1).float()
    min_val = z - s * 8.0
    w_int = ((to_q - min_val) / s).round().clamp(0, 15).to(torch.int32)
    w_int = w_int.reshape_as(w)
    # Kernel nibble order: high=even index, low=odd index.
    packed = (w_int[:, 1::2] | (w_int[:, ::2] << 4)).to(torch.uint8)
    pack = torch._convert_weight_to_int4pack(packed.contiguous(), tiles)
    return pack, _pack_saz(scales, zeros)


def _k_ok(k: int, groupsize: int, tiles: int) -> bool:
    return k % groupsize == 0 and k % (tiles * 16) == 0


class Int4Linear(nn.Module):
    """Inference Linear with packed int4 weights + optional bias."""

    def __init__(
        self,
        in_features: int,
        out_features: int,
        *,
        groupsize: int,
        tiles: int,
        bias: torch.Tensor | None,
        weight_pack: torch.Tensor,
        scales_and_zeros: torch.Tensor,
    ) -> None:
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.groupsize = groupsize
        self.register_buffer("weight", weight_pack)
        self.register_buffer("scales_and_zeros", scales_and_zeros)
        if bias is None:
            self.bias = None
        else:
            self.register_buffer("bias", bias.detach().to(torch.bfloat16))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        shape = x.shape
        flat = x.reshape(-1, shape[-1]).to(torch.bfloat16).contiguous()
        out = torch._weight_int4pack_mm(
            flat, self.weight, self.groupsize, self.scales_and_zeros
        )
        if self.bias is not None:
            out = out + self.bias
        return out.reshape(*shape[:-1], self.out_features)


def quantize_student_int4(
    model: nn.Module,
    *,
    groupsize: int = DEFAULT_GROUP,
    tiles: int = DEFAULT_TILES,
) -> nn.Module:
    """
    GIVEN a DEPTH/PRUN student on CUDA
    WHEN replacing compatible Linear layers with Int4Linear
    THEN return model ready for weight-only int4 decode.
    """
    device = next(model.parameters()).device
    if device.type != "cuda":
        raise RuntimeError("H-Q4 requires CUDA for int4pack kernels")

    def _walk(module: nn.Module) -> None:
        for name, child in list(module.named_children()):
            if isinstance(child, nn.Linear):
                if child.out_features % 8 != 0:
                    continue
                if not _k_ok(child.in_features, groupsize, tiles):
                    continue
                w = child.weight.data.to(device)
                pack, saz = _quantize_weight(w, groupsize=groupsize, tiles=tiles)
                bias = None if child.bias is None else child.bias.data.to(device)
                setattr(
                    module,
                    name,
                    Int4Linear(
                        child.in_features,
                        child.out_features,
                        groupsize=groupsize,
                        tiles=tiles,
                        bias=bias,
                        weight_pack=pack,
                        scales_and_zeros=saz,
                    ),
                )
            else:
                _walk(child)

    model = model.eval()
    _walk(model)
    return model


def count_int4_linears(model: nn.Module) -> int:
    return sum(1 for m in model.modules() if isinstance(m, Int4Linear))


def weight_bytes(model: nn.Module) -> int:
    """Total bytes of parameter/buffer tensors (approx memory)."""
    total = 0
    for p in model.parameters():
        total += int(p.numel() * p.element_size())
    for b in model.buffers():
        total += int(b.numel() * b.element_size())
    return total
