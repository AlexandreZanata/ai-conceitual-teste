"""Render H-STAG smoke n_stages grid vs tip stages=3."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from stag_ops import (
    STAG_CONTROL,
    STAG_STAGES,
    best_stages,
    decide_hstag,
    mean_lp_by_stages,
)


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    lp_by = mean_lp_by_stages(data["rows"])
    decision = decide_hstag(lp_by)
    tip = float(lp_by.get(STAG_CONTROL, float("nan")))
    best = best_stages(lp_by) if lp_by else None
    n_by: dict[int, int] = {}
    for r in data["rows"]:
        st = int(r["n_stages"])
        n_by[st] = n_by.get(st, 0) + 1
    lines = [
        "# H-STAG smoke — n_stages ∈ {2,3,4} under seq_lo=6",
        "",
        "Equal KD steps; seq_lo=6 fixed; only n_stages varies.",
        "Kill if best n_stages ≤ H-CURL2 tip (stages=3).",
        "",
        "| n_stages | mean teacher_lp | Δ vs stages=3 | n |",
        "|----------|-----------------|---------------|---|",
    ]
    for st in STAG_STAGES:
        if st not in lp_by:
            continue
        d = lp_by[st] - tip
        d1 = "—" if st == STAG_CONTROL else f"{d:+.4f}"
        lines.append(f"| {st} | {lp_by[st]:.4f} | {d1} | {n_by.get(st, 0)} |")
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            f"Best n_stages: {best}.",
            "",
            "Commands: `npm run nano:stag` → `npm run nano:stag:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/stag_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hstag-vs-hcurl2.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
