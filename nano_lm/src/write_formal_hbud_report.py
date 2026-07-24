"""Render formal H-BUD vs H-EARLY."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from bud_ops import decide_hbud
from formal_ops import means_by_family


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    stats = {
        name: {"mean_lp": st["lp"], "mean_wall": st["wall"], "n": st["n"]}
        for name, st in fam.items()
    }
    decision = decide_hbud(stats.get("H-BUD", {}), stats)
    tip = stats.get("H-EARLY", {})
    hyp = stats.get("H-BUD", {})
    d_lp = hyp.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    lines = [
        "# Formal H-BUD vs H-EARLY (max_new + exit gene)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared B2; co-evolve max_new with EARLY knobs. Fit≠eval.",
        "Kill if dominated by H-EARLY or quality < EARLY−ε.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs EARLY | n |",
        "|--------|-----------------|--------------|---------------|---|",
    ]
    for name in ("H-EARLY", "H-BUD"):
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
            "Commands: `npm run nano:formal:hbud` → "
            "`npm run nano:formal:hbud:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hbud/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hbud-vs-hearly.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
