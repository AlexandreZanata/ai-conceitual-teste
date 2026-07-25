"""Contract: H-ABS-QPFB smoke+formal PROMOTE reports exist."""

from __future__ import annotations

from pathlib import Path

SMOKE = Path("docs/results/nano-lm/hqpfb-qpfb.md")
FORMAL = Path("docs/results/nano-lm/formal-hqpfb-qpfb.md")


def test_given_smoke_when_read_then_promote() -> None:
    assert SMOKE.is_file()
    text = SMOKE.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "QQPFB" not in text
    assert "H-QT" in text or "int8" in text
    assert "-14.5449" in text or "switch" in text.lower()


def test_given_formal_when_read_then_promote() -> None:
    assert FORMAL.is_file()
    text = FORMAL.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "QQPFB" not in text
    assert "-9.6123" in text or "-10.5407" in text
    assert "int8" in text.lower()
