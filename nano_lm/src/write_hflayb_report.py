"""Render H-FLAYB smoke vs H-FCPOOLB (LAY under FCPOOLB batch)."""

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
    decision = decide_hflayb(s, stats) if s else "needs H-FLAYB rows"
    tip = stats.get("H-FCPOOLB", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_tps = s.get("mean_tps", float("nan")) - tip.get("mean_tps", float("nan"))
    d_w = s.get("mean_wall", float("nan")) - tip.get("mean_wall", float("nan"))
    d_gf = s.get("mean_gflops", float("nan")) - tip.get("mean_gflops", float("nan"))
    lays = [
        {
            "max_skip": r.get("best_gene", {}).get("max_skip"),
            "lay_conf": r.get("best_gene", {}).get("lay_conf"),
        }
        for r in data["rows"]
        if r.get("family") == "H-FLAYB"
    ]
    lines = [
        "# H-FLAYB smoke — LAY under FCPOOLB dual-budget batch",
        "",
        "Dual-budget mean: FCPOOLB path with batched BoN+LAY on the non-KV arm "
        f"(CPOOLB B=`{data.get('chunk_size')}` when `max_new > kv_threshold`).",
        "Frozen LAY tip `max_skip` / `lay_conf`. Kill if |Δlp| > ε vs H-FCPOOLB or "
        "no tok/s/wall win.",
        f"Prompt pack: smoke+fit elongated (`n_prompts={data.get('n_prompts')}`); "
        f"budgets=`{data.get('budgets')}` "
        f"target_tokens=`{data.get('target_tokens')}`; "
        f"mode `{data.get('mode', 'tip')}`.",
        f"Selected LAY knobs per seed: `{lays}`.",
        "",
        "| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | "
        "mean wall_ms/prompt | Δ wall | mean est GFLOPs | Δ GFLOPs | n |",
        "|--------|-----------------|------|------------|---------|"
        "---------------------|--------|-----------------|----------|---|",
    ]
    for fam in ("H-FCPOOLB", "H-FLAYB"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-FCPOOLB":
            d1 = d2 = d3 = d4 = "—"
        else:
            d1, d2, d3, d4 = (
                f"{d_lp:+.4f}",
                f"{d_tps:+.1f}",
                f"{d_w:+.0f}",
                f"{d_gf:+.3f}",
            )
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_tps']:.1f} | {d2} | "
            f"{st['mean_wall']:.0f} | {d3} | {st['mean_gflops']:.3f} | {d4} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Throughput util on FCPOOLB axis — tip POOL / util FCPOOLB / LAY unchanged.",
            "",
            "Commands: `npm run nano:flayb` → `npm run nano:flayb:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/flayb_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hflayb-vs-hfcpoolb.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
