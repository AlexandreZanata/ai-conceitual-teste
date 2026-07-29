"""Wave BF5 H-NANOGEN16: gen-SKIP gate — not empty DEFER · not NANOGEN15+rename."""

from __future__ import annotations

from typing import Any, Mapping

from bf_session_ops import (
    BF0_ANTI_FP,
    BF0_GEN_STANCE,
    BF0_NORTH_STAR,
    BF0_SAFE_NOTE,
    BF0_SHIP_LOCK,
    BF0_TRUE_GEN_JUDGE,
)

__all__ = [
    "NANOGEN16_ID",
    "NANOGEN16_THESIS",
    "NANOGEN16_CLAIM",
    "NANOGEN16_SAFE_NOTE",
    "NANOGEN16_ANTI_FP",
    "NANOGEN16_STANCE",
    "NANOGEN16_METHOD",
    "TRUE_GEN_JUDGE",
    "PARENT_NANOGEN6_TRUE_CONTINUE",
    "PARENT_NANOGEN7_TRUE_CONTINUE",
    "PARENT_NANOGEN8_DEFER",
    "PARENT_NANOGEN9_DEFER",
    "PARENT_NANOGEN10_DEFER",
    "PARENT_NANOGEN11_DEFER",
    "PARENT_NANOGEN12_DEFER",
    "PARENT_NANOGEN13_DEFER",
    "PARENT_NANOGEN14_DEFER",
    "PARENT_NANOGEN15_DEFER",
    "decide_nanogen16",
    "method_is_rename",
    "extract_nanogen16_board",
]

NANOGEN16_ID = "H-NANOGEN16"
NANOGEN16_THESIS = (
    "North-star generative gate under BF0 gen stance: PROMOTE only with a "
    "written M1|M2|M3 method plan AND true_continue; else SKIP stage "
    "(stop rule — not empty DEFER letter). CAPCHECK closed; never "
    "NANOGEN16 = NANOGEN15+rename; NANOGEN6·7 HOLD · NANOGEN8…15 DEFER stand; "
    "span-fallback ≠ gen IQ; mini-AGI locked while skipped"
)
NANOGEN16_CLAIM = BF0_SHIP_LOCK
NANOGEN16_SAFE_NOTE = BF0_SAFE_NOTE
NANOGEN16_ANTI_FP = BF0_ANTI_FP
NANOGEN16_STANCE = dict(BF0_GEN_STANCE)
NANOGEN16_METHOD: Mapping[str, object] = {
    "id": "gen-skip-no-plan",
    "kind": "skip",
    "real_new_method": False,
    "method_plan_attached": False,
    "capcheck": "closed",
    "candidate": "skip",
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
    "empty_defer_letter": False,
    "rationale": (
        "BF0 froze stance=skip: no written M1|M2|M3 plan; "
        "H-NANOGEN15 already DEFER once — forbid empty NANOGEN16 DEFER letter; "
        "NANOGEN6·7 HOLD · NANOGEN8…15 DEFER stand; CAPCHECK closed; "
        "prefer H-PREDINT + H-SHIPUSE2 + H-FASTBF + H-CTXBF + honest paper "
        "over vanity NANOGEN16 rename; BF5 = SKIP stage"
    ),
}
TRUE_GEN_JUDGE = dict(BF0_TRUE_GEN_JUDGE)
PARENT_NANOGEN6_TRUE_CONTINUE = 0.0
PARENT_NANOGEN7_TRUE_CONTINUE = 0.0
PARENT_NANOGEN8_DEFER = True
PARENT_NANOGEN9_DEFER = True
PARENT_NANOGEN10_DEFER = True
PARENT_NANOGEN11_DEFER = True
PARENT_NANOGEN12_DEFER = True
PARENT_NANOGEN13_DEFER = True
PARENT_NANOGEN14_DEFER = True
PARENT_NANOGEN15_DEFER = True

_RENAME_FLAGS = (
    "renames_nanogen15",
    "renames_nanogen14",
    "renames_nanogen13",
    "renames_nanogen12",
    "renames_nanogen11",
    "renames_nanogen10",
    "renames_nanogen9",
    "renames_nanogen8",
    "renames_nanogen7_tac",
    "renames_nanogen6",
)
_RENAME_KINDS = frozenset(
    {
        "tac_rename",
        "nanogen15_rename",
        "nanogen14_rename",
        "nanogen13_rename",
        "nanogen12_rename",
        "nanogen11_rename",
        "nanogen10_rename",
        "nanogen9_rename",
        "nanogen8_rename",
        "nanogen7_rename",
        "nanogen6_rename",
    }
)


