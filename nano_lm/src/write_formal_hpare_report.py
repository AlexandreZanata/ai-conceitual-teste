"""Render formal H-PARE vs B4 markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from formal_ops import means_by_family
from pare_ops import decide_hpare


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    stats = {
        name: {"mean_lp": st["lp"], "mean_wall": st["wall"], "n": st["n"]}
        for name, st in fam.items()
    }
    pare_rows = [r for r in data["rows"] if r.get("family") == "H-PARE"]
    if pare_rows:
        stats["H-PARE"]["front_n"] = sum(float(r["front_n"]) for r in pare_rows) / len(
            pare_rows
        )
    decision = decide_hpare(stats.get("H-PARE", {}), stats)
    b4 = stats.get("B4", {})
    hyp = stats.get("H-PARE", {})
    d_lp = hyp.get("mean_lp", float("nan")) - b4.get("mean_lp", float("nan"))
    lines = [
        "# Formal H-PARE vs B4 (Pareto archive + knee claim)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared B2 ckpts. pop=8 gens=12 top_k=1. Fit≠eval.",
        "Kill if empty front or ≤ B4 / dominated.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | front_n | n |",
        "|--------|-----------------|--------------|------------|---------|---|",
    ]
    for name in ("B4", "H-PARE"):
        if name not in stats:
            continue
        st = stats[name]
        d = "—" if name == "B4" else f"{d_lp:+.4f}"
        fn = "—" if name == "B4" else f"{st.get('front_n', float('nan')):.1f}"
        lines.append(
            f"| {name} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | {d} | "
            f"{fn} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Commands: `npm run nano:formal:hpare` → "
            "`npm run nano:formal:hpare:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hpare/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hpare-vs-b4.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
