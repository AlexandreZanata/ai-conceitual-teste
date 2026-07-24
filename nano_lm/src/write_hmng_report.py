"""Render H-MNG smoke vs H-MINP + H-NGRAM tips."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from matrix_report_lib import mean_by_family
from mng_ops import decide_hmng, tip_max_lp


def render(
    smoke_path: Path,
    minp_path: Path,
    ngram_path: Path,
    matrix_path: Path,
) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    minp = json.loads(minp_path.read_text(encoding="utf-8"))
    ngram = json.loads(ngram_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    tip_fams = {"H-MNG", "H-MINP", "H-NGRAM"}
    kept = [r for r in matrix.get("rows", []) if r.get("family") not in tip_fams]
    stats = mean_by_family(kept + minp["rows"] + ngram["rows"] + smoke["rows"])
    s = stats.get("H-MNG", {})
    decision = decide_hmng(s, stats) if s else "needs H-MNG rows"
    max_lp = tip_max_lp(stats) or float("nan")
    lines = [
        "# H-MNG smoke vs H-MINP × H-NGRAM (tip stack)",
        "",
        "Compose tip min_p + tip ngram_size in one AR decode; dual vs max tip.",
        "Kill if lp < max(tips)−ε or wall ≥ min(tips).",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs max tip | n |",
        "|--------|-----------------|--------------|-----------------|---|",
    ]
    for fam in ("H-MINP", "H-NGRAM", "H-MNG"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam != "H-MNG" else f"{st['mean_lp'] - max_lp:+.4f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | {delta} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:mng` → `npm run nano:mng:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/mng_smoke.json"),
    )
    p.add_argument(
        "--minp",
        type=Path,
        default=Path("results/nano-lm/student-matrix/minp_smoke.json"),
    )
    p.add_argument(
        "--ngram",
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
        default=Path("docs/results/nano-lm/hmng-vs-tips.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.minp, args.ngram, args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
