"""Contract: H-ZERR bank pairs + STAG′ story floor gate."""

from __future__ import annotations

from pathlib import Path

from zerr_ops import (
    HYPOTHESIS,
    MIN_BANK,
    STAG_TIP_LP,
    bank_qa_pairs,
    decide_hzerr,
    format_qa,
)


def test_given_error_rows_when_bank_qa_then_pairs() -> None:
    rows = [
        {
            "question": "Q1",
            "gold": "A1",
            "error": True,
            "score": 1.0,
        },
        {
            "question": "Q2",
            "gold": "A2",
            "error": False,
            "score": 9.0,
        },
        {
            "question": "Q3",
            "repaired": "A3",
            "error": False,
            "score": 5.0,
        },
    ]
    pairs = bank_qa_pairs(rows)
    assert pairs == [("Q1", "A1"), ("Q3", "A3")]


def test_given_format_qa_when_pack_then_qa_markers() -> None:
    text = format_qa("add?", "return a+b")
    assert text.startswith("Q: add?")
    assert "\nA: return a+b\n" in text


def test_given_story_ok_when_decide_then_promote() -> None:
    d = decide_hzerr(
        story_lp=-15.0,
        n_pairs=MIN_BANK,
        n_params=4_000_000,
        parent_story_lp=-15.3,
    )
    assert d == "PROMOTE"
    assert HYPOTHESIS == "H-ZERR"
    assert STAG_TIP_LP == -12.49


def test_given_story_drop_when_decide_then_kill() -> None:
    d = decide_hzerr(
        story_lp=-16.0,
        n_pairs=MIN_BANK,
        n_params=4_000_000,
        parent_story_lp=-15.0,
    )
    assert d.startswith("KILL")


def test_given_tiny_bank_when_decide_then_kill() -> None:
    d = decide_hzerr(
        story_lp=-12.0, n_pairs=3, n_params=1, parent_story_lp=-12.0
    )
    assert "bank pairs" in d


def test_given_train_zerr_when_toy_then_ckpt(tmp_path: Path) -> None:
    """CPU smoke: two CE steps on toy vocab student + fake tokenizer."""
    import torch
    from student_model import build_student
    from zerr_train import train_zerr

    class _Tok:
        def encode(self, text: str, return_tensors: str = "pt"):
            ids = [min(100, ord(c) % 50 + 1) for c in text[:32]] or [1, 2]
            return torch.tensor([ids], dtype=torch.long)

    device = torch.device("cpu")
    student = build_student(128).to(device)
    out = tmp_path / "HZERR.pt"
    meta = train_zerr(
        student=student,
        tok=_Tok(),
        pairs=[("q", "a")] * 10,
        device=device,
        steps=2,
        lr=1e-3,
        seed=0,
        out_path=out,
    )
    assert out.is_file()
    assert meta["n_pairs"] == 10
    assert meta["steps"] == 2
    assert meta["params"] <= 5_000_000
