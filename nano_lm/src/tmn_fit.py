"""Score TYP×MINP stacked decode with teacher_lp + wall."""

from __future__ import annotations

from decode_tmn import decode_tmn
from eval_student import teacher_mean_logprob
from load_model import LoadedModel


def fitness_tmn_detail(
    *,
    typ_mass: float,
    min_p: float,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
    temperature: float = 0.8,
    top_p: float = 0.9,
) -> tuple[float, float]:
    """
    GIVEN tip typ_mass + min_p and prompts
    WHEN decoding with both filters
    THEN return (mean teacher_lp, mean wall_ms).
    """
    tok = teacher.tokenizer
    device = teacher.device
    scores: list[float] = []
    walls: list[float] = []
    for i, text in enumerate(prompts):
        result = decode_tmn(
            student,
            tok,
            text,
            max_new_tokens=max_new,
            temperature=temperature,
            top_p=top_p,
            typ_mass=float(typ_mass),
            min_p=float(min_p),
            seed=seed + i,
            device=device,
        )
        walls.append(float(result.wall_ms))
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
    return sum(scores) / len(scores), sum(walls) / len(walls)
