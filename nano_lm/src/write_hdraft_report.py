"""Render H-DRAFT smoke vs B4 markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from draft_ops import decide_hdraft
from matrix_report_lib import mean_by_family


def render(smoke_path: Path, matrix_path: Path) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    stats = mean_by_family(matrix.get("rows", []) + smoke["rows"])
    s = stats.get("H-DRAFT", {})
    decision = decide_hdraft(s, stats) if s else "needs H-DRAFT rows"
    b4 = stats.get("B4", {})
    d_lp = s.get("mean_lp", float("nan")) - b4.get("mean_lp", float("nan"))
    lines = [
        "# H-DRAFT smoke vs B4 (evolved speculative draft knobs)",
        "",
        "Evolve draft_len∈{1,2,4,8} + temp/top_p; student draft, teacher verify.",
        "Kill if quality < B4−ε or no wall win vs B4 (distinct from H-SPEC vs B3).",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |",
        "|--------|-----------------|--------------|------------|---|",
    ]
    for fam in ("B4", "H-SPEC", "H-DRAFT"):
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
            f"Δ H-DRAFT vs B4 lp: {d_lp:+.4f}.",
            "",
            "Commands: `npm run nano:draft` → `npm run nano:draft:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/draft_smoke.json"),
    )
    p.add_argument(
        "--matrix",
        type=Path,
        default=Path("results/nano-lm/student-matrix/matrix.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hdraft-vs-b4.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
