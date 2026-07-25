"""Contract: Wave W close-out summary documents PROG/BTC/MIXD/EFF decisions."""

from __future__ import annotations

from pathlib import Path

SUMMARY = Path("docs/results/nano-lm/wave-w-summary.md")


def test_given_summary_when_read_then_exists() -> None:
    assert SUMMARY.is_file(), "missing Wave W public summary"


def test_given_summary_when_read_then_wave_decisions() -> None:
    text = SUMMARY.read_text(encoding="utf-8")
    assert "COMPLETE" in text
    assert "PARK" in text or "PARKED" in text
    for needle in (
        "H-PROG",
        "H-BTC",
        "H-MIXD",
        "H-EFF",
        "PROMOTE",
        "KILL",
        "formal-hprog-programming",
        "formal-hbtc-bitcoin",
        "formal-heff-efficiency",
        "hmixd-mix",
    ):
        assert needle in text, f"missing {needle}"


def test_given_summary_when_read_then_no_train_mix_claim() -> None:
    text = SUMMARY.read_text(encoding="utf-8")
    assert "no train-mix" in text.lower() or "no train mix" in text.lower()
