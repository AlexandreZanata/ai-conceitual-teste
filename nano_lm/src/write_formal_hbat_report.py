"""Render formal H-BAT vs serial EARLY (batched throughput)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from bat_ops import decide_hbat


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
    s = stats.get("H-BAT", {})
    decision = decide_hbat(s, stats) if s else "needs H-BAT rows"
    tip = stats.get("H-EARLY", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_tps = s.get("mean_tps", float("nan")) - tip.get("mean_tps", float("nan"))
    lines = [
        "# Formal H-BAT vs serial H-EARLY (batched throughput)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared formal B2 + formal EARLY exit knobs. Fit≠eval (`eval_prompts`).",
        f"Mode: `{data.get('mode')}`. Kill if |Δlp| > ε or no tok/s win.",
        f"n_prompts={data.get('n_prompts')}.",
        "",
        "| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | n |",
        "|--------|-----------------|------|------------|---------|---------------------|---|",
    ]
    for fam in ("H-EARLY", "H-BAT"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-EARLY":
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
            "Throughput util — does not replace H-EARLY single-prompt tip.",
            "",
            "Commands: `npm run nano:formal:hbat` → "
            "`npm run nano:formal:hbat:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hbat/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hbat-vs-hearly.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
