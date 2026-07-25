"""Render H-AMORT smoke — amortized soft-cache e2e vs live STAG."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from amort_ops import amortized_e2e, decide_hamort


def render(path: Path, *, formal: bool = False) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    live_lp = float(data.get("mean_live_lp", float("nan")))
    live_e2e = float(data.get("mean_live_e2e", float("nan")))
    amort_lp = float(data.get("mean_amort_lp", float("nan")))
    amort_e2e = float(data.get("mean_amort_e2e", float("nan")))
    n_runs = int(data.get("n_runs", 0))
    decision = data.get("decision") or decide_hamort(
        amort_e2e=amort_e2e,
        live_e2e=live_e2e,
        amort_lp=amort_lp,
        live_lp=live_lp,
        n_runs=n_runs,
    )
    title = "Formal H-AMORT" if formal else "H-AMORT smoke"
    lines = [
        f"# {title} — amortized soft-cache e2e vs live H-STAG",
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
            "New e2e story without ASYNC: build top-k soft-cache **once**, run "
            f"**n={n_runs}** PRE3 trains on the same cache. "
            "Amortized e2e = cache_build/n + mean(PRE3 train wall). "
            "Live STAG e2e = train wall only. "
            "Kill if lp < STAG−ε or amortized e2e ≥ live.",
            f"Mode: `{data.get('mode')}`; seq_lo=`{data.get('seq_lo')}` "
            f"n_stages=`{data.get('n_stages')}` steps=`{data.get('steps')}` "
            f"top_k=`{data.get('top_k')}`.",
            "",
            "| family | mean teacher_lp | Δ lp | mean e2e_wall_s | Δ e2e |",
            "|--------|-----------------|------|-----------------|-------|",
            f"| H-STAG (live) | {live_lp:.4f} | — | {live_e2e:.3f} | — |",
            f"| H-AMORT | {amort_lp:.4f} | {amort_lp - live_lp:+.4f} | "
            f"{amort_e2e:.3f} | {amort_e2e - live_e2e:+.3f} |",
            "",
            f"**Decision: {decision}**",
            "",
            "Tip H-STAG / util H-PRE3 unchanged. Reopens e2e claim with amortization "
            "(ETRAIN N=1 stays KILL).",
            "",
        ]
    )
    # Per-seed cache tax visibility
    rows = data.get("seed_rows") or []
    if rows:
        lines.extend(
            [
                "| seed | cache_s | mean PRE3 train_s | amort e2e | live e2e |",
                "|------|---------|-------------------|-----------|----------|",
            ]
        )
        for r in rows:
            walls = r.get("pre3_train_walls") or []
            mean_t = sum(walls) / max(len(walls), 1)
            ae = amortized_e2e(float(r["cache_build_s"]), walls)
            lines.append(
                f"| {r['seed']} | {float(r['cache_build_s']):.3f} | {mean_t:.3f} | "
                f"{ae:.3f} | {float(r['live_train_wall_s']):.3f} |"
            )
        lines.append("")
    cmd = (
        "`npm run nano:formal:hamort` → `npm run nano:formal:hamort:report`"
        if formal
        else "`npm run nano:amort` → `npm run nano:amort:report`"
    )
    lines.extend([f"Commands: {cmd}.", ""])
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/amort_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hamort-vs-hstag.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, formal=False)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
