"""Render H-TMN smoke vs H-TYP + H-MINP tips."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from matrix_report_lib import mean_by_family
from tmn_ops import decide_htmn, tip_max_lp


def render(
    smoke_path: Path,
    typ_path: Path,
    minp_path: Path,
    matrix_path: Path,
) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    typ = json.loads(typ_path.read_text(encoding="utf-8"))
    minp = json.loads(minp_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    tip_fams = {"H-TMN", "H-TYP", "H-MINP"}
    kept = [r for r in matrix.get("rows", []) if r.get("family") not in tip_fams]
    stats = mean_by_family(kept + typ["rows"] + minp["rows"] + smoke["rows"])
    s = stats.get("H-TMN", {})
    decision = decide_htmn(s, stats) if s else "needs H-TMN rows"
    max_lp = tip_max_lp(stats) or float("nan")
    lines = [
        "# H-TMN smoke vs H-TYP × H-MINP (tip stack)",
        "",
        "Compose tip typ_mass + tip min_p in one AR decode; dual vs max tip.",
        "Kill if lp < max(tips)−ε or wall ≥ min(tips).",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs max tip | n |",
        "|--------|-----------------|--------------|-----------------|---|",
    ]
    for fam in ("H-TYP", "H-MINP", "H-TMN"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam != "H-TMN" else f"{st['mean_lp'] - max_lp:+.4f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | {delta} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:tmn` → `npm run nano:tmn:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/tmn_smoke.json"),
    )
    p.add_argument(
        "--typ",
        type=Path,
        default=Path("results/nano-lm/student-matrix/typ_smoke.json"),
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
        default=Path("docs/results/nano-lm/htmn-vs-tips.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.typ, args.minp, args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
