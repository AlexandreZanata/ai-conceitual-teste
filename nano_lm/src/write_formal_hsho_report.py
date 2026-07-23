"""Render formal H-SHO vs B2 comparison markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from formal_ops import decide_formal_vs_b2, means_by_family


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = means_by_family(data["rows"])
    decision = decide_formal_vs_b2("H-SHO", stats)
    delta = stats["H-SHO"]["lp"] - stats["B2"]["lp"]
    lines = [
        "# Formal H-SHO vs B2 (equal-budget follow-up)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Prompts: `nano_lm/prompts/eval_prompts.yaml` (8). Seeds: 0,1,2.",
        "B2: KD 120 steps. H-SHO: pop=8, gens=12, mutate + layer shock.",
        "Teacher judge: TinyStories-33M. Fitness: probe CE (no teacher_lp leak).",
        "",
        "| family | mean teacher_lp | Δ vs B2 | mean wall_ms | n |",
        "|--------|-----------------|---------|--------------|---|",
        f"| B2 | {stats['B2']['lp']:.4f} | — | {stats['B2']['wall']:.0f} | "
        f"{int(stats['B2']['n'])} |",
        f"| H-SHO | {stats['H-SHO']['lp']:.4f} | {delta:+.4f} | "
        f"{stats['H-SHO']['wall']:.0f} | {int(stats['H-SHO']['n'])} |",
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
        default=Path("results/nano-lm/formal-hsho-b2/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hsho-vs-b2.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
