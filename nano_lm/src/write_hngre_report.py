"""Render H-NGRE smoke vs H-NGRAM + H-EARLY tips."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from matrix_report_lib import mean_by_family
from ngre_ops import decide_hngre, tip_max_lp


def render(
    smoke_path: Path,
    ngram_path: Path,
    early_path: Path,
    matrix_path: Path,
) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    ngram = json.loads(ngram_path.read_text(encoding="utf-8"))
    early = json.loads(early_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    tip_fams = {"H-NGRE", "H-NGRAM", "H-EARLY"}
    kept = [r for r in matrix.get("rows", []) if r.get("family") not in tip_fams]
    stats = mean_by_family(kept + ngram["rows"] + early["rows"] + smoke["rows"])
    s = stats.get("H-NGRE", {})
    decision = decide_hngre(s, stats) if s else "needs H-NGRE rows"
    max_lp = tip_max_lp(stats) or float("nan")
    lines = [
        "# H-NGRE smoke vs H-NGRAM × H-EARLY (tip stack)",
        "",
        "Compose tip EARLY gene + tip NGRAM size in one decode; dual vs max tip.",
        "Kill if lp < max(tips)−ε or wall ≥ min(tips).",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs max tip | n |",
        "|--------|-----------------|--------------|-----------------|---|",
    ]
    for fam in ("H-NGRAM", "H-EARLY", "H-NGRE"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam != "H-NGRE" else f"{st['mean_lp'] - max_lp:+.4f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | {delta} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:ngre` → `npm run nano:ngre:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/ngre_smoke.json"),
    )
    p.add_argument(
        "--ngram",
        type=Path,
        default=Path("results/nano-lm/student-matrix/ngram_smoke.json"),
    )
    p.add_argument(
        "--early",
        type=Path,
        default=Path("results/nano-lm/student-matrix/early_smoke.json"),
    )
    p.add_argument(
        "--matrix",
        type=Path,
        default=Path("results/nano-lm/student-matrix/matrix.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hngre-vs-tips.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.ngram, args.early, args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
