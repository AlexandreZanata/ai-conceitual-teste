"""Contract: H-TCACHE eligible-only code scoring uses fewer forwards."""

from __future__ import annotations

from tcache_ops import TeacherLpMemo
from tcache_score import commit_pfb_rows_naive, commit_pfb_rows_tcache


class _FakeTeacher:
    """Minimal LoadedModel stand-in for commit contracts."""

    def __init__(self) -> None:
        self.forwards = 0

    # unused by commit path when monkeypatched — keep shape only
    tokenizer = None
    device = None
    model = None


def test_given_low_elig_when_tcache_commit_then_fewer_forwards(
    monkeypatch: object,
) -> None:
    # GIVEN K=4 beams with 1 eligible WHEN tcache vs naive THEN forwards↓
    import tcache_score as ts

    calls: list[str] = []

    def fake_lp(teacher: object, prompt: str, cont: str) -> float:
        del teacher, prompt
        calls.append(cont)
        return -float(len(cont) + 1)

    monkeypatch.setattr(ts, "code_teacher_mean_logprob", fake_lp)
    monkeypatch.setattr(
        ts,
        "code_teacher_meta",
        lambda: {
            "hf_id": "fake",
            "params": 1,
            "license": "test",
            "tokenizer_id": "fake",
        },
    )
    bank = {
        "prompt": "def f():",
        "seed": 0,
        "parent_story": -10.0,
        "parent_cont": "pass",
        "parent_n_new": 1,
        "parent_wall_ms": 1.0,
        "conts": ["aaaa", "bb", "ccc", "dddd"],
        # floor = -10.05; only "bb" story -9.0 eligible
        "story_lps": [-12.0, -9.0, -12.0, -12.0],
        "wall_ms": 10.0,
        "n_news": [2, 2, 2, 2],
        "unique": 4.0,
        "k": 4.0,
    }
    parent_code = {("def f():", 0): -5.0}
    teacher = _FakeTeacher()
    _, naive_memo, _ = commit_pfb_rows_naive(
        teacher, [bank], parent_code_by_key=parent_code  # type: ignore[arg-type]
    )
    calls.clear()
    rows, tc_memo, _ = commit_pfb_rows_tcache(
        teacher, [bank], parent_code_by_key=parent_code  # type: ignore[arg-type]
    )
    assert naive_memo.forwards == 4
    assert tc_memo.forwards == 1
    assert tc_memo.forwards < naive_memo.forwards * 0.7
    assert rows[0]["switched"] == 1.0
    assert rows[0]["continuation"] == "bb"
