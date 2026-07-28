"""Contract: Wave BA4 H-NANOGEN11 — gen-defer; not NANOGEN10 rename."""

from __future__ import annotations

from nanogen11_ops import (
    NANOGEN11_ANTI_FP,
    NANOGEN11_CLAIM,
    NANOGEN11_ID,
    NANOGEN11_METHOD,
    NANOGEN11_STANCE,
    NANOGEN11_THESIS,
    PARENT_NANOGEN6_TRUE_CONTINUE,
    PARENT_NANOGEN7_TRUE_CONTINUE,
    PARENT_NANOGEN8_DEFER,
    PARENT_NANOGEN9_DEFER,
    PARENT_NANOGEN10_DEFER,
    TRUE_GEN_JUDGE,
    decide_nanogen11,
    extract_nanogen11_board,
    method_is_rename,
)


def test_given_contract_when_constants_then_match_ba4() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8 BA4 — defer unless real method + true_continue
    assert NANOGEN11_ID == "H-NANOGEN11"
    assert NANOGEN11_STANCE["stance"] == "defer"
    assert NANOGEN11_STANCE["capcheck"] == "closed"
    assert NANOGEN11_STANCE["named_hyp"] == "H-NANOGEN11"
    assert NANOGEN11_STANCE["nanogen11_rename_forbidden"] is True
    assert NANOGEN11_STANCE["nanogen10_defer_cited"] is True
    assert NANOGEN11_METHOD["real_new_method"] is False
    assert NANOGEN11_METHOD["renames_nanogen10"] is False
    assert "defer" in NANOGEN11_THESIS.lower()
    assert "nanogen10" in NANOGEN11_THESIS.lower()
    assert "gibberish-tail" in NANOGEN11_CLAIM
    assert PARENT_NANOGEN6_TRUE_CONTINUE == 0.0
    assert PARENT_NANOGEN7_TRUE_CONTINUE == 0.0
    assert PARENT_NANOGEN8_DEFER is True
    assert PARENT_NANOGEN9_DEFER is True
    assert PARENT_NANOGEN10_DEFER is True
    assert TRUE_GEN_JUDGE["span_fallback_neq_gen"] is True
    assert "NANOGEN11" in NANOGEN11_ANTI_FP or "nanogen11" in NANOGEN11_ANTI_FP.lower()


def test_given_rename_method_when_check_then_true() -> None:
    assert method_is_rename({"renames_nanogen10": True}) is True
    assert method_is_rename({"renames_nanogen9": True}) is True
    assert method_is_rename({"kind": "nanogen10_rename", "id": "x"}) is True
    assert method_is_rename(dict(NANOGEN11_METHOD)) is False


def test_given_defer_stance_when_decide_then_defer() -> None:
    board = extract_nanogen11_board()
    out = decide_nanogen11(board=board, anti_fp_signed=True)
    assert out.startswith("DEFER")
    assert NANOGEN11_ID in out
    assert "nanogen10" in out.lower() or "defer" in out.lower()


def test_given_nanogen10_rename_when_decide_then_kill() -> None:
    board = extract_nanogen11_board(
        method={
            "id": "nanogen10-clone",
            "kind": "nanogen10_rename",
            "real_new_method": True,
            "renames_nanogen10": True,
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
    out = decide_nanogen11(board=board, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "rename" in out.lower()


def test_given_real_method_true_continue_when_decide_then_promote() -> None:
    board = extract_nanogen11_board(
        stance={**dict(NANOGEN11_STANCE), "stance": "M1"},
        method={
            "id": "distill-x",
            "kind": "M1",
            "real_new_method": True,
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
    out = decide_nanogen11(board=board, anti_fp_signed=True)
    assert out.startswith("PROMOTE")


def test_given_method_no_true_continue_when_decide_then_hold() -> None:
    board = extract_nanogen11_board(
        stance={**dict(NANOGEN11_STANCE), "stance": "M2"},
        method={
            "id": "hybrid-x",
            "kind": "M2",
            "real_new_method": True,
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
    out = decide_nanogen11(board=board, anti_fp_signed=True)
    assert out.startswith("HOLD")


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_nanogen11(
        board=extract_nanogen11_board(), anti_fp_signed=False
    )
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_modes_regress_when_decide_then_kill() -> None:
    board = extract_nanogen11_board(live_modes_ok=False)
    out = decide_nanogen11(board=board, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "modes" in out.lower()
