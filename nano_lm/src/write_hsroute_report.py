"""Render H-SROUTE smoke — ROUTE vs frozen SERVE."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from sroute_ops import decide_hsroute


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
    s = stats.get("H-SROUTE", {})
    decision = decide_hsroute(s, stats) if s else "needs H-SROUTE rows"
    tip = stats.get("H-SERVE", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_w = s.get("mean_wall", float("nan")) - tip.get("mean_wall", float("nan"))
    d_tps = s.get("mean_tps", float("nan")) - tip.get("mean_tps", float("nan"))
    lines = [
        "# H-SROUTE smoke — ROUTE vs frozen H-SERVE",
        "",
        "Full-stack head-to-head: length-budget ROUTE vs frozen SERVE recipe "
        "(best of GALL-speed / GRAPHF-quality). Kill if SERVE dominates on (lp, wall).",
        f"Prompt pack: `n_prompts={data.get('n_prompts')}`; "
        f"budgets=`{data.get('budgets')}` chunk=`{data.get('chunk_size')}` "
        f"target_tokens=`{data.get('target_tokens')}`; mode `{data.get('mode')}`.",
        "",
        "| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | "
        "mean wall_ms/prompt | Δ wall | mean est GFLOPs | n |",
        "|--------|-----------------|------|------------|---------|"
        "---------------------|--------|-----------------|---|",
    ]
    for fam in ("H-SERVE", "H-SROUTE"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-SERVE":
            d1 = d2 = d3 = "—"
        else:
            d1, d2, d3 = f"{d_lp:+.4f}", f"{d_tps:+.1f}", f"{d_w:+.0f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_tps']:.1f} | "
            f"{d2} | {st['mean_wall']:.0f} | {d3} | {st['mean_gflops']:.3f} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Tip H-EARLY / util H-SERVE / H-ROUTE unchanged unless PROMOTE "
            "replaces SERVE as serving default.",
            "",
            "Commands: `npm run nano:sroute` → `npm run nano:sroute:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/sroute_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hsroute-vs-hserve.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
