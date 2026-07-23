"""Kill/promote decision helpers for matrix report."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

EPS_LP = 0.05


def mean_by_family(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        buckets[r["family"]].append(r)
    return {fam: _family_stats(items) for fam, items in buckets.items()}


def _family_stats(items: list[dict[str, Any]]) -> dict[str, float]:
    lps = [float(x["teacher_mean_logprob"]) for x in items]
    walls = [
        float(x["mean_wall_ms"])
        for x in items
        if x.get("mean_wall_ms") is not None
    ]
    speeds = [
        float(x["mean_tokens_per_s"])
        for x in items
        if x.get("mean_tokens_per_s") is not None
    ]
    return {
        "mean_lp": sum(lps) / len(lps),
        "mean_wall": sum(walls) / len(walls) if walls else float("nan"),
        "mean_tps": sum(speeds) / len(speeds) if speeds else float("nan"),
        "n": float(len(items)),
        "unstable": 1.0 if any(bool(x.get("unstable")) for x in items) else 0.0,
    }


def decision(fam: str, s: dict[str, float], stats: dict[str, dict[str, float]]) -> str:
    b2 = stats.get("B2", {}).get("mean_lp")
    if fam == "B2":
        return "BASELINE (claim gate)"
    if fam in {"B0", "B1"}:
        return "control"
    if fam == "B3":
        return "decode control (AR)"
    if fam == "B4":
        return "decode control (BoN)"
    if fam == "H-DEC":
        return _decide_hdec(s, stats)
    if fam == "H-LAM":
        return _decide_hlam(s, stats)
    if fam == "H-SPEC":
        return _decide_hspec(s, stats)
    if fam in {"H-SUP", "H-INT", "BoN-uniform"}:
        return _decide_quantum(fam, s, stats)
    if b2 is not None and s["mean_lp"] > b2 + 1e-6:
        return "PROMOTE (beats B2)"
    return "KILL / hold (≤ B2)"


def _decide_hlam(s: dict[str, float], stats: dict[str, dict[str, float]]) -> str:
    if s.get("unstable", 0.0) > 0.0:
        return "KILL (unstable)"
    bal = stats.get("H-BAL")
    if bal is None:
        return "needs H-BAL control"
    if s["mean_lp"] > bal["mean_lp"] + 1e-6:
        return "PROMOTE (beats H-BAL)"
    return "KILL (≤ H-BAL)"


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
