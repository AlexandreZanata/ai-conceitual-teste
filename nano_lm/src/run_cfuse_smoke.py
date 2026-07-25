"""Smoke H-CFUSE: CHUNK ⊕ FUSE vs EARLY/CHUNK/FUSE (protocol, not tip)."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from cfuse_fit import (
    DEFAULT_CHUNK,
    fitness_cfuse_detail,
    fitness_chunk_dual,
    fitness_early_dual,
    fitness_fuse_detail,
    tip_row,
)
from chunk_fit import long_prompts
from chunk_ops import LONG_TARGET_TOKENS
from eval_decode import load_pair
from flop_score import load_prompts
from kvsel_fit import warmup_kvsel
from kvsel_ops import SMOKE_BUDGETS
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json


def _early_gene(out: Path, seed: int) -> dict[str, Any]:
    path = out / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing EARLY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return gene


def _kv_threshold(out: Path, seed: int) -> int:
    path = out / f"HKVSEL_seed{seed}_eval.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing KVSEL util: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene") or {}
    if "kv_threshold" not in gene:
        raise ValueError(f"KVSEL missing kv_threshold: {path}")
    return int(gene["kv_threshold"])


def _run_seed(
    c: dict[str, Any],
    out: Path,
    seed: int,
    prompts: list[str],
) -> list[dict[str, Any]]:
    early = _early_gene(out, seed)
    thr = _kv_threshold(out, seed)
    teacher, student = load_pair(
        out / f"B2_seed{seed}.pt",
        c["teacher_id"],
        c["tokenizer_id"],
        c["cache"],
    )
    claim = seed + 8080
    warmup_kvsel(early, teacher=teacher, student=student, prompts=prompts)
    kw = dict(teacher=teacher, student=student, prompts=prompts, seed=claim)
    lp_e, wall_e, gf_e = fitness_early_dual(early, **kw)
    lp_c, wall_c, gf_c = fitness_chunk_dual(early, chunk_size=DEFAULT_CHUNK, **kw)
    lp_f, wall_f, gf_f = fitness_fuse_detail(early, thr, **kw)
    lp_u, wall_u, gf_u = fitness_cfuse_detail(
        early, thr, chunk_size=DEFAULT_CHUNK, **kw
    )
    gene = {
        **early,
        "kv_threshold": thr,
        "chunk_size": DEFAULT_CHUNK,
        "backend": "sdpa+chunk+kvsel",
    }
    rows = [
        tip_row("H-EARLY", f"HEARLY_cfuse_seed{seed}", lp_e, wall_e, gf_e, seed, early),
        tip_row(
            "H-CHUNK",
            f"HCHUNK_cfuse_seed{seed}",
            lp_c,
            wall_c,
            gf_c,
            seed,
            {**early, "chunk_size": DEFAULT_CHUNK},
        ),
        tip_row(
            "H-FUSE",
            f"HFUSE_cfuse_seed{seed}",
            lp_f,
            wall_f,
            gf_f,
            seed,
            {**early, "kv_threshold": thr},
        ),
        tip_row("H-CFUSE", f"HCFUSE_seed{seed}", lp_u, wall_u, gf_u, seed, gene),
    ]
    for r in rows:
        r["budgets"] = list(SMOKE_BUDGETS)
        r["target_tokens"] = LONG_TARGET_TOKENS
        r["chunk_size"] = DEFAULT_CHUNK
    write_json(out / f"HCFUSE_seed{seed}_eval.json", rows[-1])
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
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        rows.extend(_run_seed(c, out, seed, prompts))
    write_json(
        out / "cfuse_smoke.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "budgets": list(SMOKE_BUDGETS),
            "chunk_size": DEFAULT_CHUNK,
            "target_tokens": LONG_TARGET_TOKENS,
            "note": "protocol stack; not a tip H-ID",
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "cfuse_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
