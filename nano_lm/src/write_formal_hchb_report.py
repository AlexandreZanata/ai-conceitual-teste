"""Render formal H-CHB vs H-CHUNK tip (frozen smoke chunk_size)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from chb_ops import decide_hchb


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
    s = stats.get("H-CHB", {})
    decision = decide_hchb(s, stats) if s else "needs H-CHB rows"
    early = stats.get("H-EARLY", {})
    tip = stats.get("H-CHUNK", {})
    d_lp = s.get("mean_lp", float("nan")) - early.get("mean_lp", float("nan"))
    d_w = s.get("mean_wall", float("nan")) - tip.get("mean_wall", float("nan"))
    lines = [
        "# Formal H-CHB vs H-CHUNK (chunk_size sweep winner)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared formal B2 + formal EARLY. Fit≠eval (`eval_prompts`).",
        "Frozen smoke `chunk_size` vs tip CHUNK "
        f"`B={data.get('tip_chunk_size')}`. Long prompts.",
        f"Mode: `{data.get('backend')}`. Kill if lp < EARLY−ε or wall ≥ tip.",
        f"n_prompts={data.get('n_prompts')} "
        f"target_tokens=`{data.get('target_tokens')}`.",
        "",
        "| family | mean teacher_lp | Δ lp (vs EARLY) | mean wall_ms | "
        "Δ wall (vs CHUNK) | n |",
        "|--------|-----------------|-----------------|--------------|"
        "-------------------|---|",
    ]
    for fam in ("H-EARLY", "H-CHUNK", "H-CHB"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-EARLY":
            d1 = d2 = "—"
        elif fam == "H-CHUNK":
            d1 = f"{st['mean_lp'] - early.get('mean_lp', float('nan')):+.4f}"
            d2 = "—"
        else:
            d1, d2 = f"{d_lp:+.4f}", f"{d_w:+.0f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_wall']:.0f} | "
            f"{d2} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Systems util deepen on CHUNK; tip EARLY unchanged.",
            "",
            "Commands: `npm run nano:formal:hchb` → "
            "`npm run nano:formal:hchb:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hchb/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hchb-vs-hchunk.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
