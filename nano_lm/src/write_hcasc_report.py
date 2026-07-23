"""Render H-CASC smoke vs B4 markdown (B4 from matrix.json)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from casc_ops import decide_hcasc
from matrix_report_lib import mean_by_family


def render(casc_path: Path, matrix_path: Path) -> str:
    casc = json.loads(casc_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    stats = mean_by_family(matrix.get("rows", []) + casc["rows"])
    s = stats.get("H-CASC", {})
    decision = decide_hcasc(s, stats) if s else "needs H-CASC rows"
    b4 = stats.get("B4", {})
    delta = s.get("mean_lp", float("nan")) - b4.get("mean_lp", float("nan"))
    lines = [
        "# H-CASC smoke vs B4 (proxy → mid teacher → full)",
        "",
        "Cascade: self-lp proxy → short teacher mid_k → full teacher final_k.",
        "Kill if no teacher-forward save vs full H-DEC or ≤ B4.",
        "",
        "| family | mean teacher_lp | Δ vs B4 | wall_save | n |",
        "|--------|-----------------|---------|-----------|---|",
    ]
    for fam in ("B4", "H-CASC"):
        if fam not in stats:
            continue
        st = stats[fam]
        d = "—" if fam == "B4" else f"{delta:+.4f}"
        save = "—" if fam == "B4" else ("yes" if st.get("wall_save", 0) > 0 else "no")
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d} | {save} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:casc` → `npm run nano:casc:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/casc_smoke.json"),
    )
    p.add_argument(
        "--matrix",
        type=Path,
        default=Path("results/nano-lm/student-matrix/matrix.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hcasc-vs-b4.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
