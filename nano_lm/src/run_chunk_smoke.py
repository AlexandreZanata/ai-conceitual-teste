"""Smoke H-CHUNK: chunked prefill under FLASH vs EARLY/FLASH (long prompts)."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from chunk_fit import (
    DEFAULT_CHUNK,
    LONG_TARGET_TOKENS,
    fitness_chunk_detail,
    long_prompts,
    tip_row,
)
from eval_decode import load_pair
from flash_fit import fitness_flash_detail
from flop_score import load_prompts
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json
from short_fit import fitness_early_detail


def _early_gene(out: Path, seed: int) -> dict[str, Any]:
    path = out / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing EARLY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return gene


def _run_seed(
    c: dict[str, Any],
    out: Path,
    seed: int,
    prompts: list[str],
    max_new: int,
) -> list[dict[str, Any]]:
    early = _early_gene(out, seed)
    teacher, student = load_pair(
        out / f"B2_seed{seed}.pt",
        c["teacher_id"],
        c["tokenizer_id"],
        c["cache"],
    )
    claim = seed + 9090
    gene = {**early, "chunk_size": DEFAULT_CHUNK, "backend": "sdpa+chunk"}
    lp_e, wall_e, gf_e = fitness_early_detail(
        early,
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=max_new,
        seed=claim,
    )
    lp_f, wall_f, gf_f = fitness_flash_detail(
        early,
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=max_new,
        seed=claim,
    )
    lp_c, wall_c, gf_c = fitness_chunk_detail(
        early,
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=max_new,
        seed=claim,
        chunk_size=DEFAULT_CHUNK,
    )
    rows = [
        tip_row("H-EARLY", f"HEARLY_chunk_seed{seed}", lp_e, wall_e, gf_e, seed, early),
        tip_row("H-FLASH", f"HFLASH_chunk_seed{seed}", lp_f, wall_f, gf_f, seed, early),
        tip_row("H-CHUNK", f"HCHUNK_seed{seed}", lp_c, wall_c, gf_c, seed, gene),
    ]
    for r in rows:
        r["target_tokens"] = LONG_TARGET_TOKENS
        r["chunk_size"] = DEFAULT_CHUNK
    write_json(out / f"HCHUNK_seed{seed}_eval.json", rows[-1])
    return rows


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; SDPA may use math kernel", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    raw = [p["text"] for p in load_prompts(c["prompts"])]
    # Need tokenizer before elongate — load from first seed pair lightly via HF.
    from data_tiny import load_tokenizer

    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    prompts = long_prompts(raw, tok, target_tokens=LONG_TARGET_TOKENS)
    max_new = int(c["max_new_eval"])
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        rows.extend(_run_seed(c, out, seed, prompts, max_new))
    write_json(
        out / "chunk_smoke.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "chunk_size": DEFAULT_CHUNK,
            "target_tokens": LONG_TARGET_TOKENS,
            "backend": "gpt_neo_sdpa + chunked KV prefill",
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "chunk_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
