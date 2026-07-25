"""Contract: H-TCHR dual-teacher wire decision (story + code_teacher_lp)."""

from __future__ import annotations

from tchr_ops import (
    CODE_TEACHER_ID,
    CODE_TEACHER_LICENSE,
    CODE_TEACHER_PARAMS,
    STORY_REGRESS_FLOOR,
    code_teacher_meta,
    decide_htchr,
    lp_finite,
)


def test_given_catalog_when_meta_then_named_code_teacher() -> None:
    m = code_teacher_meta()
    assert m["hf_id"] == CODE_TEACHER_ID
    assert m["params"] == CODE_TEACHER_PARAMS
    assert m["license"] == CODE_TEACHER_LICENSE
    assert m["role"] == "code_teacher"


def test_given_finite_lp_when_check_then_true() -> None:
    assert lp_finite(-8.2) is True
    assert lp_finite(float("-inf")) is False
    assert lp_finite(float("nan")) is False


def test_given_stable_dual_when_decide_then_promote() -> None:
    out = decide_htchr(
        code_teacher=code_teacher_meta(),
        mean_story_lp=-8.2,
        mean_code_lp=-3.5,
        n_rows=4,
    )
    assert out.startswith("PROMOTE")
    assert "code_teacher_lp" in out


def test_given_story_collapse_when_decide_then_kill() -> None:
    out = decide_htchr(
        code_teacher=code_teacher_meta(),
        mean_story_lp=STORY_REGRESS_FLOOR - 1.0,
        mean_code_lp=-3.5,
        n_rows=4,
    )
    assert out.startswith("KILL")
    assert "story" in out.lower()


def test_given_nonfinite_code_lp_when_decide_then_kill() -> None:
    out = decide_htchr(
        code_teacher=code_teacher_meta(),
        mean_story_lp=-8.0,
        mean_code_lp=float("-inf"),
        n_rows=4,
    )
    assert out.startswith("KILL")
    assert "code_teacher_lp" in out


def test_given_wrong_hf_id_when_decide_then_kill() -> None:
    meta = {**code_teacher_meta(), "hf_id": "other/model"}
    out = decide_htchr(
        code_teacher=meta,
        mean_story_lp=-8.0,
        mean_code_lp=-3.0,
        n_rows=2,
    )
    assert out.startswith("KILL")
    assert "hf_id" in out


def test_given_no_rows_when_decide_then_kill() -> None:
    out = decide_htchr(
        code_teacher=code_teacher_meta(),
        mean_story_lp=-8.0,
        mean_code_lp=-3.0,
        n_rows=0,
    )
    assert out.startswith("KILL")
