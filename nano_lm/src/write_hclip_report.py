"""Render H-CLIP smoke vs B2 markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clip_ops import decide_hclip
from matrix_report_lib import mean_by_family


def render(smoke_path: Path, matrix_path: Path) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    kept = [r for r in matrix.get("rows", []) if r.get("family") != "H-CLIP"]
    stats = mean_by_family(kept + smoke["rows"])
    s = stats.get("H-CLIP", {})
    decision = decide_hclip(s, stats) if s else "needs H-CLIP rows"
    b2 = stats.get("B2", {})
    d_lp = s.get("mean_lp", float("nan")) - b2.get("mean_lp", float("nan"))
    lines = [
        "# H-CLIP smoke vs B2 (logit-clipped KD)",
        "",
        "KD after clamping student/teacher logits to [-clip, clip] (default 5).",
        "Kill if ≤ B2 on teacher_lp.",
        "",
        "| family | mean teacher_lp | Δ vs B2 | n |",
        "|--------|-----------------|---------|---|",
    ]
    for fam in ("B2", "H-CLIP"):
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
            "Commands: `npm run nano:clip` → `npm run nano:clip:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/clip_smoke.json"),
    )
    p.add_argument(
        "--matrix",
        type=Path,
        default=Path("results/nano-lm/student-matrix/matrix.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hclip-vs-b2.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
