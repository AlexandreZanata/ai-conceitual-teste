"""Contract: Wave AY2 H-SHIPAY — modes + intent ABSTAIN (pesquisa §5)."""

from __future__ import annotations

from shipay_ops import (
    APP_SMOKE_PACK,
    APP_SURFACES,
    HARD_NATURAL_ASK,
    INTENT_FP_ASK,
    REQUIRED_MODES,
    SHIPAY_CHARTER,
    SHIPAY_CLAIM,
    SHIPAY_ID,
    SHIPAY_PATHS,
    SHIPAY_THESIS,
    arms_honest_ok,
    attach_shipay,
    banner_modes_ok,
    content_matches_mode,
    core_modes_ok,
    decide_shipay,
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
    row = attach_shipay(
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
        row = attach_shipay(row)
    row["arm"] = arm
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
        attach_shipay(
            {
                "mode": "WRAP_LOOKUP",
                "product_mode": "LOOKUP",
                "completion": "def add(a, b):\n    return a + b",
                "wall_ms": 0,
                "n_new": 0,
                "question": "known",
            }
        ),
        attach_shipay(
            {
                "mode": "NO_ANSWER",
                "product_mode": "ABSTAIN",
                "completion": "NO_ANSWER",
                "wall_ms": 90,
                "n_new": 0,
                "question": "ood",
            }
        ),
        attach_shipay(
            {
                "mode": "SEMWRAP_LOOKUP",
                "product_mode": "LOOKUP",
                "completion": "def add(a, b):\n    return a + b",
                "wall_ms": 1.0,
                "n_new": 0,
                "question": HARD_NATURAL_ASK,
            }
        ),
        attach_shipay(
            {
                "mode": "NO_ANSWER",
                "product_mode": "ABSTAIN",
                "completion": "NO_ANSWER",
                "wall_ms": 1.0,
                "n_new": 0,
                "question": INTENT_FP_ASK,
            }
        ),
    ]


def _apps_ok() -> list[dict]:
    rows = []
    for surface in APP_SURFACES:
        row = attach_shipay(
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


def _decode_abstain() -> dict:
    return attach_shipay(
        {
            "arm": "DECODE_PROBE",
            "mode": "WRAP_DECODE",
            "product_mode": "DECODE",
            "completion": (
                "quickly and which,.Suddenly some \ufffd funny everything "
                "really carefully looking something"
            ),
            "wall_ms": 100.0,
            "n_new": 64,
        }
    )


def _near() -> dict:
    return attach_shipay(
        {
            "mode": "NO_ANSWER",
            "product_mode": "ABSTAIN",
            "completion": "NO_ANSWER",
            "wall_ms": 80,
            "n_new": 0,
        }
    )


def test_given_contract_when_constants_then_match_ay2() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AY2 — smoke + content · intent ABSTAIN
    assert SHIPAY_ID == "H-SHIPAY"
    assert REQUIRED_MODES == ("LOOKUP", "PEAK", "DECODE", "ABSTAIN")
    assert set(SHIPAY_PATHS) <= set(SHIPAY_CHARTER["paths"])
    assert SHIPAY_CHARTER.get("content_bars") is True
    assert SHIPAY_CHARTER.get("decode_usable_or_abstain") is True
    assert SHIPAY_CHARTER.get("hard_natural_labeled") is True
    assert SHIPAY_CHARTER.get("intent_fp_labeled_abstain") is True
    assert SHIPAY_CHARTER.get("regression_hold") is True
    assert SHIPAY_CHARTER.get("smoke") == "4/4"
    assert "PRODINT" in SHIPAY_THESIS or "intent" in SHIPAY_THESIS.lower()
    assert "gibberish-tail" in SHIPAY_CLAIM
    assert "Python helper" in HARD_NATURAL_ASK
    assert "mul" in INTENT_FP_ASK.lower()
    assert APP_SURFACES == ("known-ask", "howto", "long-doc")
    assert len(APP_SMOKE_PACK) == 3
    assert banner_modes_ok() is True
    cited = set(SHIPAY_CHARTER.get("cite_ay_locks") or [])
    assert {"H-PRODINT", "H-PRODNAT", "H-SHIPUX"} <= cited


def test_given_gibberish_decode_when_attach_then_abstain() -> None:
    row = _decode_abstain()
    assert row["product_mode"] == "ABSTAIN"
    assert row["completion"] == "NO_ANSWER"
    assert content_matches_mode(row) is True


def test_given_usable_decode_when_content_then_ok() -> None:
    row = attach_shipay(
        {
            "mode": "WRAP_DECODE",
            "product_mode": "DECODE",
            "completion": "Merkle trees hash leaf blocks upward into a root.",
            "wall_ms": 12.0,
            "n_new": 8,
        }
    )
    assert row["product_mode"] == "DECODE"
    assert content_matches_mode(row) is True


def test_given_arms_when_honest_then_core_modes() -> None:
    arms = _good_arms()
    assert arms_honest_ok(arms) is True
    assert core_modes_ok(arms) is True


def test_given_all_ok_when_decide_then_promote() -> None:
    out = decide_shipay(
        arms=_good_arms(),
        default_asks=_defaults(),
        apps=_apps_ok(),
        decode_probe=_decode_abstain(),
        near_miss=_near(),
        anti_fp_signed=True,
    )
    assert out.startswith("PROMOTE")
    assert SHIPAY_ID in out


def test_given_intent_fp_lookup_when_decide_then_kill() -> None:
    defaults = _defaults()
    for row in defaults:
        if row.get("question") == INTENT_FP_ASK:
            row["product_mode"] = "LOOKUP"
            row["completion"] = "def add(a, b):\n    return a + b"
            row["mode"] = "SEMWRAP_LOOKUP"
            row["modeui_line"] = (
                "mode=LOOKUP · wall_ms=1.0000 · n_new=0 · raw=SEMWRAP_LOOKUP"
            )
    out = decide_shipay(
        arms=_good_arms(),
        default_asks=defaults,
        apps=_apps_ok(),
        decode_probe=_decode_abstain(),
        near_miss=_near(),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "intent" in out.lower()


def test_given_hard_natural_abstain_when_decide_then_kill() -> None:
    defaults = _defaults()
    for row in defaults:
        if row.get("question") == HARD_NATURAL_ASK:
            row["product_mode"] = "ABSTAIN"
            row["completion"] = "NO_ANSWER"
            row["mode"] = "NO_ANSWER"
            row["modeui_line"] = (
                "mode=ABSTAIN · wall_ms=1.0000 · n_new=0 · raw=NO_ANSWER"
            )
    out = decide_shipay(
        arms=_good_arms(),
        default_asks=defaults,
        apps=_apps_ok(),
        decode_probe=_decode_abstain(),
        near_miss=_near(),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "hard-natural" in out.lower()


def test_given_gibberish_still_decode_when_decide_then_kill() -> None:
    bad = {
        "mode": "WRAP_DECODE",
        "product_mode": "DECODE",
        "completion": (
            "quickly and which,.Suddenly some \ufffd funny everything "
            "really carefully looking something"
        ),
        "wall_ms": 100.0,
        "n_new": 64,
        "modeui_line": (
            "mode=DECODE · wall_ms=100.0000 · n_new=64 · raw=WRAP_DECODE"
        ),
    }
    out = decide_shipay(
        arms=_good_arms(),
        default_asks=_defaults(),
        apps=_apps_ok(),
        decode_probe=bad,
        near_miss=_near(),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "DECODE" in out


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_shipay(
        arms=_good_arms(),
        default_asks=_defaults(),
        apps=_apps_ok(),
        decode_probe=_decode_abstain(),
        anti_fp_signed=False,
    )
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_missing_peak_when_decide_then_kill() -> None:
    arms = [a for a in _good_arms() if a["product_mode"] != "PEAK"]
    out = decide_shipay(
        arms=arms,
        default_asks=_defaults(),
        apps=_apps_ok(),
        decode_probe=_decode_abstain(),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")


def test_given_no_regression_hold_when_decide_then_kill() -> None:
    bad = dict(SHIPAY_CHARTER)
    bad["regression_hold"] = False
    out = decide_shipay(
        arms=_good_arms(),
        default_asks=_defaults(),
        apps=_apps_ok(),
        decode_probe=_decode_abstain(),
        charter=bad,
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "regression_hold" in out
