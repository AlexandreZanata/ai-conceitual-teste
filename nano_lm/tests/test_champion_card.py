"""
Contract: champion card documents tip-stack, Wave Y focus, and X+ summary pointer.
KILL catalog lives in wave-x-summary.md (not inline on the card).
"""

from __future__ import annotations

from pathlib import Path

CARD = Path("docs/results/nano-lm/champion-card.md")
WAVE_X = Path("docs/results/nano-lm/wave-x-summary.md")


def test_given_card_when_read_then_official_tips_present() -> None:
    text = CARD.read_text(encoding="utf-8")
    for tip in ("H-STAG′", "H-EARLY", "H-POOL", "H-STAG"):
        assert tip in text, f"missing {tip}"
    assert "STAG_PRIME" in text or "TIPD" in text


def test_given_card_when_read_then_compose_kills_listed() -> None:
    text = CARD.read_text(encoding="utf-8")
    for hid in ("H-SYS", "H-JOINT", "H-CACHE", "H-CAP"):
        assert hid in text


def test_given_card_when_read_then_wave_summaries() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "Wave W" in text and "COMPLETE" in text
    assert "wave-w-summary" in text
    assert "Wave X" in text and "wave-x-summary" in text
    assert "Wave Y" in text and "ACTIVE" in text
    assert "wave-y-summary" in text or "H-BEAMKV" in text
    assert "PROMOTE" in text


def test_given_card_when_read_then_domain_and_eff() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "formal-hprog-programming" in text
    assert "formal-hbtc-bitcoin" in text
    assert "formal-heff-efficiency" in text
    assert "MIXD" in text or "hmixd" in text


def test_given_card_when_read_then_xplus_promotes() -> None:
    text = CARD.read_text(encoding="utf-8")
    for needle in (
        "formal-htchr-code-teacher",
        "formal-hqt-quantize",
        "formal-hgenc-genome",
        "formal-hpfb-pfb",
        "formal-hqpfb2-qpfb2",
        "formal-hbpfb-bpfb",
        "formal-hgpfb4-gpfb4",
        "formal-hbeamkv-beamkv",
        "formal-htcache-tcache",
    ):
        assert needle in text, f"missing {needle}"
    assert "PROMOTE" in text


def test_given_card_when_read_then_points_archive_for_kills() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "archive/" in text
    assert "KILL" in text


def test_given_wave_x_summary_when_read_then_promotes_and_kills() -> None:
    assert WAVE_X.is_file()
    text = WAVE_X.read_text(encoding="utf-8")
    assert "COMPLETE" in text
    assert "Wave Y" in text
    for needle in (
        "H-TCHR",
        "H-QT",
        "H-GENC",
        "H-ABS-PFB",
        "H-ABS-QPFB2",
        "H-ABS-BPFB",
        "H-ABS-GPFB4",
        "PROMOTE",
        "KILL",
        "hrag-retrieve",
        "hctx-long-window",
        "hcbon-cbon",
        "hgpfb-gpfb",
    ):
        assert needle in text, f"missing {needle}"
