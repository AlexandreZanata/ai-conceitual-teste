"""Render H-POOL2 smoke vs H-POOL (tighter search + elite warm-start)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from matrix_report_lib import mean_by_family
from pool2_ops import decide_hpool2


def _with_fwd(rows: list, stats: dict) -> dict:
    out = {k: dict(v) for k, v in stats.items()}
    for fam in out:
        vals = [
            float(r.get("teacher_forwards", 0))
            for r in rows
            if r.get("family") == fam
        ]
        out[fam]["teacher_forwards"] = sum(vals) / max(1, len(vals))
    return out


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = _with_fwd(data["rows"], mean_by_family(data["rows"]))
    s = stats.get("H-POOL2", {})
    decision = decide_hpool2(s, stats) if s else "needs H-POOL2 rows"
    tip = stats.get("H-POOL", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    lines = [
        "# H-POOL2 smoke — tighter pop×gens vs H-POOL tip",
        "",
        "Warm-start uses elite-biased `warm_start_pop2`; smoke budget 2×1",
        "(tip H-POOL is 4×2). Kill if quality < POOL−ε or no fit-fwd save.",
        "",
        "| family | mean teacher_lp | Δ vs POOL | mean wall_ms | mean fit teacher_fwd | n |",
        "|--------|-----------------|-----------|--------------|----------------------|---|",
    ]
    for fam in ("H-POOL", "H-POOL2"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam == "H-POOL" else f"{d_lp:+.4f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {delta} | {st['mean_wall']:.0f} | "
            f"{st.get('teacher_forwards', 0):.0f} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:pool2` → `npm run nano:pool2:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/pool2_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hpool2-vs-hpool.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
