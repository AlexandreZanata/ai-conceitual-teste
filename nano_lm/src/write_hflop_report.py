"""Render H-FLOP smoke — wall + tokens/s + est GFLOPs on B3 vs EARLY."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from flop_ops import decide_hflop


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
    decision = decide_hflop(stats)
    lines = [
        "# H-FLOP smoke — tokens/s + estimated GFLOPs alongside wall",
        "",
        "Instrumentation on B2 student: B3 AR vs frozen H-EARLY tip genes.",
        "Est. FLOPs = 2·N·Σ(seq_len) (uncached); kill gate = metrics present.",
        "Future speed claims should prefer GFLOPs when wall is GPU-noisy.",
        "",
        "| family | mean teacher_lp | mean wall_ms | mean tok/s | mean est GFLOPs | n |",
        "|--------|-----------------|--------------|------------|-----------------|---|",
    ]
    for fam in ("B3", "H-EARLY"):
        if fam not in stats:
            continue
        st = stats[fam]
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | "
            f"{st['mean_tps']:.1f} | {st['mean_gflops']:.3f} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:flop` → `npm run nano:flop:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/flop_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hflop-instrumentation.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
