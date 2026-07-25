"""Render H-ABS-GPFB4 smoke — PFB K=4 under GENC genome."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from gpfb4_ops import decide_hgpfb4


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
        default=Path("results/nano-lm/student-matrix/hgpfb4_smoke.json"),
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hgpfb4-gpfb4.md"),
    )
    ap.add_argument("--formal", action="store_true")
    args = ap.parse_args()
    data = json.loads(args.inp.read_text(encoding="utf-8"))
    parent = data["parent_means"]
    g4 = data["gpfb4_means"]
    k = int(data.get("k", g4.get("k", 4)))
    decision = data.get("decision") or decide_hgpfb4(
        parent_story=float(parent["mean_story_lp"]),
        parent_code=float(parent["mean_code_lp"]),
        gpfb4_story=float(g4["mean_story_lp"]),
        gpfb4_code=float(g4["mean_code_lp"]),
        mean_unique=float(g4["mean_unique"]),
        mean_elig=float(g4["mean_elig"]),
        mean_switch=float(g4["mean_switch"]),
        k=k,
        identical=False,
    )
    title = (
        "Formal H-ABS-GPFB4 — GENC∘PFB K=4"
        if args.formal
        else "H-ABS-GPFB4 smoke — GENC∘PFB K=4"
    )
    genes = data.get("best_genes") or []
    gene0 = genes[0] if genes else {}
    lines = [
        f"# {title}",
        "",
        f"Decision: **{decision}**",
        "",
        f"Parent: `{data.get('parent', 'H-GENC-serial')}` · "
        f"k={k} · temp={data.get('pfb_temp')} · "
        f"gene0=`{gene0}` · "
        f"mechanism: `{data.get('mechanism', '')}`",
        "",
        "| arm | mean story_lp | mean code_lp | mean wall_ms | "
        "mean unique | mean n_elig | mean switch | n |",
        "|-----|---------------|--------------|--------------|"
        "-------------|-------------|--------------|---|",
        _arm("H-GENC-serial n=1", parent),
        _arm(f"H-ABS-GPFB4 k={k}", g4),
        "",
        "Tips unchanged. Wave X ABS-GPFB4 (GPFB K=2 KILL → separate k=4 ID).",
        "",
        "Reproduce:",
        "`npm run nano:gpfb4` → `npm run nano:gpfb4:report`",
    ]
    if decision.startswith("PROMOTE") and not args.formal:
        lines.extend(
            [
                "",
                "Next formal:",
                "`npm run nano:formal:hgpfb4` → "
                "`npm run nano:formal:hgpfb4:report`",
            ]
        )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "decision": decision}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
