"""Contract: H-BEAMKV shared-prefix KV decode vs indep prefills."""

from __future__ import annotations

import torch

from decode_beamkv import (
    decode_beams_indep_kv,
    decode_beams_shared_kv,
    expand_past_to_batch,
)
from student_model import build_student
from transformers.cache_utils import DynamicCache


class _Tok:
    eos_token_id = 0

    def encode(self, text: str, return_tensors: str = "pt"):
        del text, return_tensors
        return torch.tensor([[1, 2, 3, 4, 5, 6, 7, 8]])

    def decode(self, ids: list[int], skip_special_tokens: bool = True) -> str:
        del skip_special_tokens
        return " ".join(str(i) for i in ids)


def test_given_past_bsz1_when_expand_then_batch_n() -> None:
    # GIVEN bsz=1 cache WHEN expand_past_to_batch(n=3) THEN seq preserved
    m = build_student(50257).eval()
    device = torch.device("cpu")
    ids = torch.tensor([[1, 2, 3, 4]], device=device)
    with torch.no_grad():
        past = m(ids, use_cache=True).past_key_values
    past = expand_past_to_batch(past, 3)
    assert isinstance(past, DynamicCache)
    assert past.get_seq_length() == 4


def test_given_student_when_shared_kv_then_beams_and_fewer_evals() -> None:
    # GIVEN tiny student WHEN shared vs indep THEN K texts; shared evals < indep
    m = build_student(50257).eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    m = m.to(device)
    tok = _Tok()

    def _enc(text: str, return_tensors: str = "pt"):
        del text, return_tensors
        return torch.tensor([[1, 2, 3, 4, 5, 6, 7, 8]], device=device)

    tok.encode = _enc  # type: ignore[method-assign]
    kw = dict(
        n=2,
        max_new_tokens=4,
        min_new=1,
        conf_threshold=0.99,
        patience=99,
        temperature=0.8,
        top_p=0.9,
        seed=7,
        device=device,
    )
    shared = decode_beams_shared_kv(m, tok, "hi", **kw)
    indep = decode_beams_indep_kv(m, tok, "hi", **kw)
    assert len(shared) == 2 and len(indep) == 2
    assert all(len(r.token_ids) >= 1 for r in shared)
    assert shared[0].token_evals < indep[0].token_evals
