"""Score H-Q4 int4 student vs fp DEPTH control with EARLY genes."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import torch

from eval_student import load_student_ckpt
from load_model import LoadedModel
from prun_fit import row, score_early_flops
from q4_linear import count_int4_linears, quantize_student_int4, weight_bytes
from q4_ops import DEFAULT_GROUP, DEFAULT_TILES
from student_model import build_depth_student

__all__ = ["score_pair", "row", "DEFAULT_GROUP", "DEFAULT_TILES"]


def score_pair(
    early: dict[str, Any],
    *,
    ckpt: object,
    teacher: LoadedModel,
    prompts: list[str],
    max_new: int,
    seed: int,
    claim: int,
    groupsize: int = DEFAULT_GROUP,
    tiles: int = DEFAULT_TILES,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    GIVEN DEPTH/PRUN ckpt + EARLY genes
    WHEN scoring fp control and int4 challenge
    THEN return (depth_row, q4_row).
    """
    tok = teacher.tokenizer
    device = teacher.device
    ctrl = load_student_ckpt(ckpt, tok, device, build_fn=build_depth_student)
    _warmup(ctrl, device)
    lp_d, wall_d, gf_d = score_early_flops(
        early,
        teacher=teacher,
        student=ctrl,
        prompts=prompts,
        max_new=max_new,
        seed=claim,
        density=1.0,
    )
    depth_row = row(
        "H-DEPTH",
        f"HDEPTH_q4_seed{seed}",
        lp_d,
        wall_d,
        gf_d,
        seed,
        {
            "best_gene": early,
            "weight_bytes": weight_bytes(ctrl),
            "int4_linears": 0,
            "backend": "fp",
        },
    )
    q_model = quantize_student_int4(
        deepcopy(ctrl), groupsize=groupsize, tiles=tiles
    )
    n_int4 = count_int4_linears(q_model)
    if n_int4 < 1:
        raise RuntimeError("H-Q4: no Linear layers quantized")
    _warmup(q_model, device)
    lp_q, wall_q, gf_q = score_early_flops(
        early,
        teacher=teacher,
        student=q_model,
        prompts=prompts,
        max_new=max_new,
        seed=claim,
        density=1.0,
    )
    q4_row = row(
        "H-Q4",
        f"HQ4_seed{seed}",
        lp_q,
        wall_q,
        gf_q,
        seed,
        {
            "best_gene": early,
            "weight_bytes": weight_bytes(q_model),
            "int4_linears": n_int4,
            "groupsize": groupsize,
            "tiles": tiles,
            "backend": "aten_int4pack_cuda",
        },
    )
    return depth_row, q4_row


def _warmup(model: object, device: torch.device) -> None:
    if device.type != "cuda":
        return
    with torch.no_grad():
        _ = model(torch.zeros(1, 8, dtype=torch.long, device=device))
    torch.cuda.synchronize()
