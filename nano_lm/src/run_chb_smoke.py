"""Smoke H-CHB: sweep chunk_size B∈{32,64,128,256} vs H-CHUNK tip."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from chb_ops import DEFAULT_CHUNK, SMOKE_SIZES, pick_chb_size
from chunk_fit import (
    LONG_TARGET_TOKENS,
    fitness_chunk_detail,
    long_prompts,
    tip_row,
)
from eval_decode import load_pair
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
    claim = seed + 9292
    kw = dict(
        teacher=teacher, student=student, prompts=prompts, max_new=max_new, seed=claim
    )
    lp_e, wall_e, gf_e = fitness_early_detail(early, **kw)
    scored: dict[int, dict[str, float]] = {}
    rows: list[dict[str, Any]] = [
        tip_row("H-EARLY", f"HEARLY_chb_seed{seed}", lp_e, wall_e, gf_e, seed, early)
    ]
    for b in SMOKE_SIZES:
        lp, wall, gf = fitness_chunk_detail(early, chunk_size=b, **kw)
        scored[b] = {"mean_lp": lp, "mean_wall": wall, "mean_gflops": gf}
        gene = {**early, "chunk_size": b, "backend": "sdpa+chunk"}
        fam = "H-CHUNK" if b == DEFAULT_CHUNK else f"H-CHB-B{b}"
        label = (
            f"HCHUNK_chb_seed{seed}"
            if b == DEFAULT_CHUNK
            else f"HCHB_B{b}_seed{seed}"
        )
        rows.append(tip_row(fam, label, lp, wall, gf, seed, gene))
    best_b = pick_chb_size(scored, early_lp=lp_e)
    m = scored[best_b]
    gene = {**early, "chunk_size": best_b, "backend": "sdpa+chunk+sweep"}
    win = tip_row(
        "H-CHB",
        f"HCHB_seed{seed}",
        m["mean_lp"],
        m["mean_wall"],
        m["mean_gflops"],
        seed,
        gene,
    )
    rows.append(win)
    for r in rows:
        r["target_tokens"] = LONG_TARGET_TOKENS
        r["sweep"] = list(SMOKE_SIZES)
        r["chunk_size"] = int(r["best_gene"].get("chunk_size", DEFAULT_CHUNK))
    write_json(out / f"HCHB_seed{seed}_eval.json", win)
    return rows


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; SDPA may use math kernel", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    from data_tiny import load_tokenizer

    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    raw = [p["text"] for p in load_prompts(c["prompts"])]
    prompts = long_prompts(raw, tok, target_tokens=LONG_TARGET_TOKENS)
    max_new = int(c["max_new_eval"])
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        rows.extend(_run_seed(c, out, seed, prompts, max_new))
    write_json(
        out / "chb_smoke.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "sweep": list(SMOKE_SIZES),
            "tip_chunk_size": DEFAULT_CHUNK,
            "target_tokens": LONG_TARGET_TOKENS,
            "backend": "gpt_neo_sdpa + chunked KV prefill sweep",
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "chb_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
