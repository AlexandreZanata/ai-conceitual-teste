"""Contract: Wave AY3 H-NANOGEN9 — gen-defer; not NANOGEN8 rename."""

from __future__ import annotations

from nanogen9_ops import (
    NANOGEN9_ANTI_FP,
    NANOGEN9_CLAIM,
    NANOGEN9_ID,
    NANOGEN9_METHOD,
    NANOGEN9_STANCE,
    NANOGEN9_THESIS,
    PARENT_NANOGEN6_TRUE_CONTINUE,
    PARENT_NANOGEN7_TRUE_CONTINUE,
    PARENT_NANOGEN8_DEFER,
    TRUE_GEN_JUDGE,
    decide_nanogen9,
    extract_nanogen9_board,
    method_is_rename,
)


def test_given_contract_when_constants_then_match_ay3() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AY3 — defer unless real method + true_continue
    assert NANOGEN9_ID == "H-NANOGEN9"
    assert NANOGEN9_STANCE["stance"] == "defer"
    assert NANOGEN9_STANCE["capcheck"] == "closed"
    assert NANOGEN9_STANCE["named_hyp"] == "H-NANOGEN9"
    assert NANOGEN9_STANCE["nanogen9_rename_forbidden"] is True
    assert NANOGEN9_STANCE["nanogen8_defer_cited"] is True
    assert NANOGEN9_METHOD["real_new_method"] is False
    assert NANOGEN9_METHOD["renames_nanogen8"] is False
    assert "defer" in NANOGEN9_THESIS.lower()
    assert "nanogen8" in NANOGEN9_THESIS.lower()
    assert "gibberish-tail" in NANOGEN9_CLAIM
    assert PARENT_NANOGEN6_TRUE_CONTINUE == 0.0
    assert PARENT_NANOGEN7_TRUE_CONTINUE == 0.0
    assert PARENT_NANOGEN8_DEFER is True
    assert TRUE_GEN_JUDGE["span_fallback_neq_gen"] is True
    assert "NANOGEN9" in NANOGEN9_ANTI_FP or "nanogen9" in NANOGEN9_ANTI_FP.lower()


def test_given_rename_method_when_check_then_true() -> None:
    assert method_is_rename({"renames_nanogen8": True}) is True
    assert method_is_rename({"renames_nanogen7_tac": True}) is True
    assert method_is_rename({"renames_nanogen6": True}) is True
    assert method_is_rename({"kind": "nanogen8_rename", "id": "x"}) is True
    assert method_is_rename(dict(NANOGEN9_METHOD)) is False


def test_given_defer_stance_when_decide_then_defer() -> None:
    board = extract_nanogen9_board()
    out = decide_nanogen9(board=board, anti_fp_signed=True)
    assert out.startswith("DEFER")
    assert NANOGEN9_ID in out
    assert "nanogen8" in out.lower() or "defer" in out.lower()


def test_given_nanogen8_rename_when_decide_then_kill() -> None:
    board = extract_nanogen9_board(
        method={
            "id": "nanogen8-clone",
            "kind": "nanogen8_rename",
            "real_new_method": True,
            "renames_nanogen8": True,
            "renames_nanogen7_tac": False,
            "renames_nanogen6": False,
            "capcheck": "closed",
        },
        true_continue_mean=9.0,
        n_true_continue=10,
    )
    out = decide_nanogen9(board=board, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "rename" in out.lower()


def test_given_real_method_true_continue_when_decide_then_promote() -> None:
    board = extract_nanogen9_board(
        stance={
            **dict(NANOGEN9_STANCE),
            "stance": "new_method",
        },
        method={
            "id": "arch-x",
            "kind": "arch",
            "real_new_method": True,
            "renames_nanogen8": False,
            "renames_nanogen7_tac": False,
            "renames_nanogen6": False,
            "capcheck": "closed",
        },
        true_continue_mean=6.0,
        n_true_continue=8,
    )
    out = decide_nanogen9(board=board, anti_fp_signed=True)
    assert out.startswith("PROMOTE")


def test_given_method_no_true_continue_when_decide_then_hold() -> None:
    board = extract_nanogen9_board(
        stance={**dict(NANOGEN9_STANCE), "stance": "new_method"},
        method={
            "id": "data-x",
            "kind": "data",
            "real_new_method": True,
            "renames_nanogen8": False,
            "renames_nanogen7_tac": False,
            "renames_nanogen6": False,
            "capcheck": "closed",
        },
        true_continue_mean=4.0,
        n_true_continue=0,
    )
    out = decide_nanogen9(board=board, anti_fp_signed=True)
    assert out.startswith("HOLD")


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_nanogen9(
        board=extract_nanogen9_board(), anti_fp_signed=False
    )
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_modes_regress_when_decide_then_kill() -> None:
    board = extract_nanogen9_board(live_modes_ok=False)
    out = decide_nanogen9(board=board, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "modes" in out.lower()
