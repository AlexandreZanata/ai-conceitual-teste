"""Smoke H-SROUTE: ROUTE stack vs frozen H-SERVE recipe."""

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
from sroute_ops import SROUTE_CHUNK
from sroute_pair import SMOKE_BUDGETS, run_seed_pair


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
        print("ERROR: H-SROUTE requires CUDA", file=sys.stderr)
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
        pair = run_seed_pair(c, seed, prompts)
        for row in pair:
            if row["family"] == "H-SROUTE":
                write_json(out / f"HSROUTE_seed{seed}_eval.json", row)
        rows.extend(pair)
    write_json(
        out / "sroute_smoke.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "n_prompts": len(prompts),
            "chunk_size": SROUTE_CHUNK,
            "budgets": list(SMOKE_BUDGETS),
            "target_tokens": LONG_TARGET_TOKENS,
            "mode": "ROUTE vs frozen SERVE recipe",
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "sroute_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
