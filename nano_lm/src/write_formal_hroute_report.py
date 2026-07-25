"""Render formal H-ROUTE vs H-GALL / H-GRAPHF single arms."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from route_ops import decide_hroute


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
    s = stats.get("H-ROUTE", {})
    decision = decide_hroute(s, stats) if s else "needs H-ROUTE rows"
    best_wall = min(
        stats.get("H-GALL", {}).get("mean_wall", float("inf")),
        stats.get("H-GRAPHF", {}).get("mean_wall", float("inf")),
    )
    best_lp = max(
        stats.get("H-GALL", {}).get("mean_lp", float("-inf")),
        stats.get("H-GRAPHF", {}).get("mean_lp", float("-inf")),
    )
    d_lp = s.get("mean_lp", float("nan")) - best_lp
    d_w = s.get("mean_wall", float("nan")) - best_wall
    lines = [
        "# Formal H-ROUTE vs H-GALL / H-GRAPHF (length-budget router)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Fit≠eval. Short→GALL; long→GRAPHF/KV. "
        "Gate: not dominated by either single arm on (lp, wall).",
        f"n_prompts={data.get('n_prompts')} chunk_size=`{data.get('chunk_size')}` "
        f"budgets=`{data.get('budgets')}` target_tokens=`{data.get('target_tokens')}`.",
        "",
        "| family | mean teacher_lp | Δ lp vs best | mean tok/s | "
        "mean wall_ms/prompt | Δ wall vs best | mean est GFLOPs | n |",
        "|--------|-----------------|--------------|------------|"
        "---------------------|----------------|-----------------|---|",
    ]
    for fam in ("H-GALL", "H-GRAPHF", "H-ROUTE"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam != "H-ROUTE":
            d1, d2 = "—", "—"
        else:
            d1, d2 = f"{d_lp:+.4f}", f"{d_w:+.0f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_tps']:.1f} | "
            f"{st['mean_wall']:.0f} | {d2} | {st['mean_gflops']:.3f} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Tip H-EARLY / H-SERVE unchanged. Length-budget router (Wave R).",
            "",
            "Commands: `npm run nano:formal:hroute` → "
            "`npm run nano:formal:hroute:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hroute/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hroute-vs-arms.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
