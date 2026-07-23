"""Render H-NGE smoke vs H-NGRAM markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from matrix_report_lib import mean_by_family
from nge_ops import decide_hnge


def render(smoke_path: Path, ngram_path: Path, matrix_path: Path) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    ngram = json.loads(ngram_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    kept = [
        r
        for r in matrix.get("rows", [])
        if r.get("family") not in {"H-NGE", "H-NGRAM"}
    ]
    stats = mean_by_family(kept + ngram["rows"] + smoke["rows"])
    s = stats.get("H-NGE", {})
    decision = decide_hnge(s, stats) if s else "needs H-NGE rows"
    tip = stats.get("H-NGRAM", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    lines = [
        "# H-NGE smoke vs H-NGRAM (evolved ngram gene)",
        "",
        "Evolve ngram_size + T/top_p with latency-aware fitness; claim vs grid H-NGRAM.",
        "Kill if quality < tip−ε or no wall win vs H-NGRAM.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs tip | n |",
        "|--------|-----------------|--------------|-------------|---|",
    ]
    for fam in ("H-NGRAM", "H-NGE"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam == "H-NGRAM" else f"{d_lp:+.4f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | {delta} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:nge` → `npm run nano:nge:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/nge_smoke.json"),
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
        default=Path("docs/results/nano-lm/hnge-vs-hngram.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.ngram, args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
