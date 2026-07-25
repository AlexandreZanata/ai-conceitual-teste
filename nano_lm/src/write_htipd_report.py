"""Render H-TIPD smoke — RETIP tip decision vs parked H-STAG."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tipd_ops import decide_htipd, tip_outcome


def render(path: Path, *, formal: bool = False) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    live = float(data.get("mean_ar_live", float("nan")))
    retip = float(data.get("mean_ar_retip", float("nan")))
    early_c = data.get("early_control") or {}
    early_r = data.get("early_retip") or {}
    pool_c = data.get("pool_control") or {}
    pool_r = data.get("pool_retip") or {}
    decision = data.get("decision") or decide_htipd(
        retip_lp=retip,
        control_lp=live,
        early_retip=early_r,
        early_control=early_c,
        pool_retip=pool_r,
        pool_control=pool_c,
    )
    outcome = data.get("tip_outcome") or tip_outcome(decision)
    title = "Formal H-TIPD" if formal else "H-TIPD smoke"
    lines = [
        f"# {title} — RETIP → STAG′ xor util",
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
            "Binary tip decision (Wave V): promote RETIP/PRE3 ckpt to official "
            "train tip **STAG′** iff tip lp > live STAG **and** frozen EARLY/POOL "
            "serve do not regress (lp ≥ tip−ε). Else keep parked **H-STAG**; "
            "RETIP stays util.",
            f"Mode: `{data.get('mode')}`; seq_lo=`{data.get('seq_lo')}` "
            f"n_stages=`{data.get('n_stages')}` steps=`{data.get('steps')}` "
            f"top_k=`{data.get('top_k')}` max_new=`{data.get('max_new')}` "
            f"n_prompts=`{data.get('n_prompts')}` cpu_threads=`{data.get('cpu_threads')}`.",
            "",
            "## AR tip (capacity gate)",
            "",
            "| family | mean teacher_lp | Δ lp |",
            "|--------|-----------------|------|",
            f"| H-STAG (live) | {live:.4f} | — |",
            f"| STAG′ (RETIP/PRE3) | {retip:.4f} | {retip - live:+.4f} |",
            "",
            "## Frozen EARLY serve (no-regress gate)",
            "",
            "| ckpt | mean teacher_lp | Δ lp | mean wall_ms | Δ wall |",
            "|------|-----------------|------|--------------|--------|",
            f"| live | {early_c.get('mean_lp', float('nan')):.4f} | — | "
            f"{early_c.get('mean_wall', float('nan')):.0f} | — |",
            f"| STAG′ | {early_r.get('mean_lp', float('nan')):.4f} | "
            f"{early_r.get('mean_lp', float('nan')) - early_c.get('mean_lp', float('nan')):+.4f} | "
            f"{early_r.get('mean_wall', float('nan')):.0f} | "
            f"{early_r.get('mean_wall', float('nan')) - early_c.get('mean_wall', float('nan')):+.0f} |",
            "",
            "## Frozen POOL serve (no-regress gate)",
            "",
            "| ckpt | mean teacher_lp | Δ lp | mean wall_ms | Δ wall |",
            "|------|-----------------|------|--------------|--------|",
            f"| live | {pool_c.get('mean_lp', float('nan')):.4f} | — | "
            f"{pool_c.get('mean_wall', float('nan')):.0f} | — |",
            f"| STAG′ | {pool_r.get('mean_lp', float('nan')):.4f} | "
            f"{pool_r.get('mean_lp', float('nan')) - pool_c.get('mean_lp', float('nan')):+.4f} | "
            f"{pool_r.get('mean_wall', float('nan')):.0f} | "
            f"{pool_r.get('mean_wall', float('nan')) - pool_c.get('mean_wall', float('nan')):+.0f} |",
            "",
            f"**Decision: {decision}**",
            f"**Tip outcome: `{outcome}`**",
            "",
            "Decode tip genes (EARLY/POOL) unchanged. Wave V tip decision.",
            "",
        ]
    )
    cmd = (
        "`npm run nano:formal:htipd` → `npm run nano:formal:htipd:report`"
        if formal
        else "`npm run nano:tipd` → `npm run nano:tipd:report`"
    )
    lines.extend([f"Commands: {cmd}.", ""])
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/tipd_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/htipd-vs-hstag.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, formal=False)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
