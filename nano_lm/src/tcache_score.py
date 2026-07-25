"""Score PFB banks with teacher LP memo + eligible-only code forwards."""

from __future__ import annotations

import time
from typing import Any

from lat_ops import EPS_LP
from load_model import LoadedModel
from pfb_ops import eligible_indices, pick_pfb_beam
from tcache_ops import TeacherLpMemo
from tchr_ops import STORY_TEACHER_ID, code_teacher_meta
from tchr_score import code_teacher_mean_logprob

__all__ = [
    "score_story_conts",
    "rescore_bank_stories",
    "commit_pfb_rows_tcache",
    "commit_pfb_rows_naive",
]


def score_story_conts(
    story_teacher: LoadedModel,
    prompt: str,
    conts: list[str],
    memo: TeacherLpMemo | None = None,
) -> list[float]:
    """Score story LPs; memoize by completion id when memo is set."""
    out: list[float] = []
    for c in conts:
        if memo is None:
            out.append(float(code_teacher_mean_logprob(story_teacher, prompt, c)))
            continue
        out.append(
            memo.get_or_compute(
                "story",
                prompt,
                c,
                lambda c=c: code_teacher_mean_logprob(story_teacher, prompt, c),
            )
        )
    return out


def rescore_bank_stories(
    story_teacher: LoadedModel,
    banks: list[dict[str, Any]],
    memo: TeacherLpMemo | None,
) -> tuple[list[dict[str, Any]], float]:
    """Re-score story_lps on banks; return new banks + wall_ms."""
    t0 = time.perf_counter()
    out: list[dict[str, Any]] = []
    for bank in banks:
        stories = score_story_conts(
            story_teacher, str(bank["prompt"]), list(bank["conts"]), memo
        )
        out.append({**bank, "story_lps": stories})
    return out, (time.perf_counter() - t0) * 1000.0


def commit_pfb_rows_naive(
    code_teacher: LoadedModel,
    banks: list[dict[str, Any]],
    parent_code_by_key: dict[tuple[str, int], float] | None = None,
    *,
    family: str = "H-TCACHE-naive",
) -> tuple[list[dict[str, Any]], TeacherLpMemo, float]:
    """Score code for every beam; return rows, memo, wall_ms."""
    memo = TeacherLpMemo()
    t0 = time.perf_counter()
    rows = _commit(
        code_teacher,
        banks,
        parent_code_by_key,
        family=family,
        memo=memo,
        eligible_only=False,
    )
    return rows, memo, (time.perf_counter() - t0) * 1000.0


def commit_pfb_rows_tcache(
    code_teacher: LoadedModel,
    banks: list[dict[str, Any]],
    parent_code_by_key: dict[tuple[str, int], float] | None = None,
    *,
    family: str = "H-TCACHE",
    story_memo: TeacherLpMemo | None = None,
) -> tuple[list[dict[str, Any]], TeacherLpMemo, float]:
    """PFB commit with memo + code forwards only for story-eligible beams."""
    memo = story_memo if story_memo is not None else TeacherLpMemo()
    t0 = time.perf_counter()
    rows = _commit(
        code_teacher,
        banks,
        parent_code_by_key,
        family=family,
        memo=memo,
        eligible_only=True,
    )
    return rows, memo, (time.perf_counter() - t0) * 1000.0


def _commit(
    code_teacher: LoadedModel,
    banks: list[dict[str, Any]],
    parent_code_by_key: dict[tuple[str, int], float] | None,
    *,
    family: str,
    memo: TeacherLpMemo,
    eligible_only: bool,
) -> list[dict[str, Any]]:
    meta = code_teacher_meta()
    rows: list[dict[str, Any]] = []
    for bank in banks:
        conts: list[str] = list(bank["conts"])
        stories: list[float] = [float(x) for x in bank["story_lps"]]
        floor = float(bank["parent_story"]) - float(EPS_LP)
        elig = eligible_indices(stories, floor)
        idxs = elig if eligible_only else list(range(len(conts)))
        codes = _score_codes(code_teacher, str(bank["prompt"]), conts, memo, idxs)
        pick, n_elig = pick_pfb_beam(stories, codes, floor=floor)
        rows.append(
            _row_from_pick(
                bank,
                conts,
                stories,
                codes,
                pick=pick,
                n_elig=n_elig,
                floor=floor,
                family=family,
                meta=meta,
                parent_code_by_key=parent_code_by_key,
                code_teacher=code_teacher,
                memo=memo,
            )
        )
    return rows


def _score_codes(
    code_teacher: LoadedModel,
    prompt: str,
    conts: list[str],
    memo: TeacherLpMemo,
    indices: list[int],
) -> list[float]:
    codes = [float("-inf")] * len(conts)
    for i in indices:
        c = conts[i]
        codes[i] = memo.get_or_compute(
            "code",
            prompt,
            c,
            lambda c=c: code_teacher_mean_logprob(code_teacher, prompt, c),
        )
    return codes


def _row_from_pick(
    bank: dict[str, Any],
    conts: list[str],
    stories: list[float],
    codes: list[float],
    *,
    pick: int | None,
    n_elig: int,
    floor: float,
    family: str,
    meta: dict[str, Any],
    parent_code_by_key: dict[tuple[str, int], float] | None,
    code_teacher: LoadedModel,
    memo: TeacherLpMemo,
) -> dict[str, Any]:
    if pick is None:
        cont = str(bank["parent_cont"])
        story_lp = float(bank["parent_story"])
        key = (str(bank["prompt"]), int(bank["seed"]))
        if parent_code_by_key and key in parent_code_by_key:
            code_lp = float(parent_code_by_key[key])
        else:
            code_lp = memo.get_or_compute(
                "code",
                str(bank["prompt"]),
                cont,
                lambda: code_teacher_mean_logprob(
                    code_teacher, str(bank["prompt"]), cont
                ),
            )
        n_new = int(bank["parent_n_new"])
        switched, pick_f = 0.0, -1.0
    else:
        cont = conts[pick]
        story_lp = float(stories[pick])
        code_lp = float(codes[pick])
        n_new = int(bank["n_news"][pick])
        switched, pick_f = 1.0, float(pick)
    return {
        "family": family,
        "prompt": bank["prompt"],
        "continuation": cont,
        "story_teacher_id": STORY_TEACHER_ID,
        "story_teacher_lp": story_lp,
        "wall_ms": float(bank["wall_ms"]),
        "n_new": n_new,
        "seed": int(bank["seed"]),
        "unique": float(bank["unique"]),
        "k": float(bank["k"]),
        "pick": pick_f,
        "n_elig": float(n_elig),
        "switched": switched,
        "floor": float(floor),
        "code_teacher_id": meta["hf_id"],
        "code_teacher_lp": code_lp,
        "code_teacher_params": meta["params"],
        "code_teacher_license": meta["license"],
    }
