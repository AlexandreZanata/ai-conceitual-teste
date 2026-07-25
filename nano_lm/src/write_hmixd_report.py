"""Render H-MIXD smoke — story LP + prog PPL dual gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from mixd_ops import MIX_FRAC, decide_hmixd


def render(path: Path, *, formal: bool = False) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    means = data.get("means") or {}
    decision = data.get("decision") or decide_hmixd(
        mix_story_lp=float(means.get("H-MIXD:story_lp", 0)),
        ctrl_story_lp=float(means.get("H-STAG-CTRL:story_lp", 0)),
        mix_prog_ppl=float(means.get("H-MIXD:prog_ppl", 1e9)),
        ctrl_prog_ppl=float(means.get("H-STAG-CTRL:prog_ppl", 0)),
    )
    title = "Formal H-MIXD" if formal else "H-MIXD smoke"
    lines = [f"# {title} — STAG + curated programming mix", ""]
    if formal:
        lines.extend(
            [
                f"Source: `{path}`",
                f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
                "",
            ]
        )
    lines.extend(
        [
            "Wave W knowledge-in-training: TinyStories **STAG** curriculum "
            f"+ **mix_frac={data.get('mix_frac', MIX_FRAC)}** curated "
            "programming tokens (PSF / Rust book licenses). "
            "Teacher remains TinyStories. "
            "Hold-out: curated source ids ∩ prog eval prompt ids = ∅. "
            "PROMOTE iff story teacher_lp ≥ control−ε **and** prog PPL ↓.",
            f"Mode: `{data.get('mode')}`; steps=`{data.get('steps')}`; "
            f"cpu_threads=`{data.get('cpu_threads')}`; "
            f"licenses=`{data.get('licenses')}`.",
            "",
            f"**Decision: {decision}**",
            "",
            "## Means",
            "",
            "| arm | mean story teacher_lp | mean prog PPL |",
            "|-----|----------------------|---------------|",
            f"| H-STAG-CTRL | {means.get('H-STAG-CTRL:story_lp', float('nan')):.4f} | "
            f"{means.get('H-STAG-CTRL:prog_ppl', float('nan')):.3f} |",
            f"| H-MIXD | {means.get('H-MIXD:story_lp', float('nan')):.4f} | "
            f"{means.get('H-MIXD:prog_ppl', float('nan')):.3f} |",
            "",
            "Commands: "
            + (
                "`npm run nano:formal:hmixd` → `npm run nano:formal:hmixd:report`"
                if formal
                else "`npm run nano:mixd` → `npm run nano:mixd:report`"
            )
            + ".",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/hmixd_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hmixd-mix.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, formal=False)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
