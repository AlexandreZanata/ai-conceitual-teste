"""Wave BE5 H-NANOGEN15: gen-defer-once gate — not NANOGEN14+rename."""

from __future__ import annotations

from typing import Any, Mapping

from be_session_ops import (
    BE0_ANTI_FP,
    BE0_GEN_STANCE,
    BE0_NORTH_STAR,
    BE0_SAFE_NOTE,
    BE0_SHIP_LOCK,
    BE0_TRUE_GEN_JUDGE,
)

__all__ = [
    "NANOGEN15_ID",
    "NANOGEN15_THESIS",
    "NANOGEN15_CLAIM",
    "NANOGEN15_SAFE_NOTE",
    "NANOGEN15_ANTI_FP",
    "NANOGEN15_STANCE",
    "NANOGEN15_METHOD",
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
    "decide_nanogen15",
    "method_is_rename",
    "extract_nanogen15_board",
]

NANOGEN15_ID = "H-NANOGEN15"
NANOGEN15_THESIS = (
    "North-star generative gate under BE0 gen stance: PROMOTE only with a "
    "real new train/data/arch method (M1|M2|M3) AND true_continue; else "
    "DEFER once (stop rule). CAPCHECK closed; never NANOGEN15 = NANOGEN14+rename; "
    "NANOGEN6·7 HOLD · NANOGEN8…14 DEFER stand; "
    "span-fallback ≠ gen IQ; mini-AGI locked while deferred"
)
NANOGEN15_CLAIM = BE0_SHIP_LOCK
NANOGEN15_SAFE_NOTE = BE0_SAFE_NOTE
NANOGEN15_ANTI_FP = BE0_ANTI_FP
NANOGEN15_STANCE = dict(BE0_GEN_STANCE)
NANOGEN15_METHOD: Mapping[str, object] = {
    "id": "gen-defer-once",
    "kind": "defer",
    "real_new_method": False,
    "capcheck": "closed",
    "candidate": "defer",
    "renames_nanogen14": False,
    "renames_nanogen13": False,
    "renames_nanogen12": False,
    "renames_nanogen11": False,
    "renames_nanogen10": False,
    "renames_nanogen9": False,
    "renames_nanogen8": False,
    "renames_nanogen7_tac": False,
    "renames_nanogen6": False,
    "rationale": (
        "BE0 froze stance=defer: no real M1|M2|M3 method ready; "
        "NANOGEN6·7 HOLD · NANOGEN8…14 DEFER stand; CAPCHECK closed; "
        "prefer H-COMPINT + H-SHIPUSE + H-FASTBE + H-CTXBE + honest paper "
        "over vanity NANOGEN15 = NANOGEN14+rename; DEFER once stop rule"
    ),
}
TRUE_GEN_JUDGE = dict(BE0_TRUE_GEN_JUDGE)
PARENT_NANOGEN6_TRUE_CONTINUE = 0.0
PARENT_NANOGEN7_TRUE_CONTINUE = 0.0
PARENT_NANOGEN8_DEFER = True
PARENT_NANOGEN9_DEFER = True
PARENT_NANOGEN10_DEFER = True
PARENT_NANOGEN11_DEFER = True
PARENT_NANOGEN12_DEFER = True
PARENT_NANOGEN13_DEFER = True
PARENT_NANOGEN14_DEFER = True

_RENAME_FLAGS = (
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
    THEN True iff it is NANOGEN6…14 rename theater.
    """
    if any(bool(method.get(f)) for f in _RENAME_FLAGS):
        return True
    kind = str(method.get("kind") or "").lower()
    mid = str(method.get("id") or "").lower()
    if "rename" in kind and any(
        f"nanogen{n}" in mid for n in (6, 7, 8, 9, 10, 11, 12, 13, 14)
    ):
        return True
    return kind in _RENAME_KINDS


def extract_nanogen15_board(
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
    live_modes_ok: bool = True,
) -> dict[str, Any]:
    """
    GIVEN BE0 stance + claimed method + archive true_continue
    WHEN building NANOGEN15 board
    THEN publish defer/method/true_continue honesty fields.
    """
    st = dict(stance) if stance is not None else dict(NANOGEN15_STANCE)
    meth = dict(method) if method is not None else dict(NANOGEN15_METHOD)
    return {
        "stance": str(st.get("stance") or ""),
        "capcheck": str(st.get("capcheck") or meth.get("capcheck") or ""),
        "real_new_method": bool(meth.get("real_new_method")),
        "method_id": str(meth.get("id") or ""),
        "method_kind": str(meth.get("kind") or ""),
        "method_candidate": str(meth.get("candidate") or st.get("stance") or ""),
        "renames_forbidden": bool(st.get("nanogen15_rename_forbidden", True)),
        "defer_once_stop_rule": bool(st.get("defer_once_stop_rule", True)),
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
        "span_fallback_neq_gen": bool(
            TRUE_GEN_JUDGE.get("span_fallback_neq_gen", True)
        ),
        "live_modes_ok": bool(live_modes_ok),
        "north_star": BE0_NORTH_STAR,
        "ship_lock": NANOGEN15_CLAIM,
    }


def _gate_kill(board: Mapping[str, Any], *, anti_fp_signed: bool) -> str | None:
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    if bool(board.get("is_rename")):
        return "KILL (NANOGEN15 = NANOGEN14/13/…/6 rename forbidden)"
    if not bool(board.get("renames_forbidden", True)):
        return "KILL (nanogen15_rename_forbidden must stay True)"
    if not bool(board.get("defer_once_stop_rule", True)):
        return "KILL (defer-once stop rule must stay True)"
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
            f"PROMOTE ({NANOGEN15_ID}: real new method + "
            f"true_continue={tc:.1f})"
        )
    if stance == "defer" or not real:
        return (
            f"DEFER ({NANOGEN15_ID}: stance={stance or 'unset'}; "
            "CAPCHECK closed; no real M1|M2|M3; DEFER once stop rule; "
            "NANOGEN6·7 HOLD · NANOGEN8…14 DEFER stand; "
            "not NANOGEN14 rename)"
        )
    return (
        f"HOLD ({NANOGEN15_ID}: method claimed but true_continue "
        f"{tc:.1f} unmet; span-fallback ≠ gen)"
    )


def decide_nanogen15(
    *,
    board: Mapping[str, Any],
    anti_fp_signed: bool = True,
) -> str:
    """
    GIVEN NANOGEN15 board (stance · method · true_continue)
    WHEN applying pesquisa §9 BE5
    THEN PROMOTE only real M1|M2|M3 + true_continue; else DEFER/HOLD;
         KILL on rename / unsigned anti-FP / mode regress.
    """
    err = _gate_kill(board, anti_fp_signed=anti_fp_signed)
    if err:
        return err
    return _decide_promote_or_hold(board)
