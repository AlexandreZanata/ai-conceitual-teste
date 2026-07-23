"""Render H-LAT smoke vs B4 (/ H-DEC) markdown from matrix or lat_smoke."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from lat_ops import decide_hlat
from matrix_report_lib import mean_by_family


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = mean_by_family(data["rows"])
    s = stats.get("H-LAT", {})
    decision = decide_hlat(s, stats) if s else "needs H-LAT rows"
    b4 = stats.get("B4", {})
    hdec = stats.get("H-DEC", {})
    d_b4 = s.get("mean_lp", float("nan")) - b4.get("mean_lp", float("nan"))
    lines = [
        "# H-LAT smoke vs B4 (latency-aware decode genes)",
        "",
        "Fitness during search: `lp − λ·log1p(wall_ms)` on frozen B2 student.",
        "Claim metric: raw teacher_lp + mean_wall_ms on eval prompts.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |",
        "|--------|-----------------|--------------|------------|---|",
    ]
    for fam in ("B4", "H-DEC", "H-LAT"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam == "B4" else f"{st['mean_lp'] - b4.get('mean_lp', float('nan')):+.4f}"
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
            f"Δ H-LAT vs B4 lp: {d_b4:+.4f}.",
            (
                f"H-DEC present: lp={hdec.get('mean_lp', float('nan')):.4f}."
                if hdec
                else "H-DEC row missing — compare mainly vs B4."
            ),
            "",
            "Commands: `npm run nano:lat` → `npm run nano:matrix:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--matrix",
        type=Path,
        default=Path("results/nano-lm/student-matrix/matrix.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hlat-vs-b4.md"),
    )
    args = p.parse_args()
    text = render(args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
