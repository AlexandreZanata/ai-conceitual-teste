"""Render formal H-JOINT vs CURL + EARLY@B2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from formal_ops import means_by_family
from joint_ops import decide_hjoint


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    stats = {
        name: {"mean_lp": st["lp"], "mean_wall": st["wall"], "n": st["n"]}
        for name, st in fam.items()
    }
    decision = decide_hjoint(stats.get("H-JOINT", {}), stats)
    lines = [
        "# Formal H-JOINT — joint curriculum ∪ early-exit",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Kill if ≤ CURL default or ≤ H-EARLY@B2.",
        "",
        "| family | mean teacher_lp | mean wall_ms | n |",
        "|--------|-----------------|--------------|---|",
    ]
    for name in ("H-CURL", "H-EARLY", "H-JOINT"):
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
            "Commands: `npm run nano:formal:joint` → "
            "`npm run nano:formal:joint:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hjoint/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hjoint-vs-tips.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
