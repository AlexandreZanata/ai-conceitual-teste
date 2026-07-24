"""Render H-BUCKET smoke vs H-BAT / serial EARLY (length-banded pad)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from bucket_ops import decide_hbucket


def _means(rows: list[dict]) -> dict[str, dict[str, float]]:
    bags: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        bags[r["family"]].append(r)
    out: dict[str, dict[str, float]] = {}
    for fam, items in bags.items():
        n = float(len(items))
        out[fam] = {
            "mean_lp": sum(float(x["teacher_mean_logprob"]) for x in items) / n,
            "mean_wall": sum(float(x["mean_wall_ms"]) for x in items) / n,
            "mean_tps": sum(float(x["mean_tokens_per_s"]) for x in items) / n,
            "mean_gflops": sum(float(x["mean_est_gflops"]) for x in items) / n,
            "n": n,
        }
    return out


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = _means(data["rows"])
    s = stats.get("H-BUCKET", {})
    decision = decide_hbucket(s, stats) if s else "needs H-BUCKET rows"
    tip = stats.get("H-BAT", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_tps = s.get("mean_tps", float("nan")) - tip.get("mean_tps", float("nan"))
    d_w = s.get("mean_wall", float("nan")) - tip.get("mean_wall", float("nan"))
    lines = [
        "# H-BUCKET smoke — length-banded BAT vs flat H-BAT",
        "",
        f"Pad only within length bands (`band={data.get('band')}`); "
        "shared EARLY tip, n=1 near-greedy.",
        "Kill if |Δlp| > ε vs H-BAT/serial or no tok/s win vs H-BAT.",
        f"Prompt pack: `{data.get('mode')}` (`n_prompts={data.get('n_prompts')}`).",
        "",
        "| family | mean teacher_lp | Δ lp vs BAT | mean tok/s | Δ tok/s | "
        "mean wall_ms/prompt | Δ wall | n |",
        "|--------|-----------------|-------------|------------|---------|--"
        "-------------------|--------|---|",
    ]
    for fam in ("H-EARLY", "H-BAT", "H-BUCKET"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam != "H-BUCKET":
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
            f"**Decision: {decision}**",
            "",
            "Note: throughput util deepen of H-BAT; tip EARLY unchanged.",
            "Lesson: sequential band launches can cost more than pad savings on nano packs.",
            "",
            "Commands: `npm run nano:bucket` → `npm run nano:bucket:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/bucket_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hbucket-vs-hbat.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