def method_is_rename(method: Mapping[str, object]) -> bool:
    """
    GIVEN a claimed generative method
    WHEN checking anti-clone law
    THEN True iff it is NANOGEN6…15 rename theater.
    """
    if any(bool(method.get(f)) for f in _RENAME_FLAGS):
        return True
    kind = str(method.get("kind") or "").lower()
    mid = str(method.get("id") or "").lower()
    if "rename" in kind and any(
        f"nanogen{n}" in mid for n in (6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
    ):
        return True
    return kind in _RENAME_KINDS


def extract_nanogen16_board(
    *,
    stance: Mapping[str, object] | None = None,
    method: Mapping[str, object] | None = None,
    true_continue_mean: float = 0.0,
    n_true_continue: int = 0,
    n_span_fallback: int = 0,
    parent6: float = PARENT_NANOGEN6_TRUE_CONTINUE,
    parent7: float = PARENT_NANOGEN7_TRUE_CONTINUE,
    parent8_defer: bool = PARENT_NANOGEN8_DEFER,
    parent9_defer: bool = PARENT_NANOGEN9_DEFER,
    parent10_defer: bool = PARENT_NANOGEN10_DEFER,
    parent11_defer: bool = PARENT_NANOGEN11_DEFER,
    parent12_defer: bool = PARENT_NANOGEN12_DEFER,
    parent13_defer: bool = PARENT_NANOGEN13_DEFER,
    parent14_defer: bool = PARENT_NANOGEN14_DEFER,
    parent15_defer: bool = PARENT_NANOGEN15_DEFER,
    live_modes_ok: bool = True,
) -> dict[str, Any]:
    """
    GIVEN BF0 stance + claimed method + archive true_continue
    WHEN building NANOGEN16 board
    THEN publish skip/method/true_continue honesty fields.
    """
    st = dict(stance) if stance is not None else dict(NANOGEN16_STANCE)
    meth = dict(method) if method is not None else dict(NANOGEN16_METHOD)
    plan = bool(
        st.get("method_plan_attached", meth.get("method_plan_attached", False))
    )
    return {
        "stance": str(st.get("stance") or ""),
        "capcheck": str(st.get("capcheck") or meth.get("capcheck") or ""),
        "real_new_method": bool(meth.get("real_new_method")),
        "method_plan_attached": plan,
        "method_id": str(meth.get("id") or ""),
        "method_kind": str(meth.get("kind") or ""),
        "method_candidate": str(meth.get("candidate") or st.get("stance") or ""),
        "renames_forbidden": bool(st.get("nanogen16_rename_forbidden", True)),
        "skip_gen_stop_rule": bool(st.get("skip_gen_stop_rule", True)),
        "nanogen16_without_plan_forbidden": bool(
            st.get("nanogen16_without_plan_forbidden", True)
        ),
        "empty_defer_letter": bool(meth.get("empty_defer_letter", False)),
        "is_rename": method_is_rename(meth),
        "true_continue_mean": float(true_continue_mean),
        "n_true_continue": int(n_true_continue),
        "n_span_fallback": int(n_span_fallback),
        "parent_nanogen6_true_continue": float(parent6),
        "parent_nanogen7_true_continue": float(parent7),
        "parent_nanogen8_defer": bool(parent8_defer),
        "parent_nanogen9_defer": bool(parent9_defer),
        "parent_nanogen10_defer": bool(parent10_defer),
        "parent_nanogen11_defer": bool(parent11_defer),
        "parent_nanogen12_defer": bool(parent12_defer),
        "parent_nanogen13_defer": bool(parent13_defer),
        "parent_nanogen14_defer": bool(parent14_defer),
        "parent_nanogen15_defer": bool(parent15_defer),
        "span_fallback_neq_gen": bool(
            TRUE_GEN_JUDGE.get("span_fallback_neq_gen", True)
        ),
        "live_modes_ok": bool(live_modes_ok),
        "north_star": BF0_NORTH_STAR,
        "ship_lock": NANOGEN16_CLAIM,
        "bf5_gate": str(st.get("bf5_gate") or ""),
    }


def _gate_kill(board: Mapping[str, Any], *, anti_fp_signed: bool) -> str | None:
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    if bool(board.get("is_rename")):
        return "KILL (NANOGEN16 = NANOGEN15/14/…/6 rename forbidden)"
    if not bool(board.get("renames_forbidden", True)):
        return "KILL (nanogen16_rename_forbidden must stay True)"
    if not bool(board.get("skip_gen_stop_rule", True)):
        return "KILL (skip-gen stop rule must stay True)"
    if not bool(board.get("nanogen16_without_plan_forbidden", True)):
        return "KILL (NANOGEN16 without plan must stay forbidden)"
    if bool(board.get("empty_defer_letter")):
        return "KILL (empty DEFER letter forbidden — use SKIP)"
    if not bool(board.get("live_modes_ok", True)):
        return "KILL (live product modes regress on gen gate path)"
    if not bool(board.get("span_fallback_neq_gen", True)):
        return "KILL (span-fallback ≠ gen law missing)"
    return None


def _decide_promote_hold_or_skip(board: Mapping[str, Any]) -> str:
    stance = str(board.get("stance") or "")
    real = bool(board.get("real_new_method"))
    plan = bool(board.get("method_plan_attached"))
    tc = float(board.get("true_continue_mean") or 0.0)
    n_tc = int(board.get("n_true_continue") or 0)
    if plan and real and n_tc > 0 and tc >= 5.5:
        return (
            f"PROMOTE ({NANOGEN16_ID}: written M1|M2|M3 plan + "
            f"true_continue={tc:.1f})"
        )
    if stance == "skip" or not plan or not real:
        return (
            f"SKIP ({NANOGEN16_ID}: stance={stance or 'unset'}; "
            "no written M1|M2|M3 plan; CAPCHECK closed; "
            "not empty DEFER letter; NANOGEN6·7 HOLD · NANOGEN8…15 DEFER stand; "
            "not NANOGEN15 rename)"
        )
    return (
        f"HOLD ({NANOGEN16_ID}: plan/method claimed but true_continue "
        f"{tc:.1f} unmet; span-fallback ≠ gen)"
    )


def decide_nanogen16(
    *,
    board: Mapping[str, Any],
    anti_fp_signed: bool = True,
) -> str:
    """
    GIVEN NANOGEN16 board (stance · method · true_continue)
    WHEN applying pesquisa §9 BF5
    THEN PROMOTE only written plan + real M1|M2|M3 + true_continue;
         else SKIP (not empty DEFER); HOLD if plan without tc;
         KILL on rename / empty DEFER / unsigned anti-FP / mode regress.
    """
    err = _gate_kill(board, anti_fp_signed=anti_fp_signed)
    if err:
        return err
    return _decide_promote_hold_or_skip(board)
