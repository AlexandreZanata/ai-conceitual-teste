"""Render H-NGRAM smoke vs B4 markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from matrix_report_lib import mean_by_family
from ngram_ops import decide_hngram


def render(smoke_path: Path, matrix_path: Path) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    kept = [r for r in matrix.get("rows", []) if r.get("family") != "H-NGRAM"]
    stats = mean_by_family(kept + smoke["rows"])
    s = stats.get("H-NGRAM", {})
    decision = decide_hngram(s, stats) if s else "needs H-NGRAM rows"
    b4 = stats.get("B4", {})
    d_lp = s.get("mean_lp", float("nan")) - b4.get("mean_lp", float("nan"))
    lines = [
        "# H-NGRAM smoke vs B4 (no-repeat n-gram decode)",
        "",
        "Grid-search no_repeat_ngram_size on B2 student; claim best on smoke prompts.",
        "Kill if quality < B4−ε or no wall win vs B4.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |",
        "|--------|-----------------|--------------|------------|---|",
    ]
    for fam in ("B4", "H-NGRAM"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam == "B4" else f"{d_lp:+.4f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | {delta} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:ngram` → `npm run nano:ngram:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/ngram_smoke.json"),
    )
    p.add_argument(
        "--matrix",
        type=Path,
        default=Path("results/nano-lm/student-matrix/matrix.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hngram-vs-b4.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
