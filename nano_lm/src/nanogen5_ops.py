"""Wave AU3 H-NANOGEN5: strict ablated DECODE + gibberish-tail gate."""

from __future__ import annotations

import re
from typing import Any, Mapping, Sequence

from abstain_ops import is_junk_decode
from asksmart_ops import is_period_collapse
from au_session_ops import AU0_NANOGEN5_HYPOTHESIS, AU0_STRICT_GEN_JUDGE
from genbase_ops import normalize_gen_answer
from nanogen4_ops import (
    MIN_LOOKUP_MEAN,
    NANOGEN4_N,
    NANOGEN4_PACK,
    apply_bank_grounded_short,
    apply_snippet_prefix_decode,
    gold_in_context,
    nanogen4_stats,
    score_nanogen4_gen,
    score_nanogen4_lookup,
    select_snippet_span,
)
from nanogen_ops import decide_nanogen

__all__ = [
    "NANOGEN5_ID",
    "NANOGEN5_N",
    "NANOGEN5_PACK",
    "NANOGEN5_THESIS",
    "NANOGEN5_HYPOTHESIS",
    "PARENT_NANOGEN4_ABLATED",
    "MIN_LOOKUP_MEAN",
    "MIN_GEN_MEAN",
    "STRICT_JUDGE",
    "gold_in_context",
    "apply_bank_grounded_short",
    "apply_snippet_prefix_decode",
    "select_snippet_span",
    "short_answer_token_f1",
    "is_usable_gen_span",
    "continuation_is_gibberish",
    "apply_gibberish_tail_gate",
    "score_nanogen5_lookup",
    "score_nanogen5_gen",
    "nanogen5_stats",
    "decide_nanogen5",
]

NANOGEN5_ID = "H-NANOGEN5"
NANOGEN5_N = NANOGEN4_N
NANOGEN5_PACK = NANOGEN4_PACK  # fair lift vs archived NANOGEN4 5.5
NANOGEN5_HYPOTHESIS = AU0_NANOGEN5_HYPOTHESIS
PARENT_NANOGEN4_ABLATED = 5.5
MIN_GEN_MEAN = 5.5  # strict_ablated≥5.5 (AU0 judge law)
STRICT_JUDGE = dict(AU0_STRICT_GEN_JUDGE)
NANOGEN5_THESIS = (
    "Ablated DECODE lift vs H-NANOGEN4 5.5 via snippet-prefix + "
    "gibberish-tail gate under STRICT short-answer F1/HITL "
    "(gold-substring alone insufficient); PROMOTE iff "
    "strict_ablated≥5.5 else HOLD"
)

_WORD = re.compile(r"[A-Za-z0-9_./=+\-]{2,}")
_FILLER = frozenset(
    {
        "really",
        "everything",
        "something",
        "looking",
        "followed",
        "getting",
        "finally",
        "quickly",
        "just",
        "which",
        "that",
        "back",
        "even",
        "once",
        "upon",
        "little",
        "story",
        "time",
    }
)


def short_answer_token_f1(completion: str, gold: str) -> float:
    """
    GIVEN short completion + gold
    WHEN computing token F1 (HITL proxy)
    THEN return [0,1] F1; empty → 0.
    """
    a = {w.lower() for w in _WORD.findall(str(completion or ""))}
    b = {w.lower() for w in _WORD.findall(str(gold or ""))}
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if inter == 0:
        return 0.0
    prec = inter / float(len(a))
    rec = inter / float(len(b))
    return float(2.0 * prec * rec / (prec + rec))


def is_usable_gen_span(text: str) -> bool:
    """True iff DECODE text is a readable short span (not mid-word junk)."""
    t = str(text or "").strip()
    if len(t) < 4 or is_period_collapse(t):
        return False
    if set(t) <= {".", " ", "`"}:
        return False
    if t[0].islower() and t[0].isalpha() and not t.startswith(("`", "_")):
        return False
    return len(_WORD.findall(t)) >= 1


def _continuation_after_prefix(full: str, seed: str) -> str:
    """Strip retrieved seed from decode; return student continuation."""
    if not seed:
        return full
    low = full.lower()
    plow = seed.lower()
    if low.startswith(plow):
        return full[len(seed) :].strip(" \t\n-–—:")
    if plow in low:
        i = low.find(plow)
        return (full[:i] + full[i + len(seed) :]).strip()
    return full


