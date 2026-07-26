"""Contract: H-PFB256 smoke+formal PROMOTE at L=256."""

from __future__ import annotations

from pathlib import Path

SMOKE = Path("docs/results/nano-lm/hpfb256-pfb256.md")
FORMAL = Path("docs/results/nano-lm/formal-hpfb256-pfb256.md")


def test_given_smoke_when_read_then_promote() -> None:
    assert SMOKE.is_file()
    text = SMOKE.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "PFB256" in text
    assert "wall@256" in text or "@256" in text


def test_given_formal_when_read_then_promote() -> None:
    assert FORMAL.is_file()
    text = FORMAL.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "PFB256" in text
    assert "-9.2219" in text or "code↑" in text
    assert "256" in text
