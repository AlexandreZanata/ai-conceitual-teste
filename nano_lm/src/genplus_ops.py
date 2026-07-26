"""Wave AI1 H-GENPLUS: push generative completions past GENLIFT (dual-arm)."""

from __future__ import annotations

import re
from typing import Any, Mapping, Sequence

from ai_session_ops import AI0_PACK
from antifp_ops import classify_arm, extract_telemetry
from asksmart_ops import (
    SERVEALIGN_MEAN,
    is_period_collapse,
    overlap_ratio,
    strip_stop,
)
from genc_prompt import jaccard, top_k_chunks
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "GENPLUS_ID",
    "GENPLUS_N",
    "GENPLUS_PACK",
    "MIN_LOOKUP_MEAN",
    "MIN_GEN_MEAN",
    "GENLIFT_GEN_MEAN",
    "SERVEALIGN_MEAN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "chunk_doc",
    "ground_prompt",
    "fit_prompt_tokens",
    "prefer_context_beam",
    "normalize_gen_answer",
    "score_genplus_lookup",
    "score_genplus_gen",
    "genplus_stats",
    "decide_genplus",
]

GENPLUS_ID = "H-GENPLUS"
GENPLUS_N = 10
MIN_LOOKUP_MEAN = 7.0
MIN_GEN_MEAN = 5.0  # pesquisa §5 AI1 — or honest HOLD
# Parent Wave AH GENLIFT open-gen ceiling under dual-arm Cursor EVAL.
GENLIFT_GEN_MEAN = 4.0

_WORD = re.compile(r"[a-z0-9]+", re.I)

# AI0 held-out pack (same questions for both arms).
GENPLUS_PACK: tuple[dict[str, str], ...] = tuple(
    {
        "id": p["id"],
        "app_id": p["app_id"],
        "source_id": p["source_id"],
        "question": p["question"],
        "gold": p["gold"],
    }
    for p in AI0_PACK
)


def chunk_doc(text: str, *, win: int = 320, stride: int = 160) -> list[str]:
    """
    GIVEN curated source text
    WHEN slicing for grounded gen
    THEN return overlapping windows (char surrogate).
    """
    raw = str(text or "")
    if not raw.strip():
        return []
    w = max(64, int(win))
    s = max(32, int(stride))
    out: list[str] = []
    for i in range(0, len(raw), s):
        piece = raw[i : i + w].strip()
        if len(piece) >= 40:
            out.append(piece)
        if i + w >= len(raw):
            break
    return out


def ground_prompt(
    question: str,
    *,
    chunks: Sequence[str],
    k: int = 3,
    max_ctx_chars: int = 720,
) -> str:
    """
    GIVEN question + source chunks
    WHEN building GENERATE prompt
    THEN prepend top-k Jaccard hits (char-capped) + short-answer framing.
    """
    hits = top_k_chunks(str(question), list(chunks), int(k))
    ctx = "\n\n".join(hits) if hits else ""
    cap = max(120, int(max_ctx_chars))
    if len(ctx) > cap:
        ctx = ctx[:cap].rsplit(" ", 1)[0].strip()
    head = f"Context:\n{ctx}\n\n" if ctx else ""
    return (
        f"{head}Question: {question}\n"
        "Short factual answer (copy a short phrase from context when possible):"
    )


def fit_prompt_tokens(prompt: str, *, max_chars: int = 900) -> str:
    """
    GIVEN grounded prompt
    WHEN enforcing student ctx budget (≤512 pos − max_new)
    THEN keep the tail (question + answer frame) within max_chars.
    """
    t = str(prompt)
    n = max(200, int(max_chars))
    if len(t) <= n:
        return t
    return t[-n:]



def prefer_context_beam(
    conts: Sequence[str],
    *,
    context: str,
) -> tuple[str, int, bool]:
    """
    GIVEN beam continuations + grounded context
    WHEN picking a gen completion
    THEN prefer non-period text with highest Jaccard vs context (not gold).
    """
    if not conts:
        return "", -1, False
    ranked: list[tuple[float, int, str]] = []
    for i, raw in enumerate(conts):
        cleaned = strip_stop(raw)
        if is_period_collapse(cleaned):
            ranked.append((-1.0, i, cleaned))
            continue
        score = jaccard(cleaned, context) if context else 0.0
        ranked.append((score, i, cleaned))
    ranked.sort(key=lambda t: (-t[0], t[1]))
    best_score, best_i, best_text = ranked[0]
    used = best_score >= 0.0 and not is_period_collapse(best_text)
    return best_text, int(best_i), used


def normalize_gen_answer(text: str) -> str:
    """
    GIVEN raw gen completion
    WHEN polishing for EVAL
    THEN first line, strip quotes/bullets, strip_stop.
    """
    t = strip_stop(text)
    if "\n" in t:
        t = t.split("\n", 1)[0].strip()
    t = t.lstrip("-*• ").strip().strip("\"'`")
    return strip_stop(t)


def _contains_phrase(hay: str, needle: str) -> bool:
    h = str(hay).lower()
    n = str(needle).lower().strip()
    if not h or not n:
        return False
    if len(n) <= 3:
        return bool(re.search(rf"(?<![a-z0-9]){re.escape(n)}(?![a-z0-9])", h))
    return n in h


