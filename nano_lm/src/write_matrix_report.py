"""Build slim kill/promote matrix markdown (champions + baselines)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from matrix_report_lib import decision, mean_by_family
from matrix_report_notes import GATES, NOTES

ORDER = [
    "B0",
    "B1",
    "B2",
    "B3",
    "B4",
    "H-SPEC",
    "H-DEC",
    "H-DECK",
    "H-DECKL",
    "H-POOL",
    "H-EARLY",
    "H-CUR",
    "H-CURL",
    "H-CURL2",
    "H-STAG",
]


def render(matrix_path: Path) -> str:
    data = json.loads(matrix_path.read_text(encoding="utf-8"))
    stats = mean_by_family(data["rows"])
    b2 = stats.get("B2", {}).get("mean_lp")
    wall_s = data.get("wall_s", "n/a")
    wall_line = (
        f"Wall clock (matrix): {wall_s:.1f}s"
        if isinstance(wall_s, (int, float))
        else f"Wall clock (matrix): {wall_s}"
    )
    lines = [
        "# Nano student — kill / promote matrix (champions)",
        "",
        f"Source: `{matrix_path}`",
        wall_line,
        "",
        "Primary metric: teacher mean log-prob of student completions.",
        "Full historical rows: `docs/results/nano-lm/archive/`.",
        *GATES,
        "",
        "| family | mean teacher_lp | Δ vs B2 | mean wall_ms | tok/s | n | decision |",
        "|--------|-----------------|---------|--------------|-------|---|-----------|",
    ]
    for fam in ORDER:
        if fam not in stats:
            continue
        s = stats[fam]
        delta = "" if b2 is None or fam == "B2" else f"{s['mean_lp'] - b2:+.4f}"
        wall = f"{s['mean_wall']:.0f}" if s["mean_wall"] == s["mean_wall"] else "—"
        tps = f"{s['mean_tps']:.1f}" if s["mean_tps"] == s["mean_tps"] else "—"
        lines.append(
            f"| {fam} | {s['mean_lp']:.4f} | {delta or '—'} | {wall} | {tps} | "
            f"{int(s['n'])} | {decision(fam, s, stats)} |"
        )
    lines.extend(["", *NOTES, ""])
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
        default=Path("docs/results/nano-lm/kill-promote-matrix.md"),
    )
    args = p.parse_args()
    text = render(args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
