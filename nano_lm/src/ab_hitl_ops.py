"""Wave AB6 AB-HITL-10: final verify on declared AB packaged stack."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "AB6_ID",
    "AB6_N",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "DECLARED_STACK",
    "STACK_CLAIM",
    "select_app",
    "claim_is_honest",
    "score_ab6_trial",
    "ab6_stats",
    "decide_ab6",
]

AB6_ID = "AB-HITL-10"
AB6_N = 10
DECLARED_STACK: tuple[str, ...] = (
    "H-ZWRAP",
    "H-WRAPBANK",
    "H-SEMWRAP",
    "H-ASKFAST",
    "H-LONGAPP",
    "H-ASKSMART",
    "H-REALAPP",
)
STACK_CLAIM = (
    "scoped AB packaged stack (app-known + app-longdoc) — not open chat LM"
)


def select_app(item_app_id: str) -> str:
    """
    GIVEN pack item app_id
    WHEN routing on the declared AB stack
    THEN long-doc → app-longdoc; else app-known.
    """
    if str(item_app_id) == "long-doc":
        return "app-longdoc"
    return "app-known"


def claim_is_honest(claim: str) -> bool:
    low = str(claim).lower()
    if "open chat" in low and "not open chat" not in low:
        return False
    return "scoped" in low or "packaged" in low


def score_ab6_trial(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    longapp_ok: bool | None = None,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN final-stack ask result
    WHEN scoring HITL (§11.5 / §9.5)
    THEN FALSE_HIT→0; TRUE_HIT→9; LONGAPP ctx fail marks error.
    """
    from semwrap_ops import score_semwrap_trial

    score, err, notes = score_semwrap_trial(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
    )
    notes = list(notes)
    if longapp_ok is False:
        err = True
        notes.append("LONGAPP_CTX_FAIL")
    return float(score), bool(err), notes


def ab6_stats(
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
) -> dict[str, Any]:
    if len(scores) != AB6_N or len(errors) != AB6_N:
        raise ValueError(f"AB6 requires exactly {AB6_N} scores/errors")
    mean = float(sum(float(s) for s in scores) / float(AB6_N))
    n_err = int(sum(1 for e in errors if e))
    return {
        "n_trials": AB6_N,
        "mean": mean,
        "n_errors": n_err,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_miss": int(n_miss),
        "n_fix": int(n_fix),
        "claim_ok": bool(claim_ok),
        "n_known_app": int(n_known_app),
        "n_long_app": int(n_long_app),
        "pass_bar": mean >= PASS_MEAN and n_err <= PASS_MAX_ERRORS,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
        "stack": list(DECLARED_STACK),
    }


def decide_ab6(stats: Mapping[str, Any]) -> str:
    """
    GIVEN AB6 final HITL stats
    WHEN applying §8.3 / §11.5 gate
    THEN PROMOTE if pass_bar ∧ claim_ok ∧ no false-hit;
         HOLD if claim/docs soft-miss but pass_bar;
         KILL if false-hit or quality fail.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("pass_bar")):
        return "KILL"
    if not bool(stats.get("claim_ok")):
        return "HOLD"
    return "PROMOTE"
