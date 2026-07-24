"""Render H-EAR2 smoke vs H-EARLY tip."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ear2_ops import decide_hear2
from matrix_report_lib import mean_by_family


def render(smoke_path: Path, early_path: Path) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    early = json.loads(early_path.read_text(encoding="utf-8"))
    stats = mean_by_family(early["rows"] + smoke["rows"])
    s = stats.get("H-EAR2", {})
    decision = decide_hear2(s, stats) if s else "needs H-EAR2 rows"
    tip = stats.get("H-EARLY", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    lines = [
        "# H-EAR2 smoke — widened early-exit gene vs H-EARLY",
        "",
        "Gene adds max_new + conf_metric∈{max_p,margin,entropy}; wider min_new.",
        "Kill if quality < EARLY−ε or no wall win vs H-EARLY.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs EARLY | n |",
        "|--------|-----------------|--------------|---------------|---|",
    ]
    for fam in ("H-EARLY", "H-EAR2"):
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
            "Commands: `npm run nano:ear2` → `npm run nano:ear2:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    root = Path("results/nano-lm/student-matrix")
    p.add_argument("--smoke", type=Path, default=root / "ear2_smoke.json")
    p.add_argument("--early", type=Path, default=root / "early_smoke.json")
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hear2-vs-hearly.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.early)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
