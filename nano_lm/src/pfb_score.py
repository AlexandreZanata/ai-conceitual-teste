"""Score H-ABS-PFB: story-floor then code BoN; empty → parent (VRAM-safe)."""

from __future__ import annotations

from typing import Any

from decode_early import decode_early
from decode_pfb import decode_early_beams
from early_ops import EarlyGene, clamp_early_gene
from lat_ops import EPS_LP
from load_model import LoadedModel
from pfb_ops import K_BEAMS, PFB_TEMP, pick_pfb_beam, unique_texts
from tchr_ops import STORY_TEACHER_ID, code_teacher_meta
from tchr_score import code_teacher_mean_logprob, dual_means

__all__ = [
    "collect_pfb_banks",
    "commit_pfb_rows",
    "attach_code_teacher",
    "arm_means",
]


def _gene_base(gene: EarlyGene) -> EarlyGene:
    g = clamp_early_gene(gene)
    g["top_p"] = float(gene.get("top_p", g["top_p"]))
    return g


def collect_pfb_banks(
    *,
    story_teacher: LoadedModel,
    student: object,
    prompts: list[str],
    gene: EarlyGene,
    max_new: int,
    seed: int,
    k: int = K_BEAMS,
    temperature: float = PFB_TEMP,
    parent_family: str = "H-EARLY",
    weight_bytes: int | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Decode parent n=1 + K beams; score story per beam (no code yet)."""
    g = _gene_base(gene)
    tok = story_teacher.tokenizer
    device = story_teacher.device
    parent_rows: list[dict[str, Any]] = []
    banks: list[dict[str, Any]] = []
    for i, text in enumerate(prompts):
        parent = decode_early(
            student,
            tok,
            text,
            n=1,
            max_new_tokens=max_new,
            min_new=int(g["min_new"]),
            conf_threshold=float(g["conf_threshold"]),
            patience=int(g["patience"]),
            temperature=1e-6,
            top_p=float(g["top_p"]),
            seed=seed + i,
            device=device,
        )
        p_story = code_teacher_mean_logprob(
            story_teacher, text, parent.text
        )
        row: dict[str, Any] = {
            "family": parent_family,
            "prompt": text,
            "continuation": parent.text,
            "story_teacher_id": STORY_TEACHER_ID,
            "story_teacher_lp": float(p_story),
            "wall_ms": float(parent.wall_ms),
            "n_new": len(parent.token_ids),
            "seed": int(seed),
            "unique": 1.0,
            "k": 1.0,
            "pick": 0.0,
            "n_elig": 1.0,
            "switched": 0.0,
        }
        if weight_bytes is not None:
            row["weight_bytes"] = int(weight_bytes)
        parent_rows.append(row)
        beams = decode_early_beams(
            student,
            tok,
            text,
            n=int(k),
            max_new_tokens=max_new,
            min_new=int(g["min_new"]),
            conf_threshold=float(g["conf_threshold"]),
            patience=int(g["patience"]),
            temperature=float(temperature),
            top_p=float(g["top_p"]),
            seed=seed + 1000 + i,
            device=device,
        )
        conts = [b.text for b in beams]
        stories = [
            float(code_teacher_mean_logprob(story_teacher, text, c))
            for c in conts
        ]
        banks.append(
            {
                "prompt": text,
                "seed": int(seed),
                "parent_story": float(p_story),
                "parent_cont": parent.text,
                "parent_n_new": len(parent.token_ids),
                "parent_wall_ms": float(parent.wall_ms),
                "conts": conts,
                "story_lps": stories,
                "wall_ms": float(beams[0].wall_ms) if beams else 0.0,
                "n_news": [len(b.token_ids) for b in beams],
                "unique": float(unique_texts(conts)),
                "k": float(k),
            }
        )
    return parent_rows, banks


def commit_pfb_rows(
    code_teacher: LoadedModel,
    banks: list[dict[str, Any]],
    parent_code_by_key: dict[tuple[str, int], float] | None = None,
    *,
    family: str = "H-ABS-PFB",
    weight_bytes: int | None = None,
) -> list[dict[str, Any]]:
    """Score code on beams; story-floor commit or parent fallback."""
    meta = code_teacher_meta()
    rows: list[dict[str, Any]] = []
    for bank in banks:
        conts: list[str] = list(bank["conts"])
        stories: list[float] = [float(x) for x in bank["story_lps"]]
        codes = [
            float(
                code_teacher_mean_logprob(
                    code_teacher, str(bank["prompt"]), c
                )
            )
            for c in conts
        ]
        floor = float(bank["parent_story"]) - float(EPS_LP)
        pick, n_elig = pick_pfb_beam(stories, codes, floor=floor)
        if pick is None:
            cont = str(bank["parent_cont"])
            story_lp = float(bank["parent_story"])
            key = (str(bank["prompt"]), int(bank["seed"]))
            if parent_code_by_key and key in parent_code_by_key:
                code_lp = float(parent_code_by_key[key])
            else:
                code_lp = float(
                    code_teacher_mean_logprob(
                        code_teacher, str(bank["prompt"]), cont
                    )
                )
            n_new = int(bank["parent_n_new"])
            wall = float(bank["wall_ms"])
            switched = 0.0
            pick_f = -1.0
        else:
            cont = conts[pick]
            story_lp = float(stories[pick])
            code_lp = float(codes[pick])
            n_new = int(bank["n_news"][pick])
            wall = float(bank["wall_ms"])
            switched = 1.0
            pick_f = float(pick)
        row: dict[str, Any] = {
            "family": family,
            "prompt": bank["prompt"],
            "continuation": cont,
            "story_teacher_id": STORY_TEACHER_ID,
            "story_teacher_lp": story_lp,
            "wall_ms": wall,
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
        if weight_bytes is not None:
            row["weight_bytes"] = int(weight_bytes)
        rows.append(row)
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
        n = len(rows)
        means["mean_unique"] = sum(float(r["unique"]) for r in rows) / n
        means["mean_elig"] = sum(float(r.get("n_elig", 0)) for r in rows) / n
        means["mean_switch"] = sum(float(r.get("switched", 0)) for r in rows) / n
        means["k"] = float(rows[0]["k"])
        if "weight_bytes" in rows[0]:
            means["weight_bytes"] = float(rows[0]["weight_bytes"])
    else:
        means["mean_unique"] = float("nan")
        means["mean_elig"] = float("nan")
        means["mean_switch"] = float("nan")
        means["k"] = float("nan")
    return means
