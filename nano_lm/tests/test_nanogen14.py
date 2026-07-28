"""Contract: Wave BD4 H-NANOGEN14 — gen-defer; not NANOGEN13 rename."""

from __future__ import annotations

from nanogen14_ops import (
    NANOGEN14_ANTI_FP,
    NANOGEN14_CLAIM,
    NANOGEN14_ID,
    NANOGEN14_METHOD,
    NANOGEN14_STANCE,
    NANOGEN14_THESIS,
    PARENT_NANOGEN6_TRUE_CONTINUE,
    PARENT_NANOGEN7_TRUE_CONTINUE,
    PARENT_NANOGEN8_DEFER,
    PARENT_NANOGEN9_DEFER,
    PARENT_NANOGEN10_DEFER,
    PARENT_NANOGEN11_DEFER,
    PARENT_NANOGEN12_DEFER,
    PARENT_NANOGEN13_DEFER,
    TRUE_GEN_JUDGE,
    decide_nanogen14,
    extract_nanogen14_board,
    method_is_rename,
)


def test_given_contract_when_constants_then_match_bd4() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BD4 — defer unless real method + true_continue
    assert NANOGEN14_ID == "H-NANOGEN14"
    assert NANOGEN14_STANCE["stance"] == "defer"
    assert NANOGEN14_STANCE["capcheck"] == "closed"
    assert NANOGEN14_STANCE["named_hyp"] == "H-NANOGEN14"
    assert NANOGEN14_STANCE["nanogen14_rename_forbidden"] is True
    assert NANOGEN14_STANCE["nanogen13_defer_cited"] is True
    assert NANOGEN14_METHOD["real_new_method"] is False
    assert NANOGEN14_METHOD["renames_nanogen13"] is False
    assert "defer" in NANOGEN14_THESIS.lower()
    assert "nanogen13" in NANOGEN14_THESIS.lower()
    assert "gibberish-tail" in NANOGEN14_CLAIM
    assert PARENT_NANOGEN6_TRUE_CONTINUE == 0.0
    assert PARENT_NANOGEN7_TRUE_CONTINUE == 0.0
    assert PARENT_NANOGEN8_DEFER is True
    assert PARENT_NANOGEN9_DEFER is True
    assert PARENT_NANOGEN10_DEFER is True
    assert PARENT_NANOGEN11_DEFER is True
    assert PARENT_NANOGEN12_DEFER is True
    assert PARENT_NANOGEN13_DEFER is True
    assert TRUE_GEN_JUDGE["span_fallback_neq_gen"] is True
    assert "NANOGEN14" in NANOGEN14_ANTI_FP or "nanogen14" in NANOGEN14_ANTI_FP.lower()


def test_given_rename_method_when_check_then_true() -> None:
    assert method_is_rename({"renames_nanogen13": True}) is True
    assert method_is_rename({"renames_nanogen12": True}) is True
    assert method_is_rename({"kind": "nanogen13_rename", "id": "x"}) is True
    assert method_is_rename(dict(NANOGEN14_METHOD)) is False


def test_given_defer_stance_when_decide_then_defer() -> None:
    board = extract_nanogen14_board()
    out = decide_nanogen14(board=board, anti_fp_signed=True)
    assert out.startswith("DEFER")
    assert NANOGEN14_ID in out
    assert "nanogen13" in out.lower() or "defer" in out.lower()


def test_given_nanogen13_rename_when_decide_then_kill() -> None:
    board = extract_nanogen14_board(
        method={
            "id": "nanogen13-clone",
            "kind": "nanogen13_rename",
            "real_new_method": True,
            "renames_nanogen13": True,
            "renames_nanogen12": False,
            "renames_nanogen11": False,
            "renames_nanogen10": False,
            "renames_nanogen9": False,
            "renames_nanogen8": False,
            "renames_nanogen7_tac": False,
            "renames_nanogen6": False,
            "capcheck": "closed",
            "candidate": "M1",
        },
        true_continue_mean=9.0,
        n_true_continue=10,
    )
    out = decide_nanogen14(board=board, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "rename" in out.lower()


def test_given_real_method_true_continue_when_decide_then_promote() -> None:
    board = extract_nanogen14_board(
        stance={**dict(NANOGEN14_STANCE), "stance": "M1"},
        method={
            "id": "distill-x",
            "kind": "M1",
            "real_new_method": True,
            "renames_nanogen13": False,
            "renames_nanogen12": False,
            "renames_nanogen11": False,
            "renames_nanogen10": False,
            "renames_nanogen9": False,
            "renames_nanogen8": False,
            "renames_nanogen7_tac": False,
            "renames_nanogen6": False,
            "capcheck": "closed",
            "candidate": "M1",
        },
        true_continue_mean=6.0,
        n_true_continue=8,
    )
    out = decide_nanogen14(board=board, anti_fp_signed=True)
    assert out.startswith("PROMOTE")


def test_given_method_no_true_continue_when_decide_then_hold() -> None:
    board = extract_nanogen14_board(
        stance={**dict(NANOGEN14_STANCE), "stance": "M2"},
        method={
            "id": "hybrid-x",
            "kind": "M2",
            "real_new_method": True,
            "renames_nanogen13": False,
            "renames_nanogen12": False,
            "renames_nanogen11": False,
            "renames_nanogen10": False,
            "renames_nanogen9": False,
            "renames_nanogen8": False,
            "renames_nanogen7_tac": False,
            "renames_nanogen6": False,
            "capcheck": "closed",
            "candidate": "M2",
        },
        true_continue_mean=4.0,
        n_true_continue=0,
    )
    out = decide_nanogen14(board=board, anti_fp_signed=True)
    assert out.startswith("HOLD")


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_nanogen14(
        board=extract_nanogen14_board(), anti_fp_signed=False
    )
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_modes_regress_when_decide_then_kill() -> None:
    board = extract_nanogen14_board(live_modes_ok=False)
    out = decide_nanogen14(board=board, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "modes" in out.lower()
