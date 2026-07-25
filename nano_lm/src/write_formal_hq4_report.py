"""Render formal H-Q4 vs H-DEPTH (CUDA int4 weight-only)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from q4_ops import decide_hq4


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
            "mean_bytes": sum(float(x.get("weight_bytes", 0)) for x in items) / n,
            "n": n,
        }
    return out


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = _means(data["rows"])
    s = stats.get("H-Q4", {})
    decision = decide_hq4(s, stats) if s else "needs H-Q4 rows"
    tip = stats.get("H-DEPTH", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_w = s.get("mean_wall", float("nan")) - tip.get("mean_wall", float("nan"))
    d_gf = s.get("mean_gflops", float("nan")) - tip.get("mean_gflops", float("nan"))
    d_b = s.get("mean_bytes", float("nan")) - tip.get("mean_bytes", float("nan"))
    lines = [
        "# Formal H-Q4 vs H-DEPTH (CUDA int4 weight-only)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Formal `HDEPTH_prun` + formal EARLY tip. Fit≠eval (`eval_prompts`).",
        "Weight-only int4 via `aten::_weight_int4pack_mm`. "
        "Kill if lp < DEPTH−ε or no wall win.",
        f"Backend: `{data.get('backend')}`; "
        f"`groupsize={data.get('groupsize')}`; "
        f"`tiles={data.get('tiles')}`; n_prompts={data.get('n_prompts')}.",
        "",
        "| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | "
        "mean est GFLOPs | Δ GFLOPs | mean weight_bytes | Δ bytes | n |",
        "|--------|-----------------|------|--------------|--------|"
        "-----------------|----------|-------------------|--------|---|",
    ]
    for fam in ("H-DEPTH", "H-Q4"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-DEPTH":
            d1 = d2 = d3 = d4 = "—"
        else:
            d1, d2, d3, d4 = (
                f"{d_lp:+.4f}",
                f"{d_w:+.0f}",
                f"{d_gf:+.3f}",
                f"{d_b:+.0f}",
            )
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_wall']:.0f} | "
            f"{d2} | {st['mean_gflops']:.3f} | {d3} | {st['mean_bytes']:.0f} | "
            f"{d4} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Note: systems util on DEPTH ckpt; tip genes unchanged.",
            "",
            "Commands: `npm run nano:formal:hq4` → "
            "`npm run nano:formal:hq4:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hq4/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/archive/formal-hq4-vs-hdepth.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
