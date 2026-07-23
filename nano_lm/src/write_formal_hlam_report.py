"""Render formal H-LAM vs H-BAL (+ B2) comparison markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from formal_ops import decide_formal_vs_control, means_by_family


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = means_by_family(data["rows"])
    decision = decide_formal_vs_control("H-LAM", "H-BAL", stats)
    d_bal = stats["H-LAM"]["lp"] - stats["H-BAL"]["lp"]
    d_b2 = stats["H-LAM"]["lp"] - stats["B2"]["lp"]
    unstable = "yes" if stats["H-LAM"].get("unstable", 0.0) > 0.0 else "no"
    lines = [
        "# Formal H-LAM vs H-BAL (equal-budget follow-up)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Prompts: `nano_lm/prompts/eval_prompts.yaml` (8). Seeds: 0,1,2.",
        "B2: KD 120 steps. H-BAL/H-LAM: pop=8, gens=12, lifetime_steps=2.",
        "Teacher judge: TinyStories-33M. Primary gate: H-LAM vs H-BAL.",
        "",
        "| family | mean teacher_lp | Δ vs H-BAL | Δ vs B2 | mean wall_ms | unstable | n |",
        "|--------|-----------------|------------|---------|--------------|----------|---|",
        f"| B2 | {stats['B2']['lp']:.4f} | — | — | {stats['B2']['wall']:.0f} | — | "
        f"{int(stats['B2']['n'])} |",
        f"| H-BAL | {stats['H-BAL']['lp']:.4f} | — | "
        f"{stats['H-BAL']['lp'] - stats['B2']['lp']:+.4f} | "
        f"{stats['H-BAL']['wall']:.0f} | — | {int(stats['H-BAL']['n'])} |",
        f"| H-LAM | {stats['H-LAM']['lp']:.4f} | {d_bal:+.4f} | {d_b2:+.4f} | "
        f"{stats['H-LAM']['wall']:.0f} | {unstable} | {int(stats['H-LAM']['n'])} |",
        "",
        f"**Decision (vs H-BAL):** {decision}",
        f"**vs B2:** {decide_formal_vs_control('H-LAM', 'B2', stats)}",
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
        default=Path("results/nano-lm/formal-hlam-b2/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hlam-vs-hbal.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
