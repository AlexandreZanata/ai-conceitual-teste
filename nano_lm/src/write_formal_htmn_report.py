"""Render formal H-TMN vs tip markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from formal_ops import means_by_family
from tmn_ops import decide_htmn, tip_max_lp


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    stats = {
        name: {"mean_lp": st["lp"], "mean_wall": st["wall"], "n": st["n"]}
        for name, st in fam.items()
    }
    decision = decide_htmn(stats.get("H-TMN", {}), stats)
    max_lp = tip_max_lp(stats) or float("nan")
    lines = [
        "# Formal H-TMN vs H-TYP × H-MINP",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Reuse formal tip metas; claim stack on eval_prompts.",
        "Kill if lp < max(tips)−ε or wall ≥ min(tips).",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs max tip | n |",
        "|--------|-----------------|--------------|-----------------|---|",
    ]
    for name in ("H-TYP", "H-MINP", "H-TMN"):
        if name not in stats:
            continue
        st = stats[name]
        delta = "—" if name != "H-TMN" else f"{st['mean_lp'] - max_lp:+.4f}"
        lines.append(
            f"| {name} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | {delta} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Commands: `npm run nano:formal:tmn` → "
            "`npm run nano:formal:tmn:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-htmn/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-htmn-vs-tips.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
