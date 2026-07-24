"""Render H-POOLF smoke vs H-POOL tip (FLOP dual gate)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from poolf_ops import decide_hpoolf


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
    s = stats.get("H-POOLF", {})
    decision = decide_hpoolf(s, stats) if s else "needs H-POOLF rows"
    tip = stats.get("H-POOL", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_gf = s.get("mean_gflops", float("nan")) - tip.get("mean_gflops", float("nan"))
    lines = [
        "# H-POOLF smoke — FLOP-aware POOL + n≤2 vs H-POOL",
        "",
        "Warm-start from POOL tip; search score = lp − λ·log1p(GFLOPs); n clamped ≤2.",
        "Kill if quality < POOL−ε or est_gflops ≥ POOL tip.",
        "",
        "| family | mean teacher_lp | Δ lp | mean wall_ms | mean est GFLOPs | Δ GFLOPs | n |",
        "|--------|-----------------|------|--------------|-----------------|----------|---|",
    ]
    for fam in ("H-POOL", "H-POOLF"):
        if fam not in stats:
            continue
        st = stats[fam]
        d1 = "—" if fam == "H-POOL" else f"{d_lp:+.4f}"
        d2 = "—" if fam == "H-POOL" else f"{d_gf:+.3f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_wall']:.0f} | "
            f"{st['mean_gflops']:.3f} | {d2} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:poolf` → `npm run nano:poolf:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/poolf_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hpoolf-vs-hpool.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
