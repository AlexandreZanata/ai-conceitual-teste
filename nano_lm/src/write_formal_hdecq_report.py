"""Render formal H-DECQ vs B4 + H-DECM markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from decq_ops import decide_hdecq
from formal_ops import means_by_family


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    stats = {
        name: {"mean_lp": st["lp"], "mean_wall": st["wall"], "n": st["n"]}
        for name, st in fam.items()
    }
    decision = decide_hdecq(stats.get("H-DECQ", {}), stats)
    b4 = stats.get("B4", {})
    lines = [
        "# Formal H-DECQ vs B4 + H-DECM (quantized gene codes)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared B2 ckpts. Discrete T/top_p codebook; mixture claim. Fit≠eval.",
        "Kill if ≤ H-DECM or B4.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |",
        "|--------|-----------------|--------------|------------|---|",
    ]
    for name in ("B4", "H-DECM", "H-DECQ"):
        if name not in stats:
            continue
        st = stats[name]
        d = "—" if name == "B4" else f"{st['mean_lp'] - b4['mean_lp']:+.4f}"
        lines.append(
            f"| {name} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | {d} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Commands: `npm run nano:formal:hdecq` → "
            "`npm run nano:formal:hdecq:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hdecq/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hdecq-vs-b4.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
