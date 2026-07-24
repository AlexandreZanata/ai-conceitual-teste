"""Render H-TOPK smoke — k sweep vs tip k=64."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from topk_ops import TIP_TOP_K, TOPK_SWEEP, decide_htopk


def _means_by_k(rows: list[dict]) -> dict[int, dict[str, float]]:
    bags: dict[int, list[dict]] = defaultdict(list)
    for r in rows:
        bags[int(r["top_k"])].append(r)
    out: dict[int, dict[str, float]] = {}
    for k, items in bags.items():
        n = float(len(items))
        out[k] = {
            "mean_lp": sum(float(x["teacher_mean_logprob"]) for x in items) / n,
            "mean_ms_step": sum(float(x["mean_ms_step"]) for x in items) / n,
            "mean_train_wall": sum(float(x["train_wall_s"]) for x in items) / n,
            "n": n,
        }
    return out


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    by_k = _means_by_k(data["rows"])
    decision = decide_htopk(by_k) if by_k else "needs H-TOPK rows"
    tip = by_k.get(int(data.get("tip_top_k", TIP_TOP_K)), {})
    lines = [
        "# H-TOPK smoke — top-k sweep vs tip k=64",
        "",
        "Equal STAG steps; offline cache sliced from max-k=128 (sorted top-k).",
        "Kill if best k ≤ tip k=64 on (teacher_lp, ms/step).",
        f"Recipe: `seq_lo={data.get('seq_lo')}`, `n_stages={data.get('n_stages')}`, "
        f"`steps={data.get('steps')}`, sweep=`{data.get('top_k_sweep', list(TOPK_SWEEP))}`.",
        "",
        "| top_k | mean teacher_lp | Δ lp vs tip | mean ms/step | Δ ms/step | "
        "mean train_wall_s | n |",
        "|-------|-----------------|-------------|--------------|-----------|"
        "------------------|---|",
    ]
    for k in TOPK_SWEEP:
        if k not in by_k:
            continue
        st = by_k[k]
        if k == TIP_TOP_K:
            d1, d2 = "—", "—"
        else:
            d1 = f"{st['mean_lp'] - tip.get('mean_lp', float('nan')):+.4f}"
            d2 = f"{st['mean_ms_step'] - tip.get('mean_ms_step', float('nan')):+.1f}"
        mark = " **(tip)**" if k == TIP_TOP_K else ""
        lines.append(
            f"| {k}{mark} | {st['mean_lp']:.4f} | {d1} | {st['mean_ms_step']:.1f} | "
            f"{d2} | {st['mean_train_wall']:.2f} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:topk` → `npm run nano:topk:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/topk_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/htopk-vs-htop.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
