"""Render formal H-POOL2 vs H-POOL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from formal_ops import means_by_family
from pool2_ops import decide_hpool2


def _with_fwd(rows: list, fam_means: dict) -> dict:
    stats = {
        name: {"mean_lp": st["lp"], "mean_wall": st["wall"], "n": st["n"]}
        for name, st in fam_means.items()
    }
    for fam in stats:
        vals = [
            float(r.get("teacher_forwards", 0))
            for r in rows
            if r.get("family") == fam
        ]
        stats[fam]["teacher_forwards"] = sum(vals) / max(1, len(vals))
    return stats


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = _with_fwd(data["rows"], means_by_family(data["rows"]))
    decision = decide_hpool2(stats.get("H-POOL2", {}), stats)
    tip = stats.get("H-POOL", {})
    hyp = stats.get("H-POOL2", {})
    d_lp = hyp.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    lines = [
        "# Formal H-POOL2 vs H-POOL (tighter search)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared B2; tip H-POOL 8×12; H-POOL2 4×6 + elite warm-start. Fit≠eval.",
        "Kill if quality < POOL−ε or no fit-fwd save.",
        "",
        "| family | mean teacher_lp | Δ vs POOL | mean wall_ms | mean fit teacher_fwd | n |",
        "|--------|-----------------|-----------|--------------|----------------------|---|",
    ]
    for name in ("H-POOL", "H-POOL2"):
        if name not in stats:
            continue
        st = stats[name]
        d = "—" if name == "H-POOL" else f"{d_lp:+.4f}"
        lines.append(
            f"| {name} | {st['mean_lp']:.4f} | {d} | {st['mean_wall']:.0f} | "
            f"{st.get('teacher_forwards', 0):.0f} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Commands: `npm run nano:formal:hpool2` → "
            "`npm run nano:formal:hpool2:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hpool2/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hpool2-vs-hpool.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
