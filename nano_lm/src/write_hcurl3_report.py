"""Render H-CURL3 smoke micro seq_lo grid vs tip lo=6."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from curl3_ops import (
    CURL3_CONTROL,
    CURL3_LOS,
    best_seq_lo,
    decide_hcurl3,
    mean_lp_by_seq_lo,
)


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    lp_by_lo = mean_lp_by_seq_lo(data["rows"])
    decision = decide_hcurl3(lp_by_lo)
    tip = float(lp_by_lo.get(CURL3_CONTROL, float("nan")))
    best = best_seq_lo(lp_by_lo) if lp_by_lo else None
    n_by: dict[int, int] = {}
    for r in data["rows"]:
        lo = int(r["seq_lo"])
        n_by[lo] = n_by.get(lo, 0) + 1
    lines = [
        "# H-CURL3 smoke — micro seq_lo ∈ {5,6,7} vs tip lo=6",
        "",
        "Equal KD steps; n_stages=3 fixed; only seq_lo varies.",
        "Kill if best seq_lo ≤ H-CURL2 tip (lo=6).",
        "",
        "| seq_lo | mean teacher_lp | Δ vs lo=6 | n |",
        "|--------|-----------------|-----------|---|",
    ]
    for lo in CURL3_LOS:
        if lo not in lp_by_lo:
            continue
        d = lp_by_lo[lo] - tip
        d1 = "—" if lo == CURL3_CONTROL else f"{d:+.4f}"
        lines.append(
            f"| {lo} | {lp_by_lo[lo]:.4f} | {d1} | {n_by.get(lo, 0)} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            f"Best seq_lo: {best}.",
            "",
            "Commands: `npm run nano:curl3` → `npm run nano:curl3:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/curl3_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hcurl3-vs-hcurl2.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
