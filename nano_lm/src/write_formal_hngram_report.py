"""Render formal H-NGRAM vs B4 markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from formal_ops import means_by_family
from ngram_ops import decide_hngram


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    stats = {
        name: {"mean_lp": st["lp"], "mean_wall": st["wall"], "n": st["n"]}
        for name, st in fam.items()
    }
    decision = decide_hngram(stats.get("H-NGRAM", {}), stats)
    hyp = stats.get("H-NGRAM", {})
    b4 = stats.get("B4", {})
    d_lp = hyp.get("mean_lp", float("nan")) - b4.get("mean_lp", float("nan"))
    lines = [
        "# Formal H-NGRAM vs B4 (no-repeat n-gram)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared B2 ckpts; fit≠eval prompts; grid n∈{0,2,3,4}.",
        "Kill if quality < B4−ε or no wall win.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |",
        "|--------|-----------------|--------------|------------|---|",
    ]
    for name in ("B4", "H-NGRAM"):
        if name not in stats:
            continue
        st = stats[name]
        delta = "—" if name == "B4" else f"{d_lp:+.4f}"
        lines.append(
            f"| {name} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | {delta} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Commands: `npm run nano:formal:ngram` → "
            "`npm run nano:formal:ngram:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hngram/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hngram-vs-b4.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
