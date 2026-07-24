"""Render H-AMP smoke vs H-EARLY tip (CUDA autocast decode)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from amp_ops import decide_hamp


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
    s = stats.get("H-AMP", {})
    decision = decide_hamp(s, stats) if s else "needs H-AMP rows"
    tip = stats.get("H-EARLY", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_w = s.get("mean_wall", float("nan")) - tip.get("mean_wall", float("nan"))
    kind = data.get("amp_kind", "bf16")
    lines = [
        "# H-AMP smoke — CUDA AMP decode vs H-EARLY",
        "",
        f"Same B2 ckpt + frozen EARLY genes; autocast `{kind}` matmuls (Q8 redo on CUDA).",
        "Short AMP KD train path exercised; claim is same-ckpt decode.",
        "Kill if quality < EARLY−ε or no wall win vs EARLY.",
        "",
        "| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | n |",
        "|--------|-----------------|------|--------------|--------|-----------------|---|",
    ]
    for fam in ("H-EARLY", "H-AMP"):
        if fam not in stats:
            continue
        st = stats[fam]
        d1 = "—" if fam == "H-EARLY" else f"{d_lp:+.4f}"
        d2 = "—" if fam == "H-EARLY" else f"{d_w:+.0f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_wall']:.0f} | "
            f"{d2} | {st['mean_gflops']:.3f} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:amp` → `npm run nano:amp:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/amp_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hamp-vs-hearly.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
