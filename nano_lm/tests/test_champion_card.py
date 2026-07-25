"""
Contract: champion card documents tip-stack after TIPD (STAG′ official).
"""

from __future__ import annotations

from pathlib import Path

CARD = Path("docs/results/nano-lm/champion-card.md")


def test_given_card_when_read_then_official_tips_present() -> None:
    text = CARD.read_text(encoding="utf-8")
    for tip in ("H-STAG′", "H-EARLY", "H-POOL", "H-STAG"):
        assert tip in text, f"missing {tip}"
    assert "STAG_PRIME" in text or "TIPD" in text


def test_given_card_when_read_then_compose_kills_listed() -> None:
    text = CARD.read_text(encoding="utf-8")
    for hid in ("H-SYS", "H-JOINT", "H-CACHE", "H-CAP"):
        assert hid in text


def test_given_card_when_read_then_wave_v_parked() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-DOM" in text or "DOM" in text
    assert "COMPLETE" in text or "PARKED" in text
    assert "PROMOTE" in text


def test_given_card_when_read_then_hprog_promote() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-PROG" in text or "PROG" in text
    assert "formal-hprog-programming" in text
