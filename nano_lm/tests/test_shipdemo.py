"""Contract: Wave AR2 H-SHIPDEMO — four modes visible (pesquisa §5)."""

from __future__ import annotations

from shipdemo_ops import (
    REQUIRED_MODES,
    SHIPDEMO_ID,
    SHIPDEMO_THESIS,
    attach_shipdemo,
    decide_shipdemo,
    demo_card_markdown,
    mode_visible,
    smoke_modes_ok,
)


def _row(arm: str, raw: str, wall: float, n_new: int) -> dict:
    return attach_shipdemo(
        {"arm": arm, "mode": raw, "wall_ms": wall, "n_new": n_new}
    )


def test_given_contract_when_constants_then_four_modes() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AR2 — LOOKUP|PEAK|DECODE|ABSTAIN visible
    assert SHIPDEMO_ID == "H-SHIPDEMO"
    assert REQUIRED_MODES == ("LOOKUP", "PEAK", "DECODE", "ABSTAIN")
    assert "ABSTAIN" in SHIPDEMO_THESIS


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


def test_given_no_answer_when_attach_then_abstain_visible() -> None:
    row = attach_shipdemo(
        {
            "arm": "ABSTAIN",
            "mode": "NO_ANSWER",
            "product_mode": "ABSTAIN",
            "completion": "NO_ANSWER",
            "wall_ms": 11.0,
            "n_new": 8,
        }
    )
    assert row["product_mode"] == "ABSTAIN"
    assert mode_visible(row)
    assert "mode=ABSTAIN" in row["modeui_line"]


def test_given_empty_mode_when_attach_then_unknown_not_visible() -> None:
    row = attach_shipdemo({"mode": "", "wall_ms": 1.0, "n_new": 1})
    assert row["product_mode"] == "UNKNOWN"
    assert not mode_visible(row)


def test_given_four_arms_when_smoke_then_ok() -> None:
    rows = [
        _row("LOOKUP", "WRAP_LOOKUP", 0.0, 0),
        _row("PEAK", "PEAK_FAST+GENBASE", 0.1, 4),
        _row("DECODE", "WRAP_DECODE", 50.0, 16),
        attach_shipdemo(
            {
                "arm": "ABSTAIN",
                "mode": "NO_ANSWER",
                "product_mode": "ABSTAIN",
                "wall_ms": 12.0,
                "n_new": 8,
            }
        ),
    ]
    assert smoke_modes_ok(rows)
    assert decide_shipdemo(rows=rows) == "PROMOTE"


def test_given_missing_abstain_when_decide_then_kill() -> None:
    rows = [
        _row("LOOKUP", "WRAP_LOOKUP", 0.0, 0),
        _row("PEAK", "PEAK_FAST+GENBASE", 0.1, 4),
        _row("DECODE-A", "QT+EARLY n=1", 10.0, 4),
        _row("DECODE-B", "WRAP_DECODE", 12.0, 8),
    ]
    out = decide_shipdemo(rows=rows)
    assert out.startswith("KILL")


def test_given_three_arms_when_decide_then_kill() -> None:
    rows = [
        _row("LOOKUP", "WRAP_LOOKUP", 0.0, 0),
        _row("PEAK", "PEAK_FAST+GENBASE", 0.1, 4),
        _row("DECODE", "QT+EARLY n=1", 10.0, 4),
    ]
    out = decide_shipdemo(rows=rows)
    assert out.startswith("KILL")
    assert "4 smoke" in out


def test_given_rows_when_demo_card_then_contains_all_modes() -> None:
    rows = [
        _row("LOOKUP", "WRAP_LOOKUP", 0.0, 0),
        _row("PEAK", "PEAK_FAST+GENBASE", 0.1, 4),
        _row("DECODE", "QT+EARLY n=1", 20.0, 8),
        attach_shipdemo(
            {
                "arm": "ABSTAIN",
                "mode": "NO_ANSWER",
                "product_mode": "ABSTAIN",
                "wall_ms": 11.0,
                "n_new": 8,
            }
        ),
    ]
    card = demo_card_markdown(rows)
    assert "mode=LOOKUP" in card
    assert "mode=PEAK" in card
    assert "mode=DECODE" in card
    assert "mode=ABSTAIN" in card
    assert "ABSTAIN" in card
