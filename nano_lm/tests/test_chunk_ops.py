"""Contract: H-CHUNK elongate + dual gate + chunked decode."""

from __future__ import annotations

import torch

from chunk_ops import decide_hchunk, elongate_prompt
from decode_chunk import decode_early_chunked
from student_model import build_student


class _Tok:
    def encode(self, text: str, return_tensors: str | None = None):
        ids = list(range(1, len(text.split()) + 1)) or [1]
        if return_tensors == "pt":
            return torch.tensor([ids], dtype=torch.long)
        return ids

    def decode(self, ids: list[int], skip_special_tokens: bool = True) -> str:
        return " ".join(str(i) for i in ids)

    eos_token_id = 0


def test_given_short_when_elongate_then_meets_target() -> None:
    # GIVEN short text / WHEN elongate / THEN ≥ target token count
    out = elongate_prompt("once upon", _Tok(), target_tokens=8)
    assert len(_Tok().encode(out)) >= 8


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    stats = {
        "H-EARLY": {"mean_lp": -16.0, "mean_wall": 200.0},
        "H-FLASH": {"mean_lp": -16.0, "mean_wall": 120.0},
    }
    assert decide_hchunk(
        {"mean_lp": -16.0, "mean_wall": 80.0}, stats
    ).startswith("PROMOTE")
    assert "quality" in decide_hchunk(
        {"mean_lp": -16.2, "mean_wall": 50.0}, stats
    )
    assert "wall" in decide_hchunk(
        {"mean_lp": -15.9, "mean_wall": 120.0}, stats
    )
    assert decide_hchunk({"mean_lp": -16.0, "mean_wall": 80.0}, {}).startswith(
        "needs H-EARLY"
    )


def test_given_student_when_chunked_decode_then_emits_tokens() -> None:
    # GIVEN student + longish prompt / WHEN chunked decode / THEN ≥1 new token
    m = build_student(50257).eval()
    device = torch.device("cpu")
    tok = _Tok()
    prompt = " ".join(["once"] * 40)
    out = decode_early_chunked(
        m,
        tok,
        prompt,
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
    assert len(out.token_ids) >= 1
    assert out.token_evals >= 5  # ≥ ceil(40/8) prefill + ≥1 gen
