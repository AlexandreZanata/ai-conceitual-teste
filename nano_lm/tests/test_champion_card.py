"""
Contract: champion card documents tip-stack protocol after park.
"""

from __future__ import annotations

from pathlib import Path

CARD = Path("docs/results/nano-lm/champion-card.md")


def test_given_park_when_read_card_then_tips_present():
    text = CARD.read_text(encoding="utf-8")
    for tip in ("H-STAG", "H-EARLY", "H-POOL", "PARKED"):
        assert tip in text, f"missing {tip}"


def test_given_card_when_read_then_compose_kills_listed():
    text = CARD.read_text(encoding="utf-8")
    for hid in ("H-SYS", "H-JOINT", "H-CACHE", "H-CAP"):
        assert hid in text
