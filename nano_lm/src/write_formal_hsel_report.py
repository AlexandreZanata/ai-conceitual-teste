"""Render formal H-SEL vs B2 comparison markdown."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def _means(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    buckets: dict[str, list] = defaultdict(list)
    for r in rows:
        buckets[r["family"]].append(r)
    out = {}
    for fam, items in buckets.items():
        lps = [float(x["teacher_mean_logprob"]) for x in items]
        walls = [float(x["mean_wall_ms"]) for x in items]
        out[fam] = {
            "lp": sum(lps) / len(lps),
            "wall": sum(walls) / len(walls),
            "n": len(items),
        }
    return out


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = _means(data["rows"])
    b2 = stats["B2"]["lp"]
    h = stats["H-SEL"]["lp"]
    delta = h - b2
    decision = (
        "PROMOTE confirmed (H-SEL > B2)"
        if delta > 0
        else "KILL / reverse smoke (H-SEL ≤ B2)"
    )
    lines = [
        "# Formal H-SEL vs B2 (equal-budget follow-up)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Prompts: `nano_lm/prompts/eval_prompts.yaml` (8). Seeds: 0,1,2.",
        "B2: KD 120 steps. H-SEL: pop=8, gens=12. Teacher judge: TinyStories-33M.",
        "",
        "| family | mean teacher_lp | Δ vs B2 | mean wall_ms | n |",
        "|--------|-----------------|---------|--------------|---|",
        f"| B2 | {stats['B2']['lp']:.4f} | — | {stats['B2']['wall']:.0f} | "
        f"{stats['B2']['n']} |",
        f"| H-SEL | {stats['H-SEL']['lp']:.4f} | {delta:+.4f} | "
        f"{stats['H-SEL']['wall']:.0f} | {stats['H-SEL']['n']} |",
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
        default=Path("results/nano-lm/formal-hsel-b2/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hsel-vs-b2.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
