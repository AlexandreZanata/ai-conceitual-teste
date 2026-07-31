"""Derive the N32 training budget from a measured hardware profile.

CLI:
  python bench/compute_budget.py \\
    --profile results/hw/profile.json \\
    --params 42200000 --tokens 4e9 --mfu 0.25 \\
    --out results/hw/budget.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


HOURS_CAP = 72.0
FLOPS_PER_TOKEN_PARAM = 6.0  # C ≈ 6 N D


def git_hash() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def load_profile(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sustained_tflops(profile: dict) -> float:
    block = profile["sustained_bf16_tflops"]
    value = float(block["tflops_final_minute_median"])
    if value <= 0:
        raise ValueError("sustained TFLOP/s must be recorded and non-zero")
    return value


def compute_budget(
    profile: dict,
    params: float,
    tokens: float,
    mfu: float,
) -> dict:
    peak_device = sustained_tflops(profile)
    effective_tflops = peak_device * mfu
    total_flops = FLOPS_PER_TOKEN_PARAM * params * tokens
    wall_seconds = total_flops / (effective_tflops * 1e12)
    wall_hours = wall_seconds / 3600.0
    max_tokens_72h = (HOURS_CAP * 3600.0 * effective_tflops * 1e12) / (
        FLOPS_PER_TOKEN_PARAM * params
    )
    max_params_72h = (HOURS_CAP * 3600.0 * effective_tflops * 1e12) / (
        FLOPS_PER_TOKEN_PARAM * tokens
    )
    feasible = wall_hours <= HOURS_CAP
    config = {
        "params": params,
        "tokens": tokens,
        "mfu": mfu,
        "hours_cap": HOURS_CAP,
    }
    return {
        "git_hash": git_hash(),
        "config_hash": hashlib.sha256(
            json.dumps(config, sort_keys=True).encode()
        ).hexdigest()[:16],
        "seed": int(profile.get("seed", 0)),
        "wall_seconds": float(profile.get("wall_seconds", 0.0)),
        "profile_git_hash": profile.get("git_hash"),
        "sustained_bf16_tflops": peak_device,
        "effective_tflops_at_mfu": effective_tflops,
        "mfu": mfu,
        "params": params,
        "tokens": tokens,
        "total_flops": total_flops,
        "predicted_wall_hours": wall_hours,
        "max_tokens_in_72h": max_tokens_72h,
        "max_params_at_4b_tokens_in_72h": max_params_72h,
        "feasible": feasible,
        "held_out_bpb": profile.get("held_out_bpb"),
        "embedding_params": profile.get("embedding_params"),
        "non_embedding_params": profile.get("non_embedding_params"),
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="N32 compute budget from hardware profile")
    p.add_argument("--profile", type=Path, required=True)
    p.add_argument("--params", type=float, default=42_200_000)
    p.add_argument("--tokens", type=float, default=4e9)
    p.add_argument("--mfu", type=float, default=0.25)
    p.add_argument("--out", type=Path, required=True)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    profile = load_profile(args.profile)
    budget = compute_budget(profile, args.params, args.tokens, args.mfu)
    write_json(args.out, budget)
    print(
        json.dumps(
            {
                "out": str(args.out),
                "sustained_tflops": budget["sustained_bf16_tflops"],
                "predicted_wall_hours": budget["predicted_wall_hours"],
                "max_tokens_in_72h": budget["max_tokens_in_72h"],
                "max_params_at_4b_tokens_in_72h": budget[
                    "max_params_at_4b_tokens_in_72h"
                ],
                "feasible": budget["feasible"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
