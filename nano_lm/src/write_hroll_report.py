"""Render H-ROLL smoke — PFB2 on rolled summary‖W vs EARLY."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from roll_ops import decide_hroll


def _arm(name: str, m: dict) -> str:
    return (
        f"| {name} | {m['mean_story_lp']:.4f} | {m['mean_code_lp']:.4f} | "
        f"{m['mean_wall_ms']:.0f} | "
        f"{m.get('mean_unique', float('nan')):.3f} | "
        f"{m.get('mean_elig', float('nan')):.2f} | "
        f"{m.get('mean_switch', float('nan')):.2f} | {int(m['n'])} |"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--in",
        dest="inp",
        type=Path,
        default=Path("results/nano-lm/student-matrix/hroll_smoke.json"),
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hroll-roll.md"),
    )
    ap.add_argument("--formal", action="store_true")
    args = ap.parse_args()
    data = json.loads(args.inp.read_text(encoding="utf-8"))
    parent = data["parent_means"]
    roll = data["roll_means"]
    decision = data.get("decision") or decide_hroll(
        parent_story=float(parent["mean_story_lp"]),
        parent_code=float(parent["mean_code_lp"]),
        roll_story=float(roll["mean_story_lp"]),
        roll_code=float(roll["mean_code_lp"]),
        mean_unique=float(roll["mean_unique"]),
        mean_elig=float(roll["mean_elig"]),
        mean_switch=float(roll["mean_switch"]),
        l_eff=float(data["l_eff"]),
        mean_active=float(data["mean_active"]),
        w=int(data["w"]),
        s=int(data["s"]),
        identical=False,
    )
    title = (
        "Formal H-ROLL — rolling W + summary; PFB2 per segment"
        if args.formal
        else "H-ROLL smoke — rolling W + summary; PFB2 per segment"
    )
    lines = [
        f"# {title}",
        "",
        f"Decision: **{decision}**",
        "",
        f"Parent: `{data.get('parent', '')}` · k={data.get('k')} · "
        f"temp={data.get('pfb_temp')} · "
        f"mechanism: `{data.get('mechanism', '')}`",
        "",
        f"Context: L_eff={data['l_eff']:.0f} · W={data['w']} · S={data['s']} · "
        f"mean_active={data['mean_active']:.0f} · "
        f"n_segments={data.get('n_segments')}",
        "",
        "| arm | mean story_lp | mean code_lp | mean wall_ms | "
        "mean unique | mean n_elig | mean switch | n |",
        "|-----|---------------|--------------|--------------|"
        "-------------|-------------|--------------|---|",
        _arm("H-EARLY@ROLL", parent),
        _arm("H-ROLL K=2", roll),
        "",
        "Tips unchanged. Wave Y H-ROLL (summary‖W ≠ CTX full-KV).",
        "",
        "Reproduce:",
        "`npm run nano:roll` → `npm run nano:roll:report`",
    ]
    if decision.startswith("PROMOTE") and not args.formal:
        lines.extend(
            [
                "",
                "Next formal:",
                "`npm run nano:formal:hroll` → "
                "`npm run nano:formal:hroll:report`",
            ]
        )
    elif decision.startswith("KILL"):
        lines.extend(
            [
                "",
                "Archive if confirmed formal KILL — do not claim infinite ctx via ROLL alone.",
            ]
        )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "decision": decision}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
