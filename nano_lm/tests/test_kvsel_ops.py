"""Contract: H-KVSEL gated KV + dual gate vs EARLY."""

from __future__ import annotations

import torch

from decode_kvsel import decode_kvsel
from kvsel_ops import (
    decide_hkvsel,
    est_kvsel_flops,
    should_use_kv,
)
from student_model import build_student


class _Tok:
    eos_token_id = 0

    def encode(self, text: str, return_tensors: str = "pt"):
        del text, return_tensors
        return torch.tensor([[1, 2, 3, 4]])

    def decode(self, ids: list[int], skip_special_tokens: bool = True) -> str:
        del skip_special_tokens
        return " ".join(str(i) for i in ids)


def test_given_budget_when_threshold_then_kv_gate() -> None:
    # GIVEN max_new and kv_threshold WHEN selecting THEN strict >
    assert should_use_kv(64, 32) is True
    assert should_use_kv(32, 32) is False
    assert should_use_kv(16, 32) is False
    assert should_use_kv(1, 0) is True


def test_given_kv_flag_when_est_flops_then_kv_cheaper() -> None:
    # GIVEN same lengths WHEN use_kv THEN FLOPs below uncached triangle
    eager = est_kvsel_flops(n_params=1000, prompt_len=8, n_new=16, use_kv=False)
    kv = est_kvsel_flops(n_params=1000, prompt_len=8, n_new=16, use_kv=True)
    assert kv < eager
    assert kv == 2.0 * 1000 * (8 + 16)


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_wall": 70.0}
    stats = {"H-EARLY": tip}
    assert decide_hkvsel(
        {"mean_lp": -16.0, "mean_wall": 60.0}, stats
    ).startswith("PROMOTE")
    assert "quality" in decide_hkvsel(
        {"mean_lp": -16.2, "mean_wall": 50.0}, stats
    )
    assert "wall" in decide_hkvsel(
        {"mean_lp": -15.9, "mean_wall": 70.0}, stats
    )


def test_given_student_when_kv_decode_then_logits_path_runs() -> None:
    # GIVEN tiny student WHEN KV decode THEN non-empty tokens
    m = build_student(50257).eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    m = m.to(device)
    tok = _Tok()
    # override encode to device tensor
    def _enc(text: str, return_tensors: str = "pt"):
        del text, return_tensors
        return torch.tensor([[1, 2, 3, 4]], device=device)

    tok.encode = _enc  # type: ignore[method-assign]
    out = decode_kvsel(
        m,
        tok,
        "hi",
        n=1,
        max_new_tokens=3,
        min_new=1,
        conf_threshold=0.99,
        patience=99,
        temperature=0.0,
        top_p=1.0,
        seed=0,
        device=device,
        use_kv=True,
    )
    assert len(out.token_ids) >= 1
    assert out.wall_ms >= 0.0
