"""Render H-LAT2 smoke vs B4 markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from lat2_ops import decide_hlat2
from matrix_report_lib import mean_by_family


def render(smoke_path: Path, matrix_path: Path) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    stats = mean_by_family(matrix.get("rows", []) + smoke["rows"])
    s = stats.get("H-LAT2", {})
    decision = decide_hlat2(s, stats) if s else "needs H-LAT2 rows"
    b4 = stats.get("B4", {})
    d_lp = s.get("mean_lp", float("nan")) - b4.get("mean_lp", float("nan"))
    lines = [
        "# H-LAT2 smoke vs B4 (λ≥0.4 + n≤2 clamp)",
        "",
        "Stronger latency penalty than H-LAT; gene `n` clamped to ≤2.",
        "Kill if quality < B4−ε or no wall win vs B4.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |",
        "|--------|-----------------|--------------|------------|---|",
    ]
    for fam in ("B4", "H-LAT", "H-LAT2"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam == "B4" else f"{st['mean_lp'] - b4['mean_lp']:+.4f}"
        wall = st["mean_wall"]
        wall_s = f"{wall:.0f}" if wall == wall else "—"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {wall_s} | {delta} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            f"Δ H-LAT2 vs B4 lp: {d_lp:+.4f}.",
            "",
            "Commands: `npm run nano:lat2` → `npm run nano:lat2:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/lat2_smoke.json"),
    )
    p.add_argument(
        "--matrix",
        type=Path,
        default=Path("results/nano-lm/student-matrix/matrix.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hlat2-vs-b4.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
