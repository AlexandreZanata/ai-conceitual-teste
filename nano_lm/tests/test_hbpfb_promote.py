"""Contract: H-ABS-BPFB smoke+formal PROMOTE reports exist."""

from __future__ import annotations

from pathlib import Path

SMOKE = Path("docs/results/nano-lm/hbpfb-bpfb.md")
FORMAL = Path("docs/results/nano-lm/formal-hbpfb-bpfb.md")


def test_given_smoke_when_read_then_promote() -> None:
    assert SMOKE.is_file()
    text = SMOKE.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "bitcoin" in text.lower() or "BTC" in text
    assert "-15.3830" in text or "k=2" in text


def test_given_formal_when_read_then_promote() -> None:
    assert FORMAL.is_file()
    text = FORMAL.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "wall↓" in text or "wall" in text.lower()
    assert "-12.4097" in text or "-11.1616" in text
    assert "BTC" in text or "bitcoin" in text.lower()
