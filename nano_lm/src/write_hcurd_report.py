"""Render H-CURD smoke vs H-CURL2 tip (seq_lo=6)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from curd_ops import decide_hcurd
from matrix_report_lib import mean_by_family


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = mean_by_family(data["rows"])
    s = stats.get("H-CURD", {})
    decision = decide_hcurd(s, stats) if s else "needs H-CURD rows"
    tip = stats.get("H-CURL2", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    lines = [
        "# H-CURD smoke — teacher-NLL difficulty curriculum vs H-CURL2",
        "",
        "Fixed seq_len (xor length curriculum); stages open easiest→hardest",
        "by teacher CE/NLL. Equal KD steps vs tip lo=6.",
        "Kill if ≤ H-CURL2 tip on teacher_lp.",
        "",
        "| family | mean teacher_lp | Δ vs CURL2 | mean wall_ms | n |",
        "|--------|-----------------|------------|--------------|---|",
    ]
    for fam in ("H-CURL2", "H-CURD"):
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
            "Commands: `npm run nano:curd` → `npm run nano:curd:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/curd_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hcurd-vs-hcurl2.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
