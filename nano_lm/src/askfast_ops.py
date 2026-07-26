"""Wave AB2 H-ASKFAST: compose SEMWRAP + QT batch + ask completion cache."""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping

from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN
from z_wrap import normalize_question

__all__ = [
    "ASKFAST_ID",
    "ASKFAST_N",
    "WALL_DROP_MIN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "AskCompletionCache",
    "wall_reduction",
    "askfast_stats",
    "decide_askfast",
    "score_askfast_trial",
]

ASKFAST_ID = "H-ASKFAST"
ASKFAST_N = 10
WALL_DROP_MIN = 0.20  # ≥20% wall↓ vs baseline


class AskCompletionCache:
    """
    RAM memo for ask completions (SCORERAM-like for the ask path).

    KEY: normalize_question(question)
    TTL: process / pack session
    INVALIDATE: clear() or new instance
    """

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}
        self.hits = 0
        self.misses = 0

    def get(self, question: str) -> dict[str, Any] | None:
        key = normalize_question(question)
        row = self._store.get(key)
        if row is None:
            self.misses += 1
            return None
        self.hits += 1
        out = dict(row)
        out["mode"] = "ASKFAST_CACHE"
        out["wall_ms"] = 0.0
        out["cache_hit"] = True
        return out

    def put(self, question: str, payload: Mapping[str, Any]) -> None:
        key = normalize_question(question)
        self._store[key] = {
            "completion": payload.get("completion"),
            "recipe_id": payload.get("recipe_id"),
            "family": payload.get("family"),
            "n_new": payload.get("n_new", 0),
            "seed": payload.get("seed", 0),
            "wrap_id": payload.get("wrap_id"),
            "mode": payload.get("mode"),
        }

    def clear(self) -> None:
        self._store.clear()
        self.hits = 0
        self.misses = 0

    def hit_rate(self) -> float:
        total = self.hits + self.misses
        if total <= 0:
            return 0.0
        return float(self.hits) / float(total)

    def size(self) -> int:
        return len(self._store)


def wall_reduction(baseline_ms: float, askfast_ms: float) -> float:
    """
    GIVEN baseline vs ASKFAST mean wall_ms
    WHEN computing speedup fraction
    THEN (baseline - askfast) / baseline; 0 if baseline≤0.
    """
    base = float(baseline_ms)
    fast = float(askfast_ms)
    if base <= 0.0:
        return 0.0 if fast > 0.0 else 1.0
    return max(0.0, (base - fast) / base)


def score_askfast_trial(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN ASKFAST ask result
    WHEN scoring HITL (same bar as SEMWRAP known-ask)
    THEN FALSE_HIT→0; TRUE_HIT / gold match→9; else miss scores.
    """
    from semwrap_ops import score_semwrap_trial

    return score_semwrap_trial(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
    )


def askfast_stats(
    scores: list[float],
    errors: list[bool],
    *,
    baseline_wall_ms: float,
    askfast_wall_ms: float,
    cache_hit_rate: float,
    n_true_hit: int,
    n_false_hit: int,
    n_miss: int,
) -> dict[str, Any]:
    """
    GIVEN HITL scores + wall pair
    WHEN summarizing H-ASKFAST
    THEN quality + wall_drop + pass flags.
    """
    if len(scores) != ASKFAST_N or len(errors) != ASKFAST_N:
        raise ValueError(f"ASKFAST requires exactly {ASKFAST_N} scores/errors")
    mean = float(sum(scores) / float(ASKFAST_N))
    n_err = int(sum(1 for e in errors if e))
    drop = wall_reduction(baseline_wall_ms, askfast_wall_ms)
    return {
        "n_trials": ASKFAST_N,
        "mean": mean,
        "n_errors": n_err,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_miss": int(n_miss),
        "baseline_wall_ms": float(baseline_wall_ms),
        "askfast_wall_ms": float(askfast_wall_ms),
        "wall_drop": drop,
        "wall_drop_min": WALL_DROP_MIN,
        "cache_hit_rate": float(cache_hit_rate),
        "pass_quality": mean >= PASS_MEAN and n_err <= PASS_MAX_ERRORS,
        "pass_wall": drop >= WALL_DROP_MIN,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_askfast(stats: Mapping[str, Any]) -> str:
    """
    GIVEN ASKFAST stats
    WHEN applying §8.3 AB2 gate
    THEN PROMOTE if quality ∧ wall↓≥20% ∧ no false-hit;
         HOLD if quality (wall miss documented);
         KILL if false-hit or quality collapse.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("pass_quality")):
        return "KILL"
    if bool(stats.get("pass_wall")):
        return "PROMOTE"
    return "HOLD"


def merge_cache_payload(
    cached: MutableMapping[str, Any],
    *,
    question: str,
    seed: int,
) -> dict[str, Any]:
    """Materialize a cache hit payload for ask_many."""
    return {
        "recipe_id": cached.get("recipe_id"),
        "family": cached.get("family"),
        "question": question,
        "completion": cached.get("completion"),
        "wall_ms": 0.0,
        "n_new": cached.get("n_new", 0),
        "seed": int(seed),
        "mode": "ASKFAST_CACHE",
        "elapsed_s": 0.0,
        "wrap_id": cached.get("wrap_id"),
        "cache_hit": True,
    }
