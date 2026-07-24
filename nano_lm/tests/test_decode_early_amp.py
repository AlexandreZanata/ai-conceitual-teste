"""Contract: AMP decode matches early-exit API and runs under autocast."""

from __future__ import annotations

import torch

from amp_ops import cast_student_amp, resolve_amp_dtype
from decode_early_amp import decode_early_amp
from student_model import build_student


class _Tok:
    eos_token_id = 0

    def encode(self, text, return_tensors=None):
        del text
        ids = torch.tensor([[1, 2, 3]])
        return ids if return_tensors == "pt" else [1, 2, 3]

    def decode(self, ids, skip_special_tokens=True):
        del ids, skip_special_tokens
        return "x"


def test_given_amp_decode_when_run_then_tokens_and_wall():
    device = torch.device("cpu")
    m = cast_student_amp(build_student(), torch.float32)
    dtype = resolve_amp_dtype("fp32", device)
    out = decode_early_amp(
        m,
        _Tok(),
        "hi",
        n=1,
        max_new_tokens=3,
        min_new=1,
        conf_threshold=0.99,
        patience=3,
        temperature=0.8,
        top_p=0.9,
        seed=0,
        device=device,
        amp_dtype=dtype,
    )
    assert len(out.token_ids) >= 1
    assert out.wall_ms >= 0.0
    assert out.token_evals >= 1
