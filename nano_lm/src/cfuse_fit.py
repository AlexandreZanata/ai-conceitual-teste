"""Score H-CFUSE: chunked prefill ⊕ gated KV under FLASH SDPA."""

from __future__ import annotations

from chunk_fit import fitness_chunk_detail
from chunk_ops import DEFAULT_CHUNK
from decode_chunk import decode_early_chunked
from decode_early import decode_early
from early_ops import EarlyGene, clamp_early_gene
from eval_student import teacher_mean_logprob
from flash_ops import gpt_neo_sdpa_context
from flop_ops import est_decode_flops, to_gflops
from fuse_fit import fitness_fuse_detail
from kvsel_fit import fitness_early_dual
from kvsel_ops import SMOKE_BUDGETS, should_use_kv
from load_model import LoadedModel
from short_fit import tip_row
from student_model import count_params

__all__ = [
    "fitness_chunk_dual",
    "fitness_cfuse_detail",
    "fitness_early_dual",
    "fitness_fuse_detail",
    "tip_row",
    "DEFAULT_CHUNK",
]


def _mean3(rows: list[tuple[float, float, float]]) -> tuple[float, float, float]:
    n = max(len(rows), 1)
    return (
        sum(r[0] for r in rows) / n,
        sum(r[1] for r in rows) / n,
        sum(r[2] for r in rows) / n,
    )


def fitness_chunk_dual(
    early: EarlyGene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    seed: int,
    chunk_size: int = DEFAULT_CHUNK,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> tuple[float, float, float]:
    """Mean (lp, wall, gflops) for CHUNK across decode budgets."""
    rows = [
        fitness_chunk_detail(
            early,
            teacher=teacher,
            student=student,
            prompts=prompts,
            max_new=b,
            seed=seed + 1000 * b,
            chunk_size=chunk_size,
        )
        for b in budgets
    ]
    return _mean3(rows)


def fitness_cfuse_detail(
    early: EarlyGene,
    kv_threshold: int,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    seed: int,
    chunk_size: int = DEFAULT_CHUNK,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> tuple[float, float, float]:
    """
    GIVEN EARLY tip + KVSEL threshold + chunk_size under SDPA
    WHEN decoding dual budgets (chunked KV iff gated on)
    THEN return mean (teacher_lp, wall_ms, est_gflops).
    """
    e = clamp_early_gene(early)
    tok = teacher.tokenizer
    device = teacher.device
    n_params = count_params(student)
    scores: list[float] = []
    walls: list[float] = []
    gflops: list[float] = []
    with gpt_neo_sdpa_context():
        for b in budgets:
            use_kv = should_use_kv(b, kv_threshold)
            for i, text in enumerate(prompts):
                lp, wall, gf = _one(
                    e,
                    teacher=teacher,
                    student=student,
                    tok=tok,
                    device=device,
                    text=text,
                    max_new=b,
                    seed=seed + 1000 * b + i,
                    use_kv=use_kv,
                    chunk_size=chunk_size,
                    n_params=n_params,
                )
                scores.append(lp)
                walls.append(wall)
                gflops.append(gf)
    n = max(len(scores), 1)
    return sum(scores) / n, sum(walls) / n, sum(gflops) / n


def _one(
    e: EarlyGene,
    *,
    teacher: LoadedModel,
    student: object,
    tok: object,
    device: object,
    text: str,
    max_new: int,
    seed: int,
    use_kv: bool,
    chunk_size: int,
    n_params: int,
) -> tuple[float, float, float]:
    """One prompt decode; chunked path when use_kv else eager EARLY."""
    common = dict(
        n=int(e["n"]),
        max_new_tokens=max_new,
        min_new=int(e["min_new"]),
        conf_threshold=float(e["conf_threshold"]),
        patience=int(e["patience"]),
        temperature=float(e["temperature"]),
        top_p=float(e["top_p"]),
        seed=seed,
        device=device,
    )
    if use_kv:
        result = decode_early_chunked(
            student, tok, text, chunk_size=int(chunk_size), **common
        )
    else:
        result = decode_early(student, tok, text, **common)
    ids = tok.encode(text, return_tensors="pt")
    lp = teacher_mean_logprob(teacher, ids, list(result.token_ids))
    flops = est_decode_flops(
        n_params=n_params,
        prompt_len=int(ids.shape[1]),
        n_new=len(result.token_ids),
        token_evals=result.token_evals,
    )
    return lp, result.wall_ms, to_gflops(flops)
