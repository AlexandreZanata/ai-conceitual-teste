"""Matrix wave: B3 (AR), B4 (BoN), H-SPEC on B2 checkpoints."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from eval_decode import eval_decode_ops_for_ckpt
from matrix_common import write_json


def run_decode_ops(c: dict[str, Any], rows: list) -> None:
    out: Path = c["out"]
    draft_len = int(c.get("draft_len", 4))
    bon_n = int(c.get("bon_n_eval", 4))
    for seed in c["seeds"]:
        ckpt = out / f"B2_seed{seed}.pt"
        if not ckpt.is_file():
            raise FileNotFoundError(f"missing B2 checkpoint: {ckpt}")
        batch = eval_decode_ops_for_ckpt(
            student_ckpt=ckpt,
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            prompts_path=c["prompts"],
            cache_dir=c["cache"],
            max_new_tokens=c["max_new_eval"],
            seed=seed,
            draft_len=draft_len,
            bon_n=bon_n,
        )
        for row in batch:
            write_json(out / f"{row['family']}_seed{seed}_eval.json", row)
            rows.append(row)
