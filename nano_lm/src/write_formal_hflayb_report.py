"""Render formal H-FLAYB vs H-FCPOOLB (LAY under FCPOOLB batch)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from flayb_ops import decide_hflayb


def _means(rows: list[dict]) -> dict[str, dict[str, float]]:
    bags: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        bags[r["family"]].append(r)
    out: dict[str, dict[str, float]] = {}
    for fam, items in bags.items():
        n = float(len(items))
        out[fam] = {
            "mean_lp": sum(float(x["teacher_mean_logprob"]) for x in items) / n,
            "mean_tps": sum(float(x["mean_tokens_per_s"]) for x in items) / n,
            "mean_wall": sum(float(x["mean_wall_ms"]) for x in items) / n,
            "mean_gflops": sum(float(x["mean_est_gflops"]) for x in items) / n,
            "n": n,
        }
    return out


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = _means(data["rows"])
    s = stats.get("H-FLAYB", {})
    decision = decide_hflayb(s, stats) if s else "needs H-FLAYB rows"
    tip = stats.get("H-FCPOOLB", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_tps = s.get("mean_tps", float("nan")) - tip.get("mean_tps", float("nan"))
    d_w = s.get("mean_wall", float("nan")) - tip.get("mean_wall", float("nan"))
    lays = [
        {
            "max_skip": r.get("best_gene", {}).get("max_skip"),
            "lay_conf": r.get("best_gene", {}).get("lay_conf"),
        }
        for r in data["rows"]
        if r.get("family") == "H-FLAYB"
    ]
    lines = [
        "# Formal H-FLAYB vs H-FCPOOLB (LAY under FCPOOLB batch)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared formal B2 + POOL + LAY + KVSEL. Fit≠eval.",
        "Dual-budget FCPOOLB with batched BoN+LAY on non-KV arm vs tip FCPOOLB.",
        f"Mode: `{data.get('mode')}`. Kill if |Δlp| > ε or no tok/s/wall win.",
        f"n_prompts={data.get('n_prompts')} chunk_size=`{data.get('chunk_size')}` "
        f"budgets=`{data.get('budgets')}` "
        f"target_tokens=`{data.get('target_tokens')}`.",
        f"Selected LAY knobs per seed: `{lays}`.",
        "",
        "| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | "
        "mean wall_ms/prompt | Δ wall | n |",
        "|--------|-----------------|------|------------|---------|"
        "---------------------|--------|---|",
    ]
    for fam in ("H-FCPOOLB", "H-FLAYB"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-FCPOOLB":
            d1 = d2 = d3 = "—"
        else:
            d1, d2, d3 = f"{d_lp:+.4f}", f"{d_tps:+.1f}", f"{d_w:+.0f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_tps']:.1f} | {d2} | "
            f"{st['mean_wall']:.0f} | {d3} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Throughput util on FCPOOLB axis — does not replace H-POOL / H-FCPOOLB / H-LAY.",
            "",
            "Commands: `npm run nano:formal:hflayb` → "
            "`npm run nano:formal:hflayb:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hflayb/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hflayb-vs-hfcpoolb.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
