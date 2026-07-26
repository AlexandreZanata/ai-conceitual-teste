"""Render H-SUMCACHE smoke — hierarchical summary+tail vs full-prefill."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sumcache_ops import decide_hsumcache


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
        default=Path("results/nano-lm/student-matrix/hsumcache_smoke.json"),
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hsumcache-sumcache.md"),
    )
    ap.add_argument("--formal", action="store_true")
    args = ap.parse_args()
    data = json.loads(args.inp.read_text(encoding="utf-8"))
    parent = data["parent_means"]
    summ = data["sumcache_means"]
    decision = data.get("decision") or decide_hsumcache(
        parent_story=float(parent["mean_story_lp"]),
        parent_code=float(parent["mean_code_lp"]),
        sum_story=float(summ["mean_story_lp"]),
        sum_code=float(summ["mean_code_lp"]),
        mean_unique=float(summ["mean_unique"]),
        mean_elig=float(summ["mean_elig"]),
        mean_switch=float(summ["mean_switch"]),
        l_eff=float(data["l_eff"]),
        mean_active=float(data["mean_active"]),
        wall_sum=float(data["wall_sum_ms"]),
        wall_full=float(data["wall_full_ms"]),
        identical=False,
    )
    title = (
        "Formal H-SUMCACHE — hierarchical summary+tail PFB2"
        if args.formal
        else "H-SUMCACHE smoke — hierarchical summary+tail PFB2"
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
        f"Context: L_eff={data['l_eff']:.0f} · active={data['mean_active']:.0f} · "
        f"W={data['w']} · S_c={data['s_coarse']} · S_f={data['s_fine']} · "
        f"wall_sum={data['wall_sum_ms']:.0f} ms · "
        f"wall_full={data['wall_full_ms']:.0f} ms",
        "",
        "| arm | mean story_lp | mean code_lp | mean wall_ms | "
        "mean unique | mean n_elig | mean switch | n |",
        "|-----|---------------|--------------|--------------|"
        "-------------|-------------|--------------|---|",
        _arm("H-EARLY@SUM", parent),
        _arm("H-SUMCACHE K=2", summ),
        "",
        "Tips unchanged. Wave Y H-SUMCACHE (hierarchy ≠ CTX full-KV).",
        "",
        "Reproduce:",
        "`npm run nano:sumcache` → `npm run nano:sumcache:report`",
    ]
    if decision.startswith("PROMOTE") and not args.formal:
        lines.extend(
            [
                "",
                "Next formal:",
                "`npm run nano:formal:hsumcache` → "
                "`npm run nano:formal:hsumcache:report`",
            ]
        )
    elif decision.startswith("KILL"):
        lines.extend(
            [
                "",
                "Archive if confirmed formal KILL — keep H-ROLL for long ctx.",
            ]
        )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "decision": decision}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
