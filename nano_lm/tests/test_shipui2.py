"""Contract: Wave AV2 H-SHIPUI2 — modes + DECODE content honesty."""

from __future__ import annotations

from shipui2_ops import (
    APP_SMOKE_PACK,
    APP_SURFACES,
    REQUIRED_MODES,
    SHIPUI2_CHARTER,
    SHIPUI2_CLAIM,
    SHIPUI2_ID,
    SHIPUI2_PATHS,
    SHIPUI2_THESIS,
    arms_honest_ok,
    attach_shipui2,
    banner_modes_ok,
    content_matches_mode,
    core_modes_ok,
    decide_shipui2,
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
    row = attach_shipui2(
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
        row = attach_shipui2(row)
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
        attach_shipui2(
            {
                "mode": "WRAP_LOOKUP",
                "product_mode": "LOOKUP",
                "completion": "def add(a, b):\n    return a + b",
                "wall_ms": 0,
                "n_new": 0,
            }
        ),
        attach_shipui2(
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
        row = attach_shipui2(
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
    # Gibberish WRAP_DECODE must gate to ABSTAIN
    return attach_shipui2(
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


def test_given_contract_when_constants_then_match_av2() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AV2 — smoke + content · DECODE law
    assert SHIPUI2_ID == "H-SHIPUI2"
    assert REQUIRED_MODES == ("LOOKUP", "PEAK", "DECODE", "ABSTAIN")
    assert set(SHIPUI2_PATHS) <= set(SHIPUI2_CHARTER["paths"])
    assert SHIPUI2_CHARTER.get("content_bars") is True
    assert SHIPUI2_CHARTER.get("decode_usable_or_abstain") is True
    assert SHIPUI2_CHARTER.get("smoke") == "4/4"
    assert "DECODE" in SHIPUI2_THESIS or "content" in SHIPUI2_THESIS.lower()
    assert "gibberish-tail" in SHIPUI2_CLAIM
    assert APP_SURFACES == ("known-ask", "howto", "long-doc")
    assert len(APP_SMOKE_PACK) == 3
    assert banner_modes_ok() is True


def test_given_gibberish_decode_when_attach_then_abstain() -> None:
    row = _decode_abstain()
    assert row["product_mode"] == "ABSTAIN"
    assert row["completion"] == "NO_ANSWER"
    assert content_matches_mode(row) is True


def test_given_usable_decode_when_content_then_ok() -> None:
    row = attach_shipui2(
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
    near = attach_shipui2(
        {
            "mode": "NO_ANSWER",
            "product_mode": "ABSTAIN",
            "completion": "NO_ANSWER",
            "wall_ms": 80,
            "n_new": 0,
        }
    )
    out = decide_shipui2(
        arms=_good_arms(),
        default_asks=_defaults(),
        apps=_apps_ok(),
        decode_probe=_decode_abstain(),
        near_miss=near,
        anti_fp_signed=True,
    )
    assert out.startswith("PROMOTE")
    assert SHIPUI2_ID in out


def test_given_gibberish_still_decode_when_decide_then_kill() -> None:
    # Bypass attach gate: raw junk still labeled DECODE
    bad = {
        "mode": "WRAP_DECODE",
        "product_mode": "DECODE",
        "completion": (
            "quickly and which,.Suddenly some \ufffd funny everything "
            "really carefully looking something"
        ),
        "wall_ms": 100.0,
        "n_new": 64,
        "modeui_line": "mode=DECODE · wall_ms=100.0000 · n_new=64 · raw=WRAP_DECODE",
    }
    out = decide_shipui2(
        arms=_good_arms(),
        default_asks=_defaults(),
        apps=_apps_ok(),
        decode_probe=bad,
        near_miss=attach_shipui2(
            {
                "mode": "NO_ANSWER",
                "product_mode": "ABSTAIN",
                "completion": "NO_ANSWER",
                "wall_ms": 1,
                "n_new": 0,
            }
        ),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "DECODE" in out


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_shipui2(
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
    out = decide_shipui2(
        arms=arms,
        default_asks=_defaults(),
        apps=_apps_ok(),
        decode_probe=_decode_abstain(),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
