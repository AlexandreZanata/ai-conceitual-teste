"""Render formal H-ANN vs KD-cos (+ B2) markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ann_ops import decide_hann
from formal_ops import means_by_family


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    stats = {
        name: {"mean_lp": st["lp"], "mean_wall": st["wall"], "n": st["n"]}
        for name, st in fam.items()
    }
    decision = decide_hann(stats.get("H-ANN", {}), stats)
    cos = stats.get("KD-cos", {})
    hyp = stats.get("H-ANN", {})
    b2 = stats.get("B2", {})
    d_cos = hyp.get("mean_lp", float("nan")) - cos.get("mean_lp", float("nan"))
    d_b2 = hyp.get("mean_lp", float("nan")) - b2.get("mean_lp", float("nan"))
    lines = [
        "# Formal H-ANN vs KD-cos (anneal LR+temp vs cosine LR)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Equal budget: KD 120 steps, seeds 0–2, eval_prompts (8).",
        "Kill if H-ANN ≤ KD-cos on teacher_lp.",
        "",
        "| family | mean teacher_lp | Δ vs KD-cos | Δ vs B2 | mean wall_ms | n |",
        "|--------|-----------------|-------------|---------|--------------|---|",
    ]
    for name in ("B2", "KD-cos", "H-ANN"):
        if name not in stats:
            continue
        st = stats[name]
        if name == "B2":
            d_c, d_b = "—", "—"
        elif name == "KD-cos":
            d_c, d_b = "—", f"{st['mean_lp'] - b2['mean_lp']:+.4f}"
        else:
            d_c, d_b = f"{d_cos:+.4f}", f"{d_b2:+.4f}"
        lines.append(
            f"| {name} | {st['mean_lp']:.4f} | {d_c} | {d_b} | "
            f"{st['mean_wall']:.0f} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Smoke promote was tentative; this run is the claim-facing check.",
            "",
            "Commands: `npm run nano:formal:hann` → "
            "`npm run nano:formal:hann:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hann/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hann-vs-kdcos.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
