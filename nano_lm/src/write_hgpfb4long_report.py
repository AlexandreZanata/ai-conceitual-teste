"""Render H-GPFB4-LONG smoke/formal — GPFB4 K=4 on ROLL vs serial."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from gpfb4long_ops import decide_hgpfb4long


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
        default=Path("results/nano-lm/student-matrix/hgpfb4long_smoke.json"),
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hgpfb4long-gpfb4long.md"),
    )
    ap.add_argument("--formal", action="store_true")
    args = ap.parse_args()
    data = json.loads(args.inp.read_text(encoding="utf-8"))
    parent = data["parent_means"]
    long_m = data.get("long_means") or data.get("gpfb4_means") or {}
    full_m = data.get("full_means") or {}
    k = int(data.get("k", 4))
    decision = data.get("decision") or decide_hgpfb4long(
        parent_story=float(parent["mean_story_lp"]),
        parent_code=float(parent["mean_code_lp"]),
        long_story=float(long_m["mean_story_lp"]),
        long_code=float(long_m["mean_code_lp"]),
        mean_unique=float(long_m["mean_unique"]),
        mean_elig=float(long_m["mean_elig"]),
        mean_switch=float(long_m["mean_switch"]),
        k=k,
        identical=False,
        l_eff=float(data.get("l_eff", 0)),
        mean_active=float(data.get("mean_active", 0)),
        wall_roll=float(long_m["mean_wall_ms"]),
        wall_full=float(full_m.get("mean_wall_ms", long_m["mean_wall_ms"])),
    )
    title = (
        "Formal H-GPFB4-LONG — GPFB4∘ROLL"
        if args.formal
        else "H-GPFB4-LONG smoke — GPFB4∘ROLL"
    )
    genes = data.get("best_genes") or []
    gene0 = genes[0] if genes else {}
    lines = [
        f"# {title}",
        "",
        f"Decision: **{decision}**",
        "",
        f"Parent: `{data.get('parent', 'H-GENC-serial@ROLL')}` · "
        f"k={k} · temp={data.get('pfb_temp')} · "
        f"gene0=`{gene0}` · "
        f"mechanism: `{data.get('mechanism', '')}`",
        "",
        f"Context: L_eff={data.get('l_eff')} · W={data.get('w')} · "
        f"S={data.get('s')} · mean_active={data.get('mean_active')} · "
        f"n_segments={data.get('n_segments')}",
        "",
        "| arm | mean story_lp | mean code_lp | mean wall_ms | "
        "mean unique | mean n_elig | mean switch | n |",
        "|-----|---------------|--------------|--------------|"
        "-------------|-------------|--------------|---|",
        _arm("H-GENC-serial@ROLL", parent),
        _arm(f"H-GPFB4-LONG k={k}", long_m),
    ]
    if full_m:
        lines.append(_arm("H-GPFB4-FULL@384", full_m))
    lines.extend(
        [
            "",
            "Tips unchanged. Wave Y GPFB4-LONG (compose; never K=2 / GENCACHE).",
            "",
            "Reproduce:",
            "`npm run nano:gpfb4long` → `npm run nano:gpfb4long:report`",
        ]
    )
    if decision.startswith("PROMOTE") and not args.formal:
        lines.extend(
            [
                "",
                "Next formal:",
                "`npm run nano:formal:hgpfb4long` → "
                "`npm run nano:formal:hgpfb4long:report`",
            ]
        )
    if args.formal:
        lines = [
            f"# {title}",
            "",
            f"Source: `{args.inp}`",
            f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
            "",
            *lines[2:],
        ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "decision": decision}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
