"""Aggregate H-XFER recipe rows into means + dual-gate verdicts."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from xfer_ops import verdict_pack, verdict_qpack, verdict_tpack

__all__ = [
    "means_decode",
    "means_train",
    "verdicts_from_rows",
]


def means_decode(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    """Mean lp / wall / tok/s / GFLOPs by family (PACK/QPACK rows)."""
    bags: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        bags[str(r["family"])].append(r)
    out: dict[str, dict[str, float]] = {}
    for fam, items in bags.items():
        n = float(len(items))
        out[fam] = {
            "mean_lp": sum(float(x["teacher_mean_logprob"]) for x in items) / n,
            "mean_wall": sum(float(x["mean_wall_ms"]) for x in items) / n,
            "mean_tps": sum(float(x["mean_tokens_per_s"]) for x in items) / n,
            "mean_gflops": sum(float(x["mean_est_gflops"]) for x in items) / n,
            "n": n,
        }
    return out


def means_train(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    """Mean lp / ms_step by family (TPACK rows)."""
    bags: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        bags[str(r["family"])].append(r)
    out: dict[str, dict[str, float]] = {}
    for fam, items in bags.items():
        n = float(len(items))
        out[fam] = {
            "mean_lp": sum(float(x["teacher_mean_logprob"]) for x in items) / n,
            "mean_ms_step": sum(float(x["mean_ms_step"]) for x in items) / n,
            "mean_train_wall": sum(float(x["train_wall_s"]) for x in items) / n,
            "mean_cache_build": sum(float(x.get("cache_build_s", 0)) for x in items)
            / n,
            "n": n,
        }
    return out


def verdicts_from_rows(
    *,
    pack_by: dict[str, list[dict[str, Any]]],
    qpack_by: dict[str, list[dict[str, Any]]],
    tpack_by: dict[str, list[dict[str, Any]]],
) -> dict[str, dict[str, str]]:
    """
    GIVEN rows keyed by transfer pack name
    WHEN scoring each recipe
    THEN return nested verdict strings for decide_hxfer.
    """
    out: dict[str, dict[str, str]] = {"H-PACK": {}, "H-QPACK": {}, "H-TPACK": {}}
    for pack, rows in pack_by.items():
        out["H-PACK"][pack] = verdict_pack(means_decode(rows))
    for pack, rows in qpack_by.items():
        out["H-QPACK"][pack] = verdict_qpack(means_decode(rows))
    for pack, rows in tpack_by.items():
        out["H-TPACK"][pack] = verdict_tpack(means_train(rows))
    return out
