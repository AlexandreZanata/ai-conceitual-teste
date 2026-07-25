"""Render formal H-CPOOLB vs H-POOLB (chunked prefill under batch POOL)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from cpoolb_ops import decide_hcpoolb


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
    s = stats.get("H-CPOOLB", {})
    decision = decide_hcpoolb(s, stats) if s else "needs H-CPOOLB rows"
    tip = stats.get("H-POOLB", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_tps = s.get("mean_tps", float("nan")) - tip.get("mean_tps", float("nan"))
    lines = [
        "# Formal H-CPOOLB vs H-POOLB (chunked prefill under batch POOL)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared formal B2 + formal POOL tip knobs. Fit≠eval (`eval_prompts`).",
        "Long prompts + chunked KV prefill under FLASH SDPA vs flat POOLB.",
        f"Mode: `{data.get('mode')}`. Kill if |Δlp| > ε or no tok/s win.",
        f"n_prompts={data.get('n_prompts')} chunk_size=`{data.get('chunk_size')}` "
        f"target_tokens=`{data.get('target_tokens')}`.",
        "",
        "| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | "
        "mean wall_ms/prompt | n |",
        "|--------|-----------------|------|------------|---------|"
        "---------------------|---|",
    ]
    for fam in ("H-POOLB", "H-CPOOLB"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-POOLB":
            d1, d2 = "—", "—"
        else:
            d1, d2 = f"{d_lp:+.4f}", f"{d_tps:+.1f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_tps']:.1f} | {d2} | "
            f"{st['mean_wall']:.0f} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Throughput util on POOLB axis — does not replace H-POOL / H-POOLB tips.",
            "",
            "Commands: `npm run nano:formal:hcpoolb` → "
            "`npm run nano:formal:hcpoolb:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hcpoolb/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hcpoolb-vs-hpoolb.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
