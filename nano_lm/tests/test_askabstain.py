"""Contract: Wave AS1 H-ASKABSTAIN — default ask path ABSTAIN (pesquisa §5)."""

from __future__ import annotations

from askabstain_ops import (
    ASKABSTAIN_CHARTER,
    ASKABSTAIN_ID,
    ASKABSTAIN_KNOWN_ASK,
    ASKABSTAIN_OOD_PACK,
    ASKABSTAIN_THESIS,
    MIN_OOD_ABSTAIN_RATE,
    NO_ANSWER,
    askabstain_stats,
    decide_askabstain,
    default_path_abstained,
)


def test_given_contract_when_constants_then_match_as1() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AS1 — default ask OOD→NO_ANSWER · FH 0
    assert ASKABSTAIN_ID == "H-ASKABSTAIN"
    assert NO_ANSWER == "NO_ANSWER"
    assert MIN_OOD_ABSTAIN_RATE == 0.8
    assert len(ASKABSTAIN_OOD_PACK) >= 6
    assert "nano:z:ask" in ASKABSTAIN_CHARTER["paths"]
    assert "default" in ASKABSTAIN_THESIS.lower() or "nano:z:ask" in ASKABSTAIN_THESIS
    assert "named add" in ASKABSTAIN_KNOWN_ASK


def test_given_default_payload_when_abstained_then_true() -> None:
    payload = {
        "abstained": True,
        "completion": NO_ANSWER,
        "product_mode": "ABSTAIN",
        "mode": "NO_ANSWER",
    }
    assert default_path_abstained(payload) is True


def test_given_runner_only_when_not_wired_then_false() -> None:
    # GIVEN raw DECODE junk without default-path fields
    # WHEN checking default_path_abstained
    # THEN False (runner-only apply would set these — missing = not wired)
    raw = {
        "abstained": False,
        "completion": "........",
        "product_mode": "DECODE",
        "mode": "QT+EARLY n=1",
    }
    assert default_path_abstained(raw) is False


def test_given_ready_when_decide_then_promote() -> None:
    stats = askabstain_stats(
        ood_default_abstained=[True] * 8,
        known_lookup_ok=True,
        n_false_hit=0,
        modes_labeled=True,
        default_path_wired=True,
    )
    assert stats["pass_ood_abstain"] is True
    assert stats["pass_default_path"] is True
    assert decide_askabstain(stats) == "PROMOTE"


def test_given_unwired_when_decide_then_kill() -> None:
    stats = askabstain_stats(
        ood_default_abstained=[True] * 8,
        known_lookup_ok=True,
        n_false_hit=0,
        modes_labeled=True,
        default_path_wired=False,
    )
    out = decide_askabstain(stats)
    assert out.startswith("KILL")
    assert "default ask" in out


def test_given_low_abstain_when_decide_then_kill() -> None:
    stats = askabstain_stats(
        ood_default_abstained=[True, False, False, False, False],
        known_lookup_ok=True,
        n_false_hit=0,
        modes_labeled=True,
        default_path_wired=True,
    )
    assert decide_askabstain(stats).startswith("KILL")


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = askabstain_stats(
        ood_default_abstained=[True] * 8,
        known_lookup_ok=True,
        n_false_hit=1,
        modes_labeled=True,
        default_path_wired=True,
    )
    assert "false-hit" in decide_askabstain(stats)


def test_given_finalize_helper_when_junk_then_abstain_fields() -> None:
    # GIVEN junk DECODE payload · WHEN _finalize_ask_payload · THEN ABSTAIN
    from run_z_ask import _finalize_ask_payload

    out = _finalize_ask_payload(
        {"mode": "QT+EARLY n=1", "completion": "........", "wall_ms": 9.0},
        abstain=True,
    )
    assert out["abstained"] is True
    assert out["completion"] == NO_ANSWER
    assert out["product_mode"] == "ABSTAIN"
    assert "mode=ABSTAIN" in out["modeui_line"]


def test_given_finalize_off_when_junk_then_no_abstain() -> None:
    from run_z_ask import _finalize_ask_payload

    out = _finalize_ask_payload(
        {"mode": "QT+EARLY n=1", "completion": "........", "wall_ms": 9.0},
        abstain=False,
    )
    assert out.get("abstained") is not True
    assert out["completion"] == "........"
    assert out["product_mode"] == "DECODE"
