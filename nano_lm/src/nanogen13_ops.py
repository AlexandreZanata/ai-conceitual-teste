"""Wave BC4 H-NANOGEN13: gen-defer gate — not NANOGEN12+rename."""

from __future__ import annotations

from typing import Any, Mapping

from bc_session_ops import (
    BC0_ANTI_FP,
    BC0_GEN_STANCE,
    BC0_NORTH_STAR,
    BC0_SAFE_NOTE,
    BC0_SHIP_LOCK,
    BC0_TRUE_GEN_JUDGE,
)

__all__ = [
    "NANOGEN13_ID",
    "NANOGEN13_THESIS",
    "NANOGEN13_CLAIM",
    "NANOGEN13_SAFE_NOTE",
    "NANOGEN13_ANTI_FP",
    "NANOGEN13_STANCE",
    "NANOGEN13_METHOD",
    "TRUE_GEN_JUDGE",
    "PARENT_NANOGEN6_TRUE_CONTINUE",
    "PARENT_NANOGEN7_TRUE_CONTINUE",
    "PARENT_NANOGEN8_DEFER",
    "PARENT_NANOGEN9_DEFER",
    "PARENT_NANOGEN10_DEFER",
    "PARENT_NANOGEN11_DEFER",
    "PARENT_NANOGEN12_DEFER",
    "decide_nanogen13",
    "method_is_rename",
    "extract_nanogen13_board",
]

NANOGEN13_ID = "H-NANOGEN13"
NANOGEN13_THESIS = (
    "North-star generative gate under BC0 gen stance: PROMOTE only with a "
    "real new train/data/arch method (M1|M2|M3) AND true_continue; else "
    "DEFER/HOLD. CAPCHECK closed; never NANOGEN13 = NANOGEN12+rename; "
    "NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER stand; span-fallback ≠ gen IQ; "
    "mini-AGI locked while deferred"
)
NANOGEN13_CLAIM = BC0_SHIP_LOCK
NANOGEN13_SAFE_NOTE = BC0_SAFE_NOTE
NANOGEN13_ANTI_FP = BC0_ANTI_FP
NANOGEN13_STANCE = dict(BC0_GEN_STANCE)
NANOGEN13_METHOD: Mapping[str, object] = {
    "id": "gen-defer",
    "kind": "defer",
    "real_new_method": False,
    "capcheck": "closed",
    "candidate": "defer",
    "renames_nanogen12": False,
    "renames_nanogen11": False,
    "renames_nanogen10": False,
    "renames_nanogen9": False,
    "renames_nanogen8": False,
    "renames_nanogen7_tac": False,
    "renames_nanogen6": False,
    "rationale": (
        "BC0 froze stance=defer: no real M1|M2|M3 method ready; "
        "NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER stand; CAPCHECK closed; "
        "prefer BC1–BC3 anti-FP/ctx/speed + honest paper over vanity "
        "NANOGEN13 = NANOGEN12+rename"
    ),
}
TRUE_GEN_JUDGE = dict(BC0_TRUE_GEN_JUDGE)
PARENT_NANOGEN6_TRUE_CONTINUE = 0.0
PARENT_NANOGEN7_TRUE_CONTINUE = 0.0
PARENT_NANOGEN8_DEFER = True
PARENT_NANOGEN9_DEFER = True
PARENT_NANOGEN10_DEFER = True
PARENT_NANOGEN11_DEFER = True
PARENT_NANOGEN12_DEFER = True

_RENAME_FLAGS = (
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
    THEN True iff it is NANOGEN6…12 rename theater.
    """
    if any(bool(method.get(f)) for f in _RENAME_FLAGS):
        return True
    kind = str(method.get("kind") or "").lower()
    mid = str(method.get("id") or "").lower()
    if "rename" in kind and any(
        f"nanogen{n}" in mid for n in (6, 7, 8, 9, 10, 11, 12)
    ):
        return True
    return kind in _RENAME_KINDS


def extract_nanogen13_board(
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
    live_modes_ok: bool = True,
) -> dict[str, Any]:
    """
    GIVEN BC0 stance + claimed method + archive true_continue
    WHEN building NANOGEN13 board
    THEN publish defer/method/true_continue honesty fields.
    """
    st = dict(stance) if stance is not None else dict(NANOGEN13_STANCE)
    meth = dict(method) if method is not None else dict(NANOGEN13_METHOD)
    return {
        "stance": str(st.get("stance") or ""),
        "capcheck": str(st.get("capcheck") or meth.get("capcheck") or ""),
        "real_new_method": bool(meth.get("real_new_method")),
        "method_id": str(meth.get("id") or ""),
        "method_kind": str(meth.get("kind") or ""),
        "method_candidate": str(meth.get("candidate") or st.get("stance") or ""),
        "renames_forbidden": bool(st.get("nanogen13_rename_forbidden", True)),
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
        "span_fallback_neq_gen": bool(
            TRUE_GEN_JUDGE.get("span_fallback_neq_gen", True)
        ),
        "live_modes_ok": bool(live_modes_ok),
        "north_star": BC0_NORTH_STAR,
        "ship_lock": NANOGEN13_CLAIM,
    }


def _gate_kill(board: Mapping[str, Any], *, anti_fp_signed: bool) -> str | None:
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    if bool(board.get("is_rename")):
        return "KILL (NANOGEN13 = NANOGEN12/11/10/9/8/7/6 rename forbidden)"
    if not bool(board.get("renames_forbidden", True)):
        return "KILL (nanogen13_rename_forbidden must stay True)"
    if not bool(board.get("live_modes_ok", True)):
        return "KILL (live product modes regress on gen gate path)"
    if not bool(board.get("span_fallback_neq_gen", True)):
        return "KILL (span-fallback ≠ gen law missing)"
    return None


def _decide_promote_or_hold(board: Mapping[str, Any]) -> str:
    stance = str(board.get("stance") or "")
    real = bool(board.get("real_new_method"))
    tc = float(board.get("true_continue_mean") or 0.0)
    n_tc = int(board.get("n_true_continue") or 0)
    if real and n_tc > 0 and tc >= 5.5:
        return (
            f"PROMOTE ({NANOGEN13_ID}: real new method + "
            f"true_continue={tc:.1f})"
        )
    if stance == "defer" or not real:
        return (
            f"DEFER ({NANOGEN13_ID}: stance={stance or 'unset'}; "
            "CAPCHECK closed; no real M1|M2|M3; "
            "NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER stand; "
            "not NANOGEN12 rename)"
        )
    return (
        f"HOLD ({NANOGEN13_ID}: method claimed but true_continue "
        f"{tc:.1f} unmet; span-fallback ≠ gen)"
    )


def decide_nanogen13(
    *,
    board: Mapping[str, Any],
    anti_fp_signed: bool = True,
) -> str:
    """
    GIVEN NANOGEN13 board (stance · method · true_continue)
    WHEN applying pesquisa §9 BC4
    THEN PROMOTE only real M1|M2|M3 + true_continue; else DEFER/HOLD;
         KILL on rename / unsigned anti-FP / mode regress.
    """
    err = _gate_kill(board, anti_fp_signed=anti_fp_signed)
    if err:
        return err
    return _decide_promote_or_hold(board)
