"""Shared H-MIXD seed: story-only vs mix train + dual eval."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from data_tiny import load_tokenizer
from load_model import load_causal_lm
from matrix_common import eval_ckpt, write_json
from mixd_data import plan_mix_batches, plan_story_batches
from mixd_ops import MIX_FRAC
from mixd_score import student_mean_ppl
from prog_packs import PROG_PROMPTS
from top_train import train_live_batches
from xfer_packs import load_yaml_texts

__all__ = ["run_seed_pair", "means_from_rows"]


def means_from_rows(rows: list[dict[str, Any]]) -> dict[str, float]:
    """Aggregate story_lp / prog_ppl means for CTRL and MIXD families."""
    out: dict[str, float] = {}
    for fam, key in (
        ("H-STAG-CTRL", "story_lp"),
        ("H-MIXD", "story_lp"),
        ("H-STAG-CTRL", "prog_ppl"),
        ("H-MIXD", "prog_ppl"),
    ):
        vals = [float(r[key]) for r in rows if r.get("family") == fam]
        out[f"{fam}:{key}"] = sum(vals) / max(len(vals), 1)
    return out


def run_seed_pair(
    c: dict[str, Any],
    out: Path,
    seed: int,
    device: torch.device,
    steps: int,
) -> list[dict[str, Any]]:
    """
    GIVEN matrix cfg + seed
    WHEN training story-only vs mix and scoring story LP + prog PPL
    THEN return two family rows.
    """
    story = plan_story_batches(
        tokenizer_id=c["tokenizer_id"],
        cache_dir=c["cache"],
        steps=steps,
        batch_size=c["batch_size"],
        seq_len=c["seq_len"],
        max_examples=c["max_examples"],
        seed=seed + 101,
    )
    mix = plan_mix_batches(
        story,
        tokenizer_id=c["tokenizer_id"],
        cache_dir=c["cache"],
        seq_len=c["seq_len"],
        batch_size=c["batch_size"],
        seed=seed + 101,
        mix_frac=MIX_FRAC,
    )
    teacher = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    ctrl = train_live_batches(
        teacher=teacher,
        batches=story,
        device=device,
        lr=c["lr"],
        seed=seed + 101,
        temperature=2.0,
        alpha=0.5,
        out_path=out / f"HMIXD_ctrl_seed{seed}.pt",
    )
    mix_tr = train_live_batches(
        teacher=teacher,
        batches=mix,
        device=device,
        lr=c["lr"],
        seed=seed + 201,
        temperature=2.0,
        alpha=0.5,
        out_path=out / f"HMIXD_mix_seed{seed}.pt",
    )
    write_json(out / f"HMIXD_ctrl_seed{seed}_train.json", ctrl)
    write_json(out / f"HMIXD_mix_seed{seed}_train.json", mix_tr)
    del teacher
    if device.type == "cuda":
        torch.cuda.empty_cache()
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    prog_texts = load_yaml_texts(PROG_PROMPTS)
    rows: list[dict[str, Any]] = []
    for fam, tr in (("H-STAG-CTRL", ctrl), ("H-MIXD", mix_tr)):
        ckpt = Path(tr["out_path"])
        ev = eval_ckpt(c, ckpt, seed, fam)
        ppl = student_mean_ppl(
            ckpt, tok, prog_texts, device=device, seq_len=int(c["seq_len"])
        )
        rows.append(
            {
                "family": fam,
                "seed": seed,
                "story_lp": float(ev["teacher_mean_logprob"]),
                "prog_ppl": float(ppl),
                "ms_per_step": float(tr["ms_per_step"]),
                "out_path": str(ckpt),
            }
        )
        if device.type == "cuda":
            torch.cuda.empty_cache()
    return rows
