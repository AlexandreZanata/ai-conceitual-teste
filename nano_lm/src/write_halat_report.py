"""Render H-ALAT (αT) smoke vs H-CURL2 tip."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from alat_ops import decide_halat
from matrix_report_lib import mean_by_family


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = mean_by_family(data["rows"])
    s = stats.get("H-ALAT", {})
    decision = decide_halat(s, stats) if s else "needs H-ALAT rows"
    tip = stats.get("H-CURL2", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    lines = [
        "# H-ALAT smoke — KD α/T schedule under CURL2 (H-αT)",
        "",
        "Same seq_lo=6 length stages as tip; α 0.25→0.75, T 3.0→1.0 by stage.",
        "Kill if ≤ H-CURL2 tip on teacher_lp @ equal steps.",
        "",
        "| family | mean teacher_lp | Δ vs CURL2 | mean wall_ms | n |",
        "|--------|-----------------|------------|--------------|---|",
    ]
    for fam in ("H-CURL2", "H-ALAT"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam == "H-CURL2" else f"{d_lp:+.4f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {delta} | {st['mean_wall']:.0f} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:alat` → `npm run nano:alat:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/alat_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/halat-vs-hcurl2.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
