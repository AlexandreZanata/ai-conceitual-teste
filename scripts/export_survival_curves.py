#!/usr/bin/env python3
"""Export fitness curves (CSV + SVG) from results/survival for the phase 09 report."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SERIES = [
    ("TB-30", "R0", 1),
    ("TB-30", "A", 1),
    ("TB-30", "B", 1),
    ("TB-30", "C", 1),
    ("TB-60", "R0", 1),
    ("TB-60", "A", 1),
    ("TB-60", "B", 1),
    ("TB-60", "C", 1),
]


def load_metrics(path: Path) -> list[dict]:
    import json

    rows = []
    for line in path.read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_csv(rows: list[dict], out: Path, run_id: str) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "run_id",
                "generation",
                "fitness_mean",
                "wall_ms_elapsed",
                "learning_rate_mean",
                "alive_mean",
            ],
        )
        w.writeheader()
        for r in rows:
            w.writerow(
                {
                    "run_id": run_id,
                    "generation": r["generation"],
                    "fitness_mean": r["fitness_mean"],
                    "wall_ms_elapsed": r["wall_ms_elapsed"],
                    "learning_rate_mean": r["learning_rate_mean"],
                    "alive_mean": r["alive_mean"],
                }
            )


def svg_polyline(series: list[tuple[str, list[tuple[float, float]]]],
                 title: str, xlab: str, out: Path) -> None:
    """Minimal SVG multi-line chart (no external deps)."""
    w, h, pad = 640, 280, 48
    colors = ["#1b1b1b", "#0b6e4f", "#8b1e3f", "#1d4e89"]
    all_x = [p[0] for _, pts in series for p in pts]
    all_y = [p[1] for _, pts in series for p in pts]
    xmin, xmax = min(all_x), max(all_x) or 1.0
    ymin, ymax = min(all_y), max(all_y)
    if ymax <= ymin:
        ymax = ymin + 1.0

    def sx(x: float) -> float:
        return pad + (x - xmin) / (xmax - xmin) * (w - 2 * pad)

    def sy(y: float) -> float:
        return h - pad - (y - ymin) / (ymax - ymin) * (h - 2 * pad)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">',
        f'<rect width="100%" height="100%" fill="#f7f5f1"/>',
        f'<text x="{pad}" y="24" font-family="Georgia, serif" font-size="14">'
        f"{title}</text>",
        f'<text x="{w/2}" y="{h-8}" text-anchor="middle" font-size="11" '
        f'font-family="sans-serif">{xlab}</text>',
    ]
    for i, (label, pts) in enumerate(series):
        if not pts:
            continue
        d = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in pts)
        c = colors[i % len(colors)]
        parts.append(
            f'<polyline fill="none" stroke="{c}" stroke-width="2" points="{d}"/>'
        )
        parts.append(
            f'<text x="{w - pad}" y="{40 + i * 16}" text-anchor="end" '
            f'font-size="11" fill="{c}" font-family="sans-serif">{label}</text>'
        )
    parts.append("</svg>")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(parts) + "\n")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--results-root", type=Path, default=ROOT / "results" / "survival")
    p.add_argument("--out-dir", type=Path, default=ROOT / "docs" / "results" / "curves")
    args = p.parse_args()
    by_bench: dict[str, list[tuple[str, list[tuple[float, float]]]]] = {}
    by_bench_wall: dict[str, list[tuple[str, list[tuple[float, float]]]]] = {}
    for bench, tech, seed in DEFAULT_SERIES:
        run_dir = args.results_root / bench / tech / f"seed_{seed}"
        metrics = run_dir / "metrics.jsonl"
        if not metrics.is_file():
            print(f"skip missing {metrics}")
            continue
        rows = load_metrics(metrics)
        run_id = f"{bench}/{tech}/seed_{seed}"
        write_csv(rows, args.out_dir / f"{bench}_{tech}_seed{seed}.csv", run_id)
        by_bench.setdefault(bench, []).append(
            (tech, [(float(r["generation"]), float(r["fitness_mean"])) for r in rows])
        )
        by_bench_wall.setdefault(bench, []).append(
            (
                tech,
                [(float(r["wall_ms_elapsed"]), float(r["fitness_mean"])) for r in rows],
            )
        )
    for bench, series in by_bench.items():
        svg_polyline(
            series,
            f"{bench} fitness vs generation (seed_1)",
            "generation",
            args.out_dir / f"{bench}_fitness_vs_generation.svg",
        )
    for bench, series in by_bench_wall.items():
        svg_polyline(
            series,
            f"{bench} fitness vs wall_ms (seed_1)",
            "wall_ms_elapsed",
            args.out_dir / f"{bench}_fitness_vs_wall_ms.svg",
        )
    print(f"wrote curves under {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
