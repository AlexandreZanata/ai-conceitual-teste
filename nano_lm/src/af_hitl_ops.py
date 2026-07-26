"""Wave AF5 AF-HITL-10: final verify on declared AF packaged stack."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from appultra_ops import select_app as select_app_meta
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "AF5_ID",
    "AF5_N",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "DECLARED_STACK",
    "STACK_CLAIM",
    "select_app",
    "claim_is_honest",
    "score_af5_trial",
    "af5_stats",
    "decide_af5",
]

AF5_ID = "AF-HITL-10"
AF5_N = 10
DECLARED_STACK: tuple[str, ...] = (
    "H-ZWRAP",
    "H-WRAPBANK",
    "H-SEMWRAP",
    "H-ASKFAST",
    "H-ASKSMART",
    "H-CTXULTRA",
    "H-SMARTULTRA",
    "H-FASTULTRA",
    "H-APPULTRA",
)
STACK_CLAIM = (
    "scoped AF packaged stack "
    "(CTXULTRA+SMARTULTRA+FASTULTRA+APPULTRA) — not open chat LM"
)


def select_app(item_app_id: str) -> str:
    """
    GIVEN pack item app_id
    WHEN routing on the declared AF stack
    THEN return APPULTRA canonical app_id (not app-route/compose).
    """
    return str(select_app_meta(item_app_id)["app_id"])


def claim_is_honest(claim: str) -> bool:
    low = str(claim).lower()
    if "open chat" in low and "not open chat" not in low:
        return False
    return "scoped" in low or "packaged" in low


def score_af5_trial(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    ctx_ok: bool | None = None,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN final AF-stack ask result
    WHEN scoring HITL (§5 AF5)
    THEN FALSE_HIT→0; TRUE_HIT→9; CTXULTRA ctx fail marks error.
    """
    from semwrap_ops import score_semwrap_trial

    score, err, notes = score_semwrap_trial(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
    )
    notes = list(notes) + ["AF5 final stack — not open chat LM"]
    if ctx_ok is False:
        err = True
        notes.append("CTXULTRA_CTX_FAIL")
    return float(score), bool(err), notes


def af5_stats(
    scores: Sequence[float],
    errors: Sequence[bool],
    *,
    n_true_hit: int,
    n_false_hit: int,
    n_miss: int,
    n_fix: int,
    claim_ok: bool,
    held_out_ok: bool,
    n_known_app: int,
    n_long_app: int,
    n_howto_app: int,
) -> dict[str, Any]:
    if len(scores) != AF5_N or len(errors) != AF5_N:
        raise ValueError(f"AF5 requires exactly {AF5_N} scores/errors")
    mean = float(sum(float(s) for s in scores) / float(AF5_N))
    n_err = int(sum(1 for e in errors if e))
    return {
        "n_trials": AF5_N,
        "mean": mean,
        "n_errors": n_err,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_miss": int(n_miss),
        "n_fix": int(n_fix),
        "claim_ok": bool(claim_ok),
        "held_out_ok": bool(held_out_ok),
        "n_known_app": int(n_known_app),
        "n_long_app": int(n_long_app),
        "n_howto_app": int(n_howto_app),
        "pass_bar": mean >= PASS_MEAN and n_err <= PASS_MAX_ERRORS,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
        "stack": list(DECLARED_STACK),
    }


def decide_af5(stats: Mapping[str, Any]) -> str:
    """
    GIVEN AF5 final HITL stats
    WHEN applying §5 AF5 gate
    THEN PROMOTE if pass_bar ∧ claim_ok ∧ held_out ∧ no false-hit;
         HOLD if claim soft-miss but pass_bar;
         KILL if false-hit / quality / pack overlap fail.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("held_out_ok")):
        return "KILL"
    if not bool(stats.get("pass_bar")):
        return "KILL"
    if not bool(stats.get("claim_ok")):
        return "HOLD"
    return "PROMOTE"
