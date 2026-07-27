"""Wave AW3 H-NANOGEN7: teacher-anchored novel continue (TAC); span ≠ gen IQ."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from abstain_ops import is_junk_decode
from aw_session_ops import AW0_NANOGEN7_HYPOTHESIS, AW0_TRUE_GEN_JUDGE
from genbase_ops import normalize_gen_answer
from nanogen5_ops import _continuation_after_prefix, _f1_to_score
from nanogen6_ops import (
    MIN_LOOKUP_MEAN,
    NANOGEN6_N,
    NANOGEN6_PACK,
    apply_bank_grounded_short,
    apply_refuse_or_continue,
    apply_snippet_prefix_decode,
    continuation_is_gibberish,
    is_usable_gen_span,
    nanogen6_stats,
    score_nanogen6_lookup,
    short_answer_token_f1,
)
from nanogen_ops import decide_nanogen
from tchr_ops import CODE_TEACHER_ID, code_teacher_meta

__all__ = [
    "NANOGEN7_ID",
    "NANOGEN7_N",
    "NANOGEN7_PACK",
    "NANOGEN7_THESIS",
    "NANOGEN7_HYPOTHESIS",
    "PARENT_NANOGEN6_TRUE_CONTINUE",
    "MIN_LOOKUP_MEAN",
    "MIN_TRUE_CONTINUE_MEAN",
    "MIN_TEACHER_TOPK_FRAC",
    "TAC_TOP_K",
    "TRUE_GEN_JUDGE",
    "CONTINUE_KINDS",
    "code_teacher_meta",
    "CODE_TEACHER_ID",
    "apply_bank_grounded_short",
    "apply_snippet_prefix_decode",
    "apply_refuse_or_continue",
    "apply_tac_continue",
    "teacher_topk_hit_fraction",
    "score_nanogen7_lookup",
    "score_nanogen7_gen",
    "nanogen7_stats",
    "decide_nanogen7",
]

NANOGEN7_ID = "H-NANOGEN7"
NANOGEN7_N = NANOGEN6_N
NANOGEN7_PACK = NANOGEN6_PACK  # fair compare vs archived NANOGEN6 HOLD
NANOGEN7_HYPOTHESIS = AW0_NANOGEN7_HYPOTHESIS
PARENT_NANOGEN6_TRUE_CONTINUE = 0.0  # AV HOLD archive
MIN_TRUE_CONTINUE_MEAN = 5.5
MIN_TEACHER_TOPK_FRAC = 0.50
TAC_TOP_K = 32
TRUE_GEN_JUDGE = dict(AW0_TRUE_GEN_JUDGE)
CONTINUE_KINDS = frozenset({"true_continue", "span_fallback", "abstain"})
NANOGEN7_THESIS = (
    "Ablated DECODE TAC: novel tokens vs retrieved span AND code-teacher "
    "top-k at each step; pure span copy → PEAK (zero gen credit); "
    "no teacher-consistent novel continue → ABSTAIN; not NANOGEN6 "
    "refuse-or-continue rename; bar = true_continue_ablated≥5.5 else HOLD"
)


def teacher_topk_hit_fraction(
    teacher: Any,
    prompt: str,
    continuation: str,
    *,
    k: int = TAC_TOP_K,
) -> float:
    """
    GIVEN frozen code teacher + prompt/continuation
    WHEN checking each continuation token against teacher top-k
    THEN return hit fraction in [0, 1] (0 if empty).
    """
    import torch
    from tchr_score import align_prompt_continuation

    cont_text = str(continuation or "")
    if not cont_text.strip():
        return 0.0
    prompt_t, cont = align_prompt_continuation(
        teacher.tokenizer, str(prompt), cont_text
    )
    if not cont:
        return 0.0
    device = teacher.device
    ids = prompt_t.to(device)
    hits = 0
    kk = max(1, int(k))
    with torch.no_grad():
        for tok in cont:
            out = teacher.model(ids)
            logits = out.logits[:, -1, :].float()
            top = torch.topk(logits, k=min(kk, logits.size(-1)), dim=-1)
            allowed = {int(x) for x in top.indices[0].tolist()}
            if int(tok) in allowed:
                hits += 1
            nxt = torch.tensor([[tok]], device=device, dtype=ids.dtype)
            ids = torch.cat([ids, nxt], dim=1)
    return float(hits) / float(len(cont))


def apply_tac_continue(
    *,
    text: str,
    prefix: str = "",
    teacher_topk_frac: float | None = None,
    min_frac: float = MIN_TEACHER_TOPK_FRAC,
) -> tuple[str, str, bool, bool, bool]:
    """
    GIVEN decode text (+ optional snippet prefix) + teacher top-k fraction
    WHEN applying TAC law (≠ NANOGEN6 refuse-or-continue alone)
    THEN return (out, kind, truncated, refuse, teacher_ok)
         kind ∈ {true_continue, span_fallback, abstain}.
    """
    out, kind, trunc, refuse = apply_refuse_or_continue(
        text=text, prefix=prefix
    )
    if kind != "true_continue":
        return out, kind, trunc, refuse, False
    seed = normalize_gen_answer(prefix).strip()
    cleaned = normalize_gen_answer(out)
    cont = _continuation_after_prefix(cleaned, seed) if seed else cleaned
    if not cont.strip():
        return cleaned, "span_fallback", True, False, False
    if teacher_topk_frac is None:
        # Runner must supply teacher score — missing gate ⇒ refuse.
        return cleaned, "abstain", False, True, False
    if float(teacher_topk_frac) < float(min_frac):
        return cleaned, "abstain", False, True, False
    return cleaned, "true_continue", False, False, True


def score_nanogen7_lookup(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """LOOKUP arm — product retrieve ≠ generative IQ."""
    score, err, notes = score_nanogen6_lookup(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
        payload=payload,
    )
    notes = [n.replace("NANOGEN6 LOOKUP", "NANOGEN7 LOOKUP") for n in notes]
    return float(score), bool(err), notes


def score_nanogen7_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
    peak_ablated: bool,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN DECODE/GENERATE completion
    WHEN scoring AW3 TAC true-gen judge
    THEN span-fallback / no teacher top-k → 4.0 (≠ gen IQ);
         true continue requires novel + teacher_topk_ok + F1/HITL.
    """
    notes = ["NANOGEN7 TAC true-gen judge (teacher-anchored novel continue)"]
    if peak_ablated and bool(payload.get("bank_grounded")):
        return (
            4.0,
            True,
            notes
            + [
                "bank-gold rewrite is compare only",
                "excluded from true_continue gate (anti-FP)",
            ],
        )
    if peak_ablated and bool(payload.get("peak_used")):
        return (
            4.0,
            True,
            notes
            + [
                "peak overlay is compare only",
                "excluded from true_continue gate (anti-FP)",
            ],
        )
    kind = str(payload.get("continue_kind") or "")
    if bool(payload.get("span_fallback")) or kind == "span_fallback":
        return (
            4.0,
            True,
            notes
            + [
                "span-fallback ≠ gen IQ (PEAK/LOOKUP credit only)",
                "not a NANOGEN6 refuse-or-continue rename win",
            ],
        )
    if (
        bool(payload.get("abstained"))
        or kind == "abstain"
        or str(payload.get("product_mode") or "") == "ABSTAIN"
    ):
        return (
            4.0,
            True,
            notes + ["TAC: ABSTAIN (no teacher-consistent novel continue)"],
        )
    if not bool(payload.get("teacher_topk_ok")):
        return (
            4.0,
            True,
            notes
            + [
                "teacher top-k gate failed / missing",
                "TAC requires code-teacher top-k novel continue",
            ],
        )
    text = normalize_gen_answer(completion)
    if is_junk_decode(text) or not is_usable_gen_span(text):
        return 4.0, True, notes + ["usable true_continue required"]
    if continuation_is_gibberish(text=text, prefix=""):
        return 4.0, True, notes + ["gibberish continue fails TAC"]
    if float(payload.get("wall_ms") or 0.0) <= 0.0:
        return 4.0, True, notes + ["wall_ms mandatory but insufficient alone"]
    if int(payload.get("n_new") or 0) <= 0:
        return 4.0, True, notes + ["n_new mandatory but insufficient alone"]
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
                "true_continue requires short-answer F1/HITL",
            ],
        )
    score, err, msg = _f1_to_score(f1)
    frac = payload.get("teacher_topk_frac")
    if frac is not None:
        notes.append(f"teacher_topk_frac={float(frac):.3f}")
    if bool(payload.get("snippet_prefix")):
        notes.append("snippet-prefix seed + TAC novel continue")
    notes.append(msg)
    return float(score), bool(err), notes


