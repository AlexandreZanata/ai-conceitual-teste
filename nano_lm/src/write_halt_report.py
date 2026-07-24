"""Render H-ALT smoke vs H-EARLY (alternate full/shallow depth)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from alt_ops import decide_halt


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
    s = stats.get("H-ALT", {})
    decision = decide_halt(s, stats) if s else "needs H-ALT rows"
    tip = stats.get("H-EARLY", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_w = s.get("mean_wall", float("nan")) - tip.get("mean_wall", float("nan"))
    d_gf = s.get("mean_gflops", float("nan")) - tip.get("mean_gflops", float("nan"))
    lines = [
        "# H-ALT smoke — alternate full vs shallow depth under EARLY",
        "",
        "Search `alt_period` / `start_shallow` / `shallow_skip` with frozen EARLY tip.",
        "Kill if lp < EARLY−ε or no wall/GFLOPs win vs EARLY.",
        f"Search λ={data.get('lam')} (FLOP-aware).",
        "",
        "| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | "
        "Δ GFLOPs | n |",
        "|--------|-----------------|------|--------------|--------|-----------------|"
        "----------|---|",
    ]
    for fam in ("H-EARLY", "H-ALT"):
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
            f"**Decision: {decision}**",
            "",
            "Note: orthogonal to conf-gated H-LAY; forced shallow on alternate steps.",
            "Lesson: wall/GFLOPs can drop while teacher_lp falls below EARLY−ε.",
            "",
            "Commands: `npm run nano:alt` → `npm run nano:alt:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/alt_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/halt-vs-hearly.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
