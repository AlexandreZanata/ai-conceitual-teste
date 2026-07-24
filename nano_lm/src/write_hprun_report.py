"""Render H-PRUN smoke vs H-STAG tip (magnitude prune + EARLY claim)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from prun_ops import decide_hprun


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
    decision = decide_hprun(s, stats) if s else "needs H-PRUN rows"
    tip = stats.get("H-STAG", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_gf = s.get("mean_gflops", float("nan")) - tip.get("mean_gflops", float("nan"))
    spar = data.get("sparsity_target", 0.3)
    lines = [
        "# H-PRUN smoke — magnitude prune STAG + recovery vs tip",
        "",
        f"Prune Linear weights to ~{spar:.0%} sparsity, short masked KD recovery,",
        "claim with frozen EARLY genes. FLOPs scaled by density.",
        "Kill if quality < STAG−ε or no FLOP win vs STAG.",
        "",
        "| family | mean teacher_lp | Δ lp | mean wall_ms | mean est GFLOPs | Δ GFLOPs | density | n |",
        "|--------|-----------------|------|--------------|-----------------|----------|---------|---|",
    ]
    for fam in ("H-STAG", "H-PRUN"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-STAG":
            d1, d2 = "—", "—"
        else:
            d1, d2 = f"{d_lp:+.4f}", f"{d_gf:+.3f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_wall']:.0f} | "
            f"{st['mean_gflops']:.3f} | {d2} | {st['mean_density']:.3f} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Note: est. GFLOPs use density scaling (dense CUDA kernels still run).",
            "Formal deferred until sparse-kernel or wall dual gate looks real.",
            "",
            "Commands: `npm run nano:prun` → `npm run nano:prun:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/prun_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hprun-vs-hstag.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
