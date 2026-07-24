"""Render formal H-QG vs H-EARLY (quality-gated FLOP min)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from qg_ops import decide_hqg


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
            "empty_rate": sum(float(x.get("empty_rate", 0.0)) for x in items) / n,
            "n": n,
        }
    return out


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = _means(data["rows"])
    decision = decide_hqg(stats.get("H-QG", {}), stats)
    tip = stats.get("H-EARLY", {})
    hyp = stats.get("H-QG", {})
    d_lp = hyp.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_gf = hyp.get("mean_gflops", float("nan")) - tip.get("mean_gflops", float("nan"))
    lines = [
        "# Formal H-QG vs H-EARLY (quality-gated FLOP min)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Fit≠eval; hard reject lp < tip−ε; minimize GFLOPs among survivors.",
        "Kill if empty set, lp < EARLY−ε, or est_gflops ≥ EARLY tip.",
        "",
        "| family | mean teacher_lp | Δ lp | mean wall_ms | mean est GFLOPs | Δ GFLOPs | empty_rate | n |",
        "|--------|-----------------|------|--------------|-----------------|----------|------------|---|",
    ]
    for name in ("H-EARLY", "H-QG"):
        if name not in stats:
            continue
        st = stats[name]
        d1 = "—" if name == "H-EARLY" else f"{d_lp:+.4f}"
        d2 = "—" if name == "H-EARLY" else f"{d_gf:+.3f}"
        lines.append(
            f"| {name} | {st['mean_lp']:.4f} | {d1} | {st['mean_wall']:.0f} | "
            f"{st['mean_gflops']:.3f} | {d2} | {st['empty_rate']:.2f} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Commands: `npm run nano:formal:hqg` → `npm run nano:formal:hqg:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hqg/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hqg-vs-hearly.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
