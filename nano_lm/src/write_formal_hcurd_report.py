"""Render formal H-CURD vs H-CURL2 tip."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from curd_ops import decide_hcurd
from formal_ops import means_by_family


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    stats = {
        name: {"mean_lp": st["lp"], "mean_wall": st["wall"], "n": st["n"]}
        for name, st in fam.items()
    }
    decision = decide_hcurd(stats.get("H-CURD", {}), stats)
    tip = stats.get("H-CURL2", {})
    hyp = stats.get("H-CURD", {})
    d_lp = hyp.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    lines = [
        "# Formal H-CURD vs H-CURL2 (difficulty curriculum)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Equal budget: 120 steps; tip = formal CURL2 lo=6. Fixed seq_len.",
        "Kill if ≤ H-CURL2 tip on teacher_lp.",
        "",
        "| family | mean teacher_lp | Δ vs CURL2 | mean wall_ms | n |",
        "|--------|-----------------|------------|--------------|---|",
    ]
    for name in ("H-CURL2", "H-CURD"):
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
            "Commands: `npm run nano:formal:hcurd` → "
            "`npm run nano:formal:hcurd:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hcurd/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hcurd-vs-hcurl2.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
