"""Render H-DEPTH smoke vs H-STAG (shallow STAG + PRUN)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from depth_ops import decide_hdepth


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
            "mean_gflops": sum(float(x["mean_est_gflops"]) for x in items) / n,
            "mean_params": sum(float(x.get("params", 0)) for x in items) / n,
            "n": n,
        }
    return out


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = _means(data["rows"])
    s = stats.get("H-DEPTH", {})
    decision = decide_hdepth(s, stats) if s else "needs H-DEPTH rows"
    tip = stats.get("H-STAG", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_w = s.get("mean_wall", float("nan")) - tip.get("mean_wall", float("nan"))
    d_gf = s.get("mean_gflops", float("nan")) - tip.get("mean_gflops", float("nan"))
    lines = [
        "# H-DEPTH smoke — 1-layer STAG + PRUN recover vs tip",
        "",
        f"Train STAG recipe (`seq_lo=6`, `n_stages=4`) with "
        f"`n_layers={data.get('n_layers')}` (tip `{data.get('tip_layers')}`), "
        "then magnitude prune + short KD recover. Claim with frozen EARLY genes.",
        "Arch cut ≠ H-THIN (width). Kill if lp < STAG−ε or no wall win.",
        "",
        "| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | "
        "Δ GFLOPs | params | n |",
        "|--------|-----------------|------|--------------|--------|-----------------|"
        "----------|--------|---|",
    ]
    for fam in ("H-STAG", "H-DEPTH"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-STAG":
            d1 = d2 = d3 = "—"
        else:
            d1, d2, d3 = f"{d_lp:+.4f}", f"{d_w:+.0f}", f"{d_gf:+.3f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_wall']:.0f} | {d2} | "
            f"{st['mean_gflops']:.3f} | {d3} | {st['mean_params']:.0f} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:depth` → `npm run nano:depth:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/depth_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hdepth-vs-hstag.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
