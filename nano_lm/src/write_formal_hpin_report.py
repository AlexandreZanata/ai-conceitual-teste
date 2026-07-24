"""Render formal H-PIN vs H-TOP (pinned H2D)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from pin_ops import decide_hpin


def _means(rows: list[dict]) -> dict[str, dict[str, float]]:
    bags: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        bags[r["family"]].append(r)
    out: dict[str, dict[str, float]] = {}
    for fam, items in bags.items():
        n = float(len(items))
        out[fam] = {
            "mean_lp": sum(float(x["teacher_mean_logprob"]) for x in items) / n,
            "mean_ms_step": sum(float(x["mean_ms_step"]) for x in items) / n,
            "mean_train_wall": sum(float(x["train_wall_s"]) for x in items) / n,
            "n": n,
        }
    return out


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = _means(data["rows"])
    s = stats.get("H-PIN", {})
    decision = decide_hpin(s, stats) if s else "needs H-PIN rows"
    tip = stats.get("H-TOP", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_ms = s.get("mean_ms_step", float("nan")) - tip.get("mean_ms_step", float("nan"))
    wall = float(data.get("wall_s", 0.0))
    lines = [
        "# Formal H-PIN vs H-TOP (pinned + non_blocking H2D)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {wall:.1f}s",
        "",
        "Same top-k soft cache and STAG curriculum; only H2D path differs.",
        "Fit≠eval. Gate: lp ≥ TOP−ε **and** train ms/step < TOP.",
        f"Recipe: `seq_lo={data.get('seq_lo')}`, `n_stages={data.get('n_stages')}`, "
        f"`steps={data.get('steps')}`, `top_k={data.get('top_k')}`, "
        f"mode `{data.get('mode')}`.",
        "",
        "| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | "
        "mean train_wall_s | n |",
        "|--------|-----------------|------|--------------|-----------|"
        "------------------|---|",
    ]
    for fam in ("H-TOP", "H-PIN"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-TOP":
            d1, d2 = "—", "—"
        else:
            d1, d2 = f"{d_lp:+.4f}", f"{d_ms:+.1f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_ms_step']:.1f} | "
            f"{d2} | {st['mean_train_wall']:.2f} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Tip H-TOP util unchanged; H-PIN is train I/O deepen.",
            "",
            "Commands: `npm run nano:formal:hpin` → `npm run nano:formal:hpin:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hpin/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hpin-vs-htop.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
