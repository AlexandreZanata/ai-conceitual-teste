"""Contract: H-SCORERAM smoke+formal PROMOTE with warm wall↓."""

from __future__ import annotations

from pathlib import Path

SMOKE = Path("docs/results/nano-lm/hscoreram-scoreram.md")
FORMAL = Path("docs/results/nano-lm/formal-hscoreram-scoreram.md")


def test_given_smoke_when_read_then_promote() -> None:
    assert SMOKE.is_file()
    text = SMOKE.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "hit_rate" in text
    assert "SCORERAM" in text


def test_given_formal_when_read_then_promote() -> None:
    assert FORMAL.is_file()
    text = FORMAL.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "hit_rate=1.00" in text
    assert "-9.6759" in text or "-10.5426" in text
    assert "warm wall" in text.lower() or "wall↓" in text
