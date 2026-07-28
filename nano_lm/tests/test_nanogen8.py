"""Contract: Wave AX3 H-NANOGEN8 — gen-defer; not NANOGEN7 rename."""

from __future__ import annotations

from nanogen8_ops import (
    NANOGEN8_ANTI_FP,
    NANOGEN8_CLAIM,
    NANOGEN8_ID,
    NANOGEN8_METHOD,
    NANOGEN8_STANCE,
    NANOGEN8_THESIS,
    PARENT_NANOGEN6_TRUE_CONTINUE,
    PARENT_NANOGEN7_TRUE_CONTINUE,
    TRUE_GEN_JUDGE,
    decide_nanogen8,
    extract_nanogen8_board,
    method_is_rename,
)


def test_given_contract_when_constants_then_match_ax3() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AX3 — defer unless real method + true_continue
    assert NANOGEN8_ID == "H-NANOGEN8"
    assert NANOGEN8_STANCE["stance"] == "defer"
    assert NANOGEN8_STANCE["capcheck"] == "closed"
    assert NANOGEN8_STANCE["nanogen8_rename_forbidden"] is True
    assert NANOGEN8_METHOD["real_new_method"] is False
    assert NANOGEN8_METHOD["renames_nanogen7_tac"] is False
    assert "defer" in NANOGEN8_THESIS.lower()
    assert "rename" in NANOGEN8_THESIS.lower()
    assert "gibberish-tail" in NANOGEN8_CLAIM
    assert PARENT_NANOGEN6_TRUE_CONTINUE == 0.0
    assert PARENT_NANOGEN7_TRUE_CONTINUE == 0.0
    assert TRUE_GEN_JUDGE["span_fallback_neq_gen"] is True
    assert "LOOKUP" in NANOGEN8_ANTI_FP


def test_given_rename_method_when_check_then_true() -> None:
    assert method_is_rename({"renames_nanogen7_tac": True}) is True
    assert method_is_rename({"renames_nanogen6": True}) is True
    assert method_is_rename({"kind": "tac_rename", "id": "x"}) is True
    assert method_is_rename(dict(NANOGEN8_METHOD)) is False


def test_given_defer_stance_when_decide_then_defer() -> None:
    board = extract_nanogen8_board()
    out = decide_nanogen8(board=board, anti_fp_signed=True)
    assert out.startswith("DEFER")
    assert NANOGEN8_ID in out
    assert "rename" in out.lower() or "defer" in out.lower()


def test_given_tac_rename_when_decide_then_kill() -> None:
    board = extract_nanogen8_board(
        method={
            "id": "nanogen7-clone",
            "kind": "tac_rename",
            "real_new_method": True,
            "renames_nanogen7_tac": True,
            "renames_nanogen6": False,
            "capcheck": "closed",
        },
        true_continue_mean=9.0,
        n_true_continue=10,
    )
    out = decide_nanogen8(board=board, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "rename" in out.lower()


def test_given_real_method_true_continue_when_decide_then_promote() -> None:
    board = extract_nanogen8_board(
        stance={
            **dict(NANOGEN8_STANCE),
            "stance": "new_method",
        },
        method={
            "id": "arch-x",
            "kind": "arch",
            "real_new_method": True,
            "renames_nanogen7_tac": False,
            "renames_nanogen6": False,
            "capcheck": "closed",
        },
        true_continue_mean=6.0,
        n_true_continue=8,
    )
    out = decide_nanogen8(board=board, anti_fp_signed=True)
    assert out.startswith("PROMOTE")


def test_given_method_no_true_continue_when_decide_then_hold() -> None:
    board = extract_nanogen8_board(
        stance={**dict(NANOGEN8_STANCE), "stance": "new_method"},
        method={
            "id": "data-x",
            "kind": "data",
            "real_new_method": True,
            "renames_nanogen7_tac": False,
            "renames_nanogen6": False,
            "capcheck": "closed",
        },
        true_continue_mean=4.0,
        n_true_continue=0,
    )
    out = decide_nanogen8(board=board, anti_fp_signed=True)
    assert out.startswith("HOLD")


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_nanogen8(
        board=extract_nanogen8_board(), anti_fp_signed=False
    )
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_modes_regress_when_decide_then_kill() -> None:
    board = extract_nanogen8_board(live_modes_ok=False)
    out = decide_nanogen8(board=board, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "modes" in out.lower()
