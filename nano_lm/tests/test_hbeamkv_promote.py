"""Contract: H-BEAMKV smoke+formal PROMOTE reports exist with wall↓."""

from __future__ import annotations

from pathlib import Path

SMOKE = Path("docs/results/nano-lm/hbeamkv-beamkv.md")
FORMAL = Path("docs/results/nano-lm/formal-hbeamkv-beamkv.md")


def test_given_smoke_when_read_then_promote() -> None:
    assert SMOKE.is_file()
    text = SMOKE.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "wall" in text.lower()
    assert "BEAMKV" in text
    assert "indep" in text.lower() or "shared" in text.lower()


def test_given_formal_when_read_then_promote() -> None:
    assert FORMAL.is_file()
    text = FORMAL.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "wall↓" in text or "wall" in text.lower()
    assert "-9.7655" in text or "-10.4274" in text
    assert "shared" in text.lower()
