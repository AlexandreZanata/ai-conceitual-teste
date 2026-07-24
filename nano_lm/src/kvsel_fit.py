"""Score H-KVSEL genes: dual-budget mean vs EARLY tip."""

from __future__ import annotations

from decode_kvsel import decode_kvsel
from early_ops import EarlyGene, clamp_early_gene
from eval_student import teacher_mean_logprob
from flop_ops import to_gflops
from kvsel_ops import (
    SMOKE_BUDGETS,
    clamp_kvsel_gene,
    est_kvsel_flops,
    should_use_kv,
)
from load_model import LoadedModel
from short_fit import fitness_early_detail, tip_row
from student_model import count_params

__all__ = [
    "fitness_kvsel_detail",
    "fitness_early_dual",
    "pick_kvsel_threshold",
    "warmup_kvsel",
    "tip_row",
]


def _mean3(rows: list[tuple[float, float, float]]) -> tuple[float, float, float]:
    n = max(len(rows), 1)
    return (
        sum(r[0] for r in rows) / n,
        sum(r[1] for r in rows) / n,
        sum(r[2] for r in rows) / n,
    )


def warmup_kvsel(
    early: EarlyGene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> None:
    """Warm GPU kernels for eager + KV before timed claim."""
    e = clamp_early_gene(early)
    text = prompts[0]
    tok = teacher.tokenizer
    device = teacher.device
    for b in budgets:
        for use_kv in (False, True):
            decode_kvsel(
                student,
                tok,
                text,
                n=int(e["n"]),
                max_new_tokens=min(8, int(b)),
                min_new=1,
                conf_threshold=float(e["conf_threshold"]),
                patience=int(e["patience"]),
                temperature=float(e["temperature"]),
                top_p=float(e["top_p"]),
                seed=0,
                device=device,
                use_kv=use_kv,
            )


def fitness_early_dual(
    early: EarlyGene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    seed: int,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> tuple[float, float, float]:
    """Mean (lp, wall, gflops) across decode budgets for EARLY tip."""
    rows = [
        fitness_early_detail(
            early,
            teacher=teacher,
            student=student,
            prompts=prompts,
            max_new=b,
            seed=seed + 1000 * b,
        )
        for b in budgets
    ]
    return _mean3(rows)


def fitness_kvsel_detail(
    early: EarlyGene,
    kv_threshold: int,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    seed: int,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> tuple[float, float, float]:
    """
    GIVEN EARLY tip + kv_threshold
    WHEN decoding each budget with gated KV
    THEN return mean (teacher_lp, wall_ms, est_gflops).
    """
    e = clamp_early_gene(early)
    g = clamp_kvsel_gene({"kv_threshold": kv_threshold})
    thr = int(g["kv_threshold"])
    tok = teacher.tokenizer
    device = teacher.device
    n_params = count_params(student)
    scores: list[float] = []
    walls: list[float] = []
    gflops: list[float] = []
    for b in budgets:
        use_kv = should_use_kv(b, thr)
        for i, text in enumerate(prompts):
            result = decode_kvsel(
                student,
                tok,
                text,
                n=int(e["n"]),
                max_new_tokens=b,
                min_new=int(e["min_new"]),
                conf_threshold=float(e["conf_threshold"]),
                patience=int(e["patience"]),
                temperature=float(e["temperature"]),
                top_p=float(e["top_p"]),
                seed=seed + 1000 * b + i,
                device=device,
                use_kv=use_kv,
            )
            walls.append(result.wall_ms)
            ids = tok.encode(text, return_tensors="pt")
            scores.append(
                teacher_mean_logprob(teacher, ids, list(result.token_ids))
            )
            flops = est_kvsel_flops(
                n_params=n_params,
                prompt_len=int(ids.shape[1]),
                n_new=len(result.token_ids),
                use_kv=use_kv,
            )
            gflops.append(to_gflops(flops))
    n = max(len(scores), 1)
    return sum(scores) / n, sum(walls) / n, sum(gflops) / n


def pick_kvsel_threshold(
    early: EarlyGene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    seed: int,
    thresholds: tuple[int, ...],
    tip_lp: float,
    tip_wall: float,
    eps_lp: float,
) -> tuple[int, float, float, float]:
    """
    GIVEN threshold grid
    WHEN scoring each gene
    THEN prefer quality-ok with wall < tip; else best quality-ok; else min wall.
    """
    ok: list[tuple[int, float, float, float]] = []
    all_rows: list[tuple[int, float, float, float]] = []
    for thr in thresholds:
        lp, wall, gf = fitness_kvsel_detail(
            early,
            thr,
            teacher=teacher,
            student=student,
            prompts=prompts,
            seed=seed,
        )
        row = (thr, lp, wall, gf)
        all_rows.append(row)
        if lp >= tip_lp - eps_lp:
            ok.append(row)
    winners = [r for r in ok if r[2] < float(tip_wall)]
    if winners:
        return min(winners, key=lambda r: r[2])
    pool = ok if ok else all_rows
    return min(pool, key=lambda r: r[2])
