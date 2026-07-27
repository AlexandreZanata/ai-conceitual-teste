"""Contract: Wave AS6 H-SHIPUI — 4/4 modes on ask + ship/demo."""

from __future__ import annotations

from shipui_ops import (
    REQUIRED_MODES,
    SHIPUI_ID,
    SHIPUI_THESIS,
    attach_shipui,
    decide_shipui,
    default_ask_labeled,
    demo_card_markdown,
    mode_visible,
    smoke_modes_ok,
)


def _row(arm: str, raw: str, wall: float, n_new: int) -> dict:
    return attach_shipui(
        {"arm": arm, "mode": raw, "wall_ms": wall, "n_new": n_new}
    )


def test_given_contract_when_constants_then_four_modes() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AS6 — 4/4 visible · no unlabeled
    assert SHIPUI_ID == "H-SHIPUI"
    assert REQUIRED_MODES == ("LOOKUP", "PEAK", "DECODE", "ABSTAIN")
    assert "ASKABSTAIN" in SHIPUI_THESIS or "default" in SHIPUI_THESIS


def test_given_wrap_when_attach_then_lookup_visible() -> None:
    row = _row("LOOKUP", "WRAP_LOOKUP", 0.0, 0)
    assert row["product_mode"] == "LOOKUP"
    assert mode_visible(row)
    assert "mode=LOOKUP" in row["modeui_line"]


def test_given_no_answer_when_attach_then_abstain_visible() -> None:
    row = attach_shipui(
        {
            "arm": "ABSTAIN",
            "mode": "NO_ANSWER",
            "product_mode": "ABSTAIN",
            "completion": "NO_ANSWER",
            "wall_ms": 99.0,
            "n_new": 64,
        }
    )
    assert row["product_mode"] == "ABSTAIN"
    assert mode_visible(row)


def test_given_default_ask_when_labeled_then_true() -> None:
    payload = attach_shipui(
        {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    )
    assert default_ask_labeled(payload) is True
    assert default_ask_labeled({"mode": "WRAP_LOOKUP"}) is False


def test_given_four_arms_when_decide_then_promote() -> None:
    rows = [
        _row("LOOKUP", "WRAP_LOOKUP", 0.0, 0),
        _row("PEAK", "PEAK_FAST+GENBASE", 0.1, 4),
        _row("DECODE", "WRAP_DECODE", 50.0, 16),
        attach_shipui(
            {
                "arm": "ABSTAIN",
                "mode": "NO_ANSWER",
                "product_mode": "ABSTAIN",
                "wall_ms": 12.0,
                "n_new": 8,
            }
        ),
    ]
    defaults = [
        attach_shipui({"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}),
        attach_shipui(
            {
                "mode": "NO_ANSWER",
                "product_mode": "ABSTAIN",
                "wall_ms": 10.0,
                "n_new": 8,
            }
        ),
    ]
    assert smoke_modes_ok(rows)
    assert decide_shipui(rows=rows, default_asks=defaults) == "PROMOTE"


def test_given_unlabeled_default_when_decide_then_kill() -> None:
    rows = [
        _row("LOOKUP", "WRAP_LOOKUP", 0.0, 0),
        _row("PEAK", "PEAK_FAST+GENBASE", 0.1, 4),
        _row("DECODE", "WRAP_DECODE", 50.0, 16),
        attach_shipui(
            {
                "arm": "ABSTAIN",
                "mode": "NO_ANSWER",
                "product_mode": "ABSTAIN",
                "wall_ms": 12.0,
                "n_new": 8,
            }
        ),
    ]
    out = decide_shipui(rows=rows, default_asks=[{"mode": "WRAP_LOOKUP"}])
    assert out.startswith("KILL")
    assert "default ask" in out


def test_given_missing_mode_when_decide_then_kill() -> None:
    rows = [
        _row("LOOKUP", "WRAP_LOOKUP", 0.0, 0),
        _row("PEAK", "PEAK_FAST+GENBASE", 0.1, 4),
        _row("DECODE-A", "QT+EARLY n=1", 10.0, 4),
        _row("DECODE-B", "WRAP_DECODE", 12.0, 8),
    ]
    assert decide_shipui(rows=rows).startswith("KILL")


def test_given_rows_when_demo_card_then_contains_all_modes() -> None:
    rows = [
        _row("LOOKUP", "WRAP_LOOKUP", 0.0, 0),
        _row("PEAK", "PEAK_FAST+GENBASE", 0.1, 4),
        _row("DECODE", "QT+EARLY n=1", 20.0, 8),
        attach_shipui(
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
    assert "mode=ABSTAIN" in card
