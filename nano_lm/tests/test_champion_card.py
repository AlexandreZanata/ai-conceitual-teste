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


def test_given_card_when_read_then_hbtc_smoke() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-BTC" in text or "BTC" in text
    assert "formal-hbtc-bitcoin" in text


def test_given_card_when_read_then_hmixd_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-MIXD" in text or "MIXD" in text
    assert "KILL" in text
    assert "hmixd-mix" in text or "formal-hmixd" in text


def test_given_card_when_read_then_wave_w_complete() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "Wave W" in text
    assert "COMPLETE" in text
    assert "wave-w-summary" in text
    assert "Wave X" in text
    assert "ACTIVE" in text or "PARKED" in text


def test_given_card_when_read_then_heff_formal() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-EFF" in text or "EFF" in text
    assert "formal-heff-efficiency" in text
    assert "PROMOTE" in text


def test_given_card_when_read_then_htchr_promote() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-TCHR" in text or "TCHR" in text
    assert "formal-htchr-code-teacher" in text
    assert "PROMOTE" in text
