"""Contract: H-ROLL smoke+formal PROMOTE with L_eff≫W."""

from __future__ import annotations

from pathlib import Path

SMOKE = Path("docs/results/nano-lm/hroll-roll.md")
FORMAL = Path("docs/results/nano-lm/formal-hroll-roll.md")


def test_given_smoke_when_read_then_promote() -> None:
    assert SMOKE.is_file()
    text = SMOKE.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "ROLL" in text
    assert "L_eff" in text


def test_given_formal_when_read_then_promote() -> None:
    assert FORMAL.is_file()
    text = FORMAL.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "ROLL" in text
    assert "-10.0072" in text or "code↑" in text
    assert "L_eff=394" in text or "active=123" in text
