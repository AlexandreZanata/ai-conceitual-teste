"""Wave AC5 AC-HITL-10: final verify on declared AC packaged stack."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "AC5_ID",
    "AC5_N",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "DECLARED_STACK",
    "STACK_CLAIM",
    "select_app",
    "claim_is_honest",
    "score_ac5_trial",
    "ac5_stats",
    "decide_ac5",
]

AC5_ID = "AC-HITL-10"
AC5_N = 10
DECLARED_STACK: tuple[str, ...] = (
    "H-ZWRAP",
    "H-WRAPBANK",
    "H-SEMWRAP",
    "H-ASKFAST",
    "H-ASKSMART",
    "H-CTXPLUS",
    "H-SMARTPLUS",
    "H-FASTPLUS",
    "H-APPPLUS",
)
STACK_CLAIM = (
    "scoped AC packaged stack "
    "(app-known + app-longdoc + app-howto) — not open chat LM"
)


def select_app(item_app_id: str) -> str:
    """
    GIVEN pack item app_id
    WHEN routing on the declared AC stack
    THEN long-doc → app-longdoc; howto → app-howto; else app-known.
    """
    key = str(item_app_id)
    if key == "long-doc":
        return "app-longdoc"
    if key == "howto":
        return "app-howto"
    return "app-known"


def claim_is_honest(claim: str) -> bool:
    low = str(claim).lower()
    if "open chat" in low and "not open chat" not in low:
        return False
    return "scoped" in low or "packaged" in low


def score_ac5_trial(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    ctx_ok: bool | None = None,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN final AC-stack ask result
    WHEN scoring HITL (§12.1 AC5)
    THEN FALSE_HIT→0; TRUE_HIT→9; CTXPLUS/LONGAPP ctx fail marks error.
    """
    from semwrap_ops import score_semwrap_trial

    score, err, notes = score_semwrap_trial(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
    )
    notes = list(notes) + ["AC5 final stack — not open chat LM"]
    if ctx_ok is False:
        err = True
        notes.append("CTXPLUS_CTX_FAIL")
    return float(score), bool(err), notes


def ac5_stats(
    scores: Sequence[float],
    errors: Sequence[bool],
    *,
    n_true_hit: int,
    n_false_hit: int,
    n_miss: int,
    n_fix: int,
    claim_ok: bool,
    n_known_app: int,
    n_long_app: int,
    n_howto_app: int,
) -> dict[str, Any]:
    if len(scores) != AC5_N or len(errors) != AC5_N:
        raise ValueError(f"AC5 requires exactly {AC5_N} scores/errors")
    mean = float(sum(float(s) for s in scores) / float(AC5_N))
    n_err = int(sum(1 for e in errors if e))
    return {
        "n_trials": AC5_N,
        "mean": mean,
        "n_errors": n_err,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_miss": int(n_miss),
        "n_fix": int(n_fix),
        "claim_ok": bool(claim_ok),
        "n_known_app": int(n_known_app),
        "n_long_app": int(n_long_app),
        "n_howto_app": int(n_howto_app),
        "pass_bar": mean >= PASS_MEAN and n_err <= PASS_MAX_ERRORS,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
        "stack": list(DECLARED_STACK),
    }


def decide_ac5(stats: Mapping[str, Any]) -> str:
    """
    GIVEN AC5 final HITL stats
    WHEN applying §8.5 / §12.1 gate
    THEN PROMOTE if pass_bar ∧ claim_ok ∧ no false-hit;
         HOLD if claim soft-miss but pass_bar;
         KILL if false-hit or quality fail.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("pass_bar")):
        return "KILL"
    if not bool(stats.get("claim_ok")):
        return "HOLD"
    return "PROMOTE"
