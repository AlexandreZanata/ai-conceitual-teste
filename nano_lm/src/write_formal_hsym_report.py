"""Render formal H-SYM vs B2 comparison markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from formal_ops import decide_formal_vs_b2, means_by_family


def _mean_sterile(rows: list[dict]) -> float:
    vals = [float(r["sterile_gens"]) for r in rows if "sterile_gens" in r]
    return sum(vals) / len(vals) if vals else float("nan")


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data["rows"]
    stats = means_by_family(rows)
    decision = decide_formal_vs_b2("H-SYM", stats)
    delta = stats["H-SYM"]["lp"] - stats["B2"]["lp"]
    sterile = _mean_sterile([r for r in rows if r.get("family") == "H-SYM"])
    lines = [
        "# Formal H-SYM vs B2 (equal-budget follow-up)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Prompts: `nano_lm/prompts/eval_prompts.yaml` (8). Seeds: 0,1,2.",
        "B2: KD 120 steps. H-SYM: pop=8, gens=12, obligate pair + mutate.",
        "Teacher judge: TinyStories-33M. Fitness: probe CE (no teacher_lp leak).",
        "",
        "| family | mean teacher_lp | Δ vs B2 | mean wall_ms | mean sterile_gens | n |",
        "|--------|-----------------|---------|--------------|-------------------|---|",
        f"| B2 | {stats['B2']['lp']:.4f} | — | {stats['B2']['wall']:.0f} | — | "
        f"{int(stats['B2']['n'])} |",
        f"| H-SYM | {stats['H-SYM']['lp']:.4f} | {delta:+.4f} | "
        f"{stats['H-SYM']['wall']:.0f} | {sterile:.1f} | {int(stats['H-SYM']['n'])} |",
        "",
        f"**Decision:** {decision}",
        "",
        "Smoke promote was tentative; this run is the claim-facing check.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hsym-b2/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hsym-vs-b2.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
