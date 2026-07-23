"""Render formal H-POOL vs cold H-DECKL markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from formal_ops import means_by_family
from pool_ops import decide_hpool


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    stats = {
        name: {"mean_lp": st["lp"], "n": st["n"], "wall": st["wall"]}
        for name, st in fam.items()
    }
    decision = decide_hpool(stats.get("H-POOL", {}), stats)
    cold = stats.get("H-DECKL", {})
    hyp = stats.get("H-POOL", {})
    delta = hyp.get("mean_lp", float("nan")) - cold.get("mean_lp", float("nan"))
    lines = [
        "# Formal H-POOL vs cold H-DECKL (cross-seed warm-start)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared B2 ckpts. pop=8 gens=12 top_k=1. Leave-one-out gene pool.",
        "Kill if ≤ cold H-DECKL.",
        "",
        "| family | mean teacher_lp | Δ vs cold | mean wall_ms | n |",
        "|--------|-----------------|-----------|--------------|---|",
    ]
    for name in ("H-DECKL", "H-POOL"):
        if name not in stats:
            continue
        st = stats[name]
        d = "—" if name == "H-DECKL" else f"{delta:+.4f}"
        lines.append(
            f"| {name} | {st['mean_lp']:.4f} | {d} | {st['wall']:.0f} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Commands: `npm run nano:formal:hpool` → "
            "`npm run nano:formal:hpool:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hpool/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hpool-vs-hdeckl.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
