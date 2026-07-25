"""Render H-ABS-PFB smoke — parent-fallback story-floor code BoN."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pfb_ops import decide_hpfb


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
        default=Path("results/nano-lm/student-matrix/hpfb_smoke.json"),
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hpfb-pfb.md"),
    )
    ap.add_argument("--formal", action="store_true")
    args = ap.parse_args()
    data = json.loads(args.inp.read_text(encoding="utf-8"))
    parent = data["parent_means"]
    pfb = data["pfb_means"]
    k = int(data.get("k", pfb.get("k", 4)))
    decision = data.get("decision") or decide_hpfb(
        parent_story=float(parent["mean_story_lp"]),
        parent_code=float(parent["mean_code_lp"]),
        pfb_story=float(pfb["mean_story_lp"]),
        pfb_code=float(pfb["mean_code_lp"]),
        mean_unique=float(pfb["mean_unique"]),
        mean_elig=float(pfb["mean_elig"]),
        mean_switch=float(pfb["mean_switch"]),
        k=k,
        identical=False,
    )
    title = "Formal H-ABS-PFB" if args.formal else "H-ABS-PFB smoke"
    lines = [
        f"# {title}",
        "",
        f"Decision: **{decision}**",
        "",
        f"Parent: `{data.get('parent', 'H-EARLY')}` · "
        f"k={k} · temp={data.get('pfb_temp')} · "
        f"mechanism: `{data.get('mechanism', '')}`",
        "",
        "| arm | mean story_lp | mean code_lp | mean wall_ms | "
        "mean unique | mean n_elig | mean switch | n |",
        "|-----|---------------|--------------|--------------|"
        "-------------|-------------|--------------|---|",
        _arm("H-EARLY n=1", parent),
        _arm(f"H-ABS-PFB k={k}", pfb),
        "",
        "Tips unchanged. Wave X ABS-PFB (CSAFE fix: parent fallback).",
        "",
        "Reproduce:",
        "`npm run nano:pfb` → `npm run nano:pfb:report`",
    ]
    if decision.startswith("PROMOTE"):
        lines.extend(
            [
                "",
                "Next formal:",
                "`npm run nano:formal:hpfb` → "
                "`npm run nano:formal:hpfb:report`",
            ]
        )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "decision": decision}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
