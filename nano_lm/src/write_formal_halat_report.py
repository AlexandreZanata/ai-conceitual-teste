"""Render formal H-ALAT vs H-CURL2 tip."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from alat_ops import decide_halat
from formal_ops import means_by_family


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    stats = {
        name: {"mean_lp": st["lp"], "mean_wall": st["wall"], "n": st["n"]}
        for name, st in fam.items()
    }
    decision = decide_halat(stats.get("H-ALAT", {}), stats)
    tip = stats.get("H-CURL2", {})
    hyp = stats.get("H-ALAT", {})
    d_lp = hyp.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    lines = [
        "# Formal H-ALAT vs H-CURL2 (α/T schedule / H-αT)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Equal budget: 120 steps; tip = formal CURL2 lo=6 (α=0.5, T=2).",
        "H-ALAT: α 0.25→0.75, T 3→1 by length stage. Kill if ≤ tip.",
        "",
        "| family | mean teacher_lp | Δ vs CURL2 | mean wall_ms | n |",
        "|--------|-----------------|------------|--------------|---|",
    ]
    for name in ("H-CURL2", "H-ALAT"):
        if name not in stats:
            continue
        st = stats[name]
        d = "—" if name == "H-CURL2" else f"{d_lp:+.4f}"
        lines.append(
            f"| {name} | {st['mean_lp']:.4f} | {d} | {st['mean_wall']:.0f} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Commands: `npm run nano:formal:halat` → "
            "`npm run nano:formal:halat:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-halat/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-halat-vs-hcurl2.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
