"""Render formal H-CURL seq_lo ablation markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from curl_ops import (
    CURL_CONTROL,
    CURL_LOS,
    best_seq_lo,
    decide_hcurl,
    mean_lp_by_seq_lo,
)


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    lp_by_lo = mean_lp_by_seq_lo(data["rows"])
    decision = decide_hcurl(lp_by_lo)
    control = lp_by_lo.get(CURL_CONTROL, float("nan"))
    best = best_seq_lo(lp_by_lo) if lp_by_lo else None
    n_by: dict[int, int] = {}
    for r in data["rows"]:
        lo = int(r["seq_lo"])
        n_by[lo] = n_by.get(lo, 0) + 1
    lines = [
        "# Formal H-CURL — seq_lo ∈ {8,16,32} vs H-CUR (lo=16)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Equal budget: 120 steps, seeds 0–2, eval_prompts; n_stages=3.",
        "Kill if best seq_lo ≤ H-CUR (lo=16).",
        "",
        "| seq_lo | mean teacher_lp | Δ vs lo=16 | n |",
        "|--------|-----------------|------------|---|",
    ]
    for lo in CURL_LOS:
        if lo not in lp_by_lo:
            continue
        delta = "—" if lo == CURL_CONTROL else f"{lp_by_lo[lo] - control:+.4f}"
        lines.append(
            f"| {lo} | {lp_by_lo[lo]:.4f} | {delta} | {n_by.get(lo, 0)} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            f"Best seq_lo: {best}.",
            "",
            "Commands: `npm run nano:formal:curl` → "
            "`npm run nano:formal:curl:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hcurl/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hcurl-vs-hcur.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
