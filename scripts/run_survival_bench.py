#!/usr/bin/env python3
"""Run timed survival benches into results/survival/<bench>/<tech>/seed_<n>/."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH_DIR = ROOT / "experiments" / "survival" / "benches"
TECHNIQUES = ["R0", "A", "B", "C", "C-L", "A+"]
BENCHES = ["TB-30", "TB-60", "TB-120", "TB-DRIFT"]


def merge_run(bench: str, technique: str, seed: int) -> dict:
    cfg = json.loads((BENCH_DIR / f"{bench}.json").read_text())
    cfg["technique"] = technique
    cfg["seed"] = seed
    cfg["bench"] = bench
    return cfg


def run_one(evogen: Path, cfg: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    cfg_path = out_dir / "config.json"
    cfg_path.write_text(json.dumps(cfg, indent=2) + "\n")
    cmd = [
        str(evogen),
        "--config",
        str(cfg_path),
        "--results",
        str(out_dir),
    ]
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bench", action="append", choices=BENCHES)
    p.add_argument("--technique", action="append", choices=TECHNIQUES)
    p.add_argument("--seeds", type=int, default=2, help="R: seeds 1..R")
    p.add_argument("--results-root", type=Path, default=ROOT / "results" / "survival")
    p.add_argument("--evogen", type=Path, default=ROOT / "build" / "evogen")
    args = p.parse_args()
    benches = args.bench or ["TB-30"]
    techniques = args.technique or ["R0", "C"]
    if not args.evogen.is_file():
        print(f"error: evogen binary missing: {args.evogen}", file=sys.stderr)
        return 1
    for bench in benches:
        for tech in techniques:
            for seed in range(1, args.seeds + 1):
                out = args.results_root / bench / tech / f"seed_{seed}"
                cfg = merge_run(bench, tech, seed)
                run_one(args.evogen, cfg, out)
                meta = out / "meta.json"
                metrics = out / "metrics.jsonl"
                if not meta.is_file() or not metrics.is_file():
                    print(f"error: missing artifacts under {out}", file=sys.stderr)
                    return 1
                m = json.loads(meta.read_text())
                for key in ("technique", "seed", "max_wall_ms", "max_generations"):
                    if key not in m:
                        print(f"error: meta missing {key} in {meta}", file=sys.stderr)
                        return 1
                if "fitness_threshold" not in m:
                    print(f"error: meta missing fitness_threshold in {meta}", file=sys.stderr)
                    return 1
    print("ok: bench dry-run complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
