"""Render H-TIE smoke vs H-STAG tip (shared-block UT-lite)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from tie_ops import decide_htie


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
            "mean_params": sum(float(x.get("mean_params", x["n_params"])) for x in items)
            / n,
            "n": n,
        }
    return out


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = _means(data["rows"])
    s = stats.get("H-TIE", {})
    decision = decide_htie(s, stats) if s else "needs H-TIE rows"
    tip = stats.get("H-STAG", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_p = s.get("mean_params", float("nan")) - tip.get("mean_params", float("nan"))
    d_gf = s.get("mean_gflops", float("nan")) - tip.get("mean_gflops", float("nan"))
    lines = [
        "# H-TIE smoke — tied embed + shared block vs H-STAG",
        "",
        "Train under STAG recipe (`seq_lo=6`, `n_stages=4`) with UT-lite shared depth.",
        "Kill if quality < STAG−ε or no param/FLOP win (FLOPs use full-depth proxy).",
        "",
        "| family | mean teacher_lp | Δ lp | mean params | Δ params | mean est GFLOPs | Δ GFLOPs | n |",
        "|--------|-----------------|------|-------------|----------|-----------------|----------|---|",
    ]
    for fam in ("H-STAG", "H-TIE"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-STAG":
            d1, d2, d3 = "—", "—", "—"
        else:
            d1, d2, d3 = f"{d_lp:+.4f}", f"{d_p:+.0f}", f"{d_gf:+.3f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_params']:.0f} | "
            f"{d2} | {st['mean_gflops']:.3f} | {d3} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:tie` → `npm run nano:tie:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/tie_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/htie-vs-hstag.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
