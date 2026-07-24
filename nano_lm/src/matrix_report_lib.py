"""Kill/promote decision helpers for champion matrix report."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable

from cur_ops import decide_hcur
from deck_ops import decide_hdeck
from deckl_ops import decide_hdeckl
from early_ops import decide_hearly
from matrix_decide_decode import decide_hdec_row, decide_hspec_row
from pool_ops import decide_hpool


def _mean_optional(items: list[dict[str, Any]], key: str) -> float:
    vals = [float(x[key]) for x in items if x.get(key) is not None]
    return sum(vals) / len(vals) if vals else float("nan")


def _flag_any(items: list[dict[str, Any]], key: str) -> float:
    return 1.0 if any(bool(x.get(key)) for x in items) else 0.0


def mean_by_family(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        buckets[r["family"]].append(r)
    return {fam: _family_stats(items) for fam, items in buckets.items()}


def _family_stats(items: list[dict[str, Any]]) -> dict[str, float]:
    lps = [float(x["teacher_mean_logprob"]) for x in items]
    return {
        "mean_lp": sum(lps) / len(lps),
        "mean_wall": _mean_optional(items, "mean_wall_ms"),
        "mean_tps": _mean_optional(items, "mean_tokens_per_s"),
        "n": float(len(items)),
        "wall_save": _flag_any(items, "wall_save"),
        "overfit": _flag_any(items, "overfit"),
    }


_SPECIAL: dict[str, Callable[..., str]] = {
    "H-DEC": decide_hdec_row,
    "H-SPEC": decide_hspec_row,
    "H-DECK": decide_hdeck,
    "H-DECKL": decide_hdeckl,
    "H-POOL": decide_hpool,
    "H-EARLY": decide_hearly,
    "H-CUR": decide_hcur,
}


def decision(fam: str, s: dict[str, float], stats: dict[str, dict[str, float]]) -> str:
    if fam == "B2":
        return "BASELINE (claim gate)"
    if fam in {"B0", "B1"}:
        return "control"
    if fam == "B3":
        return "decode control (AR)"
    if fam == "B4":
        return "decode control (BoN)"
    if fam == "H-CURL":
        return "official train tip (see formal-hcurl)"
    if fam in _SPECIAL:
        return _SPECIAL[fam](s, stats)
    b2 = stats.get("B2", {}).get("mean_lp")
    if b2 is not None and s["mean_lp"] > b2 + 1e-6:
        return "PROMOTE (beats B2)"
    return "KILL / hold (≤ B2)"
