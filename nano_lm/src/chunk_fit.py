"""Score H-CHUNK: chunked KV prefill under FLASH SDPA on long prompts."""

from __future__ import annotations

from chunk_ops import DEFAULT_CHUNK, LONG_TARGET_TOKENS, elongate_prompt
from decode_chunk import decode_early_chunked
from early_ops import EarlyGene, clamp_early_gene
from eval_student import teacher_mean_logprob
from flash_ops import gpt_neo_sdpa_context
from flop_ops import est_decode_flops, to_gflops
from load_model import LoadedModel
from short_fit import tip_row
from student_model import count_params

__all__ = [
    "fitness_chunk_detail",
    "long_prompts",
    "tip_row",
    "DEFAULT_CHUNK",
    "LONG_TARGET_TOKENS",
]


def long_prompts(
    texts: list[str],
    tokenizer: object,
    *,
    target_tokens: int = LONG_TARGET_TOKENS,
) -> list[str]:
    """Elongate each prompt to ≥ target_tokens."""
    return [
        elongate_prompt(t, tokenizer, target_tokens=target_tokens) for t in texts
    ]


def fitness_chunk_detail(
    early: EarlyGene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
    chunk_size: int = DEFAULT_CHUNK,
) -> tuple[float, float, float]:
    """
    GIVEN frozen EARLY tip + chunk_size under SDPA
    WHEN decoding with chunked KV prefill
    THEN return (mean teacher_lp, mean wall_ms, mean est_gflops).
    """
    e = clamp_early_gene(early)
    tok = teacher.tokenizer
    device = teacher.device
    n_params = count_params(student)
    scores: list[float] = []
    walls: list[float] = []
    gflops: list[float] = []
    with gpt_neo_sdpa_context():
        for i, text in enumerate(prompts):
            result = decode_early_chunked(
                student,
                tok,
                text,
                n=int(e["n"]),
                max_new_tokens=max_new,
                min_new=int(e["min_new"]),
                conf_threshold=float(e["conf_threshold"]),
                patience=int(e["patience"]),
                temperature=float(e["temperature"]),
                top_p=float(e["top_p"]),
                seed=seed + i,
                device=device,
                chunk_size=int(chunk_size),
            )
            walls.append(result.wall_ms)
            ids = tok.encode(text, return_tensors="pt")
            scores.append(
                teacher_mean_logprob(teacher, ids, list(result.token_ids))
            )
            flops = est_decode_flops(
                n_params=n_params,
                prompt_len=int(ids.shape[1]),
                n_new=len(result.token_ids),
                token_evals=result.token_evals,
            )
            gflops.append(to_gflops(flops))
    n = max(len(scores), 1)
    return sum(scores) / n, sum(walls) / n, sum(gflops) / n
