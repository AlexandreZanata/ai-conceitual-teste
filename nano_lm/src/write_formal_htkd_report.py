"""Render formal H-TKD vs B2 markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from formal_ops import means_by_family
from tkd_ops import decide_htkd


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    stats = {
        name: {"mean_lp": st["lp"], "mean_wall": st["wall"], "n": st["n"]}
        for name, st in fam.items()
    }
    decision = decide_htkd(stats.get("H-TKD", {}), stats)
    hyp = stats.get("H-TKD", {})
    b2 = stats.get("B2", {})
    d_b2 = hyp.get("mean_lp", float("nan")) - b2.get("mean_lp", float("nan"))
    lines = [
        "# Formal H-TKD vs B2 (top-k sparse KD)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Equal budget: 120 steps, seeds 0–2, eval_prompts, k=32.",
        "Kill if ≤ B2.",
        "",
        "| family | mean teacher_lp | Δ vs B2 | mean wall_ms | n |",
        "|--------|-----------------|---------|--------------|---|",
    ]
    for name in ("B2", "H-TKD"):
        if name not in stats:
            continue
        st = stats[name]
        delta = "—" if name == "B2" else f"{d_b2:+.4f}"
        lines.append(
            f"| {name} | {st['mean_lp']:.4f} | {delta} | "
            f"{st['mean_wall']:.0f} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Commands: `npm run nano:formal:htkd` → "
            "`npm run nano:formal:htkd:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-htkd/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-htkd-vs-b2.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
