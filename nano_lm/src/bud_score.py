"""Score H-BUD survivors from PACK/QPACK/TPACK row bags."""

from __future__ import annotations

from typing import Any, Mapping

from bud_ops import survive_decode, survive_train
from xfer_score import means_decode, means_train

__all__ = ["budget_verdicts", "means_decode", "means_train"]


def budget_verdicts(
    *,
    pack_rows: list[dict[str, Any]],
    qpack_rows: list[dict[str, Any]],
    tpack_rows: list[dict[str, Any]],
) -> dict[str, str]:
    """
    GIVEN shared harness rows for the three recipes
    WHEN applying hard budgets
    THEN return H-PACK (SERVE), H-QPACK (FLAYB), H-TPACK verdicts.
    """
    pack = means_decode(pack_rows)
    qpack = means_decode(qpack_rows)
    tpack = means_train(tpack_rows)
    out: dict[str, str] = {}
    early = pack.get("H-EARLY")
    serve = pack.get("H-SERVE")
    if early is None or serve is None:
        out["H-PACK"] = "needs H-EARLY/H-SERVE"
    else:
        out["H-PACK"] = survive_decode(serve, early)
    pool = qpack.get("H-POOL")
    flayb = qpack.get("H-FLAYB")
    if pool is None or flayb is None:
        out["H-QPACK"] = "needs H-POOL/H-FLAYB"
    else:
        out["H-QPACK"] = survive_decode(flayb, pool)
    stag = tpack.get("H-STAG")
    ht = tpack.get("H-TPACK")
    if stag is None or ht is None:
        out["H-TPACK"] = "needs H-STAG/H-TPACK"
    else:
        out["H-TPACK"] = survive_train(ht, stag)
    return out


def decode_axes(
    util: Mapping[str, float], tip: Mapping[str, float]
) -> dict[str, float]:
    """Report Δ metrics for markdown tables."""
    return {
        "delta_lp": float(util["mean_lp"]) - float(tip["mean_lp"]),
        "delta_wall": float(util["mean_wall"]) - float(tip["mean_wall"]),
        "delta_tps": float(util["mean_tps"]) - float(tip["mean_tps"]),
        "delta_gflops": float(util["mean_gflops"]) - float(tip["mean_gflops"]),
    }
