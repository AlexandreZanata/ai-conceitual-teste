"""Wave AX3 H-NANOGEN8: gen-defer gate — not NANOGEN7+rename."""

from __future__ import annotations

from typing import Any, Mapping

from ax_session_ops import (
    AX0_ANTI_FP,
    AX0_GEN_STANCE,
    AX0_NORTH_STAR,
    AX0_SAFE_NOTE,
    AX0_SHIP_LOCK,
    AX0_TRUE_GEN_JUDGE,
)

__all__ = [
    "NANOGEN8_ID",
    "NANOGEN8_THESIS",
    "NANOGEN8_CLAIM",
    "NANOGEN8_SAFE_NOTE",
    "NANOGEN8_ANTI_FP",
    "NANOGEN8_STANCE",
    "NANOGEN8_METHOD",
    "TRUE_GEN_JUDGE",
    "PARENT_NANOGEN6_TRUE_CONTINUE",
    "PARENT_NANOGEN7_TRUE_CONTINUE",
    "decide_nanogen8",
    "method_is_rename",
    "extract_nanogen8_board",
]

NANOGEN8_ID = "H-NANOGEN8"
NANOGEN8_THESIS = (
    "North-star generative gate under AX0 gen stance: PROMOTE only with a "
    "real new train/data/arch method AND true_continue; else DEFER/HOLD. "
    "CAPCHECK closed; never NANOGEN8 = NANOGEN7 TAC rename; "
    "span-fallback ≠ gen IQ; mini-AGI locked while deferred"
)
NANOGEN8_CLAIM = AX0_SHIP_LOCK
NANOGEN8_SAFE_NOTE = AX0_SAFE_NOTE
NANOGEN8_ANTI_FP = AX0_ANTI_FP
NANOGEN8_STANCE = dict(AX0_GEN_STANCE)
NANOGEN8_METHOD: Mapping[str, object] = {
    "id": "gen-defer",
    "kind": "defer",
    "real_new_method": False,
    "capcheck": "closed",
    "renames_nanogen7_tac": False,
    "renames_nanogen6": False,
    "rationale": (
        "AX0 froze stance=defer: no real new train/data/arch ready; "
        "NANOGEN6·7 HOLD (true_continue=0) stands; prefer product ship "
        "+ honest paper over vanity NANOGEN8 clone"
    ),
}
TRUE_GEN_JUDGE = dict(AX0_TRUE_GEN_JUDGE)
PARENT_NANOGEN6_TRUE_CONTINUE = 0.0
PARENT_NANOGEN7_TRUE_CONTINUE = 0.0


def method_is_rename(method: Mapping[str, object]) -> bool:
    """
    GIVEN a claimed generative method
    WHEN checking anti-clone law
    THEN True iff it is NANOGEN6/7 rename theater.
    """
    if bool(method.get("renames_nanogen7_tac")):
        return True
    if bool(method.get("renames_nanogen6")):
        return True
    kind = str(method.get("kind") or "").lower()
    mid = str(method.get("id") or "").lower()
    if "nanogen7" in mid and "rename" in kind:
        return True
    if kind in {"tac_rename", "nanogen7_rename", "nanogen6_rename"}:
        return True
    return False


def extract_nanogen8_board(
    *,
    stance: Mapping[str, object] | None = None,
    method: Mapping[str, object] | None = None,
    true_continue_mean: float = 0.0,
    n_true_continue: int = 0,
    n_span_fallback: int = 0,
    parent6: float = PARENT_NANOGEN6_TRUE_CONTINUE,
    parent7: float = PARENT_NANOGEN7_TRUE_CONTINUE,
    live_modes_ok: bool = True,
) -> dict[str, Any]:
    """
    GIVEN AX0 stance + claimed method + optional live true_continue probe
    WHEN building NANOGEN8 board
    THEN publish defer/method/true_continue honesty fields.
    """
    st = dict(stance) if stance is not None else dict(NANOGEN8_STANCE)
    meth = dict(method) if method is not None else dict(NANOGEN8_METHOD)
    return {
        "stance": str(st.get("stance") or ""),
        "capcheck": str(st.get("capcheck") or meth.get("capcheck") or ""),
        "real_new_method": bool(meth.get("real_new_method")),
        "method_id": str(meth.get("id") or ""),
        "method_kind": str(meth.get("kind") or ""),
        "renames_forbidden": bool(st.get("nanogen8_rename_forbidden", True)),
        "is_rename": method_is_rename(meth),
        "true_continue_mean": float(true_continue_mean),
        "n_true_continue": int(n_true_continue),
        "n_span_fallback": int(n_span_fallback),
        "parent_nanogen6_true_continue": float(parent6),
        "parent_nanogen7_true_continue": float(parent7),
        "span_fallback_neq_gen": bool(
            TRUE_GEN_JUDGE.get("span_fallback_neq_gen", True)
        ),
        "live_modes_ok": bool(live_modes_ok),
        "north_star": AX0_NORTH_STAR,
        "ship_lock": NANOGEN8_CLAIM,
    }


def decide_nanogen8(
    *,
    board: Mapping[str, Any],
    anti_fp_signed: bool = True,
) -> str:
    """
    GIVEN NANOGEN8 board (stance · method · true_continue)
    WHEN applying pesquisa §5 AX3
    THEN PROMOTE only real method + true_continue; else DEFER/HOLD;
         KILL on rename / unsigned anti-FP / CAPCHECK reopen without method.
    """
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    if bool(board.get("is_rename")):
        return "KILL (NANOGEN8 = NANOGEN7/6 rename forbidden)"
    if not bool(board.get("renames_forbidden", True)):
        return "KILL (nanogen8_rename_forbidden must stay True)"
    if not bool(board.get("live_modes_ok", True)):
        return "KILL (live product modes regress on gen gate path)"
    if not bool(board.get("span_fallback_neq_gen", True)):
        return "KILL (span-fallback ≠ gen law missing)"
    stance = str(board.get("stance") or "")
    real = bool(board.get("real_new_method"))
    tc = float(board.get("true_continue_mean") or 0.0)
    n_tc = int(board.get("n_true_continue") or 0)
    if real and n_tc > 0 and tc >= 5.5:
        return (
            f"PROMOTE ({NANOGEN8_ID}: real new method + "
            f"true_continue={tc:.1f})"
        )
    if stance == "defer" or not real:
        return (
            f"DEFER ({NANOGEN8_ID}: stance={stance or 'unset'}; "
            "CAPCHECK closed; no real new method; "
            "NANOGEN6·7 HOLD stand; not TAC rename)"
        )
    return (
        f"HOLD ({NANOGEN8_ID}: method claimed but true_continue "
        f"{tc:.1f} unmet; span-fallback ≠ gen)"
    )
