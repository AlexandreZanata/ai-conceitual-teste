"""Render formal H-ETRAIN vs H-STAG (PRE3 e2e train wall)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from etrain_ops import decide_hetrain


def _means(rows: list[dict]) -> dict[str, dict[str, float]]:
    bags: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        bags[r["family"]].append(r)
    out: dict[str, dict[str, float]] = {}
    for fam, items in bags.items():
        n = float(len(items))
        out[fam] = {
            "mean_lp": sum(float(x["teacher_mean_logprob"]) for x in items) / n,
            "mean_e2e": sum(float(x["e2e_wall_s"]) for x in items) / n,
            "mean_ms_step": sum(float(x["mean_ms_step"]) for x in items) / n,
            "mean_train_wall": sum(float(x["train_wall_s"]) for x in items) / n,
            "mean_cache_build": sum(float(x.get("cache_build_s", 0)) for x in items)
            / n,
            "n": n,
        }
    return out


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = _means(data["rows"])
    s = stats.get("H-ETRAIN", {})
    decision = decide_hetrain(s, stats) if s else "needs H-ETRAIN rows"
    tip = stats.get("H-STAG", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_e2e = s.get("mean_e2e", float("nan")) - tip.get("mean_e2e", float("nan"))
    lines = [
        "# Formal H-ETRAIN vs H-STAG (PRE3 e2e train wall)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Fit≠eval. Live STAG e2e = train only; ETRAIN e2e = cache_build + PRE3 train. "
        "Gate: lp ≥ STAG−ε **and** e2e_wall < STAG.",
        f"Recipe: `seq_lo={data.get('seq_lo')}`, `n_stages={data.get('n_stages')}`, "
        f"`steps={data.get('steps')}`, `top_k={data.get('top_k')}`, "
        f"mode `{data.get('mode')}`.",
        "",
        "| family | mean teacher_lp | Δ lp | mean e2e_wall_s | Δ e2e | "
        "mean ms/step | mean train_wall_s | mean cache_build_s | n |",
        "|--------|-----------------|------|-----------------|-------|"
        "--------------|-------------------|--------------------|---|",
    ]
    for fam in ("H-STAG", "H-ETRAIN"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-STAG":
            d1, d2 = "—", "—"
        else:
            d1, d2 = f"{d_lp:+.4f}", f"{d_e2e:+.3f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_e2e']:.3f} | "
            f"{d2} | {st['mean_ms_step']:.1f} | {st['mean_train_wall']:.2f} | "
            f"{st['mean_cache_build']:.2f} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Tip H-STAG / H-PRE3 util unchanged. Full-stack train claim (Wave R).",
            "",
            "Commands: `npm run nano:formal:hetrain` → "
            "`npm run nano:formal:hetrain:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hetrain/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hetrain-vs-hstag.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
