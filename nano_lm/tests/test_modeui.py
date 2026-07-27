"""Contract: Wave AQ5 H-MODEUI — mode-visible ship/demo (pesquisa §5)."""

from __future__ import annotations

from modeui_ops import (
    MODEUI_ID,
    MODEUI_THESIS,
    REQUIRED_MODES,
    attach_modeui,
    decide_modeui,
    demo_card_markdown,
    format_modeui_line,
    mode_visible,
    smoke_modes_ok,
)


def _row(arm: str, raw: str, wall: float, n_new: int) -> dict:
    return attach_modeui(
        {"arm": arm, "mode": raw, "wall_ms": wall, "n_new": n_new}
    )


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AQ5 — three modes visible · no unlabeled
    assert MODEUI_ID == "H-MODEUI"
    assert REQUIRED_MODES == ("LOOKUP", "PEAK", "DECODE")
    assert "mode=" in MODEUI_THESIS or "LOOKUP" in MODEUI_THESIS


def test_given_wrap_when_attach_then_lookup_visible() -> None:
    row = _row("LOOKUP", "WRAP_LOOKUP", 0.0, 0)
    assert row["product_mode"] == "LOOKUP"
    assert mode_visible(row)
    assert "mode=LOOKUP" in row["modeui_line"]


def test_given_peak_when_attach_then_peak_visible() -> None:
    row = _row("PEAK", "PEAK_FAST+GENBASE", 0.05, 12)
    assert row["product_mode"] == "PEAK"
    assert mode_visible(row)


def test_given_decode_when_attach_then_decode_visible() -> None:
    row = _row("DECODE", "QT+EARLY n=1", 20.0, 8)
    assert row["product_mode"] == "DECODE"
    assert mode_visible(row)


def test_given_empty_mode_when_attach_then_unknown_not_visible() -> None:
    row = attach_modeui({"mode": "", "wall_ms": 1.0, "n_new": 1})
    assert row["product_mode"] == "UNKNOWN"
    assert not mode_visible(row)


def test_given_three_arms_when_smoke_then_ok() -> None:
    rows = [
        _row("LOOKUP", "WRAP_LOOKUP", 0.0, 0),
        _row("PEAK", "PEAK_FAST+GENBASE", 0.1, 4),
        _row("DECODE", "WRAP_DECODE", 50.0, 16),
    ]
    assert smoke_modes_ok(rows)
    assert decide_modeui(rows=rows) == "PROMOTE"


def test_given_missing_peak_when_decide_then_kill() -> None:
    rows = [
        _row("LOOKUP", "WRAP_LOOKUP", 0.0, 0),
        _row("DECODE-A", "QT+EARLY n=1", 10.0, 4),
        _row("DECODE-B", "WRAP_DECODE", 12.0, 8),
    ]
    out = decide_modeui(rows=rows)
    assert out.startswith("KILL")


def test_given_unlabeled_when_decide_then_kill() -> None:
    rows = [
        _row("LOOKUP", "WRAP_LOOKUP", 0.0, 0),
        _row("PEAK", "PEAK_FAST+GENBASE", 0.1, 4),
        attach_modeui({"arm": "BAD", "mode": "", "wall_ms": 1.0, "n_new": 1}),
    ]
    out = decide_modeui(rows=rows)
    assert out.startswith("KILL")
    assert "unlabeled" in out or "UNKNOWN" in out


def test_given_rows_when_demo_card_then_contains_modes() -> None:
    rows = [
        _row("LOOKUP", "WRAP_LOOKUP", 0.0, 0),
        _row("PEAK", "PEAK_FAST+GENBASE", 0.1, 4),
        _row("DECODE", "QT+EARLY n=1", 20.0, 8),
    ]
    card = demo_card_markdown(rows)
    assert "mode=LOOKUP" in card
    assert "mode=PEAK" in card
    assert "mode=DECODE" in card
    assert format_modeui_line(
        product_mode="LOOKUP", wall_ms=0.0, n_new=0
    ).startswith("mode=LOOKUP")
