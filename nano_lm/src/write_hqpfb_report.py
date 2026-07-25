"""Render H-ABS-QPFB smoke — PFB on QT-int8 vs H-QT parent."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from qpfb_ops import decide_hqpfb


def _arm(name: str, m: dict) -> str:
    wb = m.get("weight_bytes", float("nan"))
    wb_s = f"{wb:.0f}" if wb == wb else "nan"
    return (
        f"| {name} | {m['mean_story_lp']:.4f} | {m['mean_code_lp']:.4f} | "
        f"{m['mean_wall_ms']:.0f} | {m.get('mean_unique', float('nan')):.3f} | "
        f"{m.get('mean_elig', float('nan')):.2f} | "
        f"{m.get('mean_switch', float('nan')):.2f} | {wb_s} | {int(m['n'])} |"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--in",
        dest="inp",
        type=Path,
        default=Path("results/nano-lm/student-matrix/hqpfb_smoke.json"),
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hqpfb-qpfb.md"),
    )
    ap.add_argument("--formal", action="store_true")
    args = ap.parse_args()
    data = json.loads(args.inp.read_text(encoding="utf-8"))
    parent = data["parent_means"]
    qpfb = data["qpfb_means"]
    k = int(data.get("k", qpfb.get("k", 4)))
    decision = data.get("decision") or decide_hqpfb(
        parent_story=float(parent["mean_story_lp"]),
        parent_code=float(parent["mean_code_lp"]),
        qpfb_story=float(qpfb["mean_story_lp"]),
        qpfb_code=float(qpfb["mean_code_lp"]),
        mean_unique=float(qpfb["mean_unique"]),
        mean_elig=float(qpfb["mean_elig"]),
        mean_switch=float(qpfb["mean_switch"]),
        k=k,
        identical=False,
    )
    title = "Formal H-ABS-QPFB" if args.formal else "H-ABS-QPFB smoke"
    lines = [
        f"# {title}",
        "",
        f"Decision: **{decision}**",
        "",
        f"Parent: `{data.get('parent', 'H-QT')}` · "
        f"k={k} · bits={data.get('bits')} · temp={data.get('pfb_temp')} · "
        f"mechanism: `{data.get('mechanism', '')}`",
        "",
        "| arm | mean story_lp | mean code_lp | mean wall_ms | "
        "mean unique | mean n_elig | mean switch | weight_bytes | n |",
        "|-----|---------------|--------------|--------------|"
        "-------------|-------------|--------------|--------------|---|",
        _arm("H-QT-int8 n=1", parent),
        _arm(f"H-ABS-QPFB k={k}", qpfb),
        "",
        "Tips unchanged. Wave X ABS-QPFB (PFB on QT-int8).",
        "",
        "Reproduce:",
        "`npm run nano:qpfb` → `npm run nano:qpfb:report`",
    ]
    if decision.startswith("PROMOTE"):
        lines.extend(
            [
                "",
                "Next formal:",
                "`npm run nano:formal:hqpfb` → "
                "`npm run nano:formal:hqpfb:report`",
            ]
        )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "decision": decision}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
