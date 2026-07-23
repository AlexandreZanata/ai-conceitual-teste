"""Render H-DECK2 smoke top_k ablation markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from deck2_ops import DECK2_TOP_KS, best_top_k, decide_hdeck2, mean_lp_by_top_k


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    lp_by_k = mean_lp_by_top_k(data["rows"])
    decision = decide_hdeck2(lp_by_k)
    control = lp_by_k.get(2, float("nan"))
    best = best_top_k(lp_by_k) if lp_by_k else None
    lines = [
        "# H-DECK2 smoke — top_k ∈ {1,2,3} ablation vs H-DECK (k=2)",
        "",
        "Equal pop×gens; only teacher rescore width (`top_k`) varies.",
        "Kill if best k ≤ H-DECK (k=2).",
        "",
        "| top_k | mean teacher_lp | Δ vs k=2 | wall_save | n |",
        "|-------|-----------------|----------|-----------|---|",
    ]
    n_by_k: dict[int, int] = {}
    save_by_k: dict[int, bool] = {}
    for r in data["rows"]:
        k = int(r["top_k"])
        n_by_k[k] = n_by_k.get(k, 0) + 1
        save_by_k[k] = save_by_k.get(k, True) and bool(r.get("wall_save"))
    for k in DECK2_TOP_KS:
        if k not in lp_by_k:
            continue
        delta = "—" if k == 2 else f"{lp_by_k[k] - control:+.4f}"
        save = "yes" if save_by_k.get(k) else "no"
        lines.append(
            f"| {k} | {lp_by_k[k]:.4f} | {delta} | {save} | {n_by_k.get(k, 0)} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            f"Best top_k: {best}.",
            "",
            "Commands: `npm run nano:deck2` → `npm run nano:deck2:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/deck2_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hdeck2-vs-hdeck.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
