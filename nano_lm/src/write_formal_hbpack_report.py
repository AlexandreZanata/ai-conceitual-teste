"""Render formal H-BPACK vs H-EARLY."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from bpack_ops import decide_hbpack


def _means(rows: list[dict]) -> dict[str, dict[str, float]]:
    bags: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        bags[r["family"]].append(r)
    out: dict[str, dict[str, float]] = {}
    for fam, items in bags.items():
        n = float(len(items))
        out[fam] = {
            "mean_lp": sum(float(x["teacher_mean_logprob"]) for x in items) / n,
            "mean_wall": sum(float(x["mean_wall_ms"]) for x in items) / n,
            "mean_tps": sum(float(x["mean_tokens_per_s"]) for x in items) / n,
            "mean_gflops": sum(float(x["mean_est_gflops"]) for x in items) / n,
            "n": n,
        }
    return out


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = _means(data["rows"])
    decision = decide_hbpack(stats)
    tip = stats.get("H-EARLY", {})
    lines = [
        "# Formal H-BPACK — SKIP + LAYB packs vs H-EARLY",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Fit≠eval. Freeze SKIP + LAYB vs serial EARLY (|Δlp|≤ε + wall/tok/s↑; "
        "SKIP GFLOPs ≤ EARLY·(1+δ)).",
        f"n_prompts={data.get('n_prompts')} chunk_size=`{data.get('chunk_size')}` "
        f"budgets=`{data.get('budgets')}` target_tokens=`{data.get('target_tokens')}`.",
        "",
        "| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | "
        "mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |",
        "|--------|-----------------|------|------------|---------|"
        "--------------|--------|-----------------|----------|---|",
    ]
    for fam in ("H-EARLY", "H-SKIP", "H-LAYB"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-EARLY":
            d1 = d2 = d3 = d4 = "—"
        else:
            d1 = f"{st['mean_lp'] - tip.get('mean_lp', float('nan')):+.4f}"
            d2 = f"{st['mean_tps'] - tip.get('mean_tps', float('nan')):+.1f}"
            d3 = f"{st['mean_wall'] - tip.get('mean_wall', float('nan')):+.0f}"
            d4 = f"{st['mean_gflops'] - tip.get('mean_gflops', float('nan')):+.3f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_tps']:.1f} | "
            f"{d2} | {st['mean_wall']:.0f} | {d3} | {st['mean_gflops']:.3f} | "
            f"{d4} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Card hygiene (Wave T). Throughput packs frozen vs tip EARLY.",
            "",
            "Commands: `npm run nano:formal:hbpack` → "
            "`npm run nano:formal:hbpack:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hbpack/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hbpack-vs-hearly.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
