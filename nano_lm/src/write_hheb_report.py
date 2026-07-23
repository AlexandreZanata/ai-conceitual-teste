"""Render H-HEB smoke vs B2 markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from heb_ops import decide_hheb
from matrix_report_lib import mean_by_family


def render(smoke_path: Path, matrix_path: Path) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    kept = [r for r in matrix.get("rows", []) if r.get("family") != "H-HEB"]
    stats = mean_by_family(kept + smoke["rows"])
    s = dict(stats.get("H-HEB", {}))
    if "H-HEB" not in stats:
        decision = "needs H-HEB rows"
    else:
        if any(float(r.get("diverged", 0.0)) > 0.0 for r in smoke["rows"]):
            s["diverged"] = 1.0
        else:
            s["diverged"] = 0.0
        decision = decide_hheb(s, stats)
    b2 = stats.get("B2", {})
    d_lp = s.get("mean_lp", float("nan")) - b2.get("mean_lp", float("nan"))
    lines = [
        "# H-HEB smoke vs B2 (local Hebbian MLP)",
        "",
        "KD + Hebbian update on last-layer `c_fc` (pre×post).",
        "Kill if diverged or ≤ B2.",
        "",
        "| family | mean teacher_lp | Δ vs B2 | n |",
        "|--------|-----------------|---------|---|",
    ]
    for fam in ("B2", "H-HEB"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam == "B2" else f"{d_lp:+.4f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {delta} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:heb` → `npm run nano:heb:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/heb_smoke.json"),
    )
    p.add_argument(
        "--matrix",
        type=Path,
        default=Path("results/nano-lm/student-matrix/matrix.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hheb-vs-b2.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
