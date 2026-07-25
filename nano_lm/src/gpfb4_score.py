"""Score H-ABS-GPFB4: GENC prompt/exit/quant + PFB K-beam banks."""

from __future__ import annotations

from typing import Any

from decode_early import decode_early
from decode_pfb import decode_early_beams
from early_ops import EarlyGene
from genc_ops import GencGene, clamp_genc_gene
from genc_prompt import apply_genc_prompt
from genc_score import early_from_exit, prepare_student
from load_model import LoadedModel
from pfb_ops import K_BEAMS, PFB_TEMP, unique_texts
from tchr_ops import STORY_TEACHER_ID
from tchr_score import code_teacher_mean_logprob

__all__ = ["collect_gpfb4_banks"]


def collect_gpfb4_banks(
    *,
    story_teacher: LoadedModel,
    student: object,
    prompts: list[str],
    genc_gene: GencGene,
    early: EarlyGene,
    chunks: list[str],
    max_new: int,
    seed: int,
    k: int = K_BEAMS,
    temperature: float = PFB_TEMP,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    """
    GIVEN GENC genome + prompts
    WHEN decoding parent n=1 + K beams on GENC ctx (serial)
    THEN story-score on bare task; return parent rows, banks, weight_bytes.
    """
    gg = clamp_genc_gene(genc_gene)
    eg = early_from_exit(early, int(gg["exit_depth"]))
    model, nbytes = prepare_student(student, int(gg["quant_bits"]))
    if hasattr(model, "to"):
        model.to(story_teacher.device)
    tok = story_teacher.tokenizer
    device = story_teacher.device
    parent_rows: list[dict[str, Any]] = []
    banks: list[dict[str, Any]] = []
    for i, task in enumerate(prompts):
        ctx = apply_genc_prompt(
            task,
            k_retrieve=int(gg["k_retrieve"]),
            chunks=chunks,
            stride=int(gg["stride"]),
            chunk_len=int(gg["chunk_len"]),
        )
        parent = decode_early(
            model,
            tok,
            ctx,
            n=1,
            max_new_tokens=max_new,
            min_new=int(eg["min_new"]),
            conf_threshold=float(eg["conf_threshold"]),
            patience=int(eg["patience"]),
            temperature=1e-6,
            top_p=float(eg["top_p"]),
            seed=seed + i,
            device=device,
        )
        p_story = float(
            code_teacher_mean_logprob(story_teacher, task, parent.text)
        )
        parent_rows.append(
            {
                "family": "H-GENC-serial",
                "prompt": task,
                "continuation": parent.text,
                "story_teacher_id": STORY_TEACHER_ID,
                "story_teacher_lp": p_story,
                "wall_ms": float(parent.wall_ms),
                "n_new": len(parent.token_ids),
                "seed": int(seed),
                "unique": 1.0,
                "k": 1.0,
                "pick": 0.0,
                "n_elig": 1.0,
                "switched": 0.0,
                "weight_bytes": int(nbytes),
                "gene": dict(gg),
            }
        )
        beams = decode_early_beams(
            model,
            tok,
            ctx,
            n=int(k),
            max_new_tokens=max_new,
            min_new=int(eg["min_new"]),
            conf_threshold=float(eg["conf_threshold"]),
            patience=int(eg["patience"]),
            temperature=float(temperature),
            top_p=float(eg["top_p"]),
            seed=seed + 1000 + i,
            device=device,
        )
        conts = [b.text for b in beams]
        stories = [
            float(code_teacher_mean_logprob(story_teacher, task, c))
            for c in conts
        ]
        banks.append(
            {
                "prompt": task,
                "seed": int(seed),
                "parent_story": p_story,
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
    return parent_rows, banks, int(nbytes)
