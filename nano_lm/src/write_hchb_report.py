"""Render H-CHB smoke (chunk_size sweep vs H-CHUNK tip)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from chb_ops import DEFAULT_CHUNK, decide_hchb


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
    d_gf = s.get("mean_gflops", float("nan")) - tip.get("mean_gflops", float("nan"))
    win_b = "—"
    for r in data["rows"]:
        if r["family"] == "H-CHB":
            win_b = str(r.get("best_gene", {}).get("chunk_size", "—"))
            break
    lines = [
        "# H-CHB smoke — chunk_size sweep vs H-CHUNK tip",
        "",
        "Same EARLY tip genes; long prompts; prefill block sizes "
        f"`B∈{data.get('sweep')}` under SDPA+KV. Tip CHUNK uses "
        f"`B={data.get('tip_chunk_size', DEFAULT_CHUNK)}`.",
        "PROMOTE iff best-B lp ≥ EARLY−ε and wall < CHUNK tip; else KILL.",
        f"Backend: `{data.get('backend')}`; "
        f"`target_tokens={data.get('target_tokens')}`; "
        f"smoke winner `chunk_size={win_b}`.",
        "",
        "| family | mean teacher_lp | Δ lp (vs EARLY) | mean wall_ms | "
        "Δ wall (vs CHUNK) | mean est GFLOPs | Δ GFLOPs | n |",
        "|--------|-----------------|-----------------|--------------|"
        "-------------------|-----------------|----------|---|",
    ]
    order = ["H-EARLY", "H-CHUNK"] + sorted(
        f for f in stats if f.startswith("H-CHB-B")
    ) + ["H-CHB"]
    for fam in order:
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-CHB":
            d1, d2, d3 = f"{d_lp:+.4f}", f"{d_w:+.0f}", f"{d_gf:+.3f}"
        elif fam == "H-EARLY":
            d1 = d2 = d3 = "—"
        else:
            d1 = f"{st['mean_lp'] - early.get('mean_lp', float('nan')):+.4f}"
            d2 = d3 = "—"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_wall']:.0f} | "
            f"{d2} | {st['mean_gflops']:.3f} | {d3} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Systems util deepen on CHUNK; tip EARLY / CHUNK B=32 unchanged unless "
            "PROMOTE replaces util knob.",
            "",
            "Commands: `npm run nano:chb` → `npm run nano:chb:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/chb_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hchb-vs-hchunk.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
