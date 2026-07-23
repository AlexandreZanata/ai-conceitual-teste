"""Render formal H-HOLD vs B2 comparison markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from formal_ops import decide_formal_vs_b2, means_by_family


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = means_by_family(data["rows"])
    decision = decide_formal_vs_b2("H-HOLD", stats)
    delta = stats["H-HOLD"]["lp"] - stats["B2"]["lp"]
    overfit = "yes" if stats["H-HOLD"].get("overfit", 0.0) > 0.0 else "no"
    lines = [
        "# Formal H-HOLD vs B2 (equal-budget follow-up)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Fit prompts: `nano_lm/prompts/fit_prompts.yaml` (f01–f02).",
        "Eval prompts: `nano_lm/prompts/eval_prompts.yaml` (8). Seeds: 0,1,2.",
        "B2: KD 120 steps. H-HOLD: pop=8, gens=12, max_new_fit=24.",
        "Teacher judge: TinyStories-33M. Integrity: fit ∩ eval ids = ∅.",
        "",
        "| family | mean teacher_lp | Δ vs B2 | mean wall_ms | overfit | n |",
        "|--------|-----------------|---------|--------------|---------|---|",
        f"| B2 | {stats['B2']['lp']:.4f} | — | {stats['B2']['wall']:.0f} | — | "
        f"{int(stats['B2']['n'])} |",
        f"| H-HOLD | {stats['H-HOLD']['lp']:.4f} | {delta:+.4f} | "
        f"{stats['H-HOLD']['wall']:.0f} | {overfit} | {int(stats['H-HOLD']['n'])} |",
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
        default=Path("results/nano-lm/formal-hhold-b2/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hhold-vs-b2.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
