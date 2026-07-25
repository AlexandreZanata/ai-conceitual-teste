"""Render H-ABS-QPFB2 smoke — K=2 PFB on QT; wall↓ vs QPFB k=4."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from qpfb2_ops import decide_hqpfb2


def _arm(name: str, m: dict) -> str:
    wb = m.get("weight_bytes")
    wb_s = f"{int(wb)}" if wb is not None and wb == wb else "—"
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
        default=Path("results/nano-lm/student-matrix/hqpfb2_smoke.json"),
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hqpfb2-qpfb2.md"),
    )
    ap.add_argument("--formal", action="store_true")
    args = ap.parse_args()
    data = json.loads(args.inp.read_text(encoding="utf-8"))
    parent = data["parent_means"]
    qpfb4 = data["qpfb4_means"]
    qpfb2 = data["qpfb2_means"]
    decision = data.get("decision") or decide_hqpfb2(
        parent_story=float(parent["mean_story_lp"]),
        parent_code=float(parent["mean_code_lp"]),
        qpfb2_story=float(qpfb2["mean_story_lp"]),
        qpfb2_code=float(qpfb2["mean_code_lp"]),
        mean_unique=float(qpfb2["mean_unique"]),
        mean_elig=float(qpfb2["mean_elig"]),
        mean_switch=float(qpfb2["mean_switch"]),
        qpfb2_wall=float(qpfb2["mean_wall_ms"]),
        qpfb4_wall=float(qpfb4["mean_wall_ms"]),
        identical=False,
    )
    title = (
        "Formal H-ABS-QPFB2 — PFB K=2 on QT; wall↓ vs QPFB k=4"
        if args.formal
        else "H-ABS-QPFB2 smoke — PFB K=2 on QT-int8; wall↓ vs QPFB k=4"
    )
    lines = [
        f"# {title}",
        "",
        f"Decision: **{decision}**",
        "",
        f"Parent: `{data.get('parent', 'H-QT')}` · "
        f"k2={data.get('k2')} · k4={data.get('k4')} · "
        f"bits={data.get('bits')} · temp={data.get('pfb_temp')} · "
        f"mechanism: `{data.get('mechanism', '')}`",
        "",
        "| arm | mean story_lp | mean code_lp | mean wall_ms | "
        "mean unique | mean n_elig | mean switch | weight_bytes | n |",
        "|-----|---------------|--------------|--------------|"
        "-------------|-------------|--------------|--------------|---|",
        _arm("H-QT-int8 n=1", parent),
        _arm("H-ABS-QPFB k=4", qpfb4),
        _arm("H-ABS-QPFB2 k=2", qpfb2),
        "",
        "Tips unchanged. Wave X ABS-QPFB2 (QT∘PFB2).",
        "",
        "Reproduce:",
        "`npm run nano:qpfb2` → `npm run nano:qpfb2:report`",
    ]
    if decision.startswith("PROMOTE"):
        lines.extend(
            [
                "",
                "Next formal:",
                "`npm run nano:formal:hqpfb2` → "
                "`npm run nano:formal:hqpfb2:report`",
            ]
        )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "decision": decision}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
