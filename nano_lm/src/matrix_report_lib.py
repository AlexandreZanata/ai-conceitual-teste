"""Kill/promote decision helpers for matrix report."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable

from hold_ops import decide_hhold; from fxs_ops import decide_hfxs
from heb_ops import decide_hheb; from epi_ops import decide_hepi
from lot_ops import decide_hlot
from hop_ops import decide_hhop; from blk_ops import decide_hblk
from dif_ops import decide_hdif; from adv_ops import decide_hadv
from deb_ops import decide_hdeb; from rout_ops import decide_hrout
from orac_ops import decide_horac; from tkd_ops import decide_htkd
from rep_ops import decide_hrep; from clip_ops import decide_hclip
from ls_ops import decide_hls; from ngram_ops import decide_hngram
from nge_ops import decide_hnge; from ngre_ops import decide_hngre
from ngdm_ops import decide_hngdm
from lofi_ops import decide_hlofi; from ent2_ops import decide_hent2
from ent3_ops import decide_hent3
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
    ups = [float(bool(x["diversity_up"])) for x in items if "diversity_up" in x]
    keys = ("diversity_collapsed", "heads_collapsed", "niche_collapsed", "mode_collapsed")
    col = max(_flag_any(items, k) for k in keys)
    return {
        "mean_lp": sum(lps) / len(lps),
        "mean_wall": _mean_optional(items, "mean_wall_ms"),
        "mean_tps": _mean_optional(items, "mean_tokens_per_s"),
        "n": float(len(items)),
        "unstable": _flag_any(items, "unstable"),
        "collapsed": col,
        "nan": _flag_any(items, "had_nan"),
        "parasite_dominates": _flag_any(items, "parasite_dominates"),
        "overfit": _flag_any(items, "overfit"),
        "wall_save": _flag_any(items, "wall_save"),
        "mode_chaos": _flag_any(items, "mode_chaos"),
        "div_up_rate": sum(ups) / len(ups) if ups else float("nan"),
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

def _decide_hcan(s: dict[str, float], stats: dict[str, dict[str, float]]) -> str:
    if s.get("nan", 0.0) > 0.0:
        return "KILL (NaN)"
    return _decide_hfit(s, stats)
def _decide_hpar(s: dict[str, float], stats: dict[str, dict[str, float]]) -> str:
    if s.get("parasite_dominates", 0.0) > 0.0:
        return "KILL (parasite dominates)"
    return _decide_hfit(s, stats)
def _decide_hgld(s: dict[str, float], stats: dict[str, dict[str, float]]) -> str:
    c = stats.get("H-FIT")
    if c is None:
        return "needs H-FIT control"
    if s["mean_lp"] > c["mean_lp"] + 1e-6:
        return "PROMOTE (beats max-lp / H-FIT)"
    return "KILL / hold (≤ max-lp fitness)"

def _decide_hrps(s: dict[str, float], stats: dict[str, dict[str, float]]) -> str:
    if s.get("collapsed", 0.0) > 0.0:
        return "KILL (collapsed to 1 niche)"
    return _decide_hfit(s, stats)

def _decide_hnic(s: dict[str, float], stats: dict[str, dict[str, float]]) -> str:
    rate = s.get("div_up_rate", float("nan"))
    if rate == rate and rate < 1.0 - 1e-9:
        return "KILL (no diversity↑)"
    hsel = stats.get("H-SEL")
    if hsel is None:
        return "needs H-SEL control"
    if s["mean_lp"] > hsel["mean_lp"] + 1e-6:
        return "PROMOTE (beats H-SEL, diversity↑)"
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
    "H-DEC": _decide_hdec, "H-LAM": _decide_hlam, "H-ELI": _decide_heli,
    "H-XOV": _decide_heli, "H-NIC": _decide_hnic, "H-CAN": _decide_hcan,
    "H-ZOM": _decide_hcan, "H-PAR": _decide_hpar, "H-GLD": _decide_hgld,
    "H-SEA": _decide_hgld, "H-RPS": _decide_hrps, "H-ENT": _decide_hent,
    "H-ANN": _decide_hann, "H-SPEC": _decide_hspec, "H-HOLD": decide_hhold,
    "H-FXS": decide_hfxs, "H-LOFI": decide_hlofi, "H-ENT2": decide_hent2,
    "H-ENT3": decide_hent3, "H-HEB": decide_hheb, "H-EPI": decide_hepi,
    "H-LOT": decide_hlot, "H-HOP": decide_hhop, "H-BLK": decide_hblk,
    "H-DIF": decide_hdif, "H-ADV": decide_hadv, "H-DEB": decide_hdeb,
    "H-ROUT": decide_hrout, "H-ORAC": decide_horac, "H-TKD": decide_htkd,
    "H-REP": decide_hrep, "H-CLIP": decide_hclip, "H-LS": decide_hls,
    "H-NGRAM": decide_hngram, "H-NGE": decide_hnge, "H-NGRE": decide_hngre,
    "H-NGDM": decide_hngdm,
}
for _fam in (
    "H-FIT", "H-TOU", "H-MUT", "H-RAN", "H-AGE", "H-MOR", "H-SPE",
    "H-SEX", "H-ANTI", "H-TAX", "H-SYM", "H-FOS", "H-LOTU", "H-CAT", "H-HIB",
    "H-SHO",
):
    _SPECIAL[_fam] = _decide_hfit
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
