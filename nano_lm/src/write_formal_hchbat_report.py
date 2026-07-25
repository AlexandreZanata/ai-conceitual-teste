"""Render formal H-CHBAT vs H-CBAT (CHB B under CBAT)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from chbat_ops import decide_hchbat


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
    s = stats.get("H-CHBAT", {})
    decision = decide_hchbat(s, stats) if s else "needs H-CHBAT rows"
    tip = stats.get("H-CBAT", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_tps = s.get("mean_tps", float("nan")) - tip.get("mean_tps", float("nan"))
    lines = [
        "# Formal H-CHBAT vs H-CBAT (CHB B under CBAT)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared formal B2 + formal EARLY exit knobs. Fit≠eval (`eval_prompts`).",
        "Long prompts; CBAT tip B vs CHB tip B under FLASH SDPA.",
        f"Mode: `{data.get('mode')}`. Kill if |Δlp| > ε or no tok/s win.",
        f"n_prompts={data.get('n_prompts')} tip_chunk=`{data.get('tip_chunk_size')}` "
        f"chunk_size=`{data.get('chunk_size')}` "
        f"target_tokens=`{data.get('target_tokens')}`.",
        "",
        "| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | "
        "mean wall_ms/prompt | n |",
        "|--------|-----------------|------|------------|---------|"
        "---------------------|---|",
    ]
    for fam in ("H-CBAT", "H-CHBAT"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-CBAT":
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
            "Throughput util on CBAT axis — does not replace H-EARLY / H-CBAT tips.",
            "",
            "Commands: `npm run nano:formal:hchbat` → "
            "`npm run nano:formal:hchbat:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hchbat/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hchbat-vs-hcbat.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
