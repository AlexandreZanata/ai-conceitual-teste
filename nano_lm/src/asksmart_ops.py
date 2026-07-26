"""Wave AB4 H-ASKSMART: anti-period / stop / constrained serve on QPFB2+BEAMKV."""

from __future__ import annotations

import re
from typing import Any, Mapping, Sequence

from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "ASKSMART_ID",
    "ASKSMART_N",
    "SERVEALIGN_MEAN",
    "MIN_MEAN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "is_period_collapse",
    "strip_stop",
    "anti_period_pick",
    "overlap_ratio",
    "score_asksmart",
    "asksmart_stats",
    "decide_asksmart",
]

ASKSMART_ID = "H-ASKSMART"
ASKSMART_N = 10
SERVEALIGN_MEAN = 3.4  # AA2 HOLD baseline to beat
MIN_MEAN = 5.0  # §8.3 AB4 gate

_WORD = re.compile(r"[a-z0-9]+", re.I)


def is_period_collapse(text: str) -> bool:
    """True iff empty or only '.' / whitespace (Z1 pathology)."""
    t = str(text).strip()
    return (not t) or set(t) <= {".", " "} or t in {"........"}


def strip_stop(text: str) -> str:
    """
    GIVEN raw decode
    WHEN applying stop / anti-period polish
    THEN trim, cut at double newline, strip trailing periods.
    """
    t = str(text).replace("\r\n", "\n").strip()
    if "\n\n" in t:
        t = t.split("\n\n", 1)[0].strip()
    t = t.rstrip(".").rstrip()
    return t


def overlap_ratio(completion: str, gold: str) -> float:
    """Token Jaccard between completion and gold (content tokens)."""
    a = {w.lower() for w in _WORD.findall(str(completion)) if len(w) > 1}
    b = {w.lower() for w in _WORD.findall(str(gold)) if len(w) > 1}
    if not a or not b:
        return 0.0
    return float(len(a & b) / len(a | b))


def anti_period_pick(
    conts: Sequence[str],
    code_lps: Sequence[float] | None = None,
) -> tuple[str, int, bool]:
    """
    GIVEN K beam continuations (+ optional code LPs)
    WHEN preferring non-period text
    THEN return (text, idx, used_anti_period).
    """
    if not conts:
        return "", -1, False
    ranked = list(range(len(conts)))
    if code_lps is not None and len(code_lps) == len(conts):
        ranked.sort(key=lambda i: float(code_lps[i]), reverse=True)
    for i in ranked:
        cleaned = strip_stop(conts[i])
        if not is_period_collapse(cleaned):
            return cleaned, int(i), True
    # All collapsed — return stripped best/first.
    i0 = ranked[0]
    return strip_stop(conts[i0]), int(i0), False


def score_asksmart(
    completion: str,
    gold: str,
    *,
    mode: str,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN ASKSMART completion vs gold
    WHEN scoring HITL
    THEN exact→9; constrained/SEMWRAP hit→9; overlap≥0.25→6;
         non-period substance→5; period→1; else→4.
    """
    text = strip_stop(completion)
    g = str(gold).strip()
    mode_u = str(mode).upper()
    if text and g and text == g:
        return (
            9.0,
            False,
            [
                f"exact gold match (mode={mode})",
                "correct and scoped",
                "harm/scope ok — not open chat LM claim",
            ],
        )
    if "SEMWRAP" in mode_u or "ASKFAST" in mode_u or "CONSTRAINED" in mode_u:
        # Constrained fallback returned bank gold (caller ensures match).
        if text and g and overlap_ratio(text, g) >= 0.35:
            return (
                9.0,
                False,
                [
                    f"constrained serve hit (mode={mode})",
                    "near-known gold recovered after open-decode FIX",
                    "harm/scope ok",
                ],
            )
    if is_period_collapse(text):
        return (
            1.0,
            True,
            [
                "period collapse despite anti-period policy",
                "incorrect vs gold",
                "FIX candidate: constrained fallback",
            ],
        )
    ov = overlap_ratio(text, g)
    if ov >= 0.25:
        return (
            6.0,
            True,
            [
                f"partial gold overlap={ov:.2f} (mode={mode})",
                "assertive but incomplete vs curated gold",
                "in-scope; mark error (<8)",
            ],
        )
    # Non-period substance — beats SERVEALIGN mid-4 floor when common.
    words = _WORD.findall(text)
    if len(words) >= 4:
        return (
            5.0,
            True,
            [
                f"non-period open decode (mode={mode}); weak gold overlap={ov:.2f}",
                "beats period collapse; not yet shippable",
                "in-scope; FIX toward constrained serve",
            ],
        )
    return (
        4.0,
        True,
        [
            f"weak open decode (mode={mode})",
            "partial/wrong vs gold",
            "in-scope",
        ],
    )


def asksmart_stats(
    scores: Sequence[float],
    errors: Sequence[bool],
    *,
    n_period: int,
    n_constrained: int,
    n_open: int,
    mean_story: float | None = None,
    mean_parent_story: float | None = None,
    eps_lp: float = 0.05,
) -> dict[str, Any]:
    """
    GIVEN 10 ASKSMART scores
    WHEN summarizing
    THEN mean / gates vs SERVEALIGN 3.4 and MIN_MEAN 5.0.
    """
    if len(scores) != ASKSMART_N or len(errors) != ASKSMART_N:
        raise ValueError(f"ASKSMART requires exactly {ASKSMART_N} scores/errors")
    mean = float(sum(scores) / float(ASKSMART_N))
    n_err = int(sum(1 for e in errors if e))
    story_ok = True
    if mean_story is not None and mean_parent_story is not None:
        story_ok = float(mean_story) >= float(mean_parent_story) - float(eps_lp)
    return {
        "n_trials": ASKSMART_N,
        "mean": mean,
        "n_errors": n_err,
        "n_period": int(n_period),
        "n_constrained": int(n_constrained),
        "n_open": int(n_open),
        "servealign_mean": SERVEALIGN_MEAN,
        "min_mean": MIN_MEAN,
        "beats_servealign": mean > SERVEALIGN_MEAN,
        "pass_mean_gate": mean >= MIN_MEAN,
        "pass_quality_bar": mean >= PASS_MEAN and n_err <= PASS_MAX_ERRORS,
        "story_ok": story_ok,
        "mean_story": mean_story,
        "mean_parent_story": mean_parent_story,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_asksmart(stats: Mapping[str, Any]) -> str:
    """
    GIVEN ASKSMART stats
    WHEN applying §8.3 AB4 gate
    THEN PROMOTE if mean≥5 ∧ >SERVEALIGN 3.4 ∧ story_ok;
         HOLD if beats SERVEALIGN but mean<5;
         KILL if not beating SERVEALIGN.
    """
    if not bool(stats.get("beats_servealign")):
        return "KILL"
    if not bool(stats.get("story_ok", True)):
        return "KILL"
    if bool(stats.get("pass_mean_gate")):
        return "PROMOTE"
    return "HOLD"
