"""Render formal H-STEP vs H-CURL2 tip."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from formal_ops import means_by_family
from step_ops import decide_hstep


def _mean_steps(rows: list[dict]) -> dict[str, float]:
    bags: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        if r.get("steps_run") is not None:
            bags[r["family"]].append(float(r["steps_run"]))
    return {k: sum(v) / len(v) for k, v in bags.items()}


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    stats = {
        name: {"mean_lp": st["lp"], "mean_wall": st["wall"], "n": st["n"]}
        for name, st in fam.items()
    }
    steps = _mean_steps(data["rows"])
    decision = decide_hstep(stats.get("H-STEP", {}), stats)
    tip = stats.get("H-CURL2", {})
    hyp = stats.get("H-STEP", {})
    d_lp = hyp.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    lines = [
        "# Formal H-STEP vs H-CURL2 (early-stop KD)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Max budget 120 steps; tip = formal CURL2 lo=6.",
        "Val = fit_prompts teacher_lp; claim = eval_prompts.",
        "Kill if claim lp worse than tip.",
        "",
        "| family | mean teacher_lp | Δ vs CURL2 | mean steps_run | mean wall_ms | n |",
        "|--------|-----------------|------------|----------------|--------------|---|",
    ]
    for name in ("H-CURL2", "H-STEP"):
        if name not in stats:
            continue
        st = stats[name]
        d = "—" if name == "H-CURL2" else f"{d_lp:+.4f}"
        sr = steps.get(name, float("nan"))
        lines.append(
            f"| {name} | {st['mean_lp']:.4f} | {d} | {sr:.0f} | "
            f"{st['mean_wall']:.0f} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Commands: `npm run nano:formal:hstep` → "
            "`npm run nano:formal:hstep:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hstep/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hstep-vs-hcurl2.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
