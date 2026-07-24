"""Score MINP×NGRAM stacked decode with teacher_lp + wall."""

from __future__ import annotations

from decode_mng import decode_mng
from eval_student import teacher_mean_logprob
from load_model import LoadedModel


def fitness_mng_detail(
    *,
    min_p: float,
    ngram_size: int,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
    temperature: float = 0.8,
    top_p: float = 0.9,
) -> tuple[float, float]:
    """
    GIVEN tip min_p + ngram_size and prompts
    WHEN decoding with both filters
    THEN return (mean teacher_lp, mean wall_ms).
    """
    tok = teacher.tokenizer
    device = teacher.device
    scores: list[float] = []
    walls: list[float] = []
    for i, text in enumerate(prompts):
        result = decode_mng(
            student,
            tok,
            text,
            max_new_tokens=max_new,
            temperature=temperature,
            top_p=top_p,
            min_p=float(min_p),
            ngram_size=int(ngram_size),
            seed=seed + i,
            device=device,
        )
        walls.append(float(result.wall_ms))
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
    return sum(scores) / len(scores), sum(walls) / len(walls)
