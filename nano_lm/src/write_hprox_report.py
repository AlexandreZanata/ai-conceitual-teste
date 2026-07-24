"""Render H-PROX smoke vs H-POOL (CE proxy fit; teacher claim)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from matrix_report_lib import mean_by_family
from prox_ops import decide_hprox


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = mean_by_family(data["rows"])
    s = stats.get("H-PROX", {})
    decision = decide_hprox(s, stats) if s else "needs H-PROX rows"
    tip = stats.get("H-POOL", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    fwd = {
        fam: sum(
            float(r.get("teacher_forwards", 0))
            for r in data["rows"]
            if r.get("family") == fam
        )
        / max(1, sum(1 for r in data["rows"] if r.get("family") == fam))
        for fam in ("H-POOL", "H-PROX")
    }
    lines = [
        "# H-PROX smoke — CE-only fit proxy vs H-POOL claim",
        "",
        "Warm-start like H-POOL; search ranks by student CE only",
        "(no teacher forwards in fit). Claim uses full teacher_lp.",
        "Kill if claim quality < POOL−ε.",
        "",
        "| family | mean teacher_lp | Δ vs POOL | mean wall_ms | mean fit teacher_fwd | n |",
        "|--------|-----------------|-----------|--------------|----------------------|---|",
    ]
    for fam in ("H-POOL", "H-PROX"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam == "H-POOL" else f"{d_lp:+.4f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {delta} | {st['mean_wall']:.0f} | "
            f"{fwd.get(fam, 0):.0f} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:prox` → `npm run nano:prox:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/prox_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hprox-vs-hpool.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
