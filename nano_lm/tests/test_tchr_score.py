"""Contract: code_teacher_lp aligns prompt/continuation under teacher BPE."""

from __future__ import annotations

from tchr_score import align_prompt_continuation, dual_means


class _PrefixTok:
    """Deterministic tokenizer where full text keeps prompt prefix ids."""

    def encode(self, text: str, add_special_tokens: bool = True) -> list[int]:
        ids = [ord(ch) % 97 + 1 for ch in text]
        if add_special_tokens:
            return [0] + ids
        return ids


def test_given_prompt_cont_when_align_then_prefix_match() -> None:
    tok = _PrefixTok()
    prompt_t, cont = align_prompt_continuation(tok, "ab", "cd")
    assert prompt_t.shape == (1, 3)  # bos + a + b
    assert cont == [ord("c") % 97 + 1, ord("d") % 97 + 1]


def test_given_dual_rows_when_means_then_averages() -> None:
    rows = [
        {
            "story_teacher_lp": -8.0,
            "code_teacher_lp": -4.0,
            "wall_ms": 10.0,
        },
        {
            "story_teacher_lp": -10.0,
            "code_teacher_lp": -6.0,
            "wall_ms": 30.0,
        },
    ]
    m = dual_means(rows)
    assert m["mean_story_lp"] == -9.0
    assert m["mean_code_lp"] == -5.0
    assert m["mean_wall_ms"] == 20.0
    assert m["n"] == 2.0
    assert m["n_code_finite"] == 2.0


def test_given_empty_when_means_then_nonfinite() -> None:
    m = dual_means([])
    assert m["n"] == 0.0
    assert m["mean_story_lp"] == float("-inf")
    assert m["mean_code_lp"] == float("-inf")
