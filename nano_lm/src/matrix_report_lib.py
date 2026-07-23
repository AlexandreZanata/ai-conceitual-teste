"""Kill/promote decision helpers for matrix report."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable

EPS_LP = 0.05


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
        "unstable": _flag_any(items, "unstable"),
        "collapsed": max(
            _flag_any(items, "diversity_collapsed"),
            _flag_any(items, "heads_collapsed"),
        ),
    }


def _decide_hlam(s: dict[str, float], stats: dict[str, dict[str, float]]) -> str:
    if s.get("unstable", 0.0) > 0.0:
        return "KILL (unstable)"
    bal = stats.get("H-BAL")
    if bal is None:
        return "needs H-BAL control"
    if s["mean_lp"] > bal["mean_lp"] + 1e-6:
        return "PROMOTE (beats H-BAL)"
    return "KILL (≤ H-BAL)"


def _decide_heli(s: dict[str, float], stats: dict[str, dict[str, float]]) -> str:
    if s.get("collapsed", 0.0) > 0.0:
        return "KILL (diversity collapse)"
    hsel = stats.get("H-SEL")
    if hsel is None:
        return "needs H-SEL control"
    if s["mean_lp"] > hsel["mean_lp"] + 1e-6:
        return "PROMOTE (beats H-SEL, diversity ok)"
    return "KILL / hold (≤ H-SEL)"


def _decide_hfit(s: dict[str, float], stats: dict[str, dict[str, float]]) -> str:
    hsel = stats.get("H-SEL")
    if hsel is None:
        return "needs H-SEL control"
    if s["mean_lp"] > hsel["mean_lp"] + 1e-6:
        return "PROMOTE (beats H-SEL)"
    return "KILL / hold (≤ H-SEL)"


def _decide_hann(s: dict[str, float], stats: dict[str, dict[str, float]]) -> str:
    cos = stats.get("KD-cos")
    if cos is None:
        return "needs KD-cos control"
    if s["mean_lp"] > cos["mean_lp"] + 1e-6:
        return "PROMOTE (beats cosine KD)"
    return "KILL (cosine wins)"


def _decide_hent(s: dict[str, float], stats: dict[str, dict[str, float]]) -> str:
    if s.get("collapsed", 0.0) > 0.0:
        return "KILL (collapsed to one head)"
    b2 = stats.get("B2", {}).get("mean_lp")
    if b2 is None:
        return "needs B2 control"
    if s["mean_lp"] > b2 + 1e-6:
        return "PROMOTE (beats B2, heads distinct)"
    return "KILL / hold (≤ B2)"


def _decide_hdec(s: dict[str, float], stats: dict[str, dict[str, float]]) -> str:
    b4 = stats.get("B4")
    if b4 is None:
        return "needs B4 control"
    if s["mean_lp"] > b4["mean_lp"] + 1e-6:
        return "PROMOTE (beats fixed BoN/B4)"
    return "KILL (≤ fixed BoN/B4)"


def _decide_hspec(s: dict[str, float], stats: dict[str, dict[str, float]]) -> str:
    b3 = stats.get("B3")
    if b3 is None:
        return "needs B3 control"
    faster = s["mean_tps"] > b3["mean_tps"] + 1e-6
    ok_q = s["mean_lp"] >= b3["mean_lp"] - EPS_LP
    if faster and ok_q:
        return "PROMOTE (faster vs B3, quality ok)"
    if not faster:
        return "KILL (no speedup vs B3)"
    return "KILL (quality drop vs B3)"


def _decide_quantum(
    fam: str, s: dict[str, float], stats: dict[str, dict[str, float]]
) -> str:
    bon = stats.get("BoN-uniform", {}).get("mean_lp")
    if bon is None:
        return "ablation"
    if fam == "BoN-uniform":
        return "ablation control"
    if s["mean_lp"] > bon + 1e-6:
        return "PROMOTE (vs uniform BoN)"
    return "KILL (≤ uniform BoN)"


_SPECIAL: dict[str, Callable[..., str]] = {
    "H-DEC": _decide_hdec,
    "H-LAM": _decide_hlam,
    "H-ELI": _decide_heli,
    "H-FIT": _decide_hfit,
    "H-ENT": _decide_hent,
    "H-ANN": _decide_hann,
    "H-SPEC": _decide_hspec,
}


def decision(fam: str, s: dict[str, float], stats: dict[str, dict[str, float]]) -> str:
    if fam == "B2":
        return "BASELINE (claim gate)"
    if fam == "KD-cos":
        return "schedule control (cosine KD)"
    if fam in {"B0", "B1"}:
        return "control"
    if fam == "B3":
        return "decode control (AR)"
    if fam == "B4":
        return "decode control (BoN)"
    if fam in _SPECIAL:
        return _SPECIAL[fam](s, stats)
    if fam in {"H-SUP", "H-INT", "BoN-uniform"}:
        return _decide_quantum(fam, s, stats)
    b2 = stats.get("B2", {}).get("mean_lp")
    if b2 is not None and s["mean_lp"] > b2 + 1e-6:
        return "PROMOTE (beats B2)"
    return "KILL / hold (≤ B2)"
