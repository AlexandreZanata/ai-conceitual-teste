"""Contract: Wave BG5 H-NANOGEN17 — gen-SKIP stop rule; not empty DEFER."""

from __future__ import annotations

from nanogen17_ops import (
    NANOGEN17_ANTI_FP,
    NANOGEN17_CLAIM,
    NANOGEN17_ID,
    NANOGEN17_METHOD,
    NANOGEN17_STANCE,
    NANOGEN17_THESIS,
    PARENT_NANOGEN6_TRUE_CONTINUE,
    PARENT_NANOGEN7_TRUE_CONTINUE,
    PARENT_NANOGEN8_DEFER,
    PARENT_NANOGEN9_DEFER,
    PARENT_NANOGEN10_DEFER,
    PARENT_NANOGEN11_DEFER,
    PARENT_NANOGEN12_DEFER,
    PARENT_NANOGEN13_DEFER,
    PARENT_NANOGEN14_DEFER,
    PARENT_NANOGEN15_DEFER,
    PARENT_NANOGEN16_SKIP,
    TRUE_GEN_JUDGE,
    decide_nanogen17,
    extract_nanogen17_board,
    method_is_rename,
)


def _real_method(**extra: object) -> dict:
    base = {
        "id": "distill-x",
        "kind": "M1",
        "real_new_method": True,
        "method_plan_attached": True,
        "empty_defer_letter": False,
        "renames_nanogen16": False,
        "renames_nanogen15": False,
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


def test_given_contract_when_constants_then_match_bg5() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BG5 — SKIP unless plan + tc
    assert NANOGEN17_ID == "H-NANOGEN17"
    assert NANOGEN17_STANCE["stance"] == "skip"
    assert NANOGEN17_STANCE["capcheck"] == "closed"
    assert NANOGEN17_STANCE["named_hyp"] == "H-NANOGEN17"
    assert NANOGEN17_STANCE["method_plan_attached"] is False
    assert NANOGEN17_STANCE["nanogen17_rename_forbidden"] is True
    assert NANOGEN17_STANCE["skip_gen_stop_rule"] is True
    assert NANOGEN17_STANCE["nanogen16_skip_cited"] is True
    assert NANOGEN17_METHOD["real_new_method"] is False
    assert NANOGEN17_METHOD["method_plan_attached"] is False
    assert NANOGEN17_METHOD["empty_defer_letter"] is False
    assert "skip" in NANOGEN17_THESIS.lower()
    assert "nanogen16" in NANOGEN17_THESIS.lower() or "SKIP" in NANOGEN17_THESIS
    assert "gibberish-tail" in NANOGEN17_CLAIM
    assert PARENT_NANOGEN6_TRUE_CONTINUE == 0.0
    assert PARENT_NANOGEN7_TRUE_CONTINUE == 0.0
    assert PARENT_NANOGEN8_DEFER is True
    assert PARENT_NANOGEN9_DEFER is True
    assert PARENT_NANOGEN10_DEFER is True
    assert PARENT_NANOGEN11_DEFER is True
    assert PARENT_NANOGEN12_DEFER is True
    assert PARENT_NANOGEN13_DEFER is True
    assert PARENT_NANOGEN14_DEFER is True
    assert PARENT_NANOGEN15_DEFER is True
    assert PARENT_NANOGEN16_SKIP is True
    assert TRUE_GEN_JUDGE["span_fallback_neq_gen"] is True
    assert "SKIP" in NANOGEN17_ANTI_FP or "skip" in NANOGEN17_ANTI_FP.lower()


def test_given_rename_method_when_check_then_true() -> None:
    assert method_is_rename({"renames_nanogen16": True}) is True
    assert method_is_rename({"renames_nanogen15": True}) is True
    assert method_is_rename({"kind": "nanogen16_rename", "id": "x"}) is True
    assert method_is_rename(dict(NANOGEN17_METHOD)) is False


def test_given_skip_stance_when_decide_then_skip() -> None:
    board = extract_nanogen17_board()
    out = decide_nanogen17(board=board, anti_fp_signed=True)
    assert out.startswith("SKIP")
    assert NANOGEN17_ID in out
    assert "defer letter" in out.lower() or "skip" in out.lower()
    assert "nanogen" in out.lower()


def test_given_empty_defer_letter_when_decide_then_kill() -> None:
    board = extract_nanogen17_board(
        method={
            **dict(NANOGEN17_METHOD),
            "empty_defer_letter": True,
            "kind": "defer",
            "id": "empty-defer",
        }
    )
    out = decide_nanogen17(board=board, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "defer" in out.lower()


def test_given_nanogen16_rename_when_decide_then_kill() -> None:
    board = extract_nanogen17_board(
        method=_real_method(
            id="nanogen16-clone",
            kind="nanogen16_rename",
            renames_nanogen16=True,
            candidate="M1",
        ),
        true_continue_mean=9.0,
        n_true_continue=10,
    )
    out = decide_nanogen17(board=board, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "rename" in out.lower()


def test_given_plan_true_continue_when_decide_then_promote() -> None:
    board = extract_nanogen17_board(
        stance={
            **dict(NANOGEN17_STANCE),
            "stance": "M1",
            "method_plan_attached": True,
        },
        method=_real_method(),
        true_continue_mean=6.0,
        n_true_continue=8,
    )
    out = decide_nanogen17(board=board, anti_fp_signed=True)
    assert out.startswith("PROMOTE")


def test_given_plan_no_true_continue_when_decide_then_hold() -> None:
    board = extract_nanogen17_board(
        stance={
            **dict(NANOGEN17_STANCE),
            "stance": "M2",
            "method_plan_attached": True,
        },
        method=_real_method(id="hybrid-x", kind="M2", candidate="M2"),
        true_continue_mean=4.0,
        n_true_continue=0,
    )
    out = decide_nanogen17(board=board, anti_fp_signed=True)
    assert out.startswith("HOLD")


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_nanogen17(
        board=extract_nanogen17_board(), anti_fp_signed=False
    )
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_modes_regress_when_decide_then_kill() -> None:
    board = extract_nanogen17_board(live_modes_ok=False)
    out = decide_nanogen17(board=board, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "modes" in out.lower()
