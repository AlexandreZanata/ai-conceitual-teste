"""Score student text under frozen code teacher (cross-tokenizer)."""

from __future__ import annotations

from typing import Any

import torch

from decode_early import decode_early
from early_ops import EarlyGene, clamp_early_gene
from eval_student import teacher_mean_logprob
from load_model import LoadedModel
from tchr_ops import STORY_TEACHER_ID, code_teacher_meta, lp_finite

__all__ = [
    "align_prompt_continuation",
    "code_teacher_mean_logprob",
    "collect_early_story_rows",
    "score_rows_code_teacher",
    "dual_means",
]


def align_prompt_continuation(
    tok: Any, prompt: str, continuation: str
) -> tuple[torch.Tensor, list[int]]:
    """
    GIVEN prompt + continuation text under a teacher tokenizer
    WHEN aligning BPE across the boundary
    THEN return (prompt_ids tensor, continuation token ids).
    """
    p_ids = list(tok.encode(prompt, add_special_tokens=True))
    f_ids = list(tok.encode(prompt + continuation, add_special_tokens=True))
    n = 0
    for a, b in zip(p_ids, f_ids):
        if a != b:
            break
        n += 1
    if n == 0 or n >= len(f_ids):
        n = min(len(p_ids), max(len(f_ids) - 1, 0))
    cont = f_ids[n:]
    prompt_t = torch.tensor([f_ids[:n]], dtype=torch.long)
    return prompt_t, cont


def code_teacher_mean_logprob(
    teacher: LoadedModel, prompt: str, continuation: str
) -> float:
    """
    GIVEN frozen code teacher + prompt/continuation text
    WHEN scoring length-normalized continuation log-prob
    THEN return code_teacher_lp (same API shape as story teacher_lp).
    """
    if not continuation:
        return float("-inf")
    prompt_t, cont = align_prompt_continuation(
        teacher.tokenizer, prompt, continuation
    )
    return teacher_mean_logprob(teacher, prompt_t, cont)


def collect_early_story_rows(
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    gene: EarlyGene,
    max_new: int,
    seed: int,
    family: str = "H-EARLY",
) -> list[dict[str, Any]]:
    """
    GIVEN EARLY gene + story teacher
    WHEN decoding prog prompts
    THEN return rows with story_teacher_lp + continuation text.
    """
    g = clamp_early_gene(gene)
    if "n" in gene:
        g["n"] = int(max(1, int(gene["n"])))
    if "temperature" in gene:
        g["temperature"] = float(gene["temperature"])
    tok = teacher.tokenizer
    device = teacher.device
    rows: list[dict[str, Any]] = []
    for i, text in enumerate(prompts):
        result = decode_early(
            student,
            tok,
            text,
            n=int(g["n"]),
            max_new_tokens=max_new,
            min_new=int(g["min_new"]),
            conf_threshold=float(g["conf_threshold"]),
            patience=int(g["patience"]),
            temperature=float(g["temperature"]),
            top_p=float(g["top_p"]),
            seed=seed + i,
            device=device,
        )
        ids = tok.encode(text, return_tensors="pt")
        story_lp = teacher_mean_logprob(teacher, ids, list(result.token_ids))
        rows.append(
            {
                "family": family,
                "prompt": text,
                "continuation": result.text,
                "story_teacher_id": STORY_TEACHER_ID,
                "story_teacher_lp": float(story_lp),
                "wall_ms": float(result.wall_ms),
                "n_new": len(result.token_ids),
                "seed": int(seed),
            }
        )
    return rows


def score_rows_code_teacher(
    teacher: LoadedModel, rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    GIVEN rows with prompt/continuation text
    WHEN scoring under the frozen code teacher
    THEN attach code_teacher_lp + named teacher meta (never silent swap).
    """
    meta = code_teacher_meta()
    out: list[dict[str, Any]] = []
    for r in rows:
        code_lp = code_teacher_mean_logprob(
            teacher, str(r["prompt"]), str(r["continuation"])
        )
        out.append(
            {
                **r,
                "code_teacher_id": meta["hf_id"],
                "code_teacher_lp": float(code_lp),
                "code_teacher_params": meta["params"],
                "code_teacher_license": meta["license"],
            }
        )
    return out


def dual_means(rows: list[dict[str, Any]]) -> dict[str, float]:
    """Aggregate dual teacher metrics; empty → non-finite sentinels."""
    if not rows:
        return {
            "mean_story_lp": float("-inf"),
            "mean_code_lp": float("-inf"),
            "mean_wall_ms": float("nan"),
            "n": 0.0,
            "n_code_finite": 0.0,
        }
    story = [float(r["story_teacher_lp"]) for r in rows]
    code = [float(r["code_teacher_lp"]) for r in rows]
    walls = [float(r["wall_ms"]) for r in rows]
    n = float(len(rows))
    return {
        "mean_story_lp": sum(story) / n,
        "mean_code_lp": sum(code) / n,
        "mean_wall_ms": sum(walls) / n,
        "n": n,
        "n_code_finite": float(sum(1 for x in code if lp_finite(x))),
    }
