"""Contract: Wave AZ2 H-SHIPAZ — modes + held-out/over-refuse (pesquisa §5)."""

from __future__ import annotations

from shipaz_ops import (
    APP_SMOKE_PACK,
    APP_SURFACES,
    HARD_NATURAL_ASK,
    HELDOUT_FP_ASK,
    NAMED_INTENT_ASK,
    OVERREFUSE_ASK,
    REQUIRED_MODES,
    SHIPAZ_CHARTER,
    SHIPAZ_CLAIM,
    SHIPAZ_ID,
    SHIPAZ_PATHS,
    SHIPAZ_THESIS,
    arms_honest_ok,
    attach_shipaz,
    banner_modes_ok,
    content_matches_mode,
    core_modes_ok,
    decide_shipaz,
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
    row = attach_shipaz(
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
        row = attach_shipaz(row)
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
        attach_shipaz(
            {
                "mode": "WRAP_LOOKUP",
                "product_mode": "LOOKUP",
                "completion": "def add(a, b):\n    return a + b",
                "wall_ms": 0,
                "n_new": 0,
                "question": "known",
            }
        ),
        attach_shipaz(
            {
                "mode": "NO_ANSWER",
                "product_mode": "ABSTAIN",
                "completion": "NO_ANSWER",
                "wall_ms": 90,
                "n_new": 0,
                "question": "ood",
            }
        ),
        attach_shipaz(
            {
                "mode": "SEMWRAP_LOOKUP",
                "product_mode": "LOOKUP",
                "completion": "def add(a, b):\n    return a + b",
                "wall_ms": 1.0,
                "n_new": 0,
                "question": HARD_NATURAL_ASK,
            }
        ),
        attach_shipaz(
            {
                "mode": "NO_ANSWER",
                "product_mode": "ABSTAIN",
                "completion": "NO_ANSWER",
                "wall_ms": 1.0,
                "n_new": 0,
                "question": NAMED_INTENT_ASK,
            }
        ),
        attach_shipaz(
            {
                "mode": "NO_ANSWER",
                "product_mode": "ABSTAIN",
                "completion": "NO_ANSWER",
                "wall_ms": 1.0,
                "n_new": 0,
                "question": HELDOUT_FP_ASK,
            }
        ),
        attach_shipaz(
            {
                "mode": "WRAP_LOOKUP",
                "product_mode": "LOOKUP",
                "completion": "a.clear()",
                "wall_ms": 0.0,
                "n_new": 0,
                "question": OVERREFUSE_ASK,
            }
        ),
    ]


def _apps_ok() -> list[dict]:
    rows = []
    for surface in APP_SURFACES:
        row = attach_shipaz(
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
    return attach_shipaz(
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
    return attach_shipaz(
        {
            "mode": "NO_ANSWER",
            "product_mode": "ABSTAIN",
            "completion": "NO_ANSWER",
            "wall_ms": 80,
            "n_new": 0,
        }
    )


def test_given_contract_when_constants_then_match_az2() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AZ2 — smoke + content · held-out/over-refuse
    assert SHIPAZ_ID == "H-SHIPAZ"
    assert REQUIRED_MODES == ("LOOKUP", "PEAK", "DECODE", "ABSTAIN")
    assert set(SHIPAZ_PATHS) <= set(SHIPAZ_CHARTER["paths"])
    assert SHIPAZ_CHARTER.get("content_bars") is True
    assert SHIPAZ_CHARTER.get("heldout_fp_labeled_abstain") is True
    assert SHIPAZ_CHARTER.get("overrefuse_labeled_lookup") is True
    assert SHIPAZ_CHARTER.get("regression_hold") is True
    assert "PRODGEN" in SHIPAZ_THESIS or "held-out" in SHIPAZ_THESIS.lower()
    assert "gibberish-tail" in SHIPAZ_CLAIM
    assert "div" in HELDOUT_FP_ASK.lower()
    assert "clear" in OVERREFUSE_ASK.lower() or "Remove all" in OVERREFUSE_ASK
    assert "mul" in NAMED_INTENT_ASK.lower()
    assert banner_modes_ok() is True
    cited = set(SHIPAZ_CHARTER.get("cite_az_locks") or [])
    assert {"H-PRODGEN", "H-PRODINT", "H-SHIPAY"} <= cited
    assert APP_SURFACES == ("known-ask", "howto", "long-doc")
    assert len(APP_SMOKE_PACK) == 3


def test_given_gibberish_decode_when_attach_then_abstain() -> None:
    row = _decode_abstain()
    assert row["product_mode"] == "ABSTAIN"
    assert row["completion"] == "NO_ANSWER"
    assert content_matches_mode(row) is True


def test_given_arms_when_honest_then_core_modes() -> None:
    arms = _good_arms()
    assert arms_honest_ok(arms) is True
    assert core_modes_ok(arms) is True


def test_given_all_ok_when_decide_then_promote() -> None:
    out = decide_shipaz(
        arms=_good_arms(),
        default_asks=_defaults(),
        apps=_apps_ok(),
        decode_probe=_decode_abstain(),
        near_miss=_near(),
        anti_fp_signed=True,
    )
    assert out.startswith("PROMOTE")
    assert SHIPAZ_ID in out


def test_given_heldout_lookup_when_decide_then_kill() -> None:
    defaults = _defaults()
    for row in defaults:
        if row.get("question") == HELDOUT_FP_ASK:
            row["product_mode"] = "LOOKUP"
            row["completion"] = "def add(a, b):\n    return a + b"
            row["mode"] = "SEMWRAP_LOOKUP"
            row["modeui_line"] = (
                "mode=LOOKUP · wall_ms=1.0000 · n_new=0 · raw=SEMWRAP_LOOKUP"
            )
    out = decide_shipaz(
        arms=_good_arms(),
        default_asks=defaults,
        apps=_apps_ok(),
        decode_probe=_decode_abstain(),
        near_miss=_near(),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "held-out" in out.lower() or "heldout" in out.lower()


def test_given_overrefuse_abstain_when_decide_then_kill() -> None:
    defaults = _defaults()
    for row in defaults:
        if row.get("question") == OVERREFUSE_ASK:
            row["product_mode"] = "ABSTAIN"
            row["completion"] = "NO_ANSWER"
            row["mode"] = "NO_ANSWER"
            row["modeui_line"] = (
                "mode=ABSTAIN · wall_ms=1.0000 · n_new=0 · raw=NO_ANSWER"
            )
    out = decide_shipaz(
        arms=_good_arms(),
        default_asks=defaults,
        apps=_apps_ok(),
        decode_probe=_decode_abstain(),
        near_miss=_near(),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "over-refuse" in out.lower() or "overrefuse" in out.lower()


def test_given_named_lookup_when_decide_then_kill() -> None:
    defaults = _defaults()
    for row in defaults:
        if row.get("question") == NAMED_INTENT_ASK:
            row["product_mode"] = "LOOKUP"
            row["completion"] = "def add(a, b):\n    return a + b"
            row["mode"] = "SEMWRAP_LOOKUP"
            row["modeui_line"] = (
                "mode=LOOKUP · wall_ms=1.0000 · n_new=0 · raw=SEMWRAP_LOOKUP"
            )
    out = decide_shipaz(
        arms=_good_arms(),
        default_asks=defaults,
        apps=_apps_ok(),
        decode_probe=_decode_abstain(),
        near_miss=_near(),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "named" in out.lower()


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_shipaz(
        arms=_good_arms(),
        default_asks=_defaults(),
        apps=_apps_ok(),
        decode_probe=_decode_abstain(),
        anti_fp_signed=False,
    )
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_no_regression_hold_when_decide_then_kill() -> None:
    bad = dict(SHIPAZ_CHARTER)
    bad["regression_hold"] = False
    out = decide_shipaz(
        arms=_good_arms(),
        default_asks=_defaults(),
        apps=_apps_ok(),
        decode_probe=_decode_abstain(),
        charter=bad,
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "regression_hold" in out
