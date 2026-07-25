"""Render H-ROUTE smoke vs H-GALL / H-GRAPHF single arms."""

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
    d_tps = s.get("mean_tps", float("nan")) - max(
        stats.get("H-GALL", {}).get("mean_tps", float("nan")),
        stats.get("H-GRAPHF", {}).get("mean_tps", float("nan")),
    )
    lines = [
        "# H-ROUTE smoke — short→GALL, long→GRAPHF vs single arms",
        "",
        "Controls: pure H-GALL and pure H-GRAPHF on the same long prompts / budgets. "
        "H-ROUTE uses GALL on short budgets and GRAPHF/KV on long (`max_new > thr`). "
        "Kill if dominated by either arm on (lp, wall).",
        f"Prompt pack: `n_prompts={data.get('n_prompts')}`; "
        f"budgets=`{data.get('budgets')}` chunk=`{data.get('chunk_size')}` "
        f"target_tokens=`{data.get('target_tokens')}`; "
        f"mode `{data.get('mode')}`.",
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
            f"**Decision: {decision}**",
            "",
            f"(Δ tok/s vs max arm: {d_tps:+.1f})",
            "",
            "Tip H-EARLY / H-SERVE unchanged unless PROMOTE. Length-budget router.",
            "",
            "Commands: `npm run nano:route` → `npm run nano:route:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/route_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hroute-vs-arms.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
