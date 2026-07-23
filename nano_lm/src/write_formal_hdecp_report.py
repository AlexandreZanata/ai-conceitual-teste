"""Render formal H-DECP vs B4 + GLOBAL markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from decp_ops import decide_hdecp
from formal_ops import means_by_family


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    stats = {
        name: {"mean_lp": st["lp"], "mean_wall": st["wall"], "n": st["n"]}
        for name, st in fam.items()
    }
    decision = decide_hdecp(stats.get("H-DECP", {}), stats)
    b4 = stats.get("B4", {})
    lines = [
        "# Formal H-DECP vs B4 + GLOBAL (per-prompt gene bank)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared B2 ckpts. Bank on fit; claim on eval via proxy pick. Fit≠eval.",
        "Kill if ≤ GLOBAL or B4.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |",
        "|--------|-----------------|--------------|------------|---|",
    ]
    for name in ("B4", "GLOBAL", "H-DECP"):
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
            "Commands: `npm run nano:formal:hdecp` → "
            "`npm run nano:formal:hdecp:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hdecp/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hdecp-vs-b4.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
