"""Render H-SCORERAM smoke — disk/RAM pack score cache cold vs warm."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scoreram_ops import decide_hscoreram


def _arm(name: str, m: dict) -> str:
    return (
        f"| {name} | {m['mean_story_lp']:.4f} | {m['mean_code_lp']:.4f} | "
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
        default=Path("results/nano-lm/student-matrix/hscoreram_smoke.json"),
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hscoreram-scoreram.md"),
    )
    ap.add_argument("--formal", action="store_true")
    args = ap.parse_args()
    data = json.loads(args.inp.read_text(encoding="utf-8"))
    cold = data["cold_means"]
    warm = data["warm_means"]
    decision = data.get("decision") or decide_hscoreram(
        cold_wall=float(data["cold_score_wall_ms"]),
        warm_wall=float(data["warm_score_wall_ms"]),
        cold_story=float(cold["mean_story_lp"]),
        warm_story=float(warm["mean_story_lp"]),
        cold_code=float(cold["mean_code_lp"]),
        warm_code=float(warm["mean_code_lp"]),
        hit_rate=float(data["warm_hit_rate"]),
    )
    title = (
        "Formal H-SCORERAM — disk/RAM pack score cache"
        if args.formal
        else "H-SCORERAM smoke — disk/RAM pack score cache"
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
        f"Score wall_ms: cold={data['cold_score_wall_ms']:.0f} · "
        f"warm={data['warm_score_wall_ms']:.0f}",
        "",
        f"Forwards: cold={data['cold_forwards']:.0f} · "
        f"warm={data['warm_forwards']:.0f} · "
        f"hit_rate={float(data['warm_hit_rate']):.2f} · "
        f"entries={data.get('cache_entries', '—')}",
        "",
        "| arm | mean story_lp | mean code_lp | mean unique | "
        "mean n_elig | mean switch | n |",
        "|-----|---------------|--------------|-------------|"
        "-------------|--------------|---|",
        _arm("cold (fill cache)", cold),
        _arm("warm (disk hit)", warm),
        "",
        "Tips unchanged. Wave Y H-SCORERAM (AMORT-like teacher pack cache).",
        "",
        "Reproduce:",
        "`npm run nano:scoreram` → `npm run nano:scoreram:report`",
    ]
    if decision.startswith("PROMOTE") and not args.formal:
        lines.extend(
            [
                "",
                "Next formal:",
                "`npm run nano:formal:hscoreram` → "
                "`npm run nano:formal:hscoreram:report`",
            ]
        )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "decision": decision}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
