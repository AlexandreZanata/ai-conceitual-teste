"""Render formal H-FCPOOLB vs H-CPOOLB (FUSE under CPOOLB batch)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from fcpoolb_ops import decide_hfcpoolb


def _means(rows: list[dict]) -> dict[str, dict[str, float]]:
    bags: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        bags[r["family"]].append(r)
    out: dict[str, dict[str, float]] = {}
    for fam, items in bags.items():
        n = float(len(items))
        out[fam] = {
            "mean_lp": sum(float(x["teacher_mean_logprob"]) for x in items) / n,
            "mean_tps": sum(float(x["mean_tokens_per_s"]) for x in items) / n,
            "mean_wall": sum(float(x["mean_wall_ms"]) for x in items) / n,
            "mean_gflops": sum(float(x["mean_est_gflops"]) for x in items) / n,
            "n": n,
        }
    return out


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = _means(data["rows"])
    s = stats.get("H-FCPOOLB", {})
    decision = decide_hfcpoolb(s, stats) if s else "needs H-FCPOOLB rows"
    tip = stats.get("H-CPOOLB", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_tps = s.get("mean_tps", float("nan")) - tip.get("mean_tps", float("nan"))
    d_w = s.get("mean_wall", float("nan")) - tip.get("mean_wall", float("nan"))
    thrs = [
        r.get("best_gene", {}).get("kv_threshold")
        for r in data["rows"]
        if r.get("family") == "H-FCPOOLB"
    ]
    lines = [
        "# Formal H-FCPOOLB vs H-CPOOLB (FUSE under CPOOLB batch)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared formal B2 + POOL + formal KVSEL threshold. Fit≠eval.",
        "Dual-budget FLASH⊕KVSEL gate on CPOOLB path vs always-on CPOOLB.",
        f"Mode: `{data.get('mode')}`. Kill if |Δlp| > ε or no tok/s/wall win.",
        f"n_prompts={data.get('n_prompts')} chunk_size=`{data.get('chunk_size')}` "
        f"budgets=`{data.get('budgets')}` "
        f"target_tokens=`{data.get('target_tokens')}`.",
        f"Selected `kv_threshold` per seed: `{thrs}`.",
        "",
        "| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | "
        "mean wall_ms/prompt | Δ wall | n |",
        "|--------|-----------------|------|------------|---------|"
        "---------------------|--------|---|",
    ]
    for fam in ("H-CPOOLB", "H-FCPOOLB"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-CPOOLB":
            d1 = d2 = d3 = "—"
        else:
            d1, d2, d3 = f"{d_lp:+.4f}", f"{d_tps:+.1f}", f"{d_w:+.0f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_tps']:.1f} | {d2} | "
            f"{st['mean_wall']:.0f} | {d3} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Throughput util on CPOOLB axis — does not replace H-POOL / H-CPOOLB tips.",
            "",
            "Commands: `npm run nano:formal:hfcpoolb` → "
            "`npm run nano:formal:hfcpoolb:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hfcpoolb/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hfcpoolb-vs-hcpoolb.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
