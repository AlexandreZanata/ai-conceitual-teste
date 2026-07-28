"""Contract: Wave BE5 H-NANOGEN15 — gen-defer-once; not NANOGEN14 rename."""

from __future__ import annotations

from nanogen15_ops import (
    NANOGEN15_ANTI_FP,
    NANOGEN15_CLAIM,
    NANOGEN15_ID,
    NANOGEN15_METHOD,
    NANOGEN15_STANCE,
    NANOGEN15_THESIS,
    PARENT_NANOGEN6_TRUE_CONTINUE,
    PARENT_NANOGEN7_TRUE_CONTINUE,
    PARENT_NANOGEN8_DEFER,
    PARENT_NANOGEN9_DEFER,
    PARENT_NANOGEN10_DEFER,
    PARENT_NANOGEN11_DEFER,
    PARENT_NANOGEN12_DEFER,
    PARENT_NANOGEN13_DEFER,
    PARENT_NANOGEN14_DEFER,
    TRUE_GEN_JUDGE,
    decide_nanogen15,
    extract_nanogen15_board,
    method_is_rename,
)


def _real_method(**extra: object) -> dict:
    base = {
        "id": "distill-x",
        "kind": "M1",
        "real_new_method": True,
        "renames_nanogen14": False,
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
    }
    base.update(extra)
    return base


def test_given_contract_when_constants_then_match_be5() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BE5 — defer once unless real method + tc
    assert NANOGEN15_ID == "H-NANOGEN15"
    assert NANOGEN15_STANCE["stance"] == "defer"
    assert NANOGEN15_STANCE["capcheck"] == "closed"
    assert NANOGEN15_STANCE["named_hyp"] == "H-NANOGEN15"
    assert NANOGEN15_STANCE["nanogen15_rename_forbidden"] is True
    assert NANOGEN15_STANCE["defer_once_stop_rule"] is True
    assert NANOGEN15_STANCE["nanogen14_defer_cited"] is True
    assert NANOGEN15_METHOD["real_new_method"] is False
    assert NANOGEN15_METHOD["renames_nanogen14"] is False
    assert "defer" in NANOGEN15_THESIS.lower()
    assert "nanogen14" in NANOGEN15_THESIS.lower()
    assert "gibberish-tail" in NANOGEN15_CLAIM
    assert PARENT_NANOGEN6_TRUE_CONTINUE == 0.0
    assert PARENT_NANOGEN7_TRUE_CONTINUE == 0.0
    assert PARENT_NANOGEN8_DEFER is True
    assert PARENT_NANOGEN9_DEFER is True
    assert PARENT_NANOGEN10_DEFER is True
    assert PARENT_NANOGEN11_DEFER is True
    assert PARENT_NANOGEN12_DEFER is True
    assert PARENT_NANOGEN13_DEFER is True
    assert PARENT_NANOGEN14_DEFER is True
    assert TRUE_GEN_JUDGE["span_fallback_neq_gen"] is True
    assert "NANOGEN15" in NANOGEN15_ANTI_FP or "nanogen15" in NANOGEN15_ANTI_FP.lower()


def test_given_rename_method_when_check_then_true() -> None:
    assert method_is_rename({"renames_nanogen14": True}) is True
    assert method_is_rename({"renames_nanogen13": True}) is True
    assert method_is_rename({"kind": "nanogen14_rename", "id": "x"}) is True
    assert method_is_rename(dict(NANOGEN15_METHOD)) is False


def test_given_defer_stance_when_decide_then_defer() -> None:
    board = extract_nanogen15_board()
    out = decide_nanogen15(board=board, anti_fp_signed=True)
    assert out.startswith("DEFER")
    assert NANOGEN15_ID in out
    assert "nanogen14" in out.lower() or "defer" in out.lower()
    assert "once" in out.lower()


def test_given_nanogen14_rename_when_decide_then_kill() -> None:
    board = extract_nanogen15_board(
        method=_real_method(
            id="nanogen14-clone",
            kind="nanogen14_rename",
            renames_nanogen14=True,
            candidate="M1",
        ),
        true_continue_mean=9.0,
        n_true_continue=10,
    )
    out = decide_nanogen15(board=board, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "rename" in out.lower()


def test_given_real_method_true_continue_when_decide_then_promote() -> None:
    board = extract_nanogen15_board(
        stance={**dict(NANOGEN15_STANCE), "stance": "M1"},
        method=_real_method(),
        true_continue_mean=6.0,
        n_true_continue=8,
    )
    out = decide_nanogen15(board=board, anti_fp_signed=True)
    assert out.startswith("PROMOTE")


def test_given_method_no_true_continue_when_decide_then_hold() -> None:
    board = extract_nanogen15_board(
        stance={**dict(NANOGEN15_STANCE), "stance": "M2"},
        method=_real_method(id="hybrid-x", kind="M2", candidate="M2"),
        true_continue_mean=4.0,
        n_true_continue=0,
    )
    out = decide_nanogen15(board=board, anti_fp_signed=True)
    assert out.startswith("HOLD")


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_nanogen15(
        board=extract_nanogen15_board(), anti_fp_signed=False
    )
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_modes_regress_when_decide_then_kill() -> None:
    board = extract_nanogen15_board(live_modes_ok=False)
    out = decide_nanogen15(board=board, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "modes" in out.lower()
