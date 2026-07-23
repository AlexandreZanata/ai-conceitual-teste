"""Bench runner: load config, run AR / BoN / MAE on fixed prompts, write JSONL."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

from decode_ar import decode_ar
from decode_bon import decode_bon
from decode_mae import decode_mae
from load_model import load_causal_lm
from scorers import DecodeResult, distinct_n

ROOT = Path(__file__).resolve().parents[1]


def load_config(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_prompts(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return list(data["prompts"])


def run_method(
    name: str,
    loaded: Any,
    prompt: str,
    cfg: dict[str, Any],
    seed: int,
) -> DecodeResult:
    common = dict(
        model=loaded.model,
        tokenizer=loaded.tokenizer,
        prompt=prompt,
        max_new_tokens=cfg["max_new_tokens"],
        temperature=cfg["temperature"],
        top_p=cfg["top_p"],
        seed=seed,
        device=loaded.device,
    )
    if name == "ar":
        return decode_ar(**common)
    if name == "bon":
        return decode_bon(n=cfg["bon_n"], **common)
    if name == "mae":
        return decode_mae(
            k=cfg["mae_k"],
            block=cfg["mae_block"],
            horizon=cfg["mae_horizon"],
            **common,
        )
    raise ValueError(f"unknown method: {name}")


def record_row(
    method: str,
    prompt: dict[str, str],
    seed: int,
    result: DecodeResult,
) -> dict[str, Any]:
    return {
        "method": method,
        "prompt_id": prompt["id"],
        "seed": seed,
        "mean_logprob": result.mean_logprob,
        "distinct_1": distinct_n(result.token_ids, 1),
        "distinct_2": distinct_n(result.token_ids, 2),
        "wall_ms": result.wall_ms,
        "token_evals": result.token_evals,
        "n_tokens": len(result.token_ids),
        "text": result.text,
    }


def resolve_config(arg: str | None) -> Path:
    if not arg:
        return ROOT / "configs/smoke.json"
    path = Path(arg)
    if path.is_file():
        return path.resolve()
    candidate = ROOT / arg
    if candidate.is_file():
        return candidate.resolve()
    raise FileNotFoundError(arg)


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    cfg_path = resolve_config(args[0] if args else None)
    cfg = load_config(cfg_path)
    prompts = load_prompts(ROOT / cfg["prompts_path"])
    cache = ROOT / ".cache"
    cache.mkdir(parents=True, exist_ok=True)
    loaded = load_causal_lm(
        cfg["model_id"], cfg["tokenizer_id"], cache_dir=cache
    )
    out_dir = Path(cfg["out_dir"])
    if not out_dir.is_absolute():
        out_dir = ROOT.parent / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "runs.jsonl"
    rows: list[dict[str, Any]] = []
    with out_file.open("w", encoding="utf-8") as f:
        for method in cfg["methods"]:
            for prompt in prompts:
                for seed in cfg["seeds"]:
                    result = run_method(method, loaded, prompt["text"], cfg, seed)
                    row = record_row(method, prompt, seed, result)
                    rows.append(row)
                    f.write(json.dumps(row) + "\n")
                    f.flush()
    meta = {
        "config": str(cfg_path),
        "model_id": cfg["model_id"],
        "n_rows": len(rows),
        "out_file": str(out_file),
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
