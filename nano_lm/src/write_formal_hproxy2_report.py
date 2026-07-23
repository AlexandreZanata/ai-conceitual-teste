"""Render formal H-PROXY2 vs H-DECK markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from formal_ops import means_by_family
from proxy2_ops import decide_hproxy2


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data["rows"]
    fam = means_by_family(rows)
    stats: dict[str, dict[str, float]] = {}
    for name, st in fam.items():
        stats[name] = {
            "mean_lp": st["lp"],
            "teacher_forwards": _mean_fwd(rows, name),
            "n": st["n"],
            "wall": st["wall"],
        }
    decision = decide_hproxy2(stats.get("H-PROXY2", {}), stats)
    deck = stats.get("H-DECK", {})
    hyp = stats.get("H-PROXY2", {})
    delta = hyp.get("mean_lp", float("nan")) - deck.get("mean_lp", float("nan"))
    lines = [
        "# Formal H-PROXY2 vs H-DECK (CE proxy vs self-lp)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared B2 KD ckpts. pop=8 gens=12 top_k=1. Fit≠eval prompts.",
        "Kill if ≤ H-DECK quality@forwards.",
        "",
        "| family | mean teacher_lp | Δ vs H-DECK | mean wall_ms | mean fwd | n |",
        "|--------|-----------------|-------------|--------------|----------|---|",
    ]
    for name in ("H-DECK", "H-PROXY2"):
        if name not in stats:
            continue
        st = stats[name]
        d = "—" if name == "H-DECK" else f"{delta:+.4f}"
        lines.append(
            f"| {name} | {st['mean_lp']:.4f} | {d} | {st['wall']:.0f} | "
            f"{st['teacher_forwards']:.0f} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Commands: `npm run nano:formal:hproxy2` → "
            "`npm run nano:formal:hproxy2:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def _mean_fwd(rows: list, family: str) -> float:
    vals = [float(r["teacher_forwards"]) for r in rows if r.get("family") == family]
    return sum(vals) / len(vals) if vals else float("nan")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hproxy2/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hproxy2-vs-hdeck.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