def _filler_heavy(cont: str) -> bool:
    words = [w.lower() for w in _WORD.findall(cont)]
    return len(words) >= 3 and len(set(words) & _FILLER) >= 2


def _long_unrelated_tail(*, cont: str, seed: str) -> bool:
    if len(cont) <= 40:
        return False
    if short_answer_token_f1(cont, seed) >= 0.15:
        return False
    return not any(c in cont for c in ("=", "(", ")", "/", "0x"))


def continuation_is_gibberish(*, text: str, prefix: str) -> bool:
    """
    GIVEN snippet-prefix seeded text
    WHEN inspecting student continuation after prefix
    THEN True iff continuation leaves retrieved-span readability.
    """
    full = normalize_gen_answer(text).strip()
    seed = normalize_gen_answer(prefix).strip()
    if not full:
        return True
    if not seed:
        return is_junk_decode(full) or not is_usable_gen_span(full)
    cont = _continuation_after_prefix(full, seed)
    if not cont:
        return False
    if is_junk_decode(cont):
        return True
    if cont[0].islower() and cont[0].isalpha():
        return True
    if _filler_heavy(cont):
        return True
    return _long_unrelated_tail(cont=cont, seed=seed)


def apply_gibberish_tail_gate(
    *,
    text: str,
    prefix: str = "",
) -> tuple[str, bool, bool]:
    """
    GIVEN decode text (+ optional snippet prefix)
    WHEN gibberish-tail gate fires
    THEN truncate to prefix (usable) or refuse; return (out, trunc, refuse).
    """
    cleaned = normalize_gen_answer(text)
    seed = normalize_gen_answer(prefix).strip()
    if not cleaned or is_period_collapse(cleaned):
        return cleaned, False, True
    if continuation_is_gibberish(text=cleaned, prefix=seed):
        if seed and is_usable_gen_span(seed):
            return seed, True, False
        return cleaned, False, True
    if not is_usable_gen_span(cleaned):
        if seed and is_usable_gen_span(seed):
            return seed, True, False
        return cleaned, False, True
    return cleaned, False, False


