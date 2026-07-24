"""Render H-CACHE smoke vs H-EARLY + B4."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cache_ops import decide_hcache
from matrix_report_lib import mean_by_family


def render(smoke_path: Path, early_path: Path, matrix_path: Path) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    early = json.loads(early_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    stats = mean_by_family(
        matrix.get("rows", []) + early["rows"] + smoke["rows"]
    )
    s = stats.get("H-CACHE", {})
    decision = decide_hcache(s, stats) if s else "needs H-CACHE rows"
    tip = stats.get("H-EARLY", {})
    b4 = stats.get("B4", {})
    d_e = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_b = s.get("mean_lp", float("nan")) - b4.get("mean_lp", float("nan"))
    lines = [
        "# H-CACHE smoke — KV cache on H-EARLY tip genes",
        "",
        "Same EARLY tip genes on B2; decode with past_key_values.",
        "Kill if no wall save vs EARLY or quality/B4 dual fails.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs EARLY | Δ lp vs B4 | n |",
        "|--------|-----------------|--------------|---------------|------------|---|",
    ]
    for fam in ("B4", "H-EARLY", "H-CACHE"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-CACHE":
            d1, d2 = f"{d_e:+.4f}", f"{d_b:+.4f}"
        else:
            d1 = d2 = "—"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | "
            f"{d1} | {d2} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:cache` → `npm run nano:cache:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    root = Path("results/nano-lm/student-matrix")
    p.add_argument("--smoke", type=Path, default=root / "cache_smoke.json")
    p.add_argument("--early", type=Path, default=root / "early_smoke.json")
    p.add_argument("--matrix", type=Path, default=root / "matrix.json")
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hcache-vs-early.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.early, args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
