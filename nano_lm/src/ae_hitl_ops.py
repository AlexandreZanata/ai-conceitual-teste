"""Wave AE5 AE-HITL-10: final verify on declared AE packaged stack."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from appmax_ops import select_app as select_app_meta
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "AE5_ID",
    "AE5_N",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "DECLARED_STACK",
    "STACK_CLAIM",
    "select_app",
    "claim_is_honest",
    "score_ae5_trial",
    "ae5_stats",
    "decide_ae5",
]

AE5_ID = "AE-HITL-10"
AE5_N = 10
DECLARED_STACK: tuple[str, ...] = (
    "H-ZWRAP",
    "H-WRAPBANK",
    "H-SEMWRAP",
    "H-ASKFAST",
    "H-ASKSMART",
    "H-CTXMAX",
    "H-SMARTMAX",
    "H-FASTMAX",
    "H-APPMAX",
)
STACK_CLAIM = (
    "scoped AE packaged stack "
    "(CTXMAX+SMARTMAX+FASTMAX+APPMAX) — not open chat LM"
)


def select_app(item_app_id: str) -> str:
    """
    GIVEN pack item app_id
    WHEN routing on the declared AE stack
    THEN return APPMAX canonical app_id (not app-route).
    """
    return str(select_app_meta(item_app_id)["app_id"])


def claim_is_honest(claim: str) -> bool:
    low = str(claim).lower()
    if "open chat" in low and "not open chat" not in low:
        return False
    return "scoped" in low or "packaged" in low


def score_ae5_trial(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    ctx_ok: bool | None = None,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN final AE-stack ask result
    WHEN scoring HITL (§5 AE5)
    THEN FALSE_HIT→0; TRUE_HIT→9; CTXMAX ctx fail marks error.
    """
    from semwrap_ops import score_semwrap_trial

    score, err, notes = score_semwrap_trial(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
    )
    notes = list(notes) + ["AE5 final stack — not open chat LM"]
    if ctx_ok is False:
        err = True
        notes.append("CTXMAX_CTX_FAIL")
    return float(score), bool(err), notes


def ae5_stats(
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
    if len(scores) != AE5_N or len(errors) != AE5_N:
        raise ValueError(f"AE5 requires exactly {AE5_N} scores/errors")
    mean = float(sum(float(s) for s in scores) / float(AE5_N))
    n_err = int(sum(1 for e in errors if e))
    return {
        "n_trials": AE5_N,
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


def decide_ae5(stats: Mapping[str, Any]) -> str:
    """
    GIVEN AE5 final HITL stats
    WHEN applying §5 AE5 gate
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
