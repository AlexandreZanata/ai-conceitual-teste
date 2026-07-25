"""Contract: H-CHBAT dual gate vs H-CBAT + B=256 chunked batch emits tokens."""

from __future__ import annotations

import torch

from chbat_ops import CHBAT_CHUNK, decide_hchbat
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
    # GIVEN H-CBAT control WHEN CHBAT wins tok/s within ε THEN PROMOTE
    tip = {"mean_lp": -16.0, "mean_tps": 100.0}
    stats = {"H-CBAT": tip}
    assert decide_hchbat(
        {"mean_lp": -16.02, "mean_tps": 150.0}, stats
    ).startswith("PROMOTE")
    assert "lp change" in decide_hchbat(
        {"mean_lp": -16.2, "mean_tps": 200.0}, stats
    )
    assert "tok/s" in decide_hchbat(
        {"mean_lp": -16.0, "mean_tps": 90.0}, stats
    )
    assert decide_hchbat({"mean_lp": -16.0, "mean_tps": 150.0}, {}).startswith(
        "needs H-CBAT"
    )


def test_given_chb_chunk_when_batch_decode_then_emits_tokens() -> None:
    # GIVEN student + CHBAT chunk / WHEN chunked batch decode / THEN ≥1 token
    assert CHBAT_CHUNK == 256
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
        chunk_size=CHBAT_CHUNK,
    )
    assert len(results) == 2
    assert all(len(r.token_ids) >= 1 for r in results)
    assert wall > 0.0
