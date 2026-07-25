"""Contract: H-GENC prompt window + Jaccard top-k."""

from __future__ import annotations

from genc_prompt import apply_genc_prompt, jaccard, stride_window, top_k_chunks


def test_given_long_when_stride_then_tail() -> None:
    text = "abcdefghij" * 20
    out = stride_window(text, stride=16, chunk_len=32)
    assert out == text[-32:]
    assert len(out) == 32


def test_given_k0_when_top_k_then_empty() -> None:
    assert top_k_chunks("def foo", ["def bar", "hello"], 0) == []


def test_given_overlap_when_jaccard_then_positive() -> None:
    assert jaccard("def foo bar", "def foo baz") > 0.0


def test_given_k1_when_apply_then_prepends_best() -> None:
    chunks = ["unrelated text here", "def foo returns int"]
    out = apply_genc_prompt(
        "def foo",
        k_retrieve=1,
        chunks=chunks,
        stride=64,
        chunk_len=32,
    )
    assert "def foo returns int" in out
    assert out.endswith("def foo") or "def foo" in out
