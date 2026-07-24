"""Render H-CURT smoke vs H-CUR markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from curt_ops import CURT_SEQ_LO, CURT_STAGES, decide_hcurt
from matrix_report_lib import mean_by_family


def render(smoke_path: Path, cur_path: Path, matrix_path: Path) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    cur = json.loads(cur_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    kept = [
        r
        for r in matrix.get("rows", [])
        if r.get("family") not in {"H-CURT", "H-CUR"}
    ]
    stats = mean_by_family(kept + cur["rows"] + smoke["rows"])
    s = stats.get("H-CURT", {})
    decision = decide_hcurt(s, stats) if s else "needs H-CURT rows"
    tip = stats.get("H-CUR", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    lines = [
        "# H-CURT smoke vs H-CUR (adopted tip n=5, lo=8)",
        "",
        f"Curriculum KD with n_stages={CURT_STAGES}, seq_lo={CURT_SEQ_LO} "
        "(formal-best knobs).",
        "Kill if ≤ H-CUR tip (n=3, lo=16).",
        "",
        "| family | mean teacher_lp | Δ vs tip | n |",
        "|--------|-----------------|----------|---|",
    ]
    for fam in ("H-CUR", "H-CURT"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam == "H-CUR" else f"{d_lp:+.4f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {delta} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:curt` → `npm run nano:curt:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/curt_smoke.json"),
    )
    p.add_argument(
        "--cur",
        type=Path,
        default=Path("results/nano-lm/student-matrix/cur_smoke.json"),
    )
    p.add_argument(
        "--matrix",
        type=Path,
        default=Path("results/nano-lm/student-matrix/matrix.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hcurt-vs-hcur.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.cur, args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
