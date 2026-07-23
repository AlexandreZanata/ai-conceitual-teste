"""Render H-PARE smoke vs B4 markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from matrix_report_lib import mean_by_family
from pare_ops import decide_hpare


def render(smoke_path: Path, matrix_path: Path) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    stats = mean_by_family(matrix.get("rows", []) + smoke["rows"])
    # Attach mean front_n for decide_hpare.
    fronts = [float(r["front_n"]) for r in smoke["rows"]]
    if "H-PARE" in stats and fronts:
        stats["H-PARE"]["front_n"] = sum(fronts) / len(fronts)
    s = stats.get("H-PARE", {})
    decision = decide_hpare(s, stats) if s else "needs H-PARE rows"
    b4 = stats.get("B4", {})
    d_lp = s.get("mean_lp", float("nan")) - b4.get("mean_lp", float("nan"))
    lines = [
        "# H-PARE smoke vs B4 (Pareto archive + knee claim)",
        "",
        "DECK search archives teacher (lp, wall); claim = knee of front.",
        "Kill if empty front or ≤ B4 / dominated.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | front_n | n |",
        "|--------|-----------------|--------------|------------|---------|---|",
    ]
    for fam in ("B4", "H-PARE"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam == "B4" else f"{d_lp:+.4f}"
        wall = st["mean_wall"]
        wall_s = f"{wall:.0f}" if wall == wall else "—"
        fn = "—" if fam == "B4" else f"{st.get('front_n', float('nan')):.1f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {wall_s} | {delta} | {fn} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:pare` → `npm run nano:pare:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/pare_smoke.json"),
    )
    p.add_argument(
        "--matrix",
        type=Path,
        default=Path("results/nano-lm/student-matrix/matrix.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hpare-vs-b4.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
