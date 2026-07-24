"""Render formal H-PROX vs H-POOL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from formal_ops import means_by_family
from prox_ops import decide_hprox


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    stats = {
        name: {"mean_lp": st["lp"], "mean_wall": st["wall"], "n": st["n"]}
        for name, st in fam.items()
    }
    decision = decide_hprox(stats.get("H-PROX", {}), stats)
    tip = stats.get("H-POOL", {})
    hyp = stats.get("H-PROX", {})
    d_lp = hyp.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    lines = [
        "# Formal H-PROX vs H-POOL (CE proxy fit)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared B2; warm-start; fit ranks by student CE only. Fit≠eval claim.",
        "Kill if claim quality < POOL−ε.",
        "",
        "| family | mean teacher_lp | Δ vs POOL | mean wall_ms | n |",
        "|--------|-----------------|-----------|--------------|---|",
    ]
    for name in ("H-POOL", "H-PROX"):
        if name not in stats:
            continue
        st = stats[name]
        d = "—" if name == "H-POOL" else f"{d_lp:+.4f}"
        lines.append(
            f"| {name} | {st['mean_lp']:.4f} | {d} | {st['mean_wall']:.0f} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Commands: `npm run nano:formal:hprox` → "
            "`npm run nano:formal:hprox:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hprox/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hprox-vs-hpool.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
