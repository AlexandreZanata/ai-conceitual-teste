"""Render H-CAP smoke vs H-POOL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cap_ops import decide_hcap
from matrix_report_lib import mean_by_family


def render(smoke_path: Path, pool_path: Path) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    pool = json.loads(pool_path.read_text(encoding="utf-8"))
    pool_rows = [r for r in pool["rows"] if r.get("family") == "H-POOL"]
    stats = mean_by_family(pool_rows + smoke["rows"])
    s = stats.get("H-CAP", {})
    decision = decide_hcap(s, stats) if s else "needs H-CAP rows"
    tip = stats.get("H-POOL", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    lines = [
        "# H-CAP smoke — hard max_new/n caps on H-POOL tip genes",
        "",
        "Freeze POOL tip; search max_new∈{8,12,16} with n≤2; claim best lat score.",
        "Kill if quality < POOL−ε or no wall save vs H-POOL.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs POOL | n |",
        "|--------|-----------------|--------------|--------------|---|",
    ]
    for fam in ("H-POOL", "H-CAP"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam == "H-POOL" else f"{d_lp:+.4f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | "
            f"{delta} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:cap` → `npm run nano:cap:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    root = Path("results/nano-lm/student-matrix")
    p.add_argument("--smoke", type=Path, default=root / "cap_smoke.json")
    p.add_argument("--pool", type=Path, default=root / "pool_smoke.json")
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hcap-vs-hpool.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.pool)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
