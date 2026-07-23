"""Render formal H-NGE vs H-NGRAM markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from formal_ops import means_by_family
from nge_ops import decide_hnge


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    stats = {
        name: {"mean_lp": st["lp"], "mean_wall": st["wall"], "n": st["n"]}
        for name, st in fam.items()
    }
    decision = decide_hnge(stats.get("H-NGE", {}), stats)
    hyp = stats.get("H-NGE", {})
    tip = stats.get("H-NGRAM", {})
    d_lp = hyp.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    lines = [
        "# Formal H-NGE vs H-NGRAM (evolved ngram gene)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared B2 ckpts; fit≠eval; evolve ngram_size+T/top_p vs grid tip.",
        "Kill if quality < tip−ε or no wall win.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs tip | n |",
        "|--------|-----------------|--------------|-------------|---|",
    ]
    for name in ("H-NGRAM", "H-NGE"):
        if name not in stats:
            continue
        st = stats[name]
        delta = "—" if name == "H-NGRAM" else f"{d_lp:+.4f}"
        lines.append(
            f"| {name} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | {delta} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Commands: `npm run nano:formal:nge` → "
            "`npm run nano:formal:nge:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hnge/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hnge-vs-hngram.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
