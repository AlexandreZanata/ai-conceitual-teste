"""Render H-NGDM smoke vs H-NGRAM + H-DECM tips."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from matrix_report_lib import mean_by_family
from ngdm_ops import decide_hngdm, tip_max_lp


def render(
    smoke_path: Path,
    ngram_path: Path,
    decm_path: Path,
    matrix_path: Path,
) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    ngram = json.loads(ngram_path.read_text(encoding="utf-8"))
    decm = json.loads(decm_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    tip_fams = {"H-NGDM", "H-NGRAM", "H-DECM"}
    kept = [r for r in matrix.get("rows", []) if r.get("family") not in tip_fams]
    stats = mean_by_family(kept + ngram["rows"] + decm["rows"] + smoke["rows"])
    s = stats.get("H-NGDM", {})
    decision = decide_hngdm(s, stats) if s else "needs H-NGDM rows"
    max_lp = tip_max_lp(stats) or float("nan")
    lines = [
        "# H-NGDM smoke vs H-NGRAM × H-DECM (tip stack)",
        "",
        "Compose tip DECM gene (BoN n/T/top_p) + tip NGRAM size; dual vs max tip.",
        "Kill if lp < max(tips)−ε or wall ≥ min(tips).",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs max tip | n |",
        "|--------|-----------------|--------------|-----------------|---|",
    ]
    for fam in ("H-NGRAM", "H-DECM", "H-NGDM"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam != "H-NGDM" else f"{st['mean_lp'] - max_lp:+.4f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | {delta} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:ngdm` → `npm run nano:ngdm:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/ngdm_smoke.json"),
    )
    p.add_argument(
        "--ngram",
        type=Path,
        default=Path("results/nano-lm/student-matrix/ngram_smoke.json"),
    )
    p.add_argument(
        "--decm",
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
        default=Path("docs/results/nano-lm/hngdm-vs-tips.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.ngram, args.decm, args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
