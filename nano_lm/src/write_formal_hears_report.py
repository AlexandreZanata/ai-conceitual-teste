"""Render formal H-EARS vs H-EARLY."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ears_ops import decide_hears
from formal_ops import means_by_family


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    stats = {
        name: {"mean_lp": st["lp"], "mean_wall": st["wall"], "n": st["n"]}
        for name, st in fam.items()
    }
    decision = decide_hears(stats.get("H-EARS", {}), stats)
    tip = stats.get("H-EARLY", {})
    hyp = stats.get("H-EARS", {})
    d_lp = hyp.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    lines = [
        "# Formal H-EARS vs H-EARLY (scheduled early-exit thr)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared B2; evolve len/budget schedule on conf thr. Fit≠eval.",
        "Kill if quality < EARLY−ε or no wall win vs H-EARLY.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs EARLY | n |",
        "|--------|-----------------|--------------|---------------|---|",
    ]
    for name in ("H-EARLY", "H-EARS"):
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
            "Commands: `npm run nano:formal:hears` → "
            "`npm run nano:formal:hears:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hears/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hears-vs-hearly.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
