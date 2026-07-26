"""Contract: Wave AA3 H-ZPREF — prefer gold≻raw; story≥parent−ε; wrap verify."""

from __future__ import annotations

from pathlib import Path

from zpref_ops import (
    DEFAULT_REJECTED,
    HYPOTHESIS,
    MIN_BANK_ROWS,
    MIN_PREF,
    STAG_TIP_LP,
    bank_pref_pairs,
    decide_hzpref,
    format_qa,
)


def test_given_bank_when_pref_then_gold_over_raw() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9.6 / §8.1 AA3 — gold≻model_raw
    rows = [
        {
            "question": "Q1",
            "gold": "good",
            "model_raw": "........",
            "error": True,
            "score": 1.0,
        },
        {
            "question": "Q2",
            "gold": "also",
            "model_raw": "",
            "error": False,
            "score": 9.0,
        },
        {
            "question": "Q3",
            "gold": "same",
            "model_raw": "same",
            "error": True,
            "score": 1.0,
        },
    ]
    pairs = bank_pref_pairs(rows)
    assert ("Q1", "good", "........") in pairs
    assert ("Q2", "also", DEFAULT_REJECTED) in pairs
    assert not any(p[0] == "Q3" for p in pairs)


def test_given_format_when_pack_then_qa_markers() -> None:
    text = format_qa("add?", "return a+b")
    assert text.startswith("Q: add?")
    assert "\nA: return a+b\n" in text


def test_given_story_ok_wrap_ok_when_decide_then_promote() -> None:
    d = decide_hzpref(
        story_lp=-15.0,
        n_pairs=MIN_PREF,
        n_bank_rows=MIN_BANK_ROWS,
        n_params=4_000_000,
        parent_story_lp=-15.3,
        wrap_ok=True,
    )
    assert d == "PROMOTE"
    assert HYPOTHESIS == "H-ZPREF"
    assert STAG_TIP_LP == -12.49


def test_given_story_drop_when_decide_then_kill() -> None:
    d = decide_hzpref(
        story_lp=-16.0,
        n_pairs=MIN_PREF,
        n_bank_rows=MIN_BANK_ROWS,
        n_params=4_000_000,
        parent_story_lp=-15.0,
        wrap_ok=True,
    )
    assert d.startswith("KILL")


def test_given_small_bank_when_decide_then_kill() -> None:
    d = decide_hzpref(
        story_lp=-12.0,
        n_pairs=MIN_PREF,
        n_bank_rows=10,
        n_params=1,
        parent_story_lp=-12.0,
        wrap_ok=True,
    )
    assert "bank rows" in d


def test_given_wrap_fail_when_decide_then_kill() -> None:
    d = decide_hzpref(
        story_lp=-15.0,
        n_pairs=MIN_PREF,
        n_bank_rows=MIN_BANK_ROWS,
        n_params=1,
        parent_story_lp=-15.0,
        wrap_ok=False,
    )
    assert "wrap" in d.lower()


def test_given_train_zpref_when_toy_then_ckpt(tmp_path: Path) -> None:
    """CPU smoke: two rank steps on toy student + fake tokenizer."""
    import torch
    from student_model import build_student
    from zpref_train import train_zpref

    class _Tok:
        def encode(self, text: str, return_tensors: str = "pt"):
            ids = [min(100, ord(c) % 50 + 1) for c in text[:32]] or [1, 2]
            return torch.tensor([ids], dtype=torch.long)

    device = torch.device("cpu")
    student = build_student(128).to(device)
    out = tmp_path / "HZPREF.pt"
    meta = train_zpref(
        student=student,
        tok=_Tok(),
        pairs=[("q", "gold ans", "........")] * 10,
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
    assert meta["hypothesis"] == HYPOTHESIS
