"""Render H-ABS-PFB2 smoke — K=2 PFB vs EARLY + PFB k=4 wall."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pfb2_ops import decide_hpfb2


def _arm(name: str, m: dict) -> str:
    return (
        f"| {name} | {m['mean_story_lp']:.4f} | {m['mean_code_lp']:.4f} | "
        f"{m['mean_wall_ms']:.0f} | {m.get('mean_unique', float('nan')):.3f} | "
        f"{m.get('mean_elig', float('nan')):.2f} | "
        f"{m.get('mean_switch', float('nan')):.2f} | {int(m['n'])} |"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--in",
        dest="inp",
        type=Path,
        default=Path("results/nano-lm/student-matrix/hpfb2_smoke.json"),
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hpfb2-pfb2.md"),
    )
    ap.add_argument("--formal", action="store_true")
    args = ap.parse_args()
    data = json.loads(args.inp.read_text(encoding="utf-8"))
    parent = data["parent_means"]
    pfb4 = data["pfb4_means"]
    pfb2 = data["pfb2_means"]
    decision = data.get("decision") or decide_hpfb2(
        parent_story=float(parent["mean_story_lp"]),
        parent_code=float(parent["mean_code_lp"]),
        pfb2_story=float(pfb2["mean_story_lp"]),
        pfb2_code=float(pfb2["mean_code_lp"]),
        mean_unique=float(pfb2["mean_unique"]),
        mean_elig=float(pfb2["mean_elig"]),
        mean_switch=float(pfb2["mean_switch"]),
        pfb2_wall=float(pfb2["mean_wall_ms"]),
        pfb4_wall=float(pfb4["mean_wall_ms"]),
        identical=False,
    )
    title = "Formal H-ABS-PFB2" if args.formal else "H-ABS-PFB2 smoke"
    lines = [
        f"# {title}",
        "",
        f"Decision: **{decision}**",
        "",
        f"Parent: `{data.get('parent', 'H-EARLY')}` · "
        f"k2={data.get('k2')} · k4={data.get('k4')} · "
        f"temp={data.get('pfb_temp')} · mechanism: `{data.get('mechanism', '')}`",
        "",
        "| arm | mean story_lp | mean code_lp | mean wall_ms | "
        "mean unique | mean n_elig | mean switch | n |",
        "|-----|---------------|--------------|--------------|"
        "-------------|-------------|--------------|---|",
        _arm("H-EARLY n=1", parent),
        _arm("H-ABS-PFB k=4", pfb4),
        _arm("H-ABS-PFB2 k=2", pfb2),
        "",
        "Tips unchanged. Wave X ABS-PFB2 (K=2 efficiency vs PFB).",
        "",
        "Reproduce:",
        "`npm run nano:pfb2` → `npm run nano:pfb2:report`",
    ]
    if decision.startswith("PROMOTE"):
        lines.extend(
            [
                "",
                "Next formal:",
                "`npm run nano:formal:hpfb2` → "
                "`npm run nano:formal:hpfb2:report`",
            ]
        )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "decision": decision}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
