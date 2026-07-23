"""Smoke H-BAND (UCB1) vs H-CASC / H-DECK at matched teacher pulls."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from hyp_band import run_h_band
from hyp_casc import run_h_casc
from hyp_deck import run_h_deck
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json

# Match H-CASC smoke: gens=2, mid_k=2, final_k=1 → 6 teacher gene scores.
N_ARMS = 4
N_PULLS = 6
MID_K = 2
FINAL_K = 1
DECK_TOP_K = 1


def _row(family: str, seed: int, meta: dict[str, Any], n_prompts: int) -> dict:
    return {
        "family": family,
        "label": f"{family.replace('-', '')}_seed{seed}",
        "teacher_mean_logprob": float(meta["eval_fit"]),
        "search_fit": float(meta["best_fit"]),
        "mean_wall_ms": None,
        "n_prompts": n_prompts,
        "seed": seed,
        "best_gene": meta["best_gene"],
        "teacher_forwards": int(meta["teacher_forwards"]),
        "wall_save": bool(meta.get("wall_save", False)),
    }


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    max_new = min(16, int(c["max_new_eval"]))
    for seed in c["seeds"]:
        ckpt = out / f"B2_seed{seed}.pt"
        if not ckpt.is_file():
            raise FileNotFoundError(f"missing B2 checkpoint: {ckpt}")
        common = dict(
            student_ckpt=ckpt,
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            prompts_path=c["prompts"],
            cache_dir=c["cache"],
            max_new=max_new,
            eval_max_new=int(c["max_new_eval"]),
        )
        casc = run_h_casc(
            **common,
            pop_size=N_ARMS,
            generations=2,
            seed=seed,
            mid_k=MID_K,
            final_k=FINAL_K,
            out_meta=out / f"HCASC_band_seed{seed}_train.json",
        )
        rows.append(_row("H-CASC", seed, casc, 2))
        deck = run_h_deck(
            **common,
            pop_size=N_ARMS,
            generations=2,
            seed=seed + 10,
            top_k=DECK_TOP_K,
            out_meta=out / f"HDECK_band_seed{seed}_train.json",
        )
        rows.append(_row("H-DECK", seed, deck, 2))
        band = run_h_band(
            **common,
            n_arms=N_ARMS,
            n_pulls=N_PULLS,
            seed=seed + 20,
            out_meta=out / f"HBAND_seed{seed}_train.json",
        )
        rows.append(_row("H-BAND", seed, band, 2))
        write_json(out / f"HBAND_seed{seed}_eval.json", rows[-1])
    wall_s = time.perf_counter() - t0
    write_json(out / "band_smoke.json", {"rows": rows, "wall_s": wall_s})
    print(json.dumps({"n_rows": len(rows), "out": str(out / "band_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
