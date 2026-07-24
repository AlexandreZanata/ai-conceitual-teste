"""Render H-MPE smoke vs H-MINP markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from matrix_report_lib import mean_by_family
from mpe_ops import decide_hmpe


def render(smoke_path: Path, minp_path: Path, matrix_path: Path) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    minp = json.loads(minp_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    kept = [
        r
        for r in matrix.get("rows", [])
        if r.get("family") not in {"H-MPE", "H-MINP"}
    ]
    stats = mean_by_family(kept + minp["rows"] + smoke["rows"])
    s = stats.get("H-MPE", {})
    decision = decide_hmpe(s, stats) if s else "needs H-MPE rows"
    tip = stats.get("H-MINP", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    lines = [
        "# H-MPE smoke vs H-MINP (evolved min_p gene)",
        "",
        "Evolve min_p + T/top_p with latency-aware fitness; claim vs grid H-MINP.",
        "Kill if quality < tip−ε or no wall win vs H-MINP.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs tip | n |",
        "|--------|-----------------|--------------|-------------|---|",
    ]
    for fam in ("H-MINP", "H-MPE"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam == "H-MINP" else f"{d_lp:+.4f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | {delta} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:mpe` → `npm run nano:mpe:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/mpe_smoke.json"),
    )
    p.add_argument(
        "--minp",
        type=Path,
        default=Path("results/nano-lm/student-matrix/minp_smoke.json"),
    )
    p.add_argument(
        "--matrix",
        type=Path,
        default=Path("results/nano-lm/student-matrix/matrix.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hmpe-vs-hminp.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.minp, args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
