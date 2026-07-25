"""Contract: H-ABS-QPFB2 smoke+formal PROMOTE reports exist."""

from __future__ import annotations

from pathlib import Path

SMOKE = Path("docs/results/nano-lm/hqpfb2-qpfb2.md")
FORMAL = Path("docs/results/nano-lm/formal-hqpfb2-qpfb2.md")


def test_given_smoke_when_read_then_promote() -> None:
    assert SMOKE.is_file()
    text = SMOKE.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "wall" in text.lower()
    assert "QQPFB2" not in text
    assert "-14.6049" in text or "k=2" in text


def test_given_formal_when_read_then_promote() -> None:
    assert FORMAL.is_file()
    text = FORMAL.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "wall↓" in text or "wall" in text.lower()
    assert "-9.8159" in text or "-11.1390" in text
    assert "k=2" in text or "K=2" in text
