"""Render H-TCACHE smoke — memo + eligible-only code on PFB2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tcache_ops import decide_htcache


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
        default=Path("results/nano-lm/student-matrix/htcache_smoke.json"),
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/htcache-tcache.md"),
    )
    ap.add_argument("--formal", action="store_true")
    args = ap.parse_args()
    data = json.loads(args.inp.read_text(encoding="utf-8"))
    parent = data["parent_means"]
    naive = data["naive_means"]
    tcache = data["tcache_means"]
    decision = data.get("decision") or decide_htcache(
        parent_story=float(parent["mean_story_lp"]),
        parent_code=float(parent["mean_code_lp"]),
        tcache_story=float(tcache["mean_story_lp"]),
        tcache_code=float(tcache["mean_code_lp"]),
        mean_unique=float(tcache["mean_unique"]),
        mean_elig=float(tcache["mean_elig"]),
        mean_switch=float(tcache["mean_switch"]),
        tcache_wall=float(data["tcache_score_wall_ms"]),
        naive_wall=float(data["naive_score_wall_ms"]),
        tcache_forwards=float(data["tcache_forwards"]),
        naive_forwards=float(data["naive_forwards"]),
        identical=False,
    )
    drop = 1.0 - float(data["tcache_forwards"]) / max(
        float(data["naive_forwards"]), 1.0
    )
    title = (
        "Formal H-TCACHE — teacher LP memo on PFB2"
        if args.formal
        else "H-TCACHE smoke — teacher LP memo on PFB2"
    )
    lines = [
        f"# {title}",
        "",
        f"Decision: **{decision}**",
        "",
        f"Parent: `{data.get('parent', 'H-EARLY')}` · k={data.get('k')} · "
        f"temp={data.get('pfb_temp')} · "
        f"mechanism: `{data.get('mechanism', '')}`",
        "",
        f"Score forwards: naive={data['naive_forwards']:.0f} · "
        f"tcache={data['tcache_forwards']:.0f} · drop={drop:.1%} · "
        f"hit_rate={float(data.get('tcache_hit_rate', 0)):.2f}",
        "",
        f"Score wall_ms: naive={data['naive_score_wall_ms']:.0f} · "
        f"tcache={data['tcache_score_wall_ms']:.0f}",
        "",
        "| arm | mean story_lp | mean code_lp | mean wall_ms | "
        "mean unique | mean n_elig | mean switch | n |",
        "|-----|---------------|--------------|--------------|"
        "-------------|-------------|--------------|---|",
        _arm("H-EARLY n=1", parent),
        _arm("H-TCACHE-naive", naive),
        _arm("H-TCACHE", tcache),
        "",
        "Tips unchanged. Wave Y H-TCACHE (teacher memo on PFB2 spine).",
        "",
        "Reproduce:",
        "`npm run nano:tcache` → `npm run nano:tcache:report`",
    ]
    if decision.startswith("PROMOTE") and not args.formal:
        lines.extend(
            [
                "",
                "Next formal:",
                "`npm run nano:formal:htcache` → "
                "`npm run nano:formal:htcache:report`",
            ]
        )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "decision": decision}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
