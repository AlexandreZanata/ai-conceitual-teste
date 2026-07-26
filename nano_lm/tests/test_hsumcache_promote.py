"""Contract: H-SUMCACHE smoke+formal PROMOTE at L_eff≥512."""

from __future__ import annotations

from pathlib import Path

SMOKE = Path("docs/results/nano-lm/hsumcache-sumcache.md")
FORMAL = Path("docs/results/nano-lm/formal-hsumcache-sumcache.md")


def test_given_smoke_when_read_then_promote() -> None:
    assert SMOKE.is_file()
    text = SMOKE.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "SUMCACHE" in text
    assert "L_eff" in text


def test_given_formal_when_read_then_promote() -> None:
    assert FORMAL.is_file()
    text = FORMAL.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "SUMCACHE" in text
    assert "-9.0751" in text or "code↑" in text
    assert "L_eff=522" in text or "active=352" in text
