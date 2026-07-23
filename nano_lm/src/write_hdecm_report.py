"""Render H-DECM smoke vs H-LAT2 and B4 markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from decm_ops import decide_hdecm
from matrix_report_lib import mean_by_family


def render(smoke_path: Path, matrix_path: Path) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    # Prefer same-run H-LAT2 control from smoke over older matrix H-LAT2.
    matrix_rows = [r for r in matrix.get("rows", []) if r.get("family") != "H-LAT2"]
    stats = mean_by_family(matrix_rows + smoke["rows"])
    s = stats.get("H-DECM", {})
    decision = decide_hdecm(s, stats) if s else "needs H-DECM rows"
    b4 = stats.get("B4", {})
    lines = [
        "# H-DECM smoke vs H-LAT2 + B4 (elite gene mixture)",
        "",
        "LAT2 search keeps top-M unique genes; claim picks completion by proxy.",
        "Kill if ≤ H-LAT2 or B4.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |",
        "|--------|-----------------|--------------|------------|---|",
    ]
    for fam in ("B4", "H-LAT2", "H-DECM"):
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
            "Commands: `npm run nano:decm` → `npm run nano:decm:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/decm_smoke.json"),
    )
    p.add_argument(
        "--matrix",
        type=Path,
        default=Path("results/nano-lm/student-matrix/matrix.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hdecm-vs-b4.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
