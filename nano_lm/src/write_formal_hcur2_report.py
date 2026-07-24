"""Render formal H-CUR2 n_stages ablation markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cur2_ops import (
    CUR2_CONTROL,
    CUR2_STAGES,
    best_n_stages,
    decide_hcur2,
    mean_lp_by_stages,
)


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    lp_by_n = mean_lp_by_stages(data["rows"])
    decision = decide_hcur2(lp_by_n)
    control = lp_by_n.get(CUR2_CONTROL, float("nan"))
    best = best_n_stages(lp_by_n) if lp_by_n else None
    n_by: dict[int, int] = {}
    for r in data["rows"]:
        n = int(r["n_stages"])
        n_by[n] = n_by.get(n, 0) + 1
    lines = [
        "# Formal H-CUR2 — n_stages ∈ {2,3,4,5} vs H-CUR (n=3)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Equal budget: 120 steps, seeds 0–2, eval_prompts.",
        "Kill if best n ≤ H-CUR (n=3).",
        "",
        "| n_stages | mean teacher_lp | Δ vs n=3 | n |",
        "|----------|-----------------|----------|---|",
    ]
    for n in CUR2_STAGES:
        if n not in lp_by_n:
            continue
        delta = "—" if n == CUR2_CONTROL else f"{lp_by_n[n] - control:+.4f}"
        lines.append(
            f"| {n} | {lp_by_n[n]:.4f} | {delta} | {n_by.get(n, 0)} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            f"Best n_stages: {best}.",
            "",
            "Commands: `npm run nano:formal:cur2` → "
            "`npm run nano:formal:cur2:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hcur2/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hcur2-vs-hcur.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
