"""Render H-BUD smoke vs H-EARLY tip."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from bud_ops import decide_hbud
from matrix_report_lib import mean_by_family


def render(smoke_path: Path, early_path: Path) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    early = json.loads(early_path.read_text(encoding="utf-8"))
    stats = mean_by_family(early["rows"] + smoke["rows"])
    s = stats.get("H-BUD", {})
    decision = decide_hbud(s, stats) if s else "needs H-BUD rows"
    tip = stats.get("H-EARLY", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    lines = [
        "# H-BUD smoke — EARLY exit + max_new as one gene",
        "",
        "Warm-start from EARLY tip; co-evolve max_new with exit knobs.",
        "Kill if dominated by H-EARLY on (lp, wall) or quality < EARLY−ε.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs EARLY | n |",
        "|--------|-----------------|--------------|---------------|---|",
    ]
    for fam in ("H-EARLY", "H-BUD"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam == "H-EARLY" else f"{d_lp:+.4f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | "
            f"{delta} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:bud` → `npm run nano:bud:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    root = Path("results/nano-lm/student-matrix")
    p.add_argument("--smoke", type=Path, default=root / "bud_smoke.json")
    p.add_argument("--early", type=Path, default=root / "early_smoke.json")
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hbud-vs-hearly.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.early)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
