"""Scan formal JSON pairs for H-PARETO efficiency flags."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from matrix_common import REPO
from pareto_ops import DELTA_GFLOPS_FRAC, classify_util

__all__ = [
    "CONTROL_OF",
    "formal_root",
    "means_from_rows",
    "scan_formal_pairs",
    "DELTA_GFLOPS_FRAC",
]

# Challenger → tip/control measured in the same formal.json.
CONTROL_OF: dict[str, str] = {
    "H-BAT": "H-EARLY",
    "H-CBAT": "H-BAT",
    "H-CHBAT": "H-CBAT",
    "H-FUSEB": "H-CHBAT",
    "H-LAYB": "H-FUSEB",
    "H-GRAPH": "H-LAYB",
    "H-GALL": "H-GRAPH",
    "H-SERVE": "H-EARLY",
    "H-POOLB": "H-POOL",
    "H-CPOOLB": "H-POOLB",
    "H-FCPOOLB": "H-CPOOLB",
    "H-FLAYB": "H-FCPOOLB",
    "H-GRAPHF": "H-FLAYB",
    "H-ROUTE": "H-GRAPHF",
}


def formal_root() -> Path:
    return REPO / "results/nano-lm"


def means_from_rows(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    bags: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        bags[str(r["family"])].append(r)
    out: dict[str, dict[str, float]] = {}
    for fam, items in bags.items():
        n = float(len(items))
        if "mean_est_gflops" not in items[0] or "mean_tokens_per_s" not in items[0]:
            continue
        out[fam] = {
            "mean_lp": sum(float(x["teacher_mean_logprob"]) for x in items) / n,
            "mean_wall": sum(float(x["mean_wall_ms"]) for x in items) / n,
            "mean_tps": sum(float(x["mean_tokens_per_s"]) for x in items) / n,
            "mean_gflops": sum(float(x["mean_est_gflops"]) for x in items) / n,
            "n": n,
        }
    return out


def scan_formal_pairs(
    root: Path | None = None,
    *,
    delta_frac: float = DELTA_GFLOPS_FRAC,
) -> list[dict[str, Any]]:
    """
    GIVEN formal-*/formal.json under results/nano-lm
    WHEN util and its CONTROL_OF tip both have GFLOPs
    THEN emit one classified row per pair.
    """
    base = formal_root() if root is None else Path(root)
    pairs: list[dict[str, Any]] = []
    for path in sorted(base.glob("formal-*/formal.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        rows = data.get("rows") or []
        if not rows:
            continue
        stats = means_from_rows(rows)
        source = str(path.relative_to(base))
        for util_name, tip_name in CONTROL_OF.items():
            if util_name not in stats or tip_name not in stats:
                continue
            util = stats[util_name]
            tip = stats[tip_name]
            verdict = classify_util(util, tip, delta_frac=delta_frac)
            pairs.append(
                {
                    "source": source,
                    "family": util_name,
                    "control": tip_name,
                    "verdict": verdict,
                    "flagged": verdict.startswith("FLAG"),
                    "mean_lp": util["mean_lp"],
                    "mean_wall_ms": util["mean_wall"],
                    "mean_tokens_per_s": util["mean_tps"],
                    "mean_est_gflops": util["mean_gflops"],
                    "tip_mean_tps": tip["mean_tps"],
                    "tip_mean_gflops": tip["mean_gflops"],
                    "delta_tps": util["mean_tps"] - tip["mean_tps"],
                    "delta_gflops": util["mean_gflops"] - tip["mean_gflops"],
                    "n": util["n"],
                    "delta_frac": float(delta_frac),
                }
            )
    return pairs
