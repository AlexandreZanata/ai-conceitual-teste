"""Render H-POOL smoke vs cold H-DECKL markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from matrix_report_lib import mean_by_family
from pool_ops import decide_hpool


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = mean_by_family(data["rows"])
    s = stats.get("H-POOL", {})
    decision = decide_hpool(s, stats) if s else "needs H-POOL rows"
    cold = stats.get("H-DECKL", {})
    delta = s.get("mean_lp", float("nan")) - cold.get("mean_lp", float("nan"))
    lines = [
        "# H-POOL smoke vs cold H-DECKL (cross-seed warm-start)",
        "",
        "Cold H-DECKL builds a gene pool; each seed warm-starts from others.",
        "Kill if ≤ cold H-DECKL at equal pop×gens.",
        "",
        "| family | mean teacher_lp | Δ vs cold | mean wall_ms | n |",
        "|--------|-----------------|-----------|--------------|---|",
    ]
    for fam in ("H-DECKL", "H-POOL"):
        if fam not in stats:
            continue
        st = stats[fam]
        d = "—" if fam == "H-DECKL" else f"{delta:+.4f}"
        wall = st["mean_wall"]
        wall_s = f"{wall:.0f}" if wall == wall else "—"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d} | {wall_s} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:pool` → `npm run nano:pool:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/pool_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hpool-vs-hdeckl.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
