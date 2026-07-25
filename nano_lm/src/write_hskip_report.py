"""Render H-SKIP smoke — BAT→CHBAT skip CBAT."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from skip_ops import decide_hskip


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
    s = stats.get("H-SKIP", {})
    decision = decide_hskip(s, stats) if s else "needs H-SKIP rows"
    tip = stats.get("H-BAT", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_w = s.get("mean_wall", float("nan")) - tip.get("mean_wall", float("nan"))
    d_tps = s.get("mean_tps", float("nan")) - tip.get("mean_tps", float("nan"))
    d_gf = s.get("mean_gflops", float("nan")) - tip.get("mean_gflops", float("nan"))
    lines = [
        "# H-SKIP smoke — BAT→CHBAT skip CBAT (Pareto FLAG)",
        "",
        "Honest throughput path: CHB chunk (B=256) under BAT without claiming "
        "CBAT as a parent. CBAT shown for context (Pareto FLAG). "
        "Kill if no wall/tok/s win vs BAT or GFLOPs > BAT·(1+δ).",
        f"Prompt pack: `n_prompts={data.get('n_prompts')}`; "
        f"chunk=`{data.get('chunk_size')}` target_tokens=`{data.get('target_tokens')}`; "
        f"mode `{data.get('mode')}`.",
        "",
        "| family | mean teacher_lp | Δ lp vs BAT | mean tok/s | Δ tok/s | "
        "mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |",
        "|--------|-----------------|-------------|------------|---------|"
        "--------------|--------|-----------------|----------|---|",
    ]
    for fam in ("H-BAT", "H-CBAT", "H-SKIP"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam != "H-SKIP":
            d1 = d2 = d3 = d4 = "—"
        else:
            d1, d2, d3, d4 = (
                f"{d_lp:+.4f}",
                f"{d_tps:+.1f}",
                f"{d_w:+.0f}",
                f"{d_gf:+.3f}",
            )
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_tps']:.1f} | "
            f"{d2} | {st['mean_wall']:.0f} | {d3} | {st['mean_gflops']:.3f} | "
            f"{d4} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "On PROMOTE: card chain BAT→**CHBAT**/SKIP (CBAT demoted; code kept).",
            "",
            "Commands: `npm run nano:skip` → `npm run nano:skip:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/skip_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hskip-vs-hbat.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
