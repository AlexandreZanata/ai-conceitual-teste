"""Render H-WIN smoke vs H-STAG tip (local sliding-window attention)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from win_ops import decide_hwin


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
            "n": n,
        }
    return out


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = _means(data["rows"])
    s = stats.get("H-WIN", {})
    decision = decide_hwin(s, stats) if s else "needs H-WIN rows"
    tip = stats.get("H-STAG", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_w = s.get("mean_wall", float("nan")) - tip.get("mean_wall", float("nan"))
    d_gf = s.get("mean_gflops", float("nan")) - tip.get("mean_gflops", float("nan"))
    win = data.get("window", 32)
    lines = [
        "# H-WIN smoke — local sliding-window attention vs H-STAG",
        "",
        f"Train under STAG recipe (`seq_lo=6`, `n_stages=4`) with GPT-Neo local "
        f"attn `window_size={win}`.",
        "FLOPs scale attention portion by min(1, window/seq). "
        "Kill if quality < STAG−ε or no FLOP win.",
        "",
        "| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |",
        "|--------|-----------------|------|--------------|--------|-----------------|----------|---|",
    ]
    for fam in ("H-STAG", "H-WIN"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-STAG":
            d1, d2, d3 = "—", "—", "—"
        else:
            d1, d2, d3 = f"{d_lp:+.4f}", f"{d_w:+.0f}", f"{d_gf:+.3f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_wall']:.0f} | "
            f"{d2} | {st['mean_gflops']:.3f} | {d3} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:win` → `npm run nano:win:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/win_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hwin-vs-hstag.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
