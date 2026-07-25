"""Render H-RETIP smoke — PRE3 capacity + frozen tip serve."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from retip_ops import decide_hretip


def render(path: Path, *, formal: bool = False) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    live = float(data.get("mean_ar_live", float("nan")))
    retip = float(data.get("mean_ar_retip", float("nan")))
    early_c = data.get("early_control") or {}
    early_r = data.get("early_retip") or {}
    pool_c = data.get("pool_control") or {}
    pool_r = data.get("pool_retip") or {}
    decision = data.get("decision") or decide_hretip(
        retip_lp=retip,
        control_lp=live,
        early_retip=early_r,
        early_control=early_c,
        pool_retip=pool_r,
        pool_control=pool_c,
    )
    title = "Formal H-RETIP" if formal else "H-RETIP smoke"
    lines = [
        f"# {title} — PRE3 train vs live STAG; frozen EARLY/POOL serve",
        "",
    ]
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
            "Capacity question: does TPACK/PRE3 train I/O yield tip capacity "
            "(AR lp↑ vs live STAG) **or** a serve win under frozen EARLY/POOL genes? "
            "Kill iff tip lp ≤ STAG control **and** no serve win.",
            f"Mode: `{data.get('mode')}`; seq_lo=`{data.get('seq_lo')}` "
            f"n_stages=`{data.get('n_stages')}` steps=`{data.get('steps')}` "
            f"top_k=`{data.get('top_k')}` max_new=`{data.get('max_new')}` "
            f"n_prompts=`{data.get('n_prompts')}`.",
            "",
            "## AR tip (capacity)",
            "",
            "| family | mean teacher_lp | Δ lp |",
            "|--------|-----------------|------|",
            f"| H-STAG (live) | {live:.4f} | — |",
            f"| H-RETIP (PRE3) | {retip:.4f} | {retip - live:+.4f} |",
            "",
            "## Frozen EARLY serve",
            "",
            "| ckpt | mean teacher_lp | Δ lp | mean wall_ms | Δ wall |",
            "|------|-----------------|------|--------------|--------|",
            f"| live | {early_c.get('mean_lp', float('nan')):.4f} | — | "
            f"{early_c.get('mean_wall', float('nan')):.0f} | — |",
            f"| PRE3 | {early_r.get('mean_lp', float('nan')):.4f} | "
            f"{early_r.get('mean_lp', float('nan')) - early_c.get('mean_lp', float('nan')):+.4f} | "
            f"{early_r.get('mean_wall', float('nan')):.0f} | "
            f"{early_r.get('mean_wall', float('nan')) - early_c.get('mean_wall', float('nan')):+.0f} |",
            "",
            "## Frozen POOL serve",
            "",
            "| ckpt | mean teacher_lp | Δ lp | mean wall_ms | Δ wall |",
            "|------|-----------------|------|--------------|--------|",
            f"| live | {pool_c.get('mean_lp', float('nan')):.4f} | — | "
            f"{pool_c.get('mean_wall', float('nan')):.0f} | — |",
            f"| PRE3 | {pool_r.get('mean_lp', float('nan')):.4f} | "
            f"{pool_r.get('mean_lp', float('nan')) - pool_c.get('mean_lp', float('nan')):+.4f} | "
            f"{pool_r.get('mean_wall', float('nan')):.0f} | "
            f"{pool_r.get('mean_wall', float('nan')) - pool_c.get('mean_wall', float('nan')):+.0f} |",
            "",
            f"**Decision: {decision}**",
            "",
            "Official tip genes unchanged (not re-searched). Wave U capacity probe.",
            "",
        ]
    )
    cmd = (
        "`npm run nano:formal:hretip` → `npm run nano:formal:hretip:report`"
        if formal
        else "`npm run nano:retip` → `npm run nano:retip:report`"
    )
    lines.extend([f"Commands: {cmd}.", ""])
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/retip_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hretip-vs-hstag.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, formal=False)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
