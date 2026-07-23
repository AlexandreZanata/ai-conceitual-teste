"""Render H-DIF smoke vs B2 markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from dif_ops import decide_hdif
from matrix_report_lib import mean_by_family


def render(smoke_path: Path, matrix_path: Path) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    kept = [r for r in matrix.get("rows", []) if r.get("family") != "H-DIF"]
    stats = mean_by_family(kept + smoke["rows"])
    s = dict(stats.get("H-DIF", {}))
    if "H-DIF" not in stats:
        decision = "needs H-DIF rows"
    else:
        if smoke["rows"]:
            s["peak_vram_mib"] = max(
                float(r.get("peak_vram_mib", 0.0)) for r in smoke["rows"]
            )
        decision = decide_hdif(s, stats)
    b2 = stats.get("B2", {})
    d_lp = s.get("mean_lp", float("nan")) - b2.get("mean_lp", float("nan"))
    lines = [
        "# H-DIF smoke vs B2 (discrete diffusion nano)",
        "",
        "Absorb-mask diffusion train; iterative remask decode at eval.",
        "Kill if VRAM > 7 GiB, wall > 2× B2, or ≤ B2 quality.",
        "",
        "| family | mean teacher_lp | mean wall_ms | peak VRAM MiB | Δ vs B2 | n |",
        "|--------|-----------------|--------------|---------------|---------|---|",
    ]
    for fam in ("B2", "H-DIF"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam == "B2" else f"{d_lp:+.4f}"
        wall = st["mean_wall"]
        wall_s = f"{wall:.0f}" if wall == wall else "—"
        if fam == "H-DIF":
            vram = f"{s.get('peak_vram_mib', float('nan')):.0f}"
        else:
            vram = "—"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {wall_s} | {vram} | {delta} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:dif` → `npm run nano:dif:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/dif_smoke.json"),
    )
    p.add_argument(
        "--matrix",
        type=Path,
        default=Path("results/nano-lm/student-matrix/matrix.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hdif-vs-b2.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
