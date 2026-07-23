"""Aggregate nano_lm JSONL runs into markdown (+ optional CSV)."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def group_by_method(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["method"]].append(row)
    return dict(grouped)


def mean_std(values: list[float]) -> tuple[float, float]:
    if not values:
        return float("nan"), float("nan")
    if len(values) == 1:
        return values[0], 0.0
    return statistics.mean(values), statistics.stdev(values)


def win_rate_vs_ar(rows: list[dict[str, Any]], method: str) -> float:
    """Share of (prompt_id, seed) where method mean_logprob > AR."""
    by_key: dict[tuple[str, int], dict[str, float]] = defaultdict(dict)
    for row in rows:
        by_key[(row["prompt_id"], row["seed"])][row["method"]] = row[
            "mean_logprob"
        ]
    wins = 0
    total = 0
    for scores in by_key.values():
        if "ar" not in scores or method not in scores:
            continue
        total += 1
        if scores[method] > scores["ar"]:
            wins += 1
    return wins / total if total else float("nan")


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped = group_by_method(rows)
    summary = []
    for method, items in sorted(grouped.items()):
        mlp = [float(x["mean_logprob"]) for x in items]
        wall = [float(x["wall_ms"]) for x in items]
        d1 = [float(x["distinct_1"]) for x in items]
        d2 = [float(x["distinct_2"]) for x in items]
        te = [float(x["token_evals"]) for x in items]
        m_mlp, s_mlp = mean_std(mlp)
        m_wall, s_wall = mean_std(wall)
        m_d1, _ = mean_std(d1)
        m_d2, _ = mean_std(d2)
        m_te, _ = mean_std(te)
        wr = 1.0 if method == "ar" else win_rate_vs_ar(rows, method)
        summary.append(
            {
                "method": method,
                "mean_logprob": m_mlp,
                "std_logprob": s_mlp,
                "mean_wall_ms": m_wall,
                "std_wall_ms": s_wall,
                "mean_distinct_1": m_d1,
                "mean_distinct_2": m_d2,
                "mean_token_evals": m_te,
                "win_rate_vs_ar": wr,
                "n": len(items),
            }
        )
    return summary


def to_markdown(summary: list[dict[str, Any]], source: str) -> str:
    lines = [
        "# Nano-LM bench summary",
        "",
        f"Source: `{source}`",
        "",
        "| method | mean_logprob ± std | wall_ms ± std | distinct-1 | "
        "distinct-2 | token_evals | win_rate_vs_ar | n |",
        "|--------|-------------------|---------------|------------|"
        "------------|-------------|----------------|---|",
    ]
    for row in summary:
        lines.append(
            f"| {row['method']} | "
            f"{row['mean_logprob']:.4f} ± {row['std_logprob']:.4f} | "
            f"{row['mean_wall_ms']:.1f} ± {row['std_wall_ms']:.1f} | "
            f"{row['mean_distinct_1']:.3f} | {row['mean_distinct_2']:.3f} | "
            f"{row['mean_token_evals']:.0f} | {row['win_rate_vs_ar']:.3f} | "
            f"{row['n']} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runs",
        type=Path,
        default=Path("results/nano-lm/smoke/runs.jsonl"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("docs/results/nano-lm/smoke-summary.md"),
    )
    parser.add_argument("--out-csv", type=Path, default=None)
    args = parser.parse_args()
    rows = load_rows(args.runs)
    summary = summarize(rows)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(to_markdown(summary, str(args.runs)), encoding="utf-8")
    if args.out_csv:
        args.out_csv.parent.mkdir(parents=True, exist_ok=True)
        with args.out_csv.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
            writer.writeheader()
            writer.writerows(summary)
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
