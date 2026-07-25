"""Contract: H-CBAT dual gate vs H-BAT + chunked batch decode emits tokens."""

from __future__ import annotations

import torch

from cbat_ops import decide_hcbat
from decode_cbat import decode_early_batch_chunked
from student_model import build_student


class _Tok:
    pad_token_id = 0
    eos_token_id = 0

    def encode(self, text: str, add_special_tokens: bool = True):
        return list(range(1, len(text.split()) + 1)) or [1]

    def decode(self, ids: list[int], skip_special_tokens: bool = True) -> str:
        return " ".join(str(i) for i in ids)


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    # GIVEN H-BAT control WHEN CBAT wins tok/s within ε THEN PROMOTE
    tip = {"mean_lp": -16.0, "mean_tps": 100.0}
    stats = {"H-BAT": tip}
    assert decide_hcbat(
        {"mean_lp": -16.02, "mean_tps": 150.0}, stats
    ).startswith("PROMOTE")
    assert "lp change" in decide_hcbat(
        {"mean_lp": -16.2, "mean_tps": 200.0}, stats
    )
    assert "tok/s" in decide_hcbat(
        {"mean_lp": -16.0, "mean_tps": 90.0}, stats
    )
    assert decide_hcbat({"mean_lp": -16.0, "mean_tps": 150.0}, {}).startswith(
        "needs H-BAT"
    )


def test_given_batch_when_chunked_decode_then_emits_tokens() -> None:
    # GIVEN student + longish prompts / WHEN chunked batch decode / THEN ≥1 token
    m = build_student(50257).eval()
    device = torch.device("cpu")
    tok = _Tok()
    prompts = [" ".join(["once"] * 20), " ".join(["upon"] * 12)]
    results, wall = decode_early_batch_chunked(
        m,
        tok,
        prompts,
        n=1,
        max_new_tokens=4,
        min_new=1,
        conf_threshold=0.99,
        patience=8,
        temperature=0.0,
        top_p=1.0,
        seed=0,
        device=device,
        chunk_size=8,
    )
    assert len(results) == 2
    assert all(len(r.token_ids) >= 1 for r in results)
    assert wall > 0.0
    assert results[0].token_evals >= 3  # prefill chunks + gen
