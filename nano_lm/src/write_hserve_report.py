"""Render H-SERVE smoke vs H-EARLY (full serving stack)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from serve_ops import decide_hserve


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


def _recipes(rows: list[dict]) -> str:
    names = sorted(
        {
            str((r.get("best_gene") or {}).get("recipe", "?"))
            for r in rows
            if r.get("family") == "H-SERVE"
        }
    )
    return ", ".join(names) if names else "?"


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = _means(data["rows"])
    s = stats.get("H-SERVE", {})
    decision = decide_hserve(s, stats) if s else "needs H-SERVE rows"
    tip = stats.get("H-EARLY", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_tps = s.get("mean_tps", float("nan")) - tip.get("mean_tps", float("nan"))
    d_w = s.get("mean_wall", float("nan")) - tip.get("mean_wall", float("nan"))
    d_gf = s.get("mean_gflops", float("nan")) - tip.get("mean_gflops", float("nan"))
    lines = [
        "# H-SERVE smoke — full serving stack vs tip H-EARLY",
        "",
        "Control: serial H-EARLY alone on long prompts / dual budgets. "
        "Candidate: best of speed=`CHB+LAY+GALL` or quality=`CHB+FLAYB+GRAPHF` "
        f"(picked recipes: `{_recipes(data['rows'])}`). "
        "Kill if |Δlp| > ε vs EARLY or no wall/tok/s win.",
        f"Prompt pack: `n_prompts={data.get('n_prompts')}`; "
        f"budgets=`{data.get('budgets')}` chunk=`{data.get('chunk_size')}` "
        f"target_tokens=`{data.get('target_tokens')}`; "
        f"mode `{data.get('mode')}`.",
        "",
        "| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | "
        "mean wall_ms/prompt | Δ wall | mean est GFLOPs | Δ GFLOPs | n |",
        "|--------|-----------------|------|------------|---------|"
        "---------------------|--------|-----------------|----------|---|",
    ]
    for fam in ("H-EARLY", "H-SERVE"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-EARLY":
            d1 = d2 = d3 = d4 = "—"
        else:
            d1, d2, d3, d4 = (
                f"{d_lp:+.4f}",
                f"{d_tps:+.1f}",
                f"{d_w:+.0f}",
                f"{d_gf:+.3f}",
            )
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_tps']:.1f} | {d2} | "
            f"{st['mean_wall']:.0f} | {d3} | {st['mean_gflops']:.3f} | {d4} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Tip H-EARLY unchanged unless PROMOTE. Full-stack serving claim.",
            "",
            "Commands: `npm run nano:serve` → `npm run nano:serve:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/serve_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hserve-vs-hearly.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
