"""Render formal H-SYS vs CURL + tips@B2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from formal_ops import means_by_family
from sys_ops import SYS_EARLY, SYS_POOL, decide_hsys, decide_hsys_arm


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    stats = {
        name: {"mean_lp": st["lp"], "mean_wall": st["wall"], "n": st["n"]}
        for name, st in fam.items()
    }
    decision = decide_hsys(stats)
    lines = [
        "# Formal H-SYS — CURL lo=8 × EARLY|POOL",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Fit≠eval; free-lunch kill if ≤ CURL default or ≤ tip@B2.",
        "",
        "| family | mean teacher_lp | mean wall_ms | n |",
        "|--------|-----------------|--------------|---|",
    ]
    for name in ("H-CURL", "H-EARLY", "H-POOL", SYS_EARLY, SYS_POOL):
        if name not in stats:
            continue
        st = stats[name]
        lines.append(
            f"| {name} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | "
            f"{int(st['n'])} |"
        )
    lines.extend(["", "### Arm decisions", ""])
    for fam_name, tip in ((SYS_EARLY, "H-EARLY"), (SYS_POOL, "H-POOL")):
        if fam_name not in stats:
            continue
        lines.append(
            f"- **{fam_name}:** "
            f"{decide_hsys_arm(stats[fam_name], stats, tip_family=tip)}"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Commands: `npm run nano:formal:hsys` → "
            "`npm run nano:formal:hsys:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hsys/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hsys-vs-tips.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
