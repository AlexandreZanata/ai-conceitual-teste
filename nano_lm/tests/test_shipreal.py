"""Contract: Wave AU2 H-SHIPREAL — modes + content match claim (pesquisa §5)."""

from __future__ import annotations

from shipreal_ops import (
    APP_SMOKE_PACK,
    APP_SURFACES,
    REQUIRED_MODES,
    SHIPREAL_CHARTER,
    SHIPREAL_CLAIM,
    SHIPREAL_ID,
    SHIPREAL_PATHS,
    SHIPREAL_THESIS,
    apps_content_ok,
    arms_content_ok,
    attach_shipreal,
    content_matches_mode,
    decide_shipreal,
)


def _arm(
    arm: str,
    raw: str,
    *,
    completion: str,
    wall: float = 1.0,
    n_new: int = 1,
    product_mode: str | None = None,
) -> dict:
    row = attach_shipreal(
        {
            "arm": arm,
            "mode": raw,
            "completion": completion,
            "wall_ms": wall,
            "n_new": n_new,
        }
    )
    if product_mode:
        row["product_mode"] = product_mode
        row = attach_shipreal(row)
    return row


def _good_arms() -> list[dict]:
    return [
        _arm(
            "LOOKUP",
            "WRAP_LOOKUP",
            completion="def add(a, b):\n    return a + b",
            wall=0.0,
            n_new=0,
        ),
        _arm(
            "PEAK",
            "PEAK_FAST+GENBASE",
            completion=(
                "Ownership is a set of rules that govern how a Rust "
                "program manages memory."
            ),
            wall=0.02,
            n_new=12,
        ),
        _arm(
            "DECODE",
            "QT+EARLY n=1",
            completion="Merkle trees hash leaf blocks upward.",
            wall=12.0,
            n_new=8,
        ),
        _arm(
            "ABSTAIN",
            "NO_ANSWER",
            completion="NO_ANSWER",
            wall=100.0,
            n_new=0,
            product_mode="ABSTAIN",
        ),
    ]


def _defaults() -> list[dict]:
    return [
        attach_shipreal(
            {
                "mode": "WRAP_LOOKUP",
                "product_mode": "LOOKUP",
                "completion": "def add(a, b):\n    return a + b",
                "wall_ms": 0,
                "n_new": 0,
            }
        ),
        attach_shipreal(
            {
                "mode": "NO_ANSWER",
                "product_mode": "ABSTAIN",
                "completion": "NO_ANSWER",
                "wall_ms": 90,
                "n_new": 0,
            }
        ),
    ]


def _apps_ok() -> list[dict]:
    rows = []
    for surface in APP_SURFACES:
        row = attach_shipreal(
            {
                "app_id": surface,
                "mode": "WRAP_LOOKUP",
                "product_mode": "LOOKUP",
                "completion": "def add(a, b):\n    return a + b",
                "wall_ms": 0.0,
                "n_new": 0,
            }
        )
        rows.append(row)
    return rows


def test_given_contract_when_constants_then_match_au2() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AU2 — smoke + content bars
    assert SHIPREAL_ID == "H-SHIPREAL"
    assert REQUIRED_MODES == ("LOOKUP", "PEAK", "DECODE", "ABSTAIN")
    assert set(SHIPREAL_PATHS) <= set(SHIPREAL_CHARTER["paths"])
    assert SHIPREAL_CHARTER.get("content_bars") is True
    assert "content" in SHIPREAL_THESIS.lower() or "match" in SHIPREAL_THESIS.lower()
    assert "snippet-prefix" in SHIPREAL_CLAIM
    assert APP_SURFACES == ("known-ask", "howto", "long-doc")
    assert len(APP_SMOKE_PACK) == 3


def test_given_lookup_peak_decode_abstain_when_content_then_ok() -> None:
    arms = _good_arms()
    assert all(content_matches_mode(r) for r in arms)
    assert arms_content_ok(arms)
    assert apps_content_ok(_apps_ok())


def test_given_gibberish_peak_when_content_then_fail() -> None:
    bad = _arm(
        "PEAK",
        "PEAK_FAST+GENBASE",
        completion="mory while running",
        wall=0.02,
        n_new=3,
    )
    assert content_matches_mode(bad) is False


def test_given_period_decode_when_content_then_fail() -> None:
    bad = _arm(
        "DECODE",
        "QT+EARLY n=1",
        completion="........",
        wall=12.0,
        n_new=8,
    )
    assert content_matches_mode(bad) is False


def test_given_gibberish_decode_when_content_then_fail() -> None:
    # GIVEN/WHEN/THEN: AV1 DECODE debt — TinyStories sludge ≠ content_ok
    bad = _arm(
        "DECODE",
        "WRAP_DECODE",
        completion=(
            "quickly and which,.Suddenly some \ufffd -So one Suddenly "
            "funny to at m m\ufffd. an set funny almost wasn really this. "
            "m everything; really everything\ufffd; some carefully "
        ),
        wall=103.0,
        n_new=64,
    )
    assert content_matches_mode(bad) is False


def test_given_all_ok_when_decide_then_promote() -> None:
    near = attach_shipreal(
        {
            "mode": "NO_ANSWER",
            "product_mode": "ABSTAIN",
            "completion": "NO_ANSWER",
            "wall_ms": 0,
            "n_new": 0,
        }
    )
    out = decide_shipreal(
        arms=_good_arms(),
        default_asks=_defaults(),
        apps=_apps_ok(),
        near_miss=near,
        anti_fp_signed=True,
    )
    assert out.startswith("PROMOTE")
    assert SHIPREAL_ID in out


def test_given_near_miss_lookup_when_decide_then_kill() -> None:
    near = attach_shipreal(
        {
            "mode": "SEMWRAP_LOOKUP",
            "product_mode": "LOOKUP",
            "completion": "CS = ENT / 32",
            "wall_ms": 0,
            "n_new": 0,
        }
    )
    out = decide_shipreal(
        arms=_good_arms(),
        default_asks=_defaults(),
        apps=_apps_ok(),
        near_miss=near,
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "near-miss" in out


def test_given_bad_peak_content_when_decide_then_kill() -> None:
    arms = _good_arms()
    arms[1] = _arm(
        "PEAK",
        "PEAK_FAST+GENBASE",
        completion="mory while running",
        wall=0.02,
        n_new=3,
    )
    near = attach_shipreal(
        {
            "mode": "NO_ANSWER",
            "product_mode": "ABSTAIN",
            "completion": "NO_ANSWER",
            "wall_ms": 0,
            "n_new": 0,
        }
    )
    out = decide_shipreal(
        arms=arms,
        default_asks=_defaults(),
        apps=_apps_ok(),
        near_miss=near,
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "content" in out


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_shipreal(
        arms=_good_arms(),
        default_asks=_defaults(),
        apps=_apps_ok(),
        anti_fp_signed=False,
    )
    assert out.startswith("KILL")
    assert "anti-FP" in out
