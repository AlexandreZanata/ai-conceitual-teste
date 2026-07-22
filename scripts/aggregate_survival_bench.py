#!/usr/bin/env python3
"""Aggregate survival bench artifacts into markdown (+ optional CSV)."""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TECHNIQUES = ["R0", "A", "B", "C", "C-L", "A+"]
BENCHES = ["TB-30", "TB-60", "TB-120", "TB-DRIFT"]


def load_rows(metrics_path: Path) -> list[dict]:
    rows = []
    for line in metrics_path.read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def time_to_tau(rows: list[dict], tau: float | None) -> float | None:
    if tau is None:
        return None
    for r in rows:
        if r.get("fitness_mean", float("-inf")) >= tau:
            return float(r.get("wall_ms_elapsed", 0))
    return None


def auc(rows: list[dict]) -> float:
    if not rows:
        return float("nan")
    if len(rows) == 1:
        return float(rows[0]["fitness_mean"])
    total = 0.0
    for i in range(1, len(rows)):
        y0 = float(rows[i - 1]["fitness_mean"])
        y1 = float(rows[i]["fitness_mean"])
        total += 0.5 * (y0 + y1)
    return total


def recovery_lag(rows: list[dict], drift_at: int) -> float | None:
    if drift_at < 0 or not rows:
        return None
    pre = [r for r in rows if int(r["generation"]) < drift_at]
    if not pre:
        return None
    target = 0.9 * float(pre[-1]["fitness_mean"])
    for r in rows:
        gen = int(r["generation"])
        if gen <= drift_at:
            continue
        if float(r["fitness_mean"]) >= target:
            return float(gen - drift_at)
    return None


def cell(values: list[float | None]) -> str:
    nums = [v for v in values if v is not None and not math.isnan(v)]
    if not nums:
        return "—"
    if len(nums) == 1:
        return f"{nums[0]:.4g}"
    return f"{statistics.median(nums):.4g}"


def collect(root: Path) -> list[dict]:
    out = []
    for bench in BENCHES:
        for tech in TECHNIQUES:
            tech_dir = root / bench / tech
            if not tech_dir.is_dir():
                continue
            times, fits, aucs, lags = [], [], [], []
            for seed_dir in sorted(tech_dir.glob("seed_*")):
                meta_p = seed_dir / "meta.json"
                met_p = seed_dir / "metrics.jsonl"
                if not meta_p.is_file() or not met_p.is_file():
                    continue
                meta = json.loads(meta_p.read_text())
                rows = load_rows(met_p)
                tau = meta.get("fitness_threshold")
                times.append(time_to_tau(rows, tau))
                fits.append(float(rows[-1]["fitness_mean"]) if rows else None)
                aucs.append(auc(rows))
                lags.append(recovery_lag(rows, int(meta.get("drift_at_gen", -1))))
            if not fits:
                continue
            out.append(
                {
                    "technique": tech,
                    "bench": bench,
                    "median_time_to_tau_ms": cell(times),
                    "fitness_at_budget": cell(fits),
                    "auc": cell(aucs),
                    "recovery_lag_gens": cell(lags) if bench in ("TB-DRIFT", "TB-120") else "n/a",
                }
            )
    return out


def write_md(rows: list[dict], path: Path) -> None:
    lines = [
        "# Survival benchmark summary",
        "",
        "> Aggregated from `results/survival/`. Phase 08 timed benches.",
        "> **Smoke protocol:** regenerate with `npm run bench:aggregate` after runs.",
        "> `—` = τ not reached (or recovery undefined). `n/a` = not applicable.",
        "",
        "| technique | bench | median time-to-τ (ms) | fitness@budget | AUC | recovery lag (gens) |",
        "|-----------|-------|------------------------|----------------|-----|---------------------|",
    ]
    for r in rows:
        lines.append(
            f"| {r['technique']} | {r['bench']} | {r['median_time_to_tau_ms']} | "
            f"{r['fitness_at_budget']} | {r['auc']} | {r['recovery_lag_gens']} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "technique",
                "bench",
                "median_time_to_tau_ms",
                "fitness_at_budget",
                "auc",
                "recovery_lag_gens",
            ],
        )
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--results-root", type=Path, default=ROOT / "results" / "survival")
    p.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "docs" / "results" / "survival-benchmark-summary.md",
    )
    p.add_argument("--out-csv", type=Path, default=None)
    args = p.parse_args()
    rows = collect(args.results_root)
    write_md(rows, args.out_md)
    if args.out_csv:
        write_csv(rows, args.out_csv)
    print(f"wrote {args.out_md} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
