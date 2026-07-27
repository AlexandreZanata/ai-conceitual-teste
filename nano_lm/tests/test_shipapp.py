"""Contract: Wave AT2 H-SHIPAPP — ask · apps · ship/demo mode banners."""

from __future__ import annotations

from shipapp_ops import (
    APP_SMOKE_PACK,
    APP_SURFACES,
    REQUIRED_MODES,
    SHIPAPP_CHARTER,
    SHIPAPP_CLAIM,
    SHIPAPP_ID,
    SHIPAPP_PATHS,
    SHIPAPP_THESIS,
    apps_labeled,
    attach_shipapp,
    charter_ok,
    decide_shipapp,
    demo_card_markdown,
    mode_visible,
)


def _arm(arm: str, raw: str, wall: float = 1.0, n_new: int = 1) -> dict:
    row = attach_shipapp(
        {"arm": arm, "mode": raw, "wall_ms": wall, "n_new": n_new}
    )
    return row


def _apps_ok() -> list[dict]:
    rows = []
    for surface in APP_SURFACES:
        row = attach_shipapp(
            {
                "app_id": surface,
                "mode": "WRAP_LOOKUP",
                "wall_ms": 0.0,
                "n_new": 0,
            }
        )
        rows.append(row)
    return rows


def test_given_contract_when_constants_then_match_at2() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AT2 — smoke 4/4 · no unlabeled
    assert SHIPAPP_ID == "H-SHIPAPP"
    assert REQUIRED_MODES == ("LOOKUP", "PEAK", "DECODE", "ABSTAIN")
    assert set(SHIPAPP_PATHS) <= set(SHIPAPP_CHARTER["paths"])
    assert charter_ok()
    assert "apps" in SHIPAPP_THESIS.lower() or "ship" in SHIPAPP_THESIS.lower()
    assert "not open chat" in SHIPAPP_CLAIM.lower()
    assert APP_SURFACES == ("known-ask", "howto", "long-doc")
    assert len(APP_SMOKE_PACK) == 3


def test_given_four_arms_and_apps_when_decide_then_promote() -> None:
    arms = [
        _arm("LOOKUP", "WRAP_LOOKUP", 0.0, 0),
        _arm("PEAK", "PEAK_FAST+GENBASE", 0.02, 3),
        _arm("DECODE", "QT+EARLY n=1", 12.0, 8),
        _arm("ABSTAIN", "NO_ANSWER", 100.0, 64),
    ]
    # Force ABSTAIN product_mode for NO_ANSWER path
    arms[3] = attach_shipapp(
        {
            "arm": "ABSTAIN",
            "mode": "NO_ANSWER",
            "product_mode": "ABSTAIN",
            "wall_ms": 100.0,
            "n_new": 64,
        }
    )
    defaults = [
        attach_shipapp(
            {"mode": "WRAP_LOOKUP", "product_mode": "LOOKUP", "wall_ms": 0, "n_new": 0}
        ),
        attach_shipapp(
            {
                "mode": "NO_ANSWER",
                "product_mode": "ABSTAIN",
                "wall_ms": 90,
                "n_new": 64,
            }
        ),
    ]
    assert decide_shipapp(
        arms=arms, default_asks=defaults, apps=_apps_ok()
    ) == "PROMOTE"


def test_given_unlabeled_app_when_decide_then_kill() -> None:
    arms = [
        _arm("LOOKUP", "WRAP_LOOKUP", 0.0, 0),
        _arm("PEAK", "PEAK_FAST", 0.02, 3),
        _arm("DECODE", "QT+EARLY n=1", 12.0, 8),
        attach_shipapp(
            {
                "arm": "ABSTAIN",
                "mode": "NO_ANSWER",
                "product_mode": "ABSTAIN",
                "wall_ms": 100.0,
                "n_new": 64,
            }
        ),
    ]
    defaults = [
        attach_shipapp(
            {"mode": "WRAP_LOOKUP", "product_mode": "LOOKUP", "wall_ms": 0, "n_new": 0}
        ),
        attach_shipapp(
            {
                "mode": "NO_ANSWER",
                "product_mode": "ABSTAIN",
                "wall_ms": 90,
                "n_new": 64,
            }
        ),
    ]
    bad_apps = [
        {"app_id": "known-ask", "product_mode": "LOOKUP", "modeui_line": ""},
        {"app_id": "howto", "product_mode": "LOOKUP", "modeui_line": "mode=LOOKUP"},
        {"app_id": "long-doc", "product_mode": "LOOKUP", "modeui_line": "mode=LOOKUP"},
    ]
    out = decide_shipapp(arms=arms, default_asks=defaults, apps=bad_apps)
    assert out.startswith("KILL")
    assert "apps" in out


def test_given_incomplete_charter_when_decide_then_kill() -> None:
    arms = [
        _arm("LOOKUP", "WRAP_LOOKUP", 0.0, 0),
        _arm("PEAK", "PEAK_FAST", 0.02, 3),
        _arm("DECODE", "QT+EARLY n=1", 12.0, 8),
        attach_shipapp(
            {
                "arm": "ABSTAIN",
                "mode": "NO_ANSWER",
                "product_mode": "ABSTAIN",
                "wall_ms": 100.0,
                "n_new": 64,
            }
        ),
    ]
    defaults = [
        attach_shipapp(
            {"mode": "WRAP_LOOKUP", "product_mode": "LOOKUP", "wall_ms": 0, "n_new": 0}
        ),
        attach_shipapp(
            {
                "mode": "NO_ANSWER",
                "product_mode": "ABSTAIN",
                "wall_ms": 90,
                "n_new": 64,
            }
        ),
    ]
    bad = dict(SHIPAPP_CHARTER)
    bad["paths"] = ["nano:z:ask"]
    out = decide_shipapp(
        arms=arms, default_asks=defaults, apps=_apps_ok(), charter=bad
    )
    assert out.startswith("KILL")
    assert "charter" in out


def test_given_apps_when_labeled_then_pass() -> None:
    assert apps_labeled(_apps_ok())
    assert not apps_labeled(_apps_ok()[:1])


def test_given_rows_when_demo_then_includes_apps_and_arms() -> None:
    arms = [_arm("LOOKUP", "WRAP_LOOKUP", 0.0, 0)]
    body = demo_card_markdown(arms=arms, apps=_apps_ok())
    assert "SHIPAPP" in body
    assert "known-ask" in body
    assert "mode=LOOKUP" in body
    assert mode_visible(arms[0])
