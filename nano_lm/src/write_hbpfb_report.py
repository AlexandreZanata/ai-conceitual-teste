"""Render H-ABS-BPFB smoke — PFB K=2 on bitcoin pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from bpfb_ops import decide_hbpfb


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
        default=Path("results/nano-lm/student-matrix/hbpfb_smoke.json"),
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hbpfb-bpfb.md"),
    )
    ap.add_argument("--formal", action="store_true")
    args = ap.parse_args()
    data = json.loads(args.inp.read_text(encoding="utf-8"))
    parent = data["parent_means"]
    bpfb4 = data["bpfb4_means"]
    bpfb2 = data["bpfb2_means"]
    decision = data.get("decision") or decide_hbpfb(
        parent_story=float(parent["mean_story_lp"]),
        parent_code=float(parent["mean_code_lp"]),
        bpfb_story=float(bpfb2["mean_story_lp"]),
        bpfb_code=float(bpfb2["mean_code_lp"]),
        mean_unique=float(bpfb2["mean_unique"]),
        mean_elig=float(bpfb2["mean_elig"]),
        mean_switch=float(bpfb2["mean_switch"]),
        bpfb_wall=float(bpfb2["mean_wall_ms"]),
        bpfb4_wall=float(bpfb4["mean_wall_ms"]),
        identical=False,
    )
    title = (
        "Formal H-ABS-BPFB — PFB K=2 on BTC; wall↓ vs k=4"
        if args.formal
        else "H-ABS-BPFB smoke — PFB K=2 on bitcoin pack; wall↓ vs k=4"
    )
    lines = [
        f"# {title}",
        "",
        f"Decision: **{decision}**",
        "",
        f"Parent: `{data.get('parent', 'H-EARLY-BTC')}` · "
        f"k2={data.get('k2')} · k4={data.get('k4')} · "
        f"temp={data.get('pfb_temp')} · pack=`{data.get('pack', {})}` · "
        f"mechanism: `{data.get('mechanism', '')}`",
        "",
        "| arm | mean story_lp | mean code_lp | mean wall_ms | "
        "mean unique | mean n_elig | mean switch | n |",
        "|-----|---------------|--------------|--------------|"
        "-------------|-------------|--------------|---|",
        _arm("H-EARLY-BTC n=1", parent),
        _arm("H-ABS-BPFB k=4", bpfb4),
        _arm("H-ABS-BPFB k=2", bpfb2),
        "",
        "Tips unchanged. Wave X ABS-BPFB (PFB2→BTC domain transfer).",
        "",
        "Reproduce:",
        "`npm run nano:bpfb` → `npm run nano:bpfb:report`",
    ]
    if decision.startswith("PROMOTE"):
        lines.extend(
            [
                "",
                "Next formal:",
                "`npm run nano:formal:hbpfb` → "
                "`npm run nano:formal:hbpfb:report`",
            ]
        )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "decision": decision}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
