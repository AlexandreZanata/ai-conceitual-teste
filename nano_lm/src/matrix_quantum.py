"""Matrix wave 3: H-SUP / H-INT vs uniform BoN ablation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from decode_quantum import run_quantum_ablation
from load_model import load_causal_lm
from matrix_common import write_json


def run_quantum(c: dict[str, Any], rows: list) -> None:
    out: Path = c["out"]
    loaded = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    qrows = []
    prompts = [
        "Once upon a time there was a little girl named Lily. She loved",
        "One day, a boy found a magic key under a big oak tree. He",
    ]
    for seed in c["seeds"]:
        for prompt in prompts:
            q = run_quantum_ablation(
                loaded,
                prompt,
                k=8,
                max_new=16,
                temperature=0.8,
                top_p=0.9,
                seed=seed,
            )
            q["seed"] = seed
            qrows.append(q)
    write_json(out / "quantum_ablation.json", qrows)
    for name, key in [
        ("H-SUP", "sup_score"),
        ("H-INT", "int_score"),
        ("BoN-uniform", "bon_score"),
    ]:
        vals = [float(r[key]) for r in qrows]
        rows.append(
            {
                "family": name,
                "teacher_mean_logprob": sum(vals) / len(vals),
                "mean_wall_ms": None,
                "n_prompts": len(qrows),
                "seed": -1,
                "label": name,
            }
        )
