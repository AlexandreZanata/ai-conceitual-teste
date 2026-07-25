"""Score H-GENC genomes: stride/retrieve prompt + chunked EARLY ± int8."""

from __future__ import annotations

from typing import Any

from decode_chunk import decode_early_chunked
from early_ops import EarlyGene, clamp_early_gene
from genc_ops import GencGene, clamp_genc_gene
from genc_prompt import apply_genc_prompt
from load_model import LoadedModel
from qt_quant import quantize_student_int8, weight_nbytes
from tchr_ops import STORY_TEACHER_ID, code_teacher_meta
from tchr_score import code_teacher_mean_logprob, dual_means

__all__ = [
    "early_from_exit",
    "prepare_student",
    "score_gene_rows",
    "attach_code_teacher",
    "arm_means",
    "fit_score",
]


def early_from_exit(base: EarlyGene, exit_depth: int) -> EarlyGene:
    """Map exit_depth→EARLY patience knobs (1=aggressive, 2=parent gene)."""
    g = clamp_early_gene(base)
    g["n"] = 1
    g["temperature"] = 1e-6
    if int(exit_depth) <= 1:
        g["min_new"] = 4
        g["patience"] = 1
        g["conf_threshold"] = 0.55
    return g


def prepare_student(student: object, quant_bits: int) -> tuple[object, int]:
    """Return (model, weight_bytes); int8 when quant_bits≤8."""
    if int(quant_bits) <= 8:
        q = quantize_student_int8(student)  # type: ignore[arg-type]
        return q, weight_nbytes(q)
    return student, weight_nbytes(student)  # type: ignore[arg-type]


def score_gene_rows(
    *,
    story_teacher: LoadedModel,
    student: object,
    prompts: list[str],
    gene: GencGene,
    early: EarlyGene,
    chunks: list[str],
    max_new: int,
    seed: int,
    family: str,
) -> list[dict[str, Any]]:
    """Decode under genome; story_lp on bare task; code filled later."""
    g = clamp_genc_gene(gene)
    eg = early_from_exit(early, int(g["exit_depth"]))
    model, nbytes = prepare_student(student, int(g["quant_bits"]))
    if hasattr(model, "to"):
        model.to(story_teacher.device)
    tok = story_teacher.tokenizer
    device = story_teacher.device
    rows: list[dict[str, Any]] = []
    for i, task in enumerate(prompts):
        ctx = apply_genc_prompt(
            task,
            k_retrieve=int(g["k_retrieve"]),
            chunks=chunks,
            stride=int(g["stride"]),
            chunk_len=int(g["chunk_len"]),
        )
        result = decode_early_chunked(
            model,
            tok,
            ctx,
            n=int(eg["n"]),
            max_new_tokens=max_new,
            min_new=int(eg["min_new"]),
            conf_threshold=float(eg["conf_threshold"]),
            patience=int(eg["patience"]),
            temperature=float(eg["temperature"]),
            top_p=float(eg["top_p"]),
            seed=seed + i,
            device=device,
            chunk_size=int(g["chunk_len"]),
        )
        story_lp = code_teacher_mean_logprob(
            story_teacher, task, result.text
        )
        rows.append(
            {
                "family": family,
                "prompt": task,
                "continuation": result.text,
                "story_teacher_id": STORY_TEACHER_ID,
                "story_teacher_lp": float(story_lp),
                "wall_ms": float(result.wall_ms),
                "n_new": len(result.token_ids),
                "seed": int(seed),
                "weight_bytes": int(nbytes),
                "gene": dict(g),
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
    return means


def fit_score(rows: list[dict[str, Any]]) -> float:
    """Latency-aware story fit (higher better); used only on fit prompts."""
    if not rows:
        return float("-inf")
    lp = sum(float(r["story_teacher_lp"]) for r in rows) / len(rows)
    wall = sum(float(r["wall_ms"]) for r in rows) / len(rows)
    return float(lp) - 0.01 * float(wall)
