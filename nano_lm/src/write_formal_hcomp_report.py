"""Render formal H-COMP vs H-EARLY."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from comp_ops import decide_hcomp
from formal_ops import means_by_family


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    stats = {
        name: {"mean_lp": st["lp"], "mean_wall": st["wall"], "n": st["n"]}
        for name, st in fam.items()
    }
    decision = decide_hcomp(stats.get("H-COMP", {}), stats)
    tip = stats.get("H-EARLY", {})
    hyp = stats.get("H-COMP", {})
    d_lp = hyp.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    lines = [
        "# Formal H-COMP vs H-EARLY (torch.compile)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared B2 + formal EARLY tip genes; compile mode=reduce-overhead.",
        "Kill if quality < EARLY−ε or no wall win.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs EARLY | n |",
        "|--------|-----------------|--------------|---------------|---|",
    ]
    for name in ("H-EARLY", "H-COMP"):
        if name not in stats:
            continue
        st = stats[name]
        d = "—" if name == "H-EARLY" else f"{d_lp:+.4f}"
        lines.append(
            f"| {name} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | {d} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Commands: `npm run nano:formal:hcomp` → "
            "`npm run nano:formal:hcomp:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hcomp/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hcomp-vs-hearly.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
