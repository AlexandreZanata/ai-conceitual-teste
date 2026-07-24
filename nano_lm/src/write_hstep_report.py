"""Render H-STEP smoke vs H-CURL2 tip (seq_lo=6)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from matrix_report_lib import mean_by_family
from step_ops import decide_hstep


def _mean_steps(rows: list[dict]) -> dict[str, float]:
    bags: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        if r.get("steps_run") is not None:
            bags[r["family"]].append(float(r["steps_run"]))
    return {k: sum(v) / len(v) for k, v in bags.items()}


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = mean_by_family(data["rows"])
    steps = _mean_steps(data["rows"])
    s = stats.get("H-STEP", {})
    decision = decide_hstep(s, stats) if s else "needs H-STEP rows"
    tip = stats.get("H-CURL2", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    lines = [
        "# H-STEP smoke — early-stop KD vs H-CURL2",
        "",
        "CURL2 recipe (seq_lo=6); stop when fit-prompt teacher_lp plateaus.",
        "Same max step budget as tip. Kill if claim lp worse than tip.",
        "",
        "| family | mean teacher_lp | Δ vs CURL2 | mean steps_run | mean wall_ms | n |",
        "|--------|-----------------|------------|----------------|--------------|---|",
    ]
    for fam in ("H-CURL2", "H-STEP"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam == "H-CURL2" else f"{d_lp:+.4f}"
        sr = steps.get(fam, float("nan"))
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {delta} | {sr:.0f} | "
            f"{st['mean_wall']:.0f} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:step` → `npm run nano:step:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/step_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hstep-vs-hcurl2.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
