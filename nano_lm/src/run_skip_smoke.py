"""Smoke H-SKIP: BAT→CHBAT skip CBAT vs flat BAT (+ CBAT context)."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import yaml

from chunk_fit import long_prompts
from chunk_ops import LONG_TARGET_TOKENS
from data_tiny import load_tokenizer
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json
from skip_ops import SKIP_CHUNK
from skip_pair import run_seed_trio


def _load_texts(*paths: Path) -> list[str]:
    texts: list[str] = []
    for path in paths:
        with path.open(encoding="utf-8") as f:
            texts.extend(p["text"] for p in yaml.safe_load(f)["prompts"])
    return texts


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("ERROR: H-SKIP requires CUDA", file=sys.stderr)
        return 2
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    c["gene_dir"] = out
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    raw = _load_texts(c["prompts"], c["fit_prompts"])
    prompts = long_prompts(raw, tok, target_tokens=LONG_TARGET_TOKENS)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        trio = run_seed_trio(c, seed, prompts)
        for row in trio:
            if row["family"] == "H-SKIP":
                write_json(out / f"HSKIP_seed{seed}_eval.json", row)
        rows.extend(trio)
    write_json(
        out / "skip_smoke.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "n_prompts": len(prompts),
            "chunk_size": SKIP_CHUNK,
            "target_tokens": LONG_TARGET_TOKENS,
            "mode": "BAT→CHBAT skip CBAT vs BAT (+ CBAT context)",
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "skip_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