def score_genplus_lookup(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """
    GIVEN LOOKUP arm ask
    WHEN Cursor EVAL
    THEN (score, error, notes); LOOKUP ≠ generative IQ.
    """
    from semwrap_ops import score_semwrap_trial

    score, err, notes = score_semwrap_trial(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
    )
    tel = extract_telemetry(payload)
    arm = classify_arm(payload)
    notes = list(notes) + [
        f"arm={arm} mode={tel['mode']} wall_ms={tel['wall_ms']} "
        f"n_new={tel['n_new']}",
        "GENPLUS LOOKUP product retrieve — not generative IQ",
        f"lookup_kind={lookup_kind}",
    ]
    if arm != "LOOKUP":
        return float(score), True, notes + ["LOOKUP arm mislabeled"]
    return float(score), bool(err), notes


def score_genplus_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """
    GIVEN GENERATE arm (grounded QPFB2+BEAMKV+anti-period)
    WHEN Cursor EVAL completion vs gold
    THEN exact→9; gold phrase in completion→7; overlap≥0.35→6;
         overlap≥0.2→5; period→1; else mid 4. Require gen telemetry.
    """
    text = normalize_gen_answer(completion)
    g = str(expected_gold).strip()
    tel = extract_telemetry(payload)
    arm = classify_arm(payload)
    period = is_period_collapse(text)
    base_notes = [
        f"arm={arm} mode={tel['mode']} wall_ms={tel['wall_ms']} "
        f"n_new={tel['n_new']} period={period}",
        "GENPLUS grounded gen — Cursor scores completion (not LOOKUP IQ)",
        f"beat GENLIFT gen={GENLIFT_GEN_MEAN} / SERVEALIGN={SERVEALIGN_MEAN}",
    ]
    if arm != "GENERATE" or tel["wall_ms"] <= 0.0 or tel["n_new"] <= 0:
        return 4.0, True, base_notes + ["gen telemetry fail"]
    if period:
        return 1.0, True, base_notes + ["period collapse"]
    if text and g and text.lower() == g.lower():
        return 9.0, False, base_notes + ["exact gold match"]
    if text and g and (
        _contains_phrase(text, g) or _contains_phrase(g, text)
    ):
        return 7.0, False, base_notes + ["gold phrase contained in completion"]
    ov = overlap_ratio(text, g)
    if ov >= 0.35:
        return 6.0, False, base_notes + [f"strong gold overlap={ov:.2f}"]
    if ov >= 0.20:
        return 5.0, True, base_notes + [f"partial gold overlap={ov:.2f}"]
    return 4.0, True, base_notes + [f"weak overlap={ov:.2f}; mid open"]


def genplus_stats(
    *,
    lookup_scores: Sequence[float],
    lookup_errors: Sequence[bool],
    gen_scores: Sequence[float],
    gen_errors: Sequence[bool],
    n_true_hit: int,
    n_false_hit: int,
    n_period: int,
    n_fix: int,
) -> dict[str, Any]:
    """
    GIVEN dual-arm scores
    WHEN summarizing H-GENPLUS
    THEN means + pass flags vs LOOKUP≥7 / GEN≥5.
    """
    if len(lookup_scores) != GENPLUS_N or len(gen_scores) != GENPLUS_N:
        raise ValueError(f"GENPLUS requires {GENPLUS_N} dual-arm scores")
    l_mean = float(sum(lookup_scores) / float(GENPLUS_N))
    g_mean = float(sum(gen_scores) / float(GENPLUS_N))
    n_l_err = int(sum(1 for e in lookup_errors if e))
    n_g_err = int(sum(1 for e in gen_errors if e))
    return {
        "n_trials": GENPLUS_N,
        "lookup_mean": l_mean,
        "gen_mean": g_mean,
        "n_lookup_errors": n_l_err,
        "n_gen_errors": n_g_err,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_period": int(n_period),
        "n_fix": int(n_fix),
        "min_lookup_mean": MIN_LOOKUP_MEAN,
        "min_gen_mean": MIN_GEN_MEAN,
        "genlift_gen_mean": GENLIFT_GEN_MEAN,
        "servealign_mean": SERVEALIGN_MEAN,
        "pass_lookup": l_mean >= MIN_LOOKUP_MEAN
        and n_l_err <= PASS_MAX_ERRORS,
        "pass_gen": g_mean >= MIN_GEN_MEAN,
        "beats_genlift_gen": g_mean > GENLIFT_GEN_MEAN,
        "beats_servealign": g_mean > SERVEALIGN_MEAN,
        "dual_arm": True,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_genplus(stats: Mapping[str, Any]) -> str:
    """
    GIVEN GENPLUS dual-arm stats
    WHEN applying pesquisa §5 AI1 gate
    THEN KILL if false-hit; PROMOTE if lookup+gen≥5; else HOLD.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("dual_arm")):
        return "KILL"
    if bool(stats.get("pass_lookup")) and bool(stats.get("pass_gen")):
        return "PROMOTE"
    return "HOLD"
