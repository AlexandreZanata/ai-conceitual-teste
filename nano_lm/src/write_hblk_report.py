"""Render H-BLK smoke vs B3 markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from blk_ops import decide_hblk
from matrix_report_lib import mean_by_family


def render(smoke_path: Path, matrix_path: Path) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    # Prefer same-run B3 control from smoke over older matrix B3.
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    matrix_rows = [r for r in matrix.get("rows", []) if r.get("family") != "B3"]
    stats = mean_by_family(matrix_rows + smoke["rows"])
    s = stats.get("H-BLK", {})
    decision = decide_hblk(s, stats) if s else "needs H-BLK rows"
    b3 = stats.get("B3", {})
    d_lp = s.get("mean_lp", float("nan")) - b3.get("mean_lp", float("nan"))
    lines = [
        "# H-BLK smoke vs B3 (block-parallel decode)",
        "",
        "Sample block_size tokens per forward (no mid-block AR reconditioning).",
        "Kill if quality crash/drop vs B3 or no wall win.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs B3 | n |",
        "|--------|-----------------|--------------|------------|---|",
    ]
    for fam in ("B3", "H-BLK"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam == "B3" else f"{d_lp:+.4f}"
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
            "Commands: `npm run nano:blk` → `npm run nano:blk:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/blk_smoke.json"),
    )
    p.add_argument(
        "--matrix",
        type=Path,
        default=Path("results/nano-lm/student-matrix/matrix.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hblk-vs-b3.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
