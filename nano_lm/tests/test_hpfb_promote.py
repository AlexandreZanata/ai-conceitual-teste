"""Contract: H-ABS-PFB smoke+formal PROMOTE reports exist with dual-gate win."""

from __future__ import annotations

from pathlib import Path

SMOKE = Path("docs/results/nano-lm/hpfb-pfb.md")
FORMAL = Path("docs/results/nano-lm/formal-hpfb-pfb.md")


def test_given_smoke_when_read_then_promote() -> None:
    assert SMOKE.is_file()
    text = SMOKE.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "parent" in text.lower()
    assert "-14.6921" in text or "switch" in text.lower()


def test_given_formal_when_read_then_promote() -> None:
    assert FORMAL.is_file()
    text = FORMAL.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "story" in text.lower()
    assert "-9.9450" in text or "-10.3778" in text
    assert "CSAFE" in text or "parent" in text.lower()
