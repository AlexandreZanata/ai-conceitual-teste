"""Contract: H-GPFB4-LONG smoke+formal PROMOTE at K=4 on ROLL."""

from __future__ import annotations

from pathlib import Path

SMOKE = Path("docs/results/nano-lm/hgpfb4long-gpfb4long.md")
FORMAL = Path("docs/results/nano-lm/formal-hgpfb4long-gpfb4long.md")


def test_given_smoke_when_read_then_promote() -> None:
    assert SMOKE.is_file()
    text = SMOKE.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "GPFB4-LONG" in text
    assert "L_eff" in text
    assert "k=4" in text.lower() or "k=4" in text


def test_given_formal_when_read_then_promote() -> None:
    assert FORMAL.is_file()
    text = FORMAL.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "GPFB4-LONG" in text
    assert "wall" in text.lower()
    assert "ROLL" in text or "L_eff" in text
