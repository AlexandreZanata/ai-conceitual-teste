"""Render formal H-KVSEL vs H-EARLY (gated KV, dual budget)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from kvsel_ops import decide_hkvsel


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
            "mean_gflops": sum(float(x["mean_est_gflops"]) for x in items) / n,
            "n": n,
        }
    return out


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = _means(data["rows"])
    s = stats.get("H-KVSEL", {})
    decision = decide_hkvsel(s, stats) if s else "needs H-KVSEL rows"
    tip = stats.get("H-EARLY", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_w = s.get("mean_wall", float("nan")) - tip.get("mean_wall", float("nan"))
    d_gf = s.get("mean_gflops", float("nan")) - tip.get("mean_gflops", float("nan"))
    thrs = [
        r.get("best_gene", {}).get("kv_threshold")
        for r in data["rows"]
        if r.get("family") == "H-KVSEL"
    ]
    lines = [
        "# Formal H-KVSEL vs H-EARLY (gated KV)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared formal B2 + formal EARLY tip. Fit≠eval (`eval_prompts`).",
        f"KV iff `max_new > kv_threshold`; dual-budget mean `{data.get('budgets')}`.",
        "Kill if lp < EARLY−ε or no wall win.",
        f"n_prompts={data.get('n_prompts')}.",
        "",
        "| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | "
        "Δ GFLOPs | n |",
        "|--------|-----------------|------|--------------|--------|-----------------|"
        "----------|---|",
    ]
    for fam in ("H-EARLY", "H-KVSEL"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-EARLY":
            d1 = d2 = d3 = "—"
        else:
            d1, d2, d3 = f"{d_lp:+.4f}", f"{d_w:+.0f}", f"{d_gf:+.3f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_wall']:.0f} | {d2} | "
            f"{st['mean_gflops']:.3f} | {d3} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"Selected `kv_threshold` per seed: `{thrs}`.",
            "",
            f"**Decision:** {decision}",
            "",
            "Note: systems util — tip EARLY genes unchanged aside from threshold.",
            "",
            "Commands: `npm run nano:formal:hkvsel` → "
            "`npm run nano:formal:hkvsel:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hkvsel/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hkvsel-vs-hearly.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
