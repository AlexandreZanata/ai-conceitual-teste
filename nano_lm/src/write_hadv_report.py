"""Render H-ADV smoke vs B2 markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from adv_ops import decide_hadv
from matrix_report_lib import mean_by_family


def render(smoke_path: Path, matrix_path: Path) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    kept = [r for r in matrix.get("rows", []) if r.get("family") != "H-ADV"]
    stats = mean_by_family(kept + smoke["rows"])
    s = dict(stats.get("H-ADV", {}))
    if "H-ADV" not in stats:
        decision = "needs H-ADV rows"
    else:
        s["mode_collapsed"] = (
            1.0
            if any(bool(r.get("mode_collapsed")) for r in smoke["rows"])
            else 0.0
        )
        decision = decide_hadv(s, stats)
    b2 = stats.get("B2", {})
    d_lp = s.get("mean_lp", float("nan")) - b2.get("mean_lp", float("nan"))
    lines = [
        "# H-ADV smoke vs B2 (weak discriminator + teacher judge)",
        "",
        "KD + weak top-k soft discriminator; claim metric remains teacher_lp.",
        "Kill if mode collapse (entropy drop) or ≤ B2.",
        "",
        "| family | mean teacher_lp | Δ vs B2 | mode_collapsed | n |",
        "|--------|-----------------|---------|----------------|---|",
    ]
    for fam in ("B2", "H-ADV"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam == "B2" else f"{d_lp:+.4f}"
        coll = (
            "—"
            if fam == "B2"
            else ("yes" if s.get("mode_collapsed", 0.0) > 0.0 else "no")
        )
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {delta} | {coll} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:adv` → `npm run nano:adv:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/adv_smoke.json"),
    )
    p.add_argument(
        "--matrix",
        type=Path,
        default=Path("results/nano-lm/student-matrix/matrix.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hadv-vs-b2.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
