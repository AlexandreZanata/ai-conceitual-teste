"""Score fp EARLY vs int8-weight EARLY for H-QT."""

from __future__ import annotations

from typing import Any

from decode_early import decode_early
from early_ops import EarlyGene, clamp_early_gene
from load_model import LoadedModel
from qt_quant import weight_nbytes
from tchr_ops import STORY_TEACHER_ID, code_teacher_meta
from tchr_score import code_teacher_mean_logprob, dual_means

__all__ = ["collect_early_rows", "attach_code_teacher", "arm_means"]


def _gene(gene: EarlyGene) -> EarlyGene:
    g = clamp_early_gene(gene)
    if "n" in gene:
        g["n"] = int(max(1, int(gene["n"])))
    if "temperature" in gene:
        g["temperature"] = float(gene["temperature"])
    return g


def collect_early_rows(
    *,
    story_teacher: LoadedModel,
    student: object,
    prompts: list[str],
    gene: EarlyGene,
    max_new: int,
    seed: int,
    family: str,
    weight_bytes: int,
) -> list[dict[str, Any]]:
    """Decode EARLY; score story_lp on the decode prompt."""
    g = _gene(gene)
    tok = story_teacher.tokenizer
    device = story_teacher.device
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
        story_lp = code_teacher_mean_logprob(
            story_teacher, text, result.text
        )
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
                "weight_bytes": int(weight_bytes),
            }
        )
    return rows


def attach_code_teacher(
    code_teacher: LoadedModel, rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    meta = code_teacher_meta()
    out: list[dict[str, Any]] = []
    for r in rows:
        code_lp = code_teacher_mean_logprob(
            code_teacher, str(r["prompt"]), str(r["continuation"])
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


def arm_means(rows: list[dict[str, Any]]) -> dict[str, float]:
    means = dual_means(rows)
    if rows:
        means["weight_bytes"] = float(rows[0]["weight_bytes"])
    else:
        means["weight_bytes"] = float("nan")
    return means
