"""Render formal H-CURT vs H-CUR markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from curt_ops import CURT_SEQ_LO, CURT_STAGES, decide_hcurt
from formal_ops import means_by_family


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    stats = {
        name: {"mean_lp": st["lp"], "mean_wall": st["wall"], "n": st["n"]}
        for name, st in fam.items()
    }
    decision = decide_hcurt(stats.get("H-CURT", {}), stats)
    hyp = stats.get("H-CURT", {})
    tip = stats.get("H-CUR", {})
    d_lp = hyp.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    lines = [
        "# Formal H-CURT vs H-CUR (adopted tip n=5, lo=8)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        f"Equal budget: 120 steps; H-CURT uses n_stages={CURT_STAGES}, "
        f"seq_lo={CURT_SEQ_LO}.",
        "Kill if ≤ H-CUR tip.",
        "",
        "| family | mean teacher_lp | Δ vs tip | mean wall_ms | n |",
        "|--------|-----------------|----------|--------------|---|",
    ]
    for name in ("H-CUR", "H-CURT"):
        if name not in stats:
            continue
        st = stats[name]
        delta = "—" if name == "H-CUR" else f"{d_lp:+.4f}"
        lines.append(
            f"| {name} | {st['mean_lp']:.4f} | {delta} | "
            f"{st['mean_wall']:.0f} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Commands: `npm run nano:formal:curt` → "
            "`npm run nano:formal:curt:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hcurt/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hcurt-vs-hcur.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
