"""Contract: Wave AZ3 H-NANOGEN10 — gen-defer; not NANOGEN9 rename."""

from __future__ import annotations

from nanogen10_ops import (
    NANOGEN10_ANTI_FP,
    NANOGEN10_CLAIM,
    NANOGEN10_ID,
    NANOGEN10_METHOD,
    NANOGEN10_STANCE,
    NANOGEN10_THESIS,
    PARENT_NANOGEN6_TRUE_CONTINUE,
    PARENT_NANOGEN7_TRUE_CONTINUE,
    PARENT_NANOGEN8_DEFER,
    PARENT_NANOGEN9_DEFER,
    TRUE_GEN_JUDGE,
    decide_nanogen10,
    extract_nanogen10_board,
    method_is_rename,
)


def test_given_contract_when_constants_then_match_az3() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AZ3 — defer unless real method + true_continue
    assert NANOGEN10_ID == "H-NANOGEN10"
    assert NANOGEN10_STANCE["stance"] == "defer"
    assert NANOGEN10_STANCE["capcheck"] == "closed"
    assert NANOGEN10_STANCE["named_hyp"] == "H-NANOGEN10"
    assert NANOGEN10_STANCE["nanogen10_rename_forbidden"] is True
    assert NANOGEN10_STANCE["nanogen9_defer_cited"] is True
    assert NANOGEN10_STANCE["nanogen8_defer_cited"] is True
    assert NANOGEN10_METHOD["real_new_method"] is False
    assert NANOGEN10_METHOD["renames_nanogen9"] is False
    assert "defer" in NANOGEN10_THESIS.lower()
    assert "nanogen9" in NANOGEN10_THESIS.lower()
    assert "gibberish-tail" in NANOGEN10_CLAIM
    assert PARENT_NANOGEN6_TRUE_CONTINUE == 0.0
    assert PARENT_NANOGEN7_TRUE_CONTINUE == 0.0
    assert PARENT_NANOGEN8_DEFER is True
    assert PARENT_NANOGEN9_DEFER is True
    assert TRUE_GEN_JUDGE["span_fallback_neq_gen"] is True
    assert "NANOGEN10" in NANOGEN10_ANTI_FP or "nanogen10" in NANOGEN10_ANTI_FP.lower()


def test_given_rename_method_when_check_then_true() -> None:
    assert method_is_rename({"renames_nanogen9": True}) is True
    assert method_is_rename({"renames_nanogen8": True}) is True
    assert method_is_rename({"renames_nanogen7_tac": True}) is True
    assert method_is_rename({"renames_nanogen6": True}) is True
    assert method_is_rename({"kind": "nanogen9_rename", "id": "x"}) is True
    assert method_is_rename(dict(NANOGEN10_METHOD)) is False


def test_given_defer_stance_when_decide_then_defer() -> None:
    board = extract_nanogen10_board()
    out = decide_nanogen10(board=board, anti_fp_signed=True)
    assert out.startswith("DEFER")
    assert NANOGEN10_ID in out
    assert "nanogen9" in out.lower() or "defer" in out.lower()


def test_given_nanogen9_rename_when_decide_then_kill() -> None:
    board = extract_nanogen10_board(
        method={
            "id": "nanogen9-clone",
            "kind": "nanogen9_rename",
            "real_new_method": True,
            "renames_nanogen9": True,
            "renames_nanogen8": False,
            "renames_nanogen7_tac": False,
            "renames_nanogen6": False,
            "capcheck": "closed",
        },
        true_continue_mean=9.0,
        n_true_continue=10,
    )
    out = decide_nanogen10(board=board, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "rename" in out.lower()


def test_given_real_method_true_continue_when_decide_then_promote() -> None:
    board = extract_nanogen10_board(
        stance={
            **dict(NANOGEN10_STANCE),
            "stance": "new_method",
        },
        method={
            "id": "arch-x",
            "kind": "arch",
            "real_new_method": True,
            "renames_nanogen9": False,
            "renames_nanogen8": False,
            "renames_nanogen7_tac": False,
            "renames_nanogen6": False,
            "capcheck": "closed",
        },
        true_continue_mean=6.0,
        n_true_continue=8,
    )
    out = decide_nanogen10(board=board, anti_fp_signed=True)
    assert out.startswith("PROMOTE")


def test_given_method_no_true_continue_when_decide_then_hold() -> None:
    board = extract_nanogen10_board(
        stance={**dict(NANOGEN10_STANCE), "stance": "new_method"},
        method={
            "id": "data-x",
            "kind": "data",
            "real_new_method": True,
            "renames_nanogen9": False,
            "renames_nanogen8": False,
            "renames_nanogen7_tac": False,
            "renames_nanogen6": False,
            "capcheck": "closed",
        },
        true_continue_mean=4.0,
        n_true_continue=0,
    )
    out = decide_nanogen10(board=board, anti_fp_signed=True)
    assert out.startswith("HOLD")


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_nanogen10(
        board=extract_nanogen10_board(), anti_fp_signed=False
    )
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_modes_regress_when_decide_then_kill() -> None:
    board = extract_nanogen10_board(live_modes_ok=False)
    out = decide_nanogen10(board=board, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "modes" in out.lower()
