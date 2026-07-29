"""Wave BG5 H-NANOGEN17: gen-SKIP gate — not empty DEFER · not NANOGEN16+rename."""

from __future__ import annotations

from typing import Any, Mapping

from bg_session_ops import (
    BG0_ANTI_FP,
    BG0_GEN_STANCE,
    BG0_NORTH_STAR,
    BG0_SAFE_NOTE,
    BG0_SHIP_LOCK,
    BG0_TRUE_GEN_JUDGE,
)

__all__ = [
    "NANOGEN17_ID",
    "NANOGEN17_THESIS",
    "NANOGEN17_CLAIM",
    "NANOGEN17_SAFE_NOTE",
    "NANOGEN17_ANTI_FP",
    "NANOGEN17_STANCE",
    "NANOGEN17_METHOD",
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
    "PARENT_NANOGEN16_SKIP",
    "decide_nanogen17",
    "method_is_rename",
    "extract_nanogen17_board",
]

NANOGEN17_ID = "H-NANOGEN17"
NANOGEN17_THESIS = (
    "North-star generative gate under BG0 gen stance: PROMOTE only with a "
    "written M1|M2|M3 method plan AND true_continue; else SKIP stage "
    "(stop rule — not empty DEFER letter). CAPCHECK closed; never "
    "NANOGEN17 = NANOGEN16+rename; NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · "
    "NANOGEN16 SKIP stand; span-fallback ≠ gen IQ; mini-AGI locked while "
    "skipped"
)
NANOGEN17_CLAIM = BG0_SHIP_LOCK
NANOGEN17_SAFE_NOTE = BG0_SAFE_NOTE
NANOGEN17_ANTI_FP = BG0_ANTI_FP
NANOGEN17_STANCE = dict(BG0_GEN_STANCE)
NANOGEN17_METHOD: Mapping[str, object] = {
    "id": "gen-skip-no-plan",
    "kind": "skip",
    "real_new_method": False,
    "method_plan_attached": False,
    "capcheck": "closed",
    "candidate": "skip",
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
    "empty_defer_letter": False,
    "rationale": (
        "BG0 froze stance=skip: no written M1|M2|M3 plan; "
        "H-NANOGEN16 already SKIP once — forbid empty NANOGEN17 letter; "
        "NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · NANOGEN16 SKIP stand; "
        "CAPCHECK closed; prefer H-UNARYINT + H-SHIPPUB + H-FASTBG + "
        "H-CTXBG + honest paper over vanity NANOGEN17 rename; "
        "BG5 = SKIP stage"
    ),
}
TRUE_GEN_JUDGE = dict(BG0_TRUE_GEN_JUDGE)
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
PARENT_NANOGEN16_SKIP = True

_RENAME_FLAGS = (
    "renames_nanogen16",
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
        "nanogen16_rename",
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
    THEN True iff it is NANOGEN6…16 rename theater.
    """
    if any(bool(method.get(f)) for f in _RENAME_FLAGS):
        return True
    kind = str(method.get("kind") or "").lower()
    mid = str(method.get("id") or "").lower()
    if "rename" in kind and any(
        f"nanogen{n}" in mid for n in range(6, 17)
    ):
        return True
    return kind in _RENAME_KINDS


def extract_nanogen17_board(
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
    parent16_skip: bool = PARENT_NANOGEN16_SKIP,
    live_modes_ok: bool = True,
) -> dict[str, Any]:
    """
    GIVEN BG0 stance + claimed method + archive true_continue
    WHEN building NANOGEN17 board
    THEN publish skip/method/true_continue honesty fields.
    """
    st = dict(stance) if stance is not None else dict(NANOGEN17_STANCE)
    meth = dict(method) if method is not None else dict(NANOGEN17_METHOD)
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
        "renames_forbidden": bool(st.get("nanogen17_rename_forbidden", True)),
        "skip_gen_stop_rule": bool(st.get("skip_gen_stop_rule", True)),
        "nanogen17_without_plan_forbidden": bool(
            st.get("nanogen17_without_plan_forbidden", True)
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
        "parent_nanogen16_skip": bool(parent16_skip),
        "span_fallback_neq_gen": bool(
            TRUE_GEN_JUDGE.get("span_fallback_neq_gen", True)
        ),
        "live_modes_ok": bool(live_modes_ok),
        "north_star": BG0_NORTH_STAR,
        "ship_lock": NANOGEN17_CLAIM,
        "bg5_gate": str(st.get("bg5_gate") or ""),
    }


def _gate_kill(board: Mapping[str, Any], *, anti_fp_signed: bool) -> str | None:
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    if bool(board.get("is_rename")):
        return "KILL (NANOGEN17 = NANOGEN16/15/…/6 rename forbidden)"
    if not bool(board.get("renames_forbidden", True)):
        return "KILL (nanogen17_rename_forbidden must stay True)"
    if not bool(board.get("skip_gen_stop_rule", True)):
        return "KILL (skip-gen stop rule must stay True)"
    if not bool(board.get("nanogen17_without_plan_forbidden", True)):
        return "KILL (NANOGEN17 without plan must stay forbidden)"
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
            f"PROMOTE ({NANOGEN17_ID}: written M1|M2|M3 plan + "
            f"true_continue={tc:.1f})"
        )
    if stance == "skip" or not plan or not real:
        return (
            f"SKIP ({NANOGEN17_ID}: stance={stance or 'unset'}; "
            "no written M1|M2|M3 plan; CAPCHECK closed; "
            "not empty DEFER letter; NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · "
            "NANOGEN16 SKIP stand; not NANOGEN16 rename)"
        )
    return (
        f"HOLD ({NANOGEN17_ID}: plan/method claimed but true_continue "
        f"{tc:.1f} unmet; span-fallback ≠ gen)"
    )


def decide_nanogen17(
    *,
    board: Mapping[str, Any],
    anti_fp_signed: bool = True,
) -> str:
    """
    GIVEN NANOGEN17 board (stance · method · true_continue)
    WHEN applying pesquisa §9 BG5
    THEN PROMOTE only written plan + real M1|M2|M3 + true_continue;
         else SKIP (not empty DEFER); HOLD if plan without tc;
         KILL on rename / empty DEFER / unsigned anti-FP / mode regress.
    """
    err = _gate_kill(board, anti_fp_signed=anti_fp_signed)
    if err:
        return err
    return _decide_promote_hold_or_skip(board)
