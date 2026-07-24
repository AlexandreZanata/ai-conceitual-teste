"""Render formal H-CHUNK vs H-EARLY / H-FLASH (chunked prefill)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from chunk_ops import decide_hchunk


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
    s = stats.get("H-CHUNK", {})
    decision = decide_hchunk(s, stats) if s else "needs H-CHUNK rows"
    early = stats.get("H-EARLY", {})
    flash = stats.get("H-FLASH", {})
    d_lp = s.get("mean_lp", float("nan")) - early.get("mean_lp", float("nan"))
    d_w = s.get("mean_wall", float("nan")) - flash.get("mean_wall", float("nan"))
    d_gf = s.get("mean_gflops", float("nan")) - flash.get("mean_gflops", float("nan"))
    lines = [
        "# Formal H-CHUNK vs H-FLASH (chunked KV prefill)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared formal B2 + formal EARLY tip. Fit≠eval (`eval_prompts`).",
        "Long prompts + chunked KV prefill under SDPA. "
        "Kill if lp < EARLY−ε or no wall win vs H-FLASH.",
        f"Backend: `{data.get('backend')}`; "
        f"`chunk_size={data.get('chunk_size')}`; "
        f"`target_tokens={data.get('target_tokens')}`; "
        f"n_prompts={data.get('n_prompts')}.",
        "",
        "| family | mean teacher_lp | Δ lp (vs EARLY) | mean wall_ms | "
        "Δ wall (vs FLASH) | mean est GFLOPs | Δ GFLOPs | n |",
        "|--------|-----------------|-----------------|--------------|"
        "-------------------|-----------------|----------|---|",
    ]
    for fam in ("H-EARLY", "H-FLASH", "H-CHUNK"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam != "H-CHUNK":
            d1 = d2 = d3 = "—"
        else:
            d1, d2, d3 = f"{d_lp:+.4f}", f"{d_w:+.0f}", f"{d_gf:+.3f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_wall']:.0f} | "
            f"{d2} | {st['mean_gflops']:.3f} | {d3} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Note: systems util deepen on FLASH; tip EARLY genes unchanged.",
            "",
            "Commands: `npm run nano:formal:hchunk` → "
            "`npm run nano:formal:hchunk:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hchunk/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hchunk-vs-hflash.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
