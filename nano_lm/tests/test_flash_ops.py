"""Contract: H-FLASH SDPA context + dual gate vs EARLY."""

from __future__ import annotations

import torch

from flash_ops import decide_hflash, gpt_neo_sdpa_context
from student_model import build_student


def test_given_student_when_sdpa_then_logits_match_eager() -> None:
    m = build_student(50257).eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    m = m.to(device)
    ids = torch.randint(0, 1000, (1, 8), device=device)
    with torch.no_grad():
        eager = m(ids).logits
        with gpt_neo_sdpa_context():
            flash = m(ids).logits
    assert torch.allclose(eager, flash, atol=1e-4, rtol=1e-4)


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_wall": 70.0}
    stats = {"H-EARLY": tip}
    assert decide_hflash(
        {"mean_lp": -16.0, "mean_wall": 60.0}, stats
    ).startswith("PROMOTE")
    assert "quality" in decide_hflash(
        {"mean_lp": -16.2, "mean_wall": 50.0}, stats
    )
    assert "wall" in decide_hflash(
        {"mean_lp": -15.9, "mean_wall": 70.0}, stats
    )
