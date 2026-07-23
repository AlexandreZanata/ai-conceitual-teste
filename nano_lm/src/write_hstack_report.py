"""Render H-STACK smoke vs H-EARLY + H-DECM tips."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from matrix_report_lib import mean_by_family
from stack_ops import decide_hstack


def _load_rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return list(json.loads(path.read_text(encoding="utf-8")).get("rows", []))


def render(
    stack_path: Path, early_path: Path, decm_path: Path, matrix_path: Path
) -> str:
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    rows = (
        list(matrix.get("rows", []))
        + _load_rows(early_path)
        + _load_rows(decm_path)
        + _load_rows(stack_path)
    )
    # Prefer smoke tip rows over older matrix duplicates.
    tip_fams = {"H-EARLY", "H-DECM", "H-STACK"}
    base = [r for r in rows if r.get("family") not in tip_fams]
    tips = [r for r in rows if r.get("family") in tip_fams]
    stats = mean_by_family(base + tips)
    s = stats.get("H-STACK", {})
    decision = decide_hstack(s, stats) if s else "needs H-STACK rows"
    early = stats.get("H-EARLY", {})
    decm = stats.get("H-DECM", {})
    max_lp = max(early.get("mean_lp", float("nan")), decm.get("mean_lp", float("nan")))
    lines = [
        "# H-STACK smoke vs H-EARLY × H-DECM (early mixture claim)",
        "",
        "Evolve early-exit genes; elite mixture claim by student proxy.",
        "Kill if ≤ max tip quality or no wall win vs faster tip.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs max tip | n |",
        "|--------|-----------------|--------------|-----------------|---|",
    ]
    for fam in ("H-EARLY", "H-DECM", "H-STACK"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam != "H-STACK" else f"{st['mean_lp'] - max_lp:+.4f}"
        wall = st["mean_wall"]
        wall_s = f"{wall:.0f}" if wall == wall else "—"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {wall_s} | {delta} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:stack` → `npm run nano:stack:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--stack",
        type=Path,
        default=Path("results/nano-lm/student-matrix/stack_smoke.json"),
    )
    p.add_argument(
        "--early",
        type=Path,
        default=Path("results/nano-lm/student-matrix/early_smoke.json"),
    )
    p.add_argument(
        "--decm",
        type=Path,
        default=Path("results/nano-lm/student-matrix/decm_smoke.json"),
    )
    p.add_argument(
        "--matrix",
        type=Path,
        default=Path("results/nano-lm/student-matrix/matrix.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hstack-vs-tips.md"),
    )
    args = p.parse_args()
    text = render(args.stack, args.early, args.decm, args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
