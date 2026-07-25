"""Render H-QPACK smoke — FLAYB vs POOL."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from qpack_ops import decide_hqpack


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
    s = stats.get("H-FLAYB", {})
    decision = decide_hqpack(s, stats) if s else "needs H-FLAYB rows"
    tip = stats.get("H-POOL", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_w = s.get("mean_wall", float("nan")) - tip.get("mean_wall", float("nan"))
    d_tps = s.get("mean_tps", float("nan")) - tip.get("mean_tps", float("nan"))
    lines = [
        "# H-QPACK smoke — FLAYB quality pack vs tip H-POOL",
        "",
        "Card hygiene (quality axis): freeze FLAYB against serial POOL on shared "
        "budgets. Kill if lp < POOL−ε or no wall/tok/s win.",
        f"Prompt pack: `n_prompts={data.get('n_prompts')}`; "
        f"budgets=`{data.get('budgets')}` chunk=`{data.get('chunk_size')}` "
        f"target_tokens=`{data.get('target_tokens')}`; mode `{data.get('mode')}`.",
        "",
        "| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | "
        "mean wall_ms | Δ wall | mean est GFLOPs | n |",
        "|--------|-----------------|------|------------|---------|"
        "--------------|--------|-----------------|---|",
    ]
    for fam in ("H-POOL", "H-FLAYB"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-POOL":
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
            "Tip H-POOL unchanged. Quality pack: FLAYB.",
            "",
            "Commands: `npm run nano:qpack` → `npm run nano:qpack:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/qpack_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hqpack-vs-hpool.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