def nanogen7_stats(
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
    n_span_fallback: int = 0,
    n_true_continue: int = 0,
    n_teacher_topk_pass: int = 0,
) -> dict[str, Any]:
    """
    GIVEN dual-arm + TAC true_continue scores (n=10)
    WHEN summarizing H-NANOGEN7
    THEN gate on true_continue_ablated≥5.5; span/teacher-fail = 0 gen credit.
    """
    base = nanogen6_stats(
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
        n_span_fallback=n_span_fallback,
        n_true_continue=n_true_continue,
    )
    g_mean = float(base["gen_mean"])
    base["min_gen_mean"] = MIN_TRUE_CONTINUE_MEAN
    base["pass_gen"] = g_mean >= MIN_TRUE_CONTINUE_MEAN
    base["parent_nanogen6_true_continue"] = PARENT_NANOGEN6_TRUE_CONTINUE
    base["beats_nanogen6_true_continue"] = (
        float(n_true_continue) > PARENT_NANOGEN6_TRUE_CONTINUE
    )
    base["n_teacher_topk_pass"] = int(n_teacher_topk_pass)
    base["teacher_topk_gate"] = True
    base["novel_vs_span_required"] = True
    base["nanogen6_refuse_or_continue_archived"] = True
    base["span_fallback_neq_gen"] = True
    base["true_gen_judge"] = dict(TRUE_GEN_JUDGE)
    base["hypothesis"] = NANOGEN7_HYPOTHESIS
    base["code_teacher"] = code_teacher_meta()
    if int(n_span_fallback) > 0 and int(n_true_continue) == 0:
        base["pass_gen"] = False
        base["peak_only_lift"] = True
    if int(n_true_continue) > 0 and int(n_teacher_topk_pass) == 0:
        base["pass_gen"] = False
        base["peak_only_lift"] = True
    return base


def decide_nanogen7(stats: Mapping[str, Any]) -> str:
    """
    GIVEN NANOGEN7 dual-arm + TAC true_continue ablation stats
    WHEN applying pesquisa §2 AW3 gate
    THEN KILL if false-hit; PROMOTE iff lookup+true_continue≥5.5; else HOLD.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("span_fallback_neq_gen")):
        return "KILL"
    if not bool(stats.get("teacher_topk_gate")):
        return "KILL"
    if not bool(stats.get("nanogen6_refuse_or_continue_archived")):
        return "KILL"
    return decide_nanogen(stats)
