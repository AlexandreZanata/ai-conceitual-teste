"""Smoke H-DECK2: sweep top_k∈{1,2,3} on B2 ckpts (equal pop×gens)."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from deck2_ops import DECK2_TOP_KS
from hyp_deck import run_h_deck
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        ckpt = out / f"B2_seed{seed}.pt"
        if not ckpt.is_file():
            raise FileNotFoundError(f"missing B2 checkpoint: {ckpt}")
        for top_k in DECK2_TOP_KS:
            meta = run_h_deck(
                student_ckpt=ckpt,
                teacher_id=c["teacher_id"],
                tokenizer_id=c["tokenizer_id"],
                prompts_path=c["prompts"],
                cache_dir=c["cache"],
                pop_size=4,
                generations=2,
                max_new=min(16, int(c["max_new_eval"])),
                eval_max_new=int(c["max_new_eval"]),
                seed=seed + 100 * top_k,
                top_k=top_k,
                out_meta=out / f"HDECK2_k{top_k}_seed{seed}_train.json",
            )
            row = {
                "family": "H-DECK2",
                "label": f"HDECK2_k{top_k}_seed{seed}",
                "top_k": top_k,
                "teacher_mean_logprob": float(meta["eval_fit"]),
                "search_fit": float(meta["best_fit"]),
                "mean_wall_ms": None,
                "n_prompts": 2,
                "seed": seed,
                "best_gene": meta["best_gene"],
                "teacher_forwards": int(meta["teacher_forwards"]),
                "wall_save": bool(meta["wall_save"]),
            }
            write_json(out / f"HDECK2_k{top_k}_seed{seed}_eval.json", row)
            rows.append(row)
    wall_s = time.perf_counter() - t0
    write_json(out / "deck2_smoke.json", {"rows": rows, "wall_s": wall_s})
    print(json.dumps({"n_rows": len(rows), "out": str(out / "deck2_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
