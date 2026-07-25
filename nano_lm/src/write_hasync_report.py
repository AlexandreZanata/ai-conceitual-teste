"""Render H-ASYNC smoke vs sequential H-PIN (e2e wall)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from async_ops import decide_hasync


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
            "mean_e2e_wall": sum(float(x["e2e_wall_s"]) for x in items) / n,
            "mean_train_wall": sum(float(x["train_wall_s"]) for x in items) / n,
            "n": n,
        }
    return out


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = _means(data["rows"])
    s = stats.get("H-ASYNC", {})
    decision = decide_hasync(s, stats) if s else "needs H-ASYNC rows"
    tip = stats.get("H-PIN", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_e2e = s.get("mean_e2e_wall", float("nan")) - tip.get(
        "mean_e2e_wall", float("nan")
    )
    lines = [
        "# H-ASYNC smoke — overlap TOP cache build with PIN train",
        "",
        "Sequential H-PIN = full top-k cache then pinned train "
        "(`e2e = cache_build + train`).",
        "H-ASYNC = 1-deep CUDA pipeline: build record i+1 while training step i.",
        "Kill if quality < PIN−ε or no end-to-end wall win.",
        f"Recipe: `seq_lo={data.get('seq_lo')}`, `n_stages={data.get('n_stages')}`, "
        f"`steps={data.get('steps')}`, `top_k={data.get('top_k')}`, "
        f"mode `{data.get('mode')}`.",
        "",
        "| family | mean teacher_lp | Δ lp | mean e2e_wall_s | Δ e2e | "
        "mean ms/step | n |",
        "|--------|-----------------|------|-----------------|-------|"
        "--------------|---|",
    ]
    for fam in ("H-PIN", "H-ASYNC"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-PIN":
            d1 = d2 = "—"
        else:
            d1, d2 = f"{d_lp:+.4f}", f"{d_e2e:+.3f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_e2e_wall']:.3f} | "
            f"{d2} | {st['mean_ms_step']:.1f} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Train I/O util on PIN axis — tip STAG / TOP / PIN unchanged as tips.",
            "",
            "Commands: `npm run nano:async` → `npm run nano:async:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/async_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hasync-vs-hpin.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
