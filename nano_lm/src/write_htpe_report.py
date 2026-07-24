"""Render H-TPE smoke vs H-TYP markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from matrix_report_lib import mean_by_family
from tpe_ops import decide_htpe


def render(smoke_path: Path, typ_path: Path, matrix_path: Path) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    typ = json.loads(typ_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    kept = [
        r
        for r in matrix.get("rows", [])
        if r.get("family") not in {"H-TPE", "H-TYP"}
    ]
    stats = mean_by_family(kept + typ["rows"] + smoke["rows"])
    s = stats.get("H-TPE", {})
    decision = decide_htpe(s, stats) if s else "needs H-TPE rows"
    tip = stats.get("H-TYP", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    lines = [
        "# H-TPE smoke vs H-TYP (evolved typ_mass gene)",
        "",
        "Evolve typ_mass + T/top_p with latency-aware fitness; claim vs grid H-TYP.",
        "Kill if quality < tip−ε or no wall win vs H-TYP.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs tip | n |",
        "|--------|-----------------|--------------|-------------|---|",
    ]
    for fam in ("H-TYP", "H-TPE"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam == "H-TYP" else f"{d_lp:+.4f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | {delta} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:tpe` → `npm run nano:tpe:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/tpe_smoke.json"),
    )
    p.add_argument(
        "--typ",
        type=Path,
        default=Path("results/nano-lm/student-matrix/typ_smoke.json"),
    )
    p.add_argument(
        "--matrix",
        type=Path,
        default=Path("results/nano-lm/student-matrix/matrix.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/htpe-vs-htyp.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.typ, args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
