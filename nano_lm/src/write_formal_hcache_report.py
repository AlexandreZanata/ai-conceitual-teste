"""Render formal H-CACHE vs H-EARLY + B4."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cache_ops import decide_hcache
from formal_ops import means_by_family


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    stats = {
        name: {"mean_lp": st["lp"], "mean_wall": st["wall"], "n": st["n"]}
        for name, st in fam.items()
    }
    decision = decide_hcache(stats.get("H-CACHE", {}), stats)
    lines = [
        "# Formal H-CACHE vs H-EARLY + B4 (KV on tip genes)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared B2 + formal EARLY tip genes; KV decode claim. Fit≠eval.",
        "Kill if no wall save vs EARLY or B4 dual fails.",
        "",
        "| family | mean teacher_lp | mean wall_ms | n |",
        "|--------|-----------------|--------------|---|",
    ]
    for name in ("B4", "H-EARLY", "H-CACHE"):
        if name not in stats:
            continue
        st = stats[name]
        lines.append(
            f"| {name} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Commands: `npm run nano:formal:hcache` → "
            "`npm run nano:formal:hcache:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hcache/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hcache-vs-early.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
