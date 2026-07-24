"""Render H-COMP smoke vs H-EARLY (same genes; torch.compile)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from comp_ops import decide_hcomp
from matrix_report_lib import mean_by_family


def render(smoke_path: Path) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    stats = mean_by_family(smoke["rows"])
    s = stats.get("H-COMP", {})
    decision = decide_hcomp(s, stats) if s else "needs H-COMP rows"
    tip = stats.get("H-EARLY", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    lines = [
        "# H-COMP smoke — torch.compile on EARLY tip genes",
        "",
        "Same B2 ckpt + frozen EARLY genes; treatment uses",
        "`torch.compile(..., mode=reduce-overhead)` after warmup.",
        "Kill if quality < EARLY−ε or no wall win.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs EARLY | n |",
        "|--------|-----------------|--------------|---------------|---|",
    ]
    for fam in ("H-EARLY", "H-COMP"):
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
            "Commands: `npm run nano:comp` → `npm run nano:comp:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    root = Path("results/nano-lm/student-matrix")
    p.add_argument("--smoke", type=Path, default=root / "comp_smoke.json")
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hcomp-vs-hearly.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