def score_nanogen5_lookup(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """LOOKUP arm — product retrieve ≠ generative IQ."""
    score, err, notes = score_nanogen4_lookup(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
        payload=payload,
    )
    notes = [n.replace("NANOGEN4 LOOKUP", "NANOGEN5 LOOKUP") for n in notes]
    return float(score), bool(err), notes


def _f1_to_score(f1: float) -> tuple[float, bool, str]:
    if f1 >= 0.90:
        return 9.0, False, f"strict F1={f1:.2f} exact-ish"
    if f1 >= 0.70:
        return 7.0, False, f"strict F1={f1:.2f} strong"
    if f1 >= 0.50:
        return 6.0, False, f"strict F1={f1:.2f} solid"
    if f1 >= 0.35:
        return 5.5, False, f"strict F1={f1:.2f} bar-edge"
    if f1 >= 0.20:
        return 5.0, True, f"strict F1={f1:.2f} partial"
    return 4.0, True, f"strict F1={f1:.2f} weak"


def score_nanogen5_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
    peak_ablated: bool,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN DECODE/GENERATE completion
    WHEN scoring AU3 STRICT judge
    THEN gold-substring alone insufficient; gibberish-tail fails;
         short-answer F1/HITL; bank/peak compare-only on ablated.
    """
    if peak_ablated and bool(payload.get("bank_grounded")):
        return (
            4.0,
            True,
            [
                "NANOGEN5 ablated — bank-gold rewrite is compare only",
                "excluded from strict ablated gate (anti-FP)",
            ],
        )
    if peak_ablated and bool(payload.get("peak_used")):
        return (
            4.0,
            True,
            [
                "NANOGEN5 ablated — peak overlay is compare only",
                "excluded from strict ablated gate (anti-FP)",
            ],
        )
    # Soft telemetry (GENERATE arm / period) via parent; then STRICT override.
    soft, soft_err, soft_notes = score_nanogen4_gen(
        completion=completion,
        expected_gold=expected_gold,
        payload={
            **dict(payload),
            "bank_grounded": False,
            "peak_used": False,
        },
        peak_ablated=peak_ablated,
    )
    notes = [
        "NANOGEN5 STRICT judge (short-answer F1/HITL)",
        f"soft_compare_score={soft}",
        *[n for n in soft_notes if "telemetry" in n.lower() or "period" in n.lower()],
    ]
    if soft <= 4.0 and soft_err and any(
        "telemetry" in n.lower() or "period" in n.lower() for n in soft_notes
    ):
        notes = [n.replace("NANOGEN4", "NANOGEN5") for n in soft_notes]
        return float(soft), True, notes
    if bool(payload.get("gibberish_tail")) and not bool(
        payload.get("gibberish_tail_truncated")
    ):
        return 4.0, True, notes + ["gibberish-tail fails STRICT judge"]
    text = normalize_gen_answer(completion)
    if not is_usable_gen_span(text):
        return 4.0, True, notes + ["usable_span_required failed"]
    f1 = short_answer_token_f1(text, expected_gold)
    g = str(expected_gold or "").strip().lower()
    buried = bool(g) and g in text.lower() and f1 < 0.35
    if buried:
        return (
            4.0,
            True,
            notes
            + [
                f"gold-substring alone insufficient (F1={f1:.2f})",
                "STRICT: require short-answer F1/HITL",
            ],
        )
    score, err, msg = _f1_to_score(f1)
    if bool(payload.get("snippet_prefix")):
        notes.append("snippet-prefix seed (RAG span + gated continue)")
    if bool(payload.get("gibberish_tail_truncated")):
        notes.append("gibberish-tail truncated to retrieved span")
    notes.append(msg)
    return float(score), bool(err), notes


def nanogen5_stats(
    *,
    lookup_scores: Sequence[float],
    lookup_errors: Sequence[bool],
    gen_scores: Sequence[float],
    gen_errors: Sequence[bool],
    gen_peak_scores: Sequence[float],
    gen_bank_scores: Sequence[float],
    n_true_hit: int,
    n_false_hit: int,
    n_period: int,
    n_fix: int,
    n_peak: int,
    n_bank_grounded: int,
    n_abstain: int,
    n_snippet_prefix: int = 0,
    n_gibberish_truncated: int = 0,
) -> dict[str, Any]:
    """
    GIVEN dual-arm + strict ablated scores (n=10)
    WHEN summarizing H-NANOGEN5
    THEN gate on strict gen_mean≥5.5; vs NANOGEN4 5.5; peak/bank compare.
    """
    base = nanogen4_stats(
        lookup_scores=lookup_scores,
        lookup_errors=lookup_errors,
        gen_scores=gen_scores,
        gen_errors=gen_errors,
        gen_peak_scores=gen_peak_scores,
        gen_bank_scores=gen_bank_scores,
        n_true_hit=n_true_hit,
        n_false_hit=n_false_hit,
        n_period=n_period,
        n_fix=n_fix,
        n_peak=n_peak,
        n_bank_grounded=n_bank_grounded,
        n_abstain=n_abstain,
        n_snippet_prefix=n_snippet_prefix,
    )
    g_mean = float(base["gen_mean"])
    p_mean = float(base["gen_peak_mean"])
    base["min_gen_mean"] = MIN_GEN_MEAN
    base["pass_gen"] = g_mean >= MIN_GEN_MEAN
    base["peak_only_lift"] = p_mean >= MIN_GEN_MEAN and g_mean < MIN_GEN_MEAN
    base["parent_nanogen4_ablated"] = PARENT_NANOGEN4_ABLATED
    base["beats_nanogen4_ablated"] = g_mean >= PARENT_NANOGEN4_ABLATED
    base["n_gibberish_truncated"] = int(n_gibberish_truncated)
    base["strict_judge"] = dict(STRICT_JUDGE)
    base["hypothesis"] = NANOGEN5_HYPOTHESIS
    return base


def decide_nanogen5(stats: Mapping[str, Any]) -> str:
    """
    GIVEN NANOGEN5 dual-arm + STRICT ablation stats
    WHEN applying pesquisa §5 AU3 gate
    THEN KILL if false-hit; PROMOTE iff lookup+strict_ablated≥5.5; else HOLD.
    """
    return decide_nanogen(stats)
