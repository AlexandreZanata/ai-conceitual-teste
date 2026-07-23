"""Render formal H-DRAFT vs B4 markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from draft_ops import decide_hdraft
from formal_ops import means_by_family


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    stats = {
        name: {"mean_lp": st["lp"], "mean_wall": st["wall"], "n": st["n"]}
        for name, st in fam.items()
    }
    decision = decide_hdraft(stats.get("H-DRAFT", {}), stats)
    b4 = stats.get("B4", {})
    hyp = stats.get("H-DRAFT", {})
    d_lp = hyp.get("mean_lp", float("nan")) - b4.get("mean_lp", float("nan"))
    lines = [
        "# Formal H-DRAFT vs B4 (evolved speculative draft knobs)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared B2 ckpts. Evolve draft_len/temp/top_p. Fit≠eval.",
        "Kill if quality < B4−ε or no wall win vs B4.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |",
        "|--------|-----------------|--------------|------------|---|",
    ]
    for name in ("B4", "H-DRAFT"):
        if name not in stats:
            continue
        st = stats[name]
        d = "—" if name == "B4" else f"{d_lp:+.4f}"
        lines.append(
            f"| {name} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | {d} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Commands: `npm run nano:formal:hdraft` → "
            "`npm run nano:formal:hdraft:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hdraft/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hdraft-vs-b4.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
