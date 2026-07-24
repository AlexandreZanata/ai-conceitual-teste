"""Render formal H-PRUN vs H-STAG (magnitude prune + wall gate)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from prun_ops import decide_hprun_formal


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
            "mean_density": sum(float(x.get("density", 1.0)) for x in items) / n,
            "n": n,
        }
    return out


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = _means(data["rows"])
    s = stats.get("H-PRUN", {})
    decision = decide_hprun_formal(s, stats) if s else "needs H-PRUN rows"
    tip = stats.get("H-STAG", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_w = s.get("mean_wall", float("nan")) - tip.get("mean_wall", float("nan"))
    d_gf = s.get("mean_gflops", float("nan")) - tip.get("mean_gflops", float("nan"))
    lines = [
        "# Formal H-PRUN vs H-STAG (magnitude prune + recovery)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Formal STAG tip → 30% mag prune → masked KD recovery; claim with formal EARLY.",
        "Fit≠eval (`eval_prompts`). Formal gate: quality ≥ STAG−ε **and wall < STAG**",
        "(density FLOPs alone are not a real dual gate under dense CUDA kernels).",
        f"recover_steps={data.get('recover_steps')}; "
        f"sparsity_target={data.get('sparsity_target')}.",
        "",
        "| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | "
        "Δ GFLOPs | density | n |",
        "|--------|-----------------|------|--------------|--------|-----------------|"
        "----------|---------|---|",
    ]
    for fam in ("H-STAG", "H-PRUN"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-STAG":
            d1, d2, d3 = "—", "—", "—"
        else:
            d1, d2, d3 = f"{d_lp:+.4f}", f"{d_w:+.0f}", f"{d_gf:+.3f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_wall']:.0f} | {d2} | "
            f"{st['mean_gflops']:.3f} | {d3} | {st['mean_density']:.3f} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Note: density-scaled GFLOPs remain theoretical (dense kernels still run);",
            "formal promote requires mean wall win across seeds.",
            "",
            "Commands: `npm run nano:formal:hprun` → "
            "`npm run nano:formal:hprun:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hprun/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hprun-vs-hstag.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
