"""Render formal H-DECK2 top_k ablation markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from deck2_ops import DECK2_TOP_KS, best_top_k, decide_hdeck2, mean_lp_by_top_k
from formal_ops import means_by_family


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data["rows"]
    deck2 = [r for r in rows if r.get("family") == "H-DECK2"]
    lp_by_k = mean_lp_by_top_k(deck2)
    decision = decide_hdeck2(lp_by_k)
    control = lp_by_k.get(2, float("nan"))
    best = best_top_k(lp_by_k) if lp_by_k else None
    fam = means_by_family(rows)
    b4_lp = fam.get("B4", {}).get("lp", float("nan"))
    lines = [
        "# Formal H-DECK2 vs H-DECK (top_k ablation, equal pop×gens)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared B2 KD ckpts from formal H-DECK. pop=8 gens=12; top_k∈{1,2,3}.",
        "Fit: `fit_prompts.yaml`. Eval: `eval_prompts.yaml`. Seeds: 0,1,2.",
        "Kill if best k ≤ H-DECK (k=2).",
        "",
        "| top_k / family | mean teacher_lp | Δ vs k=2 | mean wall_ms | n |",
        "|----------------|-----------------|----------|--------------|---|",
    ]
    if "B4" in fam:
        lines.append(
            f"| B4 | {b4_lp:.4f} | — | {fam['B4']['wall']:.0f} | "
            f"{int(fam['B4']['n'])} |"
        )
    n_by_k: dict[int, int] = {}
    wall_by_k: dict[int, list[float]] = {k: [] for k in DECK2_TOP_KS}
    for r in deck2:
        k = int(r["top_k"])
        n_by_k[k] = n_by_k.get(k, 0) + 1
        wall_by_k[k].append(float(r.get("mean_wall_ms", float("nan"))))
    for k in DECK2_TOP_KS:
        if k not in lp_by_k:
            continue
        delta = "—" if k == 2 else f"{lp_by_k[k] - control:+.4f}"
        walls = wall_by_k[k]
        wall = sum(walls) / len(walls) if walls else float("nan")
        lines.append(
            f"| H-DECK2 k={k} | {lp_by_k[k]:.4f} | {delta} | {wall:.0f} | "
            f"{n_by_k.get(k, 0)} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            f"Best top_k: {best}. B4 mean lp: {b4_lp:.4f}.",
            "",
            "Commands: `npm run nano:formal:hdeck2` → "
            "`npm run nano:formal:hdeck2:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hdeck2/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hdeck2-vs-hdeck.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
